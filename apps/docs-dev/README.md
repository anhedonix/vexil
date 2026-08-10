# Dev Docs | VEXiL

Source of truth for developing and contributing to [VEXiL](https://github.com/anhedonix/vexil).

**Production:** [https://dev-docs.vexil.tools](https://dev-docs.vexil.tools)

This Astro Starlight site lives at `apps/docs-dev` in the monorepo. It is part of the root Bun workspaces (`apps/*`).

## Commands

From the repository root (`bun install` once for all workspaces), or from this directory:

| Command | Action |
| :------ | :----- |
| `bun run dev` | Local dev server on port `4323` |
| `bun run build` | Production build to `./dist/` |
| `bun run preview` | Preview the production build |

Root `bun run dev` (Turborepo) also starts this package alongside the other apps.

## Content

Docs content lives in `src/content/docs/`. Site branding and sidebar are configured in `astro.config.mjs`.
