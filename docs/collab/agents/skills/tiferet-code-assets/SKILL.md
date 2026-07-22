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

**Sub-groups** — partition a large `# *** constants` section with a parenthetical qualifier. The framework convention (e.g. `assets/error.py`) uses three sub-groups:
```python
# *** constants (ids)               ← raw error-code identifier strings
# ** constant: feature_not_found_id
FEATURE_NOT_FOUND_ID = 'FEATURE_NOT_FOUND'

# *** constants (errors)            ← assembled default definition dicts
# ** constant: feature_not_found
FEATURE_NOT_FOUND = { 'id': FEATURE_NOT_FOUND_ID, 'name': 'Feature Not Found', ... }

# *** constants (groups)            ← catalog dicts grouping the above
# ** constant: default_errors
DEFAULT_ERRORS = { FEATURE_NOT_FOUND_ID: FEATURE_NOT_FOUND }
```

## Key conventions

- **Layer boundary — valid `# ** app` imports:** none. `assets` is the root layer; it has no framework imports. Only `# ** core` (stdlib) and `# ** infra` (minimal third-party, e.g. `json`) are valid. Never import from any other framework layer.
- **Constants:** `SCREAMING_SNAKE_CASE`. Each constant has its own `# ** constant: <snake_case>` label. Do not group multiple constants under a single `# ** constants: <group>` mid-level label — use a top-level sub-group instead.
- **Structured defaults:** Build structured default data from a factory function (e.g. `create_default_error`), not inline dicts. Define each entry as a named constant, then assemble the catalog dict as a separate constant.
- **Functions:** Small, stateless, no framework dependencies. Use RST docstrings.
- **Classes:** Plain standalone classes (exception types, data primitives). Use `# *** classes` / `# ** class: <name>`, `# * attribute: <name>`, `# * init`.
- **Exports:** Only in `__init__.py` under `# *** exports`. Use short module aliases for frequently consumed modules (e.g. `from . import constants as const`).

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

# *** constants (errors)

# ** constant: feature_not_found
FEATURE_NOT_FOUND = {
    'id': FEATURE_NOT_FOUND_ID,
    'name': 'Feature Not Found',
    'message': [{'lang': 'en_US', 'text': 'Feature not found: {feature_id}.'}],
}

# *** constants (groups)

# ** constant: default_errors
DEFAULT_ERRORS = {
    FEATURE_NOT_FOUND_ID: FEATURE_NOT_FOUND,
}

# *** functions

# ** function: create_default_error
def create_default_error(id: str,
        name: str,
        messages: List[Tuple[str, str]]) -> Dict[str, Any]:
    '''
    Build a default error definition dictionary.

    :param id: The unique error identifier.
    :type id: str
    :param name: The human-readable error name.
    :type name: str
    :param messages: Ordered (lang, text) message pairs.
    :type messages: List[Tuple[str, str]]
    :return: The error definition dictionary.
    :rtype: Dict[str, Any]
    '''

    # Assemble and return the error definition.
    return {
        'id': id,
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
```

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/assets.md
