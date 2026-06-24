---
name: tiferet-pr-code-review
description: Review a Tiferet pull request by comparing its feature branch against a prototype "source of truth" branch and posting only the actionable discrepancies back to the PR. Use this whenever the user asks an agent to review or compare a PR — especially "review PR #N", "compare this branch to v2.0-proto / the prototype / the source of truth", parity-verification requests, or "post code-review comments on the PR" — even if they don't say the word "review" outright. Covers the file-by-file comparison method, what counts as actionable, and where each comment goes (inline vs the global PR comment).
---

# Review a Tiferet PR Against the Source of Truth

## When to use
Use this when reviewing a Tiferet-family PR whose feature branch is meant to match or move toward a prototype **source of truth** branch (e.g., `v2.0-proto`). The agent does the exhaustive, file-by-file comparison and posts precise, well-placed comments; humans decide and merge.

If there is no source-of-truth branch to compare against, say so and fall back to a standard diff-against-base review — the comparative method here does not apply.

Canonical source of truth:
https://github.com/greatstrength/tiferet/blob/main/docs/collab/code_review.md

## Method
1. **Establish inputs.** Get the PR's head and base branches and changed files (`gh pr view <n> --json number,headRefName,baseRefName,files`). Identify the source-of-truth branch and fetch it (`git fetch origin <branch>`).
2. **Compare each changed file** against the source of truth: `git diff origin/<source-of-truth>..HEAD -- <path>`. Confirm the direction of every difference (`-` = source of truth, `+` = branch); read the file on both sides when the diff is ambiguous. Map relocated files to their counterparts.
3. **Classify** each difference: **behind** (branch missing a reference change — actionable), **ahead** (branch more correct than the reference — keep it, flag the reference to reconcile), or **out of scope** (already acknowledged in the PR description — do not comment).
4. **Place comments by granularity:**
   - Line-specific issues → **inline review comments** on the exact file/line.
   - Global/structural issues (adding or removing whole files, package exports, a missing/extra `__init__.py` / `conftest.py`) → the **global PR review body**.
   - Inline comments must anchor to a line in the PR's diff vs base; if the target line is outside the diff, anchor to the nearest changed line and name the exact line, or move it to the body.
5. **Post one consolidated review** via the reviews API with the PR head commit:
   `gh api --method POST /repos/greatstrength/tiferet/pulls/<n>/reviews --input review.json`, where `review.json` has `commit_id`, `event: "COMMENT"`, a global `body`, and a `comments[]` array (`path`, `line`, `side`, `body`). See [commands.md](https://github.com/greatstrength/tiferet/blob/main/docs/collab/commands.md).

## Actionable only
Comment on naming inconsistencies from incomplete renames, docstring/description drift, test assertions or structure that change what's verified, duplicated/missing/shadowed tests, and changes to the importable surface. **Do not** comment on acknowledged out-of-scope differences, formatting that already matches the code style, or cases where the branch is correct and the reference is stale (note that once, in the body).

## Guardrails
- Actionable only — a noisy review is worse than a short one.
- Never recommend reverting a branch that is more correct than the source of truth.
- Verify behavior-dependent findings (imports, test resolution, identity) in the code before claiming them.
- Include a `Co-Authored-By:` line in the review body when an AI agent authors the review.
- A review only comments — never commit or merge unless explicitly asked.
