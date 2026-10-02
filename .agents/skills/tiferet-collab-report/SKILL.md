---
name: tiferet-collab-report
description: >
  Write a Collaboration Report for a standalone trunk TRD on the GitHub
  issue (never as a PR comment). Not for RFP issues or Super-TRD children.
---

# Collaboration Report (standalone TRD)

## When to use

- A standalone trunk TRD is done / merged and needs a closeout report on its issue.

## When not to use

- RFP / proto work.
- Super-TRD child issues.
- PR review comments.

## Canonical source

- `docs/collab/collab_report.md`
- `docs/collab/process.md`

## Inputs

Issue number. TRD path. PR url. Freeze id if reconstruction.

## Procedure

1. Confirm this is a **standalone** TRD issue.
2. Draft the report in the shape in collab_report.md (summary, components, deviations, git, chronological Human/Agent log with timestamps).
3. Post it on the **issue**, not the PR.
4. Set Status Done and End date if the human asked you to close the loop.

## Outputs

Collaboration Report comment on the issue.

## Guardrails

- Never post as a PR conversation comment.
- Never commit or merge unless asked.
