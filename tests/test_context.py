from __future__ import annotations

from pathlib import Path

from daedalus.context import detect_stack


def test_detect_stack_from_markers(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    (tmp_path / "Dockerfile").write_text("", encoding="utf-8")
    assert detect_stack(tmp_path) == ["node", "python", "docker"]


def test_detect_stack_empty(tmp_path: Path) -> None:
    assert detect_stack(tmp_path) == []
