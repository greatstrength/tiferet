# Assets in Tiferet

## Overview

`tiferet/assets/` is the dependency-light foundation of the framework. It owns constant catalogs, small factory functions, and standalone exceptions that the other packages consume. It does not import another Tiferet package.

Assets are reached through the root alias:

```python
from tiferet import a
```

`a` is the first root export and always means `tiferet.assets`. Framework modules use the same alias with `from .. import a`; consumer application assets remain a separate concern and must not reuse this name as a framework import.

## Package Layout

```text
tiferet/assets/
├── __init__.py  — package exports and module aliases
├── core.py      — shared paths, factories, TiferetError, TiferetAPIError
├── app.py       — default app sessions, services, and constants
├── cli.py       — default CLI commands and arguments
├── di.py        — DI default registration data
├── error.py     — catalogued domain-error definitions
├── feature.py   — default feature definitions
└── logging.py   — default logging definitions
```

`assets.__init__` exports the exception types, `ERROR_NOT_FOUND_ID`, and the grouped modules `core`, `error`, `app`, `feat`, `cli`, and `logging`. The `cli_app`, `cli_svc`, `cli_feat`, and `cli_cmd` aliases retain the grouped bootstrap vocabulary used by the built-in CLI surface.

## Artifact Kinds

Assets contains only five artifact kinds:

- `# *** imports` for standard-library or third-party primitives;
- `# *** constants` for `SCREAMING_SNAKE_CASE` values and catalogs;
- `# *** functions` for stateless factories;
- `# *** classes` for standalone types such as `TiferetError`;
- `# *** exports` in `__init__.py`.

Each constant, function, and class has its own `# **` artifact label. Catalogs may use correlated `ids`, `data`, and `groups` constant sections: an identifier keys a factory-built data definition in a group mapping. The consuming cache-seeding decorator reconstructs the domain object; assets itself keeps only primitive data.

## Default Catalogs

`error.py` contains catalogueable domain outcomes. Infrastructure failures are not entries in this catalog: they are `ServiceError` values whose code and inline message stay with their raising service.

`app.py` owns the default app service registrations, constants, and built-in app-session definitions. `feature.py`, `cli.py`, and `logging.py` supply the parallel defaults for their domains. Blueprint cache builders consume these catalogs through the corresponding `add_default_*` decorators; assets never constructs a context or container.

## Boundaries

Assets provides framework-wide primitive definitions and their public aliases. It does not define domain models, events, services, repositories, contexts, or blueprint orchestration. Those packages may consume `a`; they may not make assets depend on them.

## Related Documentation

- [code_style.md](code_style.md) — artifact comments and formatting
- [blueprints.md](blueprints.md) — bootstrap cache composition
- [../guides/assets.md](../guides/assets.md) — catalog and alias strategy
