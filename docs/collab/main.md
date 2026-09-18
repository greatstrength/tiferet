# Main — Trunk Strand

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

[process.md](process.md) is the index. This page is trunk: the history a release can stand on, as an **individual** lands one TRD.

## What trunk will accept

Three things, and only three:

- **Reconstruction TRDs** that implement a **frozen** catalog. They name artifacts. They do not say "copy from proto," and they do not send you to the proto branch. They cite an existing freeze id in §7.
- **Hotfix TRDs** for small mechanical defects already understood on trunk. Prototype is not consulted. There is no freeze id.
- **Doc / skills PRs** — see [doc.md](doc.md). No TRD.

Nothing from prototype lands on trunk as git. If you find yourself reaching for a merge from proto, stop. The catalog is how that work crosses.

You do not open the trunk milestone or mint the freeze id. If a reconstruction TRD has no freeze id, do not implement it — the specification is incomplete.

## Milestones

The title is the version number. Nothing else.

- Format: `v<version>`
- Examples: `v2.0.1`, `v2.1.0`

Patch versions are welcome. New trunk milestones do **not** use `bN`. Older titles such as `v2.0.0b3` mean what they meant when they were created; we are not going back to rename them.

A reviewer may assign your issue to a milestone. You do not close the milestone or publish the GitHub Release.

Every issue goes on the **Tiferet Framework** project. What the fields mean is in [project_fields.md](project_fields.md). The ids for *this* repo are in [binding.md](binding.md).

## Issue titles

```
<Component/Assemblage> – <Brief Capitalized Title>
```

Component/Assemblage is the majority of the ten core packages (assets, blueprints, contexts, di, domain, events, interfaces, mappers, utils, repos), or `Config` when the change is configuration, or `Tests` when it is only tests, or a domain assemblage when one concept spans many packages.

Five to eight words after the en-dash is about right. `Domain – Feature Model Condition Evaluation` and `Utils – SQLite Client Connection Lifecycle` are the tone.

## Status on the board

- **Ready** — the issue exists and has been triaged (Priority, Size, Estimate).
- **In Progress** — someone cut a branch or otherwise started. Set the Start date.
- **In Review** — the PR is open. If a review comment needs code, come back to In Progress, then return to In Review when you push.
- **Done** — merged, *and* for a standalone TRD the Collaboration Report is on the issue. Set the End date, then close.

New issues start at Ready. If one issue is waiting on another, use blocked-by. Do not park new work in Backlog just to show a dependency.

## Individual path: one TRD

Use this when you are landing one hotfix or one standalone reconstruction.

1. Write the TRD ([tech_requirements.md](tech_requirements.md)). Reconstruction cites an existing freeze id in §7. A hotfix says it is a hotfix and skips the freeze. Wire GitHub blocked-by from §7.
2. Open the issue. Cut `<issue-number>-<lowercase-hyphenated-title>` from `main`.
3. Implement and test. Open a PR targeting `main`, title `<Component/Assemblage> - <Plain Title> (#issue)`, **GitHub-linked** to that TRD. `Closes #<issue>` is allowed on trunk. Do not add the PR to the milestone.
4. After the PR opens, and again after you address PR feedback, post a short status on the **issue**.
5. After the squash-merge: Collaboration Report on the issue, Status Done, End date. Rename the `.trd/` file to `.complete.md`. Port to proto only if a human asks.

## Super-TRD as a shape

A Super-TRD is parent plus children, one combined PR, child size at most Medium. The TRD *genre* for that shape is in [tech_requirements.md](tech_requirements.md).

If you are asked to implement **one child** already in flight: implement that child on the existing parent branch; do not open a second PR; GitHub-link remains the **parent** issue; never `Closes #<child>`. Post short status on the child issue. Do not write a Collaboration Report on the child.

Running the parent fan-out (first child opens the PR, remaining children push, parent closeout report) is not an individual contributor loop.

## Reviewing trunk

For reconstruction, you may look at proto, but only at artifacts the freeze and the TRD actually named. You are measuring, not merging. "Make trunk match proto" is the wrong advice in almost every case. If trunk is *ahead* of proto — a later, better name, a cleaner shape — keep trunk.

A hotfix is reviewed against the hotfix TRD. Proto has nothing to say about it.

Anything that points at a diff stays on the PR. Short status stays on the issue. [code_review.md](code_review.md) and [process.md](process.md) are the longer versions of that sentence.
