---
title: Local services & ports
description: How VEXiL services run locally, known frontend ports, and backend API port status.
---

## Backend API (`apps/vexil-server`)

- **Stack:** Go with **Gin**.
- **Default listen port:** **not finalized yet.** Do not treat any hard-coded API port in older README snippets or tooling labels as the permanent contract.
- When you run `bun run dev` or `cd apps/vexil-server && bun run dev`, check the process output (and any `.env` in that package) for the port currently in use.
- Docker Compose currently publishes a host range that maps into the container’s internal listen port for development; that mapping may change as the default port is finalized.

## Frontend app (`apps/vexil-frontend`)

| Item | Value |
| ---- | ----- |
| Framework | Astro |
| Typical local URL | `http://localhost:4321` |
| Dev script | `astro dev --host` |

## Website for VEXiL (`apps/vexil-website`)

| Item | Value |
| ---- | ----- |
| Framework | Astro + Tailwind |
| Expected local port (Devcontainer / Compose) | `4322` when that port is free |
| Note | The package `dev` script uses Astro’s default port unless overridden; Compose maps the website service toward host `4322+`. |

## Dev Docs (`apps/docs-dev`)

| Item | Value |
| ---- | ----- |
| Local | `http://localhost:4323` (`bun run dev` from `apps/docs-dev`, or via root Turborepo) |
| Production | [https://dev-docs.vexil.tools](https://dev-docs.vexil.tools) |

## Docker Compose overview

From the repository root:

```bash
docker compose up --build -d
docker compose down
```

Services defined in `docker-compose.yml`:

| Service | Package | Host port mapping (ranges) |
| ------- | ------- | -------------------------- |
| `vexil-server` | `apps/vexil-server` | Dynamic range into the API container |
| `vexil-frontend` | `apps/vexil-frontend` | `4321–4399` → container `4321` |
| `vexil-website` | `apps/vexil-website` | `4322–4399` → container `4321` |

Ranges avoid collisions when a preferred host port is already taken. Inspect `docker compose ps` for the actual published ports.

## Env init TUI

```bash
uv run --directory dev-tools/env-init main.py
```

Use this to scaffold local config and manage Compose. Some TUI actions may still reflect older backend assumptions — prefer this handbook and the current `apps/vexil-server` code when something looks stale.
