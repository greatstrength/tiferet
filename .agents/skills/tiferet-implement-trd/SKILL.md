---
name: tiferet-implement-trd
description: >
  Implement one published trunk TRD or one Super-TRD child. A child cuts
  from the already-pushed Super-TRD branch and opens a PR targeting that
  branch, never main. Not for RFPs, freeze minting, cutting the Super-TRD
  branch, or running a Super-TRD fan-out.
---

# Implement a trunk TRD

## When to use

- A published standalone TRD issue exists.
- A published Super-TRD child, and the Super-TRD branch `<parent-issue>-<slug>` is already pushed.

## When not to use

- Prototype / RFP — `tiferet-rfp-session`.
- Authoring the TRD — `tiferet-author-trd`.
- Docs/skills.
- Cutting the Super-TRD branch, opening the Super-TRD PR to `main`, running a fan-out, or closing a milestone — `takwin-release`, or the human.
- A Super-TRD child whose parent branch is not pushed yet. Stop and report. Do not open a PR to `main` in its place.

## Canonical source

- `docs/collab/main.md`
- `docs/collab/tech_requirements.md`
- `docs/collab/process.md`
- `docs/collab/code_review.md`
- `docs/collab/binding.md`
- `docs/collab/commands.md`

## Inputs

TRD issue number. For a Super-TRD child: parent issue number and the already-pushed Super-TRD branch `<parent-issue>-<slug>`. Binding. The PR base, named in the dispatch prompt (standalone: `main`; child: the Super-TRD branch).

## Procedure

**Standalone**

1. Confirm the TRD. Reconstruction must cite an existing freeze id. If §7 and a blocker form a cycle — each names the other's output as a prerequisite — stop and report.
2. Cut `<issue>-<slug>` from `main`. Status In Progress. Start date.
3. Implement (`tiferet-code-style` + component skills). PR targeting `main`, title `<Component/Assemblage> - <Plain Title> (#issue)`, **GitHub-linked** to that TRD. `Closes #<issue>` is allowed. Do not add the PR to a milestone.
4. Verify the base: `gh pr view <N> --json baseRefName`. It must be `main`. If it is not, stop and report. Do not request review.
5. Short status on the **issue** after the PR opens, and again after addressing PR feedback. Re-review goes back to the same reviewer.
6. Before asking for review, self-check against the shared review standards in `docs/collab/code_review.md`: code style first (exactly one empty line between artifacts, artifact order preserved with an order-preserving mechanic if a dependency seems to force an exception), then every AC, then fidelity to every artifact TRD §3 and §4 name, then relevant and accurate tests and nothing superfluous. Work from the TRD only; do not read proto. A Release reviewer (`tiferet-pr-code-review`) reviews. A human squash-merges a PR that targets `main`.
7. After squash-merge: `tiferet-collab-report` on the issue. Status Done. End date. `.trd/` → `.complete.md`. Run the closeout cleanup in `docs/collab/process.md`. Trunk→proto git only if the human asks.

**Super-TRD child**

The first child does not open the parent PR. Later children do not commit onto a shared branch. Every child uses this procedure. Law: `docs/collab/process.md` § Super-TRD branch.

1. Confirm the parent issue, this child, and that `<parent-issue>-<slug>` is already on the remote. If it is not, stop and report. Do not cut it, and do not open a PR to `main`.
2. If this child is on a blocked-by cycle, stop and report. Do not pick an order.
3. If this child is blocked by work that is not already on the Super-TRD branch, stop and report. Cross-boundary blockers are proposed, not decided (`docs/collab/process.md`). Do not merge `main` into the Super-TRD branch. Do not commit onto a sibling's branch.
4. Cut `<child-issue>-<slug>` from the Super-TRD branch tip, not from `main`. Status In Progress. Start date on this child.
5. Implement this child only. Self-check as in Standalone step 6. Do not read proto.
6. Open a PR targeting the Super-TRD branch, never `main`. Title `<Component/Assemblage> - <Plain Title> (#child)`. Body: `Refs #<child>` and `Refs #<parent>`, plus this child's AC checkboxes. Never `Closes`, `Fixes`, or `Resolves`. Do not add the PR to a milestone.
7. Verify the base: `gh pr view <N> --json baseRefName`. It must be the Super-TRD branch. If it is `main` or anything else, stop and report. Do not request review.
8. Set this child issue Status to **In Review**. Short status on the **child issue**. No Collaboration Report. Do not close the child. Do not open the Super-TRD PR to `main`.

Children stay **In Review** until the Super-TRD PR is squash-merged to `main`. Closing them is closeout (`takwin-release`), not this skill. A sub-TRD merge does not remove the Super-TRD branch.

## Outputs

- Standalone: PR targeting `main`.
- Super-TRD child: PR targeting the Super-TRD branch. Not a commit on someone else's branch, and not a PR to `main`.
- Short issue status. Super-TRD child: Status In Review.
- Standalone: Collaboration Report after merge.

## Guardrails

- Never proto → trunk git. Never read proto to copy code. Never check out proto into the trunk worktree.
- Never merge unless asked. Sub-TRD squash-merge is the reviewer's step (`tiferet-pr-code-review`), not yours.
- Never tag or bump version on this PR.
- Never `Closes` / `Fixes` / `Resolves` on a Super-TRD child PR.
- Never close a Super-TRD child issue. Children stay In Review until the parent PR to `main` is squash-merged.
- Closeout leaves nothing behind: remove the worktree and its registration, the local and remote branch you cut, and every temp file (`docs/collab/process.md`). Do not remove the Super-TRD branch. `.trd/` and `.rfp/` working copies are not temp.
- Never put temporary information on external or cloud storage unless the human explicitly authorizes it.
