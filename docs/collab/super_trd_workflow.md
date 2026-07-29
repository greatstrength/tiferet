# Super-TRD Workflow

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet

## Purpose and Scope

A **Super-TRD** is an oversized issue (XL or above) decomposed into sequenced child sub-issues, all implemented on a **single combined feature branch** named after the parent issue. This document is the canonical reference for the full Super-TRD execution workflow — from branch creation through final merge and cleanup.

This document supersedes the process authority previously held by `.handoff/trd-authoring-implementation-process.handoff.md` §2.3–2.6. That handoff remains as a historical archive and session log.

## Single-Branch Strategy

All child implementations land on the same feature branch, cut from `main` at the start of the Starter session and named `<parent-issue-number>-<slug>` (e.g. `930-assets-error-id-migration`). The branch is not merged until all children are complete and the PR is approved. This keeps the full migration atomic and avoids cross-branch dependency noise between sequenced children.

## Role Overview

| Role | Trigger |
|---|---|
| **Starter** | No feature branch exists yet |
| **Implementor** | Branch exists; active child is In Progress, or In Review with unresolved PR comments |
| **Reviewer** | All children closed; no unresolved PR comments on the open PR |
| **Closer** | All children closed; unresolved PR review comments exist on the open PR |

To self-identify your role, read `tiferet-super-trd` and evaluate its state machine. Then follow the pointer to the matching role skill.

## State Machine

```
Parent status = Done?
  └─ Yes → Exit. Nothing to do.

All children closed?
  └─ No → Does the feature branch exist?
           ├─ No  → STARTER → read tiferet-super-trd-implementor
           └─ Yes → Is the active child's status "In Review"?
                    ├─ Yes → Does the PR have unresolved review comments?
                    │        ├─ Yes → IMPLEMENTOR (address comments) → read tiferet-super-trd-implementor
                    │        └─ No  → ASK HUMAN: await signal before proceeding
                    └─ No (In Progress) → IMPLEMENTOR → read tiferet-super-trd-implementor
  └─ Yes → Does the PR have unresolved review comments?
           ├─ Yes → CLOSER → read tiferet-super-trd-closer
           └─ No  → REVIEWER → read tiferet-super-trd-reviewer
```

**Active child** = the lowest-numbered open sub-issue whose project status is In Progress or In Review. The human developer typically names it explicitly; if not, infer from the sub-issue list.

## Starter Responsibilities and PR Gate

When the Starter has no feature branch yet:

1. **Cut the feature branch** from `main`:
   ```bash
   git checkout main && git pull origin main
   git checkout -b <parent-issue-number>-<slug>
   ```
2. **Set the first child sub-issue to In Progress** on the project board. Do **not** manually set the Super-TRD parent — GitHub automation handles the parent lifecycle.
3. **Implement and test** the first child on the feature branch.
4. **Commit** the changes and **stop** — do not push or open a PR without explicit human approval.
5. After the developer reviews the commits and signals approval, **push the branch** and **open the PR** targeting `main`.

**Note:** The Starter does not manually set the Super-TRD parent status. GitHub automation sets the parent to **In Progress** when the PR is created and linked (`Closes #<parent>`) and the first sub-issue moves to In Review — this is the official project kickoff.

## PR Body as Full Template — Starter-Gate Requirement

The PR body must be written by the **Starter** and must cover **all children up front**:

- A **Changes** sub-section and **Acceptance Criteria** sub-section for every child, in order.
- Pending children use **unchecked AC boxes** (e.g. `- [ ] AC line`).
- The `Closes #<parent-issue-number>` line in the PR body's Related Issues section.

As each child is implemented and pushed, the active Implementor:
- **Checks off that child's AC rows** (changes `- [ ]` to `- [x]`).
- Marks the Changes section with ✅.
- Adds its bullet list of changes for that child.

The `Closes` line must never be touched after PR creation. A PR body that covers only Child 1 forces subsequent Implementors to invent the format, introducing inconsistency — this is a **Starter-gate requirement**, not a post-hoc best practice.

## Post-PR Protocol (Starter — First PR Creation)

