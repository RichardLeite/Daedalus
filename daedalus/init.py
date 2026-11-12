"""Project initialization and updates."""

from __future__ import annotations

import json
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

from daedalus import __version__
from daedalus.blocks import apply_block, has_block
from daedalus.context import detect_stack
from daedalus.jsonc import JsoncError
from daedalus.manifest import (
    InstallManifest,
    ManifestError,
    ProjectManifest,
    ProjectState,
    file_record,
    load_install,
    load_project,
    load_state,
    save_project,
    save_state,
    sha256_file,
    utc_now,
)
from daedalus.paths import (
    atomic_write_text,
    find_git_root,
    opencode_config_dir,
    read_text,
    source_root,
)

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates" / "project"
KNOWLEDGE_DIRS = ("decisions", "specs")
PROFILE_SUBDIRS = ("agents", "skills", "commands", "knowledge")


@dataclass
class FileAction:
    relative: str
    action: str
    content: str | None = None
    source: Path | None = None
    reason: str = ""


@dataclass
class InitPlan:
    root: Path
    name: str
    profile: str
    stack: list[str]
    files: list[FileAction] = field(default_factory=list)
    agents_action: str = "skip"
    agents_content: str = ""
    gitignore_lines: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def conflicts(self) -> list[FileAction]:
        return [item for item in self.files if item.action == "conflict"]


def _template(name: str) -> str:
    return read_text(TEMPLATE_DIR / name)


