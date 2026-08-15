"""CLI entry that launches Streamlit on the configured port."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from env_init.config import DEFAULT_TOML, load_config


def main() -> None:
    cfg = load_config(DEFAULT_TOML)
    main_py = Path(__file__).resolve().parents[1] / "main.py"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(main_py),
        "--server.port",
        str(cfg.env_init.port),
    ]
    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
