<!--
Utils-flavored (cookbook) guide template — Tiferet Framework
===============================================================
Use this template for a CONCRETE-CLASS cookbook guide — one or more
instantiable classes with real constructor/method behavior a developer
reaches for directly. This genre is not limited to tiferet/utils/: any
concrete engine class elsewhere in the framework (e.g. the DI concretes in
di/dependency_injector.py) uses this shape too.
Examples: docs/guides/utils/sqlite.md, utils/core.md, di/dependency_injector.md.

How to use this file:
- Copy it to `docs/guides/<layer>/<module>.md` (or `docs/guides/<layer>.md`
  if the module IS the layer, as with di/dependency_injector.md).
- Replace every `<...>` placeholder. `## Ubiquitous Language` and
  `## Boundaries` are MANDATORY. Anchor every documented method/attribute
  per the convention in TEMPLATE-domain.md.
- Keep the tone task-oriented: "when should you reach for X" before "here
  is X's API."
- Delete this comment block from the copied file.
-->
# <Layer> – <ClassA>, <ClassB>

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** <Month DD, YYYY>  
**Version:** <x.y.z>

## Overview

<!-- What these concrete classes are for, and how they relate (siblings?
one extends the other?). Link out to a strategy guide for the broader
pattern they implement, if one exists, rather than repeating it. -->

<Overview paragraph.>

**Module:** `tiferet/<layer>/<module>.py`
**Vision:** See each class's docstring in `tiferet/<layer>/<module>.py` for its value statement.

## Ubiquitous Language

<!-- MANDATORY. -->

- **<Term>** — <definition>.

## When should you reach for which one?

| Use case | Best choice | Why it fits |
|---|---|---|
| <use case> | `<ClassA>` | <reason> |

## Quick example

```python
<minimal end-to-end usage example>
```

## Domain Objects

### <ClassA>

<One-line purpose.>

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="classa-lower-attr"></a>`<attr>` | `<type>` | Yes/No | `<default>` | <description> |

#### Methods

<a id="classa-lower-method"></a>
**`<method>(<args>) -> <ReturnType>`**

<Behavior description, including edge cases.>

## Error Handling

<!-- How this class's failures surface — ServiceError wrapping, specific
error codes, what does and doesn't get caught. -->

## Testing

```python
<test example>
```

## Boundaries

<!-- MANDATORY. -->

**Inside this domain:** <the concrete class(es)' own construction and behavior>.
**Outside this domain:** <the broader pattern/ABC these classes implement — link to its strategy guide>.

## Related Documentation

- <link to the strategy guide for the broader pattern, if any>
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting
