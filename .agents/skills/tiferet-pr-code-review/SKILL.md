---
name: tiferet-pr-code-review
description: >
  Post actionable diff comments on a pull request. Reconstruction review
  measures AC-named artifacts (optional proto glance). Never "make trunk
  match proto." Prototype review is against the RFP, not trunk.
---

# Review a pull request (diff surface)

## When to use

- The user asks to review a PR. Super-TRD combined review: read `tiferet-super-trd-reviewer` first; this skill is only the diff-posting mechanic.

## When not to use

- Session notes, conversation links, Collaboration Reports — those go on the **issue**.
- Promoting proto onto trunk.

## Canonical source

- `docs/collab/code_review.md`
- `docs/collab/process.md`
- `docs/collab/binding.md`

## Inputs

PR number. Strand. For reconstruction: freeze id / TRD AC. For proto: RFP AC.

## Procedure

Follow code_review.md:

1. `gh pr view` for head/base/files.
2. **Prototype:** review vs RFP + distillation. Do not compare to `main`.
3. **Trunk reconstruction:** AC-first. Optional `git diff origin/<proto>..HEAD -- <path>` only for AC-named artifacts. Ahead = keep. Behind is a finding only with an AC fail (or the freeze named that artifact).
4. **Hotfix / Doc:** TRD or PR intent only.
5. Show findings to the human; wait.
6. One reviews-API post (`path` + `position`). Review body: findings + Co-Authored-By. Conversation link for Super-TRD goes on the **parent issue**.

## Outputs

PR review (diff comments + body). Nothing else on the PR.

## Guardrails

- Never recommend proto → trunk git.
- Never recommend reverting trunk that is ahead of proto.
- Never merge.
