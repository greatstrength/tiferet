---
name: tiferet-super-trd-implementor
description: Implement child sub-issues on a Super-TRD feature branch. Covers both the Starter role (first child, branch creation, human gate, PR opening) and the Implementor role (subsequent children, PR-already-open procedure, addressing review comments). Read after tiferet-super-trd identifies your role as STARTER or IMPLEMENTOR.
---

# Tiferet Super-TRD — Implementor & Starter

## When to use
Read this after `tiferet-super-trd` identifies your role as **STARTER** (no branch yet) or **IMPLEMENTOR** (branch exists, child is In Progress or In Review with unresolved comments).

Canonical source of truth:
- https://github.com/greatstrength/tiferet/blob/main/docs/collab/super_trd_workflow.md

## Starter rituals (first child only)

When you are the **Starter** (no feature branch exists yet):

1. **Cut the feature branch** from `main` using `<parent-issue-number>-<slug>` (e.g. `930-assets-error-id-migration`):
   ```bash
   git checkout main && git pull origin main
   git checkout -b <branch-name>
   ```
2. **Set the first child sub-issue to In Progress** on the project board. Do **not** manually set the Super-TRD parent — GitHub automation handles the parent lifecycle when the PR is created.
3. **Proceed to implement the first child** on the feature branch (see Implementation procedure below).

## Implementation procedure

Before writing any code, read `tiferet-code-style` (mandatory every session) and the `tiferet-code-<component>` skill(s) for the layers this child touches. For multi-component children, also read `tiferet-code-architecture`.

Implement the child by working through its TRD **section-by-section**: read the child TRD's §4, match each `#### Add/Update/Remove: # *** <section> (<subgroup>)` heading to the corresponding code section, and execute the artifact table row-by-row. The child TRD is the complete and sufficient specification — execute it directly without paraphrasing.

Run tests (`pytest tests/`) after implementing. Verify the changes compile with no syntax errors.

## PR Body as Full Template — Starter-Gate Requirement

The PR body must be written by the **Starter** and must cover **all children up front**: a Changes sub-section and Acceptance Criteria sub-section for every child (in order), with unchecked AC boxes for pending children. The `Closes #<parent-issue-number>` line goes in the Related Issues section.

As each child is implemented and pushed, the active Implementor checks off that child's AC rows, marks the Changes section ✅, and adds its bullet list of changes. The `Closes` line is never touched after PR creation. A PR body that covers only Child 1 forces subsequent Implementors to invent the format — this is a **Starter-gate requirement**, not a post-hoc best practice.

## Human-in-the-loop PR gate (Starter only)

After implementing and testing the first child:

1. **Commit** the changes with a descriptive message (include `Co-Authored-By: Oz <oz-agent@warp.dev>`).
2. **Stop.** Do **not** push or open a PR without explicit human approval.
3. After the developer reviews the commit(s) and signals approval, **push the branch** and **open the PR** targeting `main`.

## Post-PR protocol (Starter — first PR creation)

After pushing and opening the PR:

1. **Set the child sub-issue to In Review** on the project board.
2. **Add the PR to the project board** as a linked item.
3. **Post an implementor comment** on the PR as the first comment. The comment must:
   - Include your Warp conversation link (`https://app.warp.dev/conversation/...`).
   - State that this conversation served as the Implementor for the named sub-issue.
   - List only activities within the scope of the implemented work (read/confirm, implement, validate, commit).
   - Be concise — no process discussions, no out-of-scope context.

The conversation link belongs in a **PR comment**, never in the PR body.

## PR→issue linking convention

The PR body's **`Closes` reference must point to the Super-TRD parent only** (e.g. `Closes #930`). Never add `Closes #<child>` lines. Rationale: one branch covers all children; the PR auto-closes the parent on merge; children are closed manually at the developer's direction.

## Closes convention — do not alter

