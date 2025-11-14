"""ARION 1.0 reference implementation (Python).

ARION = Alpinum Readable Indented Object Notation

This module provides:

- dumps_arion(obj) -> str
- loads_arion(text: str) -> obj
- dumps_json(obj) -> str
- loads_json(text: str) -> obj

Where obj is any JSON-serializable Python structure.
"""

from __future__ import annotations
import json
from typing import Any, List, Tuple


def _is_number(s: str) -> bool:
    try:
        # use json to match JSON number rules
        v = json.loads(s)
        return isinstance(v, (int, float))
    except Exception:
        return False


def _parse_scalar(raw: str) -> Any:
    raw = raw.strip()
    if raw == "":
        return ""
    if raw.startswith("'"):
        return raw[1:]
    if raw == "true":
        return True
    if raw == "false":
        return False
    if raw == "null":
        return None
    if _is_number(raw):
        return json.loads(raw)
    return raw


def _tokenize_lines(text: str) -> List[Tuple[int, str]]:
    lines = []
    for line in text.splitlines():
        if not line.strip():
            continue
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        # ignore header
        if stripped.startswith("!ARION"):
            continue
        # ignore comments
        if stripped.startswith("#"):
            continue
        lines.append((indent, stripped))
    return lines


def loads_arion(text: str) -> Any:
    """Parse ARION text into a Python object."""
    lines = _tokenize_lines(text)

    def parse_block(index: int, current_indent: int) -> Tuple[int, Any]:
        obj: dict = {}
        arr: list | None = None
        multiline_accumulator: List[str] | None = None
        multiline_indent: int | None = None

        while index < len(lines):
            indent, stripped = lines[index]
            if indent < current_indent:
                break

            if stripped.startswith("."):
                # close any pending multiline
                if multiline_accumulator is not None:
                    # flush multiline into last key
                    raise ValueError("Malformed ARION: multiline string not attached to a key")
                # key line
                content = stripped[1:]
                if " " in content:
                    key, value_str = content.split(" ", 1)
                    value = _parse_scalar(value_str)
                    obj[key] = value
                    index += 1
                else:
                    key = content
                    # look ahead to children
                    if index + 1 >= len(lines):
                        obj[key] = {}
                        index += 1
                        continue
                    next_indent, next_stripped = lines[index + 1]
                    if next_indent <= indent:
                        # empty object
                        obj[key] = {}
                        index += 1
                        continue
                    # multiline string vs nested structure
                    if not (next_stripped.startswith(".") or next_stripped.startswith("-")):
                        # multiline string
                        multiline_lines: List[str] = []
                        j = index + 1
                        child_indent = next_indent
                        while j < len(lines):
                            ci, cs = lines[j]
                            if ci < child_indent:
                                break
                            if ci == child_indent and not (cs.startswith(".") or cs.startswith("-")):
                                multiline_lines.append(cs)
                                j += 1
                            else:
                                break
                        obj[key] = "\n".join(multiline_lines)
                        index = j
                    else:
                        # nested structure
                        index2, child = parse_block(index + 1, indent + 1)
                        obj[key] = child
                        index = index2

            elif stripped.startswith("-"):
                # we are in an array context
                if arr is None:
                    arr = []
                # `-` may be followed by a scalar or start a nested block
                tail = stripped[1:].strip()
                if tail:
                    arr.append(_parse_scalar(tail))
                    index += 1
                else:
                    if index + 1 >= len(lines):
                        arr.append({})
                        index += 1
                        continue
                    next_indent, next_stripped = lines[index + 1]
                    if next_indent <= indent:
                        arr.append({})
                        index += 1
                        continue
                    # nested block
                    index2, child = parse_block(index + 1, indent + 1)
                    arr.append(child)
                    index = index2
            else:
                # this can only happen if malformed according to the spec
                raise ValueError(f"Invalid ARION line at indent {indent}: {stripped!r}")

        if arr is not None and not obj:
            return index, arr
        if arr is not None and obj:
            raise ValueError("Mixed object and array at the same level is not allowed")
        return index, obj

    if not lines:
        return None

    # decide top-level structure: object or array
    first_indent, first_stripped = lines[0]
    if first_stripped.startswith("-"):
        _, value = parse_block(0, first_indent)
    else:
        _, value = parse_block(0, first_indent)
    return value


def dumps_arion(value: Any, header: bool = True) -> str:
    """Serialize a Python object (JSON compatible) to ARION text."""

    def encode_scalar(v: Any) -> str:
        if isinstance(v, bool):
            return "true" if v else "false"
        if v is None:
            return "null"
        if isinstance(v, (int, float)):
            return json.dumps(v)
        s = str(v)
        # If s would be parsed as non-string, force string
        if s in ("true", "false", "null") or _is_number(s):
            return "'" + s
        return s

    def encode_block(v: Any, indent: int, as_array: bool = False) -> List[str]:
        lines: List[str] = []
        sp = " " * indent
        if isinstance(v, dict):
            for k, val in v.items():
                if isinstance(val, (dict, list)):
                    lines.append(f"{sp}.{k}")
                    lines.extend(encode_block(val, indent + 2, isinstance(val, list)))
                elif isinstance(val, str) and "\n" in val:
                    lines.append(f"{sp}.{k}")
                    for line in val.split("\n"):
                        lines.append(" " * (indent + 2) + line)
                else:
                    lines.append(f"{sp}.{k} {encode_scalar(val)}")
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, (dict, list)):
                    lines.append(f"{sp}-")
                    lines.extend(encode_block(item, indent + 2, isinstance(item, list)))
                elif isinstance(item, str) and "\n" in item:
                    lines.append(f"{sp}-")
                    for line in item.split("\n"):
                        lines.append(" " * (indent + 2) + line)
                else:
                    lines.append(f"{sp}- {encode_scalar(item)}")
        else:
            # scalar at root (rare but possible): treat as single-item array
            lines.append(f"{sp}- {encode_scalar(v)}")
        return lines

    lines: List[str] = []
    if header:
        lines.append("!ARION 1.0")
        lines.append("")

    # choose indentation root 0
    lines.extend(encode_block(value, 0, isinstance(value, list)))
    return "\n".join(lines) + "\n"


def dumps_json(value: Any, **kwargs: Any) -> str:
    """Convenience JSON dump with sensible defaults."""
    defaults = {"ensure_ascii": False, "indent": 2}
    defaults.update(kwargs)
    return json.dumps(value, **defaults)


def loads_json(text: str) -> Any:
    return json.loads(text)


__all__ = [
    "loads_arion",
    "dumps_arion",
    "loads_json",
    "dumps_json",
]
