# Contributing to Tiferet

Thank you for your interest in contributing to the Tiferet framework.

## Getting Started

1. **Fork** the repository and clone your fork locally.
2. Create a branch from the correct base (see streams below).
3. Set up a virtual environment and install in development mode:
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

## How work is authorized

Read **[docs/collab/process.md](docs/collab/process.md)** first. Trunk and prototype are two independent histories of one version family. What crosses from prototype to trunk is a **catalog** of named artifacts, never a git merge.

| You want to… | You submit | Lands on | Guide |
|---|---|---|---|
| Test a domain theory | an **RFP** (public contributors welcome if it follows the genre) | proto branch | [rfp.md](docs/collab/rfp.md) |
| Reconstruct a frozen catalog, or hotfix a mechanical defect | a **TRD** | `main` | [main.md](docs/collab/main.md), [tech_requirements.md](docs/collab/tech_requirements.md) |
| Change docs or agent skills | a **Doc PR** — no TRD | `main` | [doc.md](docs/collab/doc.md) |

Commands used across streams: **[docs/collab/commands.md](docs/collab/commands.md)**. Repo-local ids: **[docs/collab/binding.md](docs/collab/binding.md)**.

## Common practices

### Issues

Prototype work always has an RFP issue. Trunk reconstruction and hotfixes have a TRD issue. Doc/skills PRs may skip an issue.

### Specifications

- Prototype: RFP genre in [rfp.md](docs/collab/rfp.md). No TRD.
- Trunk reconstruction: TRD that cites a **freeze id**. Branch-agnostic. Never "copy from proto."
- Trunk hotfix: TRD marked hotfix. No freeze.
- Docs/skills: the PR body, in this process's vocabulary.

### Implement

- Read **`tiferet-code-style`** before writing code. If the skill is missing, use [docs/core/code_style.md](docs/core/code_style.md).
- Read the **`tiferet-code-<component>`** skill for each layer you touch. Multi-component: also `tiferet-code-architecture`.
- Docstrings / `docs/guides/`: **`tiferet-guide-docs`**.
- Tests: `pytest`.

### Commit hygiene

- Separate functional changes from docs/config/packaging.
- Title by scope (`Events – AddFeature Event`, `Docs – Process and Skills`).
- `Co-Authored-By: <name> <email>` when an AI agent collaborates.
- Never commit or merge unless asked.

### Pull requests

- Target proto for RFPs, `main` for trunk and Doc.
- The PR is a **review surface** (description, AC checkboxes, diff comments).
- Session notes, conversation links, and Collaboration Reports go on the **issue**.

### Review

Diff comments stay on the PR. Reconstruction review may measure proto only for artifacts named in the frozen catalog / TRD AC — never "make trunk match proto." Prototype review is against the RFP and cited distillation sections. See [code_review.md](docs/collab/code_review.md).

### Collaboration Report

Posted on the originating **issue**. Super-TRD children get an implementation log when pushed and a verification addendum after combined review. See [collab_report.md](docs/collab/collab_report.md).

## Working with AI Agents

Skills are committed at [`.agents/skills/`](.agents/skills/) and auto-discovered in this repo. Copying them to `~/.agents/skills/` is optional. Every skill follows [docs/collab/agents/SKILL_TEMPLATE.md](docs/collab/agents/SKILL_TEMPLATE.md). Drop stale `~/.agents/skills/tiferet-*` copies or they will shadow this repo.

**Process skills**

- `tiferet-annotation-artifacts` — scan `# ++ todo:` / `# -- obsolete:` at the start of every implementation session.
- `tiferet-author-rfp` — draft or amend an RFP.
- `tiferet-rfp-session` — implement an RFP on proto.
- `tiferet-freeze-catalog` — record a catalog freeze after a human names the cluster.
- `tiferet-author-trd` — trunk TRD (reconstruction needs a freeze id; hotfix does not).
- `tiferet-create-milestone` — proto beta milestone or trunk `vX.Y.Z`.
- `tiferet-milestone-session` — proto-alpha loop or trunk standalone / Super-TRD.
- `tiferet-collab-report` — report on the issue (log / addendum / roll-up).
- `tiferet-pr-code-review` — diff comments on the PR; AC/freeze measurement, not proto promotion.

**Super-TRD:** `tiferet-super-trd` (dispatch) → implementor / reviewer / closer. [super_trd_workflow.md](docs/collab/super_trd_workflow.md).

**Docs:** `tiferet-guide-docs`.

**Code style:** `tiferet-code-style` every session; `tiferet-code-architecture` for multi-component; then `tiferet-code-domain`, `events`, `mappers`, `interfaces`, `contexts`, `repos`, `assets`, `blueprints`, `utils`, `di`, `testing`.

Global rule template: [docs/collab/agent_rule.md](docs/collab/agent_rule.md).

## Code Style

Artifact comments (`# ***`, `# **`, `# *`), RST docstrings, commented snippets, consistent spacing. Full details: [docs/core/code_style.md](docs/core/code_style.md).

## Reporting Issues

Use the GitHub issue tracker. Bugs: steps to reproduce, expected vs actual. RFPs: follow [rfp.md](docs/collab/rfp.md).

## License

Contributions are licensed under the [BSD 3-Clause License](LICENSE).