After pushing the branch and opening the PR:

1. **Set the child sub-issue to In Review** on the project board.
2. **Add the PR to the project board** as a linked item.
3. **Post an implementor comment** on the PR as the first comment. The comment must:
   - Include your Warp conversation link (`https://app.warp.dev/conversation/...`).
   - State that this conversation served as the Implementor for the named sub-issue.
   - List only activities within the scope of the implemented work (read/confirm, implement, validate, commit).
   - Be concise — no process discussions, no out-of-scope context.

The conversation link belongs in a **PR comment**, never in the PR body.

## PR→Issue Linking Convention

The PR body's **`Closes` reference must point to the Super-TRD parent only** (e.g. `Closes #930`). Child sub-issues are closed **manually** at the developer's direction after each child's changes are approved — never via PR auto-close.

The `Closes #<parent-issue-id>` line is written once at PR creation and **must never be changed** by any subsequent Implementor session. Do not add `Closes #<child>` lines. When updating the PR body to reflect new child completions, leave the `Closes` line untouched and update only prose sections (Summary, Changes, Acceptance Criteria).

## Implementation Continuation — PR-Already-Open Procedure

When implementing a child on a Super-TRD whose PR is **already open** (Starter has previously pushed the branch and opened the PR):

1. **Implement and test** the child on the existing feature branch.
2. **Commit** the changes.
3. **Push** to origin.
4. **Set the child sub-issue to In Review** on the project board.

**Skip** all other Starter-gate steps: do not create a new PR, do not add the PR to the project board again, and do not post an implementor comment unless the developer explicitly requests one.

## Implementor Comment Convention — Same-Session Continuation

The "skip unless explicitly requested" guidance applies when a **different** Implementor agent takes over a PR already in flight. When the **same session** continues to implement multiple children, a per-child implementor comment is appropriate — each comment contextualizes the distinct scope of work and provides a durable per-child record.

## Orienting on Resume — Identifying Active Work

When spun up against an in-flight Super-TRD (branch already exists, some children may be complete):

1. **Read the Super-TRD parent issue** to understand the full child sequence and which children are complete vs. pending.
2. **Identify the active child** — the lowest-numbered open sub-issue whose status is In Progress or In Review. The developer typically names it; if not, infer from the sub-issue list.
3. **Determine current state** using two signals:
   - `git log` / `git status` on the feature branch — confirms which child commits are present and whether uncommitted changes exist.
   - **PR comments** on the linked PR — read if the sub-issue is In Review, since unresolved review comments are actionable work.
4. **Act based on sub-issue status:**
   - *In Progress* — implementation has not yet been pushed. Proceed with implementation.
   - *In Review* — changes are on origin and the PR is open. Fetch and address all review comments before proceeding.

## Impact Analysis for In-Flight Sibling Branches

Before starting a child's implementation, verify the current state of the **in-flight feature branch** — not only recently merged PRs. When a sibling child has just been implemented, confirm that:

- The code on the branch reflects the sibling's changes.
- The current child's TRD prerequisites (listed in its §7) are satisfied on the branch.
- Any constants, factories, or imports the current child depends on already exist on the branch.

Use `git log` and direct file inspection to confirm. If a prerequisite is listed as "Not yet started" in the TRD but is now complete on the branch, treat it as satisfied and proceed.

## Child TRD Prerequisite Table Update Recommendation

When a child TRD's §7 Prerequisites table lists a sibling child as "Not yet started," update the table to reflect "Complete (on branch)" once the sibling lands, or add an implementation note confirming readiness via `git log`. This eliminates ambiguity for subsequent Implementors who must mentally translate stale prerequisite language.

## Project Status Lifecycle

### Per-child status updates

- When a child's work begins: set the **child sub-issue** to **In Progress**.
- After the child's implementation is approved and closed: set it to **Done**.

### Super-TRD parent status

Agents must **not** manually set the Super-TRD parent to In Progress. GitHub automation fires that transition when the PR is linked (`Closes #<parent>`) and the first sub-issue moves to In Review.

