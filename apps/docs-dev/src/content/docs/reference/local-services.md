---
title: Local services & ports
description: How VEXiL services run locally, known frontend ports, and backend API port status.
---

## Backend API (`apps/vexil-io`)

- **Stack:** Go with **Gin** (legacy gqlgen scaffold may still be present until replaced).
- **Default listen port:** `6600` (uncommon developer-safe default; override with `PORT` in `.env`).
- When you run `bun run dev` or `cd apps/vexil-io && bun run dev`, check the process output (and any `.env` in that package) for the port currently in use.
- Docker Compose publishes host `6600` into the API container for development.

## Frontend app (`apps/vexil-frontend`)

| Item | Value |
| ---- | ----- |
| Framework | Astro |
| Typical local URL | `http://localhost:6611` |
| Dev script | `astro dev --host --port 6611` |

## Website for VEXiL (`apps/vexil-website`)

| Item | Value |
| ---- | ----- |
| Framework | Astro + Tailwind |
| Expected local port | `6622` |
| Note | Compose maps the website service to host `6622`. |

## Dev Docs (`apps/docs-dev`)

| Item | Value |
| ---- | ----- |
| Local | `http://localhost:6633` (`bun run dev` from `apps/docs-dev`, or via root Turborepo) |
| Production | [https://dev-docs.vexil.tools](https://dev-docs.vexil.tools) |

## Docker Compose overview

From the repository root:

```bash
docker compose up --build -d
docker compose down
```

Services defined in `docker-compose.yml`:

| Service | Package | Host port |
| ------- | ------- | --------- |
| `vexil-io` | `apps/vexil-io` | `6600` |
| `vexil-frontend` | `apps/vexil-frontend` | `6611` |
| `vexil-website` | `apps/vexil-website` | `6622` |

Inspect `docker compose ps` for the actual published ports.

## Env init (Streamlit)

```bash
uv run --directory apps/vexil-dev-tools/env-init streamlit run main.py --server.port 6644
```

Use this to scaffold local config from `vexil.toml`, initialize workspaces, and install the Houdini package. Prefer this handbook and the current `apps/vexil-io` code when something looks stale.
