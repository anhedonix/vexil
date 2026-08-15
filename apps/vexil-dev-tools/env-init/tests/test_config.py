"""Tests for config load/save and salt helpers."""

from __future__ import annotations

from pathlib import Path

from env_init.config import VexilConfig, load_config, save_config
from env_init.salt import ensure_salt, generate_salt, is_placeholder_salt


def test_placeholder_salt_detection() -> None:
    assert is_placeholder_salt("UUID")
    assert is_placeholder_salt("")
    assert not is_placeholder_salt("real-salt-value")


def test_generate_salt_is_long() -> None:
    salt = generate_salt()
    assert len(salt) >= 32


def test_load_config_generates_salt(tmp_path: Path) -> None:
    toml = tmp_path / "vexil.toml"
    toml.write_text(
        """
[base]
version = "0.1.2"
dev = true
os = "darwin"
scratch = "../../../.scratch"

[vexil-io]
salt = "UUID"
port = 6600
""".strip()
        + "\n",
        encoding="utf-8",
    )
    cfg = load_config(toml)
    assert not is_placeholder_salt(cfg.vexil_io.salt)
    assert cfg.vexil_io.port == 6600


def test_round_trip_toml(tmp_path: Path) -> None:
    path = tmp_path / "vexil.toml"
    cfg = VexilConfig()
    cfg.vexil_io.salt = ensure_salt(None)
    cfg.vexil_io.port = 6600
    cfg.frontend.port = 6611
    save_config(cfg, path)
    loaded = load_config(path)
    assert loaded.vexil_io.port == 6600
    assert loaded.frontend.port == 6611
    assert loaded.vexil_io.salt == cfg.vexil_io.salt
    text = path.read_text(encoding="utf-8")
    assert "[vexil-io]" in text
    assert "[backend]" not in text
