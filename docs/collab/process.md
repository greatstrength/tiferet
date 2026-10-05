# Process — Trunk, Prototype, and Catalog

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

If you only read one collaboration doc, make it this one. The rest of `docs/collab/` is detail. This page is how **one contributor** authorizes and lands work.

## Three kinds of document, not three ways to ship the same change

| You are… | The authorizing document is… | It lands on… |
|---|---|---|
| **Testing a domain theory** | a Request for Prototype (RFP) | the long-lived proto branch |
| **Rebuilding a frozen catalog, or fixing a small mechanical bug** | a Technical Requirements Document (TRD) — reconstruction cites a freeze id; a hotfix does not | `main` |
| **Changing docs or agent skills** | the pull request itself | `main` |

An RFP is not a sloppy TRD. A TRD is not "the RFP, but for `main`." A Doc PR is not a TRD you were too busy to write.

- An **RFP** asks: is this the right language? Anyone may submit one, as long as it follows [rfp.md](rfp.md). Opening a proto PR with no RFP is out of process.
- A **reconstruction TRD** asks: can we rebuild a frozen catalog on trunk, artifact by artifact? It names those artifacts. It never says "copy from proto." It cites a freeze id in §7. If there is no freeze id, do not write the TRD.
- A **hotfix TRD** asks: can we fix this small, already-understood defect on trunk? Prototype is not consulted. There is no freeze id.
- A **Doc / skills** change needs **no TRD**. Cut `docs-<context>` from trunk. See [doc.md](doc.md).

The long forms: [rfp.md](rfp.md), [main.md](main.md), [doc.md](doc.md). The TRD genre is [tech_requirements.md](tech_requirements.md).

You do not plan a prerelease, mint a freeze, or run a multi-issue reconstruction from this page. That work is out of scope for an individual contributor. If a freeze id or a milestone already exists, use it; do not invent one.

## The two histories never merge

Prototype is where vocabulary is discovered and amended. Trunk is where a cooled catalog of named artifacts is rebuilt so a release can stand on it.

They do not become each other.

Nothing from prototype lands on trunk as git. Not a merge, not a rebase, not a cherry-pick, not a checkout of proto into the trunk tree, and not a copy of proto files. What crosses the gap is a **catalog**: settled language, later written as TRDs an implementor can execute without opening the proto branch.

A Release reviewer may read the reference prototype to measure a trunk PR's named artifacts against it ([code_review.md](code_review.md)): the freeze-point tags or pre-release, and the prototype branch in [binding.md](binding.md), through `git show` / `git diff` of a fetched ref. That is measurement, not a git flow. The implementor never reads proto.

Git *may* flow the other way — trunk → prototype — when proto has not yet absorbed a mechanical fix that already shipped on trunk. That is allowed. It is not a habit. Skills do not cherry-pick unless a human asks. Treat a port as a translation, not as `git cherry-pick` and a shrug.

## What you submit

**A new feature / domain theory.** Write an RFP. Implement it on proto if you are also doing the code. The reviewer assigns the issue to a version/milestone. You do not tag. You do not bump the package version.

**A small mechanical bug on trunk.** Write a hotfix TRD and implement it.