The `Closes #<parent-issue-id>` line in the PR body is written once at PR creation and **must never be changed** by any subsequent Implementor session. Do not add child sub-issue close lines. When updating the PR body to reflect new child completions, leave the `Closes` line untouched and update only prose sections (Summary, Changes, Acceptance Criteria).

## On sub-issue completion — rename the TRD file

Whenever you are asked to mark a child sub-issue as complete, also rename its `.trd/` file to carry a `.complete.md` extension. Do this **together** with closing the sub-issue (do not defer it):

```bash
git mv .trd/<name>.md .trd/<name>.complete.md
```

Preserve the full existing filename and only append the extension.

**Fallback:** If `.trd/` is listed in `.gitignore` (exit code 128: "not under version control"), use plain `mv` instead — the rename is still a meaningful local signal regardless of whether it is tracked.

## PR-already-open procedure (subsequent children)

When you are implementing a child on a Super-TRD whose PR is **already open** (Starter has already pushed the branch and opened the PR):

1. **Implement and test** the child on the existing feature branch.
2. **Commit** the changes.
3. **Push** to origin.
4. **Set the child sub-issue to In Review** on the project board.

**Skip** all other Starter-gate steps: do not create a new PR, do not add the PR to the project board again, and do not post an implementor comment unless the developer explicitly requests one.

## Implementor comment convention — same-session continuation

The "skip unless explicitly requested" guidance applies when a **different** Implementor agent takes over a PR already in flight. When the **same session** continues to implement multiple children, a per-child implementor comment is appropriate — each comment contextualizes the distinct scope of work and provides a durable per-child record.

## Orienting on resume — identifying active work

When spun up against an in-flight Super-TRD (branch already exists, some children may be complete):

1. **Read the Super-TRD parent issue** to understand the full child sequence and which children are complete vs. pending.
2. **Identify the active child** — the lowest-numbered open sub-issue whose status is In Progress or In Review. The developer typically names it; if not, infer from the sub-issue list.
3. **Determine current state** using two signals:
   - `git log` / `git status` on the feature branch — confirms which child commits are present and whether uncommitted changes exist.
   - **PR comments** on the linked PR — read if the sub-issue is In Review, since unresolved review comments are actionable work.
4. **Act based on sub-issue status:**
   - *In Progress* — implementation has not yet been pushed. Proceed with implementation.
   - *In Review* — changes are on origin and the PR is open. Fetch and address all review comments before proceeding.

## Impact analysis for in-flight sibling branches

Before starting a child's implementation, verify the current state of the **in-flight feature branch** — not only recently merged PRs. When a sibling child has just been implemented, confirm:

- The code on the branch reflects the sibling's changes.
- The current child's TRD prerequisites (§7) are satisfied on the branch.
- Any constants, factories, or imports the current child depends on already exist on the branch.

Use `git log` and direct file inspection to confirm. If a prerequisite is listed as "Not yet started" in the TRD but is now complete on the branch, treat it as satisfied and proceed.

## PR comment retrieval — when and how

When the active sub-issue is **In Review**, retrieve all review comments before making any edits:

```bash
# Using pr-comments skill, or:
gh pr view <pr-number> --repo greatstrength/tiferet --comments
gh api /repos/greatstrength/tiferet/pulls/<pr-number>/comments
```

Read every unresolved comment. Address each one in code. Push. Mark comments resolved when available. Do **not** start the next child sub-issue until all review comments on the current child are resolved and the developer signals approval.

## Continuity across token overuse

If model degradation forces a new Implementor agent mid-review, the new agent posts a comment on the PR stating what it has done (in scope of the implemented work only), including its own Warp conversation link.

## Project status — Super-TRD parent

Agents must **not** manually set the Super-TRD parent to In Progress. GitHub automation fires that transition when the PR is linked (`Closes #<parent>`) and the first sub-issue moves to In Review. For all subsequent children, the parent status stays In Progress throughout — agents do not touch it.

Per-child status updates:
- When a child's work begins: set the child sub-issue to **In Progress**.
- After the child's implementation is approved and closed: set it to **Done**.
