<!--
Strategy-flavored guide template — Tiferet Framework
=======================================================
Use this template for a LAYER-WIDE, cross-cutting design-pattern guide — one
that explains broad, package-level understanding rather than walking through
any single concrete class in cookbook detail (that's TEMPLATE-utils.md's job).
Examples of this genre: docs/guides/mappers.md, interfaces.md, repos.md,
contexts.md, blueprints.md, di.md, utils.md, assets.md.

How to use this file:
- Copy it to `docs/guides/<layer>.md`.
- Replace every `<...>` placeholder. `## Ubiquitous Language` and
  `## Boundaries` are MANDATORY — do not omit them.
- Organize the body by PATTERN/DECISION, not by class. If you find yourself
  writing one subsection per concrete class with constructor/method details,
  you likely want TEMPLATE-utils.md (or TEMPLATE-domain.md) instead.
- Delete this comment block from the copied file.
-->
# <Layer> – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/<layer>/`  
**Version:** <x.y.z>

## Overview

<!-- Restate the layer's role in the architecture, distillation-style: what
problem this layer solves, and how it relates to its neighbors. One or two
paragraphs. -->

<Layer overview.>

## Ubiquitous Language

<!-- MANDATORY. Terms specific to this layer's design vocabulary. -->

- **<Term>** — <definition>.
- **<Term>** — <definition>.

## <Pattern/Decision Section 1>

<!-- One `##` section per cross-cutting pattern or design decision. Use a
descriptive heading, e.g. "The Standard CRUD Pattern", "When to Create an
Aggregate", "The Factory vs. Singleton Scope Decision". Include a code
example only when it clarifies the pattern generically — not a full
per-class walkthrough. -->

<Pattern description, with a short illustrative example.>

## <Pattern/Decision Section 2>

<...>

## When to Deviate

<!-- Optional but common in this genre: name the conditions under which the
standard pattern doesn't apply, and what to do instead. -->

## Creating a New <Artifact Kind>

<!-- Optional step-by-step for extending this layer (new repo, new
interface, new utility, etc.). -->

1. <Step>
2. <Step>

## Boundaries

<!-- MANDATORY. -->

**Inside this domain:** <what this layer is responsible for>.
**Outside this domain:** <adjacent responsibilities that live elsewhere, and where>.

## Related Documentation

- [docs/core/<layer>.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/<layer>.md) — Code-style conventions for this layer
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting
- <other related guides>
