# Dependency Injection in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

The `tiferet/di/` package provides the dependency-injection layer for the Tiferet framework. As of v2.0.0b10 it defines two classes in `tiferet/di/settings.py`:

- **`ServiceContainer`** — the low-level dependency-injection engine. It registers service types and constants and instantiates services with their constructor parameters wired to sibling registrations, backed by `dependency_injector`'s `DynamicContainer`.
- **`ServiceResolver`** — the application's single public provider. It takes a `DIService` as a direct dependency (in the spirit of a domain event), reads service configurations and constants, assembles a per-flag type map and constant set, and builds and caches a `ServiceContainer` engine per flag set.

There is no longer a separate "app-level" vs. "feature-level" DI split. The previous `ServiceProvider` ABC, `DynamicServiceProvider`, the `DependenciesServiceProvider` alias, and the `DIContext` feature-level context have all been retired. DI assembly now lives entirely in `ServiceResolver`, and the contexts that need to resolve services (`AppInterfaceContext`, `FeatureContext`) consume an injected `get_dependency` callable rather than holding a provider or container directly.

This document describes the structure, design principles, and best practices for the DI layer, adhering to Tiferet's structured code style ([docs/core/code_style.md](code_style.md)).

## The ServiceContainer Engine

`ServiceContainer` is the low-level engine. It wraps a `dependency_injector` `DynamicContainer` and exposes a small, consistent API for registering and resolving services.

Key characteristics:
- Backed by `containers.DynamicContainer`, which supports runtime provider registration via `set_provider()`.
- Class types are registered as `Factory` providers (a new instance per resolution); non-type values (scalars, callables, etc.) are registered as `Object` providers (pass-through).
- `get_service()` returns fully resolved instances; callers never interact with the container directly.
- Uses `RaiseError.execute()` for structured error handling.

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
        provider = self.container.providers.get(service_id)
        if provider is None:
            RaiseError.execute('INVALID_DEPENDENCY_ERROR', ...)
        return provider()

    # * method: build_factory
    def build_factory(self, service_type: type) -> providers.Factory:
        sig = inspect.signature(service_type.__init__)
        kwargs = {}
        for param_name, param in sig.parameters.items():
            if param_name == 'self' or param.kind in (VAR_POSITIONAL, VAR_KEYWORD):
                continue
            sibling = self.container.providers.get(param_name)
            if sibling is not None:
                kwargs[param_name] = sibling
        return providers.Factory(service_type, **kwargs)
```

### Method Semantics

- **`add_service(service_id, service_type)`** — Registers a single service type under an ID as a `Factory` provider.
- **`add_services(services)`** — Bulk-registers a `Dict[str, type]` mapping in two passes: scalars/non-type values first (as `Object` providers), then class types (as `Factory` providers). The two-pass order guarantees that every parameter value is available in the container before any `Factory` provider is built and its kwargs are wired.
- **`add_constants(constants)`** — Registers scalar values (strings, numbers, booleans) as `Object` providers. Constants can be resolved directly via `get_service`.
- **`get_service(service_id)`** — Returns the fully resolved service instance. Raises `INVALID_DEPENDENCY_ERROR` when the service is not registered or cannot be resolved (`TiferetError` instances are re-raised without wrapping).
- **`remove_service(service_id)`** — Deregisters a service. No-op when the ID is not present.
- **`build_factory(service_type)`** — Inspects the constructor signature via `inspect.signature()` and wires each parameter to a sibling provider if one exists, enabling cascading dependency resolution without explicit wiring configuration.

## The ServiceResolver

`ServiceResolver` is the application's single public provider and the only DI class the rest of the framework collaborates with. It takes a `DIService` as a direct constructor dependency (in the spirit of a domain event), reads the service configurations and constants, assembles a per-flag type map and constant set, and builds and caches a `ServiceContainer` engine per flag set.

```python
# ** class: service_resolver
class ServiceResolver(object):
    '''
    The application's service provider.
    '''

    # * attribute: di_service
    di_service: DIService

    # * attribute: container_factory
    container_factory: Callable

    # * attribute: default_config_index
    default_config_index: Dict[str, ServiceConfiguration]

    # * attribute: default_di_constants
    default_di_constants: Dict[str, Any]

    # * init
    def __init__(self,
            di_service: DIService,
            container_factory: Callable = None,
            default_config_index: Dict[str, ServiceConfiguration] = None,
            default_di_constants: Dict[str, Any] = None,
        ):
        self.di_service = di_service
        self.container_factory = container_factory if container_factory else self.default_container
        self.default_config_index = default_config_index if default_config_index is not None else {}
        self.default_di_constants = default_di_constants if default_di_constants is not None else {}
        self._containers: Dict[str, ServiceContainer] = {}
