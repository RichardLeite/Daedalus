"""Path helpers shared by the Daedalus CLI.

All paths are handled with :class:`pathlib.Path` and UTF-8 text. The module
never assumes a particular operating system or shell.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def home() -> Path:
    """Return the current user's home directory."""
    return Path.home()


def config_home() -> Path:
    """Return the platform configuration directory.

    ``XDG_CONFIG_HOME`` wins when set. Otherwise ``~/.config`` is used, which is
    also what OpenCode documents for its global configuration on every platform.
    """
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg).expanduser().resolve()
    return home() / ".config"


def opencode_config_dir() -> Path:
    """Return the global OpenCode configuration directory.

    ``DAEDALUS_CONFIG_DIR`` overrides the location for tests and non-standard
    installations. Otherwise the standard OpenCode config directory is used.
    """
    override = os.environ.get("DAEDALUS_CONFIG_DIR")
    if override:
        return Path(override).expanduser().resolve()
    return config_home() / "opencode"


def source_root() -> Path:
    """Return the repository root that contains the Python package."""
    return Path(__file__).resolve().parent.parent


def is_within(path: Path, root: Path) -> bool:
    """Return ``True`` when *path* is inside *root* (including *root* itself)."""
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def find_git_root(start: Path) -> Path | None:
    """Walk up from *start* until a directory containing ``.git`` is found."""
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def read_text(path: Path) -> str:
    """Read UTF-8 text from *path*."""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    """Write UTF-8 text to *path*, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def atomic_write_text(path: Path, text: str) -> None:
    """Write *text* to *path* atomically using a temporary file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def which(name: str) -> str | None:
    """Return the executable path for *name*, if available."""
    return shutil.which(name)


def command_version(command: list[str], timeout: float = 5.0) -> str | None:
    """Run *command* and return its first output line, or ``None`` on failure."""
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = (completed.stdout or completed.stderr or "").strip()
    if completed.returncode != 0 or not output:
        return None
    return output.splitlines()[0]


def git_branch(root: Path) -> str | None:
    """Return the current branch name for *root*."""
    return command_version(["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"])


def git_dirty(root: Path) -> bool | None:
    """Return whether *root* has uncommitted changes, or ``None`` on failure."""
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    return bool(completed.stdout.strip())