| Phase | Parent status | Trigger |
|---|---|---|
| Branch cut; child 1 begins | *(unchanged)* | Starter sets only the child sub-issue to In Progress |
| PR created + sub-issue set to In Review | **In Progress** | GitHub automation (PR linked + sub-issue → In Review) |
| Each subsequent child approved | **In Progress** | Automation keeps parent In Progress; agents do not touch it |
| All children closed (pre-review) | **In Progress** | Remains until Reviewer posts review |
| Reviewer posts review | **In Progress** | Reviewer resets to In Progress as the Closer's cue |
| PR merged | **Done** | GitHub auto-closes via `Closes` line |

The Super-TRD must **not** move to **In Review** until every child sub-issue is closed; only the Reviewer sets it — but only briefly: after posting the review, the Reviewer resets it to **In Progress** as the explicit signal to the Closer.

## Sub-Issue Completion Procedure

Whenever an Implementor is asked to mark a child sub-issue as complete:

1. Close the child sub-issue on GitHub and set its project status to **Done**.
2. Rename its `.trd/` file to carry a `.complete.md` extension:
   ```bash
   git mv .trd/<name>.md .trd/<name>.complete.md
   ```
   **Fallback:** If `.trd/` is listed in `.gitignore` (exit code 128: "not under version control"), use plain `mv` instead — the rename is still a meaningful local signal regardless of whether it is tracked.
3. Perform the rename **together** with the sub-issue closure — do not defer it.
4. Preserve the full existing filename and only append the extension: e.g. `m30_931_assets-error-id-migration__S_2_P0.md` → `m30_931_assets-error-id-migration__S_2_P0.complete.md`.

## Review Procedure

### Trigger condition

All child GitHub sub-issues are closed **and** the PR has no unresolved review comments → **REVIEWER** role.

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

**Semantic subgroup structure is part of the checklist.** If the AC asserts `# *** constants (ids)` exists with N entries, verify the exact section label and entry count. A flat `# *** constants` block where subgroups are asserted is a finding.

Report every AC line that fails as a separate finding. AC lines that pass require no comment.

### 3. Optional prototype branch context (restricted scope)

A diff against `origin/v2.x-proto` is **optional additional context** for parity measurement only. When used:

- Restrict the study area to artifacts **named in the AC** only. Do not report diffs outside the AC-referenced artifact set.
- Classify each diff: **behind** (branch missing a reference change — actionable if also an AC failure), **ahead** (branch more correct than reference — keep, note once in body).
- An "ahead" deviation is not a finding unless an AC line also fails.

```bash
git diff origin/v2.x-proto..HEAD -- <path>
```

### 4. Present findings first — wait for go-ahead

Summarize all findings to the developer and **await explicit approval before posting** anything to GitHub.

### 5. Before-posting checklist

Before posting the review to GitHub, confirm **all three** of the following are present in the global review body — all are mandatory, not afterthoughts:

- [ ] **Conversation link** (`https://app.warp.dev/conversation/...`) — the durable record that lets the Closer and future maintainers trace every finding back to its reasoning.
- [ ] **Findings summary** — all AC failures and actionable behind-diffs listed clearly.
- [ ] **`Co-Authored-By: Oz <oz-agent@warp.dev>`** line.

### 6. Post one consolidated review

Use the GitHub reviews API (position-based, **not** line-based — the `line` API returns 422 errors):

```bash
gh api --method POST /repos/greatstrength/tiferet/pulls/<pr-number>/reviews \
  --input review.json
```

`review.json` contains `commit_id`, `event: "COMMENT"`, a global `body`, and a `comments[]` array using `path` + `position` (not `line`).

## Reviewer AC Update Authority

When the Reviewer identifies a discrepancy between the implemented code and an AC line, it must first determine whether the deviation is **unintentional** (a genuine implementation gap — actionable finding) or **intentional** (a deliberate naming or design decision made by the developer after the TRD was authored).

If the developer confirms the deviation was **intentional** and approves updating the AC:

