# Main — Feature Release Stream

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet

## Purpose

The Main stream is the primary contribution path for feature releases. Work is organized into milestones, each containing a set of issues that are implemented on feature branches cut from `main`, reviewed via pull requests, and merged back into `main`. Upon milestone completion, a release tag and GitHub Release are published.

## Milestones

### Naming

Milestone titles use the version number only — no semantic subtitle:

- Format: `v<version>`
- Examples: `v2.0.0b3`, `v1.9.0`, `v2.1.0`

### Description

The milestone description captures all semantic context:

- A brief summary of the release's goals.
- A list of linked issues, each prefixed with its component group, issue number, and a short description of intent.
- Optionally, a "What's Included" summary and a "Release" section with tag/PyPI links (added upon completion).

### Scope

- Minor releases typically contain **3–7 issues** per milestone.
- Major releases may use **domain-scoped milestones** (e.g., one milestone per architectural area).

### Project Assignment

Each issue and TRD in a milestone is assigned to the **Tiferet Framework** project (#2) on GitHub.

## Issue Conventions

### Title Format

Issue titles follow the pattern:

```
<Component Group> – <Brief Capitalized Title>
```

- The **Component Group** identifies the primary framework layer being modified: Assets, Blueprints, Contexts, DI, Domain, Events, Interfaces, Mappers, Repos, Utils, Docs, Tests, etc.
- The **title portion** (excluding the component group) should be **5–8 words**, using standard capitalization (not all caps).
- Use an en-dash (`–`) to separate the component group from the title.

**Examples:**
- `Domain – Feature Model Condition Evaluation Enhancements`
- `Events – Add Declarative Parameter Validation Decorator`
- `Utils – SQLite Client Connection Lifecycle`
- `Docs – Contribution Stream Guidelines`

## Project Status States

Issues in the Tiferet Framework project (#2) use the following status values:

- **Backlog** — Issue created but not yet scheduled.
- **Ready** — Issue is planned and ready to be picked up.
- **In Progress** — Active implementation underway.
- **In Review** — PR submitted; awaiting review.
- **Done** — Merged and verified.

## Per-Issue Workflow

For each issue in the milestone:

1. **Create feature branch** from `main`: `<issue-number>-<lowercase-hyphenated-title>`.
2. **Link** the branch to the GitHub issue and set the project status to **In Progress**.
3. **Implement** and test the changes.
4. **Submit PR** targeting `main`. Set the project status to **In Review**. Return the PR URL to the user.
5. **If PR comments are received:** set the status back to **In Progress**, address the feedback, re-push, then set the status back to **In Review**.
6. The user **squash-merges** the PR.
7. The agent **posts a Collaboration Report** as a comment on the issue.
8. **Local cleanup:** pull latest from `main` and delete the local feature branch.
9. **Repeat** for remaining issues in the milestone.

## Closing the Milestone

Once all issues in the milestone are complete and merged, mark the milestone as **closed**.

## Release Tagging and Publishing

A release tag and GitHub Release are created on `main` upon milestone completion.

### Tag

- Format: `v<version>` (e.g., `v2.0.0b3`, `v1.9.0`)
- Created on `main` after all milestone work is merged.

### GitHub Release

- **Title** may include a semantic subtitle separated by a dash:  
  `Tiferet v<version> – <Brief Title>` (e.g., `Tiferet v2.0.0b3 – Blueprints Pattern`).
- **Body** follows the established changelog format:
  - **Header block:** version, tag, released date, branch, repository link.
  - **Highlights:** 2–3 sentence summary of the release.
  - **What's Changed:** Grouped by component/domain area, each group listing issue links, class/function names, and behavioral changes.
  - **Breaking Changes** (if any).
  - **Upgrade Notes** (if any) — before/after code snippets.
  - **Installation** — pip install and source checkout commands.

See the [v2.0.0b3 release](https://github.com/greatstrength/tiferet/releases/tag/v2.0.0b3) as the canonical formatting example.
