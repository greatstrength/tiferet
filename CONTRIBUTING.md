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
**[docs/guides/tech_requirements.md](docs/guides/tech_requirements.md)**

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
- Write tests using `pytest`. Follow existing test structure (`# *** fixtures`, `# *** tests`).

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
**[docs/guides/collab_report.md](docs/guides/collab_report.md)**

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