1. Edit the relevant AC line(s) in the `.trd/` source file — covering every section that names the artifact: §1 Overview, §4 Detailed Requirements, §5 Acceptance Criteria, and §6 NFR as applicable.
2. Publish the updated body to the corresponding GitHub issue: `gh issue edit <n> --repo greatstrength/tiferet --body-file <path>`.
3. Note the update in the PR review body under a dedicated **"Reviewer AC Updates"** section, with a one-sentence rationale for each change. State that the updates were applied before the review was posted so the Closer sees only passing AC.
4. Do **not** leave the old AC language in the issue or the `.trd/` file — the updated TRD is the new source of truth. Do not flag the deviation as an open finding in the review.

This authority belongs to the **Reviewer**, not the Implementor. An Implementor that discovers a post-authoring naming change should note it in its PR comment ("AC deviation") but defer the AC update to the Reviewer, who evaluates it in the context of the full branch before deciding whether it is intentional.

## Post-Review Actions

After posting the review:

1. **Set the Super-TRD GitHub project status to In Progress.** This is the explicit signal to the next agent that it is the **Closer**. Do **not** set it to In Review — returning to In Progress is the Closer's cue.
2. **Update `.handoff/ddd-parity-agent-workflow.handoff.md`**: session log, sub-issue state rows, detail blocks, and §6 parent tracking.

The Reviewer does **not** close the Super-TRD issue. Only the Closer does.

## Closing Procedure

### Trigger condition

All child sub-issues are closed **and** the PR has unresolved review comments → **CLOSER** role.

### 1. Retrieve all conversation links before drafting anything

Before drafting any part of the Collaboration Report, explicitly:

1. Retrieve all PR comments: `pr-comments` skill or `gh api /repos/greatstrength/tiferet/pulls/<n>/reviews` + `/comments`.
2. Extract every `https://app.warp.dev/conversation/...` link present — one per Implementor comment, one in the Reviewer's review body.
3. Search each conversation for the AI↔Human exchange.
4. Only then begin drafting any part of the Collaboration Report.

A collaboration log written without consulting these conversations will be incomplete or inaccurate.

### 2. Address review comments

```bash
git checkout <branch-name> && git pull origin <branch-name>
```

Read every unresolved comment. Address each one in code. Push:

```bash
git push origin <branch-name>
```

### 3. Post a PR comment (optional for trivial fixes)

For non-trivial fixes, post a comment on the PR noting:
- What was addressed (scope-of-work bullets, no out-of-scope context).
- Your Warp conversation link (`https://app.warp.dev/conversation/...`).

For trivial fixes (e.g. a single annotation or comment-only change), the commit message on the push is sufficient — omit the PR comment.

### 4. Await user PR approval and merge

Stop here and wait for the developer to approve and squash-merge the PR.

### 5. Post-merge cleanup

```bash
git checkout main && git pull origin main
git branch -d <branch-name>
```

### 6. Post the Collaboration Report

Use the `tiferet-collab-report` skill to post a Collaboration Report as a comment on the Super-TRD parent issue. Consult all implementor and reviewer Warp conversation links extracted in step 1.

### 7. Parent TRD rename after merge

Rename the Super-TRD parent's `.trd/` file to carry the `.complete.md` extension:

```bash
git mv .trd/<parent-name>.md .trd/<parent-name>.complete.md
git commit -m "Docs – rename Super-TRD parent TRD to .complete.md after merge"
```

**Fallback:** If `.trd/` is git-ignored (exit code 128), use plain `mv` instead.

### 8. GitHub issue and project status verification

For Super-TRD PRs that include `Closes #<n>` in the body, GitHub auto-closes the parent issue on squash-merge and typically sets project status to Done.

- Check issue state: `gh issue view <n> --repo greatstrength/tiferet --json state`
- If already closed: **skip** manual close.
- If not closed: `gh issue close <n> --repo greatstrength/tiferet`
- Check project status in the GitHub UI or via GraphQL; if not Done, set it manually and set the End date via `gh project item-edit`.

### 9. Update the handoff

Update `.handoff/ddd-parity-agent-workflow.handoff.md`: session log, §6 parent tracking (all sub-issues `close: done`), and Super-TRD entry in the parents table (status → closed).
