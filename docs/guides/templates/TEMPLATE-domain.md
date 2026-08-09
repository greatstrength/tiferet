<!--
Canonical guide-document template — Tiferet Framework
=======================================================
This template codifies the "distillation tier" of the docstring ↔ guide
convention (see `.handoff/docstring-guide-doc-reorganization.handoff.md` for
the full mechanism spec). A docstring is scoped like a vision statement (the
value proposition — why the concept exists); this guide is scoped like a
distillation document (the detailed mechanics, vocabulary, and relationships).

How to use this file:
- Copy it to `docs/guides/<component>/<module>.md` (or `docs/guides/<module>.md`
  for components without a nested domain split).
- Replace every `<...>` placeholder. Remove any section that genuinely does not
  apply (e.g. a module with no configuration mapping), but `## Ubiquitous
  Language` and `## Boundaries` are MANDATORY — do not omit them.
- Delete this comment block from the copied file.
-->
# <Component> – <Module>: <ClassA> and <ClassB>

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** <Month DD, YYYY>  
**Version:** <x.y.z>

## Overview

<!-- Restate the domain precisely, distillation-style. Do NOT repeat the class
docstring's value statement verbatim — link to it instead, so vision and
distillation each have exactly one home. One paragraph is usually enough. -->

<One-paragraph restatement of what this module's domain objects are for and
how they relate to each other.>

**Module:** `tiferet/domain/<module>.py`
**Vision:** See the `<ClassA>` class docstring in `tiferet/domain/<module>.py`
for the value statement this guide distills.

## Ubiquitous Language

<!-- MANDATORY. A short glossary of terms specific to this domain module —
terms a contributor needs defined once, consistently, rather than re-derived
from scattered prose. Keep entries to one line each. -->

- **<Term>** — <definition>.
- **<Term>** — <definition>.

## Domain Objects

<!-- One `###` subsection per class. Class-level anchors are free via the
heading itself — do not add an explicit `<a id>` for the class. Every
documented METHOD and ATTRIBUTE gets an explicit anchor, independent of
signature text, so a renamed parameter never breaks a link. Anchor id
convention: `<classname-lower>-<member-snake-case>`, scoped per class so a
multi-class guide never collides. -->

### <ClassA>

<One-line distilled purpose — mechanics, not vision.>

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="classa-lower-attr-name"></a>`<attr_name>` | `<type>` | Yes/No | `<default>` | <description> |

#### Methods

<a id="classa-lower-method-name"></a>
**`<method_name>(<args>) -> <ReturnType>`**

<Distilled behavior description — including branching/edge-case behavior a
docstring wouldn't carry.>

```python
<short usage example>
```

## <Behavior/Flow Section(s), as needed>

<!-- Optional, repeatable. Use a descriptive heading per flow, e.g. "Error
Formatting Flow", "Runtime Role", "Flag Resolution Flow". Numbered steps work
well for sequential flows. -->

## Configuration Mapping

<!-- Optional — only when this domain maps to a configuration file section. -->

```yaml
<illustrative config snippet>
```

## Domain Events

<!-- Optional — only when domain events interact with these objects. -->

| Event | Description |
|---|---|
| `<EventName>` | <description> |

## Service Interface

<!-- Optional — only when a dedicated Service interface persists these objects. -->

**`<ServiceName>`** (`tiferet/interfaces/<module>.py`) defines the abstract
contract for <domain> persistence:

- `<method_signature>`

## Relationships to Other Domains

<!-- How this domain's objects are consumed by or depend on neighboring
domains/components. Bullet per relationship. -->

- **<Neighboring Domain>:** <relationship description>.

## Boundaries

<!-- MANDATORY. The distillation-doc "Inside/Outside" split. This is where
scope creep gets caught — be explicit about what a reader might reasonably
assume is in scope but isn't. -->

**Inside this domain:** <what this module's domain objects are responsible for>.
**Outside this domain:** <adjacent responsibilities that deliberately live
elsewhere, and where they actually live>.

## Instantiation

```python
from tiferet.domain import <ClassA>

<instantiation example>
```

## Related Documentation

- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comment & formatting rules
- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — Domain model conventions
- <other related guides>
