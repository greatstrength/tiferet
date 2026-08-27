# Assets in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

A composable system begins with primitives that do not depend on the composition. `assets` holds exceptions, named error codes, and bootstrap catalogs with no inbound framework edges. This is the **Keter** position: it emits data but does not absorb dependencies or participate in runtime orchestration. Core assets may be used by other assets, `blueprints`, `contexts`, and `events`, typically through `from .. import assets as a`; they do not flow to `domain`, `interfaces`, `mappers`, `di`, `utils`, or `repos`. See [architecture.md](architecture.md).

Legal `# ** app` imports: none. The package imports only standard-library and third-party primitives. An asset that required a domain object or service would become a runtime dependency rather than a shared primitive.

## Life in the system

Assets declare. They do not execute a feature, mutate a noun, or open a file. `TiferetError` is the structured failure the rest of the framework raises. Namespaced catalogs (`error.py`, `app.py`, `feature.py` as `feat`, `cli.py`, `di.py`, `logging.py`) hold the identifiers and default definitions the factory will seed into the application runtime cache. `__init__.py` re-exports the public exceptions and the module aliases.

The package contains five artifact kinds: imports, constants, functions, standalone classes, and exports. It contains no domain objects, aggregates, services, events, or contexts.

### Acyclic in both directions

**Acyclicity defines this position.** `assets` has no framework imports, while its declared values flow only to designated consumer packages. A package that depended on framework behavior would not serve as the origin.

One of the intrinsic advantages of layers is that the lower layers can exist without the higher ones. That is also why phased introduction works at all. You can stand up `assets` and `domain` with nothing else in the repository and they are complete; you cannot stand up `repos` without the three positions it absorbs from.

### Unity through differentiation

The import idiom follows this boundary. The package is imported **whole**—`from .. import assets as a`—and referenced through differentiated members: `a.error`, `a.feat`, `a.cli`, `a.app`, and `a.logging`.

This namespaced access preserves one package boundary while keeping catalogs distinct. It also predicts the repository's import idiom rather than treating `assets` as an undifferentiated constants module.

### Static, and on every runtime path

Assets hold no operational behavior. Their catalogs are loaded during composition and referenced by the runtime, but the package does not execute features, mutate domain state, or access a substrate.

Its contents are not renegotiated at runtime. A blueprint seeds a catalog into the cache during composition, and an interface may override what it declares, but the catalog itself is not mutated. Mutable state belongs to a domain noun.

The emission path is narrow. Blueprints seed catalogs into the cache, while contexts and events raise named errors through `a.<submodule>`. Mappers and repositories receive required values as data rather than importing `assets`.

## What an asset looks like

A constant is a `SCREAMING_SNAKE_CASE` value with its own `# ** constant:` label. Structured defaults are built from a factory, not annotated inline:

```python
# ** constant: error_not_found
ERROR_NOT_FOUND = create_default_error(
    ERROR_NOT_FOUND_ID,
    'Error Not Found',
    [(EN_US, 'Error not found: {id}.')],
)

# ** constant: default_errors
DEFAULT_ERRORS = {
    ERROR_NOT_FOUND_ID: ERROR_NOT_FOUND,
}
```

The identifier, human name, and default message are data rather than a domain `Error`. The `create_default_error` factory in `core.py` prevents catalog entries from diverging into unstructured inline dictionaries.

The exception is a standalone class, not a domain object:

```python
# *** classes

# ** class: tiferet_error
class TiferetError(Exception):
    '''
    The base exception for all Tiferet-related errors.
    '''

    # * attribute: error_code
    error_code: str

    # * init
    def __init__(self, error_code: str, message: str = None, **kwargs):
        '''
        Initialize the TiferetError with an error code, message, and arguments.
        '''

        # Set the error code and additional arguments.
        self.error_code = error_code
        self.kwargs = kwargs

        # Initialize the base exception with serialized error data.
        super().__init__(
            json.dumps({'error_code': error_code, 'message': message, **kwargs})
        )
```

`error_code` and `kwargs` are what an event’s `raise_error` and a context’s error handler both understand. The class does not format a localized user message — that is `Error.format_message` on the domain noun, after the hub has loaded the catalogued `Error`. Assets name the failure. They do not present it.

Exports live only in `__init__.py`. Consumers write `from .. import assets as a` and then `a.error.ERROR_NOT_FOUND_ID`, `a.app.CORE_DEFAULT_SERVICES`, `a.feat`, `a.cli`, `a.logging`. New public symbols must be surfaced there. New concerns that need a domain, a service, or an event do not belong in this package.

## A dialect gets its own crown

The position is not reserved to the framework. `examples/basic_calculator/app/assets/` holds `core.py`, `di.py`, `error.py`, and `feature.py`, declaring `CALC_DEFAULT_ERRORS`, `CALC_DEFAULT_SERVICES`, and `CALC_DEFAULT_FEATURES` in the same five artifact kinds, with the same absence of inbound edges.

The example demonstrates the position's claim: **a consumer's bootstrap catalogs describe its bounded context before behavior exists.** Before an `execute` method is written, the calculator declares its errors, resolvable operators, and exposed features. The dialect's catalogs feed its composition in the same structural role as the framework's.

## The mirror at the bottom

Keter and Malkuth are one relation seen from both ends, and the cardinality is exact.

This position emits to exactly three — `blueprints`, `contexts`, `events`. The tenth absorbs from exactly three — `interfaces`, `mappers`, `utils`. Neither end reaches the other seven, and neither end reaches the other: `assets` never sees `repos`, and `repos` may never import `assets`.

The architecture does not reproduce every relation attributed to the traditional model. This chapter documents the relationships present in code: the metaphor is evaluated against the architecture, not the reverse.

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

- Assets emit primitives and have no inbound framework edges. That crown is Keter.
- Acyclicity in both directions is the definition of the position, not a restriction placed on it. This tier can exist without any of the others; the last one cannot.
- Five artifact kinds only: imports, constants, functions, standalone classes, exports.
- Imported whole and referenced through differentiated members: `a.error`, `a.feat`, `a.app`, `a.cli`, `a.logging`.
- Nothing here executes, and everything here is on every runtime path. That is why the tier is trustworthy — and why its contents cannot be renegotiated while the application runs.
- Used by blueprints, contexts, and events via `a`. Not by domain, interfaces, mappers, di, utils, or repos.
- Emits to exactly three; the tenth position absorbs from exactly three. The inversion is exact, and neither end reaches the other.
- A dialect declares its own crown, and those catalogs describe its bounded context before any behavior exists.
- If a concern needs a noun, a contract, or a unit of work, it is not an asset.
