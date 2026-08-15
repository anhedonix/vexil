---
title: Changelog
description: Notable changes to VEXiL across releases. Canonical copy also lives at the repository root CHANGELOG.md.
---

Notable changes to VEXiL are documented here. The same history is maintained at the repository root in `CHANGELOG.md`.

## [Unreleased]

## v0.1.3 - 2026-08-15

Streamlit-based developer environment setup, backend rename, and safer local ports.

### New Features

- **Streamlit env-init** — configure local development from a browser UI driven by `vexil.toml` (`bun run setup` / `bun run env-init` on port `6644`). Generate `.env` files, initialize Go/Bun/uv workspaces, install the Houdini 22+ package, and reset scratch/`.env` data after confirmation.
- **Patch version bump** — bump the product patch across the monorepo in one step from Streamlit or `bun run bump-version` (with a preview of every file that will change).

### Improvements

- **Renamed backend app** — `apps/vexil-server` is now `apps/vexil-io` (Go module, Compose service, and docs updated).
- **Developer-safe local ports** — defaults that are less likely to collide on a busy machine: API `6600`, frontend `6611`, website `6622`, Dev Docs `6633`, env-init `6644`.
- **Env init docs** — Dev Docs and the root README describe the Streamlit workflow (not the old Textual TUI), including Getting Started and Local services links.

### Fixes

- **Env templates stay stable** — runtime env-init writes local `.env` files only; tracked `.env.template` / `.env.example` files are no longer overwritten on every run.

## v0.1.2 - 2026-08-10

Monorepo layout consolidation under `apps/` and Dev Docs setup refresh.

### Improvements

- **Moved Dev Docs into the monorepo workspace** — Starlight site now lives at `apps/docs-dev`, joins Bun/Turborepo, and serves locally on port `4323`.
- **Moved env-init under apps** — developer TUI path is now `apps/vexil-dev-tools/env-init`.
- **Moved Houdini package** — `apps/packages/houdini-package-src` → `apps/vexil-package-src` (package renamed to match).
- **Expanded Getting Started** — download links for the toolchain, recommended Zed/GoLand editors, required SideFX Houdini 22, and a clear Bun preference blurb vs npm/Yarn/pnpm.
- **Aligned package versions** — bumped workspace packages to `0.1.2`.

## v0.1.1 - 2026-08-10

Monorepo rename and reconnect for consistent VEXiL package identities.

### Improvements

- **Renamed apps for consistent branding** — `backend-api` → `vexil-server`, `frontend-app` → `vexil-frontend`, `website-vexil` → `vexil-website`.
- **Moved Houdini package** — `apps/plugins/houdini-package` → `apps/packages/houdini-package-src`.
- **Reconnected local tooling** — Docker Compose, root setup, VS Code workspace, devcontainer, and env-init TUI now target the new paths and service names.
- **Aligned package versions** — bumped workspace packages to `0.1.1`; Pre-MVP docs banner now reads `0.1.X`.

## Unreleased - 2026-07-18

### New Features

- **Refreshed logo in the navigation bar** — the marketing site now displays the VEXiL logo image instead of a plain text wordmark.
- **Favicon added** — VEXiL now shows a proper browser tab icon and app icon across devices.
- **New GraphQL backend API** — the backend service has been rewritten in Go with a GraphQL server (via gqlgen), replacing the previous Python/Django implementation.

### Improvements

- **Upgraded to Astro 7** — the marketing website now runs on the latest version of Astro, along with updated dependencies for better performance and security.
- **Refined visual design** — polished the styling of the technical/infrastructure section of the site for a cleaner, more consistent look.
- **Better mobile browser theming** — added a theme-color meta tag so the browser UI (address bar, etc.) matches the site's branding on mobile devices.
- **Faster backend development loop** — added live-reloading (via Air) for the new Go backend, so code changes are picked up instantly during development.
- **Updated local dev environment for Go** — refreshed the dev container and Docker Compose setup (ports, caching, editor extensions) to support the new Go-based backend.
- **Faster local dev servers** — Astro dev servers now bind to all network interfaces, making it easier to preview the site from other devices on your network.
- **Faster monorepo builds** — upgraded Turborepo to the latest version (2.10.5).

### Documentation

- **Contributing guidelines** — added a pull request template and contributing guidelines to help new contributors get started.

### Fixes

- Removed a duplicate build-environment section from the Netlify configuration that could cause confusing deploy behavior.

## v0.1.0 - 2026-05-29

Initial foundation release: the VEXiL monorepo, core apps, and local developer tooling.

### New Features

- **Marketing website launched** — introduced the public VEXiL website with waitlist signup, email notifications (via Resend), and Vercel deployment support.
- **Backend API scaffold** — added the initial Django-based backend service.
- **Houdini plugin scaffold** — added the initial Houdini integration package.
- **Frontend app scaffold** — added the initial Astro-based frontend application.
- **Local development with Docker Compose** — the full stack (backend, frontend, website) can now be run locally with a single Docker Compose setup.
- **Developer TUI for environment setup** — added an interactive terminal tool that lets contributors configure environment variables, view help text, and start/stop/monitor local Docker services (including automatic port detection) without manually editing `.env` files.

### Documentation

- Published a Code of Conduct and a Security Policy for the project (Alpha stage reporting guidelines).
- Updated the README with clearer project details and setup instructions.

### Fixes

- Resolved a website build/deployment issue that broke the live site.
