"""Discover and bump product patch versions across the monorepo."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from env_init.config import MONOREPO_ROOT

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

# Relative paths from monorepo root → how to read/write the product version.
VERSION_TARGETS: tuple[tuple[str, str], ...] = (
    ("package.json", "json"),
    ("apps/vexil-io/package.json", "json"),
    ("apps/vexil-frontend/package.json", "json"),
    ("apps/vexil-website/package.json", "json"),
    ("apps/docs-dev/package.json", "json"),
    ("apps/vexil-package-src/package.json", "json"),
    ("apps/vexil-package-src/pyproject.toml", "pyproject"),
    ("apps/vexil-dev-tools/env-init/pyproject.toml", "pyproject"),
    ("apps/vexil-dev-tools/env-init/vexil.toml", "vexil_toml"),
)

UV_LOCK_DIRS: tuple[str, ...] = (
    "apps/vexil-package-src",
    "apps/vexil-dev-tools/env-init",
)


class VersionBumpError(ValueError):
    """Raised when versions cannot be discovered or applied."""


@dataclass(frozen=True)
class VersionChange:
    path: Path
    field: str
    old: str
    new: str
    kind: str


def parse_semver(version: str) -> tuple[int, int, int]:
    match = SEMVER_RE.match(version.strip())
    if not match:
        raise VersionBumpError(f"Invalid semver (expected MAJOR.MINOR.PATCH): {version!r}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_patch(version: str) -> str:
    major, minor, patch = parse_semver(version)
    return f"{major}.{minor}.{patch + 1}"


def _read_json_version(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    version = data.get("version")
    if not isinstance(version, str):
        raise VersionBumpError(f"Missing string version in {path}")
    return version


def _write_json_version(path: Path, new_version: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["version"] = new_version
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _read_pyproject_version(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', text)
    if not match:
        raise VersionBumpError(f"Missing [project] version in {path}")
    return match.group(1)


def _write_pyproject_version(path: Path, new_version: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(
        r'(?m)^(version\s*=\s*")([^"]+)("\s*$)',
        rf"\g<1>{new_version}\g<3>",
        text,
        count=1,
    )
    if count != 1:
        raise VersionBumpError(f"Could not surgically update version in {path}")
    path.write_text(updated, encoding="utf-8")


def _read_vexil_toml_version(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    # Prefer [base] version = "..." near the top of the file.
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', text)
    if not match:
        raise VersionBumpError(f"Missing base.version in {path}")
    return match.group(1)


def _write_vexil_toml_version(path: Path, new_version: str) -> None:
    """Update only the first top-level version = "..." line (base.version)."""
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(
        r'(?m)^(version\s*=\s*")([^"]+)("\s*$)',
        rf"\g<1>{new_version}\g<3>",
        text,
        count=1,
    )
    if count != 1:
        raise VersionBumpError(f"Could not surgically update base.version in {path}")
    path.write_text(updated, encoding="utf-8")


def _read_version(path: Path, kind: str) -> str:
    if kind == "json":
        return _read_json_version(path)
    if kind == "pyproject":
        return _read_pyproject_version(path)
    if kind == "vexil_toml":
        return _read_vexil_toml_version(path)
    raise VersionBumpError(f"Unknown version kind: {kind}")


def _write_version(path: Path, kind: str, new_version: str) -> None:
    if kind == "json":
        _write_json_version(path, new_version)
        return
    if kind == "pyproject":
        _write_pyproject_version(path, new_version)
        return
    if kind == "vexil_toml":
        _write_vexil_toml_version(path, new_version)
        return
    raise VersionBumpError(f"Unknown version kind: {kind}")


def _field_label(kind: str) -> str:
    if kind == "json":
        return "version"
    if kind == "pyproject":
        return "project.version"
    return "base.version"


def discover_version_changes(monorepo_root: Path | None = None) -> list[VersionChange]:
    root = (monorepo_root or MONOREPO_ROOT).resolve()
    readings: list[tuple[Path, str, str]] = []
    for rel, kind in VERSION_TARGETS:
        path = root / rel
        if not path.is_file():
            raise VersionBumpError(f"Missing version file: {path}")
        readings.append((path, kind, _read_version(path, kind)))

    versions = {version for _, _, version in readings}
    if len(versions) != 1:
        details = ", ".join(f"{path}: {version}" for path, _, version in readings)
        raise VersionBumpError(f"Version mismatch across monorepo files: {details}")

    current = next(iter(versions))
    new_version = bump_patch(current)
    return [
        VersionChange(
            path=path,
            field=_field_label(kind),
            old=current,
            new=new_version,
            kind=kind,
        )
        for path, kind, _ in readings
    ]


def apply_version_changes(
    changes: list[VersionChange],
    *,
    refresh_locks: bool = True,
    monorepo_root: Path | None = None,
) -> list[VersionChange]:
    if not changes:
        raise VersionBumpError("No version changes to apply")
    for change in changes:
        _write_version(change.path, change.kind, change.new)
    if refresh_locks:
        root = (monorepo_root or MONOREPO_ROOT).resolve()
        _refresh_uv_locks(root)
    return changes


def _refresh_uv_locks(root: Path) -> None:
    uv = shutil.which("uv") or "uv"
    for rel in UV_LOCK_DIRS:
        cwd = root / rel
        if not (cwd / "pyproject.toml").is_file():
            continue
        proc = subprocess.run(
            [uv, "lock"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise VersionBumpError(
                f"uv lock failed in {cwd}: {proc.stderr.strip() or proc.stdout.strip()}"
            )


def preview_lines(changes: list[VersionChange], monorepo_root: Path | None = None) -> list[str]:
    root = (monorepo_root or MONOREPO_ROOT).resolve()
    lines: list[str] = []
    for change in changes:
        try:
            rel = change.path.relative_to(root)
        except ValueError:
            rel = change.path
        lines.append(f"{rel} ({change.field}): {change.old} → {change.new}")
    return lines
