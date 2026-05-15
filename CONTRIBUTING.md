# Contributing to Tiferet

Thank you for your interest in contributing to the Tiferet framework! This document outlines the process and expectations for contributing, whether you're fixing a bug, proposing a feature, or improving documentation.

## Getting Started

1. **Fork** the repository and clone your fork locally.
2. Create a new branch from the appropriate base branch (e.g., `v1.x-proto` or `v2.0-proto`).
3. Set up a virtual environment and install the package in development mode:
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

## Contribution Workflow

### 1. Open or Claim an Issue

All contributions should be tied to a GitHub issue. If one doesn't exist for the work you'd like to do, open an issue first to discuss the change with maintainers before starting.

### 2. Write a Technical Requirements Document (TRD)

For non-trivial changes (new features, refactors, architectural updates), a **Technical Requirements Document** is required before implementation begins. TRDs ensure clarity, alignment, and traceability across the project.

See the full TRD authoring guide:
**[docs/collab/tech_requirements.md](docs/collab/tech_requirements.md)**

Key points:
- Follow the standard structure (Overview, Scope, Components Affected, Detailed Requirements, Acceptance Criteria).
- Include code signatures and behavior descriptions where applicable.
- Reference the relevant [code style guides](docs/core/) for the components you're modifying.

### 3. Implement

- Follow the [Structured Code Style](docs/core/code_style.md) — artifact comments, spacing rules, RST docstrings, and snippet conventions are enforced across the codebase.
- Consult the component-specific guides in `docs/core/` for the layers you're working in:
  - [domain.md](docs/core/domain.md) — Domain objects
  - [events.md](docs/core/events.md) — Domain events
  - [mappers.md](docs/core/mappers.md) — Aggregates and transfer objects
  - [interfaces.md](docs/core/interfaces.md) — Service interfaces
  - [contexts.md](docs/core/contexts.md) — Application contexts
  - [repos.md](docs/core/repos.md) — Repositories
  - [utils.md](docs/core/utils.md) — Utilities
- Write tests using `pytest`.

### 4. Commit Hygiene

- Separate functional code changes from documentation, configuration, and packaging into distinct, atomic commits.
- Title commits by scope (e.g., `Events – AddFeature event`, `Docs/Packaging – update guides`).
- Include `Co-Authored-By: <name> <email>` in commit messages when collaborating with AI agents or other contributors.

### 5. Open a Pull Request

- Target the appropriate base branch.
- Reference the GitHub issue in the PR description.
- Ensure all tests pass and the code follows project conventions.
- Keep PRs focused — one logical change per PR.

### 6. Collaboration Report

Upon completion of a story or issue, a **Collaboration Report** is published as a comment on the originating GitHub issue. This report documents the implementation, deviations from the TRD, git state, and a log of key decisions made during development.

See the full report format guide:
**[docs/collab/collab_report.md](docs/collab/collab_report.md)**

## Prototype Release Process

Ecosystem extension packages (e.g., `tiferet-agents`, `tiferet-kb`, `tiferet-h5`) use a **prototype branch workflow** for early-stage alpha development before graduating to formal release branches.

### Branch Convention

- **Prototype branch**: `v0.x-proto` — the long-lived development branch for pre-1.0 packages.
- **Release branches**: `v0.1.0a1-release`, `v0.1.0a2-release`, etc. — created from the prototype branch for each alpha milestone.
- PRs from release branches target `v0.x-proto` and are **squash-merged** as a single alpha commit.

### Workflow

1. Create a release branch from the prototype branch: `git checkout -b v0.1.0a1-release v0.x-proto`
2. Implement the alpha milestone (all issues for that release).
3. Open a PR targeting `v0.x-proto` with the `proto-release` label.
4. Squash-merge the PR as a single commit representing the alpha release.
5. After merge, delete the release branch (local and remote).

### Labeling

- Use the **`proto-release`** label on all prototype alpha PRs to distinguish them from standard feature/bugfix work.

### Graduating to Formal Releases

Once a package reaches sufficient maturity (typically after beta), it transitions to the standard Tiferet release workflow:
- Release branches created from `main` (e.g., `v1.0.0-release`).
- Tagged releases published to PyPI.
- The `v0.x-proto` branch is archived or deleted.

## Code Style

Tiferet enforces a structured code style across all modules. The essentials:

- **Artifact comments** (`# ***`, `# **`, `# *`) organize code into predictable, machine-readable sections.
- **RST docstrings** with `:param`, `:type`, `:return`, `:rtype` on all public methods.
- **Commented code snippets** — each logical step is a separate snippet preceded by a descriptive comment.
- **Consistent spacing** — one empty line between sections, comments, and code blocks.

Full details: **[docs/core/code_style.md](docs/core/code_style.md)**

## Reporting Issues

When reporting bugs or requesting features:
- Use the GitHub issue tracker.
- Include a clear description, steps to reproduce (for bugs), and the expected vs. actual behavior.
- Reference relevant files, configurations, or error messages where applicable.

## License

By contributing to Tiferet, you agree that your contributions will be licensed under the [BSD 3-Clause License](LICENSE) that covers the project.
