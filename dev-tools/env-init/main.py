from __future__ import annotations

import asyncio
import json
import os
import secrets
from pathlib import Path

from textual import events, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import (
    Button,
    Checkbox,
    Collapsible,
    Input,
    Label,
    RichLog,
    Static,
)

MONOREPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = MONOREPO_ROOT / "docker-compose.yml"

LOADED_ENV: dict[str, str] = {}


def load_all_env_files() -> dict[str, str]:
    res = {}
    dir_map = {
        "backend-api": "backend-api",
        "frontend-app": "frontend-app",
        "website-vexil": "website-vexil",
    }
    for service_name, service_dir in dir_map.items():
        env_path = MONOREPO_ROOT / "apps" / service_dir / ".env"
        if env_path.is_file():
            try:
                for line in env_path.read_text().splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        res[k.strip()] = v.strip()
            except Exception:
                pass
                
    yaml_path = MONOREPO_ROOT / "apps" / "plugins" / "houdini-package" / "env.yaml"
    if yaml_path.is_file():
        try:
            current_section = None
            for line in yaml_path.read_text().splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                indent = len(line) - len(line.lstrip())
                if indent == 0:
                    current_section = None
                if ":" in stripped:
                    k, v = stripped.split(":", 1)
                    k = k.strip()
                    v = v.strip()
                    if not v:
                        current_section = k
                        continue
                    if current_section == "online":
                        res[f"VEXIL_ONLINE_{k.upper()}"] = v
                    elif current_section == "local":
                        res[f"VEXIL_LOCAL_{k.upper()}"] = v
                    else:
                        if k == "houdini_install_path":
                            res["HOUDINI_INSTALL_PATH"] = v
                        elif k == "projects_root":
                            res["VEXIL_PROJECTS_ROOT"] = v
                        elif k == "mode":
                            res["VEXIL_MODE"] = v
                        elif k == "log_level":
                            res["VEXIL_LOG_LEVEL"] = v
                        elif k == "houdini_path":
                            res["HOUDINI_PATH"] = v
                        elif k == "pythonpath":
                            res["PYTHONPATH"] = v
        except Exception:
            pass
    return res


def check_env_files_exist() -> bool:
    env_files = [
        MONOREPO_ROOT / "apps" / "backend-api" / ".env",
        MONOREPO_ROOT / "apps" / "frontend-app" / ".env",
        MONOREPO_ROOT / "apps" / "website-vexil" / ".env",
        MONOREPO_ROOT / "apps" / "plugins" / "houdini-package" / "env.yaml",
    ]
    return all(p.is_file() for p in env_files)


VEXIL_ASCII = r"""
 __      __  _______  __   __    _    _       
 \ \    / / |  _____| \ \ / /   (_)  | |      
  \ \  / /  | |__      \ V /    | |  | |      
   \ \/ /   |  __|      > <     | |  | |      
    \  /    | |_____   / . \    | |  | |____  
     \/     |_______| /_/ \_\   |_|  |______|

 VEXiL Developer Environment Builder & Docker Dashboard
 Configure local settings, manage docker services, and run DCC Houdini pipelines.
"""

SERVICE_VARS: dict[str, list[dict]] = {
    "backend-api": [
        {
            "key": "SECRET_KEY",
            "label": "Secret Key",
            "default": lambda: secrets.token_urlsafe(50),
            "password": True,
            "hidden": True,
        },
        {"key": "DEBUG", "label": "Debug", "default": "True"},
        {
            "key": "ALLOWED_HOSTS",
            "label": "Allowed Hosts",
            "default": "localhost,127.0.0.1,0.0.0.0",
            "hidden": True,
        },
        {
            "key": "DATABASE_URL",
            "label": "Database URL",
            "default": f"sqlite:///{MONOREPO_ROOT}/apps/backend-api/db.sqlite3",
            "hidden": True,
        },
    ],
    "frontend-app": [
        {
            "key": "API_URL",
            "label": "API URL (internal)",
            "default": "http://backend-api:8000",
        },
        {
            "key": "PUBLIC_API_URL",
            "label": "Public API URL",
            "default": "http://localhost:8000",
        },
    ],
    "website-vexil": [
        {
            "key": "RESEND_API_KEY",
            "label": "Resend API Key",
            "default": "re_your_key_here",
            "password": True,
            "hidden": True,
        },
        {"key": "RESEND_FROM_EMAIL", "label": "From Email", "default": "", "hidden": True},
        {"key": "RESEND_TO_EMAIL", "label": "To Email", "default": "", "hidden": True},
        {"key": "SITE_URL", "label": "Site URL", "default": "https://vexil.dev"},
    ],
}

