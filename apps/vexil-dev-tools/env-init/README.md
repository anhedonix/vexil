# env-init

Streamlit UI that scaffolds VEXiL local environment files from `vexil.toml`.

## Run

```bash
uv sync
uv run streamlit run main.py --server.port 6644
# or
uv run env-init
```

## Features

- Edit and persist `vexil.toml` (`[vexil-io]`, frontend, website, docs, package)
- Auto-generate a long random salt on load
- Generate `.env` / `.env.template` for each app
- Initialize Go / Bun / uv workspaces
- Install Houdini 22+ `packages/vexil.json`
- Reset Dev Env (delete `.env` + clear `/.scratch`)
