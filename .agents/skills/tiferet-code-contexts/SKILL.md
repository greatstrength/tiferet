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

**Layer boundary — valid `# ** app` imports:** `assets`, `domain`, sibling contexts, `events`. Never import from `mappers`, `di`, `interfaces`, `repos`, `utils`, or `blueprints`. Prefer blueprint handler injection over constructing sibling contexts. Contexts may call events as a client surface after the blueprint has built them.

**Base class:** All contexts extend `BaseContext` from `tiferet/contexts/core.py`.
- `BaseContext` provides a `ContextMeta` registry keyed by `domain_type`.
- `BaseContext.for_domain(DomainType)` — resolves the registered context class.
- `BaseContext.from_domain(domain_obj, **kwargs)` — constructs a context bound to a domain object; the object is exposed as `ctx.domain`.
- Caching is NOT in the base — declare a `CacheContext` on contexts that need one.

**High-level contexts** (user-facing, e.g. `CliSessionContext`, `FlaskApiContext`):
- Extend `AppSessionContext` (the minimal hub in `tiferet/contexts/app.py`).
- `AppSessionContext` receives five required blueprint-injected handlers — `build_logger_handler`, `execute_feature_handler`, `create_request_handler`, `raise_error_handler`, `response_handler` — plus `get_dependency` and `cache`. CLI adds `parse_cli_args`. These are wired by the blueprint during app initialization.
- Override only the methods your interface specializes (e.g. `parse_request`, `build_response`).

**Low-level contexts** (supporting any domain concern at the app-operation level):
- Extend `BaseContext` directly.
- Declared in `tiferet/contexts/<concern>.py`.
- Not limited to the built-in trio (FeatureContext, ErrorContext, LoggingContext). Framework extensions introduce their own low-level contexts for domain-specific concerns; blueprints and handler injection are the mechanism for composing them alongside the built-in ones.

**`domain_type` ClassVar:**
- Declare on each context to register it in the `ContextMeta` registry.
- `AppSessionContext` declares `domain_type = AppSession`.
- `CliSessionContext` is selected by the CLI blueprint, not by `module_path`/`class_name` on the session.

**Construction:** The blueprint hardcodes the context class for the entry point, then constructs via `BaseContext.from_domain(app_session, **handlers)`. Never instantiate contexts directly with `ContextClass(...)`.

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

# ** context: cli_session_context
class CliSessionContext(AppSessionContext):
    '''
    High-level context for CLI interfaces.

    Extends AppSessionContext with argparse-based command parsing and
    feature dispatch. The loaded AppSession is bound as self.domain via
    from_domain. CLI parsing is owned by this context, not the blueprint.
    '''

    # * method: run
    def run(self, argv: list | None = None, **kwargs) -> Any:
        '''
        Parse argv and dispatch through the inherited hub run.

        :param argv: Explicit argv list; defaults to sys.argv[1:].
        :type argv: list | None
        :param kwargs: Unused; present for signature compatibility.
        :type kwargs: dict
        :return: The feature execution result.
        :rtype: Any
        '''

        # Parse argv via the injected callable.
        feature_id, headers, data = self._parse_cli_args(argv)

        # Delegate to the hub run entry point.
        return super().run(feature_id, headers=headers, data=data)
```

## Docstrings & guides

- **Docstrings & guides:** Context class docstrings open with a 1–2 sentence vision-tier value statement, linked via `# >> see: @guides/contexts.md#<anchor>` to `docs/guides/contexts.md`, which carries the full distillation-tier detail. See `tiferet-guide-docs` for the complete convention.

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md
