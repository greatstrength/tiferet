# Doc — Documentation and Skills

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

The process index is [process.md](process.md). This file is the Doc strand.

## Purpose

Standalone documentation and agent-skill changes — collaboration docs, style guides, README, tutorials, committed `.agents/skills/` — that are not reconstruction and not a hotfix.

**No TRD is required.** No milestone or release is required. The pull request is the authorizing document. Its title and body must use this process's ubiquitous language (trunk, prototype, catalog, freeze, RFP, TRD, issue vs PR) so a later reader can see what changed without a specification.

An issue is optional. Open one only when discussion needs a home before the PR exists.

## Branch

From `main`: `docs-<lowercase-hyphenated-context>`.
Examples: `docs-process-collab-and-agents-skills`, `docs-contribution-streams`.

## Workflow

1. Create the branch from `main`.
2. Author the documentation or skill changes. Follow [agents/SKILL_TEMPLATE.md](agents/SKILL_TEMPLATE.md) for any new or rewritten skill.
3. Open a PR targeting `main`. Title: `Docs – <Capitalized Semantic Title>`.
4. Review comments that point at a diff stay on the PR. If an issue exists, session notes and any Collaboration Report go on the issue.
5. The user squash-merges. Pull `main` and delete the local branch.

## Guide-doc changes

When the change adds or updates a `docs/guides/**/*.md` entry, start from the matching genre template in [docs/guides/templates/](../guides/templates/). See **`tiferet-guide-docs`**.

## Distillation on proto vs Doc on trunk

Folding a settled RFP decision into the distillation **on the prototype branch** is prototype-strand work, not this stream. Reconstructing that distillation onto trunk happens after a catalog freeze, as a Doc PR or as part of the reconstruction milestone — still without inventing proto vocabulary on trunk that the freeze did not name.
