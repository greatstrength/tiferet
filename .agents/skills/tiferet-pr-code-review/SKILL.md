---
name: tiferet-pr-code-review
description: >
  Review one pull request as the Prototype reviewer (RFP PR to proto) or the
  Release reviewer (trunk PR to main). Code style is held above everything
  else. Prototype review weighs RFP content, vision, and distillation; release
  review weighs artifact fidelity against the reference prototype or the TRD.
  One consolidated review with a verdict. The reviewer never merges.
---

# Review a pull request (diff surface)

## When to use

- The user asks to review a PR, or a round dispatches a reviewer for one PR.
- Prototype mode: the PR targets proto and is linked to an RFP issue.
- Release mode: the PR targets `main` and is linked to a standalone TRD or a Super-TRD parent.

## When not to use

- Session notes, status, or Collaboration Reports — those go on the **issue**.
- Implementing or fixing the PR — the author does that.
- Merging. The human squash-merges.
- Promoting proto onto trunk.

## Canonical source

- `docs/collab/code_review.md`
- `docs/core/code_style.md`
- `docs/collab/process.md`
- `docs/collab/binding.md`

## Inputs

PR number. Mode (Prototype | Release). Prototype: the RFP issue and its cited distillation sections. Release: the TRD (§3, §4, §5), and the reference prototype from its §7 row (tags or pre-release, or `None`). Binding for the proto branch name.

## Procedure

1. `gh pr view <n> --json number,headRefName,baseRefName,files` for head, base, and files. Confirm the PR is GitHub-linked to its authorizing issue and is not on a milestone.
2. Read the style guide and the `tiferet-code-<component>` skill for each component the PR touches. Style is checked first and is never waived: exactly one empty line between artifacts, artifact order preserved (an out-of-order artifact needs an order-preserving mechanic, never a reorder), including code examples in docs and skills.
3. Check the rest of the shared floor in order: every AC met, tests relevant and accurate to their unit, nothing superfluous.
4. **Prototype mode:** check the RFP content (every proposal item and AC realized as written), then alignment with the vision statement and the cited distillation sections (an amendment rides in the same PR). Concept outranks artifact cataloging. Do not compare to `main`. Skip Suggested TRD slicing.
5. **Release mode:** artifact fidelity is the primary lens. For every artifact TRD §3 and §4 name, compare against the reference prototype: `git fetch origin <proto> --tags`, then `git diff <reference-tag>..HEAD -- <path>` and `git show <reference-tag>:<path>`. With no reference prototype, §3 and §4 are the specification. A deviation on a named artifact is a finding even when trunk looks cleaner; a real improvement goes through a TRD amendment. A hotfix is reviewed against the hotfix TRD only, with no proto.
6. Sort findings: style violation (blocking), AC fail, test defect, superfluous, artifact deviation (release, blocking), concept deviation (prototype, blocking), name or placement note (prototype, non-blocking), out of scope.
7. Show the findings and a proposed verdict to the human. Wait for the go-ahead.
8. Post **one** consolidated review through the reviews API (`path` + `position`). Body: findings summary, verdict (Approve or Changes requested), `Co-Authored-By: Warp <agent@warp.dev>`. Line comments only on lines in the PR diff; whole-file or whole-package comments go in the body.
9. Post a short status on the authorizing issue (the Super-TRD parent for a Super-TRD). For a Super-TRD, note a child's AC failure on that child issue too.

## Outputs

- One PR review (diff comments + body + verdict) on the **PR**.
- A short status on the **issue**. Nothing else on the PR.

## Guardrails

- Never merge. Approve and report; a human squash-merges.
- Never lower a style or ordering finding to keep a review moving.
- Never proto → trunk git. In release mode, only the reviewer reads proto; never tell an implementor to read it.
- Never review a prototype PR against trunk.
- Check the code before claiming a behavior.
- Never commit as part of a review.
- Read `docs/collab/binding.md` in this repo for owner/repo and proto branch.
