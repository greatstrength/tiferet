# Main - Trunk Strand

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

[process.md](process.md) is the index. This page is trunk: the history a release can stand on, as an **individual** lands one TRD.

## What trunk will accept

Three things, and only three:

- **Reconstruction TRDs** that implement a **frozen** catalog. They name artifacts. They do not say "copy from proto," and they do not send you to the proto branch. They cite an existing freeze id in §7.
- **Hotfix TRDs** for small mechanical defects already understood on trunk. Prototype is not consulted. There is no freeze id.
- **Doc / skills PRs** - see [doc.md](doc.md). No issue, no TRD.

Nothing from prototype lands on trunk as git. If you find yourself reaching for a merge from proto, stop. The catalog is how that work crosses.

You do not open the trunk milestone or mint the freeze id. If a reconstruction TRD has no freeze id, do not implement it - the specification is incomplete.

## Milestones

The title is the version number. Nothing else.

- Format: `v<version>`
- Examples: `v2.0.1`, `v2.1.0`

Patch versions are welcome. New trunk milestones do **not** use `bN`. Older titles such as `v2.0.0b3` mean what they meant when they were created; we are not going back to rename them.

You do not assign your issue to a milestone, close the milestone, or publish the GitHub Release.

Every issue goes on the **Tiferet Framework** project. A Doc PR has no issue, so it has no board item. What the fields mean is in [project_fields.md](project_fields.md). The ids for *this* repo are in [binding.md](binding.md).

## Issue titles

```
<Component/Assemblage> - <Brief Capitalized Title>
```

Component/Assemblage is the majority of the ten core packages (assets, blueprints, contexts, di, domain, events, interfaces, mappers, utils, repos), or `Config` when the change is configuration, or `Tests` when it is only tests, or a domain assemblage when one concept spans many packages.

Five to eight words after the hyphen is about right. `Domain - Feature Model Condition Evaluation` and `Utils - SQLite Client Connection Lifecycle` are the tone.

## Status on the board

- **Ready** - the issue exists and has been triaged (Priority, Size, Estimate).
- **In Progress** - someone cut a branch or otherwise started. Set the Start date.
- **In Review** - the PR is open. If a review comment needs code, come back to In Progress, then return to In Review when you push.
- **Done** - merged, *and* for a standalone TRD the Collaboration Report is on the issue. Set the End date, then close.

New issues start at Ready. If one issue is waiting on another, use blocked-by. Do not park new work in Backlog just to show a dependency. A Super-TRD parent is the exception: it starts at Backlog, then moves Ready, In Progress, In Review, and Done ([process.md](process.md#super-trd)).

## Individual path: one TRD

Use this when you are landing one hotfix or one standalone reconstruction.

1. Write the TRD ([tech_requirements.md](tech_requirements.md)). Reconstruction cites an existing freeze id in §7. A hotfix says it is a hotfix and skips the freeze. Wire GitHub blocked-by from §7.
2. Open the issue. Cut `<issue-number>-<lowercase-hyphenated-title>` from `main`.
3. Implement and test. Open a PR targeting `main`, title `<Component/Assemblage> - <Plain Title> (#issue)`, **GitHub-linked** to that TRD. `Closes #<issue>` is allowed on trunk. The body lists the TRD's acceptance criteria as checkboxes, all unchecked. Do not add the PR to the milestone.
4. After the PR opens, and again after you address PR feedback, post a short status on the **issue**.
5. After the squash-merge: Collaboration Report on the issue, Status Done, End date. Rename the `.trd/` file to `.complete.md`. Port to proto only if a human asks.

## Super-TRD as a shape

A Super-TRD is parent plus children, child size at most Medium. The TRD *genre* is in [tech_requirements.md](tech_requirements.md). The branch rule is in [process.md](process.md#super-trd).

The parent is a grouping and a blocking gate. It has no branch and no PR of its own. Each child is its own PR, cut from `main` and targeting `main`. A child cannot be started until the parent is In Progress.

If you are asked to implement **one child**: confirm that the parent is In Progress and that every blocker of this child, a sibling, a standalone TRD, or other outside work, is already squash-merged to `main`. If not, do not cut a branch and do not start. See [Cross-boundary blockers](process.md#cross-boundary-blockers). Otherwise cut `<child-issue>-<slug>` from `main`. Open a PR targeting `main`. Body: `Closes #<child>` and `Refs #<parent>`. Never put `Closes`, `Fixes`, or `Resolves` on the parent. Verify `gh pr view <N> --json baseRefName`. Set the child to In Review. Short status on the child issue. Do not write a Collaboration Report. The child closes when its PR is squash-merged to `main`, and its Status goes to Done.

Once every child is Done, the parent goes In Review for a final review of the Super-TRD as a whole. After it passes, the parent goes Done. The parent has no PR, so the project administrator closes the parent issue after its final review, once every child issue is closed. The parent gets no Collaboration Report.

When the child issues allow concurrency, an agent may run the fan-out. Review and squash-merge are outside these contribution guidelines.

## Reviewing trunk

A trunk PR is reviewed on the Release lens. Code style comes first and is never waived. Then artifact fidelity: every artifact the TRD names in section 3 and section 4 is measured against the reference prototype recorded in section 7, and read-only against the prototype branch, or against the TRD alone when there is no prototype. A deviation on a named artifact is a finding even when trunk looks cleaner. A real improvement goes through a TRD amendment before merge. Only the review reads proto; the implementor works from the TRD. Reading proto is `git show` / `git diff` of a fetched ref, never a checkout, copy, or merge.

A hotfix is reviewed against the hotfix TRD. Proto has nothing to say about it.

Review and squash-merge are outside these contribution guidelines. The first line of the posted review is `Verdict: Approve` or `Verdict: Changes requested`. The implementer does not review and does not merge. Anything that points at a diff stays on the PR. Short status stays on the issue. [code_review.md](code_review.md) is the standard.
