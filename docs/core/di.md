# Dependency Injection in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

`di` is resolution: a declared service id plus flags becomes a live instance. That position is **Chesed**.

Legal `# ** app` imports: `domain`; `interfaces` (including `ServiceError`). Illegal: `assets`; `events` until a concrete resolution problem exists that `ServiceError` plus an injected callable cannot solve; `repos`; `blueprints`; `contexts`; `mappers`; `utils`. The layer stays event-free and asset-free. A missing provider raises `ServiceError`. See [architecture.md](architecture.md).

The package is two modules:

- **`tiferet/di/core.py`** — the abstract, domain-only core: the `ServiceContainer` and `ServiceResolver` ABCs plus the pure module functions `injectable_parameter_names` and `normalize_flags`. It imports only the standard library and `..domain` (`ServiceDependency`).
- **`tiferet/di/dependency_injector.py`** — the concrete implementations backed by `dependency_injector`: `DIDynamicServiceContainer` (feature-level, `Factory` scope), `DIAppServiceContainer` (app-level, `Singleton` scope), and `DIDynamicServiceResolver` (per-flag feature resolver). It imports `..interfaces.di` (`DIService`) and `..interfaces.core` (`ServiceError`). There is no `di/settings.py`.

Parameter parsing (e.g. `$env.` references) is injected as a `parse_parameter` callable so DI never imports `ParseParameter` itself.

App-level core services resolve as shared **Singletons** (`DIAppServiceContainer`), while feature-level services resolve per flag set as **Factories** (`DIDynamicServiceResolver`). Contexts (`AppSessionContext`, `FeatureContext`) consume an injected `get_dependency` callable rather than holding a provider or container directly.

This document describes the structure, design principles, and best practices for the DI layer, adhering to Tiferet's structured code style ([docs/core/code_style.md](code_style.md)).

## Module Functions

The DI package exposes pure, side-effect-free helpers under `# *** functions`:

- **`injectable_parameter_names(service_type)`** (`di/core.py`) — Returns a service type's injectable constructor parameter names, excluding `self` and variadic parameters. Used by every container's `build_factory` / `build_singleton`.
- **`normalize_flags(*flags)`** (`di/core.py`) — Flattens a mixed sequence of strings, lists, and tuples into a flat list of strings. Re-exported from `tiferet/di/__init__.py`.

## Abstract DI Contract (`di/core.py`)

`di/core.py` defines the framework's abstract DI contract. It is **domain-only** — it imports the standard library and `..domain` (`ServiceDependency`) and nothing from `..interfaces` — so the abstract layer never depends on service interfaces or events.

### `ServiceContainer` (ABC)

The `ServiceContainer` ABC is the container contract that concrete engines implement. Its methods are keyed on the core `ServiceDependency` domain model:

- **`add_service(service_id, service: ServiceDependency)`** — Register a service dependency. Implementations register the dependency's declared `parameters` as constants (taking precedence) before registering the service.
- **`add_constant(constant_id, value)`** — Register a single constant value.
- **`get_dependency(dependency_id)`** — Resolve a registered service or constant by id.
- **`remove_dependency(dependency_id)`** — Remove a registered dependency (idempotent).
- **`load_container(services, constants)`** — Bulk-load the container from service dependencies and constants (constants first so factories can wire to them).

### `ServiceResolver` (ABC)

The `ServiceResolver` ABC owns a per-flag `ServiceContainer` cache and a concrete **template-method** `get_dependency`; only `build_container` is abstract. Subclasses implement `build_container(flags)` and inherit the caching/resolution flow for free:

- **`add_container(container, *flags)` / `get_container(*flags)`** — Cache and retrieve containers keyed by the normalized flag tuple (`tuple(normalize_flags(*flags))`).
- **`build_container(flags)`** (abstract) — Build a `ServiceContainer` for a flag set.
- **`get_dependency(service_id, *flags)`** (template) — Normalize flags, retrieve the cached container (building and caching one on a miss), then delegate to `container.get_dependency(service_id)`.

```python
# tiferet/di/core.py (excerpt)

# ** class: service_resolver
class ServiceResolver(ABC):

    # * method: get_dependency
    def get_dependency(self, service_id: str, *flags) -> Any:
        # Normalize the provided flags.
        normalized = normalize_flags(*flags)

        # Retrieve the cached container, building and caching one on a miss.
        container = self.get_container(*normalized)
        if container is None:
            container = self.add_container(self.build_container(normalized), *normalized)

        # Resolve the dependency from the container.
        return container.get_dependency(service_id)
```

Keeping `di_service` off the base preserves the domain-only boundary; the DI-bound state lives on the concrete resolver in `dependency_injector.py`.

## Dependency-Injector Implementations (`di/dependency_injector.py`)

`di/dependency_injector.py` provides the concrete `dependency_injector`-backed implementations. It may import `..interfaces.di` (`DIService`) in addition to `..domain`.

### `DIDynamicServiceContainer`

