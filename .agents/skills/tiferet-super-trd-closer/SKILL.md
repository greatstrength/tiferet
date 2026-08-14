---
name: tiferet-super-trd-closer
description: >
  After Super-TRD combined review: fix PR diff comments, wait for merge,
  post verification addenda on each child issue, then the parent roll-up
  Collaboration Report on the parent issue.
---

# Super-TRD — Closer

## When to use

- `tiferet-super-trd` identified CLOSER.

## When not to use

- Combined review has not been posted — reviewer skill.
- Children still in implementation.

## Canonical source

- `docs/collab/super_trd_workflow.md`
- `docs/collab/collab_report.md`

## Inputs

PR number, parent issue, child issues. Conversation links from **issue** threads.

## Procedure

**Trunk**

1. Read unresolved **PR** review comments. Fix in code. Push.
2. Non-trivial fix: session note on the **parent issue** (conversation link). Not on the PR.
3. Wait for the human to squash-merge.
4. `git checkout main && git pull && git branch -d <branch>`
5. Each **child issue**: verification addendum (pass / amended AC / follow-up). Then close the child, Status Done, rename `.trd/` to `.complete.md` (`mv` if ignored).
6. **Parent issue**: roll-up Collaboration Report linking child logs + addenda. Read those issue threads first.
7. Rename parent `.trd/` to `.complete.md`. Verify `Closes #<parent>` closed the parent; close manually only if needed.

## Outputs

- Code push addressing review.
- Child addenda + parent roll-up on **issues**.

## Guardrails

- Implementation log was not Done; the addendum is.
- Never proto → trunk git. Never merge unless asked.
