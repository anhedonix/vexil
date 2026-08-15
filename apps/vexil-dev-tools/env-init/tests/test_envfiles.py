"""Tests for .env rendering."""

from __future__ import annotations

from pathlib import Path

from env_init.config import VexilConfig
from env_init.envfiles import preview_env_files, write_env_files
from env_init.salt import generate_salt


def test_preview_redacts_secrets_in_templates() -> None:
    cfg = VexilConfig()
    cfg.vexil_io.salt = generate_salt()
    cfg.vexil_io.password = "secret-pass"
    cfg.website.resend_api_key = "re_secret"
    preview = preview_env_files(cfg, monorepo_root=Path("/tmp/vexil-fake"))
    template = next(p for p in preview if p.name == ".env.template" and "vexil-io" in str(p))
    body = preview[template]
    assert "VEXIL_SALT=" in body
    assert cfg.vexil_io.salt not in body
    assert "secret-pass" not in body
    env = next(p for p in preview if p.name == ".env" and "vexil-io" in str(p))
    assert cfg.vexil_io.salt in preview[env]


def test_write_env_files(tmp_path: Path) -> None:
    apps = tmp_path / "apps"
    for name in (
        "vexil-io",
        "vexil-frontend",
        "vexil-website",
        "docs-dev",
        "vexil-package-src",
        "vexil-dev-tools/env-init",
    ):
        (apps / name).mkdir(parents=True)
    cfg = VexilConfig()
    cfg.vexil_io.salt = generate_salt()
    cfg.vexil_io.port = 6600
    written = write_env_files(cfg, monorepo_root=tmp_path)
    assert any(p.name == ".env" and p.parent.name == "vexil-io" for p in written)
    content = (apps / "vexil-io" / ".env").read_text(encoding="utf-8")
    assert "PORT=6600" in content
    template = (apps / "vexil-io" / ".env.template").read_text(encoding="utf-8")
    assert "VEXIL_SALT=" in template
    assert cfg.vexil_io.salt not in template
