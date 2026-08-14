# Technical Requirements Documents

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

The process index is [process.md](process.md). A TRD is a **trunk** specification. Prototype work uses an [RFP](rfp.md), not this genre. Doc and skills changes use a [Doc PR](doc.md) — **no TRD**.

## When a TRD is required

- **Reconstruction** — implement a **frozen** RFP cluster on trunk. Cite the freeze id in §7. Refuse to author if there is no freeze id.
- **Hotfix** — a small mechanical defect already understood on trunk. No freeze. Prototype is not consulted. Header: `**Type:** Hotfix`.

Do not write a TRD that says "copy from proto" or `Version: Request for Prototype`.

## Kinds, then size, then path

1. Kind: reconstruction (needs freeze id) or hotfix (does not).
2. Size: [project_fields.md](project_fields.md).
3. Path:
   - **Standalone** — XL or below, or XL with no seam. One issue, one branch, one PR. Session record on that issue.
   - **Super-TRD** — XL+ *and* a seam. Parent + children. Workflow: [super_trd_workflow.md](super_trd_workflow.md) and [main.md](main.md).

## General guidelines

- Tone: professional, precise, active voice.
- Pure Markdown. Date is a real calendar date, never "today."
- **Version:** the trunk milestone (`2.0.1`, `2.1.0`). Not an RFP label.
- Typical rendered length: 1–3 pages for a standalone or child TRD.

## Standard structure (standalone and child)

```markdown
# Technical Requirements Document: [Story Title]

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet
**Date:** [Current Date]
**Version:** [Trunk milestone, e.g., 2.0.1]
**Type:** Reconstruction | Hotfix     # omit Type on ordinary reconstruction if the freeze id in §7 is enough

## 1. Overview
[3–6 sentences: motivation, the change, key outcomes.]

## 2. Scope
### In Scope
- ...
### Out of Scope
- ...

## 3. Components Affected
| Component | File/Path | Artifact action |
|-----------|-----------|-----------------|
| ... | ... | Add / Update / Remove — one-line summary |

## 4. Detailed Requirements
[Numbered subsections. Named artifacts. Informationally complete tables.]

## 5. Acceptance Criteria
1. Binary, named-artifact assertions.

## 6. Non-Functional Requirements
- Pattern consistency, compatibility, maintainability.

## 7. Prerequisites
| Dependency | Status |
|------------|--------|
| Freeze `TIF2-FREEZE-001` (reconstruction only) | Frozen |
| ... | ... |

## 8. Related Code Style Documentation
- `tiferet-code-style` — always.
- `tiferet-code-<component>` — each layer this story modifies.
- `tiferet-code-architecture` — more than one component.
```

## Specific rules

- **Title:** exact story title with component group and en-dash (`Domain – Naming Parity: ServiceRegistration`).
- **§3:** artifact action per module, not a vague "Changes" blurb.
- **§4:** Add / Update / Remove on named artifacts. Delta tables for renames (`From (current)` / `To (target)`).
- **§5:** target artifacts exist *and* retired ones are gone.
- **§7 reconstruction:** freeze id is mandatory. Also list not-yet-satisfied trunk dependencies.
- **§7 hotfix:** no freeze row. Name the defect and why proto was not consulted.
- **§8:** always `tiferet-code-style`; component skills as touched. Fallback: `docs/core/<component>.md`.

## Artifact-based requirements

TRDs specify **artifacts to add, update, or remove** — never prose narratives or "copy from X." An artifact is any unit named by the structured code style: module, class, attribute, `# * method:`, `# ** <component>:`, `# *** <section>` (see [code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md)).

An implementor satisfies the TRD by acting on named artifacts. A reviewer verifies each one independently. The implementor must not be sent to the proto branch.

## Operation-level artifact notation in §4

Every §4 requirement is an **operation** (Add / Update / Remove) on an artifact type. Tables must be **informationally complete** — a row is enough to produce the artifact with no other source.

### Add Constant

The operation, not the count, determines the form. Always a table.

**Expression 1 — scalar or literal:**

```
| Artifact label | Constant | Value |
|---|---|---|
| `# ** constant: tiferet_events_path` | `TIFERET_EVENTS_PATH` | `'events'` |
```

**Expression 2 — factory-built object:**

State the shared factory once; table columns are the variable parameters.

```
Each constant uses `create_service_registration(ID_CONST, create_service_module_path(TIFERET, <base>, <domain>), 'ClassName')`.

| Constant | ID Constant | base | domain | class_name |
|---|---|---|---|---|
| `ADD_FEATURE_EVT` | `ADD_FEATURE_EVT_ID` | `TIFERET_EVENTS_PATH` | `FEATURE_DOMAIN_PATH` | `'AddFeature'` |
```

When a section mixes scalar ids and factory objects, produce two tables under the same `####` heading. The second table references constant *names* from the first.

Supplementary notes (ordering, naming conventions, optional-field rules) sit immediately before or after the table they govern.

### Informational completeness

- Scalar: name and exact value.
- Factory-built: every argument, prior constants by name (`ROOT_LOGGER_ID`), never by raw string (`'root'`).
- Optional fields: the omit condition is resolvable from the table (blank cell = omitted).

### Section-mirroring

