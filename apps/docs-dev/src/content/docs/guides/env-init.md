---
title: Env init (Streamlit)
description: Initialize local VEXiL env files, workspaces, Houdini package, and patch versions with the Streamlit tool.
---

Use the Streamlit **env-init** app to configure a local developer environment from `vexil.toml`.

## Launch

From the repository root:

```bash
bun install
bun run setup
```

`bun run setup` syncs Python apps (`uv sync`), downloads Go modules for `apps/vexil-io`, then launches Streamlit **in the foreground** on port **6644**.

Launch the UI alone (after deps are installed):

```bash
bun run env-init
```

Or:

```bash
uv run --directory apps/vexil-dev-tools/env-init streamlit run main.py --server.port 6644
```

Open [http://localhost:6644](http://localhost:6644). Config lives at `apps/vexil-dev-tools/env-init/vexil.toml`.

## What the UI does

1. **Edit settings** — ports, credentials, project/data roots (dev mode roots must stay under repository `/.scratch`).
2. **Validate & save TOML** — persist non-version settings to `vexil.toml`.
3. **Write `.env` files** — generates local ignored `.env` files for each app. Tracked `.env.template` files are not rewritten at runtime.
4. **Initialize repositories** — `go mod download` (vexil-io), root `bun install`, and `uv sync` for Python apps (sets `init` flags on success).
5. **Houdini package (22+)** — discover preference profiles and install `packages/vexil.json`.
6. **Reset Dev Env** — after typing `RESET`, delete generated `.env` files and clear `/.scratch` (does not remove Houdini package installs or `.venv` folders).

Salt is auto-generated on load when empty or set to a placeholder.

## Bump patch version

Product versions use `MAJOR.MINOR.PATCH`. **Bump patch** increments only the patch (for example `0.1.2` → `0.1.3`).

### From Streamlit

Next to the read-only version field:

1. Review the listed files and `old → new` preview.
2. Confirm the checkbox.
3. Click **Bump patch version**.

The control disables for the rest of that UI session so you cannot bump twice without restarting the app.

### From the monorepo root

```bash
bun run bump-version
```

Shows the same location list, asks for confirmation (`y/N`), then applies. Use `--yes` for non-interactive runs and `--dry-run` to preview only:

```bash
uv run --directory apps/vexil-dev-tools/env-init python -m env_init.bump_cli --dry-run
```

### Files updated

- Root `package.json`
- `apps/vexil-io/package.json`
- `apps/vexil-frontend/package.json`
- `apps/vexil-website/package.json`
- `apps/docs-dev/package.json`
- `apps/vexil-package-src/package.json` and `pyproject.toml`
- `apps/vexil-dev-tools/env-init/pyproject.toml`
- `apps/vexil-dev-tools/env-init/vexil.toml` — **only** `[base].version` (surgical edit)

Python package bumps also refresh `uv.lock` in package-src and env-init.

### Not updated

- VS Code `launch.json` schema `version` fields
- Third-party dependency versions inside lockfiles
- Changelog history headers

See also [Local services & ports](/reference/local-services/) and [Getting Started](/guides/getting-started/).
