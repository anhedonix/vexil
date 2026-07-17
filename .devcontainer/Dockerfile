FROM mcr.microsoft.com/devcontainers/base:bookworm

USER vscode

# uv manages Python installs and virtual envs
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/vscode/.local/bin:${PATH}"

# Python version used across the repo (pinned via .python-version in each project)
RUN uv python install 3.13

# Bun for all JS/TS tooling
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/home/vscode/.bun/bin:${PATH}"