```

### Responsibilities

- **`default_container(type_map, **constants)` (static)** — The default `container_factory`. Creates a `ServiceContainer`, registers constants first (so `Factory` providers can wire constructor parameters), then adds the service types.
- **`normalize_flags(*flags)` (static)** — Flattens a mixed sequence of strings, lists, and tuples into a flat list of strings.
- **`create_cache_key(flags)`** — Derives the per-flag cache key (e.g. `feature_services_<flag>...`).
- **`list_all_settings()`** — Calls `di_service.list_all()` for repository configurations and constants, then merges the bootstrap `default_config_index` for any service ID not present and merges `default_di_constants` beneath the repository constants (defaults are lower priority).
- **`load_constants(configurations, constants, flags)`** — Parses top-level constants and per-configuration parameters (honoring flagged dependencies) via `ParseParameter`.
- **`build_type_map(configurations, flags)`** — Resolves each configuration to a concrete type via `ServiceConfiguration.get_service_type(*flags)`, raising `DEPENDENCY_TYPE_NOT_FOUND` when no type matches.
- **`build_container(flags)`** — Builds (and caches per flag set) a `ServiceContainer` by combining `list_all_settings`, `load_constants`, and `build_type_map` through `container_factory`.
- **`get_dependency(configuration_id, *flags)`** — The public resolution entry point: normalizes flags, builds/retrieves the per-flag container, and returns the resolved service. This bound method is the `get_dependency` callable injected into the contexts.

### Bootstrap Default Merging

`ServiceResolver` preserves the bootstrap `default_*` merge behavior. The blueprint routes any bootstrap DI defaults into the resolver:

- `default_config_index` — a typed `Dict[str, ServiceConfiguration]` keyed by id, merged beneath the repository's configurations (only for IDs not already present).
- `default_di_constants` — constants merged beneath the repository's constants at lower priority.

## How Contexts Consume DI

The contexts do not hold a container or provider. Instead, the resolver's bound `get_dependency` method is injected as a plain callable:

- `AppInterfaceContext` receives `get_dependency` and forwards it to the feature context it builds on demand.
- `FeatureContext` (and `AsyncFeatureContext`) call `self.get_dependency(service_id, *flags)` to resolve each step's domain event and any configured middleware.

```python
# tiferet/contexts/feature.py (excerpt)
return self.get_dependency(service_id, *combined_flags)
```

This keeps the contexts decoupled from the DI engine: any callable with the `get_dependency(configuration_id, *flags)` signature can be injected, which simplifies testing (a `mock.Mock()` suffices).

## Blueprint Wiring

The `build_app` blueprint (`tiferet/blueprints/main.py`) wires the interface declaratively — there is no app-level DI container:

1. `wire_services(services, constants)` seeds a name-to-value registry with interface scalars and constants, then iteratively instantiates each `AppServiceDependency` whose constructor arguments are all resolvable (wiring events to the repositories they depend on).
2. `load_app_instance` builds a `ServiceResolver` from the resolved `di_service`, routing bootstrap DI defaults (`default_configurations`, `default_constants`) into it via `build_config_index`.
3. The hub's event collaborators (`get_feature_evt`, `get_error_evt`, `logging_list_all_evt`) are resolved by name from the registry, and the context is constructed via `from_domain`, injecting `resolver.get_dependency`.

```python
# tiferet/blueprints/main.py (excerpt)
resolver = ServiceResolver(
    di_service=registry.get('di_service'),
    default_config_index=build_config_index(context_kwargs.pop('default_configurations', None)),
    default_di_constants=context_kwargs.pop('default_constants', None) or {},
)
return context_cls.from_domain(
    app_interface,
    get_dependency=resolver.get_dependency,
    **resolved,
    **context_kwargs,
)
```

## Structured Code Design

The `di/` package uses `# *** classes` / `# ** class:` artifact comments, consistent with other `settings.py` modules in the framework (e.g., `domain/settings.py`).

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

## Customizing Resolution

To customize how containers are built (e.g., for testing), pass a `container_factory` to `ServiceResolver`. The factory must accept `(type_map, **constants)` and return a `ServiceContainer`:

```python
def testing_container(type_map=None, **constants):
    container = ServiceContainer()
    container.add_constants(constants)
    if type_map:
        container.add_services(type_map)
    return container

resolver = ServiceResolver(di_service=mock_di_service, container_factory=testing_container)
```

For most tests, contexts can be exercised by injecting a `get_dependency` mock directly, bypassing the resolver entirely.

## Testing the DI Layer

Tests live in `tests/di/test_settings.py` and follow the standard artifact comment structure.

### Key Patterns

- Test `ServiceContainer` registration and resolution — register types/constants and assert `get_service` returns the correct instances.
- Test `get_service` on an unregistered ID — assert `TiferetError` with `error_code == 'INVALID_DEPENDENCY_ERROR'`.
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
├── __init__.py          — Exports: ServiceContainer, ServiceResolver
└── settings.py          — ServiceContainer (engine) + ServiceResolver (provider)

tests/di/
└── test_settings.py     — DI engine and resolver tests
```

## Migration from b9

- `ServiceProvider` (ABC), `DynamicServiceProvider`, and the `DependenciesServiceProvider` alias have been removed. The low-level engine is now `ServiceContainer`; the public provider is `ServiceResolver`.
- The feature-level `DIContext` (`tiferet/contexts/di.py`) has been removed. DI assembly lives in `ServiceResolver`, and contexts consume the injected `get_dependency` callable.
- The `create_service_provider` blueprint factory has been removed. Interface wiring is now declarative via `wire_services`, and `load_app_instance` constructs a `ServiceResolver` and injects `resolver.get_dependency`.
- `build_factory` is a public method on `ServiceContainer` (it inspects the constructor signature and wires kwargs to sibling providers).

## Conclusion

The `tiferet/di/` package provides the DI foundation for Tiferet through two classes: the low-level `ServiceContainer` engine (backed by `dependency-injector`'s `DynamicContainer`) and the public `ServiceResolver`, which owns DI assembly from a `DIService` and exposes `get_dependency` for the contexts to consume. This single-provider design removes the previous app-level/feature-level split while preserving per-flag caching, automatic constructor wiring, and bootstrap default merging.

Explore source in `tiferet/di/settings.py`, runtime consumers in `tiferet/blueprints/main.py` and `tiferet/contexts/`, and tests in `tests/di/test_settings.py`.