def _render(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


def _profile_dir(profile: str) -> Path | None:
    global_profile = opencode_config_dir() / "profiles" / profile
    if (global_profile / "profile.json").is_file():
        return global_profile
    source_profile = source_root() / ".opencode" / "profiles" / profile
    if (source_profile / "profile.json").is_file():
        return source_profile
    return None


def _profile_block(profile: str) -> str:
    profile_dir = _profile_dir(profile)
    if profile_dir is None:
        return ""
    block = profile_dir / "AGENTS.block.md"
    return read_text(block).strip() if block.is_file() else ""


def _profile_extras(profile: str) -> list[Path]:
    profile_dir = _profile_dir(profile)
    if profile_dir is None:
        return []
    extras: list[Path] = []
    for subdir in PROFILE_SUBDIRS:
        base = profile_dir / subdir
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file():
                extras.append(path.relative_to(profile_dir))
    return extras


def _profile_gitignore(profile: str) -> list[str]:
    profile_dir = _profile_dir(profile)
    if profile_dir is None:
        return []
    path = profile_dir / "gitignore.append"
    if not path.is_file():
        return []
    return [line for line in read_text(path).splitlines() if line.strip()]


def _global_manifest() -> InstallManifest | None:
    try:
        return load_install(opencode_config_dir())
    except ManifestError:
        return None


def _plan_managed_file(
    root: Path,
    relative: str,
    content: str,
    state: ProjectState | None,
    *,
    update: bool,
    force: bool,
) -> FileAction:
    target = root / relative
    if not target.exists():
        return FileAction(relative, "create", content=content)
    if force:
        return FileAction(relative, "update", content=content, reason="forced")
    if update:
        installed_hash = state.files.get(relative, {}).get("sha256") if state else None
        if installed_hash == sha256_file(target):
            return FileAction(relative, "update", content=content)
        return FileAction(relative, "conflict", content=content, reason="modified since init")
    return FileAction(relative, "skip", content=content, reason="exists")


def _plan_profile_file(
    root: Path,
    relative: str,
    source: Path,
    *,
    update: bool,
    force: bool,
) -> FileAction:
    target = root / relative
    if not target.exists():
        return FileAction(relative, "create", source=source)
    if force:
        return FileAction(relative, "update", source=source, reason="forced")
    if update and sha256_file(target) == sha256_file(source):
        return FileAction(relative, "skip", source=source, reason="identical")
    return FileAction(relative, "skip", source=source, reason="exists")


def _gitignore_lines(profile: str) -> list[str]:
    lines = [line for line in _template("gitignore.append").splitlines() if line.strip()]
    for line in _profile_gitignore(profile):
        if line not in lines:
            lines.append(line)
    return lines


def plan_init(
    root: Path,
    *,
    profile: str | None = None,
    update: bool = False,
    force: bool = False,
    gitignore: bool = True,
) -> InitPlan:
    """Build a project initialization plan without writing anything."""
    root = root.resolve()
    existing_project = load_project(root)
    existing_state = load_state(root)

    resolved_profile = profile or (existing_project.profile if existing_project else "minimal")
    name = existing_project.name if existing_project else root.name
    stack = (
        existing_project.stack
        if existing_project and existing_project.stack
        else detect_stack(root)
    )

    plan = InitPlan(
        root=root,
        name=name,
        profile=resolved_profile,
        stack=stack,
    )

    if _global_manifest() is None:
        plan.warnings.append("global core is not installed; run `daedalus install --global` first")
    if _profile_dir(resolved_profile) is None and resolved_profile != "minimal":
        plan.warnings.append(f"profile {resolved_profile!r} was not found; using the core only")

    values = {
        "name": name,
        "profile": resolved_profile,
        "stack": ", ".join(stack) if stack else "unknown",
    }
    plan.files.append(
        _plan_managed_file(
            root,
            ".opencode/opencode.jsonc",
            _template("opencode.jsonc"),
            existing_state,
            update=update,
            force=force,
        )
    )
    plan.files.append(
        _plan_managed_file(
            root,
            ".opencode/knowledge/README.md",
            _template("knowledge/README.md"),
            existing_state,
            update=update,
            force=force,
        )
    )

    for dirname in KNOWLEDGE_DIRS:
        plan.files.append(
            _plan_managed_file(
                root,
                f".opencode/knowledge/{dirname}/.gitkeep",
                "",
                existing_state,
                update=update,
                force=force,
            )
        )

    project_content = (
        json.dumps(
            ProjectManifest(
                version=1,
                name=name,
                profile=resolved_profile,
                stack=stack,
                created_at=(
                    existing_project.created_at
                    if existing_project and existing_project.created_at
                    else utc_now()
                ),
            ).to_dict(),
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    plan.files.append(
        _plan_managed_file(
            root,
            ".opencode/project.json",
            project_content,
            existing_state,
            update=update,
            force=force,
        )
    )

    for relative in _profile_extras(resolved_profile):
        target_relative = (Path(".opencode") / relative).as_posix()
        if target_relative == ".opencode/knowledge/README.md":
            continue
        plan.files.append(
            _plan_profile_file(
                root,
                target_relative,
                _profile_dir(resolved_profile) / relative,  # type: ignore[operator]
                update=update,
                force=force,
            )
        )

    block = _render(_template("AGENTS.block.md"), values)
    profile_block = _profile_block(resolved_profile)
    if profile_block:
        block = f"{block.rstrip()}\n\n{_render(profile_block, values)}"
    plan.agents_content = block

    agents_path = root / "AGENTS.md"
    existing_agents = read_text(agents_path) if agents_path.is_file() else ""
    if not existing_agents.strip():
        plan.agents_action = "create"
    elif has_block(existing_agents):
        plan.agents_action = "replace"
    else:
        plan.agents_action = "append"
    updated_agents = apply_block(existing_agents, block)
    if updated_agents == existing_agents:
        plan.agents_action = "unchanged"

    if gitignore:
        plan.gitignore_lines = _gitignore_lines(resolved_profile)

    return plan


def print_plan(plan: InitPlan, *, dry_run: bool = False) -> None:
    print("Daedalus project init")
    print(f"  root: {plan.root}")
    print(f"  project: {plan.name}")
    print(f"  profile: {plan.profile}")
    print(f"  stack: {', '.join(plan.stack) or 'unknown'}")
    print("")
    print("  files:")
    for item in plan.files:
        suffix = f" ({item.reason})" if item.reason else ""
        print(f"    {item.action:9} {item.relative}{suffix}")
    print(f"    {plan.agents_action:9} AGENTS.md (managed block)")
    if plan.gitignore_lines:
        print("    update    .gitignore (managed lines)")
    if plan.warnings:
        print("")
        print("  warnings:")
        for warning in plan.warnings:
            print(f"    {warning}")
    if plan.conflicts:
        print("")
        print(f"  conflicts: {len(plan.conflicts)}")
    if dry_run:
        print("")
        print("Dry run: no files were changed.")


def _apply_gitignore(root: Path, lines: list[str]) -> None:
    path = root / ".gitignore"
    existing = read_text(path) if path.is_file() else ""
    existing_lines = set(existing.splitlines())
    additions = [line for line in lines if line not in existing_lines]
    if not additions:
        return
    if not existing:
        content = "\n".join(additions) + "\n"
    else:
        content = existing.rstrip() + "\n\n" + "\n".join(additions) + "\n"
    atomic_write_text(path, content)


def _apply_file(root: Path, item: FileAction) -> None:
    target = root / item.relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if item.content is not None:
        atomic_write_text(target, item.content)
        return
    if item.source is not None:
        shutil.copy2(item.source, target)


def apply_init(plan: InitPlan, *, gitignore: bool = True) -> ProjectState:
    """Apply an initialization plan and return the new project state."""
    plan.root.mkdir(parents=True, exist_ok=True)
    existing_state = load_state(plan.root)

    files: dict[str, dict[str, object]] = {}
    for item in plan.files:
        if item.action in {"conflict"}:
            continue
        if item.action in {"create", "update"}:
            _apply_file(plan.root, item)
        target = plan.root / item.relative
        if target.exists():
            files[item.relative] = file_record(target)

    agents_path = plan.root / "AGENTS.md"
    existing_agents = read_text(agents_path) if agents_path.is_file() else ""
    updated_agents = apply_block(existing_agents, plan.agents_content)
    if updated_agents != existing_agents:
        atomic_write_text(agents_path, updated_agents)
    if agents_path.exists():
        record = file_record(agents_path)
        record["mode"] = "managed-block"
        files["AGENTS.md"] = record

    if gitignore and plan.gitignore_lines:
        _apply_gitignore(plan.root, plan.gitignore_lines)

    now = utc_now()
    state = ProjectState(
        version=__version__,
        profile=plan.profile,
        created_at=existing_state.created_at if existing_state else now,
        updated_at=now,
        files=files,
    )
    project = ProjectManifest(
        version=1,
        name=plan.name,
        profile=plan.profile,
        stack=plan.stack,
        created_at=(
            load_project(plan.root).created_at
            if load_project(plan.root) and load_project(plan.root).created_at
            else now
        ),
    )
    save_project(plan.root, project)
    save_state(plan.root, state)
    return state


def init_project(
    *,
    path: Path,
    profile: str | None = None,
    plan: bool = False,
    yes: bool = False,
    force: bool = False,
    update: bool = False,
    gitignore: bool = True,
) -> int:
    """Initialize or update a project layer. Returns a process exit code."""
    start = path.resolve()
    if start.is_file():
        start = start.parent
    root = find_git_root(start) or start

    init_plan = plan_init(
        root,
        profile=profile,
        update=update,
        force=force,
        gitignore=gitignore,
    )
    print_plan(init_plan, dry_run=plan)

    if init_plan.conflicts and not force:
        print("\nInit aborted: resolve conflicts or use --force.")
        return 3
    if plan:
        return 0

    if not yes:
        if not sys.stdin.isatty():
            print("\nNon-interactive shell: use --yes to apply.")
            return 2
        answer = input("Apply this plan? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            print("Aborted.")
            return 2

    try:
        state = apply_init(init_plan, gitignore=gitignore)
    except (OSError, JsoncError) as exc:
        print(f"\nInit failed: {exc}")
        return 1

    print("\nProject initialized.")
    print(f"  root: {init_plan.root}")
    print(f"  profile: {state.profile}")
    print(f"  managed files: {len(state.files)}")
    return 0
