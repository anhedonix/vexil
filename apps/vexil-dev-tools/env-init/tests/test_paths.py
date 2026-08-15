"""Tests for scratch path containment."""

from __future__ import annotations

from pathlib import Path

import pytest

from env_init.config import VexilConfig
from env_init.paths import (
    PathValidationError,
    create_dev_dirs,
    ensure_under_scratch,
    resolve_scratch,
)


def test_ensure_under_scratch_accepts_child(tmp_path: Path) -> None:
    scratch = tmp_path / ".scratch"
    scratch.mkdir()
    path = ensure_under_scratch("projects", scratch, field_name="dir_project_root")
    assert path == (scratch / "projects").resolve()


def test_ensure_under_scratch_rejects_escape(tmp_path: Path) -> None:
    scratch = tmp_path / ".scratch"
    scratch.mkdir()
    with pytest.raises(PathValidationError):
        ensure_under_scratch(tmp_path / "outside", scratch, field_name="dir_project_root")


def test_create_dev_dirs(tmp_path: Path) -> None:
    env_init_root = tmp_path / "apps" / "vexil-dev-tools" / "env-init"
    env_init_root.mkdir(parents=True)
    scratch = tmp_path / ".scratch"
    cfg = VexilConfig()
    cfg.base.dev = True
    cfg.base.scratch = str(scratch)
    cfg.vexil_io.dir_project_root = "projects"
    cfg.vexil_io.dir_data_root = "data"
    created = create_dev_dirs(cfg, env_init_root=env_init_root)
    assert (scratch / "projects").is_dir()
    assert (scratch / "data").is_dir()
    assert resolve_scratch(cfg, env_init_root) == scratch.resolve()
    assert scratch.resolve() in {p.resolve() for p in created}
