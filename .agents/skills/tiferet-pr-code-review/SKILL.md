---
name: tiferet-pr-code-review
description: >
  Point a review at the Takwin QA Operator. Not a Tiferet implementation
  role, and not the orchestrator. The orchestrator does not review, does
  not post the verdict, and does not squash-merge. The operator does that
  work. Judge by docs/collab/code_review.md. Squash-merge only as
  docs/collab/qa_operator.md allows.
---

# Review as the Takwin QA Operator

## When to use

- The user asks to review a PR, or a round dispatches a reviewer for one PR.
- Prototype: the PR targets proto and is linked to an RFP issue.
- Release: the PR targets `main` and is linked to a standalone TRD or a Super-TRD parent, or the PR targets a Super-TRD branch and is one child's sub-TRD PR.
- Doc: a docs or skills PR to `main`. It has no issue. Do not flag that absence.

## When not to use

- Implementing or fixing the PR. The author does that.
- Authoring an RFP or a TRD.
- A Collaboration Report, or posting the snapshot as one.
- Reviewing a second child of the same Super-TRD. Re-review only the PR you already reviewed.
- Promoting proto onto trunk.
- You are the orchestrator. Stop. Do not review, do not post the verdict, and do not squash-merge. Summarize what the operator returns. When the human approves a squash merge, tell the operator who already holds that pull request.

## Canonical source

- `docs/collab/qa_operator.md`
- `docs/collab/code_review.md`
- `docs/collab/process.md`
- `docs/collab/binding.md`

Do not duplicate the standard here. Point, then do only the operator steps.

## Inputs

PR number. Lens (Prototype | Release | Doc), taken from the PR base and its authorizing document. Prototype: the RFP issue and its cited distillation sections. Release: the TRD (§3, §4, §5) and the reference prototype from its §7 row, or `None`. A sub-TRD review is that child only. The final Super-TRD review is the parent TRD and the child set. Binding for the proto branch name.

## Procedure

1. If you are the orchestrator, stop. You do not review, you do not post the verdict, and you do not squash-merge. That is not optional. Summarize what the operator returns. When the human approves a squash merge, tell the operator who already holds that pull request. Then summarize the result. Do not reopen an already-merged pull request to redo this.
2. You are the Takwin QA Operator, not a forward implementer and not the orchestrator. Read `docs/collab/qa_operator.md` and `docs/collab/code_review.md` before you judge.
3. Apply the matching lens. Style floor first, then acceptance criteria, then Prototype or Release as that page already writes them. Verify each acceptance criterion. The reviewer checks the PR-body box of each verified item and leaves a failing one unchecked. The author opened the PR with every box unchecked. Do not replace the standard. Do not waive a style or ordering finding.
4. Return the 350-400 word snapshot to the orchestrator. Name a future inquiry when the review found one. Do not invent the new work. You post the verdict. The orchestrator does not.
5. When the orchestrator tells you the human approved the squash merge for the pull request you already hold, post the verdict, squash-merge, and close the authorizing issue by hand. Otherwise do not squash-merge. A clean verdict is not that approval. Do not reopen an already-merged pull request. The rule is for the next one.

## Outputs

- A 350-400 word snapshot, returned to the orchestrator. Not a PR comment. Not a Collaboration Report. The orchestrator summarizes it. The orchestrator does not post the verdict.
- One posted review on the **PR**, verdict line first.
- A short status on the authorizing issue. A Doc PR has no issue; the posted review is the status.
- A squash-merge only when `docs/collab/qa_operator.md` allows it.

## Guardrails

- Never merge to `main` unless the human explicitly relinquished that specific PR.
- Never squash-merge unless the human said that issue or PR is approved for squash merge.
- Never tag, bump the version, mint a freeze, or create or close a milestone (`docs/collab/process.md` § Agent guardrails).
- Never use `Closes`, `Fixes`, or `Resolves` on a proto PR, including the squash message. Never use them on a sub-TRD PR.
- Never lower a style or ordering finding.
- Never proto → trunk git. Never send an implementer to proto. On a Release review, only this role reads proto, and only as `docs/collab/code_review.md` allows.
- Never review a second child of the same Super-TRD.
- Never commit as part of a review.
- The orchestrator never reviews, never posts the verdict, and never squash-merges. The operator who holds the pull request does. Not optional.
- Never reopen an already-merged pull request to redo this. The rule is for the next one.
- Attribute yourself in your own name (`docs/collab/process.md` § Attribution). On a shared bot account, end the review with `- <agent>@<platform> via <account>`.
