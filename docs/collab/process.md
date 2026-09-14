# Process — Trunk, Prototype, and Catalog

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

If you only read one collaboration doc, make it this one. The rest of `docs/collab/` is detail. This page is the shape of the work.

## A picture, then the real words

Trunk and prototype are two strands of the same version family. The picture we use is a **double helix**: they stay in phase by sharing a vocabulary, not by wrapping around each other. That image is useful once. After this paragraph we drop it and talk like engineers — trunk, prototype, catalog, freeze, milestone, issue, pull request.

The rules underneath are ordinary. Git history is real. GitHub issues, PRs, and milestones are real. And every kind of work has a document that authorizes it. If you cannot name that document, you are not ready to open a branch.

## Three kinds of work, not three ways to ship the same change

| You are… | The authorizing document is… | It lands on… | Versioning |
|---|---|---|---|
| **Testing a domain theory** | a Request for Prototype (RFP) | the long-lived proto branch | a beta milestone (`vX.Y.0bN`) and alpha tags |
| **Rebuilding that theory on the release line, or fixing a small mechanical bug** | a Technical Requirements Document (TRD) — reconstruction after a catalog freeze, or a hotfix with no freeze | `main` | a release milestone `vX.Y.Z` |
| **Changing docs or agent skills** | the pull request itself | `main` | none |

An RFP is not a sloppy TRD. A TRD is not "the RFP, but for `main`." A Doc PR is not a TRD you were too busy to write.

- An **RFP** asks: is this the right language? You (or a public contributor) may submit one, as long as it follows the genre in [rfp.md](rfp.md).
- A **reconstruction TRD** asks: can we rebuild that frozen language on trunk, artifact by artifact? It names those artifacts. It never says "copy from proto."
- A **hotfix TRD** asks: can we fix this small, already-understood defect on trunk? Prototype is not consulted.
- A **Doc / skills** change needs **no TRD**. Cut `docs-<context>` from trunk and describe the change in the PR, using the words on this page, so a later reader does not have to reverse-engineer your intent.

The long forms live here: [rfp.md](rfp.md), [main.md](main.md), [doc.md](doc.md). The TRD genre is [tech_requirements.md](tech_requirements.md).

## The two histories never merge

Prototype is where vocabulary is discovered and amended. Trunk is where a cooled catalog of named artifacts is rebuilt so a release can stand on it.

They do not become each other.

Nothing from prototype lands on trunk as git. Not a merge, not a rebase, not "just this one cherry-pick." What crosses the gap is a **catalog**: the settled RFP language, later written as TRDs an implementor can execute without ever opening the proto branch.

Git *may* flow the other way — trunk → prototype — when proto has not yet absorbed a mechanical fix that already shipped on trunk. That is allowed. It is not a habit. Skills do not cherry-pick unless a human asks. And because proto has often renamed the thing you just fixed, treat a port as a translation, not as `git cherry-pick` and a shrug.

Pacing is allowed to look unfair. Prototype can run many alphas inside many betas for a long time. Trunk waits. That is cheaper than reconstructing a language that is still moving.

## Catalog freeze

A freeze is not "lock the proto branch" and it is not "prototype is finished." It is a named, human-declared snapshot of an **RFP cluster** whose *shape* is stable enough to rebuild on trunk. Everything outside that cluster may keep moving.

Freeze the smallest cluster whose Depends-on / Blocks graph is closed on shape — the model, plus whatever exists only to persist or select it. Freeze "Token / Production / Grammar, and how they are stored," not "v1," and not "the compiler."

You are ready to freeze when every box below is true:

1. The cluster's RFPs have landed as alphas on prototype (or an amendment has re-landed).
2. Nobody is still rewriting the shape of those issues. Remaining work *consumes* the cluster; it does not rename it.
3. The distillation sections those RFPs cite no longer contradict the amended bodies.
4. Someone has re-read Suggested TRD slicing against the **current** RFPs, not the first draft.
5. Downstream RFPs are no longer blocked on a missing field, a renamed aggregate, or a YAML root-node shape inside the cluster.

If any box fails, do not freeze. Amend in place, or open the next beta milestone.

When you do freeze:

