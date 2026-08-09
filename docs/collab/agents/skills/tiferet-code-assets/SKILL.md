---
name: tiferet-code-assets
description: Apply assets layer conventions when adding or modifying constants, exceptions, or bootstrap defaults in a Tiferet-family repo. Covers the five permitted artifact kinds, SCREAMING_SNAKE_CASE constants, factory functions, standalone classes, and the exports pattern.
---

# Assets Code Style – Tiferet

## When to use
- When adding a new error-code constant, default error definition, or bootstrap constant in `tiferet/assets/`.
- When adding or modifying an exception class (`TiferetError`, `TiferetAPIError`).
- When adding a stateless helper function to the assets layer.
- Do NOT use for domain objects, events, services, mappers, or any component that depends on other Tiferet layers — assets must remain dependency-light.

## Artifact comment structure

Module skeleton (assets modules use exactly five artifact kinds, in this order):
```
# *** imports         ← stdlib and third-party primitives only
# *** constants       ← SCREAMING_SNAKE_CASE module-level values
# *** functions       ← stateless helper functions
# *** classes         ← standalone exception or utility classes
# *** exports         ← public re-exports (__init__.py only)
```

Artifact labels:
```
# ** constant: <snake_case_name>    ← individual constant
# ** function: <snake_case_name>    ← individual function
# ** class: <snake_case_name>       ← individual class
```

**Sub-groups** — partition a large `# *** constants` section with a parenthetical qualifier. The framework convention (e.g. `assets/error.py`) uses three correlated sub-group layers:
```python
# *** constants (ids)               ← raw error-code identifier strings (core group)
# ** constant: feature_not_found_id
FEATURE_NOT_FOUND_ID = 'FEATURE_NOT_FOUND'

# *** constants (data)              ← assembled default definition constants (core group)
# ** constant: feature_not_found_data
FEATURE_NOT_FOUND_DATA = create_default_error_data(...)  # no id — see below

# *** constants (groups)            ← catalog dicts aggregating the above
# ** constant: core_default_errors
CORE_DEFAULT_ERRORS = {
    FEATURE_NOT_FOUND_ID: FEATURE_NOT_FOUND_DATA,
}
```

The `_DATA` suffix on the leaf constant signals that the id was factored out: the factory (`create_default_error_data` and its siblings) does not take an `id`/`service_id` parameter, since the definition is always stored under its owning `*_ID` constant as the group-dict key above. Embedding the id a second time inside the value would restate it. The consuming `add_default_*` decorator (e.g. `add_default_errors`) reinjects the id from that key when reconstituting the domain object.

**Multi-group catalogs** — when a module defines additional capability groups (e.g., `admin`, `sqlite`, `csv`), each group name is a shared key across all three layers: `(ids_<group>)`, `(data_<group>)`, and a named dict entry in `(groups)`. Adding an entry to a capability group always requires touching all three locations:
```python
# *** constants (ids_sqlite)
# ** constant: sqlite_conn_failed_id
SQLITE_CONN_FAILED_ID = 'SQLITE_CONN_FAILED'

# *** constants (data_sqlite)
# ** constant: sqlite_conn_failed_data
SQLITE_CONN_FAILED_DATA = create_default_error_data(
    'SQLite Connection Failed',
    [(EN_US, 'Failed to connect: {original_error}')],
)

# *** constants (groups)
# ** constant: sqlite_default_errors
SQLITE_DEFAULT_ERRORS = {
    SQLITE_CONN_FAILED_ID: SQLITE_CONN_FAILED_DATA,
}
```

The plain `(ids)` / `(data)` sub-groups (no suffix) hold the core/baseline group. All additional groups use the `_<group>` suffix consistently.

## Key conventions

