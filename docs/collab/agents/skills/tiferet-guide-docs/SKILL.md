---
name: tiferet-guide-docs
description: Apply the docstring (vision-tier) / guide-doc (distillation-tier) convention when writing or updating a docstring, authoring or remediating a docs/guides/ entry, or adding a `# >> see:` annotation in a Tiferet-family repo. Covers what belongs in a docstring vs. a guide, the four genre-specific guide templates and how to pick between them, and the anchor/`# >> see:` linking convention.
---

# Docstring ↔ Guide-Doc Convention – Tiferet

## When to use
- Writing or upgrading a class-level docstring in `tiferet/` (or any Tiferet-family repo).
- Authoring a new `docs/guides/**/*.md` entry, or remediating one that has drifted from source.
- Adding, moving, or resolving a `# >> see:` annotation.
- Deciding whether new distillation content belongs in a docstring, a guide, or both.
- Not a substitute for `tiferet-code-style` (structural comment hierarchy) or the component `tiferet-code-*` skills (per-layer code conventions) — read those for how the *code* is organized; this skill governs where the *narrative documentation* about that code lives.

## The core split

A docstring and a guide entry serve different readers and carry different content. Collapsing them (or letting a guide silently drift out of sync with source) is the recurring failure mode this convention exists to prevent.

