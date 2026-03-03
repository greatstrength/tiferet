# Domain – Feature (Workflow Orchestration)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/domain/feature.py`  
**Version:** 2.0.0a2

## Overview

The Feature domain defines **what the application does**. While the App domain assembles the runtime and the DI domain wires up services, the Feature domain describes the user-facing units of execution — the workflows that transform input into output.

A `Feature` is a named workflow composed of ordered steps. Each step references a domain event registered in the DI container and carries orchestration metadata — parameters, result routing, error handling behavior, and flag-based resolution. When a user calls `app.run('basic_calc', 'calc.add', data={'a': 1, 'b': 2})`, the framework loads the `calc.add` feature and executes its steps in sequence.

## Domain Objects

### Feature

The top-level workflow definition. A feature groups a sequence of steps under a composite identifier (`group_id.feature_key`).

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `str` (required) | Composite identifier, typically `{group_id}.{feature_key}` |
| `name` | `str` (required) | Human-readable name |
| `description` | `str` | Optional description |
| `group_id` | `str` (required) | Group identifier for organizing related features |
| `feature_key` | `str` (required) | Unique key within the group |
| `flags` | `List[str]` (default: `[]`) | Feature-level flags for dependency resolution |
| `steps` | `List[FeatureEvent]` (default: `[]`) | Ordered workflow steps |
| `log_params` | `Dict[str, str]` (default: `{}`) | Parameters to include in log output |

**Behavior method:**

- `get_step(position)` — retrieves the step at a given index, returning `None` for out-of-range positions. Used by events that update or remove individual steps.

### FeatureStep (base class)

The base class for any step in a feature workflow. `FeatureStep` defines the common contract that all step types share.

> **Rename note (v2.0a2):** The concept of a polymorphic step base class is new in v2.0a2. Previously, only `FeatureCommand` existed as a flat command reference.

`FeatureStep` enables future step types such as `FeatureCondition` (conditional routing), `FeatureLoop` (iteration), or any other workflow primitive — without changing the `Feature` model itself.

| Attribute | Type | Description |
|-----------|------|-------------|
| `type` | `str` (choices: `['event']`, default: `'event'`) | Discriminator indicating the step type. Currently only `'event'` is supported; future values (e.g., `'condition'`, `'loop'`) will enable new step behaviors. |
| `name` | `str` (required) | Human-readable name for the step |

### FeatureEvent (extends FeatureStep)

A concrete step that executes a domain event. This is the primary step type and carries the full orchestration metadata that `FeatureContext` uses to resolve, configure, and execute a domain event.

> **Rename note (v2.0a2):** Previously named `FeatureCommand`. Renamed to `FeatureEvent` to align with the `Command` → `DomainEvent` transition and to clarify that this step type specifically executes a domain event.

| Attribute | Type | Description |
|-----------|------|-------------|
| `attribute_id` | `str` (required) | References a `ServiceConfiguration` in the DI container |
| `flags` | `List[str]` (default: `[]`) | Step-level flags for dependency resolution (combined with feature-level flags) |
| `parameters` | `Dict[str, str]` (default: `{}`) | Static or dynamic parameters passed to the domain event |
| `data_key` | `str` | If set, the step's result is stored in the request data under this key |
| `pass_on_error` | `bool` (default: `False`) | If `True`, errors from this step are swallowed and the result is set to `None` |

*Inherited from FeatureStep:* `type` (always `'event'`), `name`.

### Parameter Resolution

The `parameters` dict supports two kinds of values:

- **Static values** — literal strings (e.g., `b: '0.5'` for the square root feature).
- **Request-backed values** — strings prefixed with `$r.` that are resolved from the request data at runtime (e.g., `$r.user_id` extracts `user_id` from the request).

This enables a single domain event to be reused across multiple features with different parameter configurations.

## Runtime Role

`FeatureContext` is the sole consumer of the Feature domain at runtime. The execution flow is:

1. **`execute_feature(feature_id, request)`** loads the `Feature` by ID (with caching).
2. For each step in `feature.steps`:
   - **`load_feature_command(step, feature.flags)`** resolves the domain event from the DI container using `attribute_id` and combined flags.
   - **`parse_request_parameter(value, request)`** resolves each parameter — static values pass through `ParseParameter`, `$r.`-prefixed values are looked up in the request data.
   - **`handle_command(command, request, data_key, pass_on_error)`** executes the domain event with the merged request data and parsed parameters.
3. If `data_key` is set, the step's return value is stored back into `request.data`, making it available to subsequent steps.
4. If `pass_on_error` is `True`, any exception from the step is caught and the result is set to `None`.

```python
# A feature with two steps — the second step uses the result of the first
# feature.yml:
#   calc.add_and_double:
#     steps:
#       - attribute_id: add_number_event
#         name: Add a and b
#         data_key: sum_result
#       - attribute_id: multiply_number_event
#         name: Double the sum
#         params:
#           a: $r.sum_result
#           b: '2'
```

## Configuration

Features are defined in `app/configs/feature.yml`:

```yaml
features:
  calc:
    add:
      name: 'Add Number'
      description: 'Adds one number to another'
      commands:
        - attribute_id: add_number_event
          name: Add `a` and `b`
    sqrt:
      name: 'Square Root'
      description: 'Calculates the square root of a number'
      commands:
        - attribute_id: exponentiate_number_event
          name: Calculate square root of `a`
          params:
            b: '0.5'
```

The two-level nesting (`calc.add`) becomes the composite `Feature.id`. The `commands` list maps to `steps`. The `sqrt` feature demonstrates parameter reuse — `exponentiate_number_event` is shared with the `exp` feature but configured with a fixed `b: '0.5'`.

## Domain Events

| Event | Purpose |
|-------|---------|
| `GetFeature` | Retrieve a feature by ID (used during execution) |
| `AddFeature` | Create a new feature configuration |
| `UpdateFeature` | Update name or description |
| `RemoveFeature` | Delete a feature configuration |
| `ListFeatures` | List features, optionally filtered by group |
| `AddFeatureCommand` | Append or insert a step into a feature's workflow |
| `UpdateFeatureCommand` | Update an attribute on a step at a given position |
| `RemoveFeatureCommand` | Remove a step by position |
| `ReorderFeatureCommand` | Move a step from one position to another |

## Service Interface

`FeatureService` (`tiferet/interfaces/feature.py`) — abstracts CRUD access to feature configurations.

## Relationship to Other Domains

- **DI domain** — Each `FeatureEvent.attribute_id` references a `ServiceConfiguration` in the DI registry. The DI container resolves the domain event class at runtime based on the attribute ID and any active flags.
- **App domain** — Features are executed within a loaded `AppInterface`. The interface's `flags` influence which flagged dependencies are used when resolving feature steps.
- **Error domain** — When a step raises a `TiferetError`, the error flows up through `AppInterfaceContext.handle_error()` to `ErrorContext`, which formats the structured error response.
- **CLI domain** — CLI commands map directly to feature IDs. When a user runs `calc add 1 2`, the CLI context constructs `feature_id = 'calc.add'` and delegates to `FeatureContext`.

## Related Documentation

- [docs/core/domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md) — DomainObject base class and general patterns
- [docs/core/contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md) — Context conventions and lifecycle
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) — Domain event patterns
- [docs/guides/domain/di.md](https://github.com/greatstrength/tiferet/blob/main/docs/guides/domain/di.md) — DI domain guide
