---
title: Repository Structure
description: Active packages in the VEXiL monorepo and what each one is for.
---

VEXiL is a **Bun workspaces + Turborepo** monorepo. Workspaces are declared at the repository root as `apps/*` and `apps/vexil-dev-tools/*`.

## Layout

```text
vexil/
├── apps/
│   ├── vexil-server/              # Go Gin API
│   ├── vexil-frontend/            # Product UI (Astro)
│   ├── vexil-website/             # Website for VEXiL (Astro + Tailwind)
│   ├── docs-dev/                  # Dev Docs | VEXiL (Starlight; port 4323)
│   ├── vexil-dev-tools/
│   │   └── env-init/              # Env / Docker TUI (Textual)
│   └── vexil-package-src/         # Houdini plugin (Python 3.13 / uv)
├── .devcontainer/                 # Optional Devcontainer
├── docker-compose.yml
├── package.json                   # Root scripts: setup, dev
└── turbo.json
```

## Active packages

| Path | Stack | Purpose |
| ---- | ----- | ------- |
| `apps/vexil-server` | Go, Gin | Backend API for the product |
| `apps/vexil-frontend` | Astro | Main project-management web app |
| `apps/vexil-website` | Astro 7, Tailwind 4 | Website for VEXiL |
| `apps/docs-dev` | Astro Starlight | Contributor handbook at [dev-docs.vexil.tools](https://dev-docs.vexil.tools) |
| `apps/vexil-package-src` | Python 3.13, uv | SideFX Houdini 22 integration package |
| `apps/vexil-dev-tools/env-init` | Python 3.13, Textual | Interactive env scaffolding and Docker helpers |

## Root scripts

From the repository root:

| Script | What it does |
| ------ | ------------ |
| `bun install` | Install JS workspace dependencies |
| `bun run setup` | `uv sync` for Python packages + `go mod download` for the API |
| `bun run dev` | `turbo run dev` across workspace packages |

## Legacy paths

You may still see empty or leftover directories under older names (for example historical `apps/backend-api`, `apps/frontend-app`, `apps/website-vexil`, `apps/plugins/houdini-package`, or `apps/packages/houdini-package-src`). **Do not use those for new work.** Prefer the paths in the table above.

## Where to change what

| If you are changing… | Edit… |
| -------------------- | ----- |
| API behavior | `apps/vexil-server` |
| In-app product UI | `apps/vexil-frontend` |
| Website for VEXiL | `apps/vexil-website` |
| Houdini DCC integration | `apps/vexil-package-src` |
| Env scaffolding TUI | `apps/vexil-dev-tools/env-init` |
| This handbook | `apps/docs-dev` |
