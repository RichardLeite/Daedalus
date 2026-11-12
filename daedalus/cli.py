"""Command-line interface for Daedalus."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from daedalus import __version__
from daedalus.context import build_context
from daedalus.context import format_text as format_context
from daedalus.doctor import format_text as format_doctor
from daedalus.doctor import has_failures, run_checks
from daedalus.doctor import to_dict as doctor_to_dict
from daedalus.jsonc import JsoncError
from daedalus.manifest import ManifestError
from daedalus.validate import validate_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="daedalus",
        description="Portable development configuration for OpenCode.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    install = subparsers.add_parser("install", help="Install the global core")
    install.add_argument("--global", dest="global_", action="store_true")
    install.add_argument("--source", type=Path, default=None)
    install.add_argument("--dir", dest="target_dir", type=Path, default=None)
    install.add_argument("--dry-run", action="store_true")
    install.add_argument("--force", action="store_true")
    install.add_argument("--merge-config", action="store_true")
    install.set_defaults(handler=_cmd_install)

    update = subparsers.add_parser("update", help="Update the global core")
    update.add_argument("--global", dest="global_", action="store_true")
    update.add_argument("--source", type=Path, default=None)
    update.add_argument("--dir", dest="target_dir", type=Path, default=None)
    update.add_argument("--dry-run", action="store_true")
    update.set_defaults(handler=_cmd_update)

    uninstall = subparsers.add_parser("uninstall", help="Remove the global core")
    uninstall.add_argument("--global", dest="global_", action="store_true")
    uninstall.add_argument("--dir", dest="target_dir", type=Path, default=None)
    uninstall.add_argument("--dry-run", action="store_true")
    uninstall.add_argument("--force", action="store_true")
    uninstall.set_defaults(handler=_cmd_uninstall)

    init = subparsers.add_parser("init", help="Create or update the project layer")
    init.add_argument("--path", type=Path, default=Path("."))
    init.add_argument("--profile", default=None)
    init.add_argument("--plan", action="store_true")
    init.add_argument("--yes", action="store_true")
    init.add_argument("--force", action="store_true")
    init.add_argument("--update", action="store_true")
    init.add_argument("--no-gitignore", action="store_true")
    init.set_defaults(handler=_cmd_init)

    context = subparsers.add_parser("context", help="Show project context")
    context.add_argument("--path", type=Path, default=Path("."))
    context.add_argument("--json", action="store_true")
    context.set_defaults(handler=_cmd_context)

    doctor = subparsers.add_parser("doctor", help="Diagnose the environment")
    doctor.add_argument("--path", type=Path, default=Path("."))
    doctor.add_argument("--json", action="store_true")
    doctor.set_defaults(handler=_cmd_doctor)

    validate = subparsers.add_parser("validate", help="Validate the configuration")
    validate.add_argument("--root", type=Path, default=Path("."))
    validate.add_argument("--global", dest="global_", action="store_true")
    validate.add_argument("--json", action="store_true")
    validate.add_argument("--strict", action="store_true")
    validate.set_defaults(handler=_cmd_validate)

    return parser


def _require_global(args: argparse.Namespace, command: str) -> bool:
    if not getattr(args, "global_", False):
        print(
            f"daedalus {command}: only --global is supported in v0.1",
            file=sys.stderr,
        )
        return False
    return True


def _cmd_install(args: argparse.Namespace) -> int:
    if not _require_global(args, "install"):
        return 2
    from daedalus.install import install_global

    return install_global(
        source=args.source,
        target=args.target_dir,
        dry_run=args.dry_run,
        force=args.force,
        merge_config=args.merge_config,
    )


def _cmd_update(args: argparse.Namespace) -> int:
    if not _require_global(args, "update"):
        return 2
    from daedalus.install import update_global

    return update_global(
        source=args.source,
        target=args.target_dir,
        dry_run=args.dry_run,
    )


def _cmd_uninstall(args: argparse.Namespace) -> int:
    if not _require_global(args, "uninstall"):
        return 2
    from daedalus.install import uninstall_global

    return uninstall_global(
        target=args.target_dir,
        dry_run=args.dry_run,
        force=args.force,
    )


def _cmd_init(args: argparse.Namespace) -> int:
    from daedalus.init import init_project

    return init_project(
        path=args.path,
        profile=args.profile,
        plan=args.plan,
        yes=args.yes,
        force=args.force,
        update=args.update,
        gitignore=not args.no_gitignore,
    )


def _cmd_context(args: argparse.Namespace) -> int:
    context = build_context(args.path)
    if args.json:
        print(json.dumps(context, indent=2, ensure_ascii=False))
    else:
        print(format_context(context))
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    checks = run_checks(args.path)
    if args.json:
        print(json.dumps(doctor_to_dict(checks), indent=2, ensure_ascii=False))
    else:
        print(format_doctor(checks))
    return 1 if has_failures(checks) else 0


def _cmd_validate(args: argparse.Namespace) -> int:
    result = validate_root(
        args.root,
        strict=args.strict,
        global_layout=getattr(args, "global_", False),
    )
    if args.json:
        print(json.dumps(result.to_dict(args.root.resolve()), indent=2, ensure_ascii=False))
    else:
        print(result.format_text(args.root.resolve()))
    return 0 if result.ok else 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (JsoncError, ManifestError, OSError, ValueError) as exc:
        print(f"daedalus: error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