DOCKER_SERVICES = ["backend-api", "frontend-app", "website"]
SERVICE_PORTS = {"backend-api": 8000, "frontend-app": 4321, "website": 4322}


class SelectableRichLog(RichLog):
    can_focus = True

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.history: list[str] = []

    def write(self, text: str, *args, **kwargs) -> SelectableRichLog:
        clean = str(text)
        for tag in ["[bold]", "[/bold]", "[bold accent]", "[/bold accent]", "[bold green]", "[/bold green]", "[bold red]", "[/bold red]", "[bold blue]", "[/bold blue]", "[bold yellow]", "[/bold yellow]", "[green]", "[/green]", "[red]", "[/red]", "[blue]", "[/blue]", "[yellow]", "[/yellow]", "[dim]", "[/dim]"]:
            clean = clean.replace(tag, "")
        self.history.append(clean)
        return super().write(text, *args, **kwargs)


class AutocompleteInput(Input):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.suggestions: list[str] = []

    def on_key(self, event: events.Key) -> None:
        if event.key == "tab" and self.suggestions:
            event.prevent_default()
            event.stop()
            self.value = self.suggestions[0]
            self.suggestions = []
            self.post_message(self.Changed(self, self.value))


class PathInput(Widget):
    def __init__(self, value: str, id: str, password: bool = False) -> None:
        super().__init__(id=id)
        self.initial_value = value
        self.input_id = f"input-{id}"
        self.password = password

    def compose(self) -> ComposeResult:
        yield AutocompleteInput(value=self.initial_value, id=self.input_id, password=self.password)
        yield Label("", classes="suggestions-label")

    @property
    def value(self) -> str:
        return self.query_one(AutocompleteInput).value

    @value.setter
    def value(self, val: str) -> None:
        self.query_one(AutocompleteInput).value = val

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == self.input_id:
            self.update_suggestions(event.value)

    def update_suggestions(self, current_val: str) -> None:
        try:
            expanded = os.path.expanduser(current_val)
            path = Path(expanded)
            
            if current_val.endswith(os.sep):
                parent = path
                prefix = ""
            else:
                parent = path.parent
                prefix = path.name

            if parent.is_dir():
                matches = []
                for entry in parent.iterdir():
                    if entry.is_dir() and not entry.name.startswith("."):
                        if entry.name.lower().startswith(prefix.lower()):
                            base = current_val
                            if prefix:
                                base = current_val[:-len(prefix)]
                            sep = "" if base.endswith(os.sep) else os.sep
                            matches.append(f"{base}{sep}{entry.name}")
                
                matches = sorted(matches)
                inp = self.query_one(AutocompleteInput)
                inp.suggestions = matches
                
                label = self.query_one(".suggestions-label", Label)
                if matches:
                    first = matches[0]
                    more = f" (+{len(matches)-1} more)" if len(matches) > 1 else ""
                    label.update(f"Suggestion: [bold]{first}[/bold]{more} [Press Tab to accept]")
                    label.styles.display = "block"
                else:
                    label.styles.display = "none"
            else:
                self.query_one(".suggestions-label", Label).styles.display = "none"
                self.query_one(AutocompleteInput).suggestions = []
        except Exception:
            try:
                self.query_one(".suggestions-label", Label).styles.display = "none"
                self.query_one(AutocompleteInput).suggestions = []
            except Exception:
                pass


class EnvField(Widget):
    def __init__(
        self,
        key: str,
        label: str,
        default_value: str,
        password: bool = False,
        hidden: bool = False,
    ) -> None:
        super().__init__(classes="env-field" + (" advanced-field" if hidden else ""))
        self.key = key
        self._label = label
        self.default_value = default_value
        self.password = password
        self.hidden_by_spec = hidden

    def compose(self) -> ComposeResult:
        yield Label(self._label)
        yield Input(
            value=self.default_value,
            password=self.password,
            id=f"input-{self.key.lower().replace('_', '-')}",
        )

    @property
    def value(self) -> str:
        return self.query_one(Input).value

    def set_reveal_secrets(self, reveal: bool) -> None:
        if self.password:
            self.query_one(Input).password = not reveal


