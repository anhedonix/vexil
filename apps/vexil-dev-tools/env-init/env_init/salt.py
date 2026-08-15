"""Salt helpers for vexil-io credentials."""

from __future__ import annotations

import secrets

PLACEHOLDER_SALTS = {"", "UUID", "uuid", "CHANGE_ME", "changeme"}


def is_placeholder_salt(value: str | None) -> bool:
    if value is None:
        return True
    return value.strip() in PLACEHOLDER_SALTS


def generate_salt(nbytes: int = 48) -> str:
    """Return a long URL-safe random salt."""
    return secrets.token_urlsafe(nbytes)


def ensure_salt(value: str | None = None) -> str:
    if is_placeholder_salt(value):
        return generate_salt()
    return value or generate_salt()
