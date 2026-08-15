"""Tests for .env rendering (local files only)."""

from __future__ import annotations

from pathlib import Path

from env_init.config import VexilConfig
from env_init.envfiles import preview_env_files, write_env_files
from env_init.salt import generate_salt


def test_preview_only_env_files() -> None:
    cfg = VexilConfig()
    cfg.vexil_io.salt = generate_salt()
    cfg.vexil_io.password = "secret-pass"
    preview = preview_env_files(cfg, monorepo_root=Path("/tmp/vexil-fake"))
    assert preview
    assert all(p.name == ".env" for p in preview)
    assert not any(".env.template" in str(p) for p in preview)
    env = next(p for p in preview if "vexil-io" in str(p))
    assert cfg.vexil_io.salt in preview[env]
    assert "secret-pass" in preview[env]


def test_write_env_files_preserves_templates(tmp_path: Path) -> None:
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
    template = apps / "vexil-io" / ".env.template"
    template.write_text("# tracked template\nPORT=\n", encoding="utf-8")
    example = apps / "vexil-website" / ".env.example"
    example.write_text("RESEND_API_KEY=\n", encoding="utf-8")

    cfg = VexilConfig()
    cfg.vexil_io.salt = generate_salt()
    cfg.vexil_io.port = 6600
    written = write_env_files(cfg, monorepo_root=tmp_path)

    assert all(p.name == ".env" for p in written)
    assert any(p.parent.name == "vexil-io" for p in written)
    content = (apps / "vexil-io" / ".env").read_text(encoding="utf-8")
    assert "PORT=6600" in content
    assert template.read_text(encoding="utf-8") == "# tracked template\nPORT=\n"
    assert example.read_text(encoding="utf-8") == "RESEND_API_KEY=\n"
