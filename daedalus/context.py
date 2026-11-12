"""Project context resolution for the Daedalus orchestrator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from daedalus.manifest import (
    ManifestError,
    load_install,
    load_project,
    load_state,
)
from daedalus.paths import (
    find_git_root,
    git_branch,
    git_dirty,
    opencode_config_dir,
    source_root,
)

STACK_MARKERS: list[tuple[str, str]] = [
    ("package.json", "node"),
    ("pyproject.toml", "python"),
    ("requirements.txt", "python"),
    ("go.mod", "go"),
    ("Cargo.toml", "rust"),
    ("pom.xml", "java"),
    ("build.gradle", "java"),
    ("Gemfile", "ruby"),
    ("composer.json", "php"),
    ("docker-compose.yml", "docker"),
    ("docker-compose.yaml", "docker"),
    ("Dockerfile", "docker"),
]


def detect_stack(root: Path) -> list[str]:
    """Detect project stacks from well-known marker files."""
    stacks: list[str] = []
    for filename, stack in STACK_MARKERS:
        if (root / filename).exists() and stack not in stacks:
            stacks.append(stack)
    if any(root.glob("*.csproj")) and "dotnet" not in stacks:
        stacks.append("dotnet")
    if any(root.glob("*.sln")) and "dotnet" not in stacks:
        stacks.append("dotnet")
    return stacks


def build_context(project_path: Path) -> dict[str, Any]:
    """Build a JSON-serialisable context for the current project."""
    path = project_path.resolve()
    git_root = find_git_root(path)
    root = git_root or path

    project = None
    state = None
    try:
        project = load_project(root)
        state = load_state(root)
    except ManifestError:
        project = None
        state = None

    global_manifest = None
    try:
        global_manifest = load_install(opencode_config_dir())
    except ManifestError:
        global_manifest = None

    return {
        "root": str(root),
        "path": str(path),
        "project": project.name if project else root.name,
        "profile": project.profile if project else "minimal",
        "stack": project.stack if project and project.stack else detect_stack(root),
        "initialized": project is not None and state is not None,
        "git": {
            "root": str(git_root) if git_root else None,
            "branch": git_branch(root) if git_root else None,
            "dirty": git_dirty(root) if git_root else None,
        },
        "global": {
            "installed": global_manifest is not None,
            "version": global_manifest.version if global_manifest else None,
            "config_dir": str(opencode_config_dir()),
            "source": str(source_root()),
        },
    }


def format_text(context: dict[str, Any]) -> str:
    lines = [
        "Daedalus context",
        f"  project: {context['project']}",
        f"  profile: {context['profile']}",
        f"  root: {context['root']}",
        f"  stack: {', '.join(context['stack']) or 'unknown'}",
        f"  initialized: {context['initialized']}",
    ]
    git = context["git"]
    if git["root"]:
        lines.append(f"  git: {git['branch']} (dirty={git['dirty']})")
    else:
        lines.append("  git: not a repository")
    global_info = context["global"]
    version = global_info["version"] or "not installed"
    lines.append(f"  global: {version}")
    return "\n".join(lines)
