# Dependency Injection in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

The `tiferet/di/` package provides the dependency-injection layer for the Tiferet framework. It is structured across three modules:

- **`tiferet/di/core.py`** — the abstract, domain-only core: the `ServiceContainer` and `ServiceResolver` ABCs plus the pure module functions `injectable_parameter_names` and `normalize_flags`. It imports only the standard library and `..domain` (`ServiceDependency`).
- **`tiferet/di/dependency_injector.py`** — the concrete implementations backed by `dependency_injector`: `DIDynamicServiceContainer` (feature-level, `Factory` scope), `DIAppServiceContainer` (app-level, `Singleton` scope), and `DIDynamicServiceResolver` (per-flag feature resolver). It may additionally import `..interfaces.di` (`DIService`).
- **`tiferet/di/settings.py`** — the module-functions layer: `create_cache_key` / `merge_settings` plus the concrete `ServiceContainer` engine and `ServiceResolver` provider wired by `build_app`.

The DI layer is deliberately **event-free and asset-free**: it imports only the standard library, `dependency_injector`, `..domain`, and (in `dependency_injector.py`) `..interfaces.di` (`DIService`). It assumes best-case inputs and raises raw exceptions, leaving structured error handling to callers that have event access. Parameter parsing (e.g. `$env.` references) is injected as a `parse_parameter` callable so DI never imports `ParseParameter` itself.

App-level core services resolve as shared **Singletons** (`DIAppServiceContainer`), while feature-level services resolve per flag set as **Factories** (`DIDynamicServiceResolver`). Contexts (`AppInterfaceContext`, `FeatureContext`) consume an injected `get_dependency` callable rather than holding a provider or container directly.

This document describes the structure, design principles, and best practices for the DI layer, adhering to Tiferet's structured code style ([docs/core/code_style.md](code_style.md)).

## Module Functions

The DI package exposes pure, side-effect-free helpers under `# *** functions`:

- **`injectable_parameter_names(service_type)`** (`di/core.py`) — Returns a service type's injectable constructor parameter names, excluding `self` and variadic parameters. Used by every container's `build_factory` / `build_singleton` and `CreateServiceResolver`.
- **`normalize_flags(*flags)`** (`di/core.py`) — Flattens a mixed sequence of strings, lists, and tuples into a flat list of strings. Re-exported from `tiferet/di/__init__.py`.
- **`create_cache_key(flags)`** (`di/settings.py`) — Derives the per-flag container cache key (e.g. `feature_services_<flag>...`).
- **`merge_settings(configs, constants, default_config_index, default_constants)`** (`di/settings.py`) — Appends default-index entries for any service ID not already present and merges default constants beneath the repository constants. Backs both `ServiceResolver.list_all_settings` and the `ListAllSettings` event.

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

## The ServiceContainer Engine

`ServiceContainer` is the low-level engine. It wraps a `dependency_injector` `DynamicContainer` and exposes a small, consistent API for registering and resolving services.

Key characteristics:
- Backed by `containers.DynamicContainer`, which supports runtime provider registration via `set_provider()`.
- Class types are registered as `Factory` providers (a new instance per resolution); non-type values (scalars, callables, etc.) are registered as `Object` providers (pass-through).
- `get_service()` returns fully resolved instances; callers never interact with the container directly.
- Event-free and asset-free: a missing or failing provider raises a raw exception for a caller with event access to convert into a structured error (no `RaiseError` inside DI).

```python
# tiferet/di/settings.py

# *** classes

# ** class: service_container
class ServiceContainer(object):
    '''
    The low-level dependency-injection engine for the framework.
    '''

    # * attribute: container
    container: containers.DynamicContainer

    # * init
    def __init__(self, services: Dict[str, type] = None):
        self.container = containers.DynamicContainer()
        if services:
            self.add_services(services)

    # * method: add_service
    def add_service(self, service_id: str, service_type: type):
        factory = self.build_factory(service_type)
        self.container.set_provider(service_id, factory)

    # * method: add_services
    def add_services(self, services: Dict[str, type]):
        # Pass 1: register scalar/non-type values first so they are
        # available when Factory providers are built.
        for service_id, value in services.items():
            if not isinstance(value, type):
                self.container.set_provider(service_id, providers.Object(value))
        # Pass 2: register all class types as Factory providers.
        for service_id, value in services.items():
            if isinstance(value, type):
                self.add_service(service_id, value)

    # * method: add_constants
    def add_constants(self, constants: Dict[str, Any]):
        for name, value in constants.items():
            self.container.set_provider(name, providers.Object(value))

    # * method: get_service
    def get_service(self, service_id: str) -> Any:
        # Look up the provider and invoke it; a missing/failing provider
        # raises a raw exception for the caller to convert.
        provider = self.container.providers.get(service_id)
        return provider()

    # * method: build_factory
    def build_factory(self, service_type: type) -> providers.Factory:
        # Wire each injectable constructor parameter to a sibling provider,
        # using the shared injectable_parameter_names helper.
        kwargs = {}
        for param_name in injectable_parameter_names(service_type):
            sibling = self.container.providers.get(param_name)
            if sibling is not None:
                kwargs[param_name] = sibling
        return providers.Factory(service_type, **kwargs)
```

