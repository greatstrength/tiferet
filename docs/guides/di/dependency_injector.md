# DI – DIDynamicServiceContainer, DIAppServiceContainer, DIDynamicServiceResolver

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** August 09, 2026  
**Version:** 2.0.0

## Overview

`tiferet/di/dependency_injector.py` is the concrete engine backing the abstract `ServiceContainer`/`ServiceResolver` contract (`di/core.py`) with the third-party `dependency-injector` library. Three classes: two container flavors distinguished by provider scope, and one resolver that builds containers on demand from a `DIService`. See [docs/guides/di.md](../di.md) for the broader package-level rationale (why the engine is abstracted, the Factory-vs-Singleton decision, per-flag caching).

**Module:** `tiferet/di/dependency_injector.py`
**Vision:** See each class's docstring in `tiferet/di/dependency_injector.py` for its value statement.

## Ubiquitous Language

- **Provider** — a `dependency_injector` object (`Factory`, `Singleton`, or `Object`) that knows how to produce a value on demand.
- **Sibling provider** — another provider already registered on the same container, wired into a service's constructor kwargs by matching parameter names.
- **Registration-keyed vs. service-id-keyed** — `DIDynamicServiceContainer` keys by arbitrary `service_id`; `DIAppServiceContainer.from_dependencies` specifically keys by `AppServiceDependency.service_id`.

## When should you reach for which one?

| Use case | Best choice | Why it fits |
|---|---|---|
| Build a per-flag container for feature-step service resolution | `DIDynamicServiceContainer` (via `DIDynamicServiceResolver`) | Factory scope — fresh instance per resolution, safe across flag sets |
| Build the one shared app-level service graph (events, repos wired once) | `DIAppServiceContainer` | Singleton scope — one instance reused for the life of the app session |
| Resolve feature-step dependencies from a `DIService`'s registrations | `DIDynamicServiceResolver` | Implements `build_container`, inherits per-flag caching from `ServiceResolver` |

## Domain Objects

### DIDynamicServiceContainer

Adapts the framework's `ServiceContainer` contract to `dependency_injector`'s `DynamicContainer`. Registers services as `Factory` providers (wired to sibling providers) and constants as `Object` providers.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="didynamicservicecontainer-container"></a>`container` | `containers.DynamicContainer` | — | — | The underlying `dependency_injector` container instance. |

#### Methods

<a id="didynamicservicecontainer-init"></a>
**`__init__(services=None, constants=None)`**

Creates the underlying `DynamicContainer` and immediately loads it via `load_container` — constants first, then services.

<a id="didynamicservicecontainer-add-service"></a>
**`add_service(service_id, service: ServiceDependency)`**

Registers the dependency's declared `parameters` as constants first (a parameter overwrites an existing constant of the same name), resolves the concrete type via `service.get_service_type()`, builds a `Factory` provider (`build_factory`), and registers it under `service_id`.

<a id="didynamicservicecontainer-add-constant"></a>
**`add_constant(constant_id, value)`**

Registers `value` as an `Object` provider — a pure pass-through, no construction logic.

<a id="didynamicservicecontainer-get-dependency"></a>
**`get_dependency(dependency_id) -> Any`**

Looks up the provider and invokes it. Raises `ServiceError` (`DI_DEPENDENCY_NOT_REGISTERED`) when no provider is registered under `dependency_id`; a provider that fails while constructing raises its raw exception unwrapped, leaving structured conversion to a caller with event access.

<a id="didynamicservicecontainer-has-dependency"></a>
**`has_dependency(dependency_id) -> bool`**

Checks the container's provider registry without invoking anything.

<a id="didynamicservicecontainer-remove-dependency"></a>
**`remove_dependency(dependency_id)`**

Removes the provider if present; idempotent no-op otherwise.

<a id="didynamicservicecontainer-load-container"></a>
**`load_container(services=None, constants=None)`**

Bulk-loads constants first (so Factory providers can wire to them), then services.

<a id="didynamicservicecontainer-build-factory"></a>
**`build_factory(service_type) -> providers.Factory`**

Wires each of `service_type`'s injectable constructor parameters (`injectable_parameter_names`) to a sibling provider registered under the same name, when one exists, and returns the `Factory`.

### DIAppServiceContainer

Extends `DIDynamicServiceContainer` for the application's core service graph: same wiring mechanics, `Singleton` scope instead of `Factory`, and a keying convenience for `AppServiceDependency` lists. Inherits `add_constant`, `get_dependency`, `has_dependency`, `remove_dependency`, and `load_container` unchanged — only `add_service` and the provider-builder differ.

#### Methods

