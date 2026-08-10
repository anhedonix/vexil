# Contributing to VEXiL

Thanks for your interest in contributing to VEXiL! This document covers how to get set up, our workflow, and — importantly — our policy on AI-assisted development.

## Getting Started

For full environment setup (Devcontainer, manual setup, running the dev servers, Houdini plugin configuration), see the [README](./README.md#getting-started). In short:

```bash
bun run setup   # installs JS deps and syncs Python venvs via uv
bun run dev     # runs vexil-server, vexil-frontend, and vexil-website together
```

## Branching & Commits

- Branch off `dev` for new work; open PRs back into `dev`.
- Prefer [Conventional Commits](https://www.conventionalcommits.org/)-style messages where practical (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`) — this isn't strictly enforced today, but keeps history readable as the project grows.
- Keep commits focused; avoid bundling unrelated changes together.

## Pull Request Process

1. Open a PR against `dev` using the provided PR template.
2. Fill in the description, type of change, and how you tested it.
3. Complete the checklist, including the AI-assisted development attestation (see below).
4. A maintainer will review; expect feedback or requested changes before merge.
5. Once approved, a maintainer will merge — please don't merge your own PRs.

## Code Style

See the [README's "Linting, Formatting, & Code Style" section](./README.md#linting-formatting--code-style) for language-specific tooling (`ruff` for Python, workspace formatting defaults, etc.). Please run the relevant formatters/linters before opening a PR.

## AI-Assisted Development Policy

VEXiL welcomes the use of AI tools — chat assistants, autocomplete, code-generation agents, and similar — as part of your development workflow. What we don't accept is **"vibe-coded" contributions**: code submitted without the contributor understanding, reviewing, or testing it themselves.

### What's fine

- Using AI to scaffold boilerplate, explain unfamiliar APIs, suggest implementations, write tests, or help debug — as long as you read, understand, and verify the result before submitting.
- Iterating with an AI assistant on a design or implementation, then adapting it to fit the codebase's existing conventions.

### What's not accepted

- Submitting AI output wholesale without reading or testing it.
- PRs where the contributor can't explain *why* a change was made, or what a given piece of code does, when asked in review.
- Large, unfocused diffs that read like a raw AI dump rather than a deliberate change — inconsistent style, needless abstractions, dead code, or invented APIs/dependencies that don't actually exist in the project.

### Attestation

Every PR must check the box in the PR template confirming you've reviewed, understood, and tested everything you're submitting — regardless of how much AI assistance was involved in writing it.

### Review & Enforcement

Reviewers may ask you to explain any part of your PR. If a submission appears vibe-coded, a maintainer will first request changes or clarification and give you a chance to revise. A repeated pattern, ignoring feedback, or an especially egregious case (e.g., code that was clearly never run or tested) may result in the PR being closed outright.

## Code of Conduct

All contributors are expected to follow our [Code of Conduct](./CODE_OF_CONDUCT.md).
