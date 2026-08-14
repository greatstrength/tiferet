---
name: tiferet-freeze-catalog
description: >
  Record a catalog freeze for a named RFP cluster so trunk TRDs may be authored.
  Use only after a human names the cluster and issue numbers. Runs the ready-to-freeze
  checklist and writes freeze notes on those RFP issues.
---

# Freeze a catalog cluster

## When to use

- A human has named an RFP cluster to freeze for reconstruction.

## When not to use

- The human has not named the cluster. Do not invent a freeze.
- Implementing proto or trunk work.
- A shape amendment is still open on those RFPs.

## Canonical source

- `docs/collab/process.md` (Catalog freeze)
- `docs/collab/rfp.md`
- `docs/collab/binding.md`

## Inputs

Human-named cluster, RFP issue numbers, binding (freeze id pattern, prefix).

## Procedure

1. Run the ready-to-freeze checklist in process.md. If any box fails, stop. Recommend amend or `bN+1`.
2. Re-read Suggested TRD slicing against the **current** amended RFP bodies. Refresh the list.
3. Allocate the next freeze id (`TIF2-FREEZE-<nnn>` from binding).
4. On **each included RFP issue**, post a freeze note: Status `Frozen for reconstruction`, freeze id, alpha tags, distillation sections, refreshed slicing. Update the issue header Status if you are editing the body.
5. Tell the human they may now open a trunk milestone and author TRDs that cite this freeze id. `tiferet-author-trd` must refuse reconstruction without it.

## Outputs

Freeze notes on the **RFP issues**. No PR. No git.

## Guardrails

- Human names the cluster first.
- A later shape amendment thaws the freeze. Say that out loud if the user is about to amend a frozen RFP.
- Do not freeze a whole version line or product.
