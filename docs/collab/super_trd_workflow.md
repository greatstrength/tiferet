# Super-TRD Workflow

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Trunk-only. Process index: [process.md](process.md). Path choice: [main.md](main.md). TRD format: [tech_requirements.md](tech_requirements.md).

A Super-TRD is an XL+ story with a seam, decomposed into sequenced child sub-issues, implemented on **one** feature branch named for the parent. Prototype work does not use this workflow.

## Single-branch strategy

Cut from `main` at the start of the Starter session: `<parent-issue-number>-<slug>`. Not merged until combined review is done and the human squash-merges.

## Roles

| Role | Trigger |
|---|---|
| **Starter** | No feature branch yet |
| **Implementor** | Branch exists; active child is In Progress, or In Review with unresolved **PR diff** comments |
| **Reviewer** | Every child is In Review (implementation log posted); no unresolved PR review comments yet |
| **Closer** | Combined review has been posted and the PR has unresolved diff comments — or review had no findings and merge already happened (addenda + parent report) |

Self-identify with `tiferet-super-trd`, then the matching role skill.

**Active child** = lowest-numbered open sub-issue whose status is In Progress or In Review. Prefer the name the human gives.

## State machine

```
Parent status = Done?
  └─ Yes → Exit.

Every child In Review with an implementation-log report?
  └─ No → Does the feature branch exist?
           ├─ No  → STARTER
           └─ Yes → Active child In Review with unresolved PR diff comments?
                    ├─ Yes → IMPLEMENTOR (address comments)
                    └─ No  → IMPLEMENTOR (implement / push / log)
  └─ Yes → Unresolved PR review comments from the Reviewer?
           ├─ Yes → CLOSER (code fixes)
           └─ No  → Has the Reviewer posted the combined review?
                    ├─ No  → REVIEWER
                    └─ Yes → CLOSER (addenda after merge)
```

Children are **not** closed before combined review. Done waits for the verification addendum.

## Starter

1. `git checkout main && git pull origin main && git checkout -b <parent-issue>-<slug>`
2. Set **child 1** to In Progress. Do not set the parent — automation does that when the PR is linked (`Closes #<parent>`) and the first child moves to In Review.
3. Implement and test child 1. Commit. **Stop** — do not push or open a PR without human approval.
4. After approval: push and open the PR targeting `main`.

### PR body (Starter-gate)

Cover **all** children up front: Changes + Acceptance Criteria per child, unchecked boxes for later children, `Closes #<parent>` once. Later Implementors check off AC and add bullets. Never edit the `Closes` line. Never add `Closes #<child>`.

### After the first PR opens

1. Set child 1 to In Review. Add the PR to the project board.
2. On the **child issue** (not the PR): session note (conversation link + in-scope activities) and a Collaboration Report labeled **implementation log**.

## Later children (PR already open)

Implement, commit, push, set that child to In Review, check off that child's AC on the PR. On the **child issue**: session note + implementation-log report. Do not open a second PR.

Same-session continuation still posts a **per-child** issue comment so each child's record is durable.

## Orienting on resume

1. Read the parent issue (sequence, freeze id, which children have logs).
2. Identify the active child.
3. `git log` / `git status` on the branch. Read **issue** threads for session notes. Read **PR** reviews only for unresolved diff comments.
4. In Progress → implement. In Review with PR diff comments → address those. In Review with only an implementation log → wait for the human or the next child.

Before starting a child, confirm sibling landings on **this branch** (not only `main`). If §7 still says a sibling is "Not yet started" but the commit is on the branch, treat it as satisfied and update the table.

## Project status

| Phase | Parent | Child |
|---|---|---|
| Branch cut | unchanged | child 1 → In Progress |
| PR linked + first child In Review | In Progress (automation) | In Review |
| Later children | In Progress (do not touch) | In Progress then In Review |
| Combined review posted | In Progress (Reviewer cue for Closer) | still In Review |
| PR merged + addenda | Done (automation via `Closes`) | Done after addendum |

## Reviewer

Trigger: every child is In Review with an implementation log; no unresolved PR review comments yet.

1. `gh pr view` for files and head SHA.
2. For every child TRD §5: named artifact, binary pass/fail. Subgroup labels and counts are part of the checklist.
3. Optional proto measurement: only AC-named artifacts. Behind + AC fail = finding. Ahead = note once, do not revert. Never "make trunk match proto."
4. Show findings to the human; wait for go-ahead.
5. Post **diff findings** as one PR review (`path` + `position`). Review body: findings summary + `Co-Authored-By`. Conversation link and narrative go on the **parent issue**. Child AC failures are also noted on that **child issue**.
6. If an AC deviation is intentional and the human agrees, the Reviewer updates the `.trd/` file and the GitHub issue body before posting, and records "Reviewer AC Updates" on the parent issue. Implementors note deviations; they do not edit AC.

## Closer

1. Address every unresolved **PR** review comment in code. Push.
2. Non-trivial fix: session note on the **parent issue** (not the PR), with conversation link.
3. Wait for the human to squash-merge.
4. `git checkout main && git pull && git branch -d <branch>`.
5. On each child issue: **verification addendum** (pass / amended AC / follow-up). Then close the child and set Done. Rename the child `.trd/` to `.complete.md` (`mv` if gitignored).
6. Parent Collaboration Report on the **parent issue** — roll-up that links child logs and addenda. Consult those issue threads (not only the PR) before drafting.
7. Rename the parent `.trd/` to `.complete.md`. Verify `Closes #<parent>` closed the parent; close manually only if automation did not.

## Comment surfaces

- **PR:** description, AC checkboxes, `Closes`, inline/review-body diff comments.
- **Child issue:** session notes, implementation log, AC-failure notes, verification addendum.
- **Parent issue:** Reviewer narrative, closer session note, parent roll-up report.
