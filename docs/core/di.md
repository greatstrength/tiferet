# Dependency Injection in Tiferet

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Overview

The `tiferet/di/` package provides the dependency-injection layer for the Tiferet framework. It is structured across two modules, re-exported from `tiferet/di/__init__.py` (`ServiceContainer`, `ServiceResolver`, `DIAppServiceContainer`, `DIDynamicServiceContainer`, `DIDynamicServiceResolver`, `injectable_parameter_names`, `normalize_flags`):

- **`tiferet/di/core.py`** — the abstract, domain-only core: the `ServiceContainer` and `ServiceResolver` ABCs plus the pure module functions `injectable_parameter_names` and `normalize_flags`. It imports only the standard library and `..domain` (`ServiceDependency`).
- **`tiferet/di/dependency_injector.py`** — the concrete implementations backed by `dependency_injector`: `DIDynamicServiceContainer` (feature-level, `Factory` scope), `DIAppServiceContainer` (app-level, `Singleton` scope), and `DIDynamicServiceResolver` (per-flag feature resolver). It may additionally import `..interfaces.di` (`DIService`).

The DI layer is deliberately **event-free and asset-free**: it imports only the standard library, `dependency_injector`, `..domain`, and (in `dependency_injector.py`) `..interfaces.di` (`DIService`). It assumes best-case inputs and raises raw exceptions, leaving structured error handling to callers that have event access. Parameter parsing (e.g. `$env.` references) is injected as a `parse_parameter` callable so DI never imports the blueprint helper (`tiferet/blueprints/core.py::parse_parameter`) itself.

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

The standard path is `build_app` in `tiferet/blueprints/app.py`. It does not use a declarative wiring registry; instead it composes the DI layer from two composition functions in `tiferet/blueprints/core.py`:

1. `build_app_service_container(cache, app_session)` — merges the cache-seeded framework defaults (`CORE_DEFAULT_SERVICES`, `CORE_DEFAULT_CONSTANTS`) with the session's own services and constants (session wins) and constructs a `DIAppServiceContainer`. App-level services resolve as Singletons.
2. `build_service_resolver(app_container)` — wraps the app container in a `DIDynamicServiceResolver`, caching it under the `app` flag so feature-step resolution inherits the app-level singletons.
3. `build_app_session_context(app_session, cache)` (`app.py`) — runs the two steps above, then hands off to `core.compose_session_context`, which resolves the context's collaborators, wires the handlers, and constructs the context via `BaseContext.from_domain`, injecting `resolver.get_dependency`.

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

The older declarative-wiring path (`wire_services`, `load_app_instance`, `CreateServiceResolver`) has been removed. Every blueprint, the built-in admin and tester sessions included, composes its context through `core.compose_session_context`.

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

### Factory and Singleton Providers (Class Types)

`DIDynamicServiceContainer.add_service(service_id, service)` takes a core `ServiceDependency`. It registers the dependency's `parameters` as constants, then wraps the imported class in a `providers.Factory` whose constructor kwargs are wired to sibling providers. `DIAppServiceContainer` does the same with `providers.Singleton`.

```python
container = DIDynamicServiceContainer()
container.add_constant('feature_config', 'config.yml')
container.add_service('feature_service', ServiceDependency(
    module_path='tiferet.repos.feature',
    class_name='FeatureConfigRepository',
))

# FeatureConfigRepository(feature_config='config.yml'), a new instance each time.
repo = container.get_dependency('feature_service')
```

### Object Providers (Constants)

`add_constant(constant_id, value)` wraps the value in a `providers.Object`. Each resolution returns the same value:

```python
container.add_constant('app_config', 'config.yml')

# Direct scalar resolution returns 'config.yml'.
path = container.get_dependency('app_config')
```

## Customizing Parameter Parsing

`DIDynamicServiceResolver(di_service, parse_parameter=None)` uses `parse_parameter` to resolve constant and parameter values (e.g. `$env.` references). It defaults to an identity function so the DI layer never imports blueprint code. `core.build_service_resolver` injects `tiferet/blueprints/core.py::parse_parameter` and registers the app container under the `'app'` flag. Tests can inject a custom parser:

```python
resolver = DIDynamicServiceResolver(
    di_service=mock_di_service,
    parse_parameter=lambda value: value.upper(),
)
```

For most tests, contexts can be exercised by injecting a `get_dependency` mock directly, bypassing the resolver entirely.

## Testing the DI Layer

Tests live in `tests/di/test_core.py` (ABC contract, resolver template, pure functions) and `tests/di/test_dependency_injector.py` (concrete containers and resolver). They follow the standard artifact comment structure.

### Key Patterns

- Test container registration and resolution — register a `ServiceDependency` or constant and assert `get_dependency` returns the expected instance or value.
- Test `get_dependency` on an unregistered id — assert a raw exception propagates (DI does not raise structured `TiferetError`s).
- Test `remove_dependency` — assert the dependency is gone, and that removing an unknown id raises nothing.
- Test `ServiceResolver.get_dependency` — assert per-flag containers are built once, cached, and delegated to.

```python
# *** tests

# ** test: add_service_resolves
def test_add_service_resolves(simple_dependency: ServiceDependency):
    '''
    add_service registers a service that resolves to SimpleService.

    :param simple_dependency: The simple service dependency.
    :type simple_dependency: ServiceDependency
    :return: None
    :rtype: None
    '''

    # Register and resolve the simple service.
    container = DIDynamicServiceContainer()
    container.add_service('simple_service', simple_dependency)

    # The resolved value is a SimpleService.
    assert isinstance(container.get_dependency('simple_service'), SimpleService)
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

The `tiferet/di/` package provides the DI foundation for Tiferet. Its abstract contract (`di/core.py`) defines the `ServiceContainer` and `ServiceResolver` ABCs, and its `dependency_injector`-backed implementations (`di/dependency_injector.py`) provide the app-level Singleton container (`DIAppServiceContainer`), the feature-level Factory container (`DIDynamicServiceContainer`), and the per-flag resolver (`DIDynamicServiceResolver`). Together they preserve per-flag caching and automatic constructor wiring; bootstrap defaults are merged by the blueprints before the containers are built.

Explore source in `tiferet/di/core.py` and `tiferet/di/dependency_injector.py`; runtime consumers in `tiferet/blueprints/` and `tiferet/contexts/`; and tests in `tests/di/`.
