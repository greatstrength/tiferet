---
name: tiferet-author-trd
description: Author a Technical Requirements Document (TRD) for the Tiferet framework or any Tiferet-family repo. Use this whenever the user asks to write, draft, or format a TRD or technical requirements doc, or before implementing any non-trivial Tiferet change (new feature, refactor, architectural update) that should be specified first. Covers the exact section structure, the Version field by stream, mandatory code-style links, and branch conventions.
---

# Author a Tiferet TRD

## When to use
Use this when drafting a TRD for a Tiferet-family repo (canonical repo: `greatstrength/tiferet`). A TRD is required before implementation for non-trivial changes (features, refactors, architectural updates).

Canonical source of truth:
https://github.com/greatstrength/tiferet/blob/main/docs/collab/tech_requirements.md

## Required structure
Follow this exact structure (pure Markdown — headers, tables, code blocks):

```markdown
# Technical Requirements Document: [Story Title]

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** [Current Date]  
**Version:** [see Version field below]

## 1. Overview
[3-6 sentences: motivation, the change, key outcomes.]

## 2. Scope
### In Scope
- ...
### Out of Scope
- ...

## 3. Components Affected
| Component | File/Path | Changes |
|-----------|-----------|---------|
| ... | ... | ... |

## 4. Detailed Requirements
[Numbered subsections with signatures, behavior, validation, error cases, return values.]

## 5. Acceptance Criteria
1. Numbered, verifiable outcomes.

## 6. Non-Functional Requirements
- Consistency with patterns, backward compatibility, maintainability.

## 7. Prerequisites (optional)
| Dependency | Description |
|------------|-------------|

## 8. Related Code Style Documentation
- `tiferet-code-style` — required for every story.
- `tiferet-code-<component>` — include only for components this story modifies (domain, events, mappers, interfaces, contexts, repos, assets, blueprints, utils, di, testing). For multi-component stories, also include `tiferet-code-architecture`.
- **Fallback** (if skills not installed): link to `docs/core/<component>.md` directly.
```

## Key rules
- **Title:** the exact story title prefixed with its component group and an en-dash (e.g. `Domain – Naming Parity: ServiceRegistration and EventFeatureStep`).
- **Date:** the current calendar date (e.g. June 23, 2026) — never "today".
- **Version field — by stream:**
  - **Main stream:** the milestone version. For a no-version domain-scoped parity milestone, use the milestone's descriptive name, e.g. `Core DDD Parity I — Domain Infrastructure (tracking milestone)`.
  - **RFP stream:** `Request for Prototype`.
  - **Doc stream:** the latest released version.
- **Related Code Style Documentation** (section 8) is mandatory: always include `tiferet-code-style`; include a `tiferet-code-<component>` skill for each component the story modifies. For multi-component stories, also include `tiferet-code-architecture`. If skills are not installed, fall back to repo-relative paths — available guides: `docs/core/code_style.md`, `docs/core/domain.md`, `docs/core/events.md`, `docs/core/mappers.md`, `docs/core/interfaces.md`, `docs/core/contexts.md`, `docs/core/repos.md`, `docs/core/assets.md`, `docs/core/blueprints.md`, `docs/core/utils.md`, `docs/core/di.md`, `docs/core/testing.md`.

## Artifact-based requirements
Specify work as artifacts to **Add / Update / Remove** — modules, classes, `# * method:` / `# ** <component>:` labels / `# *** <section>` headers per the structured code style — not prose or "copy from X". In §3 give each module an artifact-action summary; in §4 enumerate the named artifacts, using a `From (current)` → `To (target)` delta table for renames/migrations with an Add/Update/Remove legend (factor the shared pattern once, list per-module exceptions). In §5 assert target artifacts exist and retired ones are gone. Make cross-layer prerequisites, artifact-label corrections, and behavioral shifts explicit.

## Migration / parity stories (branch-agnostic)
For parity/migration work sourced from a prototype branch, keep the dev-facing TRD **branch-agnostic and in the target ubiquitous language**. Do not tell the implementation agent to read, diff, or copy a prototype/source branch — extract the terminology and artifacts into the TRD. Record not-yet-met cross-layer dependencies in §7 Prerequisites with their status in `main`. The prototype source-of-truth comparison belongs to the separate `tiferet-pr-code-review` skill, not authoring or implementation.

## Branch naming (by stream)
- **Main:** `<issue-number>-<lowercase-hyphenated-title>`, from and targeting `main`.
- **RFP:** `v<major>.<minor>.<patch>b<next_beta>-<context>`, from and targeting the prototype branch (e.g. `v2.0-proto`).
- **Doc:** `docs-<lowercase-hyphenated-context>`, from and targeting `main`.

## Before finalizing
Verify: all sections present, tables well-formed, code blocks carry a language hint, acceptance criteria are verifiable, and no placeholder text remains. Keep it to ~1-3 pages.

The TRD also feeds the issue's project fields: Components Affected, Acceptance Criteria, and Prerequisites drive **Size**/**Estimate**, and the Prerequisites table drives **Priority** — see [project_fields.md](https://github.com/greatstrength/tiferet/blob/main/docs/collab/project_fields.md).
