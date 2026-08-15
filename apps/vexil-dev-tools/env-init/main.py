"""Streamlit UI for VEXiL environment initialization."""

from __future__ import annotations

import streamlit as st

from env_init.config import DEFAULT_TOML, VexilConfig, load_config, save_config
from env_init.envfiles import preview_env_files, write_env_files
from env_init.houdini import (
    copy_template_into_repo,
    discover_houdini_profiles,
    install_houdini_package,
)
from env_init.init_cmds import (
    initialize_all,
    initialize_bun_workspace,
    initialize_env_init,
    initialize_package_src,
    initialize_vexil_io,
)
from env_init.paths import PathValidationError, create_dev_dirs, resolve_scratch, validate_dev_roots
from env_init.reset import reset_dev_env
from env_init.salt import generate_salt, is_placeholder_salt

HELP = {
    "version": "VEXiL workspace version stamped into generated config.",
    "dev": "When enabled, project/data roots must live under repository /.scratch.",
    "os": "Detected host OS used for Houdini preference-path discovery.",
    "scratch": "Relative path from env-init to the monorepo .scratch folder.",
    "port_io": "Uncommon local API port (default 6600). Writes PORT and frontend API URLs.",
    "user": "Default local username written to apps/vexil-io/.env.",
    "password": "Default local password written only to ignored .env files.",
    "salt": "Long random credential salt. Auto-generated on load; regenerate to rotate.",
    "project_root": "Projects directory. In dev mode must resolve under /.scratch.",
    "data_root": "Data / SQLite directory. In dev mode must resolve under /.scratch.",
    "houdini_dir": "Selected Houdini preference profile path (set by package install).",
    "fe_port": "Local Astro port for vexil-frontend (default 6611).",
    "api_url": "Internal SSR URL used by Astro to reach vexil-io.",
    "public_api_url": "Browser-facing API URL for the frontend.",
    "auto_open": "Hint for tooling to auto-open the frontend after init.",
    "use_houdini_browser": "Prefer Houdini’s embedded browser when launching UI links.",
    "web_port": "Local Astro port for the VEXiL website (default 6622).",
    "resend_key": "Resend API key for waitlist email (secret; template stays empty).",
    "resend_from": "Verified Resend from address.",
    "resend_to": "Inbox that receives waitlist submissions.",
    "site_url": "Canonical production site URL.",
    "public_site_url": "Local/public site URL used by website helpers.",
    "docs_port": "Local Dev Docs port (default 6633).",
    "env_port": "Streamlit port for this env-init UI (default 6644).",
    "houdini_install": "Houdini 22+ preference profile that will receive packages/vexil.json.",
}


def _cfg() -> VexilConfig:
    if "vexil_cfg" not in st.session_state:
        cfg = load_config(DEFAULT_TOML)
        if is_placeholder_salt(cfg.vexil_io.salt):
            cfg.vexil_io.salt = generate_salt()
        st.session_state.vexil_cfg = cfg
        st.session_state.salt_dirty = True
    return st.session_state.vexil_cfg


def _save(cfg: VexilConfig) -> None:
    save_config(cfg, DEFAULT_TOML)
    st.session_state.vexil_cfg = cfg
    st.session_state.salt_dirty = False


def _show_cmd_results(results) -> None:
    for result in results:
        status = "OK" if result.ok else "FAILED"
        with st.expander(f"{result.name}: {status}", expanded=not result.ok):
            st.code(" ".join(result.command))
            if result.stdout:
                st.text(result.stdout)
            if result.stderr:
                st.text(result.stderr)


