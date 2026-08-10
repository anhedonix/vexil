---
title: Getting Started
description: Set up a VEXiL development environment with Devcontainer or native tooling.
---

This guide gets you from a fresh clone to running the monorepo locally.

## Prerequisites

| Tool | Notes |
| ---- | ----- |
| [Bun](https://bun.sh) | Package manager / workspace runner (`packageManager` pins Bun 1.3.x) |
| Go 1.26.x | Backend API (`apps/vexil-server`) |
| [uv](https://docs.astral.sh/uv/) + Python 3.13 | Houdini plugin + `dev-tools/env-init` |
| Docker (optional) | Compose workflow |
| VS Code + Dev Containers (recommended) | Matches `.devcontainer/` |
| SideFX Houdini (optional) | Only for plugin work |

## Recommended: Devcontainer

1. Open the repository in VS Code.
2. **Reopen in Container** when prompted (or Command Palette → `Dev Containers: Reopen in Container`).
3. Post-create runs `bun install` and `bun run setup`.

Config lives under `.devcontainer/` at the repository root.

## Manual setup

From the repository root:

```bash
bun install
bun run setup
```

`bun run setup` syncs Python envs (`uv sync` for the Houdini package and env-init TUI) and downloads Go modules for the backend.

Optional env / Docker helper TUI:

```bash
uv run --directory dev-tools/env-init main.py
```

## Run the monorepo

```bash
bun run dev
```

This uses Turborepo to start workspace `dev` scripts (backend API, frontend app, marketing site). See [Local services & ports](/reference/local-services/) for URLs.

Run a single app when you only need one surface:

```bash
cd apps/vexil-server && bun run dev
cd apps/vexil-frontend && bun run dev
cd apps/vexil-website && bun run dev
```

## Docker Compose

```bash
docker compose up --build -d
```

Compose maps host port ranges for services so local conflicts are less likely. Tear down with `docker compose down`.

## These docs

`docs/dev` is **outside** the root Bun workspaces. From that directory:

```bash
cd docs/dev
bun install
bun run dev
```

Production host: [https://dev-docs.vexil.tools](https://dev-docs.vexil.tools).

## Next steps

- [Repository Structure](/guides/repository-structure/) — where to put changes
- [Contributing](/guides/contributing/) — branches, PRs, AI policy
