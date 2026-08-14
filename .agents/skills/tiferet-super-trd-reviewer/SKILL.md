---
name: tiferet-super-trd-reviewer
description: >
  Combined Super-TRD review after every child has an implementation log.
  Primary criterion is each child TRD's Acceptance Criteria. Diff findings
  go on the PR; narrative and conversation link go on the parent issue.
---

# Super-TRD — Reviewer

## When to use

- `tiferet-super-trd` identified REVIEWER: every child is In Review with an implementation log; no Reviewer comments posted yet.

## When not to use

- Children still being implemented.
- Closing / addenda — closer skill.
- Using this as "make trunk match proto."

## Canonical source

- `docs/collab/super_trd_workflow.md`
- `docs/collab/code_review.md`
- `docs/collab/process.md`

## Inputs

PR number, child TRDs, freeze id (reconstruction). Binding for proto branch name if measuring.

## Procedure

**Trunk**

1. `gh pr view` for files and head SHA.
2. For each child §5: named artifact, binary pass/fail. Subgroup labels and counts count.
3. Optional proto glance: AC-named artifacts only. Ahead = keep. Behind + AC fail = finding.
4. Show findings to the human; wait.
5. Post **diff** findings as one PR review (`path` + `position`). Review body: findings + Co-Authored-By. Conversation link and narrative on the **parent issue**. Child AC failures also on that **child issue**.
6. Intentional AC drift: update `.trd/` + issue body, record "Reviewer AC Updates" on the parent issue, do not leave the old AC as an open finding.

Do not close children. Do not close the parent.

## Outputs

- PR review (diff only).
- Parent-issue narrative. Child-issue AC-failure notes.

## Guardrails

- Never proto → trunk git. Never "make trunk match proto."
- Never merge.
