<!--
Events-flavored guide template — Tiferet Framework
=====================================================
Use this template for a domain event MODULE guide — operation-centric,
documenting each DomainEvent subclass as a CRUD-style operation with
required/optional parameters, return type, errors, and behavior steps.
Examples of this genre: docs/guides/events/app.md, cli.md, di.md, error.md,
feature.md, logging.md, sqlite.md.

How to use this file:
- Copy it to `docs/guides/events/<module>.md`.
- Replace every `<...>` placeholder. `## Ubiquitous Language` and
  `## Boundaries` are MANDATORY additions to this genre's existing shape —
  add them even though older event guides predate the convention.
- One `###` subsection per event class, each with its own anchor (event
  class names are already unique per module, so the heading's own anchor
  suffices — no separate `<a id>` needed unless a method within an event
  needs independent linking).
- Delete this comment block from the copied file.
-->
# Events – <Module Concern>

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/events/<module>.py`  
**Version:** <x.y.z>

## Overview

<!-- What this event module's CRUD surface manages, and its shared
dependency. Distillation-style — link to the base event class's docstring
for its value statement rather than repeating it. -->

<One-paragraph overview.>

## Ubiquitous Language

<!-- MANDATORY. -->

- **<Term>** — <definition>.

## Events at a Glance

| Event | Operation | Required Parameters | Returns |
|---|---|---|---|
| `<EventName>` | Create/Read/Update/Delete | `<params>` | `<ReturnType>` |

## Dependency

All events inject:

- **`<dependency_attr>: <ServiceType>`** — <what it's used for>.

## Event Details

### <EventName>

<One-line purpose.>

**Required:** `<params>`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `<param>` | `<type>` | `<default>` | <description> |

**Returns:** `<ReturnType>` — <description>.

**Errors:**
- `<ERROR_CODE>` if <condition>.

**Behavior:**
1. <step>
2. <step>

```python
result = DomainEvent.handle(
    <EventName>,
    dependencies={'<dependency_attr>': <dependency>},
    <param>=<value>,
)
```

## Common Patterns

<!-- Optional: cross-cutting behavior shared by multiple events in this
module (e.g. "Retrieve → Verify → Mutate → Save", idempotent deletes). -->

## Boundaries

<!-- MANDATORY. -->

**Inside this domain:** <the CRUD operations this module owns>.
**Outside this domain:** <the domain object shape itself (link to its domain guide), persistence details (link to its repo)>.

## Related Documentation

- [docs/guides/domain/<module>.md](../domain/<module>.md) — Domain objects this module operates on
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns and test harness
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) — Service interface conventions
