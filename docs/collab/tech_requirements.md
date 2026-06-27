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

Every TRD must include a **"Related Code Style Documentation"** section at the end. This section provides targeted links to component-specific style guides based on the primary artifacts being modified in the story.

**Rule for inclusion:**
- Always include the general `code_style.md`.
- Include a component-specific guide **only if the story directly adds, modifies, or refactors code in that component type**.
- Do not include unrelated guides to avoid clutter.

Current available guides (located in `docs/core/` on the `main` branch):
- **[code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md)** – General structured code style (artifact comments, spacing, docstrings, snippets).
- **[domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md)** – Domain model and aggregate conventions.
- **[events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md)** – Domain event patterns and usage.
- **[mappers.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/mappers.md)** – Data mapping, DTOs, and transformation conventions.
- **[contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md)** – Context-specific conventions (injection patterns, lifecycle methods, execution flow).
- **[interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md)** – Interface / contract / service conventions.

Additional component-specific style guides will be added as the framework evolves. Always consult the relevant documents when implementing or extending components.

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
