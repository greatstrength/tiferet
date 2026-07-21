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

```
# *** functions                         ← pure, side-effect-free composition helpers
# ** function: <snake_case_name>        ← individual helper

# *** blueprints                        ← orchestration entry points
# ** blueprint: <snake_case_name>       ← individual blueprint function
```

Both sections may appear in the same module. `# *** functions` must appear first. Use `# *** functions` for helpers that take only input args and return a plain value (no I/O, no error raising, no instantiation of domain objects from services). Reserve `# *** blueprints` for the orchestration entry points (e.g. `build_app`, `build_cli`).

## Key conventions

- Blueprints are **module-level functions**, not classes.
- Blueprints are **thin orchestrators** — they wire and delegate; they do not implement domain logic.
- The canonical entry point is `build_app` in `tiferet/blueprints/core.py`, exported as `App`. The CLI entry point is `build_cli` in `tiferet/blueprints/cli.py`, exported as `CLI`.
- The `core.build_app` composition chain:
  1. `build_cache()` — build the `CacheContext` pre-seeded with framework defaults
  2. `get_app_session(interface_id, cache, ...)` — resolve the app session via `GetAppSession`
  3. `build_app_session_context(app_session, cache)` — build the app service container, compose the `ServiceResolver`, import the context class, and construct via `from_domain`
- `build_cli` is a thin entrypoint: call `core.build_app(...)` then `cli_context.run_cli(argv)`.
- Always validate the resolved context type (`INVALID_APP_SESSION_TYPE`) in single-call entry points.
- Use `RaiseError.execute()` for all error paths.
- Module-private helpers are underscore-prefixed (`_resolve_bootstrap_session`).

## Example

```python
# *** imports

# ** core
from typing import Any

# ** app
from .core import build_app as _core_build_app
from ..events.static import RaiseError
from .. import assets as a

# *** functions

# ** function: _derive_argv
def _derive_argv(argv: list | None) -> list:
    '''
    Return argv as-is or fall back to sys.argv[1:].

    :param argv: Explicit argv list, or None to use sys.argv.
    :type argv: list | None
    :return: The resolved argv list.
    :rtype: list
    '''

    # Import sys only when needed.
    import sys

    # Return the explicit argv or fall back to sys.argv.
    return argv if argv is not None else sys.argv[1:]

# *** blueprints

# ** blueprint: build_cli
def build_cli(interface_id: str,
        argv: list | None = None,
        **kwargs) -> Any:
    '''
    Build and run a CLI interface.

    Delegates argparse parsing and feature dispatch to CliContext.run_cli.

    :param interface_id: The interface identifier.
    :type interface_id: str
    :param argv: Explicit argv list; defaults to sys.argv[1:].
    :type argv: list | None
    :param kwargs: Additional kwargs forwarded to core.build_app.
    :type kwargs: dict
    :return: The feature execution result.
    :rtype: Any
    '''

    # Resolve the argv list.
    resolved_argv = _derive_argv(argv)

    # Build the app context (must resolve to a CliContext).
    cli_context = _core_build_app(interface_id, **kwargs)

    # Delegate CLI parsing and feature dispatch to the context.
    return cli_context.run_cli(resolved_argv)
```

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/blueprints.md
