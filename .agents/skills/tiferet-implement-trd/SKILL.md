---
name: tiferet-implement-trd
description: >
  Implement one published trunk TRD or one Super-TRD child already in flight.
  PR to main, GitHub-linked to the standalone TRD or the Super-TRD parent.
  Not for RFPs, freeze minting, or running a Super-TRD fan-out.
---

# Implement a trunk TRD

## When to use

- A published standalone TRD issue exists, or a Super-TRD child is already in flight on a parent branch.

## When not to use

- Prototype / RFP — `tiferet-rfp-session`.
- Authoring the TRD — `tiferet-author-trd`.
- Docs/skills.
- Opening a parent Super-TRD PR as the first of many children, or closing a milestone.

## Canonical source

- `docs/collab/main.md`
- `docs/collab/tech_requirements.md`
- `docs/collab/process.md`
- `docs/collab/binding.md`
- `docs/collab/commands.md`

## Inputs

TRD issue number. For a child: parent issue number and existing parent branch. Binding.

## Procedure

**Standalone**

1. Confirm the TRD. Reconstruction must cite an existing freeze id.
2. Cut `<issue>-<slug>` from `main`. Status In Progress. Start date.
3. Implement (`tiferet-code-style` + component skills). PR targeting `main`, title `<Component/Assemblage> - <Plain Title> (#issue)`, **GitHub-linked** to that TRD. `Closes #<issue>` is allowed. Do not add the PR to a milestone.
4. Short status on the **issue** after the PR opens, and again after addressing PR feedback.
5. After squash-merge: `tiferet-collab-report` on the issue. Status Done. End date. `.trd/` → `.complete.md`. Trunk→proto git only if the human asks.

**Super-TRD child already in flight**

1. Work on the existing parent branch. Do not open a second PR.
2. Implement this child only. Check off this child's AC on the parent PR if present.
3. The PR stays GitHub-linked to the **parent**. Never `Closes #<child>`.
4. Short status on the **child issue**. No Collaboration Report on the child.

## Outputs

- PR targeting `main` (standalone) or commits on the parent PR (child).
- Short issue status.
- Standalone: Collaboration Report after merge.

## Guardrails

- Never proto → trunk git.
- Never send yourself to proto to copy code.
- Never merge unless asked.
- Never tag or bump version on this PR.
