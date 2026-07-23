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

## Super-TRDs and file naming

**When to use a super-TRD:** any story sized XL (8 pts) or above with a natural seam (by layer, concern, or parallelizability). If no seam exists, proceed as a single XL issue.

**Sizing session:** before creating GitHub issues for a milestone, size all TRDs using [project_fields.md](https://github.com/greatstrength/tiferet/blob/main/docs/collab/project_fields.md), identify XL/XXL candidates, split into super-TRDs, encode field values in filenames, then create issues.

**Super-TRD parent structure:**
- H1 prefix: `Super-TRD: <Story Title>`
- Header addition: `**Type:** Super-TRD | N child TRDs`
- §3 → "Child Stories" (table: TRD filename, Size, Est, Prereqs, sequencing note)
- §4 → "Story Sequencing" (ASCII dependency diagram)
- §5 → "Combined Acceptance Criteria" (union of all child ACs)
- §6–8: standard NFR, Prerequisites, Related Code Style Documentation

**Child TRD addition:** `**Parent:** \`<parent-filename>\` (Child N of M)` in the header.

**Child priority rule:** a child that is a prerequisite for sibling children → P0; all other children → parent's priority.

**Super-TRD closing:** parent issue closes when all child sub-issues close. Rename parent TRD file to `.complete.md` and close the parent GitHub issue.

**TRD file naming (save to `.trd/`):**
```
Draft (no issue):           <kebab-title>__<Size>_<Est>_<Priority>.md
Active (issue, milestone):  m<milestone>_<issue>_<kebab-title>[_N]__<Size>_<Est>_<Priority>.md
Active (issue, no m/s):     <issue>_<kebab-title>__<Size>_<Est>_<Priority>.md
Complete:                   [m<N>_]<issue>_<kebab-title>[_N]__<Size>_<Est>_<Priority>.complete.md
```

`m<N>_` and the issue number are acquired simultaneously — a TRD cannot be assigned to a milestone without an issue. `.complete.md` is the only explicit state marker.

## Creating GitHub issues

**`gh issue create --milestone` silently fails** for milestones with en-dashes. Use the REST API:
```bash
gh api repos/greatstrength/tiferet/issues \
  -f title="<Story title>" \
  -f body="$(cat .trd/<filename>.md)" \
  -F milestone=<integer-number> \
  --jq '{number, node_id, html_url}'
```

After creating the issue, rename the TRD file to insert the issue number and `m<N>_` prefix.

**Set project fields** via two-step GraphQL (`gh project item-add` does not return item ID):
```bash
ITEM_ID=$(gh api graphql -f query="mutation { addProjectV2ItemById(input: {projectId: \"PVT_kwDOCKXjws4A7Y85\", contentId: \"<node-id>\"}) { item { id } } }" --jq '.data.addProjectV2ItemById.item.id')
gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: { projectId: \"PVT_kwDOCKXjws4A7Y85\", itemId: \"$ITEM_ID\", fieldId: \"<field-id>\", value: {singleSelectOptionId: \"<option-id>\"} }) { projectV2Item { id } } }"
```
Set **Status=Ready** for all new issues. See [tech_requirements.md](https://github.com/greatstrength/tiferet/blob/main/docs/collab/tech_requirements.md) for stable project field IDs.

**Wire blocked-by** (requires `gh` v2.94.0+):
```bash
gh issue edit <blocked> --add-blocked-by <blocker> --repo greatstrength/tiferet
# Multiple blockers: --add-blocked-by 905,906,907
```

**Link super-TRD sub-issues:**
```bash
CHILD_ID=$(gh api repos/greatstrength/tiferet/issues/<child> --jq '.id')
gh api repos/greatstrength/tiferet/issues/<parent>/sub_issues -X POST -F sub_issue_id=$CHILD_ID
```
