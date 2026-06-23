---
name: tiferet-create-milestone
description: Create or format a GitHub milestone for the Tiferet framework or any Tiferet-family repo (greatstrength/tiferet, tiferet-*, Tiferet.*). Use this whenever the user wants to set up, create, or format a milestone, group TRD issues into a milestone, or kick off a new release or parity effort for Tiferet — even if they don't say the word "milestone" outright (e.g. "track this work on GitHub", "organize these issues for the next release"). Covers the title convention, description format, and the gh API command.
---

# Create a Tiferet GitHub Milestone

## When to use
Use this when creating or formatting a GitHub milestone in a Tiferet-family repository (canonical repo: `greatstrength/tiferet`). It encodes the Main-stream milestone conventions so a new milestone matches the repo's established style.

Milestones are part of the **Main — Feature Release** stream. The canonical source of truth — read it for full detail or if the conventions may have changed:
https://github.com/greatstrength/tiferet/blob/main/docs/collab/main.md (Milestones section)

## Title convention
Milestone titles **normally** use the version number only — no semantic subtitle:
- Format: `v<version>` (examples: `v2.0.0b3`, `v1.9.0`, `v2.1.0`).

**Exception — domain-scoped v2 milestones:** the current v2 parity milestones track an architectural area of the `v2.0.0` line rather than a single incremental alpha/beta pre-release. These use a **descriptive title with no version**:
- Format: `<Descriptive Title>` (no version prefix).
- Example: `Core DDD Parity I – Domain Infrastructure (Domain, Mappers, Interfaces, Utils)`.
- If a version is needed at all, use `v2.0.0` only — never an alpha (`aN`) or beta (`bN`) suffix.

Use an en-dash (`–`) where a title joins a label and its detail.

## Description format
The description carries all the semantic context. Structure it as (this mirrors milestone `v2.0.0a3 — Mappers Package`):
1. A brief **overview paragraph**: the release/effort goal plus any tracking or dependency note.
2. A **list of linked issues**, one per line, each formatted as `Area (#issue): short intent / artifacts`. Use the component group as the Area (Domain, Mappers, Interfaces, Utils, Events, Repos, Docs, Tests, …).
3. Optionally (added on completion) a "What's Included" summary and a "Release" section with tag/PyPI links.

If the issues don't exist yet, use `#TBD` placeholders and backfill the real numbers once the TRD issues are created.

**Example (milestone #28, a domain-scoped parity milestone):**

Title: `Core DDD Parity I – Domain Infrastructure (Domain, Mappers, Interfaces, Utils)`

Description:
```
Establish v2.0-proto parity for Tiferet's core domain infrastructure in `main`: domain
objects, mappers, service interfaces, and utilities. Delivers naming parity, the
MiddlewareService contract, request-validation and logging-settings value objects, and
the TOML loader, plus relocated tests and documentation. Tracking-only; Milestone 2
(Events and Repos) depends on the contracts delivered here.

TRD issues:
- Domain Naming (#TBD): ServiceRegistration, EventFeatureStep, domain exports
- Mapper Naming (#TBD): *ConfigObject transfer objects, registration aggregates
- Interfaces (#TBD): MiddlewareService, DIService registration-method rename
- ...
```

## Scope guidance
- Minor releases: typically 3–7 issues per milestone.
- Major releases: domain-scoped milestones (one per architectural area) are appropriate — that is exactly the descriptive-title case above.

## Project assignment
Each issue/TRD in a milestone is assigned to the **Tiferet Framework** project (#2) on GitHub.

## How to create it
Milestone management is **`gh` CLI only** (no MCP equivalent). Write the description to a file first so backticks and multi-line content survive shell escaping, then read it with `-F field=@file`:

```bash
# 1. Write the description to a temp file (preserves backticks / newlines), e.g. /tmp/milestone_desc.md

# 2. Create the milestone
gh api repos/greatstrength/tiferet/milestones \
  -f title='<Title>' \
  -F description=@/tmp/milestone_desc.md \
  --jq '{number, title, state, html_url}'
```

For another Tiferet-family repo, swap `greatstrength/tiferet` accordingly.

## After creating
Report the milestone number and URL. If you used `#TBD` placeholders, remind the user to backfill issue numbers once the TRD issues exist (PATCH the milestone description). Related workflows: author TRDs with the `tiferet-author-trd` skill; work the milestone with `tiferet-milestone-session`.
