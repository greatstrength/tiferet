# Process — Trunk, Prototype, and Catalog

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

## The metaphor, then the rules

Trunk and prototype are two strands of one version family — a **double helix**. That image is useful once: the strands stay in phase by shared vocabulary, not by wrapping around each other. After this paragraph the rest of this corpus uses operational words: trunk, prototype, catalog, freeze, milestone, issue, and pull request.

The real rules are git history, GitHub objects, and which document authorizes work.

## What each strand is for

| Strand | Authorizing document | Lands on | Version objects |
|---|---|---|---|
| **Prototype** | Request for Prototype (RFP) | long-lived proto branch | beta milestone (`vX.Y.0bN`) + alpha tags |
| **Trunk** | Technical Requirements Document (TRD), after a catalog freeze — or a hotfix TRD | `main` | release milestone `vX.Y.Z` |
| **Doc** | the pull request itself | `main` | none |

They are not three interchangeable ways to ship the same change.

- An **RFP** tests a domain theory on prototype. It may be submitted by a maintainer or a public contributor, if it follows the RFP genre.
- A **reconstruction TRD** implements a **frozen** catalog on trunk. It names artifacts. It does not say "copy from proto."
- A **hotfix TRD** fixes a small mechanical defect on trunk. Prototype is not consulted.
- A **Doc / skills** change needs **no TRD**. Open a `docs-<context>` branch from trunk and describe the change in the PR using this process's vocabulary.

Stream guides: [rfp.md](rfp.md), [main.md](main.md), [doc.md](doc.md). TRD genre: [tech_requirements.md](tech_requirements.md).

## The two histories never merge

Prototype discovers and amends vocabulary. Trunk reconstructs a cooled catalog of named artifacts.

- Nothing from prototype lands on trunk as git — not a merge, rebase, or cherry-pick.
- What crosses the gap is a **catalog**: settled RFP language, later written as TRDs an implementor can execute without reading the proto branch.
- Git **may** flow trunk → prototype (cherry-pick or a manual port) when prototype has not absorbed a mechanical trunk fix. That is permitted, not routine. Skills do not cherry-pick by default. Identifier drift is likely; treat a port as a translation, not a patch apply.
- Pacing may diverge for a long time. Prototype can run many alphas inside many betas. Trunk waits until a named cluster is cool enough to reconstruct.

## Catalog freeze

A freeze is **not** a branch lock and **not** "prototype is finished." It is a named, human-declared snapshot of an **RFP cluster** whose shape is stable enough to reconstruct. Prototype may keep moving on everything outside that cluster.

**Freeze the smallest cluster whose Depends-on / Blocks graph is closed on shape** — the model plus whatever exists only to persist or select it. Do not freeze a whole version line or an entire product. Example: freeze "Token / Production / Grammar models and their persistence," not "v1" and not "the compiler."

**Ready-to-freeze checklist** (human; all boxes required):

1. The cluster's RFPs have landed as alphas on prototype (or an amendment has re-landed).
2. No open *shape* amendment on those issues. Remaining work consumes the cluster; it does not rewrite it.
3. Cited distillation sections no longer contradict the amended RFP bodies.
4. Suggested TRD slicing has been re-read against the **current** amended RFPs.
5. Downstream RFPs are no longer blocked on a missing field, renamed aggregate, or root-node shape inside the cluster.

If any box fails, do not freeze. Amend in place or open the next beta milestone.

**Recording a freeze:**

1. A human names the cluster and the RFP issue numbers.
2. A freeze note is posted on each included RFP issue: status `Frozen for reconstruction`, freeze id (e.g. `TIF2-FREEZE-001`), alpha tags, distillation sections, and the **refreshed** Suggested TRD slicing. That slicing is the reconstruction backlog.
3. Open a trunk milestone (`vX.Y.Z`) and author TRDs only from that freeze note. Reconstruction TRDs cite the freeze id in §7. `tiferet-author-trd` refuses reconstruction work without one.
4. A later shape amendment of a frozen RFP **thaws** the freeze. In-flight reconstruction TRDs stop. Re-freeze after the amendment lands.

Hotfix TRDs do not need a freeze. They name a mechanical defect already understood on trunk.

Cross-repo: a reconstruction may depend on another family's **catalogued** computations (distillation + frozen RFPs), never on that repo's prototype git.

## Versioning from this point forward

| Object | Strand | Shape | Meaning |
|---|---|---|---|
| Beta milestone | Prototype | `vX.Y.0bN` | one RFP drafting round on a major.minor line |
| Alpha tag / package version | Prototype | `vX.Y.0aN` | one RFP (or amended re-implementation) landed on proto |
| Trunk milestone and release | Trunk | `vX.Y.Z` | reconstructed or hotfixed release; patch allowed |

`bN` is prototype-strand only. Multiple betas on the same major.minor are expected (bugs, refactors, missed features). Historical trunk tags such as `v2.0.0b16` keep their old meaning; new trunk releases do not use `bN`.

Alphas increment inside the open beta and do not reset between betas of the same major.minor.

## Who may submit what

- **RFP** — a public contributor or maintainer who wants a domain theory tested. The draft must follow [rfp.md](rfp.md). Drive-by code against proto with no RFP is out of process.
- **Reconstruction TRD** — implement a frozen catalog on trunk.
- **Hotfix TRD** — a small mechanical fix on trunk.
- **Doc / skills PR** — documentation and agent-skill changes. No issue required unless useful; no TRD. The PR title and body use this process's ubiquitous language.

## Where comments live

Pull requests are a **review surface**. Issues are the **session record**.

- **On the PR:** change description, AC checkboxes, `Closes` line, and review comments that point at a diff.
- **On the issue** (the one issue, or the Super-TRD child issue): implementor session notes, conversation links, Collaboration Reports, and reviewer/closer narrative that is not a line comment.

Do not post session notes or Collaboration Reports as PR conversation comments.

## Trunk execution fork

Size the story, then choose a path. Detail lives in [main.md](main.md) and [tech_requirements.md](tech_requirements.md).

- **Standalone TRD** — XL or below, or XL with no seam. One issue, one branch, one PR. Session record on that issue.
- **Super-TRD** — XL+ *and* a seam. Parent + children, one combined branch, one PR. Each child gets an implementation-log Collaboration Report on the **child issue** when pushed, and a verification addendum after combined review. Closing a child as Done waits for that addendum (or explicit Reviewer acceptance of that child's AC).

## Binding

Repo-local facts — proto branch name, RFP prefix, GitHub project ids — live in [binding.md](binding.md). Skills read the current repo's `docs/collab/binding.md` if present; otherwise they fall back to this repository's file.

## Agent skills

Canonical, auto-discovered skills live at [`.agents/skills/`](../../.agents/skills/). They are committed. Copying them to `~/.agents/skills/` is optional (global convenience). Every skill follows [agents/SKILL_TEMPLATE.md](agents/SKILL_TEMPLATE.md).

Working copies of RFPs and TRDs stay local: `.rfp/` and `.trd/` are gitignored. The published GitHub issue body is the public copy.
