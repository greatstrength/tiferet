---
name: tiferet-milestone-session
description: >
  Run a milestone loop: prototype alphas (RFP → proto PR → alpha tag) or trunk
  standalone TRDs. Super-TRD parents go through tiferet-super-trd instead.
---

# Run a milestone session

## When to use

- Work the next issue in an open proto beta or trunk release milestone.

## When not to use

- Super-TRD parent — `tiferet-super-trd`.
- Drafting specs — author-rfp / author-trd.
- Docs/skills — Doc PR, no milestone loop.

## Canonical source

- `docs/collab/process.md`
- `docs/collab/rfp.md` / `docs/collab/main.md`
- `docs/collab/collab_report.md`
- `docs/collab/binding.md`

## Inputs

Milestone, next issue, strand, binding.

## Procedure

**Prototype** — delegate to `tiferet-rfp-session` per RFP in the beta milestone.

**Trunk standalone**

1. Confirm the TRD. Reconstruction must cite a freeze id.
2. Cut `<issue>-<slug>` from `main`. Status In Progress. Start date.
3. Implement (`tiferet-code-style` + component skills). PR targeting `main`.
4. Session note + Collaboration Report on the **issue**. PR stays review-clean.
5. After squash-merge: pull `main`, delete branch, `.trd/` → `.complete.md`, Status Done, End date. Trunk→proto git only if the human asks.

**Trunk Super-TRD** — stop and read `tiferet-super-trd`.

## Outputs

Per-issue PR + issue-side report, as above.

## Guardrails

- Never proto → trunk git.
- Never treat every issue as standalone.
- Never merge unless asked.
