"""Environment diagnostics for the Daedalus CLI."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from daedalus import __version__
from daedalus.jsonc import JsoncError
from daedalus.jsonc import load as load_jsonc
from daedalus.manifest import (
    ManifestError,
    install_manifest_path,
    load_install,
    load_project,
    load_state,
    project_manifest_path,
    project_state_path,
)
from daedalus.paths import (
    command_version,
    find_git_root,
    opencode_config_dir,
    read_text,
    source_root,
    which,
)


@dataclass
class Check:
    """One diagnostic check."""

    name: str
    status: str
    detail: str
    hint: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _check(
    name: str,
    condition: bool,
    detail: str,
    hint: str = "",
    *,
    warning: bool = False,
) -> Check:
    if condition:
        return Check(name, "ok", detail)
    return Check(name, "warn" if warning else "fail", detail, hint)


def _gh_auth() -> tuple[bool, str]:
    if not which("gh"):
        return False, "gh is not installed"
    try:
        completed = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"gh auth status failed: {exc}"
    if completed.returncode == 0:
        return True, "authenticated"
    output = (completed.stderr or completed.stdout or "").strip().splitlines()
    detail = output[0] if output else "not authenticated"
    return False, detail


def run_checks(project_path: Path) -> list[Check]:
    """Run diagnostics for the machine and the given project."""
    checks: list[Check] = []
    project_path = project_path.resolve()

    checks.append(
        _check(
            "python",
            sys.version_info >= (3, 11),
            f"{sys.version.split()[0]} ({sys.executable})",
            "Install Python 3.11 or newer.",
        )
    )

    git_version = command_version(["git", "--version"])
    checks.append(
        _check(
            "git",
            git_version is not None,
            git_version or "git not found",
            "Install Git and ensure it is on PATH.",
        )
    )

    gh_version = command_version(["gh", "--version"])
    checks.append(
        _check(
            "gh",
            gh_version is not None,
            gh_version or "gh not found",
            "Install the GitHub CLI from https://cli.github.com/.",
            warning=True,
        )
    )

    gh_ok, gh_detail = _gh_auth()
    checks.append(
        _check(
            "gh auth",
            gh_ok,
            gh_detail,
            "Run `gh auth login`.",
            warning=True,
        )
    )

    opencode_version = command_version(["opencode", "--version"])
    checks.append(
        _check(
            "opencode",
            opencode_version is not None,
            opencode_version or "opencode not found",
            "Install OpenCode and ensure it is on PATH.",
            warning=True,
        )
    )

    repo_root = source_root()
    checks.append(
        _check(
            "source",
            (repo_root / ".opencode" / "agents").is_dir(),
            str(repo_root),
            "Run the CLI from a Daedalus checkout.",
        )
    )

    config_dir = opencode_config_dir()
    try:
        manifest = load_install(config_dir)
    except ManifestError as exc:
        manifest = None
        checks.append(Check("global install", "fail", str(exc), "Reinstall the global core."))
    else:
        if manifest is None:
            checks.append(
                Check(
                    "global install",
                    "warn",
                    f"not installed in {config_dir}",
                    "Run `daedalus install --global`.",
                )
            )
        else:
            checks.append(
                _check(
                    "global install",
                    manifest.version == __version__,
                    f"v{manifest.version} in {config_dir}",
                    f"Run `daedalus update --global` (CLI is v{__version__}).",
                    warning=manifest.version != __version__,
                )
            )

    config_path = config_dir / "opencode.jsonc"
    if not config_path.exists():
        checks.append(
            Check(
                "global config",
                "warn",
                f"missing {config_path}",
                "Run `daedalus install --global`.",
            )
        )
    else:
        try:
            config = load_jsonc(config_path)
        except JsoncError as exc:
            checks.append(Check("global config", "fail", str(exc), "Fix the JSONC syntax."))
        else:
            instructions = config.get("instructions", []) if isinstance(config, dict) else []
            has_conventions = isinstance(instructions, list) and any(
                isinstance(entry, str) and entry.endswith("CONVENTIONS.md")
                for entry in instructions
            )
            checks.append(
                _check(
                    "global config",
                    has_conventions,
                    f"{config_path}",
                    'Add "CONVENTIONS.md" to instructions, or run '
                    "`daedalus install --global --merge-config`.",
                    warning=not has_conventions,
                )
            )

    agents_md = config_dir / "AGENTS.md"
    checks.append(
        _check(
            "global AGENTS.md",
            agents_md.is_file(),
            str(agents_md),
            "Run `daedalus install --global`.",
            warning=True,
        )
    )

    git_root = find_git_root(project_path)
    checks.append(
        _check(
            "project git",
            git_root is not None,
            str(git_root or project_path),
            "Run `git init` before initializing the project layer.",
            warning=True,
        )
    )
    project_root = git_root or project_path

    checks.append(
        _check(
            "project manifest",
            project_manifest_path(project_root).is_file(),
            str(project_manifest_path(project_root)),
            "Run `daedalus init`.",
            warning=True,
        )
    )
    checks.append(
        _check(
            "project state",
            project_state_path(project_root).is_file(),
            str(project_state_path(project_root)),
            "Run `daedalus init`.",
            warning=True,
        )
    )

    project_agents = project_root / "AGENTS.md"
    has_block = False
    if project_agents.is_file():
        try:
            has_block = "<!-- daedalus:begin" in read_text(project_agents)
        except OSError:
            has_block = False
    checks.append(
        _check(
            "project AGENTS.md",
            has_block,
            str(project_agents),
            "Run `daedalus init` or add the managed block.",
            warning=True,
        )
    )

    try:
        project = load_project(project_root)
        state = load_state(project_root)
    except ManifestError as exc:
        checks.append(Check("project files", "fail", str(exc), "Fix the JSON files."))
    else:
        if project is not None and state is not None:
            checks.append(
                _check(
                    "project files",
                    project.version == 1,
                    f"{project.name} ({project.profile}, v{state.version})",
                    "Run `daedalus init --update`.",
                    warning=project.version != 1,
                )
            )

    return checks


def has_failures(checks: list[Check]) -> bool:
    return any(check.status == "fail" for check in checks)


def format_text(checks: list[Check]) -> str:
    lines = ["Daedalus doctor", ""]
    for check in checks:
        lines.append(f"[{check.status}] {check.name}: {check.detail}")
        if check.hint and check.status != "ok":
            lines.append(f"       hint: {check.hint}")
    lines.append("")
    failures = sum(1 for check in checks if check.status == "fail")
    warnings = sum(1 for check in checks if check.status == "warn")
    lines.append(f"Result: {failures} failure(s), {warnings} warning(s)")
    return "\n".join(lines)


def to_dict(checks: list[Check]) -> dict[str, Any]:
    return {
        "ok": not has_failures(checks),
        "checks": [check.to_dict() for check in checks],
    }


def install_paths() -> dict[str, str]:
    """Return the paths doctor inspected, for debugging."""
    config_dir = opencode_config_dir()
    return {
        "source": str(source_root()),
        "config_dir": str(config_dir),
        "install_manifest": str(install_manifest_path(config_dir)),
    }
