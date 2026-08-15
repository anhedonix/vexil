"""CLI: bump product patch version across the monorepo."""

from __future__ import annotations

import argparse
import sys

from env_init.config import MONOREPO_ROOT
from env_init.version_bump import (
    VersionBumpError,
    apply_version_changes,
    discover_version_changes,
    preview_lines,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bump VEXiL product patch version across the monorepo (MAJOR.MINOR.PATCH → +patch)."
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Apply without interactive confirmation",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show locations and new version without writing",
    )
    parser.add_argument(
        "--no-lock",
        action="store_true",
        help="Skip uv lock refresh after Python package bumps",
    )
    args = parser.parse_args(argv)

    try:
        changes = discover_version_changes(MONOREPO_ROOT)
    except VersionBumpError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Current → next: {changes[0].old} → {changes[0].new}")
    print("Locations:")
    for line in preview_lines(changes, MONOREPO_ROOT):
        print(f"  - {line}")

    if args.dry_run:
        print("Dry run only; no files written.")
        return 0

    if not args.yes:
        if not sys.stdin.isatty():
            print("error: non-interactive stdin; pass --yes to apply", file=sys.stderr)
            return 1
        answer = input("Apply patch bump? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            print("Aborted.")
            return 1

    try:
        apply_version_changes(changes, refresh_locks=not args.no_lock, monorepo_root=MONOREPO_ROOT)
    except VersionBumpError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Bumped product version to {changes[0].new}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
