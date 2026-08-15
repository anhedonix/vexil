"""Tests for init commands and reset."""

from __future__ import annotations

from pathlib import Path

from env_init.config import VexilConfig, save_config
from env_init.init_cmds import CommandResult, initialize_vexil_io
from env_init.reset import reset_dev_env
from env_init.salt import generate_salt


def test_initialize_vexil_io_success(tmp_path: Path, monkeypatch) -> None:
    app = tmp_path / "apps" / "vexil-io"
    app.mkdir(parents=True)

    def fake_run(name, command, cwd):
        return CommandResult(name, command, cwd, 0, "ok", "")

    monkeypatch.setattr("env_init.init_cmds._run", fake_run)
    cfg = VexilConfig()
    result = initialize_vexil_io(cfg, monorepo_root=tmp_path)
    assert result.ok
    assert cfg.vexil_io.init is True


def test_initialize_vexil_io_failure(tmp_path: Path, monkeypatch) -> None:
    app = tmp_path / "apps" / "vexil-io"
    app.mkdir(parents=True)

    def fake_run(name, command, cwd):
        return CommandResult(name, command, cwd, 1, "", "boom")

    monkeypatch.setattr("env_init.init_cmds._run", fake_run)
    cfg = VexilConfig()
    result = initialize_vexil_io(cfg, monorepo_root=tmp_path)
    assert not result.ok
    assert cfg.vexil_io.init is False


def test_reset_dev_env(tmp_path: Path, monkeypatch) -> None:
    apps = tmp_path / "apps"
    for name in ("vexil-io", "vexil-frontend", "vexil-website", "docs-dev", "vexil-package-src"):
        d = apps / name
        d.mkdir(parents=True)
        (d / ".env").write_text("PORT=1\n", encoding="utf-8")
        (d / ".env.template").write_text("PORT=\n", encoding="utf-8")
    env_init = apps / "vexil-dev-tools" / "env-init"
    env_init.mkdir(parents=True)
    (env_init / ".env").write_text("PORT=6644\n", encoding="utf-8")
    scratch = tmp_path / ".scratch"
    scratch.mkdir()
    (scratch / "projects").mkdir()
    (scratch / "projects" / "a.txt").write_text("x", encoding="utf-8")

    cfg = VexilConfig()
    cfg.base.scratch = str(scratch)
    cfg.vexil_io.init = True
    cfg.vexil_io.dir_project_root = "projects"
    cfg.vexil_io.salt = generate_salt()
    old_salt = cfg.vexil_io.salt
    toml = env_init / "vexil.toml"
    save_config(cfg, toml)
    monkeypatch.setattr("env_init.reset.save_config", lambda c, path=None: save_config(c, toml))
    monkeypatch.setattr("env_init.config.DEFAULT_TOML", toml)

    result = reset_dev_env(cfg, monorepo_root=tmp_path, env_init_root=env_init)
    assert (apps / "vexil-io" / ".env").exists() is False
    assert (apps / "vexil-io" / ".env.template").is_file()
    assert list(scratch.iterdir()) == []
    assert cfg.vexil_io.init is False
    assert cfg.vexil_io.dir_project_root == ""
    assert cfg.vexil_io.salt != old_salt
    assert result.cleared_scratch is not None
