---
title: Getting Started
description: Set up a VEXiL development environment with Devcontainer or native tooling.
---

This guide gets you from a fresh clone to running the monorepo locally.

## Prerequisites

| Tool | Notes |
| ---- | ----- |
| [Bun](https://bun.sh) | Package manager / workspace runner (`packageManager` pins [Bun](https://bun.sh) 1.3.x) |
| [Turborepo](https://turborepo.com) | Task runner used by `bun run dev` → `turbo run dev` (installed via root `devDependencies`) |
| [Go 1.26.x](https://go.dev/dl/) | Backend API (`apps/vexil-server`) |
| [uv](https://docs.astral.sh/uv/) + [Python 3.13](https://www.python.org/downloads/) | Houdini plugin + `dev-tools/env-init` |
| [SideFX Houdini 22](https://www.sidefx.com/download/) | Required for the Houdini plugin and DCC-centric workflows |
| [Docker](https://www.docker.com/products/docker-desktop/) (optional) | Compose workflow |

### Why Bun?

VEXiL uses Bun for fast installs and first-class workspaces that fit this monorepo. Root scripts and `packageManager` assume Bun. You can use another package manager if you prefer — just know that docs, CI, and examples stay Bun-oriented.

## Optional: Devcontainer

Config lives under `.devcontainer/` at the repository root. If your editor supports Dev Containers, reopen the repo in the container; post-create runs `bun install` and `bun run setup`. Otherwise use manual setup below with [Zed](https://zed.dev) or [GoLand](https://www.jetbrains.com/go/).

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

This uses [Turborepo](https://turborepo.com) (`turbo run dev`) to start workspace `dev` scripts (backend API, frontend app, website for VEXiL). See [Local services & ports](/reference/local-services/) for URLs.

Run a single app when you only need one surface (pick one):

```bash
cd apps/vexil-server && bun run dev
```

```bash
cd apps/vexil-frontend && bun run dev
```

```bash
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
