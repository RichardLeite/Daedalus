from __future__ import annotations

from pathlib import Path

from daedalus.manifest import (
    InstallManifest,
    ProjectManifest,
    ProjectState,
    file_record,
    load_install,
    load_project,
    load_state,
    save_install,
    save_project,
    save_state,
    sha256_file,
    utc_now,
)


def test_install_manifest_round_trip(tmp_path: Path) -> None:
    manifest = InstallManifest(
        version="0.1.0",
        installed_at=utc_now(),
        source="/source",
        target="/target",
        files={"agents/orchestrator.md": {"sha256": "abc", "size": 10}},
        config={"created": True},
        agents_md_block=True,
    )
    save_install(tmp_path, manifest)
    loaded = load_install(tmp_path)
    assert loaded is not None
    assert loaded.version == "0.1.0"
    assert loaded.files["agents/orchestrator.md"]["size"] == 10
    assert loaded.agents_md_block is True


def test_project_manifest_and_state_round_trip(tmp_path: Path) -> None:
    project = ProjectManifest(
        version=1,
        name="demo",
        profile="backend",
        stack=["python"],
        created_at=utc_now(),
    )
    save_project(tmp_path, project)
    assert load_project(tmp_path) == project

    state = ProjectState(
        version="0.1.0",
        profile="backend",
        created_at=utc_now(),
        updated_at=utc_now(),
        files={"AGENTS.md": {"sha256": "abc"}},
    )
    save_state(tmp_path, state)
    assert load_state(tmp_path) == state


def test_file_record_and_hash(tmp_path: Path) -> None:
    path = tmp_path / "file.txt"
    path.write_text("daedalus", encoding="utf-8")
    assert sha256_file(path) == file_record(path)["sha256"]
    assert file_record(path)["size"] == 8
