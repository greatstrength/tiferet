# Assets – The Catalog and Factory Pattern

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/assets/`  
**Version:** 2.0.0

## Overview

`tiferet/assets/` is the dependency-light foundation every other layer builds on: it never imports from `domain`, `events`, `mappers`, `interfaces`, `repos`, `contexts`, or `blueprints`. This guide distills the pattern that recurs across every default catalog in the layer — error definitions, app service dependencies, feature workflows, app sessions, logging configuration, CLI commands — regardless of which domain the catalog eventually reconstitutes. For the two exception classes the layer also hosts (`TiferetError`, `TiferetAPIError`), see [docs/guides/errors.md](errors.md) instead — this guide is scoped to the constant/factory/catalog pattern, not the exception vocabulary.

**Vision:** See `docs/core/assets.md` for the layer's code-style role and artifact-kind constraints; this guide covers the cross-cutting catalog *pattern* those artifacts are built from.

## Ubiquitous Language

- **ID constant** — a `SCREAMING_SNAKE_CASE` string constant naming one catalog entry (e.g. `FEATURE_NOT_FOUND_ID`). Always the sole source of an entry's identifier.
- **Data constant** — the entry's definition, built by a `create_default_*` factory and **never** carrying its own id — the id lives only on the ID constant that keys it in the group dict.
- **Group dict** — the `CORE_DEFAULT_*` / `ADMIN_DEFAULT_*` mapping from ID constant to data constant that a bootstrap decorator iterates over.
- **Default-entry workflow** — the three-step sequence (ID constant → data constant via factory → group dict entry) used to add any new default catalog row.
- **Cache seeding** — the process by which a bootstrap `add_default_*` decorator (`tiferet/contexts/`) reconstitutes each group-dict entry into a domain object and stores it in the shared `CacheContext` under a dedicated prefix, re-injecting the id the data constant deliberately omitted.

## The ids / data / groups Catalog Pattern

Every default catalog in `assets/` — `assets/error.py`'s `CORE_DEFAULT_ERRORS`, `assets/app.py`'s `CORE_DEFAULT_SERVICES`/`CORE_DEFAULT_CONSTANTS`, `assets/feature.py`'s default features, `assets/logging.py`'s formatters/handlers/loggers, `assets/cli.py`'s default commands — follows the same three-section shape:

```python
# *** constants (ids)
FEATURE_NOT_FOUND_ID = 'FEATURE_NOT_FOUND'

# *** constants (data)
FEATURE_NOT_FOUND_DATA = create_default_error_data(
    'Feature Not Found',
    [(EN_US, 'Feature not found: {feature_id}.')],
)

# *** constants (groups)
CORE_DEFAULT_ERRORS = {
    FEATURE_NOT_FOUND_ID: FEATURE_NOT_FOUND_DATA,
}
```

**The id is never duplicated.** Every `create_default_*` factory deliberately omits an `id`/`service_id`/`key` parameter — the definition is always stored under its owning `*_ID` constant as the group-dict key, so the consuming `add_default_*` decorator re-injects the id from that key when it reconstitutes the domain object. Restating the id inside the data constant would create two sources of truth for the same value.

**Admin/core layering:** an admin-scoped catalog (e.g. `ADMIN_DEFAULT_SERVICES`) extends the core one with `{**CORE_DEFAULT_SERVICES, ...}` — always in the mandatory multi-line hanging-indent form, even for a pure spread with no additional entries (see [code_style.md § Constant declaration style](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md)).

## The `create_default_*_data` Factory Family

Each factory builds one data constant's dict shape and lives in `assets/core.py`, imported by the domain-specific asset module that calls it:

| Factory | Builds | Consumed by |
|---|---|---|
| `create_default_error_data(name, messages)` | An `Error` definition | `add_default_errors` (`contexts/error.py`) |
| `create_service_dependency(module_path, class_name, parameters=None)` | The shared base shape for any `ServiceDependency` | The two factories below |
| `create_app_service_dependency_data(...)` | An `AppServiceDependency` definition | `add_default_app_services` / `add_default_admin_services` (`contexts/app.py`) |
| `create_service_registration_data(...)` | A `ServiceRegistration` definition | DI-layer registration seeding |
| `create_default_feature_data(name, group_id, feature_key, steps, ...)` | A `Feature` workflow definition | `add_default_features` |
| `create_params_schema(**params)` | A `params_schema` dict for a feature definition | Passed as `create_default_feature_data`'s `params_schema` argument |
| `create_default_app_session_data(name, description=None)` | An `AppSession` definition | `add_default_app_sessions` (`contexts/app.py`) |
| `create_default_formatter` / `create_default_handler` / `create_default_logger` | Logging configuration entries | `LoggingSettings` assembly (`contexts/logging.py`) |
| `create_default_cli_argument` / `create_default_cli_command_data` | CLI argument/command definitions | `add_default_cli_commands` |
| `create_service_module_path(app_base_path, base_path, domain_path)` | A fully-qualified module path string (e.g. `'tiferet.repos.error'`) | Every `*_data` factory above, to build `module_path` |

Optional fields follow a uniform pattern: a factory parameter defaulting to `None` is added to the returned dict only `if <param> is not None`, so an omitted optional field is truly absent from the dict rather than present with a `None` value.

## Adding a New Default Entry

1. **ID constant** — add a `# ** constant: <name>_id` under `# *** constants (ids)`, value `'SCREAMING_SNAKE_NAME'`.
2. **Data constant** — add a `# ** constant: <name>_data` under `# *** constants (data)`, built via the matching `create_default_*` factory. Never pass an id/key to the factory.
3. **Group dict entry** — add `<NAME>_ID: <NAME>_DATA` to the relevant `CORE_DEFAULT_*` dict under `# *** constants (groups)`, in the multi-line hanging-indent form.
4. **Bootstrap wiring** (outside `assets/`) — confirm an `add_default_*` decorator in the corresponding `contexts/` module already consumes that group dict; if the catalog is new, that decorator needs to exist too.

