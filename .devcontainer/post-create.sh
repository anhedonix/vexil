#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Named volumes are created empty and root-owned on first use; reclaim them
# for the `vscode` user before installing into them.
sudo mkdir -p \
  node_modules \
  apps/packages/houdini-package-src/.venv \
  apps/vexil-dev-tools/env-init/.venv
sudo chown -R vscode:vscode \
  node_modules \
  apps/packages/houdini-package-src/.venv \
  apps/vexil-dev-tools/env-init/.venv

# TODO(later): route uv-installed Python libs for apps/packages/houdini-package-src
# into that package's Houdini `PythonLibs` folder instead of a standalone
# .venv, so Houdini's own Python can pick them up. Deferred for now.

bun install
bun run setup
