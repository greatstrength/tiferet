# Assets in Tiferet

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

A system that can be composed has to begin with something that does not depend on the composition. `assets` is that crown: shared primitives — exceptions, named error codes, bootstrap catalogs — with no inbound framework edges. That position is **Keter**. Keter emits. It does not absorb, and it does not become runtime. Core assets may be used by other assets. Core and other assets may be used by `blueprints`, `contexts`, and `events`, typically via `from .. import assets as a`. They do not automatically flow to `domain`, `interfaces`, `mappers`, `di`, `utils`, or `repos`. See [architecture.md](architecture.md).

Legal `# ** app` imports: none. The package imports only the standard library and third-party primitives. That refusal is the job. If an asset needed a domain object or a service, it would no longer be a crown; it would be a hidden runtime.

## Life in the system

Assets declare. They do not execute a feature, mutate a noun, or open a file. `TiferetError` is the structured failure the rest of the framework raises. Namespaced catalogs (`error.py`, `app.py`, `feature.py` as `feat`, `cli.py`, `di.py`, `logging.py`) hold the identifiers and default definitions the factory will seed into the cache. `__init__.py` re-exports the public exceptions and the module aliases. There is no `const` and no `bps`.

Only five artifact kinds appear here: imports, constants, functions, standalone classes, and exports. There are no domain objects, aggregates, services, events, or contexts. That poverty is deliberate. Every other package can depend on this one without introducing a cycle, because there is nothing here that could depend back.

The emission path is narrow on purpose. Blueprints seed catalogs into the cache. Contexts and events raise named errors through `a.<submodule>`. A mapper that imported assets would be reaching up for a constant it should receive as data. A repo that imported assets would be speaking with Keter’s voice from Malkuth. Neither is granted.

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

What the reader just saw: the identifier, the human name, and the default message are data. They are not a domain `Error` yet. The factory (`create_default_error` in `core.py`) keeps the catalog from growing inline dictionaries that later diverge from the model.

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
- Five artifact kinds only: imports, constants, functions, standalone classes, exports.
- Used by blueprints, contexts, and events via `a`. Not by domain, interfaces, mappers, di, utils, or repos.
- Error constants are `a.<submodule>`. There is no `a.const`.
- If a concern needs a noun, a contract, or a unit of work, it is not an asset.
