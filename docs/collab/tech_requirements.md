# Instructions for Creating Technical Requirements Documents in the Tiferet Framework Project

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Purpose
These instructions ensure consistency, clarity, and completeness when drafting Technical Requirements Documents (TRDs) for stories, enhancements, refactors, and subtasks in the Tiferet project. TRDs serve as the primary specification for implementation and review.

## General Guidelines
- **Tone & Style**: Professional, precise, and concise. Use active voice where possible.
- **Formatting**: Pure Markdown with proper headers, tables, code blocks, and lists.
- **Date**: Use the current date (e.g., January 08, 2026).
- **Version**: Use the current milestone version (e.g., 1.7.0). Increment only when instructed.
- **Length**: Aim for completeness without unnecessary verbosity. Typical length: 1–3 pages when rendered.

## Standard Structure
Every TRD must follow this exact structure:

```markdown
# Technical Requirements Document: [Story Title]

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** [Current Date]  
**Version:** [Current Milestone, e.g., 1.7.0]

## 1. Overview
[High-level summary of the change, purpose, and key outcomes.]

## 2. Scope
### In Scope
- Bullet list of included work.
### Out of Scope
- Bullet list of excluded work.

## 3. Components Affected
| Component       | File/Path                          | Changes                                      |
|-----------------|------------------------------------|----------------------------------------------|
| ...             | ...                                | ...                                          |

## 4. Detailed Requirements
[Numbered subsections with code examples, signatures, behavior descriptions.]

## 5. Acceptance Criteria
1. Numbered list of verifiable outcomes.

## 6. Non-Functional Requirements
- Bullet list (performance, compatibility, style, etc.).

[Optional additional sections: Subtasks, Tests, Verification, etc.]
```

## Specific Rules
- **Title**: Use the exact story title prefixed with document type (e.g., "Commands – Feature: Add AddFeatureCommand Command").
- **Overview**: 3–6 sentences. Include motivation and primary benefits.
- **Scope**: Always include both "In Scope" and "Out of Scope" sections.
- **Components Table**: Use proper Markdown table syntax. Include all directly modified files.
- **Detailed Requirements**: 
  - Use numbered subsections.
  - Include code blocks with language hint and brief path comment when relevant.
  - Describe behavior clearly, including validation, error cases, and return values.
- **Acceptance Criteria**: Numbered, testable statements. Reference tests passing where appropriate.
- **Non-Functional**: Always include consistency with patterns, backward compatibility, and maintainability notes.
- **Subtasks**: For parent stories with subtasks, reference them or include separate linked documents.

## Common Patterns
- **Commands**: Include constructor, execute signature, validation, behavior, return value, and tests via `Command.handle`.
- **Model Methods**: Include signature, behavior, and model tests.
- **Refactors**: Highlight before/after, removed files, and migration steps.
- **New Errors**: Add to constants with ID, name, and message.

## Artifact-Based Requirements

TRDs specify work as **artifacts to add, update, or remove** — never as prose narratives or "copy from X" instructions. An *artifact* is any unit named by the structured code style's artifact comments: a module, class, attribute, `# * method:`, mid-level `# ** <component>:` label, or top-level `# *** <section>` (see [code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md)).

- **Components Affected (§3):** give each affected module an *artifact action* summary (Add / Update / Remove), not a vague "Changes" blurb.
- **Detailed Requirements (§4):** enumerate the specific artifacts per module. For renames, refactors, and migrations, use a delta table with `From (current)` and `To (target)` columns and lead with an **Add / Update / Remove** legend. Factor a shared pattern once and list per-module exceptions to keep the document lean.
- **Acceptance Criteria (§5):** assert that target artifacts exist *and* that retired ones are gone (e.g., "no `*YamlObject` references remain under `tiferet/repos/`").
- **Surface what a copy hides:** cross-layer prerequisites (e.g., a mapper role-key rename), artifact-label corrections, and behavioral shifts each become an explicit requirement or prerequisite — not an implicit side effect.

The goal: an implementation agent can satisfy the TRD by acting on named artifacts, and a reviewer can verify each one independently.

## Migration and Parity Stories (implementation-source-agnostic)

When a story moves work toward a prototype or other source branch (e.g., a parity milestone), the **dev-facing TRD must be branch-agnostic and written in the target ubiquitous language**. Extract the domain terminology and artifacts from the source and specify them directly.

- **Do not** instruct the implementation agent to read, diff, or copy from a prototype/source branch — the TRD is the single source the dev side operates from.
- Name target artifacts explicitly (classes, methods, parameters, mappers, roles, error codes) so no branch lookup is required.
- Record not-yet-satisfied cross-layer dependencies in **Prerequisites (§7)** with their current status in `main`.
- The prototype/source-of-truth branch is reserved for the **review/reconciliation** step, handled separately by the [`tiferet-pr-code-review`](agents/skills/tiferet-pr-code-review/SKILL.md) skill — not the authoring or implementation step.