Each `# *** constants (<subgroup>)` code section maps 1:1 to `#### Add/Update/Remove: # *** constants (<subgroup>)` in §4. Canonical subgroups: `(ids)`, `(paths_packages)`, `(paths_domains)`, `(features)`, `(services)`, `(commands)`, `(formatters)`, `(handlers)`, `(loggers)`, `(groups)`. A flat `# *** constants` block where subgroups apply is a defect — assert the structure in §5.

### Update Constant and Remove Constant

- **Update:** delta table, current vs target. Unchanged fields only for disambiguation.
- **Remove:** list of artifact labels. Assert removal in §5.

## Reconstruction stories (branch-agnostic)

The TRD is written in the **target ubiquitous language** extracted from the freeze note / amended RFP, not from a live proto checkout.

- Do not tell the implementor to read, diff, or copy proto.
- Name classes, methods, parameters, mappers, roles, error codes.
- Proto comparison, if any, is optional review measurement of AC-named artifacts ([code_review.md](code_review.md)) — not authoring or implementation.

## Super-TRD format

Required when size is XL (8) or above **and** a seam exists. If no seam, stay standalone XL.

**Sizing session:** before creating issues, size every TRD ([project_fields.md](project_fields.md)), split XL/XXL candidates, encode fields in filenames, then create issues.

### Parent

- H1: `Super-TRD: <Story Title>`
- Header: `**Type:** Super-TRD | N child TRDs`
- §3 Child Stories (filename, Size, Est, Prereqs, sequencing) — replaces Components Affected
- §4 Story Sequencing (ASCII dependency diagram)
- §5 Combined Acceptance Criteria (union of child ACs)
- §6–8: NFR, Prerequisites (freeze id on reconstruction parents), Related Code Style Documentation

### Child

Standard 8-section TRD plus `**Parent:** \`<parent-filename>\` (Child N of M)`.

A child that unblocks siblings is **P0**. Other children inherit the parent's priority.

### Child size cap

One primary module, its tests, and at most 1–2 non-testable dependency touches. Maximum **Medium (3)**.

| Scope | Size |
|---|---|
| Single file only | XS (1) |
| Primary module + tests | S (2) |
| Primary module + tests + 1–2 dependency touches | M (3) |

Exceeds M → split. Reference scoping: issues #935 and #939.

### Closing

Children close after the verification addendum (or explicit Reviewer AC acceptance), not when the implementation log is posted. The parent closes when the PR squash-merges via `Closes #<parent>` (verify before closing manually). Rename the parent `.trd/` file to `.complete.md` after the parent Collaboration Report.

## Review checklist (author)

- [ ] All sections present; tables well-formed; code blocks have a language hint.
- [ ] Acceptance criteria are binary and name artifacts.
- [ ] No placeholders.
- [ ] Requirements are Add / Update / Remove, not "copy from X."
- [ ] Reconstruction cites a freeze id in §7; hotfix does not.
- [ ] Path chosen: standalone vs Super-TRD.

## Related code style documentation (§8)

Always `tiferet-code-style`. Add `tiferet-code-<component>` for each touched layer. Add `tiferet-code-architecture` when more than one component changes. Add `tiferet-guide-docs` when AC requires a `docs/guides/` entry, a vision-tier docstring, or a `# >> see:` annotation.

Fallback guides: `docs/core/code_style.md`, `domain.md`, `events.md`, `mappers.md`, `interfaces.md`, `contexts.md`, `repos.md`, `assets.md`, `blueprints.md`, `utils.md`, `di.md`, `testing.md`.

## File lifecycle (`.trd/`)

`.trd/` and `.milestones/` are gitignored. Filenames encode milestone, issue, and fields:

```
[m<milestone>_]<issue>_<kebab-title>[_N]__<Size>_<Est>_<Priority>[.complete].md
```

| State | Filename |
|---|---|
| Draft | `<kebab-title>__<fields>.md` |
| Active, no milestone | `<issue>_<kebab-title>__<fields>.md` |
| Active, with milestone | `m<N>_<issue>_<kebab-title>__<fields>.md` |
| Complete | `[m<N>_]<issue>_<kebab-title>__<fields>.complete.md` |

`m<N>_` and the issue number are acquired together. `.complete.md` requires an issue number.

Use `git mv` when the file is tracked; otherwise `mv` (`.trd/` is ignored).

Milestone description payloads live in `.milestones/m<N>_<kebab-title>.md`. Create and patch milestones with the recipes in [commands.md](commands.md). Project field ids live in [binding.md](binding.md).

## Creating GitHub issues

Impact-check merged PRs **and** in-flight feature branches before creating issues from TRDs. For Super-TRD child 2, "current state" is the feature branch after child 1, not `main`.

Use the REST API (`gh api`), not `gh issue create --milestone` (silently fails on en-dashes). After create, rename the TRD file to insert `m<N>_` and the issue number. Set Status=Ready. Wire blocked-by and Super-TRD sub-issues with the commands in [commands.md](commands.md).

## Branch naming (trunk)

`<issue-number>-<lowercase-hyphenated-title>`, from and targeting `main`. Super-TRD: `<parent-issue>-<slug>`. Prototype branches are specified in [rfp.md](rfp.md), not here.
