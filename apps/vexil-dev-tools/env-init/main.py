"""Streamlit UI for VEXiL environment initialization."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from env_init.config import DEFAULT_TOML, ENV_INIT_ROOT, VexilConfig, load_config, save_config
from env_init.envfiles import preview_env_files, write_env_files
from env_init.folder_browser import FolderBrowserError, FolderBrowserState, init_browser
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

LOGO_PATH = ENV_INIT_ROOT / "assets" / "vexil-logo.png"

HELP = {
    "version": "VEXiL workspace version stamped into generated config. Read-only in the UI.",
    "dev": "When enabled, project/data roots must live under repository /.scratch.",
    "os": "Detected host OS used for Houdini preference-path discovery. Read-only in the UI.",
    "scratch": "Relative path from env-init to the monorepo .scratch folder. Read-only in the UI.",
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
    "resend_key": "Resend API key for waitlist email (secret; not written to tracked templates).",
    "resend_from": "Verified Resend from address.",
    "resend_to": "Inbox that receives waitlist submissions.",
    "site_url": "Canonical production site URL.",
    "public_site_url": "Local/public site URL used by website helpers.",
    "docs_port": "Local Dev Docs port (default 6633).",
    "env_port": "Streamlit port for this env-init UI (default 6644).",
    "houdini_install": "Houdini 22+ preference profile that will receive packages/vexil.json.",
}


def _field_row(label: str, guidance: str):
    """Consistent label | control columns with visible guidance (not hover-only)."""
    left, right = st.columns([1.2, 2.0], vertical_alignment="center")
    with left:
        st.markdown(f"**{label}**")
        st.caption(guidance)
    return right


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


def _browser_key(field: str) -> str:
    return f"folder_browser_{field}"


def _get_browser(field: str, root: Path, start: Path | None = None) -> FolderBrowserState:
    key = _browser_key(field)
    state = st.session_state.get(key)
    if state is None or state.root != root.resolve():
        state = init_browser(root, start=start)
        st.session_state[key] = state
    return state


def _render_folder_browser(field: str, root: Path, current_value: str) -> str | None:
    """Render in-app folder browser. Returns selected path string or None."""
    start = Path(current_value) if current_value.strip() else None
    if start is not None and not start.is_absolute():
        start = root / start
    browser = _get_browser(field, root, start=start)

    st.markdown(f"Browsing under `{browser.root}`")
    st.code(str(browser.current))

    nav_cols = st.columns([1, 1, 2])
    if nav_cols[0].button(
        "Up",
        key=f"{field}_up",
        disabled=not browser.can_go_up(),
    ):
        try:
            browser.go_up()
            st.session_state[_browser_key(field)] = browser
            st.rerun()
        except FolderBrowserError as exc:
            st.error(str(exc))

    if nav_cols[1].button("Select this folder", key=f"{field}_select", type="primary"):
        selected = browser.select_current()
        try:
            relative = selected.relative_to(root)
            return str(relative) if str(relative) != "." else str(root)
        except ValueError:
            return str(selected)

    dirs = browser.list_dirs()
    if not dirs:
        st.caption("No subfolders here.")
        return None

    labels = [d.name for d in dirs]
    choice = st.selectbox("Subfolders", labels, key=f"{field}_dirs")
    if st.button("Open selected folder", key=f"{field}_open"):
        try:
            browser.enter(choice)
            st.session_state[_browser_key(field)] = browser
            st.rerun()
        except FolderBrowserError as exc:
            st.error(str(exc))
    return None


def _heading() -> None:
    if LOGO_PATH.is_file():
        st.image(str(LOGO_PATH), width=220)
    else:
        st.markdown("### VEXiL")
    st.title("Environment Initializer")
    st.caption(f"Config file: `{DEFAULT_TOML}`")


def main() -> None:
    st.set_page_config(
        page_title="VEXiL Env Init",
        page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else "🛠️",
        layout="wide",
    )
    _heading()

    cfg = _cfg()
    scratch = resolve_scratch(cfg)

    st.header("Base")
    with _field_row("version", HELP["version"]):
        st.text_input(
            "version",
            cfg.base.version,
            disabled=True,
            label_visibility="collapsed",
            key="base_version",
        )
    with _field_row("dev environment", HELP["dev"]):
        cfg.base.dev = st.checkbox(
            "dev environment",
            value=cfg.base.dev,
            label_visibility="collapsed",
            key="base_dev",
        )
    with _field_row("os", HELP["os"]):
        st.text_input(
            "os",
            cfg.base.os,
            disabled=True,
            label_visibility="collapsed",
            key="base_os",
        )
    with _field_row("scratch", HELP["scratch"]):
        st.text_input(
            "scratch",
            cfg.base.scratch,
            disabled=True,
            label_visibility="collapsed",
            key="base_scratch",
        )
    st.info(f"Resolved scratch: `{scratch}`")

    st.header("vexil-io")
    with _field_row("port", HELP["port_io"]):
        cfg.vexil_io.port = int(
            st.number_input(
                "port",
                min_value=1,
                max_value=65535,
                value=cfg.vexil_io.port,
                label_visibility="collapsed",
                key="io_port",
            )
        )
    with _field_row("user", HELP["user"]):
        cfg.vexil_io.user = st.text_input(
            "user",
            cfg.vexil_io.user,
            label_visibility="collapsed",
            key="io_user",
        )
    with _field_row("password", HELP["password"]):
        cfg.vexil_io.password = st.text_input(
            "password",
            cfg.vexil_io.password,
            type="password",
            label_visibility="collapsed",
            key="io_password",
        )
    with _field_row("salt", HELP["salt"]):
        salt_col, regen_col = st.columns([3, 1])
        cfg.vexil_io.salt = salt_col.text_input(
            "salt",
            cfg.vexil_io.salt,
            label_visibility="collapsed",
            key="io_salt",
        )
        if regen_col.button("Regenerate", key="regen_salt"):
            cfg.vexil_io.salt = generate_salt()
            st.session_state.vexil_cfg = cfg
            st.rerun()

    with _field_row("dir_project_root", HELP["project_root"]):
        cfg.vexil_io.dir_project_root = st.text_input(
            "dir_project_root",
            cfg.vexil_io.dir_project_root,
            label_visibility="collapsed",
            key="io_project_root",
        )
        if st.checkbox("Browse for project root", key="browse_project_toggle"):
            selected = _render_folder_browser(
                "project_root",
                scratch if cfg.base.dev else scratch.parent,
                cfg.vexil_io.dir_project_root,
            )
            if selected is not None:
                cfg.vexil_io.dir_project_root = selected
                st.session_state.vexil_cfg = cfg
                st.session_state["browse_project_toggle"] = False
                st.rerun()

    with _field_row("dir_data_root", HELP["data_root"]):
        cfg.vexil_io.dir_data_root = st.text_input(
            "dir_data_root",
            cfg.vexil_io.dir_data_root,
            label_visibility="collapsed",
            key="io_data_root",
        )
        if st.checkbox("Browse for data root", key="browse_data_toggle"):
            selected = _render_folder_browser(
                "data_root",
                scratch if cfg.base.dev else scratch.parent,
                cfg.vexil_io.dir_data_root,
            )
            if selected is not None:
                cfg.vexil_io.dir_data_root = selected
                st.session_state.vexil_cfg = cfg
                st.session_state["browse_data_toggle"] = False
                st.rerun()

    with _field_row("houdini_dir", HELP["houdini_dir"]):
        cfg.vexil_io.houdini_dir = st.text_input(
            "houdini_dir",
            cfg.vexil_io.houdini_dir,
            label_visibility="collapsed",
            key="io_houdini_dir",
        )
    st.write(f"Initialized: `{cfg.vexil_io.init}`")

    st.header("Frontend")
    with _field_row("frontend port", HELP["fe_port"]):
        cfg.frontend.port = int(
            st.number_input(
                "frontend port",
                min_value=1,
                max_value=65535,
                value=cfg.frontend.port,
                label_visibility="collapsed",
                key="fe_port",
            )
        )
    with _field_row("auto_open", HELP["auto_open"]):
        cfg.frontend.auto_open = st.checkbox(
            "auto_open",
            value=cfg.frontend.auto_open,
            label_visibility="collapsed",
            key="fe_auto_open",
        )
    with _field_row("use_houdini_browser", HELP["use_houdini_browser"]):
        cfg.frontend.use_houdini_browser = st.checkbox(
            "use_houdini_browser",
            value=cfg.frontend.use_houdini_browser,
            label_visibility="collapsed",
            key="fe_houdini_browser",
        )
    with _field_row("api_url", HELP["api_url"]):
        cfg.frontend.api_url = st.text_input(
            "api_url",
            cfg.frontend.api_url,
            label_visibility="collapsed",
            key="fe_api_url",
        )
    with _field_row("public_api_url", HELP["public_api_url"]):
        cfg.frontend.public_api_url = st.text_input(
            "public_api_url",
            cfg.frontend.public_api_url,
            label_visibility="collapsed",
            key="fe_public_api_url",
        )
    st.write(f"Initialized: `{cfg.frontend.init}`")

    st.header("Website & Docs")
    with _field_row("website port", HELP["web_port"]):
        cfg.website.port = int(
            st.number_input(
                "website port",
                min_value=1,
                max_value=65535,
                value=cfg.website.port,
                label_visibility="collapsed",
                key="web_port",
            )
        )
    with _field_row("docs-dev port", HELP["docs_port"]):
        cfg.docs_dev.port = int(
            st.number_input(
                "docs-dev port",
                min_value=1,
                max_value=65535,
                value=cfg.docs_dev.port,
                label_visibility="collapsed",
                key="docs_port",
            )
        )
    with _field_row("resend_api_key", HELP["resend_key"]):
        cfg.website.resend_api_key = st.text_input(
            "resend_api_key",
            cfg.website.resend_api_key,
            type="password",
            label_visibility="collapsed",
            key="web_resend_key",
        )
    with _field_row("resend_from_email", HELP["resend_from"]):
        cfg.website.resend_from_email = st.text_input(
            "resend_from_email",
            cfg.website.resend_from_email,
            label_visibility="collapsed",
            key="web_resend_from",
        )
    with _field_row("resend_to_email", HELP["resend_to"]):
        cfg.website.resend_to_email = st.text_input(
            "resend_to_email",
            cfg.website.resend_to_email,
            label_visibility="collapsed",
            key="web_resend_to",
        )
    with _field_row("site_url", HELP["site_url"]):
        cfg.website.site_url = st.text_input(
            "site_url",
            cfg.website.site_url,
            label_visibility="collapsed",
            key="web_site_url",
        )
    with _field_row("public_site_url", HELP["public_site_url"]):
        cfg.website.public_site_url = st.text_input(
            "public_site_url",
            cfg.website.public_site_url,
            label_visibility="collapsed",
            key="web_public_site_url",
        )
    with _field_row("env-init port", HELP["env_port"]):
        cfg.env_init.port = int(
            st.number_input(
                "env-init port",
                min_value=1,
                max_value=65535,
                value=cfg.env_init.port,
                label_visibility="collapsed",
                key="env_port",
            )
        )

    st.header("Save configuration")
    st.caption("Persist validated edits to vexil.toml after path checks.")
    if st.button("Validate & save TOML", type="primary", key="save_toml"):
        try:
            validate_dev_roots(cfg)
            created = create_dev_dirs(cfg)
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
    st.caption("Writes local `.env` files only. Tracked `.env.template` files are never modified.")
    preview = preview_env_files(cfg)
    with st.expander("Preview generated .env files", expanded=False):
        for path, body in preview.items():
            st.subheader(str(path))
            st.code(body, language="bash")
    if st.button("Write .env files", key="write_env"):
        try:
            validate_dev_roots(cfg)
            _save(cfg)
            written = write_env_files(cfg)
            st.success(f"Wrote {len(written)} .env files")
            for path in written:
                st.write(f"- `{path}`")
        except PathValidationError as exc:
            st.error(str(exc))

    st.header("Initialize repositories")
    st.caption("go mod download · bun install · uv sync (marks init=true on success)")
    cols = st.columns(5)
    if cols[0].button("Init vexil-io", key="init_io"):
        result = initialize_vexil_io(cfg)
        _save(cfg)
        _show_cmd_results([result])
    if cols[1].button("Init Bun apps", key="init_bun"):
        result = initialize_bun_workspace(cfg)
        _save(cfg)
        _show_cmd_results([result])
    if cols[2].button("Init package-src", key="init_pkg"):
        result = initialize_package_src(cfg)
        _save(cfg)
        _show_cmd_results([result])
    if cols[3].button("Init env-init", key="init_env"):
        result = initialize_env_init(cfg)
        _save(cfg)
        _show_cmd_results([result])
    if cols[4].button("Initialize all", type="primary", key="init_all"):
        results = initialize_all(cfg)
        st.session_state.vexil_cfg = cfg
        _show_cmd_results(results)

    st.header("Houdini package (22+)")
    st.caption(HELP["houdini_install"])
    copy_template_into_repo()
    if st.button("Refresh Houdini profiles", key="refresh_houdini"):
        st.session_state.houdini_profiles = discover_houdini_profiles()
    profiles = st.session_state.get("houdini_profiles")
    if profiles is None:
        profiles = discover_houdini_profiles()
        st.session_state.houdini_profiles = profiles
    if not profiles:
        st.warning("No Houdini 22+ preference profiles found.")
    else:
        labels = [p.label for p in profiles]
        with _field_row("Houdini preference profile", HELP["houdini_install"]):
            choice = st.selectbox(
                "Houdini preference profile",
                labels,
                label_visibility="collapsed",
                key="houdini_choice",
            )
        selected = next(p for p in profiles if p.label == choice)
        st.write(f"packages destination: `{selected.path / 'packages' / 'vexil.json'}`")
        if st.button("Install vexil.json package", key="install_houdini"):
            dest = install_houdini_package(cfg, selected.path)
            st.session_state.vexil_cfg = cfg
            st.success(f"Installed `{dest}`")

    st.header("Reset Dev Env")
    st.warning("Deletes generated `.env` files and clears repository `/.scratch` contents.")
    with _field_row("Type RESET to confirm", "Safety gate before destructive reset."):
        confirm = st.text_input(
            "Type RESET to confirm",
            value="",
            label_visibility="collapsed",
            key="reset_confirm",
        )
    if st.button("Reset Dev Env", type="primary", key="reset_btn"):
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
