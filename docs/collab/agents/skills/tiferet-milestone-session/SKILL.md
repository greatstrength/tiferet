---
name: tiferet-milestone-session
description: Run a Tiferet milestone implementation session — work a release/milestone's issues end-to-end on the Main stream. Use this whenever the user wants to start a milestone or release implementation session, references a release/version to implement, or asks to work through a milestone's issues one by one (feature branch → PR → merge → report → next). Covers the per-issue loop, project status transitions, milestone close, and release.
---

# Run a Tiferet Milestone Implementation Session

## When to use
Use this when implementing the issues of a Tiferet milestone/release on the **Main — Feature Release** stream (feature branches cut from `main`, PRs merged back into `main`).

Canonical source of truth:
https://github.com/greatstrength/tiferet/blob/main/docs/collab/main.md (Per-Issue Workflow, Closing the Milestone, and Release sections)

## Project status states (project #2)
`Backlog → Ready → In Progress → In Review → Done`. Move each issue's status as it progresses.

## Per-issue loop
For each issue in the milestone, in dependency-aware order:
1. **Create a feature branch** from `main`: `<issue-number>-<lowercase-hyphenated-title>`.
2. **Link** the branch to the issue and set the project status to **In Progress**.
3. **Implement and test** following the structured code style; write/port tests with `pytest`.
4. **Open a PR** targeting `main`, set status to **In Review**, and return the PR URL to the user.
5. **If PR comments arrive:** set status back to **In Progress**, address the feedback, re-push, then set back to **In Review**.
6. The **user squash-merges** the PR.
7. **Post a Collaboration Report** as a comment on the issue (use the `tiferet-collab-report` skill).
8. **Local cleanup:** check out `main`, pull latest, confirm the merge landed, delete the local feature branch.
9. **Close the issue**, then repeat for the next one.

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
