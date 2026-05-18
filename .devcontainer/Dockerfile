FROM mcr.microsoft.com/devcontainers/base:bookworm

USER vscode

# uv manages Python installs and virtual envs
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/vscode/.local/bin:${PATH}"

# Pre-fetch both Python versions used in the repo
RUN uv python install 3.14 3.11

# Bun for all JS/TS tooling
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/home/vscode/.bun/bin:${PATH}"
