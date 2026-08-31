# RFP — Prototype Strand

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

An RFP is the issue-backed specification for testing a domain theory on the prototype branch. It is not a trunk TRD and it is not a substitute for a documentation-only PR. A documentation repair may ride with an RFP only when it records or completes the acceptance criteria of already-settled prototype artifacts; standalone docs and skills work remains a Doc PR.

## Before Drafting

Read `binding.md` for the prototype branch and RFP prefix. Cite the relevant distillation or design documents, name dependencies and blocked work, and use one existing issue when amending a theory rather than opening a duplicate.

## RFP Body

The local draft lives under `.rfp/`; the GitHub issue body is the public copy. Write, in order:

1. Header — status, domain, branch, issue, related documents, dependencies,
 and blocks.
2. Summary and motivation.
3. Current state and the concrete precedents involved.
4. Numbered proposal and explicit out-of-scope items.
5. Risks/open questions, each marked resolved or open.
6. Binary acceptance criteria.
7. Suggested TRD slicing for any product artifacts that may later be frozen.

When an amendment changes a frozen shape, record that it thaws the affected freeze. Do not write a TRD for prototype work.

## Issue and Branch Lifecycle

Every RFP has a GitHub issue and belongs to the active beta milestone. Create a worktree branch from the bound prototype branch using `vX.Y.0bN-<lowercase-context>`. The PR targets that prototype branch and is reviewed against the RFP proposal and acceptance criteria.

After merge, the responsible session updates the package version, creates the next alpha tag, and records an issue session note with the RFP id, alpha, and beta milestone. A beta marks the drafting round; alpha numbers continue across betas on the same major/minor line.

## Boundaries

Prototype discovers and records its own theory. It does not merge, rebase, or cherry-pick itself into trunk. Any future reconstruction is separately authorized from a named catalog freeze.
