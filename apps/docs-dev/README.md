# Dev Docs | VEXiL

Source of truth for developing and contributing to [VEXiL](https://github.com/anhedonix/vexil).

**Production:** [https://dev-docs.vexil.tools](https://dev-docs.vexil.tools)

This Astro Starlight site lives at `docs/dev` in the monorepo. It is **not** part of the root Bun workspaces — install and run it from this directory.

## Commands

| Command | Action |
| :------ | :----- |
| `bun install` | Install dependencies |
| `bun run dev` | Local dev server |
| `bun run build` | Production build to `./dist/` |
| `bun run preview` | Preview the production build |

## Content

Docs content lives in `src/content/docs/`. Site branding and sidebar are configured in `astro.config.mjs`.
