# Technical Requirements Document: DI – Introduce ServiceProvider Package

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** March 26, 2026  
**Version:** 2.0.0a7

## 1. Overview

This story introduces the `tiferet/di/` package as a new first-class component of the Tiferet framework. It establishes the `ServiceProvider` abstract base class and the `DependenciesServiceProvider` concrete implementation, which together abstract the app-level dependency injection lifecycle that backs `AppManagerContext` during interface loading. The package includes a comprehensive unit test suite covering all methods and error paths, and a new core style guide (`docs/core/di.md`).

This work is the foundational DI story for the v2.0.0a7 release, which is organized around the `ServiceProvider` pattern as the unifying abstraction for app-level dependency injection.

## 2. Scope

### In Scope
- `tiferet/di/settings.py` — `ServiceProvider` ABC with five abstract methods.
- `tiferet/di/dependencies.py` — `DependenciesServiceProvider` concrete implementation backed by the `dependencies` library.
- `tiferet/di/__init__.py` — Package exports.
- `tiferet/di/tests/__init__.py` — Test package marker.
- `tiferet/di/tests/test_dependencies.py` — 12 unit tests for `DependenciesServiceProvider`.
- `docs/core/di.md` — Core style guide for the `di/` package.

### Out of Scope
- `pyproject.toml` registration of `tiferet.di` (deferred to the release documentation/packaging story).
- Refactoring `AppManagerContext` to fully integrate `ServiceProvider` (tracked separately).
- Feature-level DI (`DIContext`) refactoring.
- Alternative `ServiceProvider` implementations beyond `DependenciesServiceProvider`.
- Integration tests.

## 3. Components Affected

| Component | File/Path | Changes |
|---|---|---|
| ServiceProvider ABC | `tiferet/di/settings.py` | New file |
| DependenciesServiceProvider | `tiferet/di/dependencies.py` | New file |
| DI package exports | `tiferet/di/__init__.py` | New file |
| DI test package | `tiferet/di/tests/__init__.py` | New file |
| DependenciesServiceProvider tests | `tiferet/di/tests/test_dependencies.py` | New file |
| DI style guide | `docs/core/di.md` | New file |

## 4. Detailed Requirements

### 4.1 ServiceProvider ABC (`tiferet/di/settings.py`)

Defines the abstract contract for all service provider implementations.

- Must extend `ABC` from the `abc` module.
- Must declare five abstract methods with RST docstrings:
  - `add_service(service_id: str, service_type: type)` — Register a single service type.
  - `add_services(services: Dict[str, type])` — Bulk-register a dict of service types.
  - `add_constants(constants: Dict[str, Any])` — Register scalar constructor injection parameters.
  - `get_service(service_id: str) -> Any` — Resolve and return a registered service instance.
  - `remove_service(service_id: str)` — Deregister a service (idempotent).
- Must use `# *** classes` / `# ** class: service_provider` artifact comment structure.

```python
# *** classes

# ** class: service_provider
class ServiceProvider(ABC):
    '''
    Service provider for app context dependencies.
    '''

    # * method: add_service
    @abstractmethod
    def add_service(self, service_id: str, service_type: type): ...

    # * method: add_services
    @abstractmethod
    def add_services(self, services: Dict[str, type]): ...

    # * method: add_constants
    @abstractmethod
    def add_constants(self, constants: Dict[str, Any]): ...

    # * method: get_service
    @abstractmethod
    def get_service(self, service_id: str) -> Any: ...

    # * method: remove_service
    @abstractmethod
    def remove_service(self, service_id: str): ...
```

### 4.2 DependenciesServiceProvider (`tiferet/di/dependencies.py`)

Concrete implementation of `ServiceProvider` using the `dependencies` library's `Injector` as its backing resolver.

**Attributes:**
- `services: Dict[str, type]` — Registry of service IDs to types or scalar values.
- `injector: type` — The current `Injector` subclass type, or `None` when `services` is empty.
- `_name: str` — Name used for the internal injector class (default: `'TiferetInjector'`).

**Constructor:** `__init__(self, services: Dict[str, type] = None, name: str = 'TiferetInjector')`
- `services` defaults to `None`, coerced to `{}` internally.
- Calls `build_injector()` on construction.

**Static factory:** `new(name: str, dependencies: Dict[str, type]) -> DependenciesServiceProvider`
- Returns `DependenciesServiceProvider(services=dependencies, name=name)`.

**`build_injector()` — empty scope guard:**
The `dependencies` library raises `DependencyError: Extension scope can not be empty` when creating an `Injector` with no attributes. `build_injector` must guard against this:
```python
def build_injector(self):
    if self.services:
        self.injector = type(self._name, (Injector,), self.services)
    else:
        self.injector = None
```