### Method Semantics

- **`add_service(service_id, service_type)`** — Registers a single service type under an ID as a `Factory` provider.
- **`add_services(services)`** — Bulk-registers a `Dict[str, type]` mapping in two passes: scalars/non-type values first (as `Object` providers), then class types (as `Factory` providers). The two-pass order guarantees that every parameter value is available in the container before any `Factory` provider is built and its kwargs are wired.
- **`add_constants(constants)`** — Registers scalar values (strings, numbers, booleans) as `Object` providers. Constants can be resolved directly via `get_service`.
- **`get_service(service_id)`** — Returns the fully resolved service instance. A missing or failing provider raises a raw exception (no DI-level error wrapping); callers with event access convert it into a structured error.
- **`remove_service(service_id)`** — Deregisters a service. No-op when the ID is not present.
- **`build_factory(service_type)`** — Wires each injectable constructor parameter (from the shared `injectable_parameter_names` helper) to a sibling provider if one exists, enabling cascading dependency resolution without explicit wiring configuration.

## The ServiceResolver

`ServiceResolver` is the application's single public provider and the only DI class the rest of the framework collaborates with. It takes a `DIService` and a `parse_parameter` callable as direct constructor dependencies (in the spirit of a domain event), reads the service registrations and constants, assembles a per-flag type map and constant set, and builds and caches a `ServiceContainer` engine per flag set.

```python
# ** class: service_resolver
class ServiceResolver(object):
    '''
    The application's service provider.
    '''

    # * attribute: di_service
    di_service: DIService

    # * attribute: parse_parameter
    parse_parameter: Callable

    # * attribute: default_config_index
    default_config_index: Dict[str, ServiceRegistration]

    # * attribute: default_di_constants
    default_di_constants: Dict[str, Any]

    # * init
    def __init__(self,
            di_service: DIService,
            parse_parameter: Callable = None,
            default_config_index: Dict[str, ServiceRegistration] = None,
            default_di_constants: Dict[str, Any] = None,
        ):
        self.di_service = di_service
        # Default to an identity parser so DI never imports ParseParameter;
        # the bootstrap event injects the real ParseParameter.execute.
        self.parse_parameter = parse_parameter if parse_parameter else (lambda v: v)
        self.default_config_index = default_config_index if default_config_index is not None else {}
        self.default_di_constants = default_di_constants if default_di_constants is not None else {}
        self._containers: Dict[str, ServiceContainer] = {}
```

### Responsibilities

- **`normalize_flags(*flags)` (static)** — Flattens a mixed sequence of strings, lists, and tuples into a flat list of strings. Delegates to the module-level `normalize_flags` helper.
- **`create_cache_key(flags)`** — Derives the per-flag cache key (e.g. `feature_services_<flag>...`). Delegates to the module-level `create_cache_key` helper.
- **`list_all_settings()`** — Calls `di_service.list_all()` for repository configurations and constants, then delegates to the module-level `merge_settings` helper to append `default_config_index` entries for any service ID not present and merge `default_di_constants` beneath the repository constants (defaults are lower priority).
- **`load_constants(configurations, constants, flags)`** — Parses top-level constants and per-configuration parameters (honoring flagged dependencies) via the injected `parse_parameter` callable.
- **`build_type_map(configurations, flags)`** — Resolves each configuration to a concrete type via `ServiceRegistration.get_service_type(*flags)`, skipping any configuration that resolves to no type (so it is simply not registered); an unresolved service then surfaces as a raw resolution error at the consuming context.
- **`build_container(flags)`** — Builds (and caches per flag set) a `ServiceContainer` directly by combining `list_all_settings`, `load_constants`, and `build_type_map` (registering constants before service types).
- **`get_dependency(registration_id, *flags)`** — The public resolution entry point: normalizes flags, builds/retrieves the per-flag container, and returns the resolved service. This bound method is the `get_dependency` callable injected into the contexts.

### Bootstrap Default Merging