1. A human names the cluster and the RFP issue numbers. An agent does not invent this.
2. A freeze note goes on each included RFP issue: status `Frozen for reconstruction`, a freeze id (for example `TIF2-FREEZE-001`), the alpha tags, the distillation sections, and the **refreshed** Suggested TRD slicing. That slicing is now the reconstruction backlog.
3. Open a trunk milestone (`vX.Y.Z`) and write TRDs only from that freeze note. Reconstruction TRDs cite the freeze id in §7. `tiferet-author-trd` should refuse the work without one.
4. A later shape amendment of a frozen RFP **thaws** the freeze. In-flight reconstruction TRDs stop. You re-freeze after the amendment lands. You do not quietly keep building the old catalog.

Hotfixes do not need a freeze. They name a mechanical defect already understood on trunk.

Across repositories, a reconstruction may depend on another family's **catalogued** computations — their distillation plus their frozen RFPs — never on that repo's prototype git.

## Versioning from here forward

| Object | Strand | Shape | Meaning |
|---|---|---|---|
| Beta milestone | Prototype | `vX.Y.0bN` | one RFP drafting round on a major.minor line |
| Alpha tag / package version | Prototype | `vX.Y.0aN` | one RFP (or an amended re-implementation) landed on proto |
| Trunk milestone and release | Trunk | `vX.Y.Z` | a reconstructed or hotfixed release; patch is allowed |

`bN` belongs to prototype now. Multiple betas on the same major.minor are expected — bugs, refactors, the feature you realized you missed. Tiferet itself ran through a long string of them.

Historical trunk tags such as `v2.0.0b16` keep the meaning they had when they were cut. New trunk releases do not reuse `bN`.

Alphas increment inside the open beta. They do not reset when you open `b2` on the same major.minor.

## Who may submit what

If you want a domain theory tested, submit an **RFP**. Maintainers and public contributors are both welcome; the draft has to follow [rfp.md](rfp.md). Opening a proto PR with no RFP is out of process.

If you want a frozen catalog rebuilt on trunk, submit a **reconstruction TRD**.

If you want a small mechanical bug fixed on trunk, submit a **hotfix TRD**.

If you want the docs or the skills changed, open a **Doc PR**. No issue unless the discussion needs a home first. No TRD. Use the vocabulary on this page in the PR title and body.

## Where the conversation lives

Pull requests are for reviewing code. Issues are for remembering the session.

- **On the PR:** what changed, AC checkboxes, the `Closes` line, and review comments that point at a diff.
- **On an RFP issue:** session notes, conversation links, and freeze notes.
- **On a TRD issue** (the one issue, or the Super-TRD child issue): implementor session notes, conversation links, Collaboration Reports, and any reviewer or closer narrative that is not a line comment.

Please do not leave the session diary as PR conversation comments. Future you will thank present you when the review thread is only about the diff.

## Two ways to execute trunk work

Size the story, then pick a path. The detail is in [main.md](main.md) and [tech_requirements.md](tech_requirements.md).

- **Standalone TRD** — XL or smaller, or XL with no natural seam. One issue, one branch, one PR. The session record lives on that issue.
- **Super-TRD** — XL or larger *and* a seam you can name (a layer, a concern, a sequence). Parent plus children, one combined branch, one PR. Each child gets an implementation-log Collaboration Report on the **child issue** when the code is pushed, and a verification addendum after combined review. A child is not Done when the log is posted. It is Done when the addendum lands, or when the Reviewer explicitly accepts that child's acceptance criteria.

## Binding, and where the skills live

Facts that belong to *this* repo — proto branch name, RFP prefix, GitHub project ids — live in [binding.md](binding.md). Skills should read the current repo's `docs/collab/binding.md` if it exists, and fall back to this repository's file if it does not.

The skills themselves are committed at [`.agents/skills/`](../../.agents/skills/) so an agent in this checkout can find them. Copying them to `~/.agents/skills/` is optional, and only useful if you want them in every repo. If you do that, delete stale `tiferet-*` copies first or they will shadow what is in this tree. Every skill follows [agents/SKILL_TEMPLATE.md](agents/SKILL_TEMPLATE.md).

Working copies of RFPs and TRDs stay on your machine: `.rfp/` and `.trd/` are gitignored. The published GitHub issue body is the public copy.
