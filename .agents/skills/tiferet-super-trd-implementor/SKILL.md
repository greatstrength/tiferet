---
name: tiferet-super-trd-implementor
description: >
  Starter and Implementor for a trunk Super-TRD: cut the parent branch,
  implement children, keep the PR as a review surface, and post session notes
  plus an implementation-log Collaboration Report on the child issue.
---

# Super-TRD — Starter & Implementor

## When to use

- `tiferet-super-trd` identified STARTER or IMPLEMENTOR.

## When not to use

- Prototype / RFP.
- Standalone TRD.
- Combined review or closing — reviewer / closer skills.

## Canonical source

- `docs/collab/super_trd_workflow.md`
- `docs/collab/collab_report.md`
- `docs/collab/binding.md`

## Inputs

Parent issue, active child, binding. Reconstruction parents must cite a freeze id.

## Procedure

**Trunk — Starter**

1. `git checkout main && git pull && git checkout -b <parent>-<slug>`
2. Child 1 → In Progress. Do not set the parent.
3. Implement child 1 from its TRD §4, section by section. `tiferet-code-style` + component skills. `pytest`.
4. Commit. Stop. After human approval: push and open the PR targeting `main`.
5. PR body covers **all** children (unchecked AC for later ones) and `Closes #<parent>` only.
6. Child 1 → In Review. Add PR to the project board.
7. On the **child issue**: session note (conversation link, in-scope activities) and Collaboration Report kind **implementation log**.

**Trunk — later children (PR open)**

1. Confirm sibling landings on **this branch**.
2. Implement, commit, push. Check off that child's AC on the PR. Child → In Review.
3. On the **child issue**: session note + implementation log. Do not open a second PR.

**Addressing PR diff comments** on the active child: fix in code, push. Note the fix on the **child issue** if it is more than a one-line tweak.

Do **not** close the child as Done. Do **not** rename to `.complete.md` yet.

## Outputs

- Commits + PR updates (review surface).
- Session note + implementation log on the **child issue**.

## Guardrails

- Never post session notes or reports on the PR.
- Never add `Closes #<child>` or edit `Closes #<parent>`.
- Implementation log ≠ Done.
- Never proto → trunk git. Never merge unless asked.
