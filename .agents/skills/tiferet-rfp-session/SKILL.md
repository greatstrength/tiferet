---
name: tiferet-rfp-session
description: >
  Implement a published RFP on the prototype branch: cut the branch,
  implement against the RFP AC, open a PR to proto linked to that issue,
  and close the issue after squash. No tag. No version bump.
---

# Implement an RFP on prototype

## When to use

- A published RFP issue exists and the user wants it implemented on proto.

## When not to use

- Trunk work — `tiferet-implement-trd`.
- Drafting the RFP — `tiferet-author-rfp`.
- Docs/skills.
- Closing a milestone or cutting a release.

## Canonical source

- `docs/collab/rfp.md`
- `docs/collab/process.md`
- `docs/collab/binding.md`
- `docs/collab/commands.md`

## Inputs

RFP issue number. Binding (proto branch, prefix).

## Procedure

1. Read the RFP issue (current amended body). Review is against that proposal, AC, and cited distillation sections — not trunk.
2. Cut a branch from the proto branch in binding.md. PR will target proto.
3. Implement and test. Read `tiferet-code-style` and the component skills you touch.
4. Commit. Stop before push if the human has not approved opening the PR.
5. PR title: `RFP-00N — <Plain Title> (#issue)`. **GitHub-link** the PR to the RFP issue. Do not add the PR to a milestone. Body links `#issue` and does **not** use `Closes`.
6. After the PR opens, post a short status on the **RFP issue**. After addressing PR feedback, post another.
7. After squash-merge: close the RFP issue by hand. Delete the local branch / worktree. Do not tag. Do not bump the package version.

## Outputs

- PR targeting proto, linked to the RFP issue.
- Short status on the issue.
- Issue closed after squash.

## Guardrails

- No TRD.
- Never proto → trunk git.
- Never merge unless asked.
- Never tag or bump version on this PR.
