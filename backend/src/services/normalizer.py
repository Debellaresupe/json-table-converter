from __future__ import annotations

import json
from typing import Any

from src.models.schemas import ColumnDef, TransformMeta, TransformOptions, TransformResponse
from src.services.analyzer import JsonAnalyzer
from src.services.json_utils import column_path, get_by_path, is_primitive

TECH_COLUMNS = ["_row_id", "_source_path", "_root_index", "_parent_path"]


class JsonNormalizer:
    def __init__(self):
        self.warnings: list[str] = []
        self.row_seq = 0

    def transform(self, data: Any, options: TransformOptions) -> TransformResponse:
        analyzer = JsonAnalyzer(max_depth=options.max_depth)
        _, _, recommended, warnings = analyzer.analyze(data)
        self.warnings.extend(warnings)
        root_path = options.root_path or recommended or "$"
        try:
            root = get_by_path(data, root_path)
        except Exception as exc:
            raise ValueError(f"Invalid root_path '{root_path}': {exc}") from exc
        base_items = root if isinstance(root, list) else [root]
        rows: list[dict[str, Any]] = []
        for idx, item in enumerate(base_items):
            if len(rows) >= options.max_rows:
                self.warnings.append(f"Row limit {options.max_rows} reached; output was truncated.")
                break
            source_path = f"{root_path}[{idx}]" if isinstance(root, list) else root_path
            rows.extend(self._normalize_item(item, options, source_path, idx, root_path))
            if len(rows) > options.max_rows:
                rows = rows[: options.max_rows]
                self.warnings.append(f"Row limit {options.max_rows} reached; output was truncated.")
                break
        all_columns = self._union_columns(rows)
        normalized_rows = [self._fill_missing(row, all_columns, options) for row in rows]
        returned = normalized_rows[: options.preview_limit] if options.preview_limit else normalized_rows
        columns = [ColumnDef(field=c, headerName=c, type=self._infer_column_type(normalized_rows, c)) for c in all_columns]
        meta = TransformMeta(row_count=len(normalized_rows), column_count=len(all_columns), returned_rows=len(returned), root_path=root_path, array_mode=options.array_mode, primitive_array_mode=options.primitive_array_mode, truncated=len(returned) < len(normalized_rows), warnings=self.warnings)
        return TransformResponse(columns=columns, rows=returned, meta=meta)

    def _normalize_item(self, item: Any, options: TransformOptions, source_path: str, root_index: int, parent_path: str) -> list[dict[str, Any]]:
        result = []
        for row in self._flatten(item, options=options, path="", depth=0):
            self.row_seq += 1
            result.append({"_row_id": self.row_seq, "_source_path": source_path, "_root_index": root_index, "_parent_path": parent_path, **row})
        return result

    def _flatten(self, value: Any, options: TransformOptions, path: str, depth: int) -> list[dict[str, Any]]:
        if depth > options.max_depth:
            self.warnings.append(f"Max depth {options.max_depth} reached at {path or '$'}; value was stringified.")
            return [{path or "value": self._stringify(value)}]
        if is_primitive(value):
            return [{path or "value": value}]
        if isinstance(value, dict):
            rows = [{}]
            if not value:
                return [{path: "{}"} if path else {}]
            for key, child in value.items():
                child_rows = self._flatten(child, options, column_path(path, str(key)), depth + 1)
                rows = self._cross_join(rows, child_rows, options.max_rows)
            return rows
        if isinstance(value, list):
            return self._flatten_array(value, options, path, depth)
        return [{path or "value": str(value)}]

    def _flatten_array(self, arr: list[Any], options: TransformOptions, path: str, depth: int) -> list[dict[str, Any]]:
        if not arr:
            return [{path: "[]" if options.primitive_array_mode == "json-stringify" else ""}]
        all_primitive = all(is_primitive(x) for x in arr)
        all_objects = all(isinstance(x, dict) for x in arr)
        if all_primitive:
            if options.primitive_array_mode == "index":
                return [{column_path(path, str(i)): v for i, v in enumerate(arr)}]
            if options.primitive_array_mode == "json-stringify":
                return [{path: self._stringify(arr)}]
            return [{path: options.join_delimiter.join("" if x is None else str(x) for x in arr)}]
        if options.array_mode in ("join", "json-stringify"):
            return [{path: self._stringify(arr)}]
        if options.array_mode == "explode" and all_objects:
            rows: list[dict[str, Any]] = []
            for item in arr:
                rows.extend(self._flatten(item, options, path, depth + 1))
                if len(rows) >= options.max_rows:
                    self.warnings.append(f"Nested array at {path or '$'} exceeded row limit; truncated.")
                    return rows[: options.max_rows]
            return rows
        return [{path: self._stringify(arr)}]

    def _cross_join(self, left: list[dict[str, Any]], right: list[dict[str, Any]], max_rows: int) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for lrow in left:
            for rrow in right:
                out.append({**lrow, **rrow})
                if len(out) >= max_rows:
                    return out
        return out

    def _union_columns(self, rows: list[dict[str, Any]]) -> list[str]:
        seen = set()
        ordered: list[str] = []
        for col in TECH_COLUMNS:
            seen.add(col)
            ordered.append(col)
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    seen.add(key)
                    ordered.append(key)
        return ordered

    def _fill_missing(self, row: dict[str, Any], columns: list[str], options: TransformOptions) -> dict[str, Any]:
        fill = None if options.null_mode == "null" else ""
        return {col: row.get(col, fill) for col in columns}

    def _infer_column_type(self, rows: list[dict[str, Any]], column: str) -> str:
        values = [r.get(column) for r in rows if r.get(column) not in (None, "")]
        if not values:
            return "string"
        if all(isinstance(v, bool) for v in values):
            return "boolean"
        if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
            return "number"
        return "string"

    def _stringify(self, value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