| | **Docstring (vision-tier)** | **Guide (distillation-tier)** |
|---|---|---|
| **Scope** | Class: a 1–2 sentence value statement — *why the concept exists*. Method: unchanged mechanical RST contract only. | Ubiquitous language, detailed mechanics, relationships, boundaries, worked examples. |
| **Analogy** | A vision statement's "the bet," compressed to class scope. | A distillation document — the full narrative. |
| **Lives in** | The source file, next to the code. | `docs/core/<component>.md` (code-style) or `docs/guides/**/*.md` (this skill's concern). |
| **Reader** | Someone orienting on *what this is* while reading code. | Someone who needs the deeper *why/how* and followed a `# >> see:` link to get there. |

**Class-level docstrings** open with the value statement and stay terse after that. **Method-level docstrings never gain behavioral narrative** — a method is a behavior, not a domain concept, so its docstring stays exactly `:param`/`:type`/`:return`/`:rtype`/`:raises`. If a method's behavior needs richer explanation (branching, edge cases, a worked example), that explanation belongs in the guide's `#### Methods` entry, linked via `# >> see:`.

## The `# >> see:` annotation

A fifth annotation artifact (alongside `# ++ todo:` / `# -- obsolete:`), fully specified in [docs/core/code_style.md § Annotation Artifacts](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — read that section for the canonical grammar, placement, and resolution rules. Summary:

```python
# ** model: error
# >> see: docs/guides/domain/error.md#error
class Error(DomainObject):
    '''
    The declared, catalogued shape of a failure condition — the contract that
    lets a raised TiferetError be resolved back into a localized, user-facing
    message instead of leaking as raw exception state.
    '''

    # * method: format_message
    # >> see: docs/guides/domain/error.md#error-format-message
    def format_message(self, lang: str = 'en_US', **kwargs) -> str:
        '''
        Formats the error message text for the specified language.
        ...  # mechanical contract unchanged — no narrative added here
        '''
```

- Target is always a **repo-relative path plus an explicit anchor id** — never a signature-derived anchor, so a renamed parameter never breaks the link.
- Apply only to **public** classes/methods/attributes that have corresponding guide coverage. Do not add it preemptively to artifacts with no guide entry yet.
- Placement: immediately after the `# *`/`# **` structural comment it annotates, before the docstring. Stacks after `# ++ todo:`/`# -- obsolete:` are ordered `# >> see:` first (see code_style.md).
- Update the tag whenever the target anchor id changes; remove it if the guide section is deleted rather than leaving it dangling.

## Anchoring convention in guides

Every documented method and attribute gets an explicit, signature-independent anchor:

- Method: `<a id="classname-lower-method-name"></a>` placed immediately before the method's bold entry (`**\`method_name(...) -> ReturnType\`**`).
- Attribute: the same `<a id="classname-lower-attr-name"></a>` pattern, inside the first cell of the attribute's table row.
- Class-level anchors are free via the Markdown heading itself (`### ClassName`) — do not add an explicit `<a id>` for a class.
- Scope the id per class (`classname-lower-...`) so a multi-class guide never collides.

## Choosing a genre template

Four genre-specific templates live in `docs/guides/templates/`, sharing the same mandatory scaffold (front-matter, `## Ubiquitous Language`, `## Boundaries`, `## Related Documentation`, explicit member anchors) but organized around different subjects. Pick by asking **what is the guide organized around** — a domain object, a layer-wide pattern, an event module's CRUD surface, or a concrete instantiable class:

| Template | Organized around | Use for | Examples |
|---|---|---|---|
| [`TEMPLATE-domain.md`](https://github.com/greatstrength/tiferet/blob/main/docs/guides/templates/TEMPLATE-domain.md) | One or more related domain objects | `docs/guides/domain/*.md` | `domain/core.md`, `domain/error.md` |
| [`TEMPLATE-strategy.md`](https://github.com/greatstrength/tiferet/blob/main/docs/guides/templates/TEMPLATE-strategy.md) | A layer-wide design pattern or decision, not any single class | `mappers.md`, `interfaces.md`, `repos.md`, `contexts.md`, `blueprints.md`, `di.md`, `utils.md`, `assets.md`, `errors.md` | `docs/guides/di.md`, `docs/guides/utils.md` |
| [`TEMPLATE-events.md`](https://github.com/greatstrength/tiferet/blob/main/docs/guides/templates/TEMPLATE-events.md) | A domain event module's CRUD-style operations | `docs/guides/events/*.md` | `events/app.md`, `events/error.md` |
| [`TEMPLATE-utils.md`](https://github.com/greatstrength/tiferet/blob/main/docs/guides/templates/TEMPLATE-utils.md) | One or more concrete, instantiable classes (cookbook detail) | Utilities and concrete DI engines, wherever they live | `docs/guides/utils/core.md`, `docs/guides/di/dependency_injector.md` |

**Disambiguation rule:** if you find yourself writing one subsection per concrete class with full constructor/method walkthroughs inside what you intended as a strategy guide, you actually want the utils (or domain) template instead — a strategy guide is organized by *pattern*, never by *class*.

Copy the chosen template, replace every `<...>` placeholder, delete its `<!-- -->` instructional comment block, and do not omit `## Ubiquitous Language` or `## Boundaries` — both are mandatory in every genre.

## Writing `## Ubiquitous Language` and `## Boundaries`

- **Ubiquitous Language** is a short glossary of terms specific to the module/layer — one line per term, defined once so prose elsewhere in the guide (and in other guides that link to it) can use the term without re-deriving it.
- **Boundaries** is an explicit "Inside this domain" / "Outside this domain" split. Name the responsibility this guide owns, then name the adjacent responsibility a reader might reasonably assume is in scope but isn't — and link to where it actually lives. `docs/guides/domain/error.md`'s original "What the catalog deliberately excludes" prose was the informal precedent this section formalizes.
- **Overview restates, it does not repeat.** Distill the module's role precisely, then link back to the class docstring for the vision-tier value statement (`**Vision:** See the \`X\` class docstring in \`tiferet/<path>.py\` for the value statement this guide distills.`) rather than quoting it — vision and distillation each get exactly one home.

## Worked example

See `docs/guides/domain/core.md` for a complete, already-remediated guide built on `TEMPLATE-domain.md` (anchors, Ubiquitous Language, Boundaries, and cross-links to sibling guides all present) and `docs/guides/di.md` / `docs/guides/utils.md` for the strategy genre's shape.

## Related Documentation
- [docs/core/code_style.md § Annotation Artifacts](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — canonical `# >> see:` grammar, placement, and resolution rules
- `docs/guides/templates/` — the four genre templates (copy from here, don't write a guide from scratch)
- `tiferet-code-style` — structural code comment hierarchy (read alongside this skill, not instead of it)
- `tiferet-author-trd` — link this skill from a TRD's Acceptance Criteria when the story requires a `docs/guides/` addition or remediation

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md
