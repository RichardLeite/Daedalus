"""Validation for Daedalus agents, commands, skills, and OpenCode V2 config."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from daedalus.jsonc import JsoncError
from daedalus.jsonc import load as load_jsonc
from daedalus.paths import read_text


class FrontmatterError(ValueError):
    """Raised when a Markdown frontmatter block cannot be parsed."""


AGENT_ALLOWED = {"description", "mode", "model", "color", "hidden", "steps"}
AGENT_V1 = {
    "temperature",
    "permission",
    "prompt",
    "tools",
    "disable",
    "maxSteps",
    "skills",
    "trigger",
    "projects",
}
AGENT_MODES = {"primary", "subagent", "all"}

COMMAND_ALLOWED = {"description", "agent", "model", "subagent", "subtask"}

SKILL_ALLOWED = {
    "name",
    "description",
    "license",
    "compatibility",
    "disable-model-invocation",
    "metadata",
}

CONFIG_V1_KEYS = {"agent", "permission", "plugin", "reference"}
BUILTIN_AGENTS = {"build", "plan", "general", "explore"}

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Private key", re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
]

ABSOLUTE_PATH_PATTERNS = [
    re.compile(r"[A-Za-z]:\\Users\\"),
    re.compile(r"/home/[^/\s]+/"),
    re.compile(r"/Users/[^/\s]+/"),
]


@dataclass
class ValidationResult:
    """Errors and warnings collected while validating a configuration."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checked: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def format_text(self, root: Path) -> str:
        lines = [
            "Daedalus validation",
            f"  root: {root}",
            f"  checked: {self.checked}",
            f"  errors: {len(self.errors)}",
            f"  warnings: {len(self.warnings)}",
        ]
        if self.errors:
            lines.append("")
            lines.append("Errors:")
            lines.extend(f"  - {item}" for item in self.errors)
        if self.warnings:
            lines.append("")
            lines.append("Warnings:")
            lines.extend(f"  - {item}" for item in self.warnings)
        if self.ok:
            lines.append("")
            lines.append("Result: OK")
        else:
            lines.append("")
            lines.append("Result: FAILED")
        return "\n".join(lines)

    def to_dict(self, root: Path) -> dict[str, Any]:
        return {
            "root": str(root),
            "ok": self.ok,
            "checked": self.checked,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
        }


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse a flat or one-level nested YAML frontmatter block.

    Daedalus intentionally keeps its own frontmatter flat. This parser also
    accepts one level of nesting so that portable V2 skills with a ``metadata``
    map can be validated without adding a YAML dependency.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    end: int | None = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        raise FrontmatterError("unterminated frontmatter")

    data: dict[str, Any] = {}
    current: str | None = None

    for raw in lines[1:end]:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if line[0].isspace():
            if current is None:
                raise FrontmatterError(f"unexpected indentation: {stripped!r}")
            if stripped.startswith("- "):
                if not isinstance(data.get(current), list):
                    data[current] = []
                data[current].append(_parse_scalar(stripped[2:].strip()))
                continue
            key, separator, value = stripped.partition(":")
            if not separator:
                raise FrontmatterError(f"invalid nested frontmatter line: {stripped!r}")
            if not isinstance(data.get(current), dict):
                data[current] = {}
            data[current][key.strip()] = _parse_scalar(value.strip())
            continue

        key, separator, value = line.partition(":")
        if not separator:
            raise FrontmatterError(f"invalid frontmatter line: {line!r}")
        key = key.strip()
        value = value.strip()
        current = key
        if value == "":
            data[key] = {}
        else:
            data[key] = _parse_scalar(value)
            current = None

    body = "\n".join(lines[end + 1 :])
    return data, body


def _parse_scalar(value: str) -> Any:
    if value == "":
        return ""
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1]
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(item.strip()) for item in inner.split(",")]
    return value


def _validate_permissions(value: Any, label: str, result: ValidationResult) -> None:
    if not isinstance(value, list):
        result.error(f"{label}: permissions must be a list")
        return
    for index, rule in enumerate(value):
        if not isinstance(rule, dict):
            result.error(f"{label}: permission #{index} must be an object")
            continue
        for key in ("action", "resource", "effect"):
            if not isinstance(rule.get(key), str) or not rule.get(key):
                result.error(f"{label}: permission #{index} is missing {key!r}")
        effect = rule.get("effect")
        if effect not in {"allow", "ask", "deny"}:
            result.error(f"{label}: permission #{index} has invalid effect {effect!r}")