The feature-level container. It adapts the `ServiceContainer` contract to a `dependency_injector` `DynamicContainer`, registering services as **`Factory`** providers (a new instance per resolution) and constants as **`Object`** providers. `add_service` registers the dependency's `parameters` as constants first, resolves the concrete type via `ServiceDependency.get_service_type()`, then wires constructor kwargs to sibling providers via `build_factory` (using `injectable_parameter_names`). `load_container` registers constants before services.

### `DIAppServiceContainer`

The app-level container, a subclass of `DIDynamicServiceContainer` that registers services as **`Singleton`** providers (one shared instance per app) instead of Factories. It overrides `add_service` to call `build_singleton` and adds a `from_dependencies` classmethod that keys a list of `AppServiceDependency` objects by their `service_id`:

```python
# tiferet/di/dependency_injector.py (excerpt)

# ** class: di_app_service_container
class DIAppServiceContainer(DIDynamicServiceContainer):

    # * method: from_dependencies (class)
    @classmethod
    def from_dependencies(cls, services=None, constants=None):
        # Key the app service dependencies by their service id.
        services_by_id = {service.service_id: service for service in (services or [])}

        # Construct and load the container (constants first, then services).
        return cls(services=services_by_id, constants=constants)
```

The blueprint `build_app_service_container` (`tiferet/blueprints/core.py`) composes this container from the framework defaults seeded on the shared cache plus the interface's own service/constant overrides. Because the core catalog registers repositories before the events that depend on them, and constants before services, each Singleton's constructor kwargs wire to already-registered sibling providers.

### `DIDynamicServiceResolver`

The concrete feature-level resolver. It holds a `DIService` and an injected `parse_parameter` callable (default identity), and implements `build_container` by reading `di_service.list_all()`, parsing constants, and unpacking each `ServiceRegistration` into an effective core `ServiceDependency` (via `resolve_service`, below) before building a `DIDynamicServiceContainer`:

```python
# tiferet/di/dependency_injector.py (excerpt)

# * method: build_container
def build_container(self, flags: List[str] = None) -> ServiceContainer:
    # Read the registrations and top-level constants from the DI service.
    registrations, constants = self.di_service.list_all()

    # Parse the top-level constants once.
    constants = {key: self.parse_parameter(value) for key, value in constants.items()}

    # Unpack each registration into an effective dependency for these flags.
    services = {}
    for registration in registrations:
        dependency = registration.resolve_service(*(flags or []))
        if dependency is None:
            continue
        services[registration.id] = ServiceDependency(
            module_path=dependency.module_path,
            class_name=dependency.class_name,
            parameters={k: self.parse_parameter(v) for k, v in (dependency.parameters or {}).items()},
        )

    # Build the container (constants first, then services).
    return DIDynamicServiceContainer(services=services, constants=constants)
```

### `ServiceRegistration.resolve_service`

The flagged-override → default → `None` selection used during a build lives in one place on the `ServiceRegistration` domain model (`tiferet/domain/di.py`). `resolve_service(*flags)` returns the effective core `ServiceDependency` for a flag set: a matching flagged override (in flag priority order), else the registration's own default definition when fully specified, else `None`. `get_service_type(*flags)` delegates to it, so the precedence rule is defined exactly once.

## Resolution failures

`DIDynamicServiceContainer.get_dependency` raises `ServiceError.raise_for(...)` when no provider is registered under the requested id. A registered provider that fails during construction still surfaces the underlying exception. The layer does not import events or assets to wrap those failures.

The public resolver is `DIDynamicServiceResolver`. It holds a `DIService` and an injected `parse_parameter` callable (default identity), builds a `DIDynamicServiceContainer` per flag set, and caches it on the `ServiceResolver` ABC. There is no `di/settings.py` engine and no `CreateServiceResolver` bootstrap event on the current `build_app` path.

## How Contexts Consume DI

The contexts do not hold a container or provider. Instead, the resolver's bound `get_dependency` method is injected as a plain callable:

- `AppSessionContext` receives `get_dependency` and forwards it to the feature context it builds on demand.
- `FeatureContext` calls `self.get_dependency(service_id, *flags)` to resolve each step's domain event and any configured middleware.

```python
# tiferet/contexts/feature.py (excerpt)
return self.get_dependency(service_id, *combined_flags)
```

This keeps the contexts decoupled from the DI engine: any callable with the `get_dependency(registration_id, *flags)` signature can be injected, which simplifies testing (a `mock.Mock()` suffices).

## Blueprint Wiring

The standard path is `core.build_app` in `tiferet/blueprints/core.py`. It does not use a declarative wiring registry; instead it composes the DI layer from two composition functions:

1. `build_app_service_container(cache, app_session)` — merges the cache-seeded framework defaults (`CORE_DEFAULT_SERVICES`, `CORE_DEFAULT_CONSTANTS`) with the session's own services and constants (session wins) and constructs a `DIAppServiceContainer`. App-level services resolve as Singletons.
2. `build_service_resolver(app_container)` — wraps the app container in a `DIDynamicServiceResolver`, caching it under the `app` flag so feature-step resolution inherits the app-level singletons.
3. `build_app_session_context(app_session, cache)` — imports the declared context class, resolves its event collaborators from the app container, and constructs the context via `BaseContext.from_domain`, injecting `resolver.get_dependency`.

