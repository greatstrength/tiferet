---
name: tiferet-pr-code-review
description: >
  Point a review at the Takwin QA Operator. Not a Tiferet implementation
  role. The operator performs the review, returns a 350–400 word snapshot,
  and posts a verdict. Judge by docs/collab/code_review.md. Squash-merge
  only as docs/collab/qa_operator.md allows. Forward skills do not review
  or merge.
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

## Canonical source

- `docs/collab/qa_operator.md`
- `docs/collab/code_review.md`
- `docs/collab/process.md`
- `docs/collab/binding.md`

Do not duplicate the standard here. Point, then do only the operator steps.

## Inputs

PR number. Lens (Prototype | Release | Doc), taken from the PR base and its authorizing document. Prototype: the RFP issue and its cited distillation sections. Release: the TRD (§3, §4, §5) and the reference prototype from its §7 row, or `None`. A sub-TRD review is that child only. The final Super-TRD review is the parent TRD and the child set. Binding for the proto branch name.

## Procedure

1. You are the Takwin QA Operator, not a forward implementer. Read `docs/collab/qa_operator.md` and `docs/collab/code_review.md` before you judge.
2. Apply the matching lens. Style floor first, then acceptance criteria, then Prototype or Release as that page already writes them. Do not replace the standard. Do not waive a style or ordering finding.
3. Return the 350–400 word snapshot to the human. Then post one review whose first line is exactly `Verdict: Approve` or `Verdict: Changes requested`. Show the findings and wait for a go-ahead before posting. That wait is not a merge approval.
4. Squash-merge only when `docs/collab/qa_operator.md` allows it. Otherwise stop. A clean verdict is not approval to merge.

## Outputs

- A 350–400 word snapshot, returned to the human. Not a PR comment. Not a Collaboration Report.
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
- Attribute yourself in your own name (`docs/collab/process.md` § Attribution). On a shared bot account, end the review with `- <agent>@<platform> via <account>`.
