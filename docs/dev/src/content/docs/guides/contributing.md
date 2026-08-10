---
title: Contributing
description: Branching, pull requests, commit style, and AI-assisted development policy for VEXiL.
---

Thanks for contributing to VEXiL. This page is the contributor workflow you should follow. Environment setup is covered in [Getting Started](/guides/getting-started/).

## Branching & commits

- Branch off **`dev`** for new work; open pull requests **back into `dev`**.
- Prefer [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, …). Not strictly enforced today, but keeps history readable.
- Keep commits focused; avoid bundling unrelated changes.

## Pull request process

1. Open a PR against `dev` using the repository PR template.
2. Fill in the description, type of change, and how you tested it.
3. Complete the checklist, including the AI-assisted development attestation.
4. A maintainer will review; expect feedback or requested changes before merge.
5. Once approved, a **maintainer merges** — do not merge your own PRs.

## Code style

- **Python**: `ruff` (config in each package’s `pyproject.toml`).
- **JS / TS / Astro**: workspace / editor formatters; format on save is enabled in `vexil.code-workspace`.
- **Go**: follow standard Go formatting (`gofmt` / editor Go tooling).
- Workspace defaults: 2-space indent, trim trailing whitespace, format on save.

Run the relevant formatters and linters for the packages you touch before opening a PR.

## AI-assisted development policy

AI tools (chat, autocomplete, agents) are welcome. What we do **not** accept is **vibe-coded** contributions — code submitted without the contributor understanding, reviewing, or testing it.

### Fine

- Scaffolding, explaining APIs, suggesting implementations, writing tests, or debugging — when you read, understand, and verify the result.
- Iterating with an assistant, then adapting the result to this codebase’s conventions.

### Not accepted

- Submitting AI output wholesale without reading or testing it.
- PRs you cannot explain in review.
- Large, unfocused diffs that look like raw dumps (inconsistent style, dead code, invented APIs).

### Attestation

Every PR must check the template box confirming you reviewed, understood, and tested what you submit — regardless of how much AI help you used.

Reviewers may ask you to explain any part of the change. Repeated vibe-coded submissions may be closed.

## Code of Conduct

All contributors are expected to follow the [Code of Conduct](https://github.com/anhedonix/vexil/blob/dev/CODE_OF_CONDUCT.md) in the repository root.
