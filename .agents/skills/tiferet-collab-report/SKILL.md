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
- The QA Operator's review snapshot (`docs/collab/qa_operator.md`).

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
- Never commit unless asked. Never merge.
- Attribute yourself in your own name, never another agent's (`docs/collab/process.md` § Attribution). On a shared bot account, end every issue, PR, and comment with `— <agent>@<platform> via <account>` (§ Shared bot accounts). Never merge, tag, bump the version, mint a freeze, or create or close a milestone (§ Agent guardrails).
