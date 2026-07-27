---
name: tiferet-super-trd-reviewer
description: Review a Super-TRD combined PR after all child sub-issues are closed. Primary criterion is always the Acceptance Criteria of the child TRDs — verify named artifacts exist exactly as specified. The prototype branch (origin/v2.x-proto) is optional context restricted to AC-referenced artifacts only. Read after tiferet-super-trd identifies your role as REVIEWER.
---

# Tiferet Super-TRD — Reviewer

## When to use
Read this after `tiferet-super-trd` identifies your role as **REVIEWER**. Trigger: Super-TRD project status is In Progress **and** all child GitHub sub-issues are closed. This combination means the Implementor has finished all children on the combined PR branch and the PR is ready for final review.

**Guardrail:** For any Super-TRD PR, read this skill before starting. The `tiferet-pr-code-review` skill provides diff mechanics and comment-posting API that serve the AC-first analysis below — those mechanics do not replace it.

Canonical source of truth:
- `.handoff/trd-authoring-implementation-process.handoff.md` §2.5 (live process authority)

## Review procedure

### 1. Establish inputs
```bash
gh pr view <pr-number> --repo greatstrength/tiferet --json number,headRefName,baseRefName,files
git fetch origin v2.x-proto
```

Collect the list of changed files and the PR head commit SHA.

### 2. AC-first verification (primary criterion)

The primary review criterion is always the **Acceptance Criteria of each child TRD**. For every child TRD:
1. Read the child TRD's §5 (Acceptance Criteria).
2. Identify the named artifact each AC line asserts: section header, constant name, factory function, method, count.
3. Locate that artifact in the code.
4. Verify the binary assertion — the AC line is either true or false; no interpretation required.

**Semantic subgroup structure is part of the checklist.** If the AC asserts `# *** constants (ids)` exists with 41 entries, verify the exact section label and entry count. A flat `# *** constants` block where subgroups are asserted is a finding.

Report every AC line that fails as a separate finding. An AC line that passes requires no comment.

### 3. Optional prototype branch context (restricted scope)
A diff against `origin/v2.x-proto` is **optional additional context** for parity measurement only. When used:
- Restrict the study area to artifacts **named in the AC** only. Do not report diffs outside the AC-referenced artifact set.
- Classify each diff: **behind** (branch missing a reference change — actionable if also an AC failure), **ahead** (branch more correct than reference — keep, note once in body).
- An "ahead" deviation is not a finding unless an AC line also fails.

Mechanics (from `tiferet-pr-code-review`):
```bash
git diff origin/v2.x-proto..HEAD -- <path>
```
Read both sides when the diff is ambiguous. Map relocated files to their counterparts.

### 4. Present findings first — wait for go-ahead
Summarize all findings to the developer and **await explicit approval before posting** anything to GitHub.

### 5. Post one consolidated review
Use the GitHub reviews API (position-based, **not** line-based — the `line` API returns 422 errors):
```bash
gh api --method POST /repos/greatstrength/tiferet/pulls/<pr-number>/reviews \
  --input review.json
```
`review.json` contains `commit_id`, `event: "COMMENT"`, a global `body`, and a `comments[]` array using `path` + `position` (not `line`). The global body must include a `Co-Authored-By: Oz <oz-agent@warp.dev>` line and your Warp conversation link.

## Post-review actions

After posting the review:
1. **Set the Super-TRD GitHub project status to In Progress.** This is the explicit signal to the next agent that it is the **Closer**. Do **not** set it to In Review — returning to In Progress is the Closer's cue.
2. **Update `.handoff/ddd-parity-agent-workflow.handoff.md`**: session log, sub-issue state rows, detail blocks, and §6 parent tracking.

The Reviewer does **not** close the Super-TRD issue. Only the Closer does.

## Actionable findings only
Comment only on AC failures and behind-diffs for AC-referenced artifacts. Do not comment on:
- Acknowledged out-of-scope differences
- Code style that already matches standards
- Cases where the branch is more correct than the reference (note once in body, never recommend reverting)

Include `Co-Authored-By: Oz <oz-agent@warp.dev>` in the review body.
