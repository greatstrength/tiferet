# Contributing to Tiferet

Thank you for your interest in contributing to the Tiferet framework! This document outlines the process and expectations for contributing, whether you're fixing a bug, proposing a feature, or improving documentation.

## Getting Started

1. **Fork** the repository and clone your fork locally.
2. Create a new branch from the appropriate base branch (see Contribution Streams below).
3. Set up a virtual environment and install the package in development mode:
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

## Contribution Workflow Streams

Tiferet uses three distinct contribution workflow streams, each with its own branching, versioning, and review process:

- **[RFP — Request for Prototype](docs/collab/rfp.md)**: Exploratory and architectural work developed on prototype branches with alpha/beta versioning. Used for significant refactors and new architectural ideas.
- **[Main — Feature Release](docs/collab/main.md)**: The primary path for feature releases. Work is organized into milestones, implemented on feature branches from `main`, and merged via pull requests.
- **[Doc — Documentation Updates](docs/collab/doc.md)**: Standalone documentation changes merged directly into `main` via pull requests. No milestones or releases involved.

Each stream guide covers branch naming, workflow steps, and versioning conventions in detail.

For a reference of git and `gh` CLI commands used across all streams, see **[docs/collab/commands.md](docs/collab/commands.md)**.

## Common Workflow Steps

Regardless of stream, all contributions share the following practices.

### Open or Claim an Issue

All contributions should be tied to a GitHub issue (except internal RFPs and standalone doc changes). If one doesn't exist for the work you'd like to do, open an issue first to discuss the change with maintainers before starting.

### Write a Technical Requirements Document (TRD)

For non-trivial changes (new features, refactors, architectural updates), a **Technical Requirements Document** is required before implementation begins. TRDs ensure clarity, alignment, and traceability across the project.

See the full TRD authoring guide:
**[docs/collab/tech_requirements.md](docs/collab/tech_requirements.md)**

Key points:
- Follow the standard structure (Overview, Scope, Components Affected, Detailed Requirements, Acceptance Criteria).
- Include code signatures and behavior descriptions where applicable.
- Reference the relevant [code style guides](docs/core/) for the components you're modifying.
- Set the **Version** field according to the applicable stream (milestone version for Main, "Request for Prototype" for RFP, latest released version for Doc).

### Implement

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

### Commit Hygiene

- Separate functional code changes from documentation, configuration, and packaging into distinct, atomic commits.
- Title commits by scope (e.g., `Events – AddFeature Event`, `Docs/Packaging – Update Guides`).
- Include `Co-Authored-By: <name> <email>` in commit messages when collaborating with AI agents or other contributors.

### Open a Pull Request

- Target the appropriate base branch for the stream (`main` for Main/Doc, prototype branch for RFP).
- Reference the GitHub issue in the PR description.
- Ensure all tests pass and the code follows project conventions.
- Keep PRs focused — one logical change per PR.
- After submitting, provide the PR URL to the user.

### Collaboration Report

Upon completion of a story or issue, a **Collaboration Report** is published as a comment on the originating GitHub issue. This report documents the implementation, deviations from the TRD, git state, and a log of key decisions made during development.

See the full report format guide:
**[docs/collab/collab_report.md](docs/collab/collab_report.md)**

## Working with AI Agents

Warp/AI agents contributing to Tiferet follow the same conventions described above and in the [`docs/collab/`](docs/collab/) stream guides. The most common workflows are also packaged as reusable agent **skills** so they're applied consistently across all Tiferet-family repositories:

- **`tiferet-create-milestone`** — create or format a GitHub milestone (title and description conventions).
- **`tiferet-author-trd`** — author a TRD in the standard structure ([tech_requirements.md](docs/collab/tech_requirements.md)).
- **`tiferet-collab-report`** — generate a Collaboration Report once an issue is confirmed complete ([collab_report.md](docs/collab/collab_report.md)).
- **`tiferet-milestone-session`** — run a milestone's per-issue branch → PR → merge → report loop ([main.md](docs/collab/main.md)).

A ready-to-apply **global agent rule** is preserved at [docs/collab/agent_rule.md](docs/collab/agent_rule.md) — copy it into your agent's global/user rules to apply these standards across every Tiferet repo.

These skills and any AI rules treat `docs/collab/` and the [code style guides](docs/core/) as the **single source of truth** — they reference these documents rather than copying them, so the docs stay authoritative. The skills' canonical copies live in [docs/collab/agents/skills/](docs/collab/agents/skills/); follow that folder's README to copy them into `~/.agents/skills/` (global) or a repo's `.agents/skills/` (project) so your agent auto-discovers them.

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
