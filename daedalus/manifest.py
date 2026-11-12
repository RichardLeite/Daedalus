"""Manifest and project-state helpers.

Daedalus records what it installed so that updates and uninstalls never touch
files it does not own. Project state is stored in ``.opencode/.daedalus.json``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from daedalus.paths import atomic_write_text


class ManifestError(ValueError):
    """Raised when a manifest is missing or malformed."""


def utc_now() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path) -> dict[str, Any]:
    """Return a small record describing a managed file."""
    return {"sha256": sha256_file(path), "size": path.stat().st_size}


def _load_json(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ManifestError(f"cannot read {path}: {exc}") from exc
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ManifestError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ManifestError(f"expected an object in {path}")
    return value


def _save_json(path: Path, value: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


@dataclass
class InstallManifest:
    """Record of a global installation."""

    version: str
    installed_at: str
    source: str
    target: str
    files: dict[str, dict[str, Any]] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    agents_md: dict[str, Any] = field(default_factory=dict)
    agents_md_block: bool = False
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> InstallManifest:
        return cls(
            version=str(value.get("version", "")),
            installed_at=str(value.get("installed_at", "")),
            source=str(value.get("source", "")),
            target=str(value.get("target", "")),
            files=dict(value.get("files", {})),
            config=dict(value.get("config", {})),
            agents_md=dict(value.get("agents_md", {})),
            agents_md_block=bool(value.get("agents_md_block", False)),
            updated_at=str(value.get("updated_at", "")),
        )


@dataclass
class ProjectManifest:
    """Project-level Daedalus manifest."""

    version: int
    name: str
    profile: str
    stack: list[str] = field(default_factory=list)
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> ProjectManifest:
        return cls(
            version=int(value.get("version", 1)),
            name=str(value.get("name", "")),
            profile=str(value.get("profile", "minimal")),
            stack=list(value.get("stack", [])),
            created_at=str(value.get("created_at", "")),
        )


@dataclass
class ProjectState:
    """Record of files managed inside a project."""

    version: str
    profile: str
    created_at: str
    updated_at: str
    files: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> ProjectState:
        return cls(
            version=str(value.get("version", "")),
            profile=str(value.get("profile", "minimal")),
            created_at=str(value.get("created_at", "")),
            updated_at=str(value.get("updated_at", "")),
            files=dict(value.get("files", {})),
        )


def install_manifest_path(config_dir: Path) -> Path:
    return config_dir / ".daedalus" / "install.json"


def project_manifest_path(project_root: Path) -> Path:
    return project_root / ".opencode" / "project.json"


def project_state_path(project_root: Path) -> Path:
    return project_root / ".opencode" / ".daedalus.json"


def load_install(config_dir: Path) -> InstallManifest | None:
    path = install_manifest_path(config_dir)
    if not path.exists():
        return None
    return InstallManifest.from_dict(_load_json(path))


def save_install(config_dir: Path, manifest: InstallManifest) -> None:
    _save_json(install_manifest_path(config_dir), manifest.to_dict())


def load_project(project_root: Path) -> ProjectManifest | None:
    path = project_manifest_path(project_root)
    if not path.exists():
        return None
    return ProjectManifest.from_dict(_load_json(path))


def save_project(project_root: Path, manifest: ProjectManifest) -> None:
    _save_json(project_manifest_path(project_root), manifest.to_dict())


def load_state(project_root: Path) -> ProjectState | None:
    path = project_state_path(project_root)
    if not path.exists():
        return None
    return ProjectState.from_dict(_load_json(path))


def save_state(project_root: Path, state: ProjectState) -> None:
    _save_json(project_state_path(project_root), state.to_dict())
