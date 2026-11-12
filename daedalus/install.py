"""Global installation, update, and uninstall."""

from __future__ import annotations

import contextlib
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from daedalus import __version__
from daedalus.blocks import apply_block, has_block, remove_block
from daedalus.jsonc import JsoncError
from daedalus.jsonc import dump as dump_jsonc
from daedalus.jsonc import load as load_jsonc
from daedalus.manifest import (
    InstallManifest,
    ManifestError,
    file_record,
    load_install,
    save_install,
    sha256_file,
    utc_now,
)
from daedalus.paths import (
    atomic_write_text,
    is_within,
    opencode_config_dir,
    read_text,
    source_root,
)

CORE_DIRS = ("agents", "commands", "skills", "rules", "templates", "profiles")
CORE_FILES = ("CONVENTIONS.md",)
SKIP_PARTS = {"__pycache__", ".git", "node_modules", ".venv"}


@dataclass
class PlanItem:
    relative: str
    action: str
    source: Path
    target: Path
    reason: str = ""


@dataclass
class InstallPlan:
    source: Path
    target: Path
    items: list[PlanItem] = field(default_factory=list)
    config_action: str = "skip"
    agents_action: str = "skip"
    warnings: list[str] = field(default_factory=list)

    @property
    def conflicts(self) -> list[PlanItem]:
        return [item for item in self.items if item.action == "conflict"]


def _validate_source(source: Path) -> None:
    if not source.is_dir():
        raise FileNotFoundError(f"source is not a directory: {source}")
    if not (source / ".opencode" / "agents").is_dir():
        raise FileNotFoundError(f"source does not look like Daedalus: {source}")
    if not (source / "opencode.jsonc").is_file():
        raise FileNotFoundError(f"source is missing opencode.jsonc: {source}")
    if not (source / "AGENTS.md").is_file():
        raise FileNotFoundError(f"source is missing AGENTS.md: {source}")


def _iter_core_files(source: Path) -> list[Path]:
    files: list[Path] = []
    opencode = source / ".opencode"
    for dirname in CORE_DIRS:
        base = opencode / dirname
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            files.append(Path(dirname) / path.relative_to(base))
    for name in CORE_FILES:
        path = source / name
        if path.is_file():
            files.append(Path(name))
    return files


def _safe_path(root: Path, relative: str | Path, label: str) -> Path:
    candidate = (root / relative).resolve()
    if not is_within(candidate, root):
        raise ValueError(f"unsafe {label} path escapes root: {relative}")
    return candidate


def _source_path(source: Path, relative: Path) -> Path:
    if relative.parts and relative.parts[0] in CORE_DIRS:
        return _safe_path(source / ".opencode", relative, "source")
    return _safe_path(source, relative, "source")


def _plan_core(
    source: Path,
    target: Path,
    manifest: InstallManifest | None,
    force: bool,
) -> list[PlanItem]:
    items: list[PlanItem] = []
    for relative in _iter_core_files(source):
        source_path = _source_path(source, relative)
        target_path = _safe_path(target, relative, "target")
        if not target_path.exists():
            items.append(PlanItem(relative.as_posix(), "create", source_path, target_path))
            continue

        source_hash = sha256_file(source_path)
        target_hash = sha256_file(target_path)
        if source_hash == target_hash:
            items.append(
                PlanItem(relative.as_posix(), "skip", source_path, target_path, "identical")
            )
            continue

        installed_hash = None
        if manifest is not None:
            installed_hash = manifest.files.get(relative.as_posix(), {}).get("sha256")

        if installed_hash == target_hash:
            items.append(
                PlanItem(relative.as_posix(), "overwrite", source_path, target_path, "managed")
            )
        elif force:
            items.append(
                PlanItem(
                    relative.as_posix(),
                    "overwrite",
                    source_path,
                    target_path,
                    "forced",
                )
            )
        else:
            items.append(
                PlanItem(
                    relative.as_posix(),
                    "conflict",
                    source_path,
                    target_path,
                    "modified since install",
                )
            )
    return items


def plan_install(
    source: Path,
    target: Path,
    *,
    force: bool = False,
    merge_config: bool = False,
    manifest: InstallManifest | None = None,
) -> InstallPlan:
    """Build a plan without writing anything."""
    source = source.resolve()
    target = target.resolve()
    _validate_source(source)

    if manifest is None:
        manifest = load_install(target)

    plan = InstallPlan(source=source, target=target)
    plan.items = _plan_core(source, target, manifest, force)

    config_path = target / "opencode.jsonc"
    if not config_path.exists():
        plan.config_action = "create"
    elif (
        manifest is not None
        and manifest.config.get("action") == "created"
        and manifest.config.get("sha256") == sha256_file(config_path)
    ):
        plan.config_action = "managed"
    elif merge_config:
        plan.config_action = "merge"
    else:
        plan.config_action = "skip"
        plan.warnings.append(
            "existing opencode.jsonc was left unchanged; use --merge-config to merge"
        )

    agents_path = target / "AGENTS.md"
    if not agents_path.exists():
        plan.agents_action = "create"
    elif has_block(read_text(agents_path)):
        plan.agents_action = "replace"
    else:
        plan.agents_action = "append"

    return plan