class ServiceSection(Widget):
    def __init__(self, service_name: str, field_specs: list[dict]) -> None:
        super().__init__(id=f"section-{service_name}")
        self.service_name = service_name
        self.field_specs = field_specs

    def _resolve_default(self, spec: dict) -> str:
        raw = spec.get("default", "")
        resolved = raw() if callable(raw) else raw
        if spec["key"] in LOADED_ENV:
            return LOADED_ENV[spec["key"]]
        return os.environ.get(spec["key"], str(resolved))

    def compose(self) -> ComposeResult:
        with Collapsible(
            title=f"  {self.service_name}",
            collapsed=False,
            id=f"collapsible-{self.service_name}",
        ):
            for spec in self.field_specs:
                yield EnvField(
                    spec["key"],
                    spec["label"],
                    self._resolve_default(spec),
                    password=spec.get("password", False),
                    hidden=spec.get("hidden", False),
                )

    def get_values(self) -> dict[str, str]:
        return {field.key: field.value for field in self.query(EnvField)}


class HoudiniSection(Widget):
    def __init__(self) -> None:
        super().__init__(id="section-houdini")

    def compose(self) -> ComposeResult:
        h_path = LOADED_ENV.get("HOUDINI_INSTALL_PATH", "/opt/hfs20.5")
        p_root = LOADED_ENV.get("VEXIL_PROJECTS_ROOT", str(Path.home() / "vexil_projects"))
        mode = LOADED_ENV.get("VEXIL_MODE", "local")
        online_val = (mode == "online")
        
        local_dir = LOADED_ENV.get("VEXIL_LOCAL_CONFIG_DIR", str(Path.home() / ".config" / "vexil"))
        local_db = LOADED_ENV.get("VEXIL_LOCAL_DB_DIR", str(Path.home() / ".local" / "share" / "vexil" / "db"))
        local_data = LOADED_ENV.get("VEXIL_LOCAL_DATA_DIR", str(Path.home() / ".local" / "share" / "vexil" / "data"))
        
        online_api = LOADED_ENV.get("VEXIL_ONLINE_API_URL", "http://localhost:8000")
        user = LOADED_ENV.get("VEXIL_ONLINE_USERNAME", "")
        pwd = LOADED_ENV.get("VEXIL_ONLINE_PASSWORD", "")
        
        log_level = LOADED_ENV.get("VEXIL_LOG_LEVEL", "INFO")
        h_path_override = LOADED_ENV.get("HOUDINI_PATH", str(MONOREPO_ROOT / "apps" / "plugins" / "houdini-package"))
        pythonpath_override = LOADED_ENV.get("PYTHONPATH", str(MONOREPO_ROOT / "apps" / "plugins" / "houdini-package" / "python"))

        with Collapsible(title="  Houdini Plugin Settings", collapsed=False, id="collapsible-houdini"):
            with Horizontal(classes="form-row"):
                yield Label("Houdini Install Path")
                yield PathInput(value=h_path, id="h-install-path")
            with Horizontal(classes="form-row"):
                yield Label("Projects Root Folder")
                yield PathInput(value=p_root, id="h-projects-root")
            with Horizontal(classes="form-row"):
                yield Label("Online Mode")
                yield Checkbox("Use Online Project Sync", value=online_val, id="h-mode-online")
            
            # Local Mode Settings
            with Horizontal(classes="form-row", id="h-row-local-dir"):
                yield Label("Local Config Folder")
                yield PathInput(value=local_dir, id="h-local-dir")
            with Horizontal(classes="form-row", id="h-row-local-db"):
                yield Label("Local Database Folder")
                yield PathInput(value=local_db, id="h-local-db")
            with Horizontal(classes="form-row", id="h-row-local-data"):
                yield Label("Local Data Folder")
                yield PathInput(value=local_data, id="h-local-data")
                
            # Online Mode Settings
            with Horizontal(classes="form-row advanced-field", id="h-row-online-api"):
                yield Label("Online API URL")
                yield Input(value=online_api, id="h-online-api")
            with Horizontal(classes="form-row", id="h-row-online-user"):
                yield Label("Online Username")
                yield Input(value=user, id="h-online-user")
            with Horizontal(classes="form-row", id="h-row-online-pass"):
                yield Label("Online Password")
                yield Input(value=pwd, password=True, id="h-online-pass")

            # Advanced environment variables
            with Horizontal(classes="form-row advanced-field", id="h-row-path-override"):
                yield Label("HOUDINI_PATH")
                yield PathInput(value=h_path_override, id="h-path-override")
            with Horizontal(classes="form-row advanced-field", id="h-row-pythonpath-override"):
                yield Label("PYTHONPATH")
                yield PathInput(value=pythonpath_override, id="h-pythonpath-override")
            with Horizontal(classes="form-row advanced-field", id="h-row-log-level"):
                yield Label("Log Level")
                yield Input(value=log_level, id="h-log-level")

    def on_mount(self) -> None:
        online_mode = self.query_one("#h-mode-online", Checkbox).value
        self.update_visibility(online_mode)

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "h-mode-online":
            self.update_visibility(event.value)

    def update_visibility(self, online_mode: bool) -> None:
        self.query_one("#h-row-local-dir").styles.display = "none" if online_mode else "block"
        self.query_one("#h-row-local-db").styles.display = "none" if online_mode else "block"
        self.query_one("#h-row-local-data").styles.display = "none" if online_mode else "block"
        
        self.query_one("#h-row-online-user").styles.display = "block" if online_mode else "none"
        self.query_one("#h-row-online-pass").styles.display = "block" if online_mode else "none"
        
        try:
            show_advanced = self.screen.query_one("#toggle-advanced", Checkbox).value
            self.set_show_advanced(show_advanced)
        except Exception:
            pass

    def set_show_advanced(self, show: bool) -> None:
        self.query_one("#h-row-path-override").styles.display = "block" if show else "none"
        self.query_one("#h-row-pythonpath-override").styles.display = "block" if show else "none"
        self.query_one("#h-row-log-level").styles.display = "block" if show else "none"
        
        online_mode = self.query_one("#h-mode-online", Checkbox).value
        self.query_one("#h-row-online-api").styles.display = "block" if (show and online_mode) else "none"

    def get_values(self) -> dict:
        online_mode = self.query_one("#h-mode-online", Checkbox).value
        res = {
            "houdini_install_path": self.query_one("#h-install-path", PathInput).value,
            "projects_root": self.query_one("#h-projects-root", PathInput).value,
            "mode": "online" if online_mode else "local",
            "log_level": self.query_one("#h-log-level", Input).value,
            "houdini_path": self.query_one("#h-path-override", PathInput).value,
            "pythonpath": self.query_one("#h-pythonpath-override", PathInput).value,
        }
        if online_mode:
            res["online"] = {
                "api_url": self.query_one("#h-online-api", Input).value,
                "username": self.query_one("#h-online-user", Input).value,
                "password": self.query_one("#h-online-pass", Input).value,
            }
        else:
            res["local"] = {
                "config_dir": self.query_one("#h-local-dir", PathInput).value,
                "db_dir": self.query_one("#h-local-db", PathInput).value,
                "data_dir": self.query_one("#h-local-data", PathInput).value,
            }
        return res

    def set_reveal_secrets(self, reveal: bool) -> None:
        self.query_one("#h-online-pass", Input).password = not reveal


