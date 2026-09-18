# RFP — Prototype Strand

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Start from [process.md](process.md) if you have not already. This page is the **document genre** for a Request for Prototype — how to write one. Implementing it is [tiferet-rfp-session](../../.agents/skills/tiferet-rfp-session/SKILL.md) and [process.md](process.md).

## What an RFP is for

An RFP is a bet you are willing to run on the long-lived proto branch. You settle vocabulary against the distillation, you implement it on proto, and you leave Suggested TRD slicing behind for a later catalog freeze.

It is not a TRD you wrote in a hurry. It is not how trunk ships.

Anyone may submit one — a maintainer, or a public contributor who wants a theory tested — as long as the draft follows the genre below. Opening a proto PR with no RFP behind it is out of process.

You do not need a TRD to implement on proto. The RFP *is* the specification for that strand.

## Before you start

The domain should already have a vision statement and a core-domain distillation on trunk. If this RFP is amending that distillation, say so and do the amendment in the same proto work. Cite numbered distillation sections; a later reader should be able to walk from the RFP to the claim it is testing.

This repo's [binding.md](binding.md) tells you the proto branch name and the RFP id prefix. Read it before you invent either.

## How we name them

```
<PREFIX><major>-RFP-<nnn>
```

`TLY1-RFP-001` and `TIF2-RFP-001` are the shape. Prefix and major come from [binding.md](binding.md). Numbers count up for that prefix and do not reset when you open the next grouping.

The GitHub issue title is the short form people will actually say out loud: `RFP-00N — <Plain Title>`.

## The document

Keep a local copy at `.rfp/<prefix-lower>-rfp-<nnn>-<kebab-title>.md`. That folder is gitignored on purpose — it is a working draft, not a committed artifact. The public copy is the GitHub issue body. Keep them in sync.

### Header

```markdown
# TIF2-RFP-001 — <Plain Title>

**Status:** Draft | Amended | Frozen for reconstruction · **Domain:** `tiferet` ·
**Branch:** `v2.x-proto` · **Issue:** #N
**Related:** `docs/…` §… ; skill names as needed
**Depends on:** none | RFP-00N (amended) — one-line reason
**Blocks:** RFP-00N — one-line reason
```

`Depends on` / `Blocks` are required. When you publish the issue, mirror them as GitHub blocked-by / blocking. A header that is not wired on GitHub is incomplete.

### Body, in this order

1. **Amendment note** — only when Status is Amended. What changed, what survived, and why you kept the same issue instead of opening a new one.
2. **Summary** — the shape you are settling, in the language the distillation already uses.
3. **Motivation** — why this RFP exists *now*, and which later RFPs will have to read whatever you decide here.
4. **Current state** — what proto (or trunk) actually has today, plus the concrete precedents you are borrowing from.
5. **Proposal** — numbered design items. Resolve the questions here. Name the alternatives you considered and set down.
6. **Out of scope** — named, and either handed to a later RFP or explicitly deferred. "We'll see" is not a section.
7. **Risks and open questions** — mark each one **resolved** or still open. A resolved item that still looks open will be relitigated.
8. **Acceptance criteria** — binary assertions. A proto implementor and a reviewer should be able to check them without taste.
9. **Suggested TRD slicing** — reconstruction debt, not a gate. Re-read this list at freeze time. The first draft is almost never the backlog you actually want.

When the design is wrong, amend **in place** on the same issue. You are not rewriting the past; you are saying what the next implementation replaces.

## Implementing on proto

1. Publish the RFP as a GitHub issue. Wire blocked-by. A reviewer assigns the milestone; you do not invent one.
2. Cut a branch from the proto branch in [binding.md](binding.md). The PR targets proto, not `main`.
3. Implement against the proposal, the acceptance criteria, and the distillation sections you cited. Review is against those. Nobody should be asking whether this matches trunk.
4. Title the PR `RFP-00N — <Plain Title> (#issue)`. GitHub-link the PR to the RFP issue. Do not add the PR to a milestone. The body links `#issue` and does **not** use `Closes` (proto will not honor it).
5. After squash-merge: close the RFP issue yourself. Do not tag. Do not bump the package version.

Suggested TRD slicing does not block the merge.

## What this strand will not do

It will not merge, rebase, or cherry-pick proto onto trunk.

It will not invent "internal RFPs" that never become issues. If it is an RFP, it has an issue.

It will not cut a version tag. Versioning is a milestone closeout, not an issue-pull.
