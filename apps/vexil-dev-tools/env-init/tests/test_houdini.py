"""Tests for Houdini profile discovery and package install."""

from __future__ import annotations

import json
from pathlib import Path

from env_init.config import VexilConfig, save_config
from env_init.houdini import (
    discover_houdini_profiles,
    install_houdini_package,
    parse_houdini_version,
    render_package_manifest,
)


def test_parse_houdini_version() -> None:
    assert parse_houdini_version("houdini22.0") == (22, 0)
    assert parse_houdini_version("21.5") == (21, 5)
    assert parse_houdini_version("nope") is None


def test_discover_filters_below_22(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "home"
    home.mkdir()
    (home / "houdini21.5").mkdir()
    (home / "houdini22.0").mkdir()
    (home / "houdini23.0").mkdir()
    monkeypatch.setattr("env_init.houdini._home", lambda: home)
    monkeypatch.setattr("env_init.houdini.platform.system", lambda: "Linux")
    monkeypatch.delenv("HOUDINI_USER_PREF_DIR", raising=False)
    profiles = discover_houdini_profiles()
    versions = {p.version for p in profiles}
    assert (22, 0) in versions
    assert (23, 0) in versions
    assert (21, 5) not in versions


def test_render_and_install(tmp_path: Path, monkeypatch) -> None:
    package_src = tmp_path / "apps" / "vexil-package-src"
    (package_src / "python").mkdir(parents=True)
    template = package_src / "houdini_package" / "vexil.json"
    template.parent.mkdir(parents=True)
    template.write_text(
        json.dumps({"path": "$VEXIL_PACKAGE", "env": [{"PYTHONPATH": "$VEXIL_PACKAGE/python"}]}),
        encoding="utf-8",
    )
    manifest = render_package_manifest(package_src=package_src, template_path=template)
    assert manifest["path"] == str(package_src.resolve())
    assert manifest["env"][0]["PYTHONPATH"].endswith("python")

    profile = tmp_path / "houdini22.0"
    profile.mkdir()
    cfg = VexilConfig()
    toml = tmp_path / "vexil.toml"
    monkeypatch.setattr(
        "env_init.houdini.save_config",
        lambda c, path=None: save_config(c, toml),
    )
    dest = install_houdini_package(
        cfg,
        profile,
        package_src=package_src,
        template_path=template,
    )
    assert dest.is_file()
    data = json.loads(dest.read_text(encoding="utf-8"))
    assert data["path"] == str(package_src.resolve())
    assert cfg.houdini_package.init is True
