"""Render and write per-app .env / .env.template files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from env_init.config import MONOREPO_ROOT, VexilConfig

SECRET_KEYS = {
    "VEXIL_PASSWORD",
    "VEXIL_SALT",
    "RESEND_API_KEY",
}


@dataclass(frozen=True)
class EnvFileSpec:
    app_dir: str
    lines: tuple[tuple[str, str, str], ...]  # key, value, comment


def _specs(cfg: VexilConfig) -> list[EnvFileSpec]:
    port = cfg.vexil_io.port
    return [
        EnvFileSpec(
            "vexil-io",
            (
                ("PORT", str(port), "HTTP listen port for vexil-io"),
                ("VEXIL_USER", cfg.vexil_io.user, "Default local API user"),
                ("VEXIL_PASSWORD", cfg.vexil_io.password, "Default local API password"),
                ("VEXIL_SALT", cfg.vexil_io.salt, "Credential hashing salt"),
                ("VEXIL_PROJECT_ROOT", cfg.vexil_io.dir_project_root, "Projects root directory"),
                ("VEXIL_DATA_ROOT", cfg.vexil_io.dir_data_root, "Data / SQLite root directory"),
                ("HOUDINI_DIR", cfg.vexil_io.houdini_dir, "Optional Houdini install hint"),
            ),
        ),
        EnvFileSpec(
            "vexil-frontend",
            (
                (
                    "API_URL",
                    cfg.frontend.api_url or f"http://vexil-io:{port}",
                    "Internal SSR URL to reach vexil-io",
                ),
                (
                    "PUBLIC_API_URL",
                    cfg.frontend.public_api_url or f"http://localhost:{port}",
                    "Browser-facing API URL",
                ),
            ),
        ),
        EnvFileSpec(
            "vexil-website",
            (
                ("RESEND_API_KEY", cfg.website.resend_api_key, "Resend API key for waitlist mail"),
                (
                    "RESEND_FROM_EMAIL",
                    cfg.website.resend_from_email,
                    "Verified Resend from address",
                ),
                ("RESEND_TO_EMAIL", cfg.website.resend_to_email, "Waitlist delivery inbox"),
                ("SITE_URL", cfg.website.site_url, "Canonical production site URL"),
                (
                    "PUBLIC_SITE_URL",
                    cfg.website.public_site_url or f"http://localhost:{cfg.website.port}",
                    "Local/public site URL for SEO helpers",
                ),
            ),
        ),
        EnvFileSpec(
            "docs-dev",
            (("PORT", str(cfg.docs_dev.port), "Local Dev Docs Astro port"),),
        ),
        EnvFileSpec(
            "vexil-package-src",
            (
                (
                    "HOUDINI_PACKAGE_INSTALL_PATH",
                    cfg.houdini_package.install_path,
                    "Selected Houdini preference profile path",
                ),
            ),
        ),
        EnvFileSpec(
            "vexil-dev-tools/env-init",
            (("PORT", str(cfg.env_init.port), "Streamlit env-init UI port"),),
        ),
    ]


def render_env_body(spec: EnvFileSpec, *, template: bool) -> str:
    chunks: list[str] = []
    for key, value, comment in spec.lines:
        chunks.append(f"# {comment}")
        if template and key in SECRET_KEYS:
            chunks.append(f"{key}=")
        else:
            chunks.append(f"{key}={value}")
        chunks.append("")
    return "\n".join(chunks).rstrip() + "\n"


def preview_env_files(cfg: VexilConfig, monorepo_root: Path | None = None) -> dict[Path, str]:
    root = monorepo_root or MONOREPO_ROOT
    out: dict[Path, str] = {}
    for spec in _specs(cfg):
        out[root / "apps" / spec.app_dir / ".env"] = render_env_body(spec, template=False)
        out[root / "apps" / spec.app_dir / ".env.template"] = render_env_body(spec, template=True)
    return out


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def write_env_files(
    cfg: VexilConfig,
    *,
    monorepo_root: Path | None = None,
    write_templates: bool = True,
) -> list[Path]:
    written: list[Path] = []
    for path, body in preview_env_files(cfg, monorepo_root).items():
        if path.name == ".env.template" and not write_templates:
            continue
        if path.name == ".env.example":
            continue
        atomic_write(path, body)
        written.append(path)
    # Keep website .env.example aligned with template secrets placeholders
    root = monorepo_root or MONOREPO_ROOT
    example = root / "apps" / "vexil-website" / ".env.example"
    template = root / "apps" / "vexil-website" / ".env.template"
    if template.is_file():
        atomic_write(example, template.read_text(encoding="utf-8"))
        written.append(example)
    return written