<a id="diappservicecontainer-add-service"></a>
**`add_service(service_id, service: ServiceDependency)`**

Same precedence as the parent's `add_service` (parameters registered as constants first), but builds a `Singleton` provider (`build_singleton`) instead of a `Factory`.

<a id="diappservicecontainer-build-singleton"></a>
**`build_singleton(service_type) -> providers.Singleton`**

Sibling-wiring mirror of `build_factory`, producing a `Singleton` provider.

<a id="diappservicecontainer-from-dependencies"></a>
**`from_dependencies(services=None, constants=None) -> DIAppServiceContainer`** *(classmethod)*

Keys a `List[AppServiceDependency]` by each entry's `service_id`, then constructs and loads the container in one call. This is the entry point `build_app_service_container` (`tiferet/blueprints/core.py`) uses to compose the singleton app-level container from merged cache defaults and interface overrides.

```python
container = DIAppServiceContainer.from_dependencies(
    services=app_session.services,
    constants=merged_constants,
)
error_service = container.get_dependency('error_service')
```

### DIDynamicServiceResolver

Builds `DIDynamicServiceContainer`s from the registrations and constants supplied by a `DIService`, resolving each registration to its effective service dependency for the requested flags.

| Attribute | Type | Required | Default | Description |
|---|---|---|---|---|
| <a id="didynamicserviceresolver-di-service"></a>`di_service` | `DIService` | Yes | — | Supplies `list_all()` — registrations plus top-level constants. |
| <a id="didynamicserviceresolver-parse-parameter"></a>`parse_parameter` | `Callable` | No | identity | Applied to every constant/parameter value before registration (e.g. `$r.`-prefixed resolution). |

#### Methods

<a id="didynamicserviceresolver-init"></a>
**`__init__(di_service, parse_parameter=None)`**

Initializes the inherited per-flag container cache (`super().__init__()`), stores `di_service`, and defaults `parse_parameter` to the identity function.

<a id="didynamicserviceresolver-build-container"></a>
**`build_container(flags=None) -> ServiceContainer`**

For the given (already-normalized) flag list: reads all registrations and constants from `di_service.list_all()`, parses the top-level constants, then for each registration calls `resolve_service(*flags)` — skipping registrations that resolve to `None` — and re-wraps the effective dependency's own parameters through `parse_parameter`. Returns a freshly built `DIDynamicServiceContainer`. This method is the one piece `DIDynamicServiceResolver` must supply; `get_dependency` and the per-flag cache come from the inherited `ServiceResolver` template method (see [docs/guides/di.md](../di.md#the-serviceresolver-contract)).

```python
resolver = DIDynamicServiceResolver(di_service=my_di_service)
error_service = resolver.get_dependency('error_service', 'sqlite')  # flag-aware
```

## Error Handling

`get_dependency` on either container flavor raises `ServiceError.raise_for(self, DI_DEPENDENCY_NOT_REGISTERED_ID, ...)` — not a `TiferetError` — when an id has no registered provider, since a missing DI registration is infrastructural misconfiguration, not a domain outcome. A provider that raises *while constructing* is left unwrapped: the resolver has no event access to convert it, so the raw exception propagates to a caller that does.

## Testing

Container and resolver tests construct real (not mocked) `DIDynamicServiceContainer`/`DIAppServiceContainer` instances against small `ServiceDependency` fixtures, then assert `get_dependency` resolves the expected type and that sibling wiring occurred:

```python
container = DIDynamicServiceContainer(
    services={'error_service': ServiceDependency(module_path='myapp.repos', class_name='ErrorRepo')},
)
assert isinstance(container.get_dependency('error_service'), ErrorRepo)
```

For `DIDynamicServiceResolver`, mock `DIService.list_all` to return fixture registrations and assert `get_dependency(id, *flags)` resolves the flag-appropriate type, and that a second call with the same flags reuses the cached container (`build_container` called once).

## Boundaries

**Inside this domain:** the concrete `dependency_injector`-backed container/resolver classes, provider construction, and sibling-wiring mechanics.
**Outside this domain:** the abstract `ServiceContainer`/`ServiceResolver` contract and the Factory-vs-Singleton rationale (`docs/guides/di.md`), and the declarative `ServiceRegistration` data these classes consume (`docs/guides/domain/di.md`).

## Related Documentation

- [docs/guides/di.md](../di.md) — DI layer strategy guide: the abstract contract, scope decision, per-flag caching
- [docs/guides/domain/di.md](../domain/di.md) — `ServiceRegistration` and `FlaggedDependency` domain objects
- [docs/guides/domain/core.md](../domain/core.md) — `ServiceDependency` core model
- [docs/core/di.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/di.md) — DI layer code-style conventions
