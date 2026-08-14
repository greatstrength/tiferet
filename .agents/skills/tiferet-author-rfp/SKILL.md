---
name: tiferet-author-rfp
description: >
  Author or amend a Request for Prototype (RFP) for a Tiferet-family repo.
  Use when the user wants a domain theory tested on the prototype strand,
  or to update an existing RFP in place. Not for trunk TRDs or Doc PRs.
---

# Author an RFP

## When to use

- Draft a new RFP or amend one in place on the same issue.

## When not to use

- Trunk reconstruction or hotfix — `tiferet-author-trd`.
- Docs/skills — no specification document; open a Doc PR.
- Implementing an already-published RFP — `tiferet-rfp-session`.
- Freezing a cluster — `tiferet-freeze-catalog` (human names the cluster first).

## Canonical source

- `docs/collab/rfp.md`
- `docs/collab/process.md`
- `docs/collab/binding.md`

## Inputs

Binding file (proto branch, RFP prefix). Distillation sections to cite. Optional existing issue number.

## Procedure

**Prototype**

1. Read binding.md. Prefix example: `TIF2`. Proto branch example: `v2.x-proto`.
2. Draft `.rfp/<prefix-lower>-rfp-<nnn>-<kebab>.md` with the genre in rfp.md: header (Status, Domain, Branch, Issue, Related, Depends on, Blocks) then Summary, Motivation, Current state, Proposal, Out of scope, Risks (resolved vs open), Acceptance criteria, Suggested TRD slicing.
3. Amendments: Status = Amended, add Amendment note, keep the same issue. Do not open a new number.
4. Publish or refresh the GitHub issue body from that file. Title: `RFP-00N — <Plain Title>`. Assign the open beta milestone `vX.Y.0bN` (create it with `tiferet-create-milestone` if missing).
5. If this amendment changes shape of a **frozen** RFP, say so — that freeze is thawed. Do not keep reconstructing the old catalog.

## Outputs

- Local `.rfp/` file (gitignored).
- GitHub issue body (public copy). Posted on the **issue**, not a PR.

## Guardrails

- Every RFP is an issue. No internal RFPs without an issue.
- Do not write a TRD. Do not set `Version: Request for Prototype` on anything.
- Never proto → trunk git.
