# QA Operator

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

[process.md](process.md) is the index. This page is a **Takwin role**. It is not a Tiferet implementation role, and it is not a second review standard.

Forward development stays forward: authoring an RFP, implementing on proto, reconstructing on trunk. Those skills do not perform the review, and they do not merge. QA and review orchestration sit at the rear. This page is that orchestration. The judgment stays in [code_review.md](code_review.md). Do not replace it, and do not copy it here.

## Orchestrator and operator

This split is not optional.

The orchestrator does not review, does not post the verdict, and does not squash-merge. That work belongs to the QA Operator.

The orchestrator's context is for communicating with the human and summarizing what the operator returns. The operator returns the snapshot to the orchestrator. The orchestrator summarizes it to the human. The orchestrator does not turn that summary into the posted review.

When the human approves a squash merge, the orchestrator tells the operator who already holds that pull request. The operator posts the verdict, squash-merges, and closes the authorizing issue by hand. The orchestrator then summarizes the result.

An already-merged pull request is not reopened to redo this. The rule is for the next one.

## What the operator judges by

The standard already written in [code_review.md](code_review.md). Style floor first, then acceptance criteria, then the lens for the PR:

- **Prototype** — an RFP PR to proto. The RFP's content, the vision, and the distillation sections it cites. Not trunk.
- **Release** — a trunk PR to `main`, or a sub-TRD PR to its Super-TRD branch. Artifact fidelity. On a Release review the operator is the only role that reads proto, and only as that page allows.

A Doc or skills PR is the same operator, held to that page's Doc section. There is no third standard.

One operator per PR. A Super-TRD still follows the fresh-reviewer rule in [code_review.md](code_review.md): one fresh operator per sub-TRD PR, the same operator on re-review, a fresh final operator for the Super-TRD PR to `main`. If you have already reviewed another child of this Super-TRD, stop. Do not review it.

The operator may assign an issue to a milestone. The author does not invent one. The PR stays off the milestone.

## The snapshot

Return 350–400 words to the orchestrator. Stay inside that range. The orchestrator summarizes that return to the human. The operator does not hand the orchestrator a verdict to post.

Name:

- the objective;
- what was added, changed, and removed;
- what each new artifact owns, taken from artifact comments and docstrings;
- comments of note: redundancies, inconsistencies, refactors, and cleanups;
- a point of future inquiry, when the review found one.

Ownership comes from the artifact comments and the docstrings, not from the PR blurb. Comments of note are observations. They do not become a new blocking class, and they do not waive the style floor. A blocking finding is still a blocking finding under [code_review.md](code_review.md). If there is nothing of note, say so in one sentence. If there is no future inquiry, do not manufacture one. Both ride inside the same 350–400 words.

The snapshot is not the posted review. It is not a short status. It is not a [Collaboration Report](collab_report.md). Do not post it as a PR conversation comment.

## Future inquiry

The snapshot may name a point of future inquiry for the forward team. New work is possible. It is not a blocking finding, and it is not a defect in the reviewed change. The operator records it. The forward team decides whether it becomes new work. Do not invent that work. Do not open an RFP or a TRD from the note.

It is not the **Out of scope** sort in [code_review.md](code_review.md). That sort leaves a thing alone. A future inquiry is written down.

The first case, from the approved squash of PR #1340 (RFP-053, issue #1333): an empty `parameters: {}` compared with None is still a tester gap. `equals` does not settle how an expected empty mapping compares with None. RFP-053 left that comparison outside its scope. That sentence is the kind of note the snapshot carries. It is not a new RFP.

## The posted review

Perform the review, then post it as [code_review.md](code_review.md) already requires: one consolidated review, line comments only on lines in the diff. Posting mechanics, including a shared GitHub token, stay on that page.

The first line of the posted review remains exactly `Verdict: Approve` or `Verdict: Changes requested`. Then the findings summary. Then your own attribution ([process.md](process.md#attribution)).

The operator posts the verdict. The orchestrator does not. This is not optional. Return the snapshot to the orchestrator. Do not wait for the orchestrator to post the review. A clean verdict is not, by itself, approval to merge.

When the orchestrator relays that the human approved the squash merge, the operator who already holds that pull request posts the verdict, squash-merges, and closes the authorizing issue by hand. Then the orchestrator summarizes the result.

On a Doc PR there is no issue. The posted review is the status. The snapshot is still returned to the orchestrator, not pasted onto the PR as a second note.

## Squash-merge

The operator may squash-merge only after the human says that issue or PR is approved for squash merge. The orchestrator does not squash-merge, even after that approval. The orchestrator tells the operator who already holds the pull request. That operator squash-merges.

The operator does not merge to `main` unless the human explicitly relinquished that specific PR.

Both sentences hold. A squash approval for a proto PR, or for a sub-TRD PR, is not a relinquishment of a PR that targets `main`. Saying a PR is approved for squash merge does not, by itself, relinquish a PR that targets `main`. Relinquishing a PR that targets `main` does not skip the squash-merge sentence. That merge still needs the human to have said it is approved for squash merge.

There is no standing permission to squash-merge a sub-TRD PR without that human approval. A `Verdict: Approve` is not that approval.

Immediately before the merge, run `gh pr view <N> --json baseRefName` again. A sub-TRD PR whose base is not the Super-TRD branch is not merged. A PR that should land on `main` and does not have base `main` is not merged. The command is in [commands.md](commands.md).

The squash message for a proto PR must not contain `Closes`, `Fixes`, or `Resolves`. The same ban holds for a sub-TRD PR. Proto does not honor those keywords. The operator closes the authorizing issue by hand. The implementing session does not close it in the operator's place. Neither puts a closing keyword on the proto PR.

No tag. No version bump. Those stay on the [agent guardrails](process.md#agent-guardrails) list. This exception does not cover them.

The maintainer, a human, may still squash-merge. The orchestrator does not. Every agent who is not the QA Operator, and not the maintainer, never merges ([process.md](process.md#agent-guardrails)).

This exception is squash-merge only. It is not a merge commit, not a push to `main` or proto, and not a fan-out. Cutting a Super-TRD branch, opening the Super-TRD PR, and merge-committing `main` into that branch stay with the maintainer.

## What stays forward

The author implements, self-checks against [code_review.md](code_review.md), opens the PR, and posts short status on the issue. After a squash the author still runs closeout. A standalone trunk closeout is still a Collaboration Report on the issue. That report is not this role.

Round skills point here for review orchestration. They do not restate a different merge rule.

## Guardrails

- Never merge to `main` unless the human explicitly relinquished that specific PR.
- Never squash-merge unless the human said that issue or PR is approved for squash merge.
- Never tag, bump the package version, mint a freeze, or create or close a milestone.
- Never use `Closes`, `Fixes`, or `Resolves` on a proto PR, including the squash message. Never use them on a sub-TRD PR.
- Never lower a style or ordering finding.
- Never proto → trunk git. Never send an implementer to proto.
- Never review a second child of the same Super-TRD.
- Never commit as part of a review.
- Never post the snapshot as a Collaboration Report or as a PR conversation comment.
- The orchestrator never reviews, never posts the verdict, and never squash-merges. That work is the operator's. Not optional.
- Never reopen an already-merged pull request to redo this split. The rule is for the next one.
