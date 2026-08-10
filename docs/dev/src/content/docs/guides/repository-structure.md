---
title: Repository Structure
description: Active packages in the VEXiL monorepo and what each one is for.
---

VEXiL is a **Bun workspaces + Turborepo** monorepo. Workspaces are declared at the repository root as `apps/*`, `apps/packages/*`, and `dev-tools/*`.

## Layout

```text
vexil/
├── apps/
│   ├── vexil-server/              # Go Gin API
│   ├── vexil-frontend/             # Product UI (Astro)
│   ├── vexil-website/            # Marketing site (Astro + Tailwind)
│   └── packages/
│       └── houdini-package-src/      # Houdini plugin (Python 3.13 / uv)
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
| `apps/vexil-server` | Go, Gin | Backend API for the product |
| `apps/vexil-frontend` | Astro | Main project-management web app |
| `apps/vexil-website` | Astro 7, Tailwind 4 | Public marketing / waitlist site |
| `apps/packages/houdini-package-src` | Python 3.13, uv | SideFX Houdini integration package |
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
| API behavior | `apps/vexil-server` |
| In-app product UI | `apps/vexil-frontend` |
| Marketing / waitlist | `apps/vexil-website` |
| Houdini DCC integration | `apps/packages/houdini-package-src` |
| Env scaffolding TUI | `dev-tools/env-init` |
| This handbook | `docs/dev` |
