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

- Prototype / RFP - `tiferet-author-rfp`.
- Docs/skills - no issue, no TRD; open a Doc PR.
- Implementing an already-authored TRD - `tiferet-implement-trd`.
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

1. Kind first. Reconstruction without a freeze id: stop. Do not invent a freeze.
2. Size ([project_fields.md]). Path: standalone (XL or below, or XL with no seam). Super-TRD parent/child *genre* is in tech_requirements.md; do not run a parent fan-out from this skill.
3. Write the TRD in `.trd/` using the structure in tech_requirements.md. Artifact operations only. Branch-agnostic. Never "copy from proto." Title uses Component/Assemblage.
4. Section 4 is one numbered block per component: **Implementation**, then **Tests**, both as Add / Update / Remove, with no pytest and no YAML in the block. Implementation states the code artifacts; its operation headings (`##### Add: # *** constants (<subgroup>)`) sit under it, and that table is not the test spec. Tests states one case per named test in tester language (fixtures, tester, subject, conditions, action, expectation) and names its test module; the TRD does not choose Python or YAML. One name per test, the same in both renderings. Section 5 cites the test name and does not restate the case. Until the rendering skill exists, the Python file is the acceptance gate, the YAML under `tiferet_tests/` is not, and cases do not call `run_test_module`. The rules and a worked example are in tech_requirements.md under Component blocks in section 4.
5. Reconstruction section 7 cites the existing freeze id, records the **reference prototype** (the proto tags or pre-release from the freeze, or `None`), and names blocking TRDs. Name every section 3/section 4 artifact completely (labels, names, section and sub-group placement, parameters, named test cases): a Release review measures each one against that row and, read-only, against the prototype branch. The TRD is the whole fidelity source when there is no prototype. Hotfix header `**Type:** Hotfix` with no freeze row and no reference prototype row.
6. Before wiring blocked-by, check for a cycle. If this issue's output is a prerequisite of an issue that blocks it - or the maintainer-supplied set has two issues each naming the other's output as a prerequisite - stop and report. Do not wire the cycle. Do not invent an order.
7. After human approval, create the GitHub issue via `gh api` (not `gh issue create --milestone`). Rename the file to insert the issue number. Status=Ready. Wire blocked-by from section 7 (`docs/collab/commands.md`) only if step 6 found no cycle. If this TRD is a Super-TRD child, also wire its external blocked-by (standalone TRDs and any work outside the parent branch) on the parent issue. Do not assign a milestone.

## Outputs

- `.trd/` file (gitignored).
- GitHub issue body. Not a PR.
- Blocked-by edges.

## Guardrails

- No `Version: Request for Prototype`.
- Never send the implementor to proto. The reference prototype row, and the read-only branch check, are for review, which is outside these contribution guidelines.
- Never proto → trunk git. Never check proto out or copy it into a TRD.
- Never publish a blocked-by cycle.
- Doc/skills changes do not get a TRD.
- Do not mint freeze ids. Do not open milestones.
- Attribute yourself in your own name, never another agent's (`docs/collab/process.md` § Attribution). On a shared bot account, end every issue, PR, and comment with `- <agent>@<platform> via <account>` (§ Shared bot accounts). Never merge, tag, bump the version, mint a freeze, or create or close a milestone (§ Agent guardrails).
