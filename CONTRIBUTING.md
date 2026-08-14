# Contributing to Tiferet

Thank you for wanting to contribute. This page is the front door. The map of how work actually moves is [docs/collab/process.md](docs/collab/process.md) — read that before you invent a branch name.

## Getting started

1. Fork the repository and clone your fork.
2. Cut a branch from the right base (proto for an RFP, `main` for trunk or docs).
3. Set up a virtual environment and install in development mode:

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -e .
```

## How work is authorized

Trunk and prototype are two independent histories of the same version family. What crosses from prototype to trunk is a **catalog** of named artifacts, never a git merge.

| You want to… | You submit | It lands on | The guide |
|---|---|---|---|
| Test a domain theory | an **RFP** (public contributors welcome if it follows the genre) | the proto branch | [rfp.md](docs/collab/rfp.md) |
| Rebuild a frozen catalog, or hotfix a mechanical defect | a **TRD** | `main` | [main.md](docs/collab/main.md), [tech_requirements.md](docs/collab/tech_requirements.md) |
| Change docs or agent skills | a **Doc PR** — no TRD | `main` | [doc.md](docs/collab/doc.md) |

Commands used across all of that: [docs/collab/commands.md](docs/collab/commands.md). Facts that belong only to this repo: [docs/collab/binding.md](docs/collab/binding.md).

## Common practices

### Issues

An RFP always has an issue. A reconstruction or hotfix always has a TRD issue. A Doc/skills PR may skip the issue if there is nothing to discuss first.

### Specifications

- Prototype: the RFP genre in [rfp.md](docs/collab/rfp.md). No TRD.
- Trunk reconstruction: a TRD that cites a **freeze id**. Written in the target language. Never "copy from proto."
- Trunk hotfix: a TRD marked hotfix. No freeze.
- Docs and skills: the PR body, using the words in process.md.

### Implement

- Read **`tiferet-code-style`** before you write code. If the skill is missing, [docs/core/code_style.md](docs/core/code_style.md) is the fallback.
- Read the **`tiferet-code-<component>`** skill for each layer you touch. More than one layer: also `tiferet-code-architecture`.
- Docstrings and `docs/guides/`: **`tiferet-guide-docs`**.
- Tests: `pytest`.

### Commit hygiene

Keep functional changes out of the same commit as docs, config, or packaging. Title by scope — `Events – AddFeature Event`, `Docs – Process and Skills`. When an AI agent collaborated, add `Co-Authored-By: <name> <email>`. Never commit or merge unless someone asked you to.

### Pull requests

RFPs target proto. Trunk and Doc target `main`. The PR is a **review surface**: what changed, AC checkboxes, comments that point at a line. Session notes, conversation links, and Collaboration Reports belong on the **issue**.

### Review

Diff comments stay on the PR. Reconstruction review may look at proto only for artifacts the freeze and the TRD named — never "make trunk match proto." Prototype review is against the RFP and the distillation sections it cites. More in [code_review.md](docs/collab/code_review.md).

### Collaboration Report

Posted on the originating **issue**. A Super-TRD child gets an implementation log when the code is pushed, and a verification addendum after combined review. See [collab_report.md](docs/collab/collab_report.md).

## Working with AI agents

Skills live at [`.agents/skills/`](.agents/skills/) and are auto-discovered in this checkout. Copying them to `~/.agents/skills/` is optional. If you do, delete stale `tiferet-*` copies first or they will shadow this repo. Every skill follows [docs/collab/agents/SKILL_TEMPLATE.md](docs/collab/agents/SKILL_TEMPLATE.md).

**Process**

- `tiferet-annotation-artifacts` — scan `# ++ todo:` / `# -- obsolete:` at the start of every implementation session.
- `tiferet-author-rfp` — draft or amend an RFP.
- `tiferet-rfp-session` — implement an RFP on proto.
- `tiferet-freeze-catalog` — record a catalog freeze after a human names the cluster.
- `tiferet-author-trd` — trunk TRD (reconstruction needs a freeze id; a hotfix does not).
- `tiferet-create-milestone` — proto beta milestone or trunk `vX.Y.Z`.
- `tiferet-milestone-session` — proto-alpha loop, or trunk standalone / Super-TRD.
- `tiferet-collab-report` — the report on the issue (log, addendum, or roll-up).
- `tiferet-pr-code-review` — diff comments on the PR; measurement, not proto promotion.

**Super-TRD:** start with `tiferet-super-trd`, then the implementor, reviewer, or closer skill. The long form is [super_trd_workflow.md](docs/collab/super_trd_workflow.md).

**Docs:** `tiferet-guide-docs`.

**Code style:** `tiferet-code-style` every session; `tiferet-code-architecture` when more than one component changes; then `tiferet-code-domain`, `events`, `mappers`, `interfaces`, `contexts`, `repos`, `assets`, `blueprints`, `utils`, `di`, `testing`.

A global rule you can paste into your agent: [docs/collab/agent_rule.md](docs/collab/agent_rule.md).

## Code style

Artifact comments (`# ***`, `# **`, `# *`), RST docstrings, commented snippets, consistent spacing. The full guide is [docs/core/code_style.md](docs/core/code_style.md).

## Reporting issues

Use the GitHub issue tracker. Bugs need steps to reproduce and expected versus actual. RFPs need to follow [rfp.md](docs/collab/rfp.md).

## License

Contributions are licensed under the [BSD 3-Clause License](LICENSE).
