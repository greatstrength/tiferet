---
name: tiferet-author-trd
description: >
  Author a Technical Requirements Document for trunk reconstruction or a hotfix.
  Use before implementing non-trivial trunk work. Reconstruction requires a
  catalog freeze id. Not for RFPs or Doc/skills PRs.
---

# Author a trunk TRD

## When to use

- Reconstruction of a **frozen** RFP cluster, or a mechanical hotfix on trunk.

## When not to use

- Prototype / RFP — `tiferet-author-rfp`.
- Docs/skills — no TRD; open a Doc PR.
- Implementing an already-authored TRD — milestone / Super-TRD skills.

## Canonical source

- `docs/collab/tech_requirements.md`
- `docs/collab/process.md`
- `docs/collab/project_fields.md`
- `docs/collab/binding.md`

## Inputs

Kind (reconstruction | hotfix). For reconstruction: freeze id. Binding file. Size signals.

## Procedure

**Trunk**

1. Kind first. Reconstruction without a freeze id → stop. Point at `tiferet-freeze-catalog`.
2. Size ([project_fields.md]). Then path: standalone (XL or below, or XL with no seam) vs Super-TRD (XL+ and a seam).
3. Write the TRD in `.trd/` using the structure in tech_requirements.md. Artifact operations only. Branch-agnostic. Never "copy from proto."
4. Reconstruction §7 cites the freeze id. Hotfix header `**Type:** Hotfix` and no freeze row.
5. Super-TRD parent uses the parent structure; children stay ≤ Medium.
6. After human approval, create the GitHub issue via `gh api` (not `gh issue create --milestone`). Rename the file to insert `m<N>_` and the issue number. Status=Ready. Field ids from binding.md. Commands in `docs/collab/commands.md`.

## Outputs

- `.trd/` file (gitignored).
- GitHub issue body. Not a PR.

## Guardrails

- No `Version: Request for Prototype`.
- Never send the implementor to proto.
- Never proto → trunk git.
- Doc/skills changes do not get a TRD.