**A reconstruction already specified.** If a TRD issue exists, implement that issue. A standalone PR targets `main` and links that TRD. A Super-TRD child targets the Super-TRD branch, not `main`, and links the child and the parent. See [Super-TRD branch](#super-trd-branch).

**Docs or skills.** Open a Doc PR. No issue unless the discussion needs a home first.

## Issues, PRs, and blocking

Pull requests are for reviewing code. Issues are for remembering the work item.

- **The issue** may sit on a milestone. **The PR does not.** Do not add the PR to the milestone.
- Every implementation PR is **GitHub-linked** to its authorizing issue (not a title mention alone): proto PR → the RFP issue; standalone trunk PR → that TRD; Super-TRD PR (Super-TRD branch → `main`) → the parent; sub-TRD PR → the child and the parent.
- Proto PRs do not honor `Closes`. Link `#issue` in the body. After squash-merge, **close the issue yourself**.
- A standalone trunk PR may use `Closes #<issue>`. The Super-TRD PR to `main` uses `Closes #<parent>` only. A sub-TRD PR uses `Refs #<child>` and `Refs #<parent>` and never `Closes`, `Fixes`, or `Resolves` — not in the body, and not in the squash commit. Never `Closes` a child from the Super-TRD PR.
- RFP headers include `Depends on` / `Blocks`. When you publish the issue, wire the same edges as GitHub blocked-by. TRD §7 does the same. Before wiring a freeze's issue set, check for a blocked-by cycle. Do not publish one. See [Safeguards](#safeguards).

## Versioning (what an individual must not do)

Do not cut a git tag or GitHub Release when your PR merges. Version moves when a **milestone** closes, and that closeout is not an individual contributor step.

If you need the shapes for orientation only:

- Proto grouping titles look like `vX.Y.0aN` (git tag at close) or `vX.Y.0bN` (GitHub pre-release at close).
- Trunk releases look like `vX.Y.Z`.
- Freeze ids look like `TIF2-FREEZE-nnn` and are per milestone, not per version number.

Facts for *this* repo: [binding.md](binding.md). Commands an individual needs (link a PR, set blocked-by): [commands.md](commands.md).

## Super-TRD branch

A Super-TRD is parent plus children. It is not one branch that children commit onto, and the first child does not open the parent PR. That shape breaks when children run in parallel.

A **sub-TRD PR** is one child's pull request. It targets the Super-TRD branch. The **Super-TRD PR** is that branch to `main`, opened once, after the children have merged into it.

The orchestrator (a Release round, or the human) cuts `<parent-issue>-<slug>` from `main` at the freeze base — trunk as it stands for this reconstruction, never proto — and pushes it **before any child starts**. A child does not cut that branch.

Each unblocked child cuts `<child-issue>-<slug>` from the Super-TRD branch tip and opens a sub-TRD PR targeting that branch, never `main`. Title: `<Component/Assemblage> - <Plain Title> (#child)`. Body: `Refs #<child>`, `Refs #<parent>`, and that child's AC checkboxes. After `gh pr create`, the author runs `gh pr view <N> --json baseRefName` and stops if the base is not the Super-TRD branch. A child with an external blocker is not cut yet. See [Cross-boundary blockers](#cross-boundary-blockers).

Children stay **In Review** from the moment that PR is open until the Super-TRD PR is squash-merged to `main`. Closing them is closeout, not the child's job.

The Super-TRD PR title is `<Component/Assemblage> - <Plain Title> (#parent)`. Body: `Closes #<parent>` only. The orchestrator or the human opens it. A child does not.

## Cross-boundary blockers

A Super-TRD child blocked by a standalone TRD, or by any work outside its parent branch, is not branched, assigned, or implemented until every such blocker is squash-merged to `main`. The process keeps that work from starting. It does not start speculatively and rebase later.

Those external blocked-by edges are recorded on the child and on the **parent** issue, so they are visible at the parent. The orchestrator checks the parent's blocked-by before launching any child and does not launch a child whose blocker is unmerged.

Unblocked children of the same parent may still be cut from the Super-TRD branch at the freeze base and merged into it. Their progress does not lift a sibling's external block.

Once those blockers are on `main`, the orchestrator or the human merges `main` into the Super-TRD branch with a merge commit. Not a rebase. Not the child. Only then is the blocked child's branch cut from that updated tip.

A blocker between children of the same parent is satisfied when the blocking child's PR is squash-merged into the Super-TRD branch. It does not wait for `main`. The dependent child is cut from that tip, not from the sibling's branch.

## Where the conversation lives

- **On the PR:** what changed, AC checkboxes, the link to the issue, and review comments that point at a line.
- **On an RFP issue:** the RFP body, blocked-by, a short status after the PR opens and after you address feedback.
- **On a standalone TRD issue:** the TRD body, blocked-by, short status, and — when the work is done — a [Collaboration Report](collab_report.md).
- **On a Super-TRD child:** short status only. The child stays In Review until the Super-TRD PR to `main` is squash-merged. Do not post a Collaboration Report on the child; that artifact belongs on a standalone TRD issue, or on the parent at round closeout.

Please do not leave the session diary as PR conversation comments.

## Review and merge

Every implementation PR gets one reviewer. The **Prototype reviewer** holds code style first, then the RFP's content against the vision and distillation. The **Release reviewer** holds code style first, then artifact fidelity against the reference prototype recorded in the TRD and, read-only, against the prototype branch. A hotfix does not consult proto. The standards, including who is fresh, are in [code_review.md](code_review.md).

The reviewer posts one consolidated review. The first line is `Verdict: Approve` or `Verdict: Changes requested`. When the reviewer and the author share a GitHub token, GitHub rejects `--approve` and `--request-changes`. The verdict line is the signal either way.

A **human squash-merges** every PR that targets `main`. The reviewer never merges to `main` unless the human has explicitly relinquished that specific PR.

A Release reviewer may squash-merge a sub-TRD PR into its Super-TRD branch without a further human approval when all of these hold, checked at merge time: `gh pr view <N> --json baseRefName` is the Super-TRD branch; the verdict line is `Verdict: Approve`; the review is clean (code style, every AC, artifact fidelity, tests) and no blocking finding is unresolved; the PR-body AC checkboxes required by [code_review.md](code_review.md) are checked. That permission does not extend to `main`. The final review of the Super-TRD PR is verdict only, aside from an explicit per-PR delegation to `main`.

## Safeguards

These checks keep a fan-out off the wrong base. State them as checks, not as a story about a round.

- Before a fan-out, the orchestrator validates its dispatch branch and PR-base rules against `tiferet-implement-trd`. Every implementer prompt states the PR base explicitly.
- After opening a PR, the implementer verifies `gh pr view <N> --json baseRefName` and stops if it is wrong.
- A reviewer verifies that base immediately before any merge.
- Freeze and TRD authoring (`takwin-code-freeze`, `tiferet-author-trd`) check the issue set for a blocked-by cycle before wiring edges. A cycle is two or more issues each naming the other's output as a prerequisite. Do not publish it. A child stuck on a cycle stops and reports.

## Closeout leaves nothing behind

When a PR is squash-merged (and again when a milestone closes), remove everything the work created locally. Nothing is left to be found, resumed, or mistaken for current.

- The worktree and its registration: `git worktree remove`, then `git worktree prune`.
- The local branch, and the remote branch if GitHub did not delete it.
- Anything that points at them: symlinks, config entries, editor or index references.
- Temp files: scratch scripts, virtual environments, snapshots, downloaded artifacts, and PR or comment body drafts.

The working copies this process defines are not temp: `.rfp/` and `.trd/` stay. Each is renamed `.complete.md` when its work is done: an RFP after its proto PR is squash-merged and the issue is closed, a standalone TRD after its PR is squash-merged and the issue is Done. A Super-TRD child is not Done when its sub-TRD PR merges into the Super-TRD branch; that working copy completes at parent closeout, after the Super-TRD PR reaches `main`. A sub-TRD merge does not remove the Super-TRD branch. Do not remove another contributor's branch or worktree, or your own uncommitted work, without asking.

**Temporary information never goes to external or cloud storage** (gists, pastebins, uploaded images or screenshots, hosted drives, third-party services) unless the human explicitly authorizes it. What the process defines goes where it says: RFP and TRD bodies, status notes, review comments, and Collaboration Reports live on GitHub issues and PRs. Temporary images and scratch output do not.

## Binding, and where the skills live

Facts that belong to *this* repo — proto branch name, RFP prefix, GitHub project ids — live in [binding.md](binding.md). Skills should read the current repo's `docs/collab/binding.md` if it exists, and fall back to this repository's file if it does not.

The skills themselves are committed at [`.agents/skills/`](../../.agents/skills/) so an agent in this checkout can find them. Copying them to `~/.agents/skills/` is optional. If you do that, delete stale `tiferet-*` copies first or they will shadow what is in this tree. Every skill follows [agents/SKILL_TEMPLATE.md](agents/SKILL_TEMPLATE.md).

Working copies of RFPs and TRDs stay on your machine: `.rfp/` and `.trd/` are gitignored. The published GitHub issue body is the public copy.
