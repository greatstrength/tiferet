# Assets in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

`assets` declares the concepts an application must have before it can exist: exceptions, named error codes, and bootstrap catalogs, with no inbound framework edges. It emits data but does not absorb dependencies or participate in runtime orchestration. Core assets may be used by other assets, `blueprints`, `contexts`, and `events`, typically through `from .. import assets as a`; they do not flow to `domain`, `interfaces`, `mappers`, `di`, `utils`, or `repos`. See [architecture.md](architecture.md).

Legal `# ** app` imports: none. The package imports only standard-library and third-party primitives. An asset that required a domain object or service would become a runtime dependency rather than a shared primitive.

## Life in the system

Assets declare. They do not execute a feature, mutate a noun, or open a file. `TiferetError` is the structured failure the rest of the framework raises. Namespaced catalogs (`error.py`, `app.py`, `feature.py` as `feat`, `cli.py`, `di.py`, `logging.py`) hold the identifiers and default definitions the factory will seed into the application runtime cache. `__init__.py` re-exports the public exceptions and the module aliases.

The package uses the standard preamble artifact kinds — imports, constants, functions, standalone classes, and exports — and contains no construct of its own. It holds no domain objects, aggregates, services, events, or contexts.

### Acyclic by purpose

`assets` has no framework imports, and that is its purpose rather than a restriction placed on it. The package describes the structure and prerequisites of an application's bounded context before the application is in use, so it must be able to exist before anything else does. A package that depended on framework behavior could not serve as that origin.

### Unity through differentiation

The import idiom follows this boundary. The package is imported **whole**—`from .. import assets as a`—and referenced through differentiated members: `a.error`, `a.feat`, `a.cli`, `a.app`, and `a.logging`.

This namespaced access preserves one package boundary while keeping catalogs distinct. It also predicts the repository's import idiom rather than treating `assets` as an undifferentiated constants module.

### Static, and on every runtime path

Assets hold no operational behavior. Their catalogs are loaded during composition and referenced by the runtime, but the package does not execute features, mutate domain state, or access a substrate.

Its contents are not renegotiated at runtime. A blueprint seeds a catalog into the cache during composition, and an interface may override what it declares, but the catalog itself is not mutated. Mutable state belongs to a domain noun.

The emission path is narrow. Blueprints seed catalogs into the cache, while contexts and events raise named errors through `a.<submodule>`. Every other package receives what it needs as data rather than importing `assets`.

## What an asset looks like

A constant is a `SCREAMING_SNAKE_CASE` value with its own `# ** constant:` label. Structured defaults are built from a factory, not annotated inline, so the identifier, human name, and default message stay data rather than becoming a domain `Error`. The `create_default_error` factory in `core.py` prevents catalog entries from diverging into unstructured inline dictionaries. The catalog and factory pattern itself is a guide concern; see [docs/guides/assets.md](../guides/assets.md).

The exception is a standalone class, not a domain object. `TiferetError` carries `error_code` and `kwargs`, which is what an event's `raise_error` and a context's error handler both understand. The class does not format a localized user message — that is `Error.format_message` on the domain noun, after the hub has loaded the catalogued `Error`. Assets name the failure. They do not present it.

Exports live only in `__init__.py`. Consumers write `from .. import assets as a` and then `a.error.ERROR_NOT_FOUND_ID`, `a.app.CORE_DEFAULT_SERVICES`, `a.feat`, `a.cli`, `a.logging`. New public symbols must be surfaced there. New concerns that need a domain, a service, or an event do not belong in this package.

## A dialect declares its own catalogs

The role is not reserved to the framework. `examples/basic_calculator/app/assets/` holds `core.py`, `di.py`, `error.py`, and `feature.py`, declaring `CALC_DEFAULT_ERRORS`, `CALC_DEFAULT_SERVICES`, and `CALC_DEFAULT_FEATURES` in the same preamble kinds, with the same absence of inbound edges.

The example demonstrates the position's claim: **a consumer's bootstrap catalogs describe its bounded context before behavior exists.** Before an `execute` method is written, the calculator declares its errors, resolvable operators, and exposed features. The dialect's catalogs feed its composition in the same structural role as the framework's.

## Package layout

```
tiferet/assets/
├── __init__.py      — Public exports; namespaced module aliases
├── core.py          — TiferetError, TiferetAPIError, shared factories and path constants
├── error.py         — Error-code ids and default error catalogs
├── app.py           — Default app sessions, services, and constants
├── feature.py       — Default feature catalogs (exported as feat)
├── cli.py           — Default CLI command catalogs
├── di.py            — Default service-registration catalogs
└── logging.py       — Default logging formatters, handlers, and loggers
```

## In short

- Assets declare the concepts an application must have before it can exist, and have no inbound framework edges.
- Acyclicity is the package's purpose, not a restriction placed on it: it describes the prerequisites of an application's bounded context before the application is in use.
- No construct of its own. Assets use the standard preamble kinds — imports, constants, functions, standalone classes, exports.
- Imported whole and referenced through differentiated members: `a.error`, `a.feat`, `a.app`, `a.cli`, `a.logging`.
- Nothing here executes, and everything here is on every runtime path. That is why the package is trustworthy — and why its contents cannot be renegotiated while the application runs.
- Used by blueprints, contexts, and events via `a`. Not by domain, interfaces, mappers, di, utils, or repos.
- A dialect declares its own catalogs, and those catalogs describe its bounded context before any behavior exists.
- If a concern needs a noun, a contract, or a unit of work, it is not an asset.
