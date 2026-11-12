from __future__ import annotations

from pathlib import Path

from daedalus.paths import (
    atomic_write_text,
    find_git_root,
    is_within,
    opencode_config_dir,
    write_text,
)


def test_is_within_accepts_root_and_child(tmp_path: Path) -> None:
    child = tmp_path / "a" / "b"
    child.mkdir(parents=True)
    assert is_within(child, tmp_path)
    assert is_within(tmp_path, tmp_path)


def test_is_within_rejects_outside_path(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside"
    assert not is_within(outside, tmp_path)


def test_find_git_root_walks_up(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    nested = tmp_path / "src" / "package"
    nested.mkdir(parents=True)
    assert find_git_root(nested) == tmp_path


def test_find_git_root_returns_none_without_repository(tmp_path: Path) -> None:
    nested = tmp_path / "src"
    nested.mkdir()
    assert find_git_root(nested) is None


def test_write_text_is_utf8_and_creates_parents(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "file.txt"
    write_text(path, "olá")
    assert path.read_text(encoding="utf-8") == "olá"


def test_atomic_write_text_replaces_content(tmp_path: Path) -> None:
    path = tmp_path / "file.txt"
    path.write_text("old", encoding="utf-8")
    atomic_write_text(path, "new")
    assert path.read_text(encoding="utf-8") == "new"


def test_opencode_config_dir_override(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DAEDALUS_CONFIG_DIR", str(tmp_path))
    assert opencode_config_dir() == tmp_path.resolve()
