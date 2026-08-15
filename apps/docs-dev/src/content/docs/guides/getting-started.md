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
| [Go 1.26.x](https://go.dev/dl/) | Backend API (`apps/vexil-io`) |
| [uv](https://docs.astral.sh/uv/) + [Python 3.13](https://www.python.org/downloads/) / [3.14](https://www.python.org/downloads/) | Houdini plugin (3.13); Streamlit env-init (3.14+) |
| [SideFX Houdini 22](https://www.sidefx.com/download/) | Required for the Houdini plugin and DCC-centric workflows |
| [Docker](https://www.docker.com/products/docker-desktop/) (optional) | Compose workflow |

### Why Bun?

VEXiL prefers [Bun](https://bun.sh) over [npm](https://www.npmjs.com/), [Yarn](https://yarnpkg.com/), and [pnpm](https://pnpm.io/) for speed and simple monorepo / workspace ergonomics. That is a preference, not a hard requirement — you are free to use other workspace-aware package managers such as [pnpm](https://pnpm.io/). Docs, CI, and `packageManager` examples stay Bun-oriented, so adapt commands if you choose something else.

## Recommended editors

- **[Zed](https://zed.dev)** — recommended general editor for the monorepo
- **[GoLand](https://www.jetbrains.com/go/)** — recommended for Go work in `apps/vexil-io`

Either works for the full repo; [GoLand](https://www.jetbrains.com/go/) is the stronger fit when focusing on the API.

## Optional: Devcontainer

Config lives under `.devcontainer/` at the repository root. If your editor supports Dev Containers, reopen the repo in the container; post-create runs `bun install` and `bun run setup`. Otherwise use [manual setup](#manual-setup) with [Zed](https://zed.dev) or [GoLand](https://www.jetbrains.com/go/).

## Manual setup

From the repository root:

```bash
bun install
bun run setup
```

`bun run setup` syncs Python envs (`uv sync` for the Houdini package and Streamlit env-init) and downloads Go modules for the backend.

Optional Streamlit env initializer:

```bash
uv run --directory apps/vexil-dev-tools/env-init streamlit run main.py --server.port 6644
```

## Run the monorepo

```bash
bun run dev
```

This uses [Turborepo](https://turborepo.com) (`turbo run dev`) to start workspace `dev` scripts (backend API, frontend app, website for VEXiL). See [Local services & ports](/reference/local-services/) for URLs.

Run a single app when you only need one surface (pick one):

```bash
cd apps/vexil-io && bun run dev
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

`apps/docs-dev` is a Bun workspace package. Root `bun run dev` starts it via Turborepo (port `6633`). To run only the docs:

```bash
cd apps/docs-dev
bun run dev
```

Production host: [https://dev-docs.vexil.tools](https://dev-docs.vexil.tools).

## Next steps

- [Repository Structure](/guides/repository-structure/) — where to put changes
- [Contributing](/guides/contributing/) — branches, PRs, AI policy
