---
name: tiferet-author-trd
description: >
  Author a Technical Requirements Document for a hotfix or one standalone
  reconstruction on trunk. Reconstruction requires an existing catalog freeze id.
  Not for RFPs or Doc/skills PRs.
---

# Author a trunk TRD

## When to use

- One reconstruction TRD of a **frozen** catalog (freeze id already exists), or a mechanical hotfix on trunk.

## When not to use

- Prototype / RFP — `tiferet-author-rfp`.
- Docs/skills — no TRD; open a Doc PR.
- Implementing an already-authored TRD — `tiferet-implement-trd`.
- Minting a freeze id or opening a trunk milestone.

## Canonical source

- `docs/collab/tech_requirements.md`
- `docs/collab/process.md`
- `docs/collab/project_fields.md`
- `docs/collab/binding.md`
- `docs/collab/commands.md`

## Inputs

Kind (reconstruction | hotfix). For reconstruction: freeze id (must already exist). Binding file. Size signals.

## Procedure

1. Kind first. Reconstruction without a freeze id → stop. Do not invent a freeze.
2. Size ([project_fields.md]). Path: standalone (XL or below, or XL with no seam). Super-TRD parent/child *genre* is in tech_requirements.md; do not run a parent fan-out from this skill.
3. Write the TRD in `.trd/` using the structure in tech_requirements.md. Artifact operations only. Branch-agnostic. Never "copy from proto." Title uses Component/Assemblage.
4. Reconstruction §7 cites the existing freeze id and names blocking TRDs. Hotfix header `**Type:** Hotfix` and no freeze row.
5. After human approval, create the GitHub issue via `gh api` (not `gh issue create --milestone`). Rename the file to insert the issue number. Status=Ready. Wire blocked-by from §7 (`docs/collab/commands.md`). Leave milestone assignment to the reviewer unless asked.

## Outputs

- `.trd/` file (gitignored).
- GitHub issue body. Not a PR.
- Blocked-by edges.

## Guardrails

- No `Version: Request for Prototype`.
- Never send the implementor to proto.
- Never proto → trunk git.
- Doc/skills changes do not get a TRD.
- Do not mint freeze ids. Do not open milestones.
