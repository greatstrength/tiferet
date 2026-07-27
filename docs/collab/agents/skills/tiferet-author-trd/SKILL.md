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


## Operation-level artifact notation in §4

Every requirement in §4 is expressed as an **operation** on an **artifact type**: Add, Update, or Remove applied to a constant, function, method, section header, import, or file. The notation for each combination is standardized and must be **informationally complete** — an agent reading the table must be able to produce the artifact without consulting any other source, and a DSL compiler must be able to parse the same table as input to generate the code directly.

### "Add Constant" notation

The canonical notation for the **Add Constant** operation is a table, regardless of whether one constant or one hundred are being added. The operation, not the count, determines the form.

There are two primary expressions — use either, or combine both in sequence when a section mixes scalar IDs and factory-built objects:

**Expression 1 — scalar or literal value:**
```
| Artifact label | Constant | Value |
|---|---|---|
| `# ** constant: tiferet_events_path` | `TIFERET_EVENTS_PATH` | `'events'` |
| `# ** constant: tiferet_repos_path`  | `TIFERET_REPOS_PATH`  | `'repos'`  |
```

**Expression 2 — factory-built object:**
State the shared factory invocation pattern in a prefix sentence; table columns carry only the variable parameters. This keeps the table compact and keeps the factory name out of every row.
```
Each constant uses `create_service_registration(ID_CONST, create_service_module_path(TIFERET, <base>, <domain>), 'ClassName')`.

| Constant | ID Constant | base | domain | class_name |
|---|---|---|---|---|
| `ADD_FEATURE_EVT` | `ADD_FEATURE_EVT_ID` | `TIFERET_EVENTS_PATH` | `FEATURE_DOMAIN_PATH` | `'AddFeature'` |
```

**Combining both expressions** — when a code section contains scalar ID constants followed by factory-built object constants (the three-section catalog pattern), produce two tables in sequence under the same `####` heading. The second table references constant names from the first (not bare string values), making the dependency between sections explicit and verifiable.

**Supplementary notes** serve three purposes within an Add Constant block: ordering (which subsection must land before another), naming conventions that apply across all rows (state once rather than repeat per row), and invariants such as optional-field omission rules. Place them as a bold or italic note immediately before or after the table they govern.

### Informational completeness requirement

A table row must contain every parameter needed to produce the artifact:
- For scalar constants: the constant name and its exact value.
- For factory-built constants: all factory arguments, including which previously-defined constant is passed where. Reference prior constants by their constant name (e.g. `ROOT_LOGGER_ID`), not by their string value (`'root'`), so the dependency chain is derivable.
- For optional fields: if a field is conditionally included, the condition must be resolvable from the table alone (e.g. a column whose cell is blank when the field is omitted).

This completeness requirement means the same table can serve as the input to a code-generating agent, a test-generating agent, or a future declarative DSL compiler — the notation is the specification, not a summary of it.

### Section-mirroring in §4

Map each `# *** constants (<name>)` code section directly to a `####` sub-heading in §4, using the exact code section label as the heading text (e.g. `#### Add: # *** constants (ids)`). An implementation agent works section-by-section; the heading correspondence eliminates ambiguity about which part of the file each table governs.

### Constant section subgroups

When a module contains many constants of a given type, organize them into named `# *** constants (<subgroup>)` sections — not a flat `# *** constants` block. The subgroup label is semantic: it names what the group *represents*.

Canonical subgroup labels: `(ids)`, `(paths_packages)`, `(paths_domains)`, `(features)`, `(services)`, `(commands)`, `(formatters)`, `(handlers)`, `(loggers)`, `(groups)`, etc.

The section-mirroring rule extends to subgroup level: each `# *** constants (<subgroup>)` code section maps 1:1 to a `#### Add: # *** constants (<subgroup>)` heading in §4. A flat `# *** constants` block where subgroups apply is a defect — assert the correct section structure in §5.

### "Update Constant" and "Remove Constant"

- **Update**: use a delta table with columns for the current value and the target value (or target expression). Identify each constant by name in the first column. State unchanged fields only if they provide disambiguation context.
- **Remove**: a plain list of artifact labels is sufficient. Assert removal in §5.

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

**Semantic scoping principles (issues #935 and #939 are canonical references):**
- Super-TRDs are scoped around a **semantic concern** — a named domain problem — not around a file, layer label, or count of changes.
- Children are divided by **semantic ownership**: each child owns a bounded domain area that can be read and verified independently.
- Child TRD titles name the **actual artifacts delivered** (e.g. "Path Constants, Service Dependency Factory, and Module Path Factory"), not generic descriptions.
- Every §4 requirement names a specific artifact (section header, constant name, factory function, count).
- Every §5 AC line is a binary assertion on a named artifact — true or false given the code, no interpretation required.
- §6 NFR states artifact comment requirements per entry (`# ** constant: <snake_case_name>` per named constant, etc.).

**Child TRD size cap (hard constraint):**
A child TRD covers exactly **one primary module**, its test file (if applicable), and at most **1–2 non-testable dependency touches** (e.g. a factory in `core.py` the primary module uses, or an `__init__.py` export). Maximum size is **Medium (3 pts)**.

| Scope | Size |
|---|---|
| Single file only | XS (1 pt) |
| Primary module + tests | S (2 pts) |
| Primary module + tests + 1–2 dependency touches | M (3 pts) |

If a child would exceed M (3 pts), split it into additional children. The TRD author takes creative latitude in how work is divided — but the size cap is a hard constraint.

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