## Super-TRD Format

A **super-TRD** is required when a story is sized XL (8 points) or above and has a natural decomposition seam (by layer, concern, or parallelizability). If no seam exists, proceed as a single XL issue with clear acceptance criteria.

**Sizing session:** Before creating GitHub issues for a milestone, run a sizing pass on all TRDs using the rubric in [project_fields.md](project_fields.md). Identify XL/XXL candidates and split them into super-TRDs. Encode field values in filenames before beginning issue creation.

### Super-TRD document structure

The super-TRD parent is both a local planning artifact and a GitHub issue (children are linked as GitHub sub-issues). Use the following structure:

- **H1 prefix:** `Super-TRD: <Story Title>`
- **Header addition:** `**Type:** Super-TRD | N child TRDs`
- **§3 — Child Stories:** replaces Components Affected — a table with TRD filename, Size, Estimate, Prerequisites, and sequencing note.
- **§4 — Story Sequencing:** replaces Detailed Requirements — an ASCII dependency diagram.
- **§5 — Combined Acceptance Criteria:** union of all child ACs.
- **§6–8:** standard Non-Functional Requirements, Prerequisites, Related Code Style Documentation.

### Child TRD structure

Each child TRD is a standard 8-section TRD with one header addition:

- `**Parent:** \`<parent-filename>\` (Child N of M)`

### Child priority rule

A child that is a prerequisite for one or more sibling children carries **P0**. All other children carry the parent story's priority.

### Super-TRD closing

The parent issue closes when all child sub-issues are closed. When the last child's issue is closed, also rename the parent's TRD file to `.complete.md` and close the parent GitHub issue.

## Review Checklist
Before finalizing:
- [ ] All sections present.
- [ ] Table formatted correctly.
- [ ] Code blocks have language hint.
- [ ] Acceptance criteria are verifiable.
- [ ] No placeholder text or unresolved comments.
- [ ] Requirements are expressed as artifacts to add/update/remove (not prose or "copy from X").
- [ ] For parity/migration stories, the TRD is branch-agnostic — no prototype/source-branch instructions for the implementation agent.

These instructions ensure all TRDs remain uniform, readable, and actionable across the Tiferet codebase. Follow them strictly for every new document.

## Related Code Style Documentation

Every TRD must include a **"Related Code Style Documentation"** section (§8) listing the code-style skills the implementation agent must read before starting work.

**Rule for inclusion:**
- `tiferet-code-style` — always required for every story.
- `tiferet-code-<component>` — include for each component the story modifies.
- `tiferet-code-architecture` — include for any story that modifies more than one component.
- **Fallback** (if skills not installed): link to `docs/core/<component>.md` directly.

