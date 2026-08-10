---
title: Repository Structure
description: Active packages in the VEXiL monorepo and what each one is for.
---

VEXiL is a **Bun workspaces + Turborepo** monorepo. Workspaces are declared at the repository root as `apps/*`, `apps/plugins/*`, and `dev-tools/*`.

## Layout

```text
vexil/
├── apps/
│   ├── backend-api/              # Go Gin API
│   ├── frontend-app/             # Product UI (Astro)
│   ├── website-vexil/            # Marketing site (Astro + Tailwind)
│   └── plugins/
│       └── houdini-package/      # Houdini plugin (Python 3.13 / uv)
├── dev-tools/
│   └── env-init/                 # Env / Docker TUI (Textual)
├── docs/
│   └── dev/                      # VEXiL Dev Docs (Starlight; not in workspaces)
├── .devcontainer/                # Recommended VS Code Devcontainer
├── docker-compose.yml
├── package.json                  # Root scripts: setup, dev
└── turbo.json
```

## Active packages

| Path | Stack | Purpose |
| ---- | ----- | ------- |
| `apps/backend-api` | Go, Gin | Backend API for the product |
| `apps/frontend-app` | Astro | Main project-management web app |
| `apps/website-vexil` | Astro 7, Tailwind 4 | Public marketing / waitlist site |
| `apps/plugins/houdini-package` | Python 3.13, uv | SideFX Houdini integration package |
| `dev-tools/env-init` | Python 3.13, Textual | Interactive env scaffolding and Docker helpers |
| `docs/dev` | Astro Starlight | Contributor handbook at [dev-docs.vexil.tools](https://dev-docs.vexil.tools) |

## Root scripts

From the repository root:

| Script | What it does |
| ------ | ------------ |
| `bun install` | Install JS workspace dependencies |
| `bun run setup` | `uv sync` for Python packages + `go mod download` for the API |
| `bun run dev` | `turbo run dev` across workspace packages |

## Legacy paths

You may still see empty or leftover directories under older names (for example historical `apps/backend`, `apps/frontend`, `apps/website`, or `apps/houdini-package`). **Do not use those for new work.** Prefer the paths in the table above.

## Where to change what

| If you are changing… | Edit… |
| -------------------- | ----- |
| API behavior | `apps/backend-api` |
| In-app product UI | `apps/frontend-app` |
| Marketing / waitlist | `apps/website-vexil` |
| Houdini DCC integration | `apps/plugins/houdini-package` |
| Env scaffolding TUI | `dev-tools/env-init` |
| This handbook | `docs/dev` |
