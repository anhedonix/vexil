## Learned User Preferences

- Prefer atomic conventional commits after each coherent change unit; when todos are in progress, commit after each completed todo when the atomic-commits skill is in play
- Prefer REST APIs over GraphQL; no TUIs — product surfaces should be UI
- Prefer TOML for config/storage (not JSON); use SQLite as the basic database
- Prefer ADHD-friendly, simple-to-follow planning artifacts when specifying MVP scope
- Treat VEXiL Dev Docs as the source of truth for development and contributions; keep a clear pre-MVP breaking-change disclaimer
- Refer to `apps/vexil-website` as the VEXiL website; do not call it marketing
- Prefer Bun for the monorepo, but treat it as a preference — developers may use other workspace-aware package managers (e.g. pnpm)
- In Dev Docs Getting Started: require SideFX Houdini; include Zed and GoLand as editor options; link prerequisite software/language names to their download sites

## Learned Workspace Facts

- Do not use leftover directories under older names (`backend-api`, `frontend-app`, `website-vexil`, `plugins/houdini-package`, `packages/houdini-package-src`, etc.) for new work
- Bun workspaces + Turborepo monorepo; primary apps are `apps/vexil-server`, `apps/vexil-frontend`, and `apps/vexil-website`; Houdini package source lives at `apps/vexil-package-src` (not under `apps/plugins/` or `apps/packages/`); env-init TUI lives at `apps/vexil-dev-tools/env-init`
- Backend is Go with Gin (API port not finalized); Houdini/plugin work targets Python 3.13 and SideFX Houdini 22
- VEXiL Dev Docs live at `apps/docs-dev` (Starlight with Theme Black; site title `Dev Docs | VEXiL`; in root Bun workspaces), intended host `dev-docs.vexil.tools`; pre-MVP versioning is `0.1.X` with expected breaking changes or restructuring; changelogs are surfaced in docs-dev
- Core hierarchy is Project → Sequence → Shot → Scene (`.hip`); explicit publish with a comment creates a version, while every save creates a backup
- Phase-1 primary audience is solo freelancers; local and online install ship, LAN may remain a stub
- Default start frame is `1001` when unset
