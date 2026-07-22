---
name: tiferet-code-contexts
description: Apply context conventions when adding or modifying runtime contexts in a Tiferet-family repo. Covers BaseContext registry, AppSessionContext hub, high-level vs low-level contexts, domain_type, and from_domain construction.
---

# Contexts Code Style – Tiferet

## When to use
- When adding a new context class or modifying an existing one in `tiferet/contexts/`.
- When extending `AppSessionContext` for a new high-level interface (e.g. CLI, web API, gRPC).
- When adding behavior to a low-level context (`FeatureContext`, `ErrorContext`, `LoggingContext`) or introducing a new domain-specific context for a framework extension.

## Artifact comment structure

Module skeleton (any module):
```
# *** imports
# *** constants          ← optional
# *** functions          ← optional; side-effect-free module helpers
# *** classes            ← base classes only (core.py modules)
# *** contexts           ← construct group for this skill
# *** exports            ← __init__.py only
```

Context-specific labels:
```
# *** contexts                          ← artifact section
# ** context: <snake_case_name>         ← artifact
# * attribute: <name>                   ← artifact member: instance attributes (type hints)
# * attribute: domain_type              ← artifact member: ClassVar mapping this context to its domain type
# * init                                ← artifact member: constructor
# * method: <name>                      ← artifact member: runtime behavior methods
```

## Key conventions

**Layer boundary — valid `# ** app` imports:** `assets`, `domain`, `events`, `mappers`, `di`. Never import from `repos` or `utils` directly (resolved via DI at runtime), or from `blueprints`.

**Base class:** All contexts extend `BaseContext` from `tiferet/contexts/core.py`.
- `BaseContext` provides a `ContextMeta` registry keyed by `domain_type`.
- `BaseContext.for_domain(DomainType)` — resolves the registered context class.
- `BaseContext.from_domain(domain_obj, **kwargs)` — constructs a context bound to a domain object; the object is exposed as `ctx.domain`.
- Caching is NOT in the base — declare a `CacheContext` on contexts that need one.

**High-level contexts** (user-facing, e.g. `CliContext`, `FlaskApiContext`):
- Extend `AppSessionContext` (the minimal hub in `tiferet/contexts/app.py`).
- `AppSessionContext` receives blueprint-injected handler callables — `execute_feature_handler`, `create_request_handler`, `raise_error_handler`, `response_handler` — plus `get_dependency`, `logging_context`, and `cache`. These are wired by the blueprint during app initialization, not declared as named event collaborators.
- Override only the methods your interface specializes (e.g. `parse_request`, `build_response`).

**Low-level contexts** (supporting any domain concern at the app-operation level):
- Extend `BaseContext` directly.
- Declared in `tiferet/contexts/<concern>.py`.
- Not limited to the built-in trio (FeatureContext, ErrorContext, LoggingContext). Framework extensions introduce their own low-level contexts for domain-specific concerns; blueprints and handler injection are the mechanism for composing them alongside the built-in ones.

**`domain_type` ClassVar:**
- Declare on each context to register it in the `ContextMeta` registry.
- `AppSessionContext` declares `domain_type = AppSession`.
- `CliContext` intentionally omits `domain_type` — it is selected via the interface config's `module_path`/`class_name`, not the registry.

**Construction:** The blueprint resolves the context class from `module_path`/`class_name`, then constructs via `BaseContext.from_domain(app_session, **collaborators)`. Never instantiate contexts directly with `ContextClass(...)`.

**`run(feature_id, headers, data, **kwargs)`** is the standard high-level execution entry point (inherited from `AppSessionContext`).

## Example

```python
# *** imports

# ** core
import sys
from typing import Any

# ** app
from .core import BaseContext
from .app import AppSessionContext
from ..domain import AppSession

# *** contexts

# ** context: cli_context
class CliContext(AppSessionContext):
    '''
    High-level context for CLI interfaces.

    Extends AppSessionContext with argparse-based command parsing and
    feature dispatch. The loaded AppSession is bound as self.domain via
    from_domain. CLI parsing is owned by this context, not the blueprint.
    '''

    # * method: run_cli
    def run_cli(self, argv: list | None = None) -> Any:
        '''
        Parse argv and dispatch the resolved feature request.

        :param argv: Explicit argv list; defaults to sys.argv[1:].
        :type argv: list | None
        :return: The feature execution result.
        :rtype: Any
        '''

        # Resolve argv, falling back to sys.argv.
        resolved = argv if argv is not None else sys.argv[1:]

        # Parse the CLI request into feature_id and data.
        feature_id, data = self.parse_cli_request(resolved)

        # Delegate to the standard run entry point.
        return self.run(feature_id=feature_id, data=data)
```

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md
