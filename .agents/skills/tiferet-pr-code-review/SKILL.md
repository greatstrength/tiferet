---
name: tiferet-pr-code-review
description: Review one pull request as the Prototype reviewer (RFP PR to proto) or the Release reviewer (trunk PR to main, or a sub-TRD PR to its Super-TRD branch). Code style is held above everything else. Prototype review weighs RFP content, vision, and distillation; release review weighs artifact fidelity against the reference prototype and, read-only, the prototype branch. One consolidated review. The first line is the verdict. The reviewer never merges, on any base; the maintainer does.
---

# Review a pull request (diff surface)

## When to use

- The user asks you to review one PR.
- Prototype mode: the PR targets proto and is linked to an RFP issue.
- Release mode: the PR targets `main` and is linked to a standalone TRD or a Super-TRD parent, or the PR targets a Super-TRD branch and is one child's sub-TRD PR.
- Doc mode: a `Docs - <Title>` PR from a `docs-<context>` branch to `main`. It has no issue, no TRD, no milestone, and no project-board item; do not flag their absence (`docs/collab/code_review.md` § Doc and skills PRs).

## When not to use

- Session notes, status, or Collaboration Reports - those go on the **issue**.
- Implementing or fixing the PR - the author does that.
- Merging a PR, on any base. Only the maintainer merges.
- Reviewing a second child of the same Super-TRD. Re-review only the PR you already reviewed.
- Promoting proto onto trunk.

## Canonical source

- `docs/collab/code_review.md`
- `docs/collab/process.md`
- `docs/core/code_style.md`
- `docs/collab/binding.md`

## Inputs

PR number. Mode (Prototype | Release | Doc). Prototype: the RFP issue and its cited distillation sections. Release: the TRD (§3, §4, §5), and the reference prototype from its §7 row (tags or pre-release, or `None`). For a sub-TRD PR: the child TRD only. For the final Super-TRD review: the parent TRD and the child set. Binding for the proto branch name. The expected PR base (`main`, proto, or the Super-TRD branch).

## Procedure

1. `gh pr view <n> --json number,headRefName,baseRefName,files` for head, base, and files. Confirm the PR is GitHub-linked to its authorizing issue and is not on a milestone. A Doc PR has no authorizing issue; a missing issue, board item, or `Closes` on it is not a finding. A sub-TRD PR whose base is not the Super-TRD branch is a blocking finding: do not review it as the parent PR, and do not merge it. A Super-TRD PR whose base is not `main` is the same kind of finding.
2. Read the style guide and the `tiferet-code-<component>` skill for each component the PR touches. Style is checked first and is never waived: exactly one empty line between artifacts, artifact order preserved (an out-of-order artifact needs an order-preserving mechanic, never a reorder), including code examples in docs and skills. Import groups are part of that floor. `# ** core` is the Python standard library only (`abc`, `typing`, `re`, `uuid`). `# ** infra` is third-party packages only (boto3 or other AWS libraries, Flask, FastAPI, Pydantic, pytest) - not the standard library, not this application. `# ** app` is this application's own imports only, including relative imports. Order stays core, then infra, then app. Omit an empty group. A misplaced import is a blocking style finding. An acceptance criterion does not waive it.
3. Check the rest of the shared floor in order: every AC met, tests relevant and accurate to their unit, nothing superfluous.
4. **Prototype mode:** check the RFP content (every proposal item and AC realized as written), then alignment with the vision statement and the cited distillation sections (an amendment rides in the same PR). Concept outranks artifact cataloging. Do not compare to `main`. Skip Suggested TRD slicing.
5. **Release mode:** artifact fidelity is the primary lens. Law: `docs/collab/code_review.md`. For every artifact TRD §3 and §4 name, when §7 records a reference prototype, compare against that freeze-point tag and, read-only, against the prototype branch: `git fetch origin <proto-branch> --tags`, then `git diff <reference-tag>..HEAD -- <path>`, `git show <reference-tag>:<path>`, `git diff origin/<proto-branch>..HEAD -- <path>`, and `git show origin/<proto-branch>:<path>`. Do not check the branch out, merge it, cherry-pick it, or copy files from it. With §7 `None`, §3 and §4 are the specification; do not browse proto to fill a blank. A hotfix is the hotfix TRD only. A deviation on a named artifact is a finding even when trunk looks cleaner; a real improvement goes through a TRD amendment. A sub-TRD review is that child only. The final Super-TRD review is the combined diff to `main`, the parent TRD, the proto baseline, and cross-child consistency. Verdict only on that PR.
6. Sort findings: style violation (blocking), wrong PR base (blocking), AC fail, test defect, superfluous, artifact deviation (release, blocking), concept deviation (prototype, blocking), name or placement note (prototype, non-blocking), out of scope.
7. Show the findings and a proposed verdict to the human. Wait for the go-ahead before posting. That go-ahead is for posting, never for merging. Posting needs the go-ahead of Andrew (the maintainer) or Major.
8. Post **one** consolidated review (`path` + `position`). The first line is exactly `Verdict: Approve` or `Verdict: Changes requested`. Then the findings summary, then your own attribution per `docs/collab/process.md` § Attribution (your own `Co-Authored-By`, or `- <agent>@<platform> via <account>` on a shared bot account). Never another agent's identity. Line comments only on lines in the PR diff; whole-file or whole-package comments go in the body. When you share the author's GitHub token, GitHub rejects `--approve` and `--request-changes`. Post the review as a comment. Do not treat a rejected API event as a failed review. The verdict line is the signal.
9. Post a short status on the authorizing issue. Doc PR: there is no issue, so the review on the PR is the status. Sub-TRD review: the child issue. Final Super-TRD review: the parent. A child's AC failure is noted on that child issue.
10. Stop. Do not merge. The maintainer squash-merges every PR, a sub-TRD PR into its Super-TRD branch included (`docs/collab/code_review.md` § Verdict and merge). For a sub-TRD PR, say in the issue status whether the merge preconditions hold: the base is the Super-TRD branch, the verdict line is `Verdict: Approve`, no blocking finding is unresolved, and the PR-body AC checkboxes are checked. Merge readiness keys off the verdict line plus the AC checkboxes, not off `--approve`.

## Outputs

- One PR review (diff comments + body + verdict line) on the **PR**.
- A short status on the **issue**. Nothing else on the PR.
- No merge. The maintainer merges.

## Guardrails

- Never merge, on any base. Never tag, bump the version, mint a freeze, or create or close a milestone (`docs/collab/process.md` § Agent guardrails).
- Never lower a style or ordering finding to keep a review moving.
- Never proto → trunk git. Never check proto out or copy it. In release mode, only the reviewer reads proto; never tell an implementor to read it.
- Never review a prototype PR against trunk.
- Never review a second child of the same Super-TRD. Re-review messages the same reviewer.
- Check the code before claiming a behavior.
- Never commit as part of a review.
- Leave nothing behind: remove temp files, fetched artifacts, and any worktree you created (`docs/collab/process.md`). Never put temporary information on external or cloud storage unless the human explicitly authorizes it.
- Read `docs/collab/binding.md` in this repo for owner/repo and proto branch.
- On a shared bot account (`docs/collab/process.md` § Shared bot accounts), end the review with `- <agent>@<platform> via <account>`.