class ServiceStatusBar(Widget):
    def __init__(self, name: str) -> None:
        super().__init__(id=f"bar-{name}")
        self.service_name = name

    def compose(self) -> ComposeResult:
        yield Static(
            "*",
            id=f"dot-{self.service_name}",
            classes="status-dot status-unknown",
        )
        yield Label(
            f"[bold]{self.service_name}[/bold]  :{SERVICE_PORTS[self.service_name]}"
        )
        yield Button("Start", variant="success", id=f"start-{self.service_name}")
        yield Button("Stop", variant="error", id=f"stop-{self.service_name}")
        yield Button("Open", variant="default", id=f"open-{self.service_name}")
        yield Button("Logs", variant="default", id=f"logs-{self.service_name}")

    def set_state(self, state: str) -> None:
        try:
            dot = self.query_one(f"#dot-{self.service_name}", Static)
            dot.remove_class("status-running", "status-exited", "status-unknown")
            
            is_running = "running" in state
            
            if is_running:
                dot.add_class("status-running")
            elif "exited" in state or "stopped" in state:
                dot.add_class("status-exited")
            else:
                dot.add_class("status-unknown")
            
            # Enable/disable Open button based on running state
            try:
                open_btn = self.query_one(f"#open-{self.service_name}", Button)
                open_btn.disabled = not is_running
            except Exception:
                pass
        except Exception:
            pass


