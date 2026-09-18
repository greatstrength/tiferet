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

Nothing from prototype lands on trunk as git. Not a merge, not a rebase, not "just this one cherry-pick." What crosses the gap is a **catalog**: settled language, later written as TRDs an implementor can execute without opening the proto branch.

Git *may* flow the other way — trunk → prototype — when proto has not yet absorbed a mechanical fix that already shipped on trunk. That is allowed. It is not a habit. Skills do not cherry-pick unless a human asks. Treat a port as a translation, not as `git cherry-pick` and a shrug.

## What you submit

**A new feature / domain theory.** Write an RFP. Implement it on proto if you are also doing the code. The reviewer assigns the issue to a version/milestone. You do not tag. You do not bump the package version.

**A small mechanical bug on trunk.** Write a hotfix TRD and implement it.

**A reconstruction already specified.** If a TRD issue exists (standalone or a Super-TRD child), implement that issue. Link the PR to the standalone TRD or to the Super-TRD parent.

**Docs or skills.** Open a Doc PR. No issue unless the discussion needs a home first.

## Issues, PRs, and blocking

Pull requests are for reviewing code. Issues are for remembering the work item.

- **The issue** may sit on a milestone. **The PR does not.** Do not add the PR to the milestone.
- Every implementation PR is **GitHub-linked** to its authorizing issue (not a title mention alone): proto PR → the RFP issue; trunk PR → the standalone TRD or the Super-TRD **parent**.
- Proto PRs do not honor `Closes`. Link `#issue` in the body. After squash-merge, **close the issue yourself**.
- Trunk PRs may use `Closes #<issue>` for a standalone TRD, or `Closes #<parent>` for a Super-TRD. Never `Closes` a Super-TRD child from the parent PR.
- RFP headers include `Depends on` / `Blocks`. When you publish the issue, wire the same edges as GitHub blocked-by. TRD §7 and Super-TRD child sequencing do the same.

## Versioning (what an individual must not do)

Do not cut a git tag or GitHub Release when your PR merges. Version moves when a **milestone** closes, and that closeout is not an individual contributor step.

If you need the shapes for orientation only:

- Proto grouping titles look like `vX.Y.0aN` (git tag at close) or `vX.Y.0bN` (GitHub pre-release at close).
- Trunk releases look like `vX.Y.Z`.
- Freeze ids look like `TIF2-FREEZE-nnn` and are per milestone, not per version number.

Facts for *this* repo: [binding.md](binding.md). Commands an individual needs (link a PR, set blocked-by): [commands.md](commands.md).

## Where the conversation lives

- **On the PR:** what changed, AC checkboxes, the link to the issue, and review comments that point at a line.
- **On an RFP issue:** the RFP body, blocked-by, a short status after the PR opens and after you address feedback.
- **On a standalone TRD issue:** the TRD body, blocked-by, short status, and — when the work is done — a [Collaboration Report](collab_report.md).
- **On a Super-TRD child:** short status only. Do not post a Collaboration Report on the child; that artifact belongs on a standalone TRD issue.

Please do not leave the session diary as PR conversation comments.

## Binding, and where the skills live

Facts that belong to *this* repo — proto branch name, RFP prefix, GitHub project ids — live in [binding.md](binding.md). Skills should read the current repo's `docs/collab/binding.md` if it exists, and fall back to this repository's file if it does not.

The skills themselves are committed at [`.agents/skills/`](../../.agents/skills/) so an agent in this checkout can find them. Copying them to `~/.agents/skills/` is optional. If you do that, delete stale `tiferet-*` copies first or they will shadow what is in this tree. Every skill follows [agents/SKILL_TEMPLATE.md](agents/SKILL_TEMPLATE.md).

Working copies of RFPs and TRDs stay on your machine: `.rfp/` and `.trd/` are gitignored. The published GitHub issue body is the public copy.