- **Layer boundary — valid `# ** app` imports:** none. `assets` is the root layer; it has no framework imports. Only `# ** core` (stdlib) and `# ** infra` (minimal third-party, e.g. `json`) are valid. Never import from any other framework layer.
- **Constants:** `SCREAMING_SNAKE_CASE`. Each constant has its own `# ** constant: <snake_case>` label. Do not group multiple constants under a single `# ** constants: <group>` mid-level label — use a top-level sub-group instead.
- **Structured defaults:** Build structured default data from a factory function (e.g. `create_default_error_data`), not inline dicts. Define each entry as a named constant with a `_DATA` suffix (it is raw data, not an id-keyed model), then assemble the catalog dict as a separate constant keyed by the corresponding `_ID` constant.
- **Constant declaration style:** All list- and dictionary-typed constants use the multi-line hanging-indent style with a trailing comma everywhere. This is especially important in `assets/` modules: unlike `# *** events`, `# *** mappers`, and other construct groups, the assets layer has no unique construct-level section designation — it is a pure repository of constants, functions, and classes, making constant formatting the primary quality signal. Never `{ **OTHER_DICT }` inline — always expand to multi-line.
- **Factory function constants:** Constants whose value is a factory function call (e.g. `create_default_error_data`, `create_app_service_dependency_data`) must list each argument on its own line with hanging indent and a trailing comma. Never collapse a factory call to a single line. These id-adjacent factories intentionally omit an `id`/`service_id` parameter — the group-dict key is the sole source of the id, and the consuming `add_default_*` decorator reinjects it.
- **Optional parameters in factory calls:** must always be passed as keyword arguments. Required positional parameters may be passed positionally. See `tiferet-code-style` for the general keyword-argument rule and example.
- **Functions:** Small, stateless, no framework dependencies. Use RST docstrings.
- **Classes:** Plain standalone classes (exception types, data primitives). Use `# *** classes` / `# ** class: <name>`, `# * attribute: <name>`, `# * init`.
- **`TiferetError.raise_error`:** `TiferetError` (and its subclass `TiferetAPIError`) carries a `raise_error(cls, error_code, message=None, **kwargs)` classmethod raiser — `raise cls(error_code, message, **kwargs)` dispatches to whichever subclass it is called on, so `TiferetAPIError.raise_error(...)` raises a `TiferetAPIError` directly with no override needed. This mirrors the classmethod-raiser shape of `ModelError.raise_error` (`domain/core.py`) and `ServiceError.raise_for` (`interfaces/core.py`) — each of the framework's three error families raises through a classmethod on the exception it owns.
- **Exports:** Only in `__init__.py` under `# *** exports`. Use short module aliases for frequently consumed modules (e.g. `from . import constants as const`).
- **Docstrings & guides:** Standalone class docstrings (e.g. `TiferetError`) open with a 1–2 sentence vision-tier value statement, linked via `# >> see: @guides/assets.md#<anchor>` to `docs/guides/assets.md`, which carries the full distillation-tier detail. See `tiferet-guide-docs` for the complete convention.

## Example

```python
# *** imports

# ** core
from typing import List, Tuple, Dict, Any
import json

# *** constants (ids)

# ** constant: feature_not_found_id
FEATURE_NOT_FOUND_ID = 'FEATURE_NOT_FOUND'

# ** constant: feature_already_exists_id
FEATURE_ALREADY_EXISTS_ID = 'FEATURE_ALREADY_EXISTS'

# *** constants (data)

# ** constant: feature_not_found_data
FEATURE_NOT_FOUND_DATA = create_default_error_data(
    'Feature Not Found',
    [('en_US', 'Feature not found: {feature_id}.')],
)

# *** constants (groups)

# ** constant: default_errors
DEFAULT_ERRORS = {
    FEATURE_NOT_FOUND_ID: FEATURE_NOT_FOUND_DATA,
}

# *** functions

# ** function: create_default_error_data
def create_default_error_data(name: str,
        messages: List[Tuple[str, str]]) -> Dict[str, Any]:
    '''
    Build a default error definition dictionary.

    :param name: The human-readable error name.
    :type name: str
    :param messages: Ordered (lang, text) message pairs.
    :type messages: List[Tuple[str, str]]
    :return: The error definition dictionary, without its id.
    :rtype: Dict[str, Any]
    '''

    # Assemble and return the error definition.
    return {
        'name': name,
        'message': [{'lang': lang, 'text': text} for lang, text in messages],
    }

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
        Initialize TiferetError.

        :param error_code: The structured error code.
        :type error_code: str
        :param message: Optional human-readable message.
        :type message: str
        :param kwargs: Additional error context.
        :type kwargs: dict
        '''

        # Set the error code and context.
        self.error_code = error_code
        self.kwargs = kwargs

        # Initialize with serialized error data.
        super().__init__(
            json.dumps({'error_code': error_code, 'message': message, **kwargs})
        )

    # * method: raise_error (class)
    @classmethod
    def raise_error(cls, error_code: str, message: str = None, **kwargs):
        '''
        Raise an instance of the class this classmethod is called on.

        :param error_code: The structured error code.
        :type error_code: str
        :param message: Optional human-readable message.
        :type message: str
        :param kwargs: Additional error context.
        :type kwargs: dict
        '''

        # Raise an instance of the class this method is called on.
        raise cls(error_code, message, **kwargs)
```

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/assets.md
