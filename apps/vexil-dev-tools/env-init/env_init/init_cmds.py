"""Initialize monorepo apps (go / bun / uv)."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from env_init.config import MONOREPO_ROOT, VexilConfig, save_config


@dataclass
class CommandResult:
    name: str
    command: list[str]
    cwd: Path
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def _run(name: str, command: list[str], cwd: Path) -> CommandResult:
    proc = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return CommandResult(
        name=name,
        command=command,
        cwd=cwd,
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def _has_venv(app_dir: Path) -> bool:
    return (app_dir / ".venv").is_dir()


def initialize_vexil_io(cfg: VexilConfig, monorepo_root: Path | None = None) -> CommandResult:
    root = monorepo_root or MONOREPO_ROOT
    app = root / "apps" / "vexil-io"
    result = _run("vexil-io", ["go", "mod", "download"], app)
    if result.ok:
        cfg.vexil_io.init = True
    return result


def initialize_bun_workspace(cfg: VexilConfig, monorepo_root: Path | None = None) -> CommandResult:
    root = monorepo_root or MONOREPO_ROOT
    bun = shutil.which("bun") or "bun"
    result = _run("bun-workspace", [bun, "install"], root)
    if result.ok:
        cfg.frontend.init = True
        cfg.website.init = True
        cfg.docs_dev.init = True
    return result


def initialize_package_src(cfg: VexilConfig, monorepo_root: Path | None = None) -> CommandResult:
    root = monorepo_root or MONOREPO_ROOT
    app = root / "apps" / "vexil-package-src"
    uv = shutil.which("uv") or "uv"
    result = _run("package-src", [uv, "sync"], app)
    if result.ok and _has_venv(app):
        cfg.package_src.init = True
    elif result.ok and not _has_venv(app):
        result = CommandResult(
            name=result.name,
            command=result.command,
            cwd=result.cwd,
            returncode=1,
            stdout=result.stdout,
            stderr=result.stderr + "\n.venv missing after uv sync",
        )
    return result


def initialize_env_init(cfg: VexilConfig, monorepo_root: Path | None = None) -> CommandResult:
    root = monorepo_root or MONOREPO_ROOT
    app = root / "apps" / "vexil-dev-tools" / "env-init"
    uv = shutil.which("uv") or "uv"
    result = _run("env-init", [uv, "sync"], app)
    if result.ok and _has_venv(app):
        cfg.env_init.init = True
    elif result.ok and not _has_venv(app):
        result = CommandResult(
            name=result.name,
            command=result.command,
            cwd=result.cwd,
            returncode=1,
            stdout=result.stdout,
            stderr=result.stderr + "\n.venv missing after uv sync",
        )
    return result


def initialize_all(cfg: VexilConfig, monorepo_root: Path | None = None) -> list[CommandResult]:
    results = [
        initialize_vexil_io(cfg, monorepo_root),
        initialize_bun_workspace(cfg, monorepo_root),
        initialize_package_src(cfg, monorepo_root),
        initialize_env_init(cfg, monorepo_root),
    ]
    save_config(cfg)
    return results
