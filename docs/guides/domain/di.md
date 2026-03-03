# Domain – DI (Dependency Injection Wiring)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/domain/di.py`  
**Version:** 2.0.0a2

## Overview

The DI domain defines **how services are connected at runtime**. Every domain event that a feature step executes is resolved from the DI container — and the DI domain controls what class is instantiated, what parameters it receives, and which implementation is selected based on active flags.

A `ServiceConfiguration` is a registry entry that maps an identifier to a concrete class. It can optionally carry `FlaggedDependency` overrides that swap the implementation based on the runtime environment (e.g., a YAML-backed repository for production, a mock for testing). The `ContainerContext` reads all service configurations, resolves their types, and builds a live DI injector.

> **Rename note (v2.0a2):** The module was renamed from `container.py` to `di.py` to capture its true role as part of the Dependency Injection infrastructure. `ContainerAttribute` was renamed to `ServiceConfiguration` to align with the event naming (`AddServiceConfiguration`, etc.).

## Domain Objects

### ServiceConfiguration

A single entry in the DI registry. Defines how to resolve a dependency — either from a default type or from a flag-matched override.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `str` (required) | Unique identifier (e.g., `add_number_event`, `feature_service`) |
| `name` | `str` | Optional human-readable name |
| `module_path` | `str` | Default module path for the dependency class |
| `class_name` | `str` | Default class name to import |
| `parameters` | `Dict[str, str]` (default: `{}`) | Default configuration parameters |
| `dependencies` | `List[FlaggedDependency]` (default: `[]`) | Flag-specific implementation overrides |

A `ServiceConfiguration` must have **at least one** type source: either a default `module_path`/`class_name` pair, or one or more `FlaggedDependency` entries. The domain events enforce this invariant.

**Behavior method:**

- `get_dependency(*flags)` — searches flagged dependencies in flag-priority order. Returns the first `FlaggedDependency` whose `flag` matches any of the provided flags, or `None` if no match is found. This enables ordinal flag precedence — the caller lists flags from highest to lowest priority.

### FlaggedDependency

An alternative implementation binding activated by a specific flag. When the runtime's active flags match, this dependency's `module_path`/`class_name` is used instead of the default.

| Attribute | Type | Description |
|-----------|------|-------------|
| `module_path` | `str` (required) | Module path for the flag-specific implementation |
| `class_name` | `str` (required) | Class name for the flag-specific implementation |
| `flag` | `str` (required) | The flag that activates this dependency |
| `parameters` | `Dict[str, str]` (default: `{}`) | Flag-specific configuration parameters |

### Flag Resolution

Flags flow from two sources:

1. **`AppInterface.flags`** — set per-interface in `app.yml`.
2. **`FeatureEvent.flags`** and **`Feature.flags`** — set per-step or per-feature in `feature.yml`.

At resolution time, `ContainerContext` combines these flags and passes them to `get_dependency()`. This enables scenarios like:

- A `feature_service` that uses `FeatureYamlRepository` by default but switches to `FeatureSqliteRepository` when the `sqlite` flag is active.
- A `data_service` that uses different storage backends depending on the app interface configuration.

## Runtime Role

`ContainerContext` is the sole consumer of the DI domain at runtime. The flow is:

1. **`build_injector(flags)`** retrieves all `ServiceConfiguration` entries via `ListAllSettings`.
2. For each configuration:
   - **`get_attribute_type(attribute, *flags)`** checks `FlaggedDependency` entries in flag-priority order. If a match is found, that class is used. Otherwise, the default `module_path`/`class_name` is used.
   - Each resolved class is imported via `ImportDependency.execute()`.
3. **`load_constants(attributes, constants, flags)`** collects parameters from the matched dependencies (or defaults) and parses them via `ParseParameter`.
4. All resolved types and constants are passed to `create_injector`, which builds the DI container.
5. **`get_dependency(attribute_id, *flags)`** retrieves a live instance from the built injector.

The injector is cached per flag combination, so repeated calls with the same flags reuse the same container.

```python
# FeatureContext loading a domain event from the container:
cmd = self.container.get_dependency(
    feature_command.attribute_id,    # e.g., 'add_number_event'
    *combined_flags,                 # e.g., ['default']
)
result = cmd.execute(**request.data)
```

## Configuration

Service configurations are defined in `app/configs/container.yml`:

```yaml
attrs:
  add_number_event:
    module_path: app.events.calc
    class_name: AddNumber
  feature_service:
    module_path: tiferet.repos.feature
    class_name: FeatureYamlRepository
    params:
      feature_yaml_file: app/configs/feature.yml
    dependencies:
      - flag: sqlite
        module_path: tiferet.repos.feature_sqlite
        class_name: FeatureSqliteRepository
        params:
          db_path: app/data/features.db
```

Each key under `attrs` becomes the `ServiceConfiguration.id`. The `dependencies` list maps to `FlaggedDependency` entries, enabling environment-specific overrides without changing the feature configuration.

## Domain Events

| Event | Purpose |
|-------|---------|
| `ListAllSettings` | Retrieve all service configurations and constants (used during injector build) |
| `AddServiceConfiguration` | Register a new service configuration |
| `SetDefaultServiceConfiguration` | Update the default type and parameters |
| `SetServiceDependency` | Add or update a flagged dependency |
| `RemoveServiceDependency` | Remove a flagged dependency (validates at least one type source remains) |
| `RemoveServiceConfiguration` | Delete a service configuration |
| `SetServiceConstants` | Set or clear container-level constants |

## Service Interface

`ContainerService` (`tiferet/interfaces/container.py`) — abstracts CRUD access to service configurations and constants.

## Relationship to Other Domains

- **Feature domain** — Every `FeatureEvent.attribute_id` references a `ServiceConfiguration.id`. The DI container resolves the domain event class that the feature step executes.
- **App domain** — `AppInterface.flags` controls which flagged dependencies are activated. `AppServiceDependency` entries on the interface are wired separately (at bootstrap), but often reference the same implementation classes registered here.
- **Error domain** — Error service implementations (e.g., `ErrorYamlRepository`) are registered as service configurations and resolved via the DI container.

## Related Documentation

- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — DomainObject base class and general patterns
- [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md) — Context conventions and lifecycle
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns
- [docs/guides/domain/feature.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/feature.md) — Feature domain guide
- [docs/guides/domain/app.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/app.md) — App domain guide
