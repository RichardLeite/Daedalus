from __future__ import annotations

import json
from pathlib import Path

import pytest

from daedalus.cli import main
from tests.test_validate import make_project


def test_version_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "daedalus" in capsys.readouterr().out


def test_validate_json_returns_zero(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    make_project(tmp_path)
    code = main(["validate", "--root", str(tmp_path), "--json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True


def test_validate_invalid_returns_one(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = make_project(tmp_path)
    agent = root / ".opencode" / "agents" / "reviewer.md"
    agent.write_text("---\ntemperature: 0.2\n---\n", encoding="utf-8")
    code = main(["validate", "--root", str(root), "--json"])
    assert code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False


def test_context_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    code = main(["context", "--path", str(tmp_path), "--json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["root"] == str(tmp_path.resolve())
    assert "python" in payload["stack"]


def test_install_requires_global(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["install", "--dir", str(tmp_path)])
    assert code == 2
    assert "only --global" in capsys.readouterr().err
