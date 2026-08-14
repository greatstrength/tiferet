# Main — Trunk Strand

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

[process.md](process.md) is the index. This page is trunk: the history a release can stand on.

## What trunk will accept

Three things, and only three:

- **Reconstruction TRDs** that implement a **frozen** RFP cluster. They name artifacts. They do not say "copy from proto," and they do not send the implementor to the proto branch.
- **Hotfix TRDs** for small mechanical defects already understood on trunk. Prototype is not consulted. There is no freeze id, because there is nothing left to discover.
- **Doc / skills PRs** — see [doc.md](doc.md). No TRD.

Nothing from prototype lands on trunk as git. If you find yourself reaching for a merge from proto, stop. The catalog is how that work crosses.

## Milestones

The title is the version number. Nothing else.

- Format: `v<version>`
- Examples: `v2.0.1`, `v2.1.0`

Patch versions are welcome. New trunk milestones do **not** use `bN`. Older titles such as `v2.0.0b3` mean what they meant when they were created; we are not going back to rename them.

There is a leftover exception for domain-scoped tracking milestones from the parity era: a descriptive title with no version, or `v2.0.0` with no alpha/beta suffix. Prefer an ordinary `vX.Y.Z` reconstruction milestone when you can.

The description is where the story lives — the goal, the freeze id if this is reconstruction, and a list of issues in the form `Area (#issue): short intent`.

A small reconstruction release is usually three to seven issues. A larger catalog does not get a fancier milestone title; it gets Super-TRDs inside the same milestone.

Every issue goes on the **Tiferet Framework** project. What the fields mean is in [project_fields.md](project_fields.md). The ids for *this* repo are in [binding.md](binding.md).

## Issue titles

```
<Component Group> – <Brief Capitalized Title>
```

Five to eight words after the en-dash is about right. `Domain – Feature Model Condition Evaluation` and `Utils – SQLite Client Connection Lifecycle` are the tone.

## Status on the board

- **Ready** — the issue exists and has been triaged (Priority, Size, Estimate).
- **In Progress** — someone cut a branch or otherwise started. Set the Start date.
- **In Review** — the PR is open. If a review comment needs code, come back to In Progress, then return to In Review when you push.
- **Done** — merged, *and* the Collaboration Report (standalone) or verification addendum (Super-TRD child) is on the issue. Set the End date, then close.

New issues start at Ready. If one issue is waiting on another, use blocked-by. Do not park new work in Backlog just to show a dependency.

## Two ways to do the work

Size the story first — [project_fields.md](project_fields.md) has the rubric — then choose a path. Do not start a Super-TRD because the work "feels big." Do not stay standalone because splitting seemed like ceremony.

### Standalone TRD

Use this when the story is XL or smaller, **or** it is XL but you cannot name a seam.

1. Write the TRD ([tech_requirements.md](tech_requirements.md)). Reconstruction cites a freeze id in §7. A hotfix says it is a hotfix and skips the freeze.
2. Open the issue. Cut `<issue-number>-<lowercase-hyphenated-title>` from `main`.
3. Implement and test. Open a PR targeting `main`. That PR is for reviewing the diff, not for narrating the session.
4. Put implementation notes, the conversation link, and the Collaboration Report on the **issue**.
5. After the squash-merge: pull `main`, delete the local branch, rename the `.trd/` file to `.complete.md`. Port to proto only if a human asks.

### Super-TRD

Use this when the story is XL or larger **and** you can name the seam — a layer, a concern, a sequence. The full loop is in [super_trd_workflow.md](super_trd_workflow.md). The short version:

- One parent issue, several child sub-issues, one branch named for the parent, one PR. `Closes #<parent>` only. Children are never auto-closed by the PR.
- Each child stays at most Medium: one primary module, its tests, and at most a couple of non-testable dependency touches.
- The Starter writes the PR body for **every** child up front, with later AC still unchecked. That is a gate, not a courtesy. A PR that only describes child 1 forces every later agent to invent a format.
- When a child's code is pushed: check off that child's AC on the PR, set the child to In Review, and on the **child issue** post a session note plus a Collaboration Report labeled **implementation log**. That log means "this is what landed," not "combined review passed."
- The Reviewer checks every child AC against the combined PR. Comments that point at a line stay on the PR. The narrative and the conversation link go on the **parent issue**. If a child AC fails, say so on that **child issue** as well, so the log is not the last word.
- After merge: a short **verification addendum** on each child issue, then a parent roll-up Collaboration Report. A child becomes Done after the addendum — or after the Reviewer explicitly accepts that child's AC — not when the log was posted.

## Reviewing trunk

For reconstruction, you may look at proto, but only at artifacts the freeze and the TRD actually named. You are measuring, not merging. "Make trunk match proto" is the wrong advice in almost every case. If trunk is *ahead* of proto — a later, better name, a cleaner shape — keep trunk.

A hotfix is reviewed against the hotfix TRD. Proto has nothing to say about it.

Anything that points at a diff stays on the PR. The session record stays on the issue. [code_review.md](code_review.md) and [process.md](process.md#where-the-conversation-lives) are the longer versions of that sentence.

## Closing the milestone

When every issue is Done, close the milestone. Tag `vX.Y.Z` on `main` and publish a GitHub Release.

The release title may carry a subtitle: `Tiferet v<version> – <Brief Title>`. The body is the usual changelog: header (version, tag, date, branch, repo), Highlights, What's Changed by area with issue links, Breaking Changes, Upgrade Notes, Installation.

The [v2.0.0b3 release](https://github.com/greatstrength/tiferet/releases/tag/v2.0.0b3) is still a good *formatting* example. It is not a template for new tag *names* — that `bN` on trunk is historical.
