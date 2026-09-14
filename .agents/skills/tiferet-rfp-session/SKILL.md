---
name: tiferet-rfp-session
description: >
  Implement a published RFP on the prototype branch: cut the worktree,
  implement against the RFP AC, open a PR to proto, tag the alpha after merge,
  and record the landing in an RFP issue session note.
---

# Implement an RFP on prototype

## When to use

- A published RFP issue exists and the user wants it implemented on proto.

## When not to use

- Trunk work — `tiferet-milestone-session` / Super-TRD skills.
- Drafting the RFP — `tiferet-author-rfp`.
- Docs/skills.

## Canonical source

- `docs/collab/rfp.md`
- `docs/collab/process.md`
- `docs/collab/binding.md`

## Inputs

RFP issue number. Binding (proto branch, prefix). Next alpha from `git tag --list 'vX.Y.0a*'`.

## Procedure

**Prototype**

1. Read the RFP issue (current amended body). Review is against that proposal, AC, and cited distillation sections — not trunk.
2. Cut `vX.Y.0bN-<kebab-context>` from the proto branch in binding.md. PR will target proto.
3. Implement and test. Read `tiferet-code-style` and the component skills you touch.
4. Commit. Stop before push if the human has not approved opening the PR.
5. PR title: `vX.Y.0aN — <Plain Title> (RFP-00N)`. PR body: what changed + AC checkboxes. No session novel on the PR.
6. After squash-merge: bump package version to that alpha, annotated tag, push the tag.
7. On the **RFP issue**: session note with the conversation link, RFP id, alpha tag, and beta milestone.

## Outputs

- PR targeting proto (review surface).
- Alpha tag on proto.
- Session note on the **issue**.

## Guardrails

- No TRD.
- Never proto → trunk git.
- Never merge unless asked.
