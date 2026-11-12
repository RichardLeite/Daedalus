from __future__ import annotations

from pathlib import Path

from daedalus.validate import validate_root


def make_project(tmp_path: Path) -> Path:
    agents = tmp_path / ".opencode" / "agents"
    commands = tmp_path / ".opencode" / "commands"
    skill = tmp_path / ".opencode" / "skills" / "code-review"
    agents.mkdir(parents=True)
    commands.mkdir(parents=True)
    skill.mkdir(parents=True)

    (agents / "reviewer.md").write_text(
        "---\ndescription: Reviews changes\nmode: subagent\n---\n\nReview the current changes.\n",
        encoding="utf-8",
    )
    (commands / "review.md").write_text(
        "---\ndescription: Review changes\nagent: reviewer\n---\n\nReview $ARGUMENTS.\n",
        encoding="utf-8",
    )
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: Code Review\n"
        "description: Review code for correctness\n"
        "---\n\n"
        "Review the diff.\n",
        encoding="utf-8",
    )
    (tmp_path / "AGENTS.md").write_text("# Project\n", encoding="utf-8")
    (tmp_path / "opencode.jsonc").write_text(
        "{\n"
        '  "default_agent": "reviewer",\n'
        '  "instructions": ["AGENTS.md"],\n'
        '  "permissions": [\n'
        '    { "action": "shell", "resource": "*", "effect": "allow" }\n'
        "  ]\n"
        "}\n",
        encoding="utf-8",
    )
    return tmp_path


def test_valid_project_passes(tmp_path: Path) -> None:
    result = validate_root(make_project(tmp_path))
    assert result.ok, result.errors
    assert result.checked >= 4


def test_v1_agent_field_is_rejected(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    agent = root / ".opencode" / "agents" / "reviewer.md"
    agent.write_text(
        "---\ndescription: Reviews changes\nmode: subagent\ntemperature: 0.1\n---\n\nReview.\n",
        encoding="utf-8",
    )
    result = validate_root(root)
    assert not result.ok
    assert any("V1 field" in error for error in result.errors)


def test_agent_description_is_required(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    agent = root / ".opencode" / "agents" / "reviewer.md"
    agent.write_text("---\nmode: subagent\n---\n\nReview.\n", encoding="utf-8")
    result = validate_root(root)
    assert not result.ok
    assert any("description is required" in error for error in result.errors)


def test_duplicate_skill_id_is_rejected(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    duplicate = root / ".opencode" / "skills" / "group" / "code-review"
    duplicate.mkdir(parents=True)
    (duplicate / "SKILL.md").write_text(
        "---\ndescription: Duplicate\n---\n\nDuplicate.\n",
        encoding="utf-8",
    )
    result = validate_root(root)
    assert not result.ok
    assert any("duplicate skill id" in error for error in result.errors)


def test_skill_description_is_required(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    skill = root / ".opencode" / "skills" / "code-review" / "SKILL.md"
    skill.write_text("---\nname: Code Review\n---\n\nReview.\n", encoding="utf-8")
    result = validate_root(root)
    assert not result.ok
    assert any("description is required" in error for error in result.errors)


def test_command_template_in_frontmatter_is_rejected(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    command = root / ".opencode" / "commands" / "review.md"
    command.write_text(
        "---\ndescription: Review\ntemplate: Review this\n---\n\nBody.\n",
        encoding="utf-8",
    )
    result = validate_root(root)
    assert not result.ok
    assert any("template must be the Markdown body" in error for error in result.errors)


def test_v1_mcp_shape_is_rejected(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    config = root / "opencode.jsonc"
    config.write_text(
        '{\n  "default_agent": "reviewer",\n'
        '  "mcp": { "server": { "type": "local", "command": ["x"] } }\n'
        "}\n",
        encoding="utf-8",
    )
    result = validate_root(root)
    assert not result.ok
    assert any("V1 mcp shape" in error for error in result.errors)


def test_missing_default_agent_is_rejected(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    config = root / "opencode.jsonc"
    config.write_text(
        '{\n  "default_agent": "missing",\n  "instructions": ["AGENTS.md"]\n}\n',
        encoding="utf-8",
    )
    result = validate_root(root)
    assert not result.ok
    assert any("default_agent" in error for error in result.errors)


def test_missing_instruction_file_is_rejected(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    config = root / "opencode.jsonc"
    config.write_text(
        '{\n  "default_agent": "reviewer",\n  "instructions": ["MISSING.md"]\n}\n',
        encoding="utf-8",
    )
    result = validate_root(root)
    assert not result.ok
    assert any("instruction file not found" in error for error in result.errors)


def test_secret_is_rejected(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    agent = root / ".opencode" / "agents" / "reviewer.md"
    agent.write_text(
        "---\ndescription: Reviews\nmode: subagent\n---\n\n"
        "token: ghp_abcdefghijklmnopqrstuvwxyz0123456789\n",
        encoding="utf-8",
    )
    result = validate_root(root)
    assert not result.ok
    assert any("GitHub token" in error for error in result.errors)


def test_project_manifest_is_validated(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    (root / ".opencode" / "project.json").write_text(
        '{"version": "one", "name": "", "profile": "", "stack": "python"}\n',
        encoding="utf-8",
    )
    result = validate_root(root)
    assert not result.ok
    assert any("project.json: version" in error for error in result.errors)
    assert any("project.json: stack" in error for error in result.errors)
