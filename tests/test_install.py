from __future__ import annotations

from pathlib import Path

from daedalus.install import install_global, plan_install, uninstall_global, update_global
from daedalus.jsonc import load as load_jsonc
from daedalus.manifest import load_install


def make_source(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    (source / ".opencode" / "agents").mkdir(parents=True)
    (source / ".opencode" / "skills" / "demo").mkdir(parents=True)
    (source / "AGENTS.md").write_text("# Agents\n\nGlobal rules.\n", encoding="utf-8")
    (source / "CONVENTIONS.md").write_text("# Conventions\n", encoding="utf-8")
    (source / "opencode.jsonc").write_text(
        '{\n  "default_agent": "orchestrator",\n  "instructions": ["CONVENTIONS.md"],\n'
        '  "agents": {\n'
        '    "code-reviewer": {\n'
        '      "permissions": [\n'
        '        { "action": "edit", "resource": "*", "effect": "deny" }\n'
        "      ]\n"
        "    }\n"
        "  }\n"
        "}\n",
        encoding="utf-8",
    )
    (source / ".opencode" / "agents" / "orchestrator.md").write_text(
        "---\ndescription: Orchestrates\nmode: primary\n---\n\nRoute work.\n",
        encoding="utf-8",
    )
    (source / ".opencode" / "skills" / "demo" / "SKILL.md").write_text(
        "---\ndescription: Demo skill\n---\n\nDo the demo.\n",
        encoding="utf-8",
    )
    return source


def test_plan_install_creates_files(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    target = tmp_path / "target"
    plan = plan_install(source, target)
    actions = {item.relative: item.action for item in plan.items}
    assert actions["agents/orchestrator.md"] == "create"
    assert actions["skills/demo/SKILL.md"] == "create"
    assert actions["CONVENTIONS.md"] == "create"


def test_install_is_idempotent(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    target = tmp_path / "target"

    assert install_global(source=source, target=target) == 0
    manifest = load_install(target)
    assert manifest is not None
    assert (target / "agents" / "orchestrator.md").is_file()
    assert (target / "AGENTS.md").read_text(encoding="utf-8").startswith("<!-- daedalus:begin")

    assert install_global(source=source, target=target) == 0
    plan = plan_install(source, target)
    assert all(item.action == "skip" for item in plan.items)


def test_install_uses_absolute_conventions_path(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    target = tmp_path / "target"
    assert install_global(source=source, target=target) == 0

    config = load_jsonc(target / "opencode.jsonc")
    instructions = config["instructions"]
    assert any(
        Path(entry).is_absolute() and entry.endswith("CONVENTIONS.md") for entry in instructions
    )


def test_merge_config_preserves_existing_settings(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    target = tmp_path / "target"
    target.mkdir()
    (target / "opencode.jsonc").write_text(
        "{\n"
        "  // user configuration\n"
        '  "model": "custom/model",\n'
        '  "permissions": [\n'
        '    { "action": "shell", "resource": "rm *", "effect": "deny" }\n'
        "  ],\n"
        '  "agents": {\n'
        '    "code-reviewer": {\n'
        '      "permissions": [\n'
        '        { "action": "shell", "resource": "git diff *", "effect": "allow" }\n'
        "      ]\n"
        "    }\n"
        "  }\n"
        "}\n",
        encoding="utf-8",
    )

    assert install_global(source=source, target=target, merge_config=True) == 0

    config = load_jsonc(target / "opencode.jsonc")
    assert config["model"] == "custom/model"
    assert config["default_agent"] == "orchestrator"
    assert any(
        Path(entry).is_absolute() and entry.endswith("CONVENTIONS.md")
        for entry in config["instructions"]
    )
    # User rules are appended after Daedalus defaults, so they win.
    assert config["permissions"][-1]["resource"] == "rm *"
    assert config["agents"]["code-reviewer"]["permissions"] == [
        {"action": "edit", "resource": "*", "effect": "deny"},
        {"action": "shell", "resource": "git diff *", "effect": "allow"},
    ]
    backups = list((target / ".daedalus" / "backups").rglob("opencode.jsonc"))
    assert backups


def test_install_detects_conflict(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    target = tmp_path / "target"
    assert install_global(source=source, target=target) == 0

    (target / "agents" / "orchestrator.md").write_text("user edit\n", encoding="utf-8")
    assert install_global(source=source, target=target) == 3
    assert install_global(source=source, target=target, force=True) == 0


def test_update_refreshes_managed_file(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    target = tmp_path / "target"
    assert install_global(source=source, target=target) == 0

    (source / ".opencode" / "agents" / "orchestrator.md").write_text(
        "---\ndescription: Updated\nmode: primary\n---\n\nUpdated.\n",
        encoding="utf-8",
    )
    assert update_global(source=source, target=target) == 0
    assert "Updated" in (target / "agents" / "orchestrator.md").read_text(encoding="utf-8")


def test_uninstall_removes_managed_files(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    target = tmp_path / "target"
    assert install_global(source=source, target=target) == 0

    assert uninstall_global(target=target) == 0
    assert not (target / "agents" / "orchestrator.md").exists()
    assert not (target / "opencode.jsonc").exists()
    assert not (target / ".daedalus" / "install.json").exists()


def test_uninstall_restores_backup(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    target = tmp_path / "target"
    (target / "agents").mkdir(parents=True)
    original = target / "agents" / "orchestrator.md"
    original.write_text("original\n", encoding="utf-8")

    assert install_global(source=source, target=target, force=True) == 0
    assert original.read_text(encoding="utf-8") != "original\n"

    assert uninstall_global(target=target) == 0
    assert original.read_text(encoding="utf-8") == "original\n"
