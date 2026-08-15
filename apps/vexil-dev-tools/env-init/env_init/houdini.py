"""Discover Houdini 22+ preference profiles and install vexil.json."""

from __future__ import annotations

import json
import os
import platform
import re
from dataclasses import dataclass
from pathlib import Path

from env_init.config import MONOREPO_ROOT, VexilConfig, save_config

VERSION_RE = re.compile(r"(?:houdini)?(?P<major>\d+)\.(?P<minor>\d+)", re.IGNORECASE)
MIN_MAJOR = 22

PACKAGE_TEMPLATE = MONOREPO_ROOT / "apps" / "vexil-package-src" / "houdini_package" / "vexil.json"
PACKAGE_SRC = MONOREPO_ROOT / "apps" / "vexil-package-src"


@dataclass(frozen=True, order=True)
class HoudiniProfile:
    version: tuple[int, int]
    path: Path

    @property
    def label(self) -> str:
        major, minor = self.version
        return f"Houdini {major}.{minor} — {self.path}"


def parse_houdini_version(text: str) -> tuple[int, int] | None:
    match = VERSION_RE.search(text.replace("__HVER__", "99.99"))
    if not match:
        return None
    return int(match.group("major")), int(match.group("minor"))


def _home() -> Path:
    return Path.home()


def candidate_pref_roots() -> list[Path]:
    """Return directories that may contain houdiniX.Y preference folders."""
    home = _home()
    roots: list[Path] = [home]
    system = platform.system().lower()
    if system == "darwin":
        roots.append(home / "Library" / "Preferences" / "houdini")
    elif system == "windows":
        docs = Path(os.environ.get("USERPROFILE", str(home))) / "Documents"
        roots.append(docs)
    pref = os.environ.get("HOUDINI_USER_PREF_DIR")
    if pref:
        # Expand __HVER__ by scanning parent for versioned dirs later
        expanded = Path(os.path.expandvars(pref.replace("__HVER__", "*")))
        roots.append(expanded.parent)
        roots.append(Path(os.path.expandvars(pref.split("__HVER__")[0].rstrip("/\\"))))
    # Deduplicate while preserving order
    seen: set[Path] = set()
    out: list[Path] = []
    for root in roots:
        try:
            resolved = root.expanduser().resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        out.append(resolved)
    return out


def discover_houdini_profiles(min_major: int = MIN_MAJOR) -> list[HoudiniProfile]:
    profiles: dict[Path, HoudiniProfile] = {}
    for root in candidate_pref_roots():
        if not root.exists():
            continue
        # Direct versioned dirs under home: ~/houdini22.0
        for child in root.iterdir() if root.is_dir() else []:
            if not child.is_dir():
                continue
            version = parse_houdini_version(child.name)
            if version is None or version[0] < min_major:
                continue
            profiles[child.resolve()] = HoudiniProfile(version=version, path=child.resolve())
        # Also match houdini/22.0 style (mac Preferences)
        if root.name.lower() == "houdini" or (root / "houdini").is_dir():
            base = root if root.name.lower() == "houdini" else root / "houdini"
            if base.is_dir():
                for child in base.iterdir():
                    if not child.is_dir():
                        continue
                    version = parse_houdini_version(child.name)
                    if version is None or version[0] < min_major:
                        continue
                    profiles[child.resolve()] = HoudiniProfile(
                        version=version, path=child.resolve()
                    )
    return sorted(profiles.values(), reverse=True)


def render_package_manifest(
    package_src: Path | None = None,
    template_path: Path | None = None,
) -> dict:
    src = (package_src or PACKAGE_SRC).resolve()
    template = template_path or PACKAGE_TEMPLATE
    if template.is_file():
        data = json.loads(template.read_text(encoding="utf-8"))
    else:
        data = {
            "path": "$VEXIL_PACKAGE",
            "env": [{"PYTHONPATH": "$VEXIL_PACKAGE/python"}],
        }
    package_path = str(src)
    python_path = str(src / "python")
    # Replace placeholders
    raw = json.dumps(data)
    raw = raw.replace("$VEXIL_PACKAGE", package_path)
    raw = raw.replace("<path-to-repo-root>/apps/vexil-package-src", package_path)
    rendered = json.loads(raw)
    rendered["path"] = package_path
    env = rendered.get("env") or []
    # Ensure PYTHONPATH points at package python dir
    found = False
    for item in env:
        if isinstance(item, dict) and "PYTHONPATH" in item:
            item["PYTHONPATH"] = python_path
            found = True
    if not found:
        env.append({"PYTHONPATH": python_path})
    rendered["env"] = env
    # Validate JSON-serializable
    json.dumps(rendered)
    return rendered


def install_houdini_package(
    cfg: VexilConfig,
    profile: Path,
    *,
    package_src: Path | None = None,
    template_path: Path | None = None,
) -> Path:
    profile = profile.resolve()
    packages_dir = profile / "packages"
    packages_dir.mkdir(parents=True, exist_ok=True)
    dest = packages_dir / "vexil.json"
    manifest = render_package_manifest(package_src=package_src, template_path=template_path)
    tmp = dest.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    tmp.replace(dest)
    cfg.houdini_package.install_path = str(profile)
    cfg.houdini_package.init = True
    cfg.vexil_io.houdini_dir = str(profile)
    save_config(cfg)
    return dest


def copy_template_into_repo(template_path: Path | None = None) -> Path:
    """Ensure the source template exists under package-src/houdini_package."""
    dest = template_path or PACKAGE_TEMPLATE
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.is_file():
        content = {
            "path": "$VEXIL_PACKAGE",
            "env": [{"PYTHONPATH": "$VEXIL_PACKAGE/python"}],
        }
        dest.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")
    return dest