def print_plan(plan: InstallPlan, *, dry_run: bool = False) -> None:
    lines = [
        "Daedalus global install",
        f"  source: {plan.source}",
        f"  target: {plan.target}",
        f"  config: {plan.config_action}",
        f"  AGENTS.md: {plan.agents_action}",
        "",
        "  files:",
    ]
    for item in plan.items:
        suffix = f" ({item.reason})" if item.reason else ""
        lines.append(f"    {item.action:9} {item.relative}{suffix}")
    if plan.warnings:
        lines.append("")
        lines.append("  warnings:")
        lines.extend(f"    {warning}" for warning in plan.warnings)
    if plan.conflicts:
        lines.append("")
        lines.append(f"  conflicts: {len(plan.conflicts)}")
    if dry_run:
        lines.append("")
        lines.append("Dry run: no files were changed.")
    print("\n".join(lines))


def _backup_file(path: Path, backup_dir: Path, target: Path) -> str | None:
    if not path.exists():
        return None
    destination = backup_dir / path.relative_to(target)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    return destination.relative_to(target).as_posix()


def _copy_item(item: PlanItem, backup_dir: Path, target: Path) -> dict[str, Any]:
    backup = _backup_file(item.target, backup_dir, target)
    item.target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(item.source, item.target)
    record = file_record(item.target)
    if backup:
        record["backup"] = backup
    return record


def _merge_config(target_config: dict[str, Any], source_config: dict[str, Any]) -> dict[str, Any]:
    merged = dict(target_config)

    if "default_agent" not in merged:
        merged["default_agent"] = source_config.get("default_agent", "orchestrator")

    instructions = merged.get("instructions")
    if not isinstance(instructions, list):
        instructions = []
    for entry in source_config.get("instructions", []):
        if isinstance(entry, str) and entry not in instructions:
            instructions.append(entry)
    if instructions:
        merged["instructions"] = instructions

    source_permissions = source_config.get("permissions", [])
    permissions = merged.get("permissions")
    if not isinstance(permissions, list):
        permissions = []
    if isinstance(source_permissions, list):
        existing = [rule for rule in permissions if isinstance(rule, dict)]
        additions = [
            rule for rule in source_permissions if isinstance(rule, dict) and rule not in existing
        ]
        if additions:
            merged["permissions"] = additions + permissions

    source_agents = source_config.get("agents")
    if isinstance(source_agents, dict):
        agents = merged.get("agents")
        if not isinstance(agents, dict):
            agents = {}
        for agent_id, source_agent in source_agents.items():
            if not isinstance(source_agent, dict):
                continue
            target_agent = agents.get(agent_id)
            if not isinstance(target_agent, dict):
                agents[agent_id] = dict(source_agent)
                continue
            merged_agent = dict(target_agent)
            source_rules = source_agent.get("permissions")
            target_rules = target_agent.get("permissions")
            if isinstance(source_rules, list):
                if not isinstance(target_rules, list):
                    target_rules = []
                combined: list[Any] = []
                for rule in [*source_rules, *target_rules]:
                    if rule not in combined:
                        combined.append(rule)
                merged_agent["permissions"] = combined
            agents[agent_id] = merged_agent
        merged["agents"] = agents

    return merged


def _install_config(source_config: dict[str, Any], target: Path) -> dict[str, Any]:
    """Make relative instruction paths valid from the global config directory."""
    config = dict(source_config)
    instructions = config.get("instructions")
    if not isinstance(instructions, list):
        return config
    resolved: list[Any] = []
    for entry in instructions:
        if entry == "CONVENTIONS.md":
            resolved.append(str((target / "CONVENTIONS.md").resolve()))
        else:
            resolved.append(entry)
    config["instructions"] = resolved
    return config


