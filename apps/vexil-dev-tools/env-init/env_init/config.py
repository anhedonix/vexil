"""Typed load/save for env-init vexil.toml."""

from __future__ import annotations

import platform
import tomllib
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

import tomli_w

from env_init.salt import ensure_salt, is_placeholder_salt

PACKAGE_DIR = Path(__file__).resolve().parent
ENV_INIT_ROOT = PACKAGE_DIR.parent
# env-init → vexil-dev-tools → apps → <monorepo root>
MONOREPO_ROOT = ENV_INIT_ROOT.parents[2]
DEFAULT_TOML = ENV_INIT_ROOT / "vexil.toml"


@dataclass
class BaseConfig:
    version: str = "0.1.2"
    dev: bool = True
    os: str = field(default_factory=lambda: platform.system().lower())
    scratch: str = "../../../.scratch"


@dataclass
class VexilIoConfig:
    init: bool = False
    port: int = 6600
    houdini_dir: str = ""
    dir_project_root: str = ""
    user: str = "vexil"
    password: str = "lixev"
    dir_data_root: str = ""
    salt: str = "UUID"


@dataclass
class FrontendConfig:
    init: bool = False
    auto_open: bool = True
    use_houdini_browser: bool = True
    port: int = 6611
    api_url: str = "http://vexil-io:6600"
    public_api_url: str = "http://localhost:6600"


@dataclass
class WebsiteConfig:
    init: bool = False
    port: int = 6622
    resend_api_key: str = ""
    resend_from_email: str = ""
    resend_to_email: str = ""
    site_url: str = "https://vexil.tools"
    public_site_url: str = "http://localhost:6622"


@dataclass
class DocsDevConfig:
    init: bool = False
    port: int = 6633


@dataclass
class PackageSrcConfig:
    init: bool = False


@dataclass
class EnvInitAppConfig:
    init: bool = False
    port: int = 6644


@dataclass
class HoudiniPackageConfig:
    install_path: str = ""
    init: bool = False


@dataclass
class VexilConfig:
    base: BaseConfig = field(default_factory=BaseConfig)
    vexil_io: VexilIoConfig = field(default_factory=VexilIoConfig)
    frontend: FrontendConfig = field(default_factory=FrontendConfig)
    website: WebsiteConfig = field(default_factory=WebsiteConfig)
    docs_dev: DocsDevConfig = field(default_factory=DocsDevConfig)
    package_src: PackageSrcConfig = field(default_factory=PackageSrcConfig)
    env_init: EnvInitAppConfig = field(default_factory=EnvInitAppConfig)
    houdini_package: HoudiniPackageConfig = field(default_factory=HoudiniPackageConfig)

    def ensure_runtime_defaults(self) -> bool:
        """Fill salt / OS when missing. Returns True if anything changed."""
        changed = False
        detected = platform.system().lower()
        if self.base.os in {"", "linux/darwin/windows"}:
            self.base.os = detected
            changed = True
        if is_placeholder_salt(self.vexil_io.salt):
            self.vexil_io.salt = ensure_salt(self.vexil_io.salt)
            changed = True
        return changed


SECTION_MAP = {
    "base": ("base", BaseConfig),
    "vexil-io": ("vexil_io", VexilIoConfig),
    "frontend": ("frontend", FrontendConfig),
    "website": ("website", WebsiteConfig),
    "docs-dev": ("docs_dev", DocsDevConfig),
    "package-src": ("package_src", PackageSrcConfig),
    "env-init": ("env_init", EnvInitAppConfig),
    "houdini_package": ("houdini_package", HoudiniPackageConfig),
}

ATTR_TO_TOML = {attr: key for key, (attr, _) in SECTION_MAP.items()}


def _from_table(cls: type, data: dict[str, Any] | None) -> Any:
    data = data or {}
    allowed = {f.name for f in fields(cls)}
    kwargs = {k: v for k, v in data.items() if k in allowed}
    return cls(**kwargs)


def load_config(path: Path | None = None) -> VexilConfig:
    path = path or DEFAULT_TOML
    if not path.is_file():
        cfg = VexilConfig()
        cfg.ensure_runtime_defaults()
        return cfg
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    cfg = VexilConfig(
        base=_from_table(BaseConfig, raw.get("base")),
        vexil_io=_from_table(VexilIoConfig, raw.get("vexil-io") or raw.get("backend")),
        frontend=_from_table(FrontendConfig, raw.get("frontend")),
        website=_from_table(WebsiteConfig, raw.get("website")),
        docs_dev=_from_table(DocsDevConfig, raw.get("docs-dev")),
        package_src=_from_table(PackageSrcConfig, raw.get("package-src")),
        env_init=_from_table(EnvInitAppConfig, raw.get("env-init")),
        houdini_package=_from_table(HoudiniPackageConfig, raw.get("houdini_package")),
    )
    cfg.ensure_runtime_defaults()
    return cfg


def config_to_toml_dict(cfg: VexilConfig) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for attr, toml_key in ATTR_TO_TOML.items():
        out[toml_key] = asdict(getattr(cfg, attr))
    return out


def save_config(cfg: VexilConfig, path: Path | None = None) -> Path:
    path = path or DEFAULT_TOML
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = config_to_toml_dict(cfg)
    text = tomli_w.dumps(payload)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)
    return path
