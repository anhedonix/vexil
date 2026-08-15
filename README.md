# VEXiL

VEXiL is a SideFX Houdini-centric project management tool equipped with advanced quality-of-life features. The name is a nod to Vector Expression Language (VEX), an essential part of Houdini workflows.

This workspace is structured as a monorepo containing a Django backend API, Astro frontend applications, a Houdini plugin, and environment management tools.

---

## Project Structure

The project code is organized within the following directories:

```text
vexil/
├── apps/
│   ├── vexil-io/                # Go API backend (Gin REST target)
│   ├── vexil-frontend/          # Main project management web app (Astro)
│   ├── vexil-website/           # VEXiL website (Astro + Tailwind CSS)
│   ├── docs-dev/                # Developer documentation (Starlight)
│   ├── vexil-dev-tools/
│   │   └── env-init/            # Streamlit UI for environment setup
│   └── vexil-package-src/       # Houdini integration plugin (Python package)
├── .devcontainer/               # VS Code Devcontainer configuration
└── vexil.code-workspace         # Recommended VS Code Multi-Root Workspace config
```

### Key Workspace Files

- **Root Settings**: [package.json](./package.json) | [tsconfig.json](./tsconfig.json) | [turbo.json](./turbo.json)
- **Orchestration**: [docker-compose.yml](./docker-compose.yml)
- **VS Code Workspace Config**: [vexil.code-workspace](./vexil.code-workspace)

---

## Getting Started

### 1. Devcontainer Setup (Recommended) (FIX: Moving to GoLang, needs restructuring)

The fastest way to get up and running is to use Visual Studio Code with the **Dev Containers** extension:

1. Open this repository folder in VS Code.
2. When prompted at the bottom right, click **Reopen in Container** (or run `Remote-Containers: Reopen in Container` from the Command Palette).
3. The Devcontainer automatically installs all system requirements:
   - **Base OS**: Debian Bookworm
   - **Node & JS Tooling**: Bun (installed via curl)
   - **Python Tooling**: `uv` with pre-fetched Python `3.13`.
4. VS Code will run the workspace setup command (`bun install` + `uv sync` workspaces) automatically upon creation. (TODO: using Zed editor)

_Configuration files:_ [.devcontainer/devcontainer.json](./.devcontainer/devcontainer.json) | [.devcontainer/Dockerfile](./.devcontainer/Dockerfile)

---

### 2. Manual Environment Initialization

If you prefer running services natively on your local machine:

1. **Prerequisites**: Ensure you have [Bun](https://bun.sh) and [`uv`](https://docs.astral.sh/uv/) installed.
2. **Install Workspace Dependencies**:
   Run the following setup command from the repository root:
   ```bash
   bun run setup
   ```
   _This command installs Node/TypeScript dependencies and syncs virtual environments for the Python projects using `uv` (defined in the root [package.json](./package.json))._

---

## The Dev Environment Initialization UI

VEXiL includes a Streamlit app to scaffold local configuration, initialize workspaces, and install the Houdini package.

### How to Run

```bash
uv run --directory apps/vexil-dev-tools/env-init streamlit run main.py --server.port 6644
```

_Source:_ [apps/vexil-dev-tools/env-init](./apps/vexil-dev-tools/env-init) — configuration lives in `vexil.toml`.

### Capabilities

- **Scaffold Configuration**: Generates local `.env` files and updates tracked `.env.template` files from TOML.
- **Workspace Init**: Runs `go mod download`, Bun workspace install, and `uv sync` for Python apps.
- **Houdini Package**: Installs `vexil.json` into a detected Houdini 22+ preference profile.
- **Reset Dev Env**: Clears generated `.env` files and repository `/.scratch` data after confirmation.

---

## Development Workflows

You can run Vexil using either a native local workflow or a containerized Docker workflow.

### Workflow A: Native inside Devcontainer (Fast Reloading)

Using the pre-installed tools inside the Devcontainer, you can run all services concurrently using Turbo:

```bash
bun run dev
```

This starts the following development servers:

- **Backend API**: [http://localhost:6600](http://localhost:6600) (`apps/vexil-io`)
- **Frontend App**: [http://localhost:6611](http://localhost:6611) (Astro Dev Server in [apps/vexil-frontend](./apps/vexil-frontend))
- **Website**: [http://localhost:6622](http://localhost:6622) (Astro Dev Server in [apps/vexil-website](./apps/vexil-website))
- **Dev Docs**: [http://localhost:6633](http://localhost:6633) (Starlight in [apps/docs-dev](./apps/docs-dev))

### Workflow B: Containerized (Docker Compose)

To run the production-like isolated container environment:

```bash
docker compose up --build -d
```

Docker Compose publishes uncommon developer-safe ports (`6600`, `6611`, `6622`) to reduce collisions with other local stacks.

---

## Houdini Plugin Setup

The Vexil Houdini plugin resides under [apps/vexil-package-src](./apps/vexil-package-src). To integrate it with your local SideFX Houdini installation, configure Houdini to load the package files using one of the two methods below.

### Method 1: Houdini Package Schema (Recommended)

Creating a package manifest is the modern, cleanest approach to register Houdini extensions. Create a JSON manifest file named `vexil.json` in your Houdini user preferences `packages` directory:

- **Windows**: `Documents/houdini22/packages/vexil.json`
- **Linux/macOS**: `~/houdini22/packages/vexil.json`

Add the following configuration, replacing `<path-to-repo-root>` with the absolute path to your local Vexil repository root directory:

```json
{
  "path": "<path-to-repo-root>/apps/vexil-package-src",
  "env": [{ "PYTHONPATH": "<path-to-repo-root>/apps/vexil-package-src/python" }]
}
```

### Method 2: Environment Variables

Alternatively, you can append directories directly to Houdini environment variables prior to launching Houdini:

```bash
# Add to HOUDINI_PATH
export HOUDINI_PATH="<path-to-repo-root>/apps/vexil-package-src:$HOUDINI_PATH"

# Add python scripts directory to PYTHONPATH
export PYTHONPATH="<path-to-repo-root>/apps/vexil-package-src/python:$PYTHONPATH"
```

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for
the full guide, including our development workflow and PR process.

AI tools are welcome as part of your workflow, but we don't accept
"vibe-coded" submissions — you're expected to understand, review, and test
anything you submit. See our
[AI-Assisted Development Policy](./CONTRIBUTING.md#ai-assisted-development-policy)
for details.

---

## Linting, Formatting, & Code Style (TODO: GoLang related details)

To maintain a consistent codebase, please adhere to the following development conventions:

- **Python Styling & Linting**: We utilize `ruff` for all Python formatting and linting.
  - Configuration is defined inside each project's [pyproject.toml](./apps/vexil-package-src/pyproject.toml).
  - VS Code users are encouraged to install the Ruff extension.
- **JS/TS/Astro Formatting**: Handled via the default TypeScript formatters inside the workspace.
- **Workspace Formatting Defaults**:
  - Tab size: `2` spaces
  - Format on save: Enabled (`"editor.formatOnSave": true`)
  - Trims trailing whitespace on save.
  - Configuration is enforced in [vexil.code-workspace](./vexil.code-workspace).