**`get_service(service_id)` — two-stage error handling:**
```python
def get_service(self, service_id: str) -> Any:
    if self.injector is None:
        RaiseError.execute('INVALID_DEPENDENCY_ERROR', ...)

    try:
        return getattr(self.injector, service_id)
    except (DependencyError, AttributeError) as e:
        RaiseError.execute('INVALID_DEPENDENCY_ERROR', ...)
```
Note: `AttributeError` must be caught in addition to `DependencyError` — the library raises `AttributeError` for unknown attributes, not `DependencyError`.

**`remove_service`** — idempotent; no-op if `service_id` is not in `services`.

**Error handling:** All errors must use `RaiseError.execute()`. No raw `raise` statements.

**Artifact comments:** Must use `# *** classes` / `# ** class: dependencies_service_provider`.

### 4.3 Tests (`tiferet/di/tests/test_dependencies.py`)

12 unit tests covering all methods and error paths. Must follow `# *** fixtures` / `# ** fixture:` / `# *** tests` / `# ** test:` artifact comment structure.

Required test cases:

| Test | Description |
|---|---|
| `test_init_empty` | Provider created with no args; `services == {}`; `injector is None`. |
| `test_init_with_services` | Provider created with services dict; types are registered. |
| `test_is_service_provider` | `isinstance(provider, ServiceProvider)` is `True`. |
| `test_new_static_factory` | `new()` returns a populated provider with correct `_name`. |
| `test_add_service` | Single service registered and resolvable via `get_service`. |
| `test_add_services` | Multiple services registered and resolvable. |
| `test_add_constants` | Scalar constant injected into a dependent service via its constructor (not via direct `get_service`). |
| `test_get_service_success` | Registered service resolves to the correct type. |
| `test_get_service_not_found` | `TiferetError` raised with `error_code == 'INVALID_DEPENDENCY_ERROR'`. |
| `test_remove_service` | Service removed; no longer resolvable. |
| `test_remove_service_nonexistent` | No-op; no exception raised. |
| `test_build_injector_rebuilds_on_mutation` | `injector` reference changes after `add_service`. |

**Note on `test_add_constants`:** Scalars registered via `add_constants` are constructor injection parameters, not standalone resolvable services. The test must verify injection by resolving a service that depends on the constant:
```python
provider.add_services({'configurable_service': ConfigurableService})
provider.add_constants({'config_value': 'test_config'})
service = provider.get_service('configurable_service')
assert service.config_value == 'test_config'
```

### 4.4 Style Guide (`docs/core/di.md`)

Must cover the following sections:

- **Overview** — Purpose of the `di/` package and the two-layer DI distinction (`tiferet/di/` for app-level vs. `DIContext` for feature-level).
- **What is a ServiceProvider?** — Key characteristics and role in runtime (the four-step `AppManagerContext` lifecycle).
- **The ServiceProvider Abstract Base** — Full API with method semantics.
- **The DependenciesServiceProvider** — Three key design decisions: rebuild-on-mutation, empty scope guard, named injector.
- **Structured Code Design** — Artifact comment conventions (`# *** classes` / `# ** class:`) with layout examples for both `settings.py` and `dependencies.py`.
- **Scalar Constants vs. Service Types** — The `add_constants` constraint and correct usage pattern.
- **Creating a New ServiceProvider Implementation** — Full example with all abstract methods implemented.
- **Testing ServiceProvider Implementations** — Key testing patterns with code examples.
- **Package Layout** — Directory tree.
- **Conclusion** — Source pointers.

## 5. Acceptance Criteria

1. `tiferet/di/__init__.py` exports both `ServiceProvider` and `DependenciesServiceProvider`.
2. All 12 unit tests in `tiferet/di/tests/test_dependencies.py` pass (`pytest tiferet/di/` exits with code 0).
3. `DependenciesServiceProvider()` (no args) initializes without error and sets `injector = None`.
4. `DependenciesServiceProvider.get_service(id)` raises `TiferetError` with `error_code == 'INVALID_DEPENDENCY_ERROR'` for any unresolvable service ID, including when the provider is empty.
5. `docs/core/di.md` exists and covers all sections defined in §4.4.
6. Feature branch is named `<issue-number>-di-introduce-service-provider-package` and PR targets `v2.0a7-release`.
7. Feature branch is deleted after merge.

## 6. Non-Functional Requirements

- All code follows the structured artifact comment style defined in `docs/core/code_style.md`.
- All error handling uses `RaiseError.execute()` exclusively; no raw `raise` statements in implementation code.
- All public methods have RST docstrings with `:param`, `:type`, `:return`, and `:rtype` fields.
- `add_services` and `add_constants` are the preferred bulk-registration methods; `add_service` is for single-registration use cases.
- The scalar constants limitation of the `dependencies` library is documented in both `docs/core/di.md` and the `test_add_constants` test docstring.

## Related Code Style Documentation

- [code_style.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/code_style.md) — General structured code style.
- [di.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/di.md) — DI package conventions (introduced by this story).
