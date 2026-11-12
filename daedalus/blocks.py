"""Managed Markdown blocks used by global install and project init."""

from __future__ import annotations

BEGIN_MARKER = "<!-- daedalus:begin"
END_MARKER = "<!-- daedalus:end -->"


def has_block(text: str) -> bool:
    """Return ``True`` when *text* contains a Daedalus managed block."""
    start = text.find(BEGIN_MARKER)
    if start == -1:
        return False
    return text.find(END_MARKER, start) != -1


def apply_block(text: str, content: str, version: str = "v1") -> str:
    """Insert or replace the managed block in *text*."""
    body = content.strip()
    block = f"{BEGIN_MARKER} {version} -->\n{body}\n{END_MARKER}"
    start = text.find(BEGIN_MARKER)
    if start != -1:
        end = text.find(END_MARKER, start)
        if end != -1:
            end += len(END_MARKER)
            return text[:start] + block + text[end:]

    stripped = text.rstrip()
    if not stripped:
        return block + "\n"
    return f"{stripped}\n\n{block}\n"


def remove_block(text: str) -> str:
    """Remove the managed block and collapse the surrounding blank lines."""
    start = text.find(BEGIN_MARKER)
    if start == -1:
        return text
    end = text.find(END_MARKER, start)
    if end == -1:
        return text
    end += len(END_MARKER)
    before = text[:start].rstrip()
    after = text[end:].lstrip()
    if before and after:
        return f"{before}\n\n{after}\n"
    if before:
        return before + "\n"
    if after:
        return after + "\n"
    return ""
