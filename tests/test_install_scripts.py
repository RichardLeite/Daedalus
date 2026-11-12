from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_install_scripts_exist() -> None:
    assert (REPO_ROOT / "install.sh").is_file()
    assert (REPO_ROOT / "install.ps1").is_file()
    shell = (REPO_ROOT / "install.sh").read_text(encoding="utf-8")
    powershell = (REPO_ROOT / "install.ps1").read_text(encoding="utf-8")
    assert shell.startswith("#!/usr/bin/env bash")
    assert "opencode.ai/v2/install" in shell
    assert "[CmdletBinding()]" in powershell
    assert "Anomaly.OpenCode" in powershell


@pytest.mark.skipif(sys.platform == "win32", reason="bash path mapping on Windows")
def test_shell_script_syntax_and_help() -> None:
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash is not installed")
    syntax = subprocess.run(
        [bash, "-n", "install.sh"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert syntax.returncode == 0, syntax.stderr

    help_result = subprocess.run(
        [bash, "install.sh", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert help_result.returncode == 0
    assert "Daedalus installer" in help_result.stdout

    dry_run = subprocess.run(
        [bash, "install.sh", "--dry-run"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert dry_run.returncode == 0
    assert "opencode:" in dry_run.stdout


@pytest.mark.skipif(sys.platform != "win32", reason="Windows PowerShell")
def test_powershell_script_syntax_and_help() -> None:
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if powershell is None:
        pytest.skip("PowerShell is not installed")
    syntax = subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-Command",
            "[scriptblock]::Create((Get-Content -Raw 'install.ps1')) | Out-Null",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert syntax.returncode == 0, syntax.stderr

    help_result = subprocess.run(
        [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "install.ps1", "-Help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert help_result.returncode == 0
    assert "Daedalus installer" in help_result.stdout

    dry_run = subprocess.run(
        [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "install.ps1", "-DryRun"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert dry_run.returncode == 0
    assert "opencode:" in dry_run.stdout
