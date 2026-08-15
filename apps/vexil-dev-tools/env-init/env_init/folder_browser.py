"""In-app directory browser for Streamlit (no native OS dialog)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class FolderBrowserError(ValueError):
    """Raised when navigation would escape the allowed root."""


@dataclass
class FolderBrowserState:
    root: Path
    current: Path

    def __post_init__(self) -> None:
        self.root = self.root.resolve()
        self.current = self.current.resolve()
        self._ensure_under_root(self.current)

    def _ensure_under_root(self, path: Path) -> Path:
        resolved = path.resolve()
        try:
            resolved.relative_to(self.root)
        except ValueError as exc:
            raise FolderBrowserError(
                f"Path {resolved} is outside allowed root {self.root}"
            ) from exc
        return resolved

    def list_dirs(self) -> list[Path]:
        if not self.current.is_dir():
            return []
        children = [p for p in self.current.iterdir() if p.is_dir() and not p.name.startswith(".")]
        return sorted(children, key=lambda p: p.name.lower())

    def enter(self, child: Path | str) -> Path:
        target = self.current / Path(child).name if not Path(child).is_absolute() else Path(child)
        self.current = self._ensure_under_root(target)
        return self.current

    def go_up(self) -> Path:
        if self.current == self.root:
            return self.current
        parent = self.current.parent
        self.current = self._ensure_under_root(parent)
        return self.current

    def can_go_up(self) -> bool:
        return self.current != self.root

    def select_current(self) -> Path:
        return self.current


def _sanitize_start_path(root: Path, start: Path | None) -> Path:
    root = root.resolve()
    if start is None:
        return root

    untrusted = Path(start)
    if untrusted.is_absolute():
        try:
            relative_candidate = untrusted.relative_to(root)
        except ValueError:
            return root
    else:
        relative_candidate = untrusted

    if ".." in relative_candidate.parts:
        return root

    try:
        candidate = (root / relative_candidate).resolve()
    except OSError:
        return root
    try:
        candidate.relative_to(root)
    except ValueError:
        return root
    if not candidate.is_dir():
        return root
    return candidate


def init_browser(root: Path, start: Path | None = None) -> FolderBrowserState:
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    start_path = _sanitize_start_path(root, start)
    return FolderBrowserState(root=root, current=start_path)
