# Main — Trunk Strand

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

The process index is [process.md](process.md). This file is the trunk strand.

## Purpose

Trunk is the reconstructed, releasable history. It accepts:

- **Reconstruction TRDs** that implement a **frozen** RFP cluster. They name artifacts. They do not say "copy from proto."
- **Hotfix TRDs** for small mechanical defects already understood on trunk. Prototype is not consulted. No freeze id.
- **Doc / skills PRs** (see [doc.md](doc.md)) — no TRD.

Nothing from prototype lands on trunk as git.

## Milestones

Titles use the version number only:

- Format: `v<version>`
- Examples: `v2.0.1`, `v2.1.0`

Patch is allowed. New trunk milestones do **not** use `bN`. Historical titles such as `v2.0.0b3` keep their old meaning.

**Exception — domain-scoped tracking milestones** (legacy parity work): a descriptive title with no version, or `v2.0.0` with no alpha/beta suffix. Prefer versioned reconstruction milestones going forward.

The description carries the semantic context: goal, freeze id(s) if this is reconstruction, and a list of linked issues (`Area (#issue): short intent`).

Minor reconstruction releases typically hold 3–7 issues. Larger catalogs use Super-TRDs inside the milestone rather than a second title scheme.

Each issue is assigned to the **Tiferet Framework** project. Field semantics: [project_fields.md](project_fields.md). Repo-local ids: [binding.md](binding.md).

## Issue titles

```
<Component Group> – <Brief Capitalized Title>
```

Five to eight words after the en-dash. Examples: `Domain – Feature Model Condition Evaluation`, `Utils – SQLite Client Connection Lifecycle`.

## Project status

- **Ready** — created, triaged (Priority, Size, Estimate set).
- **In Progress** — branch cut / work started. Set Start date.
- **In Review** — PR open. Review comments that require code send status back to In Progress, then return to In Review.
- **Done** — merged. Set End date. Close the issue after the Collaboration Report (standalone) or verification addendum (Super-TRD child).

New issues start at Ready. Use blocked-by for ordering, not Backlog.

## Two execution paths

Size first ([project_fields.md](project_fields.md)). Then choose.

### Standalone TRD

Use when the story is XL or below, **or** XL with no natural seam.

1. Author the TRD ([tech_requirements.md](tech_requirements.md)). Reconstruction TRDs cite a freeze id in §7. Hotfix TRDs say hotfix and skip the freeze.
2. Create the issue. Cut `<issue-number>-<lowercase-hyphenated-title>` from `main`.
3. Implement and test. Open a PR targeting `main`. The PR is for code review only.
4. Post implementation notes, conversation link, and the Collaboration Report on the **issue**, not the PR.
5. The user squash-merges. Agent: pull `main`, delete the local branch, rename the `.trd/` file to `.complete.md`. Trunk→proto git only if a human asks.

### Super-TRD

Use when the story is XL+ **and** has a seam (layer, concern, sequencing). Full workflow: [super_trd_workflow.md](super_trd_workflow.md).

- Parent issue + child sub-issues. One combined branch `<parent-issue>-<slug>`. One PR. `Closes #<parent>` only.
- Child TRDs stay at most Medium (one primary module + tests + at most 1–2 dependency touches).
- Starter writes the PR body covering **all** children up front (unchecked AC for later children).
- When a child is pushed: check off that child's AC on the PR, set the child to In Review, and on the **child issue** post a session note plus a Collaboration Report labeled **implementation log**. That log is not combined-review acceptance.
- Reviewer verifies every child AC on the combined PR. Diff findings stay on the PR. Narrative and conversation link go on the **parent issue**. Child AC failures are also noted on that **child issue**.
- After merge: verification **addendum** on each child issue, then a parent roll-up Collaboration Report on the parent. Close a child as Done only after the addendum (or explicit Reviewer acceptance of that child's AC).

## Review on trunk

- Reconstruction review may glance at proto **only** for artifacts named in the frozen catalog / TRD AC. That is measurement, not a merge source. Never recommend "make trunk match proto" as a general rule.
- Hotfix review is against the hotfix TRD only.
- Comments that point at a diff stay on the PR. Session record stays on the issue. See [code_review.md](code_review.md) and [process.md](process.md#where-comments-live).

## Closing a milestone and releasing

When every issue is Done, close the milestone. Tag `vX.Y.Z` on `main` and publish a GitHub Release.

Release title may add a subtitle: `Tiferet v<version> – <Brief Title>`.
Body: header block (version, tag, date, branch, repo), Highlights, What's Changed (by area, with issue links), Breaking Changes, Upgrade Notes, Installation.

Canonical formatting example: the [v2.0.0b3 release](https://github.com/greatstrength/tiferet/releases/tag/v2.0.0b3) (historical `bN` on trunk — do not reuse that shape for new trunk tags).
