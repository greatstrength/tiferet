# Builders – Strategies and Patterns

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/builders/`  
**Version:** 2.0.0a9

## Overview

Builders are the top-level orchestration layer in Tiferet v2.0+. They serve as the primary public entry point for applications, replacing the previous direct usage of `AppManagerContext`.

A builder is responsible for:
- Loading the application service (repository)
- Preparing default services and constants
- Resolving interfaces via domain events
- Wiring dependency injection
- Executing features through the resolved interface context

The canonical example is `AppBuilder` in `tiferet/builders/main.py`.

## Role of Builders in the Architecture

Builders sit at the highest level of the runtime graph. They are what application code interacts with directly:

```python
from tiferet import AppBuilder

builder = AppBuilder()
builder.load_app_service(...)          # optional custom service
result = builder.run("basic_calc", "calc.add", data={"a": 5, "b": 3})
```

Key responsibilities:
- **Initialization** — cache and service provider setup
- **Service loading** — dynamic import of the app service (usually a repository)
- **Default configuration** — injecting `DEFAULT_SERVICES` and `DEFAULT_CONSTANTS`
- **Interface resolution** — calling `GetAppInterface` and validating the result
- **Execution** — delegating to `AppInterfaceContext.run()`

Builders are intentionally **thin** — they coordinate rather than implement business logic.

## The AppBuilder Pattern

`AppBuilder` follows a clear, reusable pattern:

### 1. Initialization

```python
def __init__(self):
    self.cache = {}
    self.service_provider = self.create_service_provider()
```

### 2. Service Provider Factory

A static factory allows downstream contexts to create providers consistently:

```python
@staticmethod
def create_service_provider(
    provider_type: type = DependenciesServiceProvider,
    type_map: Dict[str, type] = None,
    **constants
) -> ServiceProvider:
    ...
```

This is registered in the DI container so contexts can create scoped providers.

### 3. Loading the App Service

```python
def load_app_service(self, module_path=..., class_name=..., **parameters) -> 'AppBuilder':
    ...
    self.cache[APP_SERVICE_KEY] = app_service
    return self   # supports chaining
```

### 4. Loading Default Services & Constants

```python
def load_default_services(self) -> List[AppServiceDependency]:
    return [
        DomainObject.new(AppServiceDependency, **data, validate=False)
        for data in a.const.DEFAULT_SERVICES
    ]
```

Constants are passed via `default_constants=a.const.DEFAULT_CONSTANTS` to `GetAppInterface`.

### 5. Interface Resolution Flow

```python
def load_interface(self, interface_id: str) -> AppInterfaceContext:
    app_service = self.cache[APP_SERVICE_KEY]
    default_services = self.load_default_services()

    app_interface = DomainEvent.handle(
        GetAppInterface,
        dependencies={'app_service': app_service},
        interface_id=interface_id,
        default_services=default_services,
        default_constants=a.const.DEFAULT_CONSTANTS,
    )

    return self.load_app_instance(app_interface)
```

### 6. High-Level Run Method

```python
def run(self, interface_id: str, feature_id: str, headers=None, data=None, **kwargs):
    context = self.load_interface(interface_id)
    return context.run(feature_id, headers or {}, data or {}, **kwargs)
```

## When to Create a New Builder

Create a new builder when you need a specialized entry point:

- `CliBuilder` — for CLI-only applications with argument parsing
- `WebBuilder` — for Flask/FastAPI integration
- `TestBuilder` — for integration testing with mocked services

**Rule of thumb:** If you find yourself repeating the same loading + wiring logic in multiple scripts, extract it into a dedicated builder.

## Builder vs Context

| Concern                  | Builder                          | Context                              |
|--------------------------|----------------------------------|--------------------------------------|
| Public API               | Yes (`AppBuilder().run(...)`)    | Internal (used by builder)           |
| Service loading          | Yes                              | No                                   |
| Default config injection | Yes                              | No                                   |
| Feature execution        | Delegates to interface context   | Yes (`execute_feature`, `run`)       |
| Lifecycle                | Application-level                | Per-interface                        |

Builders are **application-level**; contexts are **interface-level**.

## Best Practices

### 1. Method Chaining

`load_app_service()` returns `self` to support fluent usage:

```python
builder = AppBuilder().load_app_service(...)
```

### 2. Defensive Service Lookup

Always check the cache before using `app_service`:

```python
app_service = self.cache.get(APP_SERVICE_KEY)
if not app_service:
    RaiseError.execute(...)
```

### 3. Consistent Error Handling

Use framework constants and `RaiseError.execute()` for all failure paths.

### 4. Keep Builders Thin

Builders should **not** contain domain logic — only orchestration, wiring, and delegation.

### 5. Register `create_service_provider`

Always register the builder’s static factory so contexts can create scoped providers:

```python
dependencies['create_service_provider'] = self.create_service_provider
```

## Related Documentation

- [docs/core/builders.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/builders.md) — Detailed `AppBuilder` implementation reference
- [docs/guides/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/contexts.md) — Context patterns and lifecycle
- [docs/guides/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/events.md) — Domain event usage in builders
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — Artifact comments and formatting