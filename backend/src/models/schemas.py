from typing import Any, Literal
from pydantic import BaseModel, Field

ArrayMode = Literal["explode", "join", "json-stringify"]
NullMode = Literal["empty", "null"]


class CandidateRoot(BaseModel):
    path: str
    kind: str
    score: float
    length: int | None = None
    object_ratio: float | None = None
    primitive_ratio: float | None = None
    columns_preview: list[str] = Field(default_factory=list)


class StructureSummary(BaseModel):
    root_type: str
    max_depth: int
    total_nodes: int
    object_count: int
    array_count: int
    primitive_count: int
    null_count: int


class AnalyzeRequest(BaseModel):
    data: Any


class AnalyzeResponse(BaseModel):
    summary: StructureSummary
    candidate_roots: list[CandidateRoot]
    recommended_root_path: str
    recommended_array_mode: ArrayMode = "explode"
    recommended_null_mode: NullMode = "empty"
    warnings: list[str] = Field(default_factory=list)


class TransformOptions(BaseModel):
    root_path: str | None = None
    array_mode: ArrayMode = "explode"
    primitive_array_mode: Literal["join", "index", "json-stringify"] = "join"
    null_mode: NullMode = "empty"
    join_delimiter: str = ", "
    stringify_complex: bool = True
    max_depth: int = 80
    max_rows: int = 100_000
    preview_limit: int | None = None


class TransformRequest(BaseModel):
    data: Any
    options: TransformOptions = Field(default_factory=TransformOptions)


class ColumnDef(BaseModel):
    field: str
    headerName: str
    type: str = "string"


class TransformMeta(BaseModel):
    row_count: int
    column_count: int
    returned_rows: int
    root_path: str
    array_mode: ArrayMode
    primitive_array_mode: str
    truncated: bool = False
    warnings: list[str] = Field(default_factory=list)


class TransformResponse(BaseModel):
    columns: list[ColumnDef]
    rows: list[dict[str, Any]]
    meta: TransformMeta


class ExportRequest(BaseModel):
    columns: list[str] | None = None
    rows: list[dict[str, Any]]
    delimiter: str = ","
    filename: str = "json-table"


class HierarchicalExportRequest(BaseModel):
    data: Any
    filename: str = "json-table"
    max_depth: int = 80


class HierarchicalPreviewRequest(BaseModel):
    data: Any
    max_depth: int = 80
    preview_limit: int = 100


class HierarchicalPreviewMeta(BaseModel):
    row_count: int
    column_count: int
    returned_rows: int
    truncated: bool = False


class HierarchicalPreviewResponse(BaseModel):
    header_rows: list[list[Any]]
    rows: list[list[Any]]
    meta: HierarchicalPreviewMeta
