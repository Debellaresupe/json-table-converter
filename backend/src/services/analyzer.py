from __future__ import annotations

from typing import Any

from src.models.schemas import CandidateRoot, StructureSummary
from src.services.json_utils import is_primitive, join_path, type_name


class JsonAnalyzer:
    def __init__(self, max_depth: int = 80, max_children_per_array: int = 50):
        self.max_depth = max_depth
        self.max_children_per_array = max_children_per_array
        self.warnings: list[str] = []

    def analyze(self, data: Any) -> tuple[StructureSummary, list[CandidateRoot], str, list[str]]:
        counters = {"max_depth": 0, "total_nodes": 0, "object_count": 0, "array_count": 0, "primitive_count": 0, "null_count": 0}
        candidates: list[CandidateRoot] = []
        self._walk(data, "$", 0, counters, candidates)
        candidates.sort(key=lambda c: c.score, reverse=True)
        recommended = candidates[0].path if candidates else "$"
        return StructureSummary(root_type=type_name(data), **counters), candidates, recommended, self.warnings

    def _walk(self, node: Any, path: str, depth: int, counters: dict[str, int], candidates: list[CandidateRoot]) -> None:
        counters["total_nodes"] += 1
        counters["max_depth"] = max(counters["max_depth"], depth)
        if depth > self.max_depth:
            self.warnings.append(f"Max depth {self.max_depth} reached at {path}; nested content was not fully analyzed.")
            return
        if isinstance(node, dict):
            counters["object_count"] += 1
            for key, value in list(node.items()):
                self._walk(value, join_path(path, key), depth + 1, counters, candidates)
        elif isinstance(node, list):
            counters["array_count"] += 1
            candidates.append(self._candidate_for_array(node, path))
            for idx, item in enumerate(node[: self.max_children_per_array]):
                self._walk(item, join_path(path, idx), depth + 1, counters, candidates)
        else:
            counters["primitive_count"] += 1
            if node is None:
                counters["null_count"] += 1

    def _candidate_for_array(self, arr: list[Any], path: str) -> CandidateRoot:
        length = len(arr)
        if length == 0:
            return CandidateRoot(path=path, kind="empty_array", score=0, length=0)
        sample = arr[: self.max_children_per_array]
        obj_count = sum(isinstance(x, dict) for x in sample)
        primitive_count = sum(is_primitive(x) for x in sample)
        object_ratio = obj_count / len(sample)
        primitive_ratio = primitive_count / len(sample)
        columns: set[str] = set()
        for item in sample:
            if isinstance(item, dict):
                columns.update(item.keys())
        score = length * 2 + object_ratio * 100 + min(len(columns), 30)
        kind = "array_of_objects" if object_ratio >= 0.5 else "array_of_primitives" if primitive_ratio >= 0.8 else "mixed_array"
        return CandidateRoot(path=path, kind=kind, score=round(score, 2), length=length, object_ratio=round(object_ratio, 2), primitive_ratio=round(primitive_ratio, 2), columns_preview=sorted(columns)[:20])