def _write_config(
    plan: InstallPlan,
    backup_dir: Path,
) -> dict[str, Any]:
    target_config = plan.target / "opencode.jsonc"
    source_config = plan.source / "opencode.jsonc"

    if plan.config_action == "create":
        target_config.parent.mkdir(parents=True, exist_ok=True)
        try:
            source = load_jsonc(source_config)
        except JsoncError as exc:
            raise ValueError(f"cannot read source config: {exc}") from exc
        if not isinstance(source, dict):
            raise ValueError("source opencode.jsonc must contain an object")
        dump_jsonc(target_config, _install_config(source, plan.target))
        return {"action": "created", **file_record(target_config)}

    if plan.config_action == "managed":
        return {"action": "created", **file_record(target_config)}

    if plan.config_action == "merge":
        backup = _backup_file(target_config, backup_dir, plan.target)
        try:
            current = load_jsonc(target_config)
            source = load_jsonc(source_config)
        except JsoncError as exc:
            raise ValueError(f"cannot merge config: {exc}") from exc
        if not isinstance(current, dict) or not isinstance(source, dict):
            raise ValueError("cannot merge config: both files must contain objects")
        merged = _merge_config(current, _install_config(source, plan.target))
        dump_jsonc(target_config, merged)
        record = {"action": "merged", **file_record(target_config)}
        if backup:
            record["backup"] = backup
        return record

    if target_config.exists():
        return {"action": "skipped", **file_record(target_config)}
    return {"action": "skipped"}


def _write_agents_md(
    plan: InstallPlan,
    backup_dir: Path,
) -> dict[str, Any]:
    target_agents = plan.target / "AGENTS.md"
    source_agents = read_text(plan.source / "AGENTS.md")
    existing = read_text(target_agents) if target_agents.exists() else ""
    updated = apply_block(existing, source_agents)

    if updated == existing:
        record: dict[str, Any] = {"action": "unchanged", **file_record(target_agents)}
        return record

    backup = _backup_file(target_agents, backup_dir, plan.target)
    atomic_write_text(target_agents, updated)
    record = {"action": plan.agents_action, **file_record(target_agents)}
    if backup:
        record["backup"] = backup
    return record


def install_global(
    *,
    source: Path | None = None,
    target: Path | None = None,
    dry_run: bool = False,
    force: bool = False,
    merge_config: bool = False,
) -> int:
    """Install the global core. Returns a process exit code."""
    source_path = (source or source_root()).resolve()
    target_path = (target or opencode_config_dir()).resolve()
    plan = plan_install(
        source_path,
        target_path,
        force=force,
        merge_config=merge_config,
    )
    print_plan(plan, dry_run=dry_run)

    if plan.conflicts and not force:
        print("\nInstall aborted: resolve conflicts or use --force.")
        return 3
    if dry_run:
        return 0

    target_path.mkdir(parents=True, exist_ok=True)
    backup_dir = target_path / ".daedalus" / "backups" / utc_now().replace(":", "-")
    backup_dir.mkdir(parents=True, exist_ok=True)

    files: dict[str, dict[str, Any]] = {}
    for item in plan.items:
        if item.action == "conflict":
            continue
        if item.action == "skip":
            files[item.relative] = file_record(item.target)
            continue
        files[item.relative] = _copy_item(item, backup_dir, target_path)

    config_record = _write_config(plan, backup_dir)
    agents_record = _write_agents_md(plan, backup_dir)

    manifest = InstallManifest(
        version=__version__,
        installed_at=utc_now(),
        updated_at=utc_now(),
        source=str(source_path),
        target=str(target_path),
        files=files,
        config=config_record,
        agents_md=agents_record,
        agents_md_block=True,
    )
    save_install(target_path, manifest)

    print("\nInstalled Daedalus globally.")
    print(f"  config: {target_path}")
    print(f"  managed files: {len(files)}")
    return 0


def _load_required_manifest(target: Path) -> InstallManifest:
    manifest = load_install(target)
    if manifest is None:
        raise ManifestError(f"Daedalus is not installed in {target}")
    return manifest


