# RFP — Prototype Strand

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

The process index is [process.md](process.md). This file is only the prototype strand.

## Purpose

An RFP (Request for Prototype) tests a domain theory on the long-lived prototype branch. It settles vocabulary against the distillation, lands as an **alpha** on proto, and leaves a Suggested TRD slicing list for a later **catalog freeze**. It is not a sloppy TRD and it is not a way to ship trunk.

A public contributor or a maintainer may submit an RFP. Drive-by code against proto with no RFP is out of process.

No TRD is required to implement on proto.

## Preconditions

- A domain vision and core-domain distillation exist on trunk (or are being updated in the same proto work when the RFP amends them). RFPs cite numbered distillation sections.
- The repo's [binding.md](binding.md) names the proto branch and the RFP id prefix.

## Identifier

```
<PREFIX><major>-RFP-<nnn>
```

Examples: `TLY1-RFP-001`, `TIF2-RFP-001`. Prefix and major come from [binding.md](binding.md). Numbers are sequential per prefix and do not reset between betas.

Issue title: `RFP-00N — <Plain Title>`.

## Document genre

Local source: gitignored `.rfp/<prefix-lower>-rfp-<nnn>-<kebab-title>.md`.
Public copy: the GitHub issue body (same markdown).

### Header

```markdown
# TIF2-RFP-001 — <Plain Title>

**Status:** Draft | Amended | Frozen for reconstruction · **Domain:** `tiferet` ·
**Branch:** `v2.x-proto` · **Issue:** #N
**Related:** `docs/…` §… ; skill names as needed
**Depends on:** none | RFP-00N (amended) — one-line reason
**Blocks:** RFP-00N — one-line reason
```

### Body sections (in this order)

1. **Amendment note** — only when Status is Amended. What changed, what survived, why the same issue.
2. **Summary** — the shape being settled, in ubiquitous language.
3. **Motivation** — why this RFP exists now; which downstream RFPs read this shape.
4. **Current state** — what proto (or trunk) actually has, plus concrete precedents.
5. **Proposal** — numbered design items. Resolve questions here. Name rejected alternatives.
6. **Out of scope** — named and assigned to a later RFP or explicitly deferred.
7. **Risks and open questions** — mark each **resolved** or still open. Do not leave a resolved item looking open.
8. **Acceptance criteria** — binary assertions a proto implementor and reviewer can check without taste.
9. **Suggested TRD slicing** — reconstruction debt. Re-read this list at freeze time; do not treat the first draft as the trunk backlog.

Amendments happen **in place** on the same issue. The superseded alpha tag remains a historical record.

## Versioning on this strand

- A drafting round for a major.minor **creates** GitHub milestone `vX.Y.0bN` when the RFPs exist, not when the last one has shipped.
- Later drafts of the same line (bugs, refactors, missed features) are `b2`…`bN`. Multiple betas are expected.
- Each landed RFP (or amended re-implementation) is the next **alpha** tag / package version on proto: `vX.Y.0aN`. Alphas do not reset between betas of the same major.minor.
- `bN` is prototype-only going forward. Trunk releases are `vX.Y.Z`.

Discover the next alpha with `git tag --list 'vX.Y.0a*' --sort=-version:refname`. The next beta milestone is the next unused `bN` on that major.minor, independent of historical trunk tags that reused the `bN` shape.

## Implementation on proto

1. Publish the RFP as a GitHub issue. Assign it to the open beta milestone.
2. Cut `vX.Y.0bN-<kebab-context>` from the proto branch in [binding.md](binding.md). PR targets proto.
3. Implement against the RFP proposal and AC (and cited distillation sections). Review is against those, not against trunk.
4. PR title: `vX.Y.0aN — <Plain Title> (RFP-00N)`.
5. After squash-merge: bump the package version to that alpha, tag it, post a Collaboration Report on the **RFP issue** (cite RFP id, alpha tag, beta milestone). Session notes also go on the issue. The PR stays a review surface.

Suggested TRD slicing is not a gate. Reconstruction waits for a [catalog freeze](process.md#catalog-freeze).

## Freeze and thaw

See [process.md](process.md). A freeze note on this issue sets Status to `Frozen for reconstruction` and records a freeze id plus refreshed slicing. A later shape amendment thaws that freeze.

## What this strand does not do

- Does not merge, rebase, or cherry-pick proto onto trunk.
- Does not require Super-TRD child issues. Implement the RFP. If a single RFP is itself XL with a seam, split it into more RFPs rather than inventing a proto Super-TRD by default.
- Does not invent "internal RFPs" with no issue. Every RFP is an issue.
