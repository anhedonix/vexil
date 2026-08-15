# env-init

Streamlit UI that scaffolds VEXiL local environment files from `vexil.toml`.

## Run

From the repository root (after deps are installed):

```bash
bun run env-init
```

`bun run setup` installs Python/Go deps and then launches this Streamlit app in the foreground on port `6644`.

Or from this directory:

```bash
uv sync
uv run streamlit run main.py --server.port 6644
# or
uv run env-init
```

## Patch version bump

Increment product patch (`0.1.2` → `0.1.3`) across the monorepo:

```bash
bun run bump-version
# dry-run
uv run python -m env_init.bump_cli --dry-run
```

Or use **Bump patch version** in the Streamlit Base section (once per UI session).

## Features

- Edit and persist `vexil.toml` (`[vexil-io]`, frontend, website, docs, package)
- Auto-generate a long random salt on load
- Generate local `.env` files for each app (tracked `.env.template` files are not rewritten)
- In-app folder browser for project/data roots under `/.scratch`
- Initialize Go / Bun / uv workspaces
- Install Houdini 22+ `packages/vexil.json`
- Bump product patch version across package manifests
- Reset Dev Env (delete `.env` + clear `/.scratch`)