def validate_agents(agents_dir: Path, result: ValidationResult) -> set[str]:
    ids: set[str] = set()
    if not agents_dir.is_dir():
        return ids

    for path in sorted(agents_dir.rglob("*.md")):
        relative = path.relative_to(agents_dir).with_suffix("").as_posix()
        result.checked += 1
        try:
            frontmatter, body = parse_frontmatter(read_text(path))
        except (OSError, FrontmatterError) as exc:
            result.error(f"agents/{relative}: {exc}")
            continue

        if not frontmatter:
            result.error(f"agents/{relative}: missing frontmatter")
            continue
        if relative in ids:
            result.error(f"agents/{relative}: duplicate agent id")
        ids.add(relative)

        description = frontmatter.get("description")
        if not isinstance(description, str) or not description.strip():
            result.error(f"agents/{relative}: description is required")

        for key in frontmatter:
            if key in AGENT_V1:
                result.error(f"agents/{relative}: V1 field {key!r} is not allowed")
            elif key not in AGENT_ALLOWED:
                result.warn(f"agents/{relative}: unknown frontmatter field {key!r}")

        mode = frontmatter.get("mode")
        if mode is None:
            result.warn(f"agents/{relative}: mode is missing (defaults to primary)")
        elif mode not in AGENT_MODES:
            result.error(f"agents/{relative}: invalid mode {mode!r}")

        steps = frontmatter.get("steps")
        if steps is not None and (
            isinstance(steps, bool) or not isinstance(steps, int) or steps < 1
        ):
            result.error(f"agents/{relative}: steps must be a positive integer")

        hidden = frontmatter.get("hidden")
        if hidden is not None and not isinstance(hidden, bool):
            result.error(f"agents/{relative}: hidden must be a boolean")

        color = frontmatter.get("color")
        if color is not None and not (
            isinstance(color, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", color)
        ):
            result.error(f"agents/{relative}: color must be a six-digit hex value")

        if not body.strip():
            result.warn(f"agents/{relative}: empty system prompt")

    return ids


def validate_commands(commands_dir: Path, result: ValidationResult) -> set[str]:
    ids: set[str] = set()
    if not commands_dir.is_dir():
        return ids

    for path in sorted(commands_dir.rglob("*.md")):
        relative = path.relative_to(commands_dir).with_suffix("").as_posix()
        result.checked += 1
        try:
            text = read_text(path)
            frontmatter, body = parse_frontmatter(text)
        except (OSError, FrontmatterError) as exc:
            result.error(f"commands/{relative}: {exc}")
            continue

        if relative in ids:
            result.error(f"commands/{relative}: duplicate command id")
        ids.add(relative)

        if "template" in frontmatter:
            result.error(
                f"commands/{relative}: template must be the Markdown body, not frontmatter"
            )

        for key in frontmatter:
            if key not in COMMAND_ALLOWED:
                result.warn(f"commands/{relative}: unknown frontmatter field {key!r}")

        if not isinstance(frontmatter.get("description"), str):
            result.warn(f"commands/{relative}: description is recommended")

        subagent = frontmatter.get("subagent")
        if subagent is not None and not isinstance(subagent, bool):
            result.error(f"commands/{relative}: subagent must be a boolean")

        if "subtask" in frontmatter:
            result.warn(f"commands/{relative}: subtask is deprecated; use subagent")

        if not body.strip():
            result.error(f"commands/{relative}: empty prompt template")

    return ids


def validate_skills(skills_dir: Path, result: ValidationResult) -> set[str]:
    ids: set[str] = set()
    if not skills_dir.is_dir():
        return ids

    paths = list(skills_dir.rglob("SKILL.md"))
    paths.extend(path for path in skills_dir.glob("*.md") if path.name != "SKILL.md")

    for path in sorted(paths):
        if path.name == "SKILL.md":
            skill_id = path.parent.name
            label = path.parent.relative_to(skills_dir).as_posix()
        else:
            skill_id = path.stem
            label = path.relative_to(skills_dir).as_posix()
        result.checked += 1

        try:
            frontmatter, body = parse_frontmatter(read_text(path))
        except (OSError, FrontmatterError) as exc:
            result.error(f"skills/{label}: {exc}")
            continue

        if skill_id in ids:
            result.error(f"skills/{label}: duplicate skill id {skill_id!r}")
        ids.add(skill_id)

        description = frontmatter.get("description")
        if not isinstance(description, str) or not description.strip():
            result.error(f"skills/{label}: description is required for discovery")

        for key in frontmatter:
            if key not in SKILL_ALLOWED:
                result.warn(f"skills/{label}: unknown frontmatter field {key!r}")

        disable = frontmatter.get("disable-model-invocation")
        if disable is not None and not isinstance(disable, bool):
            result.error(f"skills/{label}: disable-model-invocation must be a boolean")

        metadata = frontmatter.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            result.error(f"skills/{label}: metadata must be a mapping")

        if not body.strip():
            result.warn(f"skills/{label}: empty SKILL.md body")

    return ids


def _validate_agent_config(agent_id: str, value: Any, result: ValidationResult) -> None:
    if not isinstance(value, dict):
        result.error(f"config agents.{agent_id}: must be an object")
        return
    for key in value:
        if key in AGENT_V1:
            result.error(f"config agents.{agent_id}: V1 field {key!r} is not allowed")
    if "permissions" in value:
        _validate_permissions(value["permissions"], f"config agents.{agent_id}", result)
    mode = value.get("mode")
    if mode is not None and mode not in AGENT_MODES:
        result.error(f"config agents.{agent_id}: invalid mode {mode!r}")


def validate_config(
    root: Path,
    agent_ids: set[str],
    skill_ids: set[str],
    result: ValidationResult,
    *,
    global_layout: bool = False,
) -> None:
    candidates: list[Path] = []
    if not global_layout:
        candidates.extend(
            [root / ".opencode" / "opencode.jsonc", root / ".opencode" / "opencode.json"]
        )
    candidates.extend([root / "opencode.jsonc", root / "opencode.json"])
    existing = [path for path in candidates if path.exists()]
    if len(existing) > 1:
        result.warn("multiple OpenCode config files found; keep one")
    if not existing:
        result.warn("no opencode.jsonc found")
        return
    path = existing[0]

    result.checked += 1
    try:
        config = load_jsonc(path)
    except JsoncError as exc:
        result.error(str(exc))
        return
    if not isinstance(config, dict):
        result.error(f"{path.name}: top-level value must be an object")
        return

    for key in CONFIG_V1_KEYS:
        if key in config:
            result.error(f"{path.name}: V1 key {key!r} is not allowed")

    if "mcp" in config:
        mcp = config["mcp"]
        if not isinstance(mcp, dict) or "servers" not in mcp:
            result.error(f"{path.name}: V1 mcp shape; use mcp.servers")
        elif not isinstance(mcp["servers"], dict):
            result.error(f"{path.name}: mcp.servers must be an object")
        else:
            for name, server in mcp["servers"].items():
                if not isinstance(server, dict):
                    result.error(f"{path.name}: mcp.servers.{name} must be an object")
                    continue
                server_type = server.get("type")
                if server_type not in {"local", "remote"}:
                    result.error(f"{path.name}: mcp.servers.{name}.type must be local or remote")
                if server_type == "local" and not isinstance(server.get("command"), list):
                    result.error(f"{path.name}: mcp.servers.{name}.command must be a list")
                if server_type == "remote" and not isinstance(server.get("url"), str):
                    result.error(f"{path.name}: mcp.servers.{name}.url must be a string")

    if "permissions" in config:
        _validate_permissions(config["permissions"], f"{path.name}", result)

    instructions = config.get("instructions")
    if instructions is not None:
        if not isinstance(instructions, list) or not all(
            isinstance(item, str) for item in instructions
        ):
            result.error(f"{path.name}: instructions must be a list of strings")
        else:
            for item in instructions:
                if item.startswith(("http://", "https://")) or Path(item).is_absolute():
                    continue
                if not (root / item).exists():
                    result.error(f"{path.name}: instruction file not found: {item}")

    default_agent = config.get("default_agent")
    if default_agent is not None:
        if not isinstance(default_agent, str):
            result.error(f"{path.name}: default_agent must be a string")
        elif default_agent not in agent_ids and default_agent not in BUILTIN_AGENTS:
            result.error(f"{path.name}: default_agent {default_agent!r} has no agent file")

    agents = config.get("agents")
    if agents is not None:
        if not isinstance(agents, dict):
            result.error(f"{path.name}: agents must be an object")
        else:
            for agent_id, value in agents.items():
                _validate_agent_config(str(agent_id), value, result)
                if str(agent_id) not in agent_ids and str(agent_id) not in BUILTIN_AGENTS:
                    result.warn(f"{path.name}: agents.{agent_id} has no matching agent file")
                if isinstance(value, dict) and isinstance(value.get("permissions"), list):
                    for rule in value["permissions"]:
                        if (
                            isinstance(rule, dict)
                            and rule.get("action") == "skill"
                            and rule.get("resource") not in {"*", None}
                            and rule["resource"] not in skill_ids
                        ):
                            result.warn(
                                f"{path.name}: agents.{agent_id} references unknown skill "
                                f"{rule['resource']!r}"
                            )

    skills = config.get("skills")
    if skills is not None and not (
        isinstance(skills, list) and all(isinstance(item, str) for item in skills)
    ):
        result.error(f"{path.name}: skills must be a list of strings")


def _iter_text_files(root: Path, *, global_layout: bool = False) -> list[Path]:
    files: list[Path] = []
    bases: list[Path] = []
    if global_layout:
        bases = [
            root / name
            for name in ("agents", "commands", "skills", "rules", "templates", "profiles")
        ]
    else:
        bases = [root / ".opencode"]
    for base in bases:
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if any(part in {"__pycache__", ".git", "node_modules", ".venv"} for part in path.parts):
                continue
            if path.suffix.lower() in {
                ".md",
                ".json",
                ".jsonc",
                ".yaml",
                ".yml",
                ".toml",
                ".py",
                ".sh",
                ".ps1",
            }:
                files.append(path)
    for name in ("opencode.jsonc", "opencode.json", "AGENTS.md", "CONVENTIONS.md"):
        path = root / name
        if path.is_file():
            files.append(path)
    return files


def scan_text(root: Path, result: ValidationResult, *, global_layout: bool = False) -> None:
    for path in _iter_text_files(root, global_layout=global_layout):
        try:
            text = read_text(path)
        except OSError as exc:
            result.warn(f"{path}: cannot read: {exc}")
            continue
        try:
            label = path.relative_to(root).as_posix()
        except ValueError:
            label = str(path)

        for name, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                result.error(f"{label}: possible {name} found")

        for pattern in ABSOLUTE_PATH_PATTERNS:
            match = pattern.search(text)
            if match:
                result.warn(f"{label}: machine-specific absolute path found")
                break


def validate_project_metadata(root: Path, result: ValidationResult) -> None:
    """Validate the optional project manifest and state files."""
    project_path = root / ".opencode" / "project.json"
    state_path = root / ".opencode" / ".daedalus.json"

    if project_path.exists():
        result.checked += 1
        try:
            project = json.loads(project_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            result.error(f"project.json: {exc}")
            project = None
        if project is not None:
            if not isinstance(project, dict):
                result.error("project.json: top-level value must be an object")
            else:
                if not isinstance(project.get("version"), int):
                    result.error("project.json: version must be an integer")
                if not isinstance(project.get("name"), str) or not project.get("name"):
                    result.error("project.json: name must be a non-empty string")
                if not isinstance(project.get("profile"), str) or not project.get("profile"):
                    result.error("project.json: profile must be a non-empty string")
                if not (
                    isinstance(project.get("stack"), list)
                    and all(isinstance(item, str) for item in project.get("stack", []))
                ):
                    result.error("project.json: stack must be a list of strings")

    if state_path.exists():
        result.checked += 1
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            result.error(f".daedalus.json: {exc}")
            state = None
        if state is not None and not isinstance(state, dict):
            result.error(".daedalus.json: top-level value must be an object")

    agents_path = root / "AGENTS.md"
    if state_path.exists() and agents_path.is_file():
        try:
            if "<!-- daedalus:begin" not in read_text(agents_path):
                result.warn("AGENTS.md: managed block is missing")
        except OSError:
            result.warn("AGENTS.md: cannot read")


def validate_root(
    root: Path, *, strict: bool = False, global_layout: bool = False
) -> ValidationResult:
    """Validate a Daedalus repository, project root, or global config dir."""
    result = ValidationResult()
    root = root.resolve()
    if not root.is_dir():
        result.error(f"root is not a directory: {root}")
        return result

    base = root if global_layout else root / ".opencode"
    if not base.is_dir():
        result.warn("no .opencode directory found")

    agent_ids = validate_agents(base / "agents", result)
    validate_commands(base / "commands", result)
    skill_ids = validate_skills(base / "skills", result)
    validate_config(root, agent_ids, skill_ids, result, global_layout=global_layout)
    if not global_layout:
        validate_project_metadata(root, result)
    scan_text(root, result, global_layout=global_layout)

    if strict and result.warnings:
        result.errors.extend(f"strict: {item}" for item in result.warnings)
        result.warnings.clear()

    return result
