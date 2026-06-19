from __future__ import annotations

import json

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from src.core.config import settings
from src.models.schemas import AnalyzeRequest, AnalyzeResponse, ExportRequest, HierarchicalExportRequest, HierarchicalPreviewRequest, HierarchicalPreviewResponse, TransformRequest, TransformResponse
from src.services.analyzer import JsonAnalyzer
from src.services.exporter import to_csv_bytes, to_xlsx_bytes
from src.services.normalizer import JsonNormalizer
from src.services.hierarchical_exporter import build_hierarchical_table, to_hierarchical_xlsx_bytes

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@router.post("/parse-file")
async def parse_file(file: UploadFile = File(...)) -> dict:
    if not file.filename.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="Only .json files are supported")
    content = await file.read(settings.max_json_bytes + 1)
    if len(content) > settings.max_json_bytes:
        raise HTTPException(status_code=413, detail=f"JSON file is too large. Limit is {settings.max_json_bytes // 1024 // 1024} MB")
    try:
        return {"data": json.loads(content.decode("utf-8-sig"))}
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded") from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    analyzer = JsonAnalyzer(max_depth=settings.max_depth)
    summary, candidates, recommended, warnings = analyzer.analyze(payload.data)
    return AnalyzeResponse(summary=summary, candidate_roots=candidates, recommended_root_path=recommended, warnings=warnings)


@router.post("/transform", response_model=TransformResponse)
def transform(payload: TransformRequest) -> TransformResponse:
    payload.options.max_depth = min(payload.options.max_depth, settings.max_depth)
    payload.options.max_rows = min(payload.options.max_rows, settings.max_rows)
    payload.options.preview_limit = payload.options.preview_limit or settings.preview_limit
    try:
        return JsonNormalizer().transform(payload.data, payload.options)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/preview/reference", response_model=HierarchicalPreviewResponse)
def preview_reference(payload: HierarchicalPreviewRequest) -> HierarchicalPreviewResponse:
    table = build_hierarchical_table(
        payload.data,
        max_depth=min(payload.max_depth, settings.max_depth),
        preview_limit=min(payload.preview_limit, settings.preview_limit),
    )
    return HierarchicalPreviewResponse(**table)


@router.post("/export/csv")
def export_csv(payload: ExportRequest) -> Response:
    content = to_csv_bytes(payload.rows, payload.columns, payload.delimiter)
    filename = _safe_filename(payload.filename, "csv")
    return Response(content, media_type="text/csv; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.post("/export/xlsx")
def export_xlsx(payload: ExportRequest) -> Response:
    content = to_xlsx_bytes(payload.rows, payload.columns)
    filename = _safe_filename(payload.filename, "xlsx")
    return Response(content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.post("/export/xlsx-hierarchical")
def export_xlsx_hierarchical(payload: HierarchicalExportRequest) -> Response:
    content = to_hierarchical_xlsx_bytes(payload.data, max_depth=min(payload.max_depth, settings.max_depth))
    filename = _safe_filename(payload.filename, "xlsx")
    return Response(content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


def _safe_filename(name: str, ext: str) -> str:
    safe = "".join(ch for ch in name if ch.isalnum() or ch in ("-", "_")) or "json-table"
    return f"{safe}.{ext}"
