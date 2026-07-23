---
name: tiferet-milestone-session
description: Run a Tiferet milestone implementation session — work a release/milestone's issues end-to-end on the Main stream. Use this whenever the user wants to start a milestone or release implementation session, references a release/version to implement, or asks to work through a milestone's issues one by one (feature branch → PR → merge → report → next). Covers the per-issue loop, project status transitions, milestone close, and release.
---

# Run a Tiferet Milestone Implementation Session

## When to use
Use this when implementing the issues of a Tiferet milestone/release on the **Main — Feature Release** stream (feature branches cut from `main`, PRs merged back into `main`).

Canonical sources of truth:
- https://github.com/greatstrength/tiferet/blob/main/docs/collab/main.md (Per-Issue Workflow, Closing the Milestone, and Release sections)
- https://github.com/greatstrength/tiferet/blob/main/docs/collab/project_fields.md (Status Workflow, Priority/Size/Estimate fields, Start/End dates)

## Project status states (project #2)
`Ready → In Progress → In Review → Done`. All new issues start at **Ready** — do not use Backlog. Blocked-by relationships communicate dependency ordering; Status does not reflect blocked state.

Set **Priority**, **Size**, and **Estimate** at issue creation; set the **Start date** when work begins (In Progress) and the **End date** when the issue is Done — see [project_fields.md](https://github.com/greatstrength/tiferet/blob/main/docs/collab/project_fields.md).

## Before starting: confirm issue setup

Before beginning implementation, verify that all issues in the milestone:
- Exist on GitHub with Status=Ready, Priority, Size, Estimate, and milestone set.
- Have blocked-by relationships wired (`gh issue edit <n> --add-blocked-by <blocker>`).
- Super-TRD children are linked to their parent via the sub_issues API.

If any issues still need to be created or wired, follow the GitHub Issue Creation workflow in [tech_requirements.md](https://github.com/greatstrength/tiferet/blob/main/docs/collab/tech_requirements.md) before starting the per-issue loop.

## Per-issue loop
For each issue in the milestone, in dependency-aware order:
1. **Create a feature branch** from `main`: `<issue-number>-<lowercase-hyphenated-title>`.
2. **Link** the branch to the issue, set the project status to **In Progress**, and set the **Start date**.
3. **Read code-style skills, then implement and test.** Before writing any code, read `tiferet-code-style` (mandatory every session) and the `tiferet-code-<component>` skill(s) for the layers this issue touches; for multi-component issues, also read `tiferet-code-architecture`. Then implement following the structured code style; write/port tests with `pytest`.
4. **Open a PR** targeting `main`, set status to **In Review**, and return the PR URL to the user.
5. **If PR comments arrive:** set status back to **In Progress**, address the feedback, re-push, then set back to **In Review**.
6. The **user squash-merges** the PR.
7. **Post a Collaboration Report** as a comment on the issue (use the `tiferet-collab-report` skill).
8. **Local cleanup:** check out `main`, pull latest, confirm the merge landed, delete the local feature branch.
9. **Mark Done:** set the project status to **Done**, set the **End date**, and close the issue. If the project has a `.trd/` folder containing a file matching `[m<N>_]<issue>_*.md`, rename it to `[m<N>_]<issue>_*.complete.md`. For child TRDs of a super-TRD parent: if all sibling children are now `.complete.md`, also rename the parent's TRD file and close the parent GitHub issue. Then repeat for the next issue.

## Guardrails
- Never commit or merge unless the user asks — branch/PR work is yours; merging is the user's.
- Confirm `git_head` matches the expected branch before starting each issue.
- Tie every change to its GitHub issue.
- Include a `Co-Authored-By: <name> <email>` line in commit messages when collaborating with an AI agent.

## Closing the milestone
Once all issues are merged, mark the milestone **closed**. A release tag and GitHub Release are created on `main` upon completion:
- **Tag:** `v<version>`. Note: the no-version domain-scoped parity milestones do not tag an incremental pre-release — confirm with the user whether a `v2.0.0`-line tag applies.
- **GitHub Release** title may add a semantic subtitle: `Tiferet v<version> – <Brief Title>`; the body follows the changelog format (highlights; what's changed grouped by area; breaking changes; upgrade notes; installation).

## Optional release-branch flow
For a multi-issue release the user may prefer a dedicated release branch (e.g. `v1.0a4-release`) from which feature branches are cut and into which PRs merge, rebased into `main` at the end. The documented default is to branch directly from `main`, so confirm the base-branch strategy with the user before starting.
