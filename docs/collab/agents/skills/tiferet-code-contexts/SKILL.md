---
name: tiferet-code-contexts
description: Apply context conventions when adding or modifying runtime contexts in a Tiferet-family repo. Covers BaseContext registry, AppSessionContext hub, high-level vs low-level contexts, domain_type, and from_domain construction.
---

# Contexts Code Style – Tiferet

## When to use
- When adding a new context class or modifying an existing one in `tiferet/contexts/`.
- When extending `AppSessionContext` for a new high-level interface (e.g. Flask API, gRPC).
- When adding behavior to a low-level context (`FeatureContext`, `ErrorContext`, `LoggingContext`).

## Artifact comment structure

```
# *** contexts                          ← top-level
# ** context: <snake_case_name>         ← individual context
# * attribute: <name>                   ← instance attributes (type hints)
# * attribute: domain_type              ← ClassVar mapping this context to its domain type
# * init                                ← constructor
# * method: <name>                      ← runtime behavior methods
```

## Key conventions

**Base class:** All contexts extend `BaseContext` from `tiferet/contexts/settings.py`.
- `BaseContext` provides a `ContextMeta` registry keyed by `domain_type`.
- `BaseContext.for_domain(DomainType)` — resolves the registered context class.
- `BaseContext.from_domain(domain_obj, **kwargs)` — constructs a context bound to a domain object; the object is exposed as `ctx.domain`.
- Caching is NOT in the base — declare a `CacheContext` on contexts that need one.

**High-level contexts** (user-facing, e.g. `FlaskApiContext`):
- Extend `AppSessionContext` (the minimal hub in `tiferet/contexts/app.py`).
- The `AppSessionContext` hub takes event collaborators (`get_feature_evt`, `get_error_evt`, `logging_list_all_evt`), `get_dependency`, and optional `cache` and defaults. It binds the loaded `AppSession` via `from_domain` and exposes `self.domain.id`.
- Override only the methods your interface specializes (e.g. `parse_request`).

**Low-level contexts** (supporting, e.g. `FeatureContext`, `ErrorContext`):
- Extend `BaseContext` directly.
- Declared in `tiferet/contexts/<concern>.py`.

**`domain_type` ClassVar:**
- Declare on each context to register it in the `ContextMeta` registry.
- `AppSessionContext` declares `domain_type = AppSession`.
- `CliContext` intentionally omits `domain_type` — it is selected via the interface config's `module_path`/`class_name`, not the registry.

**Construction:** The blueprint resolves the context class from `module_path`/`class_name`, then constructs via `BaseContext.from_domain(app_session, **collaborators)`. Never instantiate contexts directly with `ContextClass(...)`.

**`run(feature_id, headers, data, **kwargs)`** is the standard high-level execution entry point (inherited from `AppSessionContext`).

## Example

```python
# *** imports

# ** app
from .settings import BaseContext
from .app import AppSessionContext
from ..domain import AppSession

# *** contexts

# ** context: flask_api_context
class FlaskApiContext(AppSessionContext):
    '''
    High-level context for Flask API interfaces.

    Extends AppSessionContext with Flask-specific request parsing.
    The loaded AppSession is bound as self.domain via from_domain.
    '''

    # * attribute: domain_type
    domain_type = AppSession

    # * attribute: flask_handler
    flask_handler: object

    # * init
    def __init__(self, flask_handler, **kwargs):
        '''
        Initialize the Flask API context.

        :param flask_handler: The Flask application handler.
        :type flask_handler: object
        :param kwargs: Hub collaborators forwarded to AppSessionContext.
        :type kwargs: dict
        '''

        # Forward all hub collaborators to the parent context.
        super().__init__(**kwargs)

        # Store the Flask handler.
        self.flask_handler = flask_handler

    # * method: parse_flask_request
    def parse_flask_request(self, flask_request) -> dict:
        '''
        Parse a Flask request into a data dict for feature execution.

        :param flask_request: The Flask request object.
        :type flask_request: object
        :return: A dict of feature input data.
        :rtype: dict
        '''

        # Extract and return the JSON payload from the request.
        return flask_request.get_json(force=True) or {}
```

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md
