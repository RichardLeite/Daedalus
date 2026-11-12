"""Minimal JSONC reader and writer.

OpenCode accepts JSON and JSONC. Daedalus only needs to read configuration and
write generated JSON, so this module implements comment and trailing-comma
handling without a third-party dependency. It deliberately does not preserve
comments on write; callers that rewrite an existing user configuration must
create a backup first.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from daedalus.paths import atomic_write_text


class JsoncError(ValueError):
    """Raised when a JSONC document cannot be parsed."""


def _strip_comments(text: str) -> str:
    output: list[str] = []
    index = 0
    length = len(text)
    in_string = False
    escaped = False

    while index < length:
        char = text[index]

        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            output.append(char)
            index += 1
            continue

        if char == "/" and index + 1 < length:
            following = text[index + 1]
            if following == "/":
                index += 2
                while index < length and text[index] not in "\r\n":
                    index += 1
                continue
            if following == "*":
                index += 2
                while index + 1 < length and not (text[index] == "*" and text[index + 1] == "/"):
                    index += 1
                index += 2
                continue

        output.append(char)
        index += 1

    if in_string:
        raise JsoncError("unterminated string")
    return "".join(output)


def _strip_trailing_commas(text: str) -> str:
    output: list[str] = []
    index = 0
    length = len(text)
    in_string = False
    escaped = False

    while index < length:
        char = text[index]

        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            output.append(char)
            index += 1
            continue

        if char == ",":
            following = index + 1
            while following < length and text[following] in " \t\r\n":
                following += 1
            if following < length and text[following] in "]}":
                index += 1
                continue

        output.append(char)
        index += 1

    return "".join(output)


def loads(text: str) -> Any:
    """Parse JSONC text into Python values."""
    if text.startswith("\ufeff"):
        text = text[1:]
    if not text.strip():
        raise JsoncError("empty document")
    cleaned = _strip_trailing_commas(_strip_comments(text))
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise JsoncError(
            f"invalid JSONC at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc


def load(path: Path) -> Any:
    """Read and parse a JSONC file."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise JsoncError(f"cannot read {path}: {exc}") from exc
    try:
        return loads(text)
    except JsoncError as exc:
        raise JsoncError(f"{path}: {exc}") from exc


def dumps(value: Any) -> str:
    """Serialize *value* as indented JSON with a trailing newline."""
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def dump(path: Path, value: Any) -> None:
    """Atomically write *value* as JSON to *path*."""
    atomic_write_text(path, dumps(value))
