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

## Review Checklist
Before finalizing:
- [ ] All sections present.
- [ ] Table formatted correctly.
- [ ] Code blocks have language hint.
- [ ] Acceptance criteria are verifiable.
- [ ] No placeholder text or unresolved comments.

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

All work in the Tiferet project follows a standard GitHub branching workflow. TRD authors and AI agents must follow these conventions.

### Branch Naming
- Feature branches are named after their GitHub issue: `<issue-number>-<lowercase-hyphenated-title>`.
- Spaces and special characters are replaced with a single hyphen (`-`). All letters are lowercase.
- Examples:
  - Issue #574 "Utils – JsonLoader Utility" → `574-utils-jsonloader-utility`
  - Issue #568 "Interfaces – File, Configuration, and SQLite Service Contracts" → `568-interfaces-file-configuration-and-sqlite-service-contracts`

### Branch Workflow
- **Feature branches** are created from and target `main`.
- PRs are opened against the release branch, not `main`.
- Upon completion of all release work, the **release branch is rebased into `main`**.
- After merge, the feature branch is deleted (both remote and local).

### AI Agent Checkout Conventions
When an AI agent begins work on a TRD:
1. Confirm the current branch matches the expected feature branch (check `git_head` in environment context).
2. If the feature branch does not exist yet, create it from the release branch: `git checkout -b <feature-branch> <release-branch>`.
3. After PR merge, check out the release branch, pull changes, confirm the merge landed, and delete the local feature branch.
4. Do **not** check out or push directly to `main`.

### Acceptance Criteria (branch-related)
When a TRD includes branch/PR work, Acceptance Criteria should reference:
- Feature branch name follows the naming convention.
- PR targets the correct release branch.
- Feature branch deleted after merge.

## Process Conventions (for TRD authors and executors)

- Commit hygiene: separate functional code changes from documentation/config/packaging in distinct, atomic commits. Title commits by scope (e.g., "Interfaces – base class" vs "Docs/Packaging").
- Versioning & tagging (when the story includes a release): specify the target version, branch, and bump type. Acceptance Criteria should include: (1) version bump commit, (2) annotated tag pushed, (3) published release with notes following the previous release style.
- Source-of-truth references: when instructing to "retrofit from …", include the exact branch and path (and optionally the commit SHA) that contains the source document.
- Reporting: upon completion, publish a Collaboration Report as a comment on the originating issue; include links to the PR, tag, and release.
- Tooling fallback: if first-choice automation (e.g., MCP tools) is unavailable, specify the approved fallback (e.g., `gh` CLI) and prerequisites (authenticated session).
- Cross-branch artifacts: if the referenced source does not exist locally on the working branch, it is acceptable to retrieve it via `git show <branch>:<path>` or include the minimal excerpts inline within the TRD.