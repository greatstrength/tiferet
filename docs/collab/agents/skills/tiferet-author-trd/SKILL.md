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
- Always link code_style.md; add component guides only for components actually touched.
```

## Key rules
- **Title:** the exact story title prefixed with its component group and an en-dash (e.g. `Domain – Naming Parity: ServiceRegistration and EventFeatureStep`).
- **Date:** the current calendar date (e.g. June 23, 2026) — never "today".
- **Version field — by stream:**
  - **Main stream:** the milestone version. For a no-version domain-scoped parity milestone, use the milestone's descriptive name, e.g. `Core DDD Parity I — Domain Infrastructure (tracking milestone)`.
  - **RFP stream:** `Request for Prototype`.
  - **Doc stream:** the latest released version.
- **Related Code Style Documentation** (section 8) is mandatory: always include `code_style.md`; include a component guide only when the story modifies that component. Link to `https://github.com/greatstrength/tiferet/blob/main/docs/core/<file>` — available guides: `code_style.md`, `domain.md`, `events.md`, `mappers.md`, `interfaces.md`, `contexts.md`, `repos.md`, `utils.md`.

## Branch naming (by stream)
- **Main:** `<issue-number>-<lowercase-hyphenated-title>`, from and targeting `main`.
- **RFP:** `v<major>.<minor>.<patch>b<next_beta>-<context>`, from and targeting the prototype branch (e.g. `v2.0-proto`).
- **Doc:** `docs-<lowercase-hyphenated-context>`, from and targeting `main`.

## Before finalizing
Verify: all sections present, tables well-formed, code blocks carry a language hint, acceptance criteria are verifiable, and no placeholder text remains. Keep it to ~1-3 pages.

The TRD also feeds the issue's project fields: Components Affected, Acceptance Criteria, and Prerequisites drive **Size**/**Estimate**, and the Prerequisites table drives **Priority** — see [project_fields.md](https://github.com/greatstrength/tiferet/blob/main/docs/collab/project_fields.md).