def update_global(
    *,
    source: Path | None = None,
    target: Path | None = None,
    dry_run: bool = False,
) -> int:
    """Update managed files that were not modified by the user."""
    manifest = _load_required_manifest((target or opencode_config_dir()).resolve())
    target_path = (target or Path(manifest.target)).resolve()
    source_path = (source or Path(manifest.source)).resolve()
    if not source_path.is_dir():
        source_path = source_root()

    plan = plan_install(source_path, target_path, manifest=manifest)
    print_plan(plan, dry_run=dry_run)
    if plan.conflicts:
        print("\nUpdate aborted: resolve conflicts or reinstall with --force.")
        return 3
    if dry_run:
        return 0

    backup_dir = target_path / ".daedalus" / "backups" / utc_now().replace(":", "-")
    backup_dir.mkdir(parents=True, exist_ok=True)

    files: dict[str, dict[str, Any]] = {}
    for item in plan.items:
        if item.action == "skip":
            files[item.relative] = file_record(item.target)
        else:
            files[item.relative] = _copy_item(item, backup_dir, target_path)

    config_action = manifest.config.get("action")
    if config_action == "created" and plan.config_action == "create":
        config_record = _write_config(plan, backup_dir)
    elif config_action == "created" and (target_path / "opencode.jsonc").exists():
        current = target_path / "opencode.jsonc"
        if manifest.config.get("sha256") == sha256_file(current):
            plan.config_action = "create"
            config_record = _write_config(plan, backup_dir)
        else:
            config_record = {"action": "skipped", **file_record(current)}
    else:
        config_record = _write_config(plan, backup_dir)

    agents_record = _write_agents_md(plan, backup_dir)

    updated = InstallManifest(
        version=__version__,
        installed_at=manifest.installed_at,
        updated_at=utc_now(),
        source=str(source_path),
        target=str(target_path),
        files=files,
        config=config_record,
        agents_md=agents_record,
        agents_md_block=True,
    )
    save_install(target_path, updated)

    stale = sorted(set(manifest.files) - set(files))
    if stale:
        print("\nStale managed files were kept:")
        for relative in stale:
            print(f"  {relative}")

    print("\nUpdated Daedalus.")
    return 0


def _uninstall_plan(
    manifest: InstallManifest, target: Path, force: bool
) -> tuple[list[tuple[str, str]], list[str]]:
    actions: list[tuple[str, str]] = []
    conflicts: list[str] = []
    for relative, record in sorted(manifest.files.items()):
        path = _safe_path(target, relative, "target")
        if not path.exists():
            actions.append(("missing", relative))
            continue
        installed_hash = record.get("sha256")
        if installed_hash == sha256_file(path) or force:
            actions.append(("remove", relative))
        else:
            conflicts.append(relative)
            actions.append(("conflict", relative))
    return actions, conflicts


def uninstall_global(
    *,
    target: Path | None = None,
    dry_run: bool = False,
    force: bool = False,
) -> int:
    """Remove managed files and restore backups where possible."""
    manifest = _load_required_manifest((target or opencode_config_dir()).resolve())
    target_path = (target or Path(manifest.target)).resolve()
    actions, conflicts = _uninstall_plan(manifest, target_path, force)

    print("Daedalus global uninstall")
    print(f"  target: {target_path}")
    for action, relative in actions:
        print(f"    {action:9} {relative}")
    if conflicts:
        print(f"\n  conflicts: {len(conflicts)}")
        for relative in conflicts:
            print(f"    {relative}")
    if dry_run:
        print("\nDry run: no files were changed.")
        return 0
    if conflicts and not force:
        print("\nUninstall aborted: resolve conflicts or use --force.")
        return 3

    for relative, record in sorted(manifest.files.items()):
        path = _safe_path(target_path, relative, "target")
        backup = record.get("backup")
        if not path.exists():
            continue
        if record.get("sha256") != sha256_file(path) and not force:
            continue
        path.unlink()
        if backup:
            backup_path = _safe_path(target_path, backup, "backup")
            if backup_path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_path, path)

    config_path = target_path / "opencode.jsonc"
    if config_path.exists() and manifest.config.get("action") == "created":
        if force or manifest.config.get("sha256") == sha256_file(config_path):
            config_path.unlink()
    elif config_path.exists():
        print("\n  kept opencode.jsonc (merged or not owned by Daedalus)")

    agents_path = target_path / "AGENTS.md"
    if agents_path.exists() and has_block(read_text(agents_path)):
        current_hash = sha256_file(agents_path)
        backup = manifest.agents_md.get("backup")
        if backup and (force or manifest.agents_md.get("sha256") == current_hash):
            backup_path = _safe_path(target_path, backup, "backup")
            if backup_path.exists():
                shutil.copy2(backup_path, agents_path)
            else:
                atomic_write_text(agents_path, remove_block(read_text(agents_path)))
        else:
            updated = remove_block(read_text(agents_path))
            if updated.strip():
                atomic_write_text(agents_path, updated)
            else:
                agents_path.unlink()

    for dirname in CORE_DIRS:
        _remove_empty_dirs(target_path / dirname)

    manifest_path = target_path / ".daedalus" / "install.json"
    manifest_path.unlink(missing_ok=True)
    _remove_empty_dirs(target_path / ".daedalus")

    print("\nUninstalled Daedalus.")
    return 0


def _remove_empty_dirs(root: Path) -> None:
    if not root.is_dir():
        return
    for path in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if path.is_dir():
            with contextlib.suppress(OSError):
                path.rmdir()
    with contextlib.suppress(OSError):
        root.rmdir()
