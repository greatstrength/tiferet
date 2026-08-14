---
name: tiferet-create-milestone
description: >
  Create or format a GitHub milestone. Prototype drafting rounds are vX.Y.0bN.
  Trunk releases are vX.Y.Z. Use when organizing RFPs or TRDs into a milestone.
---

# Create a milestone

## When to use

- Open a proto beta milestone for an RFP drafting round, or a trunk `vX.Y.Z` milestone for reconstruction / hotfix / release.

## When not to use

- Doc/skills work — no milestone.
- Inventing a freeze — `tiferet-freeze-catalog`.

## Canonical source

- `docs/collab/process.md` (versioning)
- `docs/collab/rfp.md` / `docs/collab/main.md`
- `docs/collab/binding.md`
- `docs/collab/commands.md`

## Inputs

Strand (Prototype | Trunk). Version. Binding (owner/repo, title shapes). Optional freeze id for trunk reconstruction.

## Procedure

1. Read binding.md for owner/repo.
2. **Prototype:** title `vX.Y.0bN`. Description = drafting-round goal + RFP list (`RFP-00N (#issue): intent`). Create when the RFPs exist, not when the last one shipped.
3. **Trunk:** title `vX.Y.Z`. No `bN` on new trunk milestones. Description = goal, freeze id(s) if reconstruction, issue list.
4. Write the description to `.milestones/m<N>_<kebab>.md` (or a temp file) and:
   ```bash
   gh api repos/<owner>/<repo>/milestones \
     -f title='<Title>' \
     -F description=@<file> \
     --jq '{number, title, state, html_url}'
   ```
5. Report number and URL. Backfill `#TBD` issue numbers with a PATCH when issues exist.

## Outputs

GitHub milestone. Local `.milestones/` payload (gitignored).

## Guardrails

- Do not reuse historical trunk `bN` titles for new trunk work.
- Do not hardcode `greatstrength/tiferet` if binding.md says otherwise.
