"""Path helpers and scratch containment for dev mode."""

from __future__ import annotations

from pathlib import Path

from env_init.config import ENV_INIT_ROOT, MONOREPO_ROOT, VexilConfig


class PathValidationError(ValueError):
    """Raised when a configured path is invalid for the current mode."""


def resolve_scratch(cfg: VexilConfig, env_init_root: Path | None = None) -> Path:
    root = env_init_root or ENV_INIT_ROOT
    scratch = Path(cfg.base.scratch)
    if not scratch.is_absolute():
        scratch = (root / scratch).resolve()
    else:
        scratch = scratch.resolve()
    return scratch


def monorepo_scratch(monorepo_root: Path | None = None) -> Path:
    return (monorepo_root or MONOREPO_ROOT) / ".scratch"


def ensure_under_scratch(
    candidate: str | Path,
    scratch: Path,
    *,
    field_name: str,
) -> Path:
    """Resolve candidate and require it to live under scratch (no escapes)."""
    raw = Path(candidate)
    if not str(candidate).strip():
        raise PathValidationError(f"{field_name} must not be empty in dev mode")
    if not raw.is_absolute():
        resolved = (scratch / raw).resolve()
    else:
        resolved = raw.resolve()
    scratch_resolved = scratch.resolve()
    try:
        resolved.relative_to(scratch_resolved)
    except ValueError as exc:
        raise PathValidationError(
            f"{field_name} must be under {scratch_resolved}, got {resolved}"
        ) from exc
    return resolved


def validate_dev_roots(cfg: VexilConfig, env_init_root: Path | None = None) -> None:
    if not cfg.base.dev:
        return
    scratch = resolve_scratch(cfg, env_init_root)
    if cfg.vexil_io.dir_project_root:
        ensure_under_scratch(cfg.vexil_io.dir_project_root, scratch, field_name="dir_project_root")
    if cfg.vexil_io.dir_data_root:
        ensure_under_scratch(cfg.vexil_io.dir_data_root, scratch, field_name="dir_data_root")


def create_dev_dirs(cfg: VexilConfig, env_init_root: Path | None = None) -> list[Path]:
    """Create approved project/data roots when set. Returns created/ensured paths."""
    validate_dev_roots(cfg, env_init_root)
    created: list[Path] = []
    if not cfg.base.dev:
        return created
    scratch = resolve_scratch(cfg, env_init_root)
    scratch.mkdir(parents=True, exist_ok=True)
    created.append(scratch)
    for value, name in (
        (cfg.vexil_io.dir_project_root, "dir_project_root"),
        (cfg.vexil_io.dir_data_root, "dir_data_root"),
    ):
        if not value:
            continue
        path = ensure_under_scratch(value, scratch, field_name=name)
        path.mkdir(parents=True, exist_ok=True)
        created.append(path)
    return created