def main() -> None:
    st.set_page_config(page_title="VEXiL Env Init", page_icon="🛠️", layout="wide")
    st.title("VEXiL Environment Initializer")
    st.caption(f"Config file: `{DEFAULT_TOML}`")

    cfg = _cfg()

    st.header("Base")
    c1, c2, c3 = st.columns(3)
    cfg.base.version = c1.text_input("version", cfg.base.version, help=HELP["version"])
    cfg.base.dev = c2.checkbox("dev environment", value=cfg.base.dev, help=HELP["dev"])
    cfg.base.os = c3.text_input("os", cfg.base.os, help=HELP["os"])
    cfg.base.scratch = st.text_input("scratch", cfg.base.scratch, help=HELP["scratch"])
    st.info(f"Resolved scratch: `{resolve_scratch(cfg)}`")

    st.header("vexil-io")
    c1, c2, c3 = st.columns(3)
    cfg.vexil_io.port = int(
        c1.number_input(
            "port", min_value=1, max_value=65535, value=cfg.vexil_io.port, help=HELP["port_io"]
        )
    )
    cfg.vexil_io.user = c2.text_input("user", cfg.vexil_io.user, help=HELP["user"])
    cfg.vexil_io.password = c3.text_input(
        "password", cfg.vexil_io.password, type="password", help=HELP["password"]
    )
    salt_col, regen_col = st.columns([4, 1])
    cfg.vexil_io.salt = salt_col.text_input("salt", cfg.vexil_io.salt, help=HELP["salt"])
    if regen_col.button("Regenerate salt", help="Replace the salt with a new random value"):
        cfg.vexil_io.salt = generate_salt()
        st.session_state.vexil_cfg = cfg
        st.rerun()
    cfg.vexil_io.dir_project_root = st.text_input(
        "dir_project_root",
        cfg.vexil_io.dir_project_root,
        help=HELP["project_root"],
    )
    cfg.vexil_io.dir_data_root = st.text_input(
        "dir_data_root",
        cfg.vexil_io.dir_data_root,
        help=HELP["data_root"],
    )
    cfg.vexil_io.houdini_dir = st.text_input(
        "houdini_dir",
        cfg.vexil_io.houdini_dir,
        help=HELP["houdini_dir"],
    )
    st.write(f"Initialized: `{cfg.vexil_io.init}`")

    st.header("Frontend")
    c1, c2 = st.columns(2)
    cfg.frontend.port = int(
        c1.number_input(
            "frontend port",
            min_value=1,
            max_value=65535,
            value=cfg.frontend.port,
            help=HELP["fe_port"],
        )
    )
    cfg.frontend.auto_open = c2.checkbox(
        "auto_open", value=cfg.frontend.auto_open, help=HELP["auto_open"]
    )
    cfg.frontend.use_houdini_browser = st.checkbox(
        "use_houdini_browser",
        value=cfg.frontend.use_houdini_browser,
        help=HELP["use_houdini_browser"],
    )
    cfg.frontend.api_url = st.text_input("api_url", cfg.frontend.api_url, help=HELP["api_url"])
    cfg.frontend.public_api_url = st.text_input(
        "public_api_url",
        cfg.frontend.public_api_url,
        help=HELP["public_api_url"],
    )
    st.write(f"Initialized: `{cfg.frontend.init}`")

    st.header("Website & Docs")
    c1, c2 = st.columns(2)
    cfg.website.port = int(
        c1.number_input(
            "website port",
            min_value=1,
            max_value=65535,
            value=cfg.website.port,
            help=HELP["web_port"],
        )
    )
    cfg.docs_dev.port = int(
        c2.number_input(
            "docs-dev port",
            min_value=1,
            max_value=65535,
            value=cfg.docs_dev.port,
            help=HELP["docs_port"],
        )
    )
    cfg.website.resend_api_key = st.text_input(
        "resend_api_key",
        cfg.website.resend_api_key,
        type="password",
        help=HELP["resend_key"],
    )
    cfg.website.resend_from_email = st.text_input(
        "resend_from_email",
        cfg.website.resend_from_email,
        help=HELP["resend_from"],
    )
    cfg.website.resend_to_email = st.text_input(
        "resend_to_email",
        cfg.website.resend_to_email,
        help=HELP["resend_to"],
    )
    cfg.website.site_url = st.text_input("site_url", cfg.website.site_url, help=HELP["site_url"])
    cfg.website.public_site_url = st.text_input(
        "public_site_url",
        cfg.website.public_site_url,
        help=HELP["public_site_url"],
    )
    cfg.env_init.port = int(
        st.number_input(
            "env-init port",
            min_value=1,
            max_value=65535,
            value=cfg.env_init.port,
            help=HELP["env_port"],
        )
    )

    st.header("Save configuration")
    if st.button(
        "Validate & save TOML", type="primary", help="Persist vexil.toml after path checks"
    ):
        try:
            validate_dev_roots(cfg)
            created = create_dev_dirs(cfg)
            # Keep frontend API URLs aligned with port when left empty-ish
            if not cfg.frontend.api_url or "vexil-io:" in cfg.frontend.api_url:
                cfg.frontend.api_url = f"http://vexil-io:{cfg.vexil_io.port}"
            if not cfg.frontend.public_api_url or "localhost:" in cfg.frontend.public_api_url:
                cfg.frontend.public_api_url = f"http://localhost:{cfg.vexil_io.port}"
            _save(cfg)
            st.success(f"Saved `{DEFAULT_TOML}`")
            if created:
                st.write("Ensured directories:", ", ".join(str(p) for p in created))
        except PathValidationError as exc:
            st.error(str(exc))

    st.header("Generate environment files")
    preview = preview_env_files(cfg)
    with st.expander("Preview generated files", expanded=False):
        for path, body in preview.items():
            st.subheader(str(path))
            st.code(body, language="bash")
    if st.button("Write .env and .env.template files", help="Atomic write of local env files"):
        try:
            validate_dev_roots(cfg)
            _save(cfg)
            written = write_env_files(cfg)
            st.success(f"Wrote {len(written)} files")
            for path in written:
                st.write(f"- `{path}`")
        except PathValidationError as exc:
            st.error(str(exc))

    st.header("Initialize repositories")
    st.caption("go mod download · bun install · uv sync (marks init=true on success)")
    cols = st.columns(5)
    if cols[0].button("Init vexil-io", help="Run go mod download in apps/vexil-io"):
        result = initialize_vexil_io(cfg)
        _save(cfg)
        _show_cmd_results([result])
    if cols[1].button("Init Bun apps", help="Run bun install at the monorepo root"):
        result = initialize_bun_workspace(cfg)
        _save(cfg)
        _show_cmd_results([result])
    if cols[2].button("Init package-src", help="Run uv sync for vexil-package-src"):
        result = initialize_package_src(cfg)
        _save(cfg)
        _show_cmd_results([result])
    if cols[3].button("Init env-init", help="Run uv sync for this Streamlit app"):
        result = initialize_env_init(cfg)
        _save(cfg)
        _show_cmd_results([result])
    if cols[4].button("Initialize all", type="primary", help="Run every init command in sequence"):
        results = initialize_all(cfg)
        st.session_state.vexil_cfg = cfg
        _show_cmd_results(results)

    st.header("Houdini package (22+)")
    copy_template_into_repo()
    if st.button("Refresh Houdini profiles", help="Rescan HOUDINI_USER_PREF_DIR and OS defaults"):
        st.session_state.houdini_profiles = discover_houdini_profiles()
    profiles = st.session_state.get("houdini_profiles")
    if profiles is None:
        profiles = discover_houdini_profiles()
        st.session_state.houdini_profiles = profiles
    if not profiles:
        st.warning("No Houdini 22+ preference profiles found.")
    else:
        labels = [p.label for p in profiles]
        choice = st.selectbox(
            "Houdini preference profile",
            labels,
            help=HELP["houdini_install"],
        )
        selected = next(p for p in profiles if p.label == choice)
        st.write(f"packages destination: `{selected.path / 'packages' / 'vexil.json'}`")
        if st.button(
            "Install vexil.json package", help="Copy rendered package JSON into packages/"
        ):
            dest = install_houdini_package(cfg, selected.path)
            st.session_state.vexil_cfg = cfg
            st.success(f"Installed `{dest}`")

    st.header("Reset Dev Env")
    st.warning("Deletes generated `.env` files and clears repository `/.scratch` contents.")
    confirm = st.text_input(
        "Type RESET to confirm",
        value="",
        help="Safety gate before destructive reset.",
    )
    if st.button("Reset Dev Env", type="primary", help="Wipe local .env files and scratch data"):
        if confirm.strip() != "RESET":
            st.error("Confirmation text must be exactly RESET")
        else:
            result = reset_dev_env(cfg)
            st.session_state.vexil_cfg = cfg
            if result.errors:
                for err in result.errors:
                    st.error(err)
            st.success("Dev environment reset")
            st.write("Deleted:", ", ".join(str(p) for p in result.deleted_env_files) or "(none)")
            st.write("Cleared scratch:", result.cleared_scratch)


if __name__ == "__main__":
    main()
