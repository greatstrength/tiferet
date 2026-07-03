# Assets in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

The assets package (`tiferet/assets/`) is the framework's foundational, dependency-light layer. It holds the primitive building blocks shared across every other layer — the structured exception types, error-code and default-configuration constants, bootstrap wiring definitions, and the package's public exports.

Because it sits at the bottom of the dependency graph, assets modules import only the standard library and third-party primitives. They never import from `domain`, `events`, `mappers`, `interfaces`, `repos`, `contexts`, or `blueprints` — those layers depend on assets, not the other way around.

Assets modules are deliberately simple. Only five artifact kinds appear in the layer:

- **imports**
- **constants**
- **functions**
- **classes** (standalone)
- **exports**

There are no domain objects, aggregates, services, events, or contexts here. That simplicity is the point: keeping assets primitive lets every other layer depend on it without introducing dependency cycles.

## The Assets Layer's Role

- **Exceptions** — `TiferetError` and `TiferetAPIError` (`exceptions.py`) are the structured error types raised throughout the framework.
- **Constants** — error-code identifier constants (`constants.py`), the `DEFAULT_ERRORS` catalog (`error.py`), bootstrap wiring defaults (`blueprints.py`), and default logging configuration (`logging.py`).
- **Exports** — `__init__.py` re-exports the commonly used symbols and exposes the `constants` and `blueprints` modules under the short aliases `const` and `bps`.

## Structured Code Design

Assets modules follow the standard Tiferet artifact comment hierarchy (see [code_style.md](code_style.md)). Because the layer is primitive, only these top-level sections appear:

- `# *** imports` — with `# ** core` / `# ** infra` / `# ** app` groupings.
- `# *** constants` — module-level constants, each under `# ** constant: <snake_case_name>`.
- `# *** functions` — module-level functions, each under `# ** function: <snake_case_name>`.
- `# *** classes` — standalone classes, each under `# ** class: <snake_case_name>`.
- `# *** exports` — public re-exports (only in `__init__.py`).

**Spacing rules** match the rest of the framework: one empty line between a top-level comment and the first mid-level comment, one empty line between mid-level entries, and one empty line after docstrings and between code snippets.

There are no specialized top-level labels in this layer. Exception types are plain standalone **classes** (`# *** classes` / `# ** class: <name>`), and default configuration data structures are plain **constants** (`# *** constants` / `# ** constant: <name>`).

## Artifact Kinds

### Imports

```python
# *** imports

# ** core
from typing import Dict, Any
import json
```

### Constants

Constants are `SCREAMING_SNAKE_CASE` module-level values. Each constant carries its own `# ** constant: <snake_case_name>` label — related constants are not grouped under a shared comment. Entries nested inside a data structure are annotated in place (e.g., `# * error: <NAME>` within `DEFAULT_ERRORS`):

```python
# *** constants

# ** constant: error_not_found_id
ERROR_NOT_FOUND_ID = 'ERROR_NOT_FOUND'

# ** constant: default_errors
DEFAULT_ERRORS = {

    # * error: ERROR_NOT_FOUND
    ERROR_NOT_FOUND_ID: {
        'id': ERROR_NOT_FOUND_ID,
        'name': 'Error Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Error not found: {id}.'}
        ],
    },
}
```

### Functions

Assets functions are small, stateless helpers with no framework dependencies:

```python
# *** functions

# ** function: is_blank
def is_blank(value: str) -> bool:
    '''
    Return True when a string is empty or whitespace-only.

    :param value: The string to inspect.
    :type value: str
    :return: True if the value is None or blank, otherwise False.
    :rtype: bool
    '''

    # Treat None and whitespace-only strings as blank.
    return value is None or not value.strip()
```

### Classes (standalone)

Standalone classes carry no injected dependencies and extend only stdlib or other assets primitives. Exception types like `TiferetError` are ordinary standalone classes under `# *** classes` / `# ** class:`:

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

### Exports

Only `__init__.py` carries an `# *** exports` section. It re-exports the public surface and exposes module aliases where consumers use them heavily:

```python
# *** exports

# ** app
from .exceptions import TiferetError, TiferetAPIError
from .constants import ERROR_NOT_FOUND_ID
from .error import DEFAULT_ERRORS
from . import constants as const
from . import blueprints as bps
```

## Creating and Extending Assets Modules

1. Start the module with a docstring, then an `# *** imports` section limited to the standard library and third-party primitives.
2. Add content under exactly one primary artifact kind per concern — `# *** constants`, `# *** functions`, or `# *** classes`.
3. Do not introduce domain, service, event, mapper, or context artifacts here; if a concern needs one, it belongs in the corresponding layer.
4. Surface any new public symbols from `__init__.py` under `# *** exports`.

### Best Practices

- Keep the layer dependency-light: never import from another Tiferet layer.
- Restrict modules to the five artifact kinds (imports, constants, functions, standalone classes, exports).
- Use `SCREAMING_SNAKE_CASE` values, each with its own `# ** constant: <snake_case>` label; do not group multiple constants under a shared `# ** constants: <group>` comment.
- Place exception classes under `# *** classes` and default configuration data under `# *** constants`; the layer uses no specialized artifact labels.
- Write RST docstrings on functions and classes, and keep code snippets separated by single blank lines.

## Package Layout

```
tiferet/assets/
├── __init__.py      — Public exports; exposes `const` and `bps` module aliases
├── constants.py     — Error-code identifier constants
├── error.py         — The DEFAULT_ERRORS catalog (imports ids from constants.py)
├── exceptions.py    — TiferetError and TiferetAPIError
├── blueprints.py    — Bootstrap default constants and service wiring
└── logging.py       — Default logging formatters, handlers, and loggers
```

## Conclusion

The assets layer is the simple, stable foundation of the Tiferet framework: a dependency-light collection of imports, constants, functions, standalone classes, and exports. Constraining it to these primitive artifact kinds keeps the dependency graph acyclic and the framework's shared building blocks easy to locate and reason about.

Explore `tiferet/assets/` for the error catalog, exception types, and bootstrap defaults.

## Related Documentation

- [code_style.md](code_style.md) — General structured code style and artifact comments
- [docs/guides/domain/error.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/error.md) — Error handling that consumes `TiferetError` and `DEFAULT_ERRORS`
- [docs/core/blueprints.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/blueprints.md) — Bootstrap orchestration that consumes the `blueprints` defaults