Available skills and their fallback docs:
- **`tiferet-code-style`** / [code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — general structured code style (artifact comments, spacing, docstrings, snippets).
- **`tiferet-code-domain`** / [domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — domain object and aggregate conventions.
- **`tiferet-code-events`** / [events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — domain event patterns.
- **`tiferet-code-mappers`** / [mappers.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/mappers.md) — aggregate and transfer object conventions.
- **`tiferet-code-interfaces`** / [interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — service interface conventions.
- **`tiferet-code-contexts`** / [contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md) — context conventions.
- **`tiferet-code-repos`** / [repos.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/repos.md) — repository conventions.
- **`tiferet-code-assets`** / [assets.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/assets.md) — constants, exceptions, and bootstrap defaults.
- **`tiferet-code-blueprints`** / [blueprints.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/blueprints.md) — blueprint orchestration functions.
- **`tiferet-code-utils`** / [utils.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/utils.md) — infrastructure utility conventions.
- **`tiferet-code-di`** / [di.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/di.md) — dependency injection layer.
- **`tiferet-code-testing`** / [testing.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/testing.md) — test harness conventions.

## TRD File Lifecycle and Naming

All TRDs are stored locally in `.trd/` (git-ignored). Milestone description payloads are stored in `.milestones/` (git-ignored). Neither folder is committed to the repository.

### `.trd/` — flat file structure

All TRDs live in `.trd/` as a flat list. The filename encodes milestone, issue number, state, and project field values.

**Naming convention:**
```
[m<milestone>_]<issue>_<kebab-title>[_N]__<Size>_<Est>_<Priority>[.complete].md
```

- `m<milestone>_` — present when the issue is assigned to a milestone (e.g. `m30_`). Requires an issue number — never appears without one.
- `<issue>_` — GitHub issue number (e.g. `895_`). Presence signals the TRD is active.
- `<kebab-title>` — lowercase-hyphenated story title.
- `[_N]` — child number for super-TRD children (e.g. `_1`, `_2`); omitted for standalone TRDs and super-TRD parents.
- `__<Size>_<Est>_<Priority>` — project field suffix (e.g. `__L_5_P0`); omitted for unscoped RFP TRDs.
- `.complete` — appended when the issue is closed and work is done; the only explicit state marker.

**Lifecycle states (determined by filename structure):**

| State | Filename shape | Rule |
|-------|---------------|------|
| Draft | `<kebab-title>__<fields>.md` | No issue number |
| Active (no milestone) | `<issue>_<kebab-title>__<fields>.md` | Issue exists, no milestone |
| Active (with milestone) | `m<N>_<issue>_<kebab-title>__<fields>.md` | Issue + milestone acquired together |
| Complete | `[m<N>_]<issue>_<kebab-title>__<fields>.complete.md` | PR merged, issue closed |

**Invariants:**
- No issue number → draft. `m<N>_` always requires an issue number — both are added simultaneously when the GitHub issue is created and assigned to a milestone.
- `.complete.md` requires an issue number; milestone is optional.

**Transition: draft → active** — when the GitHub issue is created and assigned to a milestone:
```bash
mv .trd/assets-error-catalog-extraction__L_5_P0.md \
   .trd/m30_895_assets-error-catalog-extraction__L_5_P0.md
```

**Transition: active → complete** — when the PR is merged and the issue is closed:
```bash
mv .trd/m30_895_assets-error-catalog-extraction__L_5_P0.md \
   .trd/m30_895_assets-error-catalog-extraction__L_5_P0.complete.md
```

For **super-TRD parents**: when the last child issue closes, check if all sibling children are `.complete.md`; if so, also rename the parent and close the parent GitHub issue.

### `.milestones/` — milestone description payloads

`.milestones/` stores Markdown files used as `gh api` description payloads. The milestone number prefix is required:

```
m<milestone-number>_<kebab-milestone-title>.md
```

```bash
# Create milestone
gh api repos/greatstrength/tiferet/milestones \
  -f title='<Title>' \
  -F description=@.milestones/m<N>_<kebab-title>.md \
  --jq '{number, title, state, html_url}'

# PATCH to backfill issue numbers:
gh api repos/greatstrength/tiferet/milestones/<number> \
  -X PATCH \
  -F description=@.milestones/m<N>_<kebab-title>.md
```

## GitHub Issue Creation

### Creating an issue

The `--milestone` flag on `gh issue create` silently fails for milestones with en-dashes or when an integer is passed. Use the REST API directly:

```bash
gh api repos/greatstrength/tiferet/issues \
  -f title="<Story title>" \
  -f body="$(cat .trd/<filename>.md)" \
  -F milestone=<integer-number> \
  --jq '{number, node_id, html_url}'
```

`gh api` does not support `--json` output — use `--jq` with a projection. After creating the issue, rename the TRD file to insert the issue number and `m<N>_` prefix (see TRD File Lifecycle above).

### Setting project fields

Use the two-step GraphQL pattern — `gh project item-add` does not return the item ID in machine-readable form:

**Step 1 — Add to project:**
```bash
ITEM_ID=$(gh api graphql -f query="mutation {
  addProjectV2ItemById(input: {projectId: \"PVT_kwDOCKXjws4A7Y85\", contentId: \"<issue-node-id>\"}) {
    item { id }
  }
}" --jq '.data.addProjectV2ItemById.item.id')
```

**Step 2 — Set a field (repeat per field):**
```bash
gh api graphql -f query="mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: \"PVT_kwDOCKXjws4A7Y85\",
    itemId: \"$ITEM_ID\",
    fieldId: \"<field-node-id>\",
    value: {singleSelectOptionId: \"<option-id>\"}
  }) { projectV2Item { id } }
}"
```

**Tiferet Framework project (#2) stable IDs:**
- Project: `PVT_kwDOCKXjws4A7Y85`
- Status (`PVTSSF_lADOCKXjws4A7Y85zgvs_j4`): Ready=`08afe404`, In Progress=`47fc9ee4`, In Review=`4cc61d42`, Done=`98236657`
- Priority (`PVTSSF_lADOCKXjws4A7Y85zgvs_no`): P0=`79628723`, P1=`0a877460`, P2=`da944a9c`
- Size (`PVTSSF_lADOCKXjws4A7Y85zgvs_ns`): XS=`eff732af`, S=`9592a5a3`, M=`9728cbdc`, L=`c53df028`, XL=`7b141a16`
- Estimate (`PVTF_lADOCKXjws4A7Y85zgvs_nw`): number field — use `value: {number: N}`

Set **Status=Ready** for all new issues. Blocked-by relationships communicate dependency ordering — do not use Backlog for blocked issues.

### Wiring blocked-by dependencies

Requires `gh` v2.94.0+:
```bash
# Single blocker
gh issue edit <blocked-number> --add-blocked-by <blocker-number> --repo greatstrength/tiferet

# Multiple blockers (comma-separated)
gh issue edit <n> --add-blocked-by 905,906,907 --repo greatstrength/tiferet
```

REST fallback (gh < v2.94.0):
```bash
BLOCKER_ID=$(gh api repos/greatstrength/tiferet/issues/<N> --jq '.id')
gh api repos/greatstrength/tiferet/issues/<blocked>/dependencies/blocked_by \
  -X POST -f issue_id=$BLOCKER_ID
```

### Linking super-TRD sub-issues

After creating parent and child issues, link each child as a GitHub sub-issue:
```bash
CHILD_ID=$(gh api repos/greatstrength/tiferet/issues/<child-number> --jq '.id')
gh api repos/greatstrength/tiferet/issues/<parent-number>/sub_issues \
  -X POST -F sub_issue_id=$CHILD_ID
```

`sub_issue_id` uses the integer `id` field (not the display number).

## Branch Naming and Workflow Conventions

Branch naming and workflow differ by **contribution stream**. TRD authors and AI agents must follow the conventions for the applicable stream. See [docs/collab/](.) for the full stream guides.

### Stream-Specific Branch Naming

**Main stream** (feature releases):
- Feature branches are named after their GitHub issue: `<issue-number>-<lowercase-hyphenated-title>`.
- Created from and targeting `main`.
- Examples:
  - Issue #574 "Utils – JsonLoader Utility" → `574-utils-jsonloader-utility`
  - Issue #568 "Interfaces – File, Configuration, and SQLite Service Contracts" → `568-interfaces-file-configuration-and-sqlite-service-contracts`
- See [main.md](main.md) for the full workflow.

**RFP stream** (prototype work):
- Prototype worktree branches: `v<major>.<minor>.<patch>b<next_beta>-<context>` (e.g., `v2.0.0b6-dicontext-varargs`).
- Created from and targeting the main prototype branch (e.g., `v2.0-proto`).
- TRD **Version** field is set to `Request for Prototype`.
- See [rfp.md](rfp.md) for branch conventions, versioning/tagging rules, and workflows.

**Doc stream** (documentation updates):
- Documentation branches: `docs-<lowercase-hyphenated-context>` (e.g., `docs-contribution-streams`).
- Created from and targeting `main`.
- See [doc.md](doc.md) for the full workflow.

### AI Agent Checkout Conventions
When an AI agent begins work on a TRD:
1. Confirm the current branch matches the expected branch for the applicable stream (check `git_head` in environment context).
2. If the branch does not exist yet, create it from the appropriate base branch (`main` for Main/Doc streams, `v<major>.<minor>-proto` for RFP stream).
3. After PR merge, check out the base branch, pull changes, confirm the merge landed, and delete the local feature/docs branch.

### Acceptance Criteria (branch-related)
When a TRD includes branch/PR work, Acceptance Criteria should reference:
- Branch name follows the naming convention for its stream.
- PR targets the correct base branch (`main` or the prototype branch).
- Branch deleted after merge.

## Process Conventions (for TRD authors and executors)

- Commit hygiene: separate functional code changes from documentation/config/packaging in distinct, atomic commits. Title commits by scope (e.g., "Interfaces – base class" vs "Docs/Packaging").
- Versioning & tagging (when the story includes a release): specify the target version, branch, and bump type. Acceptance Criteria should include: (1) version bump commit, (2) annotated tag pushed, (3) published release with notes following the previous release style.
- Source-of-truth references: keep dev/implementation TRDs **branch-agnostic** — do not embed "retrofit from <branch>" instructions for the implementation agent. Extract the needed terminology and artifacts into the TRD itself (see *Migration and Parity Stories* above). Branch/path/SHA references to a prototype source of truth belong to the review/reconciliation step (the [`tiferet-pr-code-review`](agents/skills/tiferet-pr-code-review/SKILL.md) skill), not authoring or implementation.
- Reporting: upon completion, publish a Collaboration Report as a comment on the originating issue; include links to the PR, tag, and release.
- Tooling fallback: if first-choice automation (e.g., MCP tools) is unavailable, specify the approved fallback (e.g., `gh` CLI) and prerequisites (authenticated session).
- Cross-branch research: a TRD author may inspect a source branch via `git show <branch>:<path>` while drafting, but the finished TRD must stand alone — inline the extracted terminology/artifacts so the implementation agent never needs the branch.
