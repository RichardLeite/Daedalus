from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CI = REPO_ROOT / ".github" / "workflows" / "ci.yml"
RELEASE = REPO_ROOT / ".github" / "workflows" / "release.yml"


def test_ci_workflow_tests_all_platforms_and_installers() -> None:
    text = CI.read_text(encoding="utf-8")
    assert "ubuntu-latest" in text
    assert "macos-latest" in text
    assert "windows-latest" in text
    assert "installers:" in text
    assert "install.sh" in text
    assert "install.ps1" in text
    assert "--source ." in text
    assert "-Source ." in text


def test_release_workflow_builds_and_publishes_artifacts() -> None:
    text = RELEASE.read_text(encoding="utf-8")
    assert 'tags: ["v*"]' in text
    assert "python -m build" in text
    assert "git archive" in text
    assert "source.tar.gz" in text
    assert "SHA256SUMS" in text
    assert "gh release create" in text
    assert "actions/upload-artifact" in text
