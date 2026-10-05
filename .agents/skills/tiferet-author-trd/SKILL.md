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
4. Reconstruction §7 cites the existing freeze id, records the **reference prototype** (the proto tags or pre-release from the freeze, or `None`), and names blocking TRDs. Name every §3/§4 artifact completely (labels, names, section and sub-group placement, parameters, test catalog rows): the Release reviewer measures each one against that row and, read-only, against the prototype branch. The TRD is the whole fidelity source when there is no prototype. Hotfix header `**Type:** Hotfix` with no freeze row and no reference prototype row.
5. Before wiring blocked-by, check for a cycle. If this issue's output is a prerequisite of an issue that blocks it — or the orchestrator-supplied set has two issues each naming the other's output as a prerequisite — stop and report. Do not wire the cycle. Do not invent an order.
6. After human approval, create the GitHub issue via `gh api` (not `gh issue create --milestone`). Rename the file to insert the issue number. Status=Ready. Wire blocked-by from §7 (`docs/collab/commands.md`) only if step 5 found no cycle. Leave milestone assignment to the reviewer unless asked.

## Outputs

- `.trd/` file (gitignored).
- GitHub issue body. Not a PR.
- Blocked-by edges.

## Guardrails

- No `Version: Request for Prototype`.
- Never send the implementor to proto. The reference prototype row, and the read-only branch check, are for the Release reviewer.
- Never proto → trunk git. Never check proto out or copy it into a TRD.
- Never publish a blocked-by cycle.
- Doc/skills changes do not get a TRD.
- Do not mint freeze ids. Do not open milestones.
