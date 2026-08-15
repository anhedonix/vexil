"""Reset generated local env artifacts for a clean developer start."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from env_init.config import MONOREPO_ROOT, VexilConfig, save_config
from env_init.paths import resolve_scratch
from env_init.salt import generate_salt

ENV_APP_DIRS = (
    "vexil-io",
    "vexil-frontend",
    "vexil-website",
    "docs-dev",
    "vexil-package-src",
    "vexil-dev-tools/env-init",
)


@dataclass
class ResetResult:
    deleted_env_files: list[Path]
    cleared_scratch: Path | None
    errors: list[str]


def _clear_directory_contents(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        return
    for child in path.iterdir():
        if child.is_symlink() or child.is_file():
            child.unlink(missing_ok=True)
        elif child.is_dir():
            shutil.rmtree(child)


def reset_dev_env(
    cfg: VexilConfig,
    *,
    monorepo_root: Path | None = None,
    env_init_root: Path | None = None,
) -> ResetResult:
    root = monorepo_root or MONOREPO_ROOT
    deleted: list[Path] = []
    errors: list[str] = []

    for rel in ENV_APP_DIRS:
        env_path = root / "apps" / rel / ".env"
        if env_path.is_file():
            try:
                env_path.unlink()
                deleted.append(env_path)
            except OSError as exc:
                errors.append(f"{env_path}: {exc}")

    scratch = resolve_scratch(cfg, env_init_root)
    monorepo_scratch = (root / ".scratch").resolve()
    try:
        # Only clear if scratch resolves under monorepo .scratch or equals it
        scratch.relative_to(monorepo_scratch)
        safe = True
    except ValueError:
        safe = scratch == monorepo_scratch

    cleared: Path | None = None
    if safe:
        try:
            _clear_directory_contents(scratch)
            cleared = scratch
        except OSError as exc:
            errors.append(f"{scratch}: {exc}")
    else:
        errors.append(f"Refusing to clear scratch outside monorepo .scratch: {scratch}")

    cfg.vexil_io.init = False
    cfg.frontend.init = False
    cfg.website.init = False
    cfg.docs_dev.init = False
    cfg.package_src.init = False
    cfg.env_init.init = False
    # Keep houdini_package.init / install_path — package install is separate
    cfg.vexil_io.dir_project_root = ""
    cfg.vexil_io.dir_data_root = ""
    cfg.vexil_io.salt = generate_salt()
    save_config(cfg)

    return ResetResult(deleted_env_files=deleted, cleared_scratch=cleared, errors=errors)
