# Code Review

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

[process.md](process.md) is the index. A pull request is where we argue about the diff. An issue is where we remember the work item. Mixing those two jobs makes both worse.

There are two reviewer types: the **Prototype reviewer** (an RFP PR to proto) and the **Release reviewer** (a trunk PR to `main`). They share one standard and differ in what they weigh next. The merge step is the same for both.

## Shared review standards

Every reviewer checks the following, in this order of precedence. A higher item is never traded for a lower one.

1. **Code style is sacrosanct.** The general style ([code_style.md](../core/code_style.md)) and the style of each component the PR touches (`docs/core/<component>.md`) are held above everything else, including exactly one empty line between artifacts. No acceptance criterion, reference prototype, or precedent waives a style rule. This applies to code examples in docs and skills too.
2. **Ordering is preserved.** Artifact order is fixed. When a declaration or initialization dependency appears to force an out-of-order artifact, the author introduces a mechanic that preserves the order ([Ordering and Declaration Constraints](../core/code_style.md#ordering-and-declaration-constraints)). Reordering to keep things easy is a blocking finding.
3. **The acceptance criteria are met.** Each AC item is binary and names an artifact. Check each one.
4. **The tests are relevant and accurate.** Every test exercises the unit its label names, with the right tester type and fixtures, and the catalog rows say what the test does. A test that asserts nothing, duplicates another, or targets the wrong unit is a finding.
5. **Nothing is superfluous.** No unnecessary statements, declarations, imports, parameters, constants, or comments.

After that floor, each reviewer type applies its own priorities.

## Prototype reviewer

The authorizing document is the RFP. Read it. Review the proposal items, the acceptance criteria, and the distillation sections it cites. Do not review it against trunk. Do not ask the author to make proto look like `main`. That is the opposite of what this strand is for.

After the shared floor, in order:

1. **The RFP content holds.** Every proposal item and AC is realized as written, and nothing outside the RFP's scope has crept in.
2. **It aligns with the vision and the distillation.** The result matches the domain's vision statement and the core-domain distillation sections the RFP cites. If the RFP amends the distillation, the amendment is in the same PR.
3. **Artifacts land appropriately.** The right component, section, and name, but concept outranks cataloging. A name or placement that differs from the RFP while leaving the concept intact is a non-blocking note. A style violation is never a non-blocking note.

Suggested TRD slicing is out of scope for this review.

Confirm the PR is GitHub-linked to the RFP issue and is not on the milestone.

## Release reviewer

The authorizing document is the TRD. The first question is its acceptance criteria. For a Super-TRD, check each child TRD's artifacts and AC against the combined PR.

After the shared floor, **artifact fidelity is the primary lens**, and proper artifact cataloging outranks conceptual content. Every artifact the TRD names in §3 and §4 is checked, not only the ones the AC names: exact labels, names, section and sub-group placement, ordering, constant tables, parameters and keyword-argument style, test catalog rows, and file paths.

The source of fidelity, in order:

1. **The reference prototype**, when one exists. That is proto at the freeze point: the alpha tags or beta pre-release recorded in the TRD's §7 *Reference prototype* row. Measure each named artifact against it. A deviation on a named artifact is a finding, even when trunk looks cleaner.
2. **The TRD itself**, when there is no reference prototype. §3 and §4 are the whole specification.

A deviation that is a real improvement does not stay on trunk quietly. The Release reviewer sends it through a TRD amendment: update the TRD and the issue body before merge. If it changes the shape of a frozen RFP, it thaws the freeze ([process.md](process.md)), and the proto side takes it up as an RFP amendment.

A hotfix is reviewed against the hotfix TRD only. It has no reference prototype, and proto is not consulted.

The reviewer is the only role that reads proto during a release. The implementor works from the TRD and is never sent to proto ([tech_requirements.md](tech_requirements.md)). Reading proto is measurement. A finding names the artifact and the reference it deviates from. It never asks anyone to merge, rebase, or cherry-pick proto onto trunk.

Confirm the PR is GitHub-linked to the standalone TRD or the Super-TRD parent.

## Doc and skills PRs

A Doc or skills PR has no TRD and no RFP. Review the diff against the intent in the PR and the vocabulary in [process.md](process.md). Code examples inside docs and skills are held to the shared floor like any other code.

## How to leave a diff comment

1. `gh pr view <n> --json number,headRefName,baseRefName,files` so you know what you are looking at.
2. Reconstruction with a reference prototype: `git fetch origin <proto> --tags` using the branch in [binding.md](binding.md), then for each file the TRD's §3 names, `git diff <reference-tag>..HEAD -- <path>`. Read the reference artifact with `git show <reference-tag>:<path>` when the diff is noisy. Prototype review and hotfix review never run this step.
3. Sort what you see:
   - **Style violation** — blocking, always. Includes spacing and ordering.
   - **AC fail** — say so, naming the artifact.
   - **Test defect** — wrong unit, wrong tester, assertion gap, duplicate.
   - **Superfluous** — remove it.
   - **Artifact deviation from the reference** — release only, blocking. Name the artifact and the reference.
   - **Concept deviation** from the RFP, vision, or distillation — prototype only, blocking.
   - **Name or placement note** — prototype only, non-blocking, when the concept holds.
   - **Out of scope** — leave it alone.
4. A comment about a line goes on that line, and the line has to be in the PR diff. A comment about a missing file or a whole package goes in the review body.
5. Tell the human what you found and wait for a go-ahead before you post anything to GitHub.
6. Post **one consolidated review** through the reviews API (`path` + `position`, not `line`). The body holds the findings summary, the verdict, and `Co-Authored-By: Warp <agent@warp.dev>`. Do not post a stream of separate comments. After opening a PR, and after addressing PR feedback, the author posts a short status on the issue.

Do not put Collaboration Reports or session notes on the PR. That is what the issue is for.

## Verdict and merge

The merge process is the same for both reviewer types.

The review ends with one verdict: **Approve** or **Changes requested**. Approve only when:

- no blocking finding remains and no diff comment is unresolved;
- the PR is GitHub-linked to its authorizing issue (the RFP, the standalone TRD, or the Super-TRD parent) and is not on a milestone;
- the PR body's AC checkboxes are checked;
- no tag or version bump rides on the PR.

The reviewer approves and reports. The **human squash-merges**. The reviewer never merges by default.

The one exception is a human-delegated merge. When the human explicitly relinquishes the squash-merge for a specific PR, the reviewer may squash-merge that PR, and only after its own Approve verdict. This is situational, most often for a correction follow-up, and never universal: absent that instruction for that PR, the reviewer does not merge.

What follows the merge is unchanged. A proto PR does not honor `Closes`, so the implementing agent closes the RFP issue by hand. A trunk PR closes its TRD (or Super-TRD parent) through `Closes`, and the standalone TRD gets its Collaboration Report.

## Guardrails

A short, accurate review is kinder than a long one. Check the code before you claim a behavior. Never recommend proto → trunk git. Release reviewers never tell an implementor to read proto. Never lower a style or ordering finding to keep a review moving. Never commit as part of a review. Never merge unless the human has explicitly relinquished the squash-merge for that specific PR.