## Cache Seeding via `add_default_*` Decorators

The catalog itself only produces plain dicts — reconstitution into domain objects happens outside `assets/`, in `contexts/`. Each `add_default_*` decorator (e.g. `add_default_app_services`, `add_default_app_sessions`, `add_default_errors`) wraps a cache-builder callable: after the wrapped builder constructs the `CacheContext`, the decorator iterates the group dict, calls `<DomainObject>.model_validate({**data, 'id_field': id})` to re-inject the id, and stores the result under a dedicated cache-key prefix (e.g. `APP_SERVICE_CACHE_PREFIX = ('app', 'services')`). Consumers read the seeded catalog back directly via `cache.get_by_prefix(...)` / `cache.get(...)` against that prefix (as `blueprints/core.py` and `blueprints/admin.py` do); a single-caller `get_default_*` accessor is no longer interposed for the app and admin catalogs, though `get_default_cli_commands` remains as a genuinely shared, multi-caller case. This indirection is why a data constant never carries its own id: the cache key *is* the id, and the decorator is the single place that reunites them.

## When to Deviate

A catalog that only ever has one entry (no meaningful "many rows" shape) does not need the full ids/data/groups three-way split — a single well-named constant is enough. Introduce the split only once a module has more than a handful of related default entries that benefit from a uniform shape.

## Boundaries

**Inside this domain:** the id/data/groups catalog shape, the `create_default_*` factory family, and the default-entry workflow for adding a new catalog row.
**Outside this domain:** the two exception classes (`TiferetError`/`TiferetAPIError`) also hosted in `assets/core.py` — see [docs/guides/errors.md](errors.md); reconstituting a group dict into cached domain objects via `add_default_*` decorators — that orchestration lives in `contexts/`, not `assets/`; the artifact-comment/spacing conventions governing how these constants are labeled — see `docs/core/assets.md` and `docs/core/code_style.md`.

## Root-Level Alias and the Import-Order Exception

`a` — this layer's established internal alias (`from .. import assets as a`) — is also exported from the framework root as `from tiferet import a`, making it the one name every layer, including consumer code, can rely on to mean `tiferet.assets`. Framework-internal modules that need `assets` now resolve it the same way consumers do, via `from .. import a`, rather than importing the `assets` submodule directly. This is a deliberate, singular exception to the general rule that inner layers do not depend on the aggregating root package — justified only because `assets` is this dependency-light and already sits beneath every other layer. It works because `tiferet/__init__.py` binds `a` before importing any dependent layer; that ordering is a hard invariant backed by a dedicated AST-based test, not a convention to be maintained by memory. See `docs/core/assets.md` for the artifact-kind detail.

## Related Documentation

- [docs/guides/errors.md](errors.md) — `TiferetError`/`TiferetAPIError`, the other artifact kind this layer hosts
- [docs/core/assets.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/assets.md) — assets layer artifact kinds and code-style conventions
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — constant declaration style and artifact comments
