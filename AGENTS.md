## Learned User Preferences

- Prefer atomic conventional commits after each coherent change unit; when todos are in progress, commit after each completed todo when the atomic-commits skill is in play
- Prefer REST APIs over GraphQL; no TUIs — product surfaces should be UI
- Prefer TOML for config/storage (not JSON); use SQLite as the basic database
- Prefer ADHD-friendly, simple-to-follow planning artifacts when specifying MVP scope
- Treat VEXiL Dev Docs as the source of truth for development and contributions; keep a clear pre-MVP breaking-change disclaimer

## Learned Workspace Facts

- Bun workspaces + Turborepo monorepo; primary apps are `apps/vexil-server`, `apps/vexil-frontend`, and `apps/vexil-website`; Houdini package source lives at `apps/packages/houdini-package-src` (not under `apps/plugins/`)
- Do not use leftover directories under older names (`backend-api`, `frontend-app`, `website-vexil`, `plugins/houdini-package`, etc.) for new work
- Backend is Go with Gin (API port not finalized); Houdini/plugin work targets Python 3.13 and SideFX Houdini 22
- VEXiL Dev Docs live at `apps/docs-dev` (Starlight; in root Bun workspaces), intended host `dev-docs.vexil.tools`; pre-MVP versioning is `0.1.X` with expected breaking changes or restructuring
- Core hierarchy is Project → Sequence → Shot → Scene (`.hip`); explicit publish with a comment creates a version, while every save creates a backup
- Phase-1 primary audience is solo freelancers; local and online install ship, LAN may remain a stub
- Default start frame is `1001` when unset
