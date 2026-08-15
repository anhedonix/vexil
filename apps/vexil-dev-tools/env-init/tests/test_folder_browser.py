"""Tests for in-app folder browser."""

from __future__ import annotations

from pathlib import Path

import pytest

from env_init.folder_browser import FolderBrowserError, init_browser


def test_browser_lists_and_enters(tmp_path: Path) -> None:
    root = tmp_path / ".scratch"
    (root / "projects" / "a").mkdir(parents=True)
    (root / "data").mkdir()
    browser = init_browser(root)
    names = {p.name for p in browser.list_dirs()}
    assert names == {"projects", "data"}
    browser.enter("projects")
    assert browser.current == (root / "projects").resolve()
    assert {p.name for p in browser.list_dirs()} == {"a"}


def test_browser_cannot_escape_root(tmp_path: Path) -> None:
    root = tmp_path / ".scratch"
    root.mkdir()
    browser = init_browser(root)
    assert not browser.can_go_up()
    browser.go_up()
    assert browser.current == root.resolve()
    with pytest.raises(FolderBrowserError):
        browser.enter(tmp_path / "outside")


def test_init_browser_clamps_start_outside_root(tmp_path: Path) -> None:
    root = tmp_path / ".scratch"
    root.mkdir()
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    browser = init_browser(root, start=outside)
    assert browser.current == root.resolve()
