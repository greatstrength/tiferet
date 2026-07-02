# Code Review — Agent-Assisted PR Review

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet

## Purpose

The Code Review process uses an AI agent to review an open pull request by comparing the contents of its feature branch against a prototype **"source of truth"** branch, then posting only the **actionable** discrepancies back to the PR as review comments. It complements — it does not replace — human review: the agent performs the mechanical, exhaustive file-by-file comparison and drafts precise, well-placed comments for a human to act on and merge.

This process emerged from parity work, where a feature branch is meant to bring `main` (or another base) into line with a prototype branch (e.g., `v2.0-proto`). The agent's job is to find where the branch and the source of truth disagree **in ways that need action** — and to ignore the differences that don't.

## When to Use

Use this process when:

- A PR claims to bring a branch toward parity with a prototype/source-of-truth branch, and you want to verify that claim file by file.
- You want a thorough, line-anchored review of a PR against a known-good reference.
- A human asks an agent to "review PR #N against `<prototype>`" or to "compare the branch to the source of truth and comment."

If there is **no** prototype source of truth to compare against, say so explicitly and fall back to a standard diff-against-base review — the comparative method below does not apply.

## Inputs

Before starting, establish:

- The **PR number** and its **head (feature) branch** and **base branch** (`gh pr view <n> --json number,headRefName,baseRefName,files`).
- The **source-of-truth branch**, if one exists (e.g., `v2.0-proto`). Fetch it so the comparison uses the latest: `git fetch origin <source-of-truth>`.
- The **files changed** in the PR — these scope the comparison.

## Method

### 1. Compare each changed file against the source of truth

For every file the PR touches, diff the feature branch against the source of truth:

```bash
git diff origin/<source-of-truth>..HEAD -- <path>
```

Confirm the **direction** of every difference before drawing conclusions (`-` lines are the source of truth, `+` lines are the feature branch). When a diff is ambiguous, read the actual file on both sides — do not infer naming or intent from the diff alone. Account for files that moved (e.g., relocated tests): map each PR file to its counterpart on the source of truth even when the path differs.

### 2. Classify every discrepancy

Sort each difference into one of:

- **Behind** — the branch is missing a change the source of truth has. Actionable: align the branch.
- **Ahead** — the branch is *more* correct than the source of truth (e.g., a later naming decision). Do **not** revert it; instead flag the source of truth as the thing to reconcile.
- **Out of scope** — a real difference that belongs to other work and is already acknowledged in the PR description. Do **not** comment on these; they are noise.

Only **Behind** and **Ahead** items are actionable. Everything else is excluded.

### 3. Place comments by granularity

- **Line-specific** discrepancies (a wrong description, a stale docstring, an assertion style, a renamed symbol) → **inline review comments** anchored to the exact file and line.
- **Global / structural** discrepancies (adding or removing an entire file, package-level export structure, a missing or extra `__init__.py` / `conftest.py`, anything not tied to a single line) → the **global PR review body**.

Inline comments must anchor to a line that is part of the PR's diff against its base. If the relevant line was **not** changed by the PR (so it falls outside the diff), anchor to the nearest changed line and name the exact line in the comment text, or move the item to the global body.

### 4. Post one consolidated review

Submit a single review so the comments arrive together. Use the GitHub reviews API with the PR head commit and an array of inline comments plus the global body:

```bash
gh api --method POST /repos/greatstrength/tiferet/pulls/<n>/reviews --input review.json
```

`review.json` contains `commit_id` (the PR head OID), `event: "COMMENT"`, a `body` (the global/structural items), and a `comments[]` array where each entry has `path`, `line`, `side` (usually `"RIGHT"`), and `body`. See [commands.md](commands.md) for the surrounding `gh` operations.

## What Counts as Actionable

Comment on differences that change behavior, correctness, public API, naming consistency, or test integrity — for example:

- Stale or inconsistent naming left behind by an incomplete rename.
- Docstrings or field descriptions that disagree with the source of truth.
- Test assertions or structure that diverge from the reference in a way that changes what is verified.
- Duplicated, missing, or shadowed tests.
- Export lists or package markers that change the importable surface.

Do **not** comment on:

- Differences the PR description already declares out of scope.
- Pure formatting that already matches the project's [code style](../core/code_style.md).
- Cases where the branch is correct and the difference is the source of truth being stale — except to note, once, that the source of truth should be reconciled.

## Guardrails

- **Actionable only.** A noisy review is worse than a short one. Exclude acknowledged, out-of-scope differences.
- **Respect "ahead" branches.** Never recommend reverting a branch that is more correct than the source of truth; flag the reference instead.
- **Verify before claiming.** When a finding hinges on behavior (imports, test resolution, identity), confirm it in the code rather than asserting it.
- **Place comments correctly.** Line items inline; structural and whole-file items in the PR body.
- **Attribution.** When an AI agent authors the review, include a `Co-Authored-By:` line in the review body.
- **Never commit or merge** as part of a review unless explicitly asked — a review only comments.
