from __future__ import annotations

from typing import Any


def is_primitive(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def join_path(base: str, part: str | int) -> str:
    if base in ("", "$"):
        return f"$[{part}]" if isinstance(part, int) else f"$.{part}"
    return f"{base}[{part}]" if isinstance(part, int) else f"{base}.{part}"


def column_path(base: str, key: str) -> str:
    return key if not base else f"{base}.{key}"


def get_by_path(data: Any, path: str | None) -> Any:
    if not path or path == "$":
        return data
    if not path.startswith("$"):
        raise ValueError("root_path must start with '$'")

    current = data
    i = 1
    while i < len(path):
        if path[i] == ".":
            i += 1
            start = i
            while i < len(path) and path[i] not in ".[":
                i += 1
            key = path[start:i]
            if not isinstance(current, dict) or key not in current:
                raise KeyError(f"Path segment not found: {key}")
            current = current[key]
        elif path[i] == "[":
            end = path.index("]", i)
            idx = int(path[i + 1:end])
            if not isinstance(current, list) or idx >= len(current):
                raise KeyError(f"Array index not found: {idx}")
            current = current[idx]
            i = end + 1
        else:
            raise ValueError(f"Invalid path near: {path[i:]}")
    return current
