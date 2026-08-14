# Code Review

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Process index: [process.md](process.md). The PR is a **review surface**. Session notes and Collaboration Reports belong on the **issue**.

## Two review kinds

### Prototype PR (RFP)

Review against the RFP proposal, acceptance criteria, and cited distillation sections. Do not review against trunk. Do not ask the author to match `main`.

### Trunk PR (reconstruction or hotfix)

Primary criterion is the TRD Acceptance Criteria (each child TRD, for a Super-TRD).

Reconstruction review **may** glance at proto only for artifacts **named in the frozen catalog / TRD AC**. That is measurement, not a merge source. Never recommend "make trunk match proto" as a general rule. An "ahead" trunk (more correct than proto) is kept.

Hotfix review is against the hotfix TRD only. Proto is not consulted.

If there is no TRD and no RFP (Doc/skills PR), review the diff against [process.md](process.md) vocabulary and the stated PR intent.

## Method (diff comments)

1. Establish PR number, head, base, files: `gh pr view <n> --json number,headRefName,baseRefName,files`.
2. For reconstruction measurement only: `git fetch origin <proto>` from [binding.md](binding.md), then `git diff origin/<proto>..HEAD -- <path>` restricted to AC-named artifacts.
3. Classify: **AC fail** (actionable), **behind proto on a named artifact** (actionable only if it is also an AC fail or the freeze named that artifact), **ahead** (note once, do not revert), **out of scope** (no comment).
4. Line-specific items → inline review comments on a line in the PR diff. Structural / whole-file items → the review body.
5. Present findings to the human and wait for go-ahead before posting.
6. One consolidated review via the reviews API (`path` + `position`, not `line`). Include conversation link and `Co-Authored-By: Oz <oz-agent@warp.dev>` in the review body.

Do **not** put implementor session notes, conversation-only logs, or Collaboration Reports on the PR.

## Guardrails

- Actionable only. A noisy review is worse than a short one.
- Never recommend proto → trunk git.
- Never recommend reverting trunk that is ahead of proto.
- Verify behavior in code before claiming it.
- Attribution on the review body.
- Never commit or merge as part of a review.