class HelpStatusBar(Static):
    def __init__(self) -> None:
        super().__init__(
            " [b #fafafa]Ctrl+Q[/] [#a1a1aa]Quit[/]  [#3f3f46]|[/]  "
            "[b #fafafa]Ctrl+S[/] [#a1a1aa]Save Configs[/]  [#3f3f46]|[/]  "
            "[b #fafafa]Ctrl+U[/] [#a1a1aa]Start All[/]  [#3f3f46]|[/]  "
            "[b #fafafa]Ctrl+D[/] [#a1a1aa]Stop All[/]  [#3f3f46]|[/]  "
            "[b #fafafa]Ctrl+Y[/] [#a1a1aa]Copy Logs[/]  [#3f3f46]|[/]  "
            "[b #fafafa]Ctrl+L[/] [#a1a1aa]Focus Logs[/]",
            id="help-status-bar",
            markup=True,
        )


class VexilApp(App):
    TITLE = "VEXiL Dev Tools"
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+s", "save_configs", "Save Configs"),
        Binding("ctrl+u", "start_services", "Start All"),
        Binding("ctrl+d", "stop_services", "Stop All"),
        Binding("ctrl+y", "copy_logs", "Copy Logs"),
        Binding("ctrl+l", "focus_logs", "Focus Logs"),
    ]

    CSS_PATH = "main.tcss"

    service_status: reactive[dict[str, str]] = reactive({})

    def compose(self) -> ComposeResult:
        yield Static(VEXIL_ASCII, id="app-header")
        with Horizontal(id="main-content"):
            with Vertical(id="left-pane"):
                yield Label("[bold accent]Environment Builder[/bold accent]\n")
                with Horizontal(id="toggle-container"):
                    yield Checkbox("Show Advanced / Hidden Fields", value=False, id="toggle-advanced")
                    yield Checkbox("Reveal Passwords / Secrets", value=False, id="toggle-secrets")
                with VerticalScroll(id="config-scroll"):
                    for service_name, specs in SERVICE_VARS.items():
                        yield ServiceSection(service_name, specs)
                    yield HoudiniSection()
                with Horizontal(id="config-actions"):
                    yield Button("Save & Apply Configs", variant="success", id="btn-save-config")
            
            with Vertical(id="right-pane"):
                with VerticalScroll(id="right-scroll"):
                    yield Label("[bold accent]Service Control Dashboard[/bold accent]\n")
                    for name in DOCKER_SERVICES:
                        yield ServiceStatusBar(name)
                        
                    with Collapsible(title="  Django Database & Admin Actions", collapsed=True, id="section-django"):
                        with Horizontal(classes="action-row"):
                            yield Button("Apply Database Migrations", variant="primary", id="btn-migrate")
                        
                        yield Label("\n[bold]Create Django Admin Superuser[/bold]")
                        with Horizontal(classes="form-row"):
                            yield Label("Username:")
                            yield Input(value="admin", id="su-username")
                        with Horizontal(classes="form-row"):
                            yield Label("Email:")
                            yield Input(value="admin@example.com", id="su-email")
                        with Horizontal(classes="form-row"):
                            yield Label("Password:")
                            yield Input(value="adminpass", password=True, id="su-password")
                        with Horizontal(classes="action-row"):
                            yield Button("Create Superuser", variant="primary", id="btn-create-su")
                
                yield SelectableRichLog(id="log-console", highlight=True, markup=True, auto_scroll=True)
                with Horizontal(id="global-actions"):
                    yield Button("Copy Logs", variant="default", id="btn-copy-logs")
                    yield Button("Start All Services", variant="success", id="btn-start-all")
                    yield Button("Stop All Services", variant="error", id="btn-stop-all")
        yield HelpStatusBar()

    def action_save_configs(self) -> None:
        self.save_configurations()

    def action_start_services(self) -> None:
        if check_env_files_exist():
            self.stream_compose("up", "-d")
        else:
            self.notify("Please save environment configurations first!", severity="warning")

    def action_stop_services(self) -> None:
        if check_env_files_exist():
            self.stream_compose("down")
        else:
            self.notify("Please save environment configurations first!", severity="warning")

    def action_copy_logs(self) -> None:
        try:
            log_widget = self.query_one("#log-console", SelectableRichLog)
            full_text = "\n".join(log_widget.history)
            self.copy_to_clipboard(full_text)
            self.notify("[OK] Logs copied to clipboard!", severity="information")
        except Exception as e:
            self.notify(f"Failed to copy logs: {e}", severity="error")

    def action_focus_logs(self) -> None:
        try:
            self.query_one("#log-console").focus()
        except Exception:
            pass

    def on_mount(self) -> None:
        global LOADED_ENV
        LOADED_ENV.clear()
        LOADED_ENV.update(load_all_env_files())
        self.update_config_status()
        
        self._poll_timer = self.set_interval(4.0, self._poll_status)
        self._poll_status()

    def update_config_status(self) -> None:
        # Status is now shown in logs instead of a dedicated alert box
        pass

    def watch_service_status(self, new_status: dict[str, str]) -> None:
        for name in DOCKER_SERVICES:
            try:
                bar = self.query_one(f"#bar-{name}", ServiceStatusBar)
                state = new_status.get(name, "unknown")
                bar.set_state(state)
            except Exception:
                pass

    @work(exclusive=True, group="status-poll", exit_on_error=False)
    async def _poll_status(self) -> None:
        try:
            proc = await asyncio.create_subprocess_exec(
                "docker",
                "compose",
                "-f",
                str(COMPOSE_FILE),
                "ps",
                "--format",
                "json",
                "--all",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
                cwd=str(MONOREPO_ROOT),
            )
            stdout, _ = await proc.communicate()
            new_status: dict[str, str] = {}
            for line in stdout.decode().strip().splitlines():
                if not line.strip():
                    continue
                data = json.loads(line)
                new_status[data["Service"]] = data["State"]
            self.service_status = new_status
        except Exception:
            pass

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "toggle-advanced":
            show = event.value
            for field in self.query(EnvField):
                if field.hidden_by_spec:
                    field.styles.display = "block" if show else "none"
            try:
                self.query_one(HoudiniSection).set_show_advanced(show)
            except Exception:
                pass
        elif event.checkbox.id == "toggle-secrets":
            reveal = event.value
            for field in self.query(EnvField):
                field.set_reveal_secrets(reveal)
            try:
                self.query_one(HoudiniSection).set_reveal_secrets(reveal)
            except Exception:
                pass
            try:
                self.query_one("#su-password", Input).password = not reveal
            except Exception:
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if not btn_id:
            return
        
        # Guard docker commands if unconfigured
        if btn_id in ["btn-start-all", "btn-stop-all", "btn-migrate", "btn-create-su"] or \
           btn_id.startswith("start-") or btn_id.startswith("stop-") or btn_id.startswith("logs-"):
            if not check_env_files_exist():
                self.notify("Please save environment configurations first!", severity="warning")
                event.stop()
                return

        if btn_id == "btn-save-config":
            self.save_configurations()
        elif btn_id == "btn-copy-logs":
            try:
                log_widget = self.query_one("#log-console", SelectableRichLog)
                full_text = "\n".join(log_widget.history)
                self.copy_to_clipboard(full_text)
                self.notify("[OK] Logs copied to clipboard!", severity="information")
            except Exception as e:
                self.notify(f"Failed to copy logs: {e}", severity="error")
        elif btn_id == "btn-start-all":
            self.stream_compose("up", "-d")
        elif btn_id == "btn-stop-all":
            self.stream_compose("down")
        elif btn_id == "btn-migrate":
            self.run_migrations()
        elif btn_id == "btn-create-su":
            self.run_create_superuser()
        elif btn_id.startswith("start-"):
            svc = btn_id[len("start-"):]
            self.stream_compose("up", "-d", svc)
        elif btn_id.startswith("stop-"):
            svc = btn_id[len("stop-"):]
            self.stream_compose("stop", svc)
        elif btn_id.startswith("open-"):
            svc = btn_id[len("open-"):]
            if svc in SERVICE_PORTS:
                port = SERVICE_PORTS[svc]
                url = f"http://localhost:{port}"
                try:
                    import webbrowser
                    webbrowser.open(url)
                    log = self.query_one("#log-console", RichLog)
                    log.write(f"[bold blue]Opening {url} in browser...[/bold blue]")
                    self.notify(f"Opening {url}", severity="information")
                except Exception as e:
                    self.notify(f"Failed to open browser: {e}", severity="error")
        elif btn_id.startswith("logs-"):
            svc = btn_id[len("logs-"):]
            self.stream_compose("logs", "--follow", "--tail=100", svc)
        
        event.stop()

    def save_configurations(self) -> None:
        try:
            log = self.query_one("#log-console", RichLog)
            log.write("[bold blue]Saving environment configurations...[/bold blue]")
            
            # 1. Save general services dotenv files
            dir_map = {
                "backend-api": "backend-api",
                "frontend-app": "frontend-app",
                "website-vexil": "website-vexil",
            }
            
            for service_name, service_dir in dir_map.items():
                section = self.query_one(f"#section-{service_name}", ServiceSection)
                values = section.get_values()
                env_path = MONOREPO_ROOT / "apps" / service_dir / ".env"
                lines = [f"{k}={v}\n" for k, v in values.items()]
                env_path.write_text("".join(lines))
                log.write(f"[dim]Wrote {env_path.relative_to(MONOREPO_ROOT)}[/dim]")
                
            # 2. Save Houdini env.yaml settings
            houdini_sec = self.query_one(HoudiniSection)
            h_values = houdini_sec.get_values()
            
            yaml_lines = [
                f"houdini_install_path: {h_values['houdini_install_path']}\n",
                f"projects_root: {h_values['projects_root']}\n",
                f"mode: {h_values['mode']}\n",
                f"log_level: {h_values['log_level']}\n",
                f"houdini_path: {h_values['houdini_path']}\n",
                f"pythonpath: {h_values['pythonpath']}\n",
            ]
            if h_values['mode'] == 'online':
                yaml_lines.extend([
                    "online:\n",
                    f"  api_url: {h_values['online']['api_url']}\n",
                    f"  username: {h_values['online']['username']}\n",
                    f"  password: {h_values['online']['password']}\n",
                ])
            else:
                yaml_lines.extend([
                    "local:\n",
                    f"  config_dir: {h_values['local']['config_dir']}\n",
                    f"  db_dir: {h_values['local']['db_dir']}\n",
                    f"  data_dir: {h_values['local']['data_dir']}\n",
                ])
            
            yaml_path = MONOREPO_ROOT / "apps" / "plugins" / "houdini-package" / "env.yaml"
            yaml_path.write_text("".join(yaml_lines))
            log.write(f"[dim]Wrote {yaml_path.relative_to(MONOREPO_ROOT)}[/dim]")
            
            # Clean up old .env from Houdini plugins folder
            old_dotenv = MONOREPO_ROOT / "apps" / "plugins" / "houdini-package" / ".env"
            if old_dotenv.is_file():
                try:
                    old_dotenv.unlink()
                    log.write(f"[dim]Removed obsolete .env from plugins folder[/dim]")
                except Exception:
                    pass
            
            # 3. Reload variables
            global LOADED_ENV
            LOADED_ENV.clear()
            LOADED_ENV.update(load_all_env_files())
            
            log.write("[green][OK] Environment configurations written successfully![/green]")
            self.notify("Configurations saved!", severity="information")
            self.update_config_status()
            
        except Exception as e:
            self.query_one("#log-console", RichLog).write(f"[bold red]Error saving configurations: {e}[/bold red]")
            self.notify("Failed to save configurations", severity="error")

    @work(exclusive=True, group="docker-stream", exit_on_error=False)
    async def stream_compose(self, *args: str) -> None:
        log = self.query_one("#log-console", RichLog)
        log.write(f"[dim]$ docker compose {' '.join(args)}[/dim]")
        proc = await asyncio.create_subprocess_exec(
            "docker",
            "compose",
            "-f",
            str(COMPOSE_FILE),
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(MONOREPO_ROOT),
        )
        try:
            assert proc.stdout is not None
            async for raw in proc.stdout:
                log.write(raw.decode(errors="replace").rstrip())
            await proc.wait()
            rc = proc.returncode
            log.write(f"[{'green' if rc == 0 else 'red'}]exit {rc}[/]")
        except asyncio.CancelledError:
            proc.terminate()
            await proc.wait()
            log.write("[dim]cancelled[/dim]")
            raise
        self.call_after_refresh(self._poll_status)

    @work(exclusive=True, group="docker-stream", exit_on_error=False)
    async def run_migrations(self) -> None:
        log = self.query_one("#log-console", RichLog)
        
        # Check container state
        states = self.service_status
        if "running" not in states.get("backend-api", ""):
            log.write("[bold yellow]Warning: backend-api container is not running. Starting it first...[/bold yellow]")
            proc = await asyncio.create_subprocess_exec(
                "docker", "compose", "-f", str(COMPOSE_FILE), "up", "-d", "backend-api",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=str(MONOREPO_ROOT)
            )
            assert proc.stdout is not None
            async for raw in proc.stdout:
                log.write(raw.decode(errors="replace").rstrip())
            await proc.wait()
            await asyncio.sleep(2)
        
        log.write("[bold blue]Applying Django database migrations inside container...[/bold blue]")
        log.write("[dim]$ docker compose exec backend-api uv run python manage.py migrate[/dim]")
        
        proc = await asyncio.create_subprocess_exec(
            "docker", "compose", "-f", str(COMPOSE_FILE), "exec", "backend-api",
            "uv", "run", "python", "manage.py", "migrate",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(MONOREPO_ROOT),
        )
        try:
            assert proc.stdout is not None
            async for raw in proc.stdout:
                log.write(raw.decode(errors="replace").rstrip())
            await proc.wait()
            rc = proc.returncode
            if rc == 0:
                log.write("[green][OK] Database migrations applied successfully![/green]")
                self.notify("Migrations completed!", severity="information")
            else:
                log.write(f"[red][FAIL] Migrations failed with exit code {rc}[/red]")
                self.notify("Migrations failed!", severity="error")
        except Exception as e:
            log.write(f"[red]Error running migrations: {e}[/red]")

    @work(exclusive=True, group="docker-stream", exit_on_error=False)
    async def run_create_superuser(self) -> None:
        log = self.query_one("#log-console", RichLog)
        
        states = self.service_status
        if "running" not in states.get("backend-api", ""):
            log.write("[bold red]Error: backend-api container must be running to create a superuser.[/bold red]")
            self.notify("backend-api not running!", severity="error")
            return
            
        username = self.query_one("#su-username", Input).value
        email = self.query_one("#su-email", Input).value
        password = self.query_one("#su-password", Input).value
        
        if not username or not password:
            log.write("[bold red]Error: Username and Password are required.[/bold red]")
            self.notify("Missing credentials!", severity="error")
            return
            
        log.write(f"[bold blue]Creating superuser '{username}'...[/bold blue]")
        log.write("[dim]$ docker compose exec -e DJANGO_SUPERUSER_USERNAME=... backend-api uv run python manage.py createsuperuser --noinput[/dim]")
        
        proc = await asyncio.create_subprocess_exec(
            "docker", "compose", "-f", str(COMPOSE_FILE), "exec",
            "-e", f"DJANGO_SUPERUSER_USERNAME={username}",
            "-e", f"DJANGO_SUPERUSER_EMAIL={email}",
            "-e", f"DJANGO_SUPERUSER_PASSWORD={password}",
            "backend-api", "uv", "run", "python",
            "manage.py", "createsuperuser", "--noinput",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(MONOREPO_ROOT),
        )
        try:
            assert proc.stdout is not None
            async for raw in proc.stdout:
                log.write(raw.decode(errors="replace").rstrip())
            await proc.wait()
            rc = proc.returncode
            if rc == 0:
                log.write(f"[green][OK] Superuser '{username}' created successfully![/green]")
                self.notify("Superuser created!", severity="information")
            else:
                log.write(f"[red][FAIL] Failed to create superuser (code {rc}). It might already exist.[/red]")
                self.notify("Superuser creation failed!", severity="warning")
        except Exception as e:
            log.write(f"[red]Error creating superuser: {e}[/red]")


def main() -> None:
    VexilApp().run()


if __name__ == "__main__":
    main()
