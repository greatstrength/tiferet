---
name: tiferet-implement-trd
description: >
  Implement one published trunk TRD, the first Super-TRD child (opens the
  parent PR), or a later Super-TRD child already in flight. PR to main,
  GitHub-linked to the standalone TRD or the Super-TRD parent. Not for RFPs,
  freeze minting, or running a Super-TRD fan-out.
---

# Implement a trunk TRD

## When to use

- A published standalone TRD issue exists.
- The first Super-TRD child, when no parent PR exists yet.
- A later Super-TRD child already in flight on the parent branch.

## When not to use

- Prototype / RFP — `tiferet-rfp-session`.
- Authoring the TRD — `tiferet-author-trd`.
- Docs/skills.
- Running a Super-TRD fan-out or closing a milestone — `takwin-release`.

## Canonical source

- `docs/collab/main.md`
- `docs/collab/tech_requirements.md`
- `docs/collab/process.md`
- `docs/collab/binding.md`
- `docs/collab/commands.md`

## Inputs

TRD issue number. For a Super-TRD child: parent issue number. For a later child: existing parent branch. Binding.

## Procedure

**Standalone**

1. Confirm the TRD. Reconstruction must cite an existing freeze id.
2. Cut `<issue>-<slug>` from `main`. Status In Progress. Start date.
3. Implement (`tiferet-code-style` + component skills). PR targeting `main`, title `<Component/Assemblage> - <Plain Title> (#issue)`, **GitHub-linked** to that TRD. `Closes #<issue>` is allowed. Do not add the PR to a milestone.
4. Short status on the **issue** after the PR opens, and again after addressing PR feedback.
5. After squash-merge: `tiferet-collab-report` on the issue. Status Done. End date. `.trd/` → `.complete.md`. Trunk→proto git only if the human asks.

**Super-TRD first child** (no parent PR yet)

1. Confirm the parent issue and this child. Cut `<parent-issue>-<slug>` from `main`. Status In Progress. Start date on this child.
2. Implement this child only.
3. When complete, open the **one** Super-TRD PR targeting `main`, title `<Component/Assemblage> - <Plain Title> (#parent)`, **GitHub-linked** to the **parent**. `Closes #<parent>` only. Never `Closes #<child>`. Do not add the PR to a milestone.
4. Set this child issue Status to **In Review**. Short status on the **child issue**. No Collaboration Report on the child. Do not close the child.

**Super-TRD later child already in flight**

1. Work on the existing parent branch. Do not open a second PR.
2. Implement this child only. Check off this child's AC on the parent PR if present.
3. The PR stays GitHub-linked to the **parent**. Never `Closes #<child>`.
4. Set this child issue Status to **In Review**. Short status on the **child issue**. No Collaboration Report on the child. Do not close the child.

Super-TRD children stay **In Review** until the parent PR is squash-merged. Closing them is closeout (`takwin-release`), not this skill.

## Outputs

- PR targeting `main` (standalone or Super-TRD first child) or commits on the parent PR (later child).
- Short issue status. Super-TRD child: Status In Review.
- Standalone: Collaboration Report after merge.

## Guardrails

- Never proto → trunk git.
- Never send yourself to proto to copy code.
- Never merge unless asked.
- Never tag or bump version on this PR.
- Never close a Super-TRD child issue. Children stay In Review until parent-PR closeout.