```python
# tiferet/blueprints/core.py (excerpt)
app_container = build_app_service_container(cache, app_session)
resolver = build_service_resolver(app_container)
return context_cls.from_domain(
    app_session,
    get_dependency=resolver.get_dependency,
    **resolved_collaborators,
)
```

Consumer applications always use the core compose path. Do not document `CreateServiceResolver` or `di/settings.py` as current surface.

## Structured Code Design

The `di/` package uses `# *** classes` / `# ** class:` artifact comments, consistent with other `core.py` modules in the framework (e.g., `contexts/core.py`).

### Artifact Comments

- `# *** classes` — top-level section for the module.
- `# ** class: <snake_case_name>` — individual class definition.
- `# * attribute: <name>` — instance attributes (type hints only, no assignment).
- `# * init` — constructor.
- `# * method: <name>` — instance methods.
- `# * method: <name> (static)` — static methods.

**Spacing rules** follow `code_style.md`: one empty line between `# ***` and the first `# **`, one empty line between each `# *` section, one empty line after docstrings, and one empty line between code snippets.

## Provider Types and Registration

### Factory Providers (Class Types)

When a class type is registered via `add_service()`, it is wrapped in a `providers.Factory`. Each resolution creates a new instance with constructor kwargs wired to sibling providers:

```python
container.add_constants({'feature_config': 'config.yml'})
container.add_service('feature_service', FeatureConfigRepository)

# FeatureConfigRepository(feature_config='config.yml') is resolved:
repo = container.get_service('feature_service')  # ✓ new instance each time
```

### Object Providers (Scalars and Callables)

Non-type values registered via `add_services()` or `add_constants()` are wrapped in `providers.Object`. Each resolution returns the same value:

```python
container.add_constants({'app_config': 'config.yml'})

# Direct scalar resolution works:
path = container.get_service('app_config')  # ✓ returns 'config.yml'
```

## Customizing Parameter Parsing

The resolver accepts a `parse_parameter` callable used to resolve constant and parameter values (e.g. `$env.` references). It defaults to an identity function so the DI layer never imports `ParseParameter`. Blueprints may inject `ParseParameter.execute`. Tests can inject a custom parser to assert parsing behavior:

```python
resolver = ServiceResolver(
    di_service=mock_di_service,
    parse_parameter=lambda v: v.upper(),
)
```

For most tests, contexts can be exercised by injecting a `get_dependency` mock directly, bypassing the resolver entirely.

## Testing the DI Layer

Tests live in `tests/di/test_core.py` and `tests/di/test_dependency_injector.py` and follow the standard artifact comment structure.

### Key Patterns

- Test `ServiceContainer` registration and resolution — register types/constants and assert `get_service` returns the correct instances.
- Test `get_dependency` on an unregistered ID — assert `ServiceError` with `DI_DEPENDENCY_NOT_REGISTERED`.
- Test `remove_service` — assert the service is gone, and that removing an unknown ID raises nothing.
- Test `ServiceResolver.list_all_settings` merge behavior — assert repository configs/constants take priority over bootstrap defaults.
- Test `ServiceResolver.get_dependency` — assert per-flag containers are cached and that flagged dependency types resolve correctly.

```python
# *** tests

# ** test: get_dependency_success
def test_get_dependency_success(resolver: ServiceResolver):
    '''Test that a configured service resolves via get_dependency.'''

    # Resolve the service by configuration id.
    service = resolver.get_dependency('feature_service')

    # Assert it is the expected type.
    assert isinstance(service, FeatureConfigRepository)
```

## Package Layout

```
tiferet/di/
├── __init__.py                — Exports: ServiceContainer, ServiceResolver,
│                                DIAppServiceContainer, DIDynamicServiceContainer,
│                                DIDynamicServiceResolver, injectable_parameter_names,
│                                normalize_flags
├── core.py                    — # *** functions (injectable_parameter_names,
│                                normalize_flags) + ServiceContainer (ABC)
│                                + ServiceResolver (ABC, template get_dependency)
└── dependency_injector.py     — DIDynamicServiceContainer (Factory),
                                 DIAppServiceContainer (Singleton),
                                 DIDynamicServiceResolver (per-flag)

tests/di/
├── test_core.py                  — ABC contract + resolver template + normalize_flags
└── test_dependency_injector.py   — DIDynamic/DIApp container + resolver tests
```

## Conclusion

The `tiferet/di/` package provides the DI foundation for Tiferet. Its abstract contract (`di/core.py`) defines the `ServiceContainer` and `ServiceResolver` ABCs, and its `dependency_injector`-backed implementations (`di/dependency_injector.py`) provide the app-level Singleton container (`DIAppServiceContainer`), the feature-level Factory container (`DIDynamicServiceContainer`), and the per-flag resolver (`DIDynamicServiceResolver`). Explore source in `tiferet/di/core.py` and `tiferet/di/dependency_injector.py`; runtime consumers in `tiferet/blueprints/` and `tiferet/contexts/`; and tests in `tests/di/`.
