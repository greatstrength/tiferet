# QA Operator

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

[process.md](process.md) is the index. This page is a **Takwin role**. It is not a Tiferet implementation role, and it is not a second review standard.

Forward development stays forward: authoring an RFP, implementing on proto, reconstructing on trunk. Those skills do not perform the review, and they do not merge. QA and review orchestration sit at the rear. This page is that orchestration. The judgment stays in [code_review.md](code_review.md). Do not replace it, and do not copy it here.

## What the operator judges by

The standard already written in [code_review.md](code_review.md). Style floor first, then acceptance criteria, then the lens for the PR:

- **Prototype** — an RFP PR to proto. The RFP's content, the vision, and the distillation sections it cites. Not trunk.
- **Release** — a trunk PR to `main`, or a sub-TRD PR to its Super-TRD branch. Artifact fidelity. On a Release review the operator is the only role that reads proto, and only as that page allows.

A Doc or skills PR is the same operator, held to that page's Doc section. There is no third standard.

One operator per PR. A Super-TRD still follows the fresh-reviewer rule in [code_review.md](code_review.md): one fresh operator per sub-TRD PR, the same operator on re-review, a fresh final operator for the Super-TRD PR to `main`. If you have already reviewed another child of this Super-TRD, stop. Do not review it.

The operator may assign an issue to a milestone. The author does not invent one. The PR stays off the milestone.

## The snapshot

Return 350–400 words to the human who asked for the review. Stay inside that range.

Name:

- the objective;
- what was added, changed, and removed;
- what each new artifact owns, taken from artifact comments and docstrings;
- comments of note: redundancies, inconsistencies, refactors, and cleanups.

Ownership comes from the artifact comments and the docstrings, not from the PR blurb. Comments of note are observations. They do not become a new blocking class, and they do not waive the style floor. A blocking finding is still a blocking finding under [code_review.md](code_review.md). If there is nothing of note, say so in one sentence.

The snapshot is not the posted review. It is not a short status. It is not a [Collaboration Report](collab_report.md). Do not post it as a PR conversation comment.

## The posted review

Perform the review, then post it as [code_review.md](code_review.md) already requires: one consolidated review, line comments only on lines in the diff. Posting mechanics, including a shared GitHub token, stay on that page.

The first line of the posted review remains exactly `Verdict: Approve` or `Verdict: Changes requested`. Then the findings summary. Then your own attribution ([process.md](process.md#attribution)).

Show the findings and the proposed verdict to the human and wait for a go-ahead before you post. That wait is for posting. It is not a merge approval. A clean verdict is not approval to merge.

On a Doc PR there is no issue. The posted review is the status. The snapshot is still returned to the human, not pasted onto the PR as a second note.

## Squash-merge

The operator may squash-merge only after the human says that issue or PR is approved for squash merge.

The operator does not merge to `main` unless the human explicitly relinquished that specific PR.

Both sentences hold. A squash approval for a proto PR, or for a sub-TRD PR, is not a relinquishment of a PR that targets `main`. Saying a PR is approved for squash merge does not, by itself, relinquish a PR that targets `main`. Relinquishing a PR that targets `main` does not skip the squash-merge sentence. That merge still needs the human to have said it is approved for squash merge.

There is no standing permission to squash-merge a sub-TRD PR without that human approval. A `Verdict: Approve` is not that approval.

Immediately before the merge, run `gh pr view <N> --json baseRefName` again. A sub-TRD PR whose base is not the Super-TRD branch is not merged. A PR that should land on `main` and does not have base `main` is not merged. The command is in [commands.md](commands.md).

The squash message for a proto PR must not contain `Closes`, `Fixes`, or `Resolves`. The same ban holds for a sub-TRD PR. Proto does not honor those keywords. After a proto squash, close the RFP issue by hand if it is still open. The implementing session does the same at its closeout if the issue is still open. Neither puts a closing keyword on the proto PR.

No tag. No version bump. Those stay on the [agent guardrails](process.md#agent-guardrails) list. This exception does not cover them.

The maintainer, a human, may still squash-merge. Every other agent never merges ([process.md](process.md#agent-guardrails)).

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
