from __future__ import annotations

from pathlib import Path

from daedalus.init import init_project, plan_init


def make_project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    (root / ".git").mkdir()
    (root / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    return root


def test_init_creates_project_layer(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    assert init_project(path=root, yes=True) == 0

    assert (root / ".opencode" / "opencode.jsonc").is_file()
    assert (root / ".opencode" / "project.json").is_file()
    assert (root / ".opencode" / ".daedalus.json").is_file()
    assert (root / ".opencode" / "knowledge" / "README.md").is_file()
    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    assert "<!-- daedalus:begin" in agents
    assert "Project: project" in agents
    assert "python" in agents
    gitignore = (root / ".gitignore").read_text(encoding="utf-8")
    assert ".opencode/knowledge/plans/" in gitignore


def test_init_plan_does_not_write(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    plan = plan_init(root)
    assert plan.files
    assert not (root / ".opencode").exists()


def test_init_is_idempotent(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    assert init_project(path=root, yes=True) == 0
    assert init_project(path=root, yes=True, update=True) == 0


def test_init_profile_adds_guidance(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    assert init_project(path=root, profile="backend", yes=True) == 0
    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    assert "Profile: backend" in agents
    assert "Validate input at the boundary" in agents
    gitignore = (root / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in gitignore


def test_init_update_detects_user_edit(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    assert init_project(path=root, yes=True) == 0
    config = root / ".opencode" / "opencode.jsonc"
    config.write_text('{"instructions": []}\n', encoding="utf-8")
    assert init_project(path=root, yes=True, update=True) == 3
    assert init_project(path=root, yes=True, update=True, force=True) == 0
