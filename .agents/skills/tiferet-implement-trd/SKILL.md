---
name: tiferet-implement-trd
description: Implement one published trunk TRD or one Super-TRD child. A child cuts from main and opens a PR targeting main; the Super-TRD has no branch of its own. Not for RFPs or freeze minting.
---

# Implement a trunk TRD

## When to use

- A published standalone TRD issue exists.
- A published Super-TRD child whose blockers are all squash-merged to `main`.

## When not to use

- Prototype / RFP - `tiferet-rfp-session`.
- Authoring the TRD - `tiferet-author-trd`.
- Docs/skills.
- Closing a milestone - the maintainer only (`docs/collab/process.md`, Agent guardrails).
- A Super-TRD child whose parent is not In Progress yet. Stop and report.
- A Super-TRD child with a blocker not yet squash-merged to `main`. Stop and report.

## Canonical source

- `docs/collab/main.md`
- `docs/collab/tech_requirements.md`
- `docs/collab/process.md`
- `docs/collab/code_review.md`
- `docs/collab/binding.md`
- `docs/collab/commands.md`

## Inputs

TRD issue number. For a Super-TRD child: parent issue number. Binding. The PR base, named in the task (`main` for both standalone and child).

## Procedure

**Standalone**

1. Confirm the TRD. Reconstruction must cite an existing freeze id. If §7 and a blocker form a cycle - each names the other's output as a prerequisite - stop and report.
2. Cut `<issue>-<slug>` from `main`. Status In Progress. Start date.
3. Implement (`tiferet-code-style` + component skills). PR targeting `main`, title `<Component/Assemblage> - <Plain Title> (#issue)`, **GitHub-linked** to that TRD. `Closes #<issue>` is allowed. Body: the TRD's AC as checkboxes, all unchecked. Do not add the PR to a milestone.
4. Verify the base: `gh pr view <N> --json baseRefName`. It must be `main`. If it is not, stop and report. Do not request review.
5. Short status on the **issue** after the PR opens, and again after addressing PR feedback. Re-review goes back to the same reviewer.
6. Before asking for review, self-check against the shared review standards in `docs/collab/code_review.md`: code style first (exactly one empty line between artifacts, artifact order preserved with an order-preserving mechanic if a dependency seems to force an exception), then every AC, then fidelity to every artifact TRD section 3 and section 4 name, then relevant and accurate tests and nothing superfluous. Tests in section 4 are cases on named tests, not a second field table and not a pasted implementation: write each one under the name the TRD gives it. Until the rendering skill exists, the Python file is the acceptance gate; do not call `run_test_module`, and the YAML under `tiferet_tests/` is the same cases, not a gate. Work from the TRD only; do not read proto. Do not review and do not merge. Review and merge are outside these contribution guidelines.
7. After squash-merge: `tiferet-collab-report` on the issue. Status Done. End date. `.trd/` → `.complete.md`. Run the closeout cleanup in `docs/collab/process.md`. Trunk→proto git only if the human asks.

**Super-TRD child**

The parent has no branch and no PR of its own. Children do not commit onto a shared branch. Every child uses this procedure, from `main` to Done. When the child issues allow concurrency, an agent may run a fan-out with one implementer per ready child. Law: `docs/collab/process.md`, Super-TRD.

1. Confirm the parent issue and this child, and that the parent is In Progress. If it is not, stop and report.
2. If this child is on a blocked-by cycle, stop and report. Do not pick an order.
3. If this child is blocked by a standalone TRD or by any other work outside its parent, do not branch, assign, or implement until those blockers are squash-merged to `main`. Do not start speculatively. Do not rebase later. A sibling blocker is satisfied only when that sibling's PR is squash-merged to `main`; cut from `main` after that, not from the sibling's branch. Law: `docs/collab/process.md`, Cross-boundary blockers.
4. Cut `<child-issue>-<slug>` from `main`. Status In Progress. Start date on this child.
5. Implement this child only. Self-check as in Standalone step 6. Do not read proto.
6. Open a PR targeting `main`. Title `<Component/Assemblage> - <Plain Title> (#child)`. Body: `Closes #<child>` and `Refs #<parent>`, plus this child's AC checkboxes, all unchecked. Never put `Closes`, `Fixes`, or `Resolves` on the parent. Do not add the PR to a milestone.
7. Verify the base: `gh pr view <N> --json baseRefName`. It must be `main`. If it is not, stop and report. Do not request review.
8. Set this child issue Status to **In Review**. Short status on the **child issue**. No Collaboration Report.

9. After squash-merge: the child closes through `Closes #<child>`. Status Done. End date. No Collaboration Report. Rename `.trd/` to `.complete.md` and run the closeout cleanup in `docs/collab/process.md`.

Once every child is Done, the parent goes In Review for its final review. The parent issue closes after its final review, once every child issue is closed. Neither step is part of this skill.

## Outputs

- Standalone: PR targeting `main`.
- Super-TRD child: PR targeting `main`. Not a commit on someone else's branch.
- Short issue status. Super-TRD child: Status In Review, then Done after merge.
- Standalone: Collaboration Report after merge.

## Guardrails

- Never proto → trunk git. Never read proto to copy code. Never check out proto into the trunk worktree.
- Never review. Never merge from this skill. Review and merge are outside these contribution guidelines. Never start a child whose blockers are not yet squash-merged to `main`.
- Never tag or bump version on this PR.
- Never check an AC box on your own PR. The reviewer checks each one as it verifies it.
- Never `Closes` / `Fixes` / `Resolves` on the parent from a Super-TRD child PR.
- Closeout leaves nothing behind: remove the worktree and its registration, the local and remote branch you cut, and every temp file (`docs/collab/process.md`). `.trd/` and `.rfp/` working copies are not temp.
- Never put temporary information on external or cloud storage unless the human explicitly authorizes it.
- Attribute yourself in your own name, never another agent's (`docs/collab/process.md` § Attribution). On a shared bot account, end every issue, PR, and comment with `- <agent>@<platform> via <account>` (§ Shared bot accounts). Never merge, tag, bump the version, mint a freeze, or create or close a milestone (§ Agent guardrails).
