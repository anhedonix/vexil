# Changelog

All notable changes to VEXiL are documented in this file.

## [Unreleased] - 2026-07-17

### ✨ New Features
- **Refreshed logo in the navigation bar** — the marketing site now displays the VEXiL logo image instead of a plain text wordmark.
- **Favicon added** — VEXiL now shows a proper browser tab icon and app icon across devices.

### 🔧 Improvements
- **Upgraded to Astro 7** — the marketing website now runs on the latest version of Astro, along with updated dependencies for better performance and security.
- **Refined visual design** — polished the styling of the technical/infrastructure section of the site for a cleaner, more consistent look.
- **Better mobile browser theming** — added a theme-color meta tag so the browser UI (address bar, etc.) matches the site's branding on mobile devices.

---

## v0.1.0 - 2026-05-29

Initial foundation release: the VEXiL monorepo, core apps, and local developer tooling.

### ✨ New Features
- **Marketing website launched** — introduced the public VEXiL website with waitlist signup, email notifications (via Resend), and Vercel deployment support.
- **Backend API scaffold** — added the initial Django-based backend service.
- **Houdini plugin scaffold** — added the initial Houdini integration package.
- **Frontend app scaffold** — added the initial Astro-based frontend application.
- **Local development with Docker Compose** — the full stack (backend, frontend, website) can now be run locally with a single Docker Compose setup.
- **Developer TUI for environment setup** — added an interactive terminal tool that lets contributors configure environment variables, view help text, and start/stop/monitor local Docker services (including automatic port detection) without manually editing `.env` files.

### 📝 Documentation
- Published a Code of Conduct and a Security Policy for the project (Alpha stage reporting guidelines).
- Updated the README with clearer project details and setup instructions.

### 🐛 Fixes
- Resolved a website build/deployment issue that broke the live site.

---

*This is the first generated changelog for the VEXiL project — entries were reconstructed from the full git history since the initial commit (2026-05-10). Internal-only changes (dependency lockfiles, editor/workspace configuration, CI scaffolding, code reorganization) have been omitted as they don't affect end users.*
