---
name: tiferet-code-blueprints
description: Apply blueprint conventions when adding or modifying blueprint orchestration functions in a Tiferet-family repo. Covers the build_app composition chain, thin entrypoint design, functions vs blueprints sections, and the App/CLI export pattern.
---

# Blueprints Code Style – Tiferet

## When to use
- When adding a new blueprint entrypoint or modifying the application initialization flow in `tiferet/blueprints/`.
- When creating a new interface type (e.g. a web blueprint wrapping Flask or FastAPI).
- When adding a side-effect-free composition helper that feeds into a blueprint.
- Do NOT use for domain logic — blueprints orchestrate, they do not implement.

## Artifact comment structure

Module skeleton (any module):
```
# *** imports
# *** constants          ← optional
# *** functions          ← pure, side-effect-free composition helpers
# *** classes            ← base classes only (core.py modules)
# *** blueprints         ← construct group for this skill
# *** exports            ← __init__.py only
```

Blueprint-specific labels:
```
# *** functions                         ← artifact section: pure, side-effect-free composition helpers
# ** function: <snake_case_name>        ← artifact

# *** blueprints                        ← artifact section: orchestration entry points
# ** blueprint: <snake_case_name>       ← artifact
```

Both sections may appear in the same module. `# *** functions` must appear first. Use `# *** functions` for helpers that take only input args and return a plain value (no I/O, no error raising, no instantiation of domain objects from services). Reserve `# *** blueprints` for the orchestration entry points (e.g. `build_app`, `build_cli`).

## Key conventions

- **Layer boundary — valid `# ** app` imports:** `assets`, `contexts`, `di`, `events`. Events are for pre-DI bootstrap only (`DomainEvent.handle` or a direct event-class import). Domain types come from the context that owns them, never `from ..domain`. Service instances arrive from `di` (`get_dependency`); never import `interfaces`. Never import from `mappers`, `utils`, or `repos`.
- Blueprints are **module-level functions**, not classes.
- Blueprints are **thin orchestrators** — they wire and delegate; they do not implement domain logic.
- The canonical entry point is `build_app` in `tiferet/blueprints/core.py`, exported as `App`. The CLI entry point is `build_cli` in `tiferet/blueprints/cli.py`, exported as `CLI`.
- The `core.build_app` composition chain:
  1. `build_cache()` — build the `CacheContext` pre-seeded with default errors, app services, app constants, app sessions, and logging settings.
  2. `get_app_session(interface_id, cache, ...)` — return a cache-seeded default session when available; otherwise compose the app service and resolve the session via `GetAppSession`.
  3. `build_app_session_context(app_session, cache)` — build the app service container, compose the `ServiceResolver`, then delegate the context graph construction to `compose_session_context`.
  4. `compose_session_context(...)` — wire the injected logger, feature-execution, request-construction, error, and response handlers before binding the app session to `AppSessionContext`.
- `build_cli` builds the CLI cache, resolves the app session, constructs `CliSessionContext` with its CLI parser and runtime handlers, then delegates `argv` to `cli_context.run(argv)`.
- Validate the resolved `AppSessionContext` type (`INVALID_APP_SESSION_TYPE`) in `build_app`.
- Use `TiferetError.raise_error()` for domain-outcome error paths (e.g. `TiferetError.raise_error(a.error.INVALID_APP_SESSION_TYPE_ID, ...)`).
- Module-private helpers are underscore-prefixed.

## Example

```python
# *** imports

# ** core
from typing import Any

# ** app
from . import core

# *** blueprints

# ** blueprint: build_cli
def build_cli(interface_id: str,
        argv: list | None = None,
        **kwargs) -> Any:
    '''
    Build and run a CLI interface.

    Delegates argparse parsing and feature dispatch to CliSessionContext.run.

    :param interface_id: The interface identifier.
    :type interface_id: str
    :param argv: Explicit argv list; defaults to sys.argv[1:].
    :type argv: list | None
    :param kwargs: Additional kwargs forwarded to app-session resolution.
    :type kwargs: dict
    :return: The feature execution result.
    :rtype: Any
    '''

    # Build the CLI cache and resolve the app session.
    cache = build_cli_cache()
    app_session = core.get_app_session(interface_id, cache, **kwargs)

    # Build the CLI context with its parser and runtime handlers.
    cli_context = build_cli_session_context(app_session, cache)

    # Delegate CLI parsing and feature dispatch to the context.
    return cli_context.run(argv)
```

## Docstrings & guides

- **Docstrings & guides:** Blueprint docstrings open with a 1–2 sentence vision-tier value statement, linked via `# >> see: @guides/blueprints.md#<anchor>` to `docs/guides/blueprints.md`, which carries the composition-chain detail. See `tiferet-guide-docs` for the complete convention.

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/blueprints.md
