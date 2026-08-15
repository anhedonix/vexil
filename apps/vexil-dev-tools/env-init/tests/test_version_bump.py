"""Tests for monorepo patch version bump."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from env_init.version_bump import (
    VersionBumpError,
    apply_version_changes,
    bump_patch,
    discover_version_changes,
    parse_semver,
    preview_lines,
)


def _write_fixture(root: Path, version: str = "0.1.2") -> None:
    targets = [
        ("package.json", "json"),
        ("apps/vexil-io/package.json", "json"),
        ("apps/vexil-frontend/package.json", "json"),
        ("apps/vexil-website/package.json", "json"),
        ("apps/docs-dev/package.json", "json"),
        ("apps/vexil-package-src/package.json", "json"),
        ("apps/vexil-package-src/pyproject.toml", "pyproject"),
        ("apps/vexil-dev-tools/env-init/pyproject.toml", "pyproject"),
        ("apps/vexil-dev-tools/env-init/vexil.toml", "vexil_toml"),
    ]
    for rel, kind in targets:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if kind == "json":
            path.write_text(
                json.dumps({"name": path.parent.name or "root", "version": version}, indent=2)
                + "\n",
                encoding="utf-8",
            )
        elif kind == "pyproject":
            path.write_text(
                f'[project]\nname = "demo"\nversion = "{version}"\n',
                encoding="utf-8",
            )
        else:
            path.write_text(
                f'[base]\nversion = "{version}"\ndev = true\n\n[vexil-io]\nport = 6600\n',
                encoding="utf-8",
            )


def test_bump_patch_math() -> None:
    assert bump_patch("0.1.2") == "0.1.3"
    assert parse_semver("1.2.3") == (1, 2, 3)
    with pytest.raises(VersionBumpError):
        bump_patch("1.2")


def test_discover_and_preview(tmp_path: Path) -> None:
    _write_fixture(tmp_path, "0.1.2")
    changes = discover_version_changes(tmp_path)
    assert len(changes) == 9
    assert all(c.old == "0.1.2" and c.new == "0.1.3" for c in changes)
    lines = preview_lines(changes, tmp_path)
    assert any("vexil.toml" in line and "0.1.2 → 0.1.3" in line for line in lines)


def test_mismatch_raises(tmp_path: Path) -> None:
    _write_fixture(tmp_path, "0.1.2")
    (tmp_path / "package.json").write_text(
        json.dumps({"name": "vexil", "version": "0.1.9"}, indent=2) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(VersionBumpError, match="mismatch"):
        discover_version_changes(tmp_path)


def test_apply_surgical_vexil_toml(tmp_path: Path) -> None:
    _write_fixture(tmp_path, "0.1.2")
    vexil = tmp_path / "apps/vexil-dev-tools/env-init/vexil.toml"
    original_extra = "\n[frontend]\nport = 6611\n"
    vexil.write_text(
        '[base]\nversion = "0.1.2"\ndev = true\nos = "darwin"\n' + original_extra,
        encoding="utf-8",
    )
    changes = discover_version_changes(tmp_path)
    apply_version_changes(changes, refresh_locks=False, monorepo_root=tmp_path)
    text = vexil.read_text(encoding="utf-8")
    assert 'version = "0.1.3"' in text
    assert "dev = true" in text
    assert "[frontend]" in text
    assert "port = 6611" in text
    root_pkg = json.loads((tmp_path / "package.json").read_text(encoding="utf-8"))
    assert root_pkg["version"] == "0.1.3"
    pyproject = (tmp_path / "apps/vexil-dev-tools/env-init/pyproject.toml").read_text(
        encoding="utf-8"
    )
    assert 'version = "0.1.3"' in pyproject
