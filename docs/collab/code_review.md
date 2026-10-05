# Code Review

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

[process.md](process.md) is the index. A pull request is where we argue about the diff. An issue is where we remember the work item. Mixing those two jobs makes both worse.

There are two reviewer types: the **Prototype reviewer** (an RFP PR to proto) and the **Release reviewer** (a trunk PR to `main`, or a sub-TRD PR to its Super-TRD branch). They share one standard and differ in what they weigh next. Merge to `main` is the same for both. A sub-TRD merge into the Super-TRD branch is the exception below.

## Shared review standards

Every reviewer checks the following, in this order of precedence. A higher item is never traded for a lower one.

1. **Code style is sacrosanct.** The general style ([code_style.md](../core/code_style.md)) and the style of each component the PR touches (`docs/core/<component>.md`) are held above everything else, including exactly one empty line between artifacts. No acceptance criterion, reference prototype, or precedent waives a style rule. This applies to code examples in docs and skills too.
2. **Ordering is preserved.** Artifact order is fixed, including class member bands: attribute, then init, then property methods, then other methods. When a declaration or initialization dependency appears to force an out-of-order artifact, the author introduces a mechanic that preserves the order ([Ordering and Declaration Constraints](../core/code_style.md#ordering-and-declaration-constraints)). Reordering to keep things easy is a blocking finding.
3. **The acceptance criteria are met.** Each AC item is binary and names an artifact. Check each one.
4. **The tests are relevant and accurate.** Every test exercises the unit its label names, with the right tester type and fixtures, and the catalog rows say what the test does. A test that asserts nothing, duplicates another, or targets the wrong unit is a finding.
5. **Nothing is superfluous.** No unnecessary statements, declarations, imports, parameters, constants, or comments.

Import groups are part of the style floor, not a separate standard.

- `# ** core` is the Python standard library only. `abc`, `typing`, `re`, and `uuid` belong here.
- `# ** infra` is third-party packages only. Examples: boto3 or other AWS libraries, Flask, FastAPI, Pydantic, pytest. Not the standard library. Not this application.
- `# ** app` is this application's own imports only, including relative imports. Not the standard library. Not a third-party package.

Order stays core, then infra, then app. Omit an empty group. A misplaced import is a blocking style finding. An acceptance criterion does not waive it.

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

The authorizing document is the TRD. The first question is its acceptance criteria.

Review topology for a Super-TRD:

- One **fresh** reviewer per sub-TRD PR. The context is that child only. Do not carry findings or confidence forward from an earlier child's merge. If you have already reviewed another child of this Super-TRD, you are not the fresh reviewer — stop and say so.
- Re-review after changes is that same reviewer, messaged again. Do not start a second reviewer for the same PR.
- After every child has merged into the Super-TRD branch, one **fresh final** reviewer — someone who has not reviewed a child of this Super-TRD — reviews the Super-TRD PR (that branch to `main`) against the parent TRD, the proto baseline, and cross-child consistency. Verdict only. No standing merge authority. The human squash-merges to `main`.

A sub-TRD review checks that child's artifacts and AC. The final review checks each child TRD's artifacts and AC against the combined diff, plus cross-child consistency.

After the shared floor, **artifact fidelity is the primary lens**, and proper artifact cataloging outranks conceptual content. Every artifact the TRD names in §3 and §4 is checked, not only the ones the AC names: exact labels, names, section and sub-group placement, ordering, constant tables, parameters and keyword-argument style, test catalog rows, and file paths.

The source of fidelity, in order:

1. **The reference prototype recorded in §7**, when one exists. That is proto at the freeze point: the alpha tags or beta pre-release in the *Reference prototype* row. Measure each named artifact against it. A deviation on a named artifact is a finding, even when trunk looks cleaner.
2. **The reference prototype branch**, on every reconstruction review that records a reference prototype. The branch name is in [binding.md](binding.md) (for this repo, `v2.x-proto`). Read it only through a fetched ref. Drift between the freeze-point reference and the branch is a finding to report, not a port. This check does not replace the §7 row. A §7 row of `None` means §3 and §4 are the specification; do not fill a blank by browsing proto.
3. **The TRD itself**, when there is no reference prototype. §3 and §4 are the whole specification.

A deviation that is a real improvement does not stay on trunk quietly. The Release reviewer sends it through a TRD amendment: update the TRD and the issue body before merge. If it changes the shape of a frozen RFP, it thaws the freeze ([process.md](process.md)), and the proto side takes it up as an RFP amendment.

A hotfix is reviewed against the hotfix TRD only. It has no reference prototype, and proto — tags or branch — is not consulted.

The reviewer is the only role that reads proto during a release. The implementor works from the TRD and is never sent to proto ([tech_requirements.md](tech_requirements.md)). Reading proto is `git fetch` plus `git show` / `git diff` of that ref. It is not a checkout into the trunk worktree, not a copy, and not a git flow. A finding names the artifact and the reference it deviates from. It never asks anyone to merge, rebase, cherry-pick, check out, or copy proto onto trunk.

Confirm the link and the base:

- Standalone: GitHub-linked to that TRD. Base is `main`.
- Sub-TRD PR: body has `Refs #<child>` and `Refs #<parent>`, and no `Closes`, `Fixes`, or `Resolves`. Base is the Super-TRD branch. A base of `main` is a blocking finding. Do not review it as the Super-TRD PR, and do not merge it.
- Super-TRD PR: GitHub-linked to the parent. `Closes #<parent>` only. Base is `main`.

## Doc and skills PRs

A Doc or skills PR has no TRD and no RFP. Review the diff against the intent in the PR and the vocabulary in [process.md](process.md). Code examples inside docs and skills are held to the shared floor like any other code.

## How to leave a diff comment

1. `gh pr view <n> --json number,headRefName,baseRefName,files` so you know what you are looking at.
2. Reconstruction with a recorded reference prototype: `git fetch origin <proto-branch> --tags` using the branch in [binding.md](binding.md). Do not check that branch out. For each file the TRD's §3 names, measure the freeze-point reference with `git diff <reference-tag>..HEAD -- <path>` and `git show <reference-tag>:<path>`, and measure the branch with `git diff origin/<proto-branch>..HEAD -- <path>` and `git show origin/<proto-branch>:<path>`. Prototype review, hotfix review, and a reconstruction whose §7 reference is `None` never run this step.
3. Sort what you see:
   - **Style violation** — blocking, always. Includes spacing and ordering.
   - **Wrong PR base** — blocking. A sub-TRD PR whose base is not the Super-TRD branch, or a Super-TRD PR whose base is not `main`.
   - **AC fail** — say so, naming the artifact.
   - **Test defect** — wrong unit, wrong tester, assertion gap, duplicate.
   - **Superfluous** — remove it.
   - **Artifact deviation from the reference** — release only, blocking. Name the artifact and the reference (freeze-point tag or prototype branch).
   - **Concept deviation** from the RFP, vision, or distillation — prototype only, blocking.
   - **Name or placement note** — prototype only, non-blocking, when the concept holds.
   - **Out of scope** — leave it alone.
4. A comment about a line goes on that line, and the line has to be in the PR diff. A comment about a missing file or a whole package goes in the review body.
5. Tell the human what you found and wait for a go-ahead before you post anything to GitHub. That wait is for posting the review. It is not a merge approval.
6. Post **one consolidated review** (`path` + `position`, not `line`). The first line of the review body is exactly `Verdict: Approve` or `Verdict: Changes requested`. Then the findings summary, then `Co-Authored-By: Warp <agent@warp.dev>`. Do not post a stream of separate comments. When the reviewer and the author share a GitHub token, GitHub rejects `--approve` and `--request-changes`. Post the review as a comment in that case. The verdict line is the signal either way; do not treat a rejected API event as a failed review. After opening a PR, and after addressing PR feedback, the author posts a short status on the issue.

Do not put Collaboration Reports or session notes on the PR. That is what the issue is for.

## Verdict and merge

Merge to `main` is the same for both reviewer types. A sub-TRD PR is the second exception below.

The review ends with one verdict line, the first line of the review: `Verdict: Approve` or `Verdict: Changes requested`. Approve only when:

- no blocking finding remains and no diff comment is unresolved;
- the PR is GitHub-linked to its authorizing issue (the RFP, the standalone TRD, the Super-TRD parent, or — for a sub-TRD PR — the child and the parent) and is not on a milestone;
- the PR body's AC checkboxes are checked;
- no tag or version bump rides on the PR;
- a sub-TRD PR's base is the Super-TRD branch, and a PR that should land on `main` has base `main`.

A **human squash-merges** every PR that targets `main`. The reviewer never merges to `main` by default.

Two exceptions, and only these:

1. **Human-delegated merge of a specific PR.** When the human explicitly relinquishes the squash-merge for that PR, the reviewer may squash-merge it, and only after `Verdict: Approve`. This is situational, most often a correction follow-up, and never universal. It is the only way a reviewer merges to `main`. The final Super-TRD reviewer has no standing merge authority; this exception still applies if the human names that PR.
2. **Sub-TRD PR into the Super-TRD branch.** A Release reviewer may squash-merge that PR without a further human approval when all of these hold, checked immediately before the merge, not from memory of an earlier look: `gh pr view <N> --json baseRefName` is the Super-TRD branch; the verdict line is `Verdict: Approve`; the review is clean (code style, every AC, artifact fidelity, tests) and no blocking finding is unresolved; the PR-body AC checkboxes are checked. The squash commit message must not contain `Closes`, `Fixes`, or `Resolves`. This permission never extends to `main`.

Delegated merge — either exception — keys off the verdict line plus those AC checkboxes. It does not key off a GitHub `--approve` event, which a shared token cannot submit.

What follows a merge to `main` is unchanged. A proto PR does not honor `Closes`, so the implementing agent closes the RFP issue by hand. A standalone trunk PR closes its TRD through `Closes`. The Super-TRD PR closes the parent through `Closes #<parent>` only. A sub-TRD merge does not close the child. Children stay In Review until that parent PR is squash-merged; closing them is closeout. The standalone TRD gets its Collaboration Report.

## Guardrails

A short, accurate review is kinder than a long one. Check the code before you claim a behavior. Never recommend proto → trunk git, including checkout or copy. Release reviewers never tell an implementor to read proto. Never lower a style or ordering finding to keep a review moving. Never commit as part of a review. Never merge to `main` unless the human has explicitly relinquished that specific PR. Never squash-merge a sub-TRD PR without a fresh base check. Never review a second child of the same Super-TRD; re-review only the PR you already have.