`ServiceResolver` preserves the bootstrap `default_*` merge behavior. The `CreateServiceResolver` bootstrap event routes any bootstrap DI defaults into the resolver:

- `default_config_index` — a typed `Dict[str, ServiceRegistration]` keyed by id, merged beneath the repository's configurations (only for IDs not already present).
- `default_di_constants` — constants merged beneath the repository's constants at lower priority.

## How Contexts Consume DI

The contexts do not hold a container or provider. Instead, the resolver's bound `get_dependency` method is injected as a plain callable:

- `AppInterfaceContext` receives `get_dependency` and forwards it to the feature context it builds on demand.
- `FeatureContext` (and `AsyncFeatureContext`) call `self.get_dependency(service_id, *flags)` to resolve each step's domain event and any configured middleware.

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

The older declarative-wiring path (`wire_services`, `load_app_instance`, `CreateServiceResolver`) survives module-private inside `tiferet/blueprints/tiferet_cli.py` for the built-in `tiferet_cli` session, which the core compose path cannot yet replace. Consumer applications always use the core path.

## Structured Code Design

The `di/` package uses `# *** classes` / `# ** class:` artifact comments, consistent with other `settings.py` modules in the framework (e.g., `contexts/settings.py`).

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
container.add_constants({'feature_config': 'app/configs/feature.yml'})
container.add_service('feature_service', FeatureConfigRepository)

# FeatureConfigRepository(feature_config='app/configs/feature.yml') is resolved:
repo = container.get_service('feature_service')  # ✓ new instance each time
```

### Object Providers (Scalars and Callables)

Non-type values registered via `add_services()` or `add_constants()` are wrapped in `providers.Object`. Each resolution returns the same value:

```python
container.add_constants({'app_config': 'app/configs/app.yml'})

# Direct scalar resolution works:
path = container.get_service('app_config')  # ✓ returns 'app/configs/app.yml'
```

## Customizing Parameter Parsing

The resolver accepts a `parse_parameter` callable used to resolve constant and parameter values (e.g. `$env.` references). It defaults to an identity function so the DI layer never imports `ParseParameter`; the `CreateServiceResolver` bootstrap event injects the real `ParseParameter.execute`. Tests can inject a custom parser to assert parsing behavior:

```python
resolver = ServiceResolver(
    di_service=mock_di_service,
    parse_parameter=lambda v: v.upper(),
)
```

For most tests, contexts can be exercised by injecting a `get_dependency` mock directly, bypassing the resolver entirely.

## Testing the DI Layer

Tests live in `tests/di/test_settings.py` and follow the standard artifact comment structure.

### Key Patterns

- Test `ServiceContainer` registration and resolution — register types/constants and assert `get_service` returns the correct instances.
- Test `get_service` on an unregistered ID — assert a raw exception propagates (DI does not raise structured `TiferetError`s).
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
│                                DIAppServiceContainer, injectable_parameter_names,
│                                normalize_flags, create_cache_key, merge_settings
├── core.py                    — # *** functions (injectable_parameter_names,
│                                normalize_flags) + ServiceContainer (ABC)
│                                + ServiceResolver (ABC, template get_dependency)
├── dependency_injector.py     — DIDynamicServiceContainer (Factory),
│                                DIAppServiceContainer (Singleton),
│                                DIDynamicServiceResolver (per-flag)
└── settings.py                — # *** functions (create_cache_key,
                                 merge_settings) + concrete ServiceContainer engine
                                 + ServiceResolver provider

tests/di/
├── test_core.py                  — ABC contract + resolver template + normalize_flags
├── test_dependency_injector.py   — DIDynamic/DIApp container + resolver tests
└── test_settings.py              — ServiceContainer engine and ServiceResolver tests
```

## Conclusion

The `tiferet/di/` package provides the DI foundation for Tiferet. Its abstract contract (`di/core.py`) defines the `ServiceContainer` and `ServiceResolver` ABCs, and its `dependency_injector`-backed implementations (`di/dependency_injector.py`) provide the app-level Singleton container (`DIAppServiceContainer`), the feature-level Factory container (`DIDynamicServiceContainer`), and the per-flag resolver (`DIDynamicServiceResolver`). The `di/settings.py` module supplies the concrete engine and resolver wired by `build_app`, together preserving per-flag caching, automatic constructor wiring, and bootstrap default merging.

Explore source in `tiferet/di/core.py`, `tiferet/di/dependency_injector.py`, and `tiferet/di/settings.py`; runtime consumers in `tiferet/blueprints/` and `tiferet/contexts/`; and tests in `tests/di/`.
