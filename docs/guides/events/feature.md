# Events – Feature Management

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/events/feature.py`  
**Version:** 2.0.0

## Overview

The feature event module provides the full CRUD surface for `Feature` domain objects — the configuration-driven workflow definitions that power Tiferet's feature execution engine. Every event in this module depends on an injected `FeatureService` and operates on `Feature` domain objects through the `FeatureAggregate` mapper.

Features are composed of ordered **steps** (`FeatureEvent` instances), each referencing a `service_id` that maps to a service configuration in the dependency injection container.

## Events at a Glance

| Event | Operation | Required Parameters | Returns |
|---|---|---|---|
| `AddFeature` | Create | `name`, `group_id` | `Feature` |
| `GetFeature` | Read (single) | `id` | `Feature` |
| `ListFeatures` | Read (all/filtered) | *(none)* | `List[Feature]` |
| `RemoveFeature` | Delete | `id` | `str` (ID) |
| `UpdateFeature` | Update (metadata) | `id`, `attribute` | `Feature` |
| `AddFeatureStep` | Add step | `id`, `name`, `service_id` | `str` (ID) |
| `UpdateFeatureStep` | Update step | `id`, `position`, `attribute` | `str` (ID) |
| `RemoveFeatureStep` | Remove step | `id`, `position` | `str` (ID) |
| `ReorderFeatureStep` | Reorder step | `id`, `start_position`, `end_position` | `str` (ID) |

## Dependency

All events inject a single dependency:

- **`feature_service: FeatureService`** — the service interface for persisting and retrieving `Feature` objects.

## Event Details

### AddFeature

Creates a new `Feature` with derived defaults, then persists it via `FeatureService.save()`.

**Required:** `name`, `group_id`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `feature_key` | `str` | snake_case of `name` | Explicit feature key |
| `id` | `str` | `{group_id}.{feature_key}` | Explicit full feature ID |
| `description` | `str` | same as `name` | Feature description |
| `steps` | `list` | `[]` | Initial feature steps |
| `log_params` | `dict` | `{}` | Logging parameters |

**Returns:** The created `Feature` instance.

**Errors:**
- `FEATURE_ALREADY_EXISTS` if a feature with the derived/explicit ID already exists.

```python
result = DomainEvent.handle(
    AddFeature,
    dependencies={'feature_service': feature_service},
    name='Calculate Sum',
    group_id='calc',
)
```

### GetFeature

Retrieves a `Feature` by ID from the repository.

**Required:** `id`

**Returns:** The `Feature` instance.

**Errors:**
- `FEATURE_NOT_FOUND` if the feature does not exist.

```python
feature = DomainEvent.handle(
    GetFeature,
    dependencies={'feature_service': feature_service},
    id='calc.calculate_sum',
)
```

### ListFeatures

Lists `Feature` objects, optionally filtered by `group_id`.

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `group_id` | `str` | `None` | Filter by group identifier |

**Returns:** `List[Feature]` — the list of feature objects.

```python
# All features
features = DomainEvent.handle(
    ListFeatures,
    dependencies={'feature_service': feature_service},
)

# Filtered by group
features = DomainEvent.handle(
    ListFeatures,
    dependencies={'feature_service': feature_service},
    group_id='calc',
)
```

### RemoveFeature

Removes a feature by ID. Delegates to `FeatureService.delete()`, which is expected to be idempotent.

**Required:** `id`

**Returns:** `str` — the feature ID.

```python
DomainEvent.handle(
    RemoveFeature,
    dependencies={'feature_service': feature_service},
    id='calc.calculate_sum',
)
```

### UpdateFeature

Updates basic metadata (`name` or `description`) on an existing feature.

**Required:** `id`, `attribute`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `value` | `Any` | — | The new value for the attribute |

**Supported attributes:** `name`, `description`

**Returns:** The updated `Feature` instance.

**Errors:**
- `INVALID_FEATURE_ATTRIBUTE` if the attribute is not `name` or `description`.
- `FEATURE_NAME_REQUIRED` if updating `name` with an empty value.
- `FEATURE_NOT_FOUND` if the feature does not exist.

```python
DomainEvent.handle(
    UpdateFeature,
    dependencies={'feature_service': feature_service},
    id='calc.calculate_sum',
    attribute='name',
    value='Calculate Total',
)
```

### AddFeatureStep

Adds a step to an existing feature's workflow. Steps reference a `service_id` that maps to a service configuration in the DI container.

**Required:** `id`, `name`, `service_id`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `parameters` | `dict` | `{}` | Step parameters |
| `data_key` | `str` | `None` | Result data key |
| `pass_on_error` | `bool` | `False` | Whether to continue on error |
| `position` | `int` | `None` | Insertion position (None to append) |

**Returns:** `str` — the feature ID.

**Errors:**
- `FEATURE_NOT_FOUND` if the feature does not exist.

```python
DomainEvent.handle(
    AddFeatureStep,
    dependencies={'feature_service': feature_service},
    id='calc.calculate_sum',
    name='Add Numbers',
    service_id='add_number_event',
    parameters={'precision': '2'},
    data_key='sum_result',
)
```

### UpdateFeatureStep

Updates an attribute on a feature step at a given position.

**Required:** `id`, `position`, `attribute`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `value` | `Any` | `None` | The new value for the attribute |

**Supported attributes:** `name`, `service_id`, `data_key`, `pass_on_error`, `parameters`

**Returns:** `str` — the feature ID.

**Errors:**
- `INVALID_FEATURE_COMMAND_ATTRIBUTE` if the attribute is not supported.
- `COMMAND_PARAMETER_REQUIRED` if updating `name` or `service_id` with an empty value.
- `FEATURE_NOT_FOUND` if the feature does not exist.
- `FEATURE_COMMAND_NOT_FOUND` if no step exists at the given position.

```python
DomainEvent.handle(
    UpdateFeatureStep,
    dependencies={'feature_service': feature_service},
    id='calc.calculate_sum',
    position=0,
    attribute='service_id',
    value='updated_service',
)
```

### RemoveFeatureStep

Removes a step from a feature by position. Idempotent — invalid positions result in a no-op.

**Required:** `id`, `position`

**Returns:** `str` — the feature ID.

**Errors:**
- `FEATURE_NOT_FOUND` if the feature does not exist.

```python
DomainEvent.handle(
    RemoveFeatureStep,
    dependencies={'feature_service': feature_service},
    id='calc.calculate_sum',
    position=0,
)
```

### ReorderFeatureStep

Moves a feature step from one position to another. The target position is clamped to the valid range. Idempotent for invalid start positions.

**Required:** `id`, `start_position`, `end_position`

**Returns:** `str` — the feature ID.

**Errors:**
- `FEATURE_NOT_FOUND` if the feature does not exist.

```python
DomainEvent.handle(
    ReorderFeatureStep,
    dependencies={'feature_service': feature_service},
    id='calc.calculate_sum',
    start_position=0,
    end_position=2,
)
```

## Migration Notes

### v2.0.0a6 Changes

- **Class renames:** `AddFeatureCommand` → `AddFeatureStep`, `UpdateFeatureCommand` → `UpdateFeatureStep`, `RemoveFeatureCommand` → `RemoveFeatureStep`, `ReorderFeatureCommand` → `ReorderFeatureStep`.
- **Parameter renames:** `attribute_id` → `service_id` in `AddFeatureStep.execute()` and `UpdateFeatureStep` valid attributes.
- **Parameter renames:** `commands` → `steps` in `AddFeature.execute()`.
- **Artifact comments:** Updated from `# *** commands` / `# ** command:` to `# *** events` / `# ** event:`.
- **Unused imports removed:** `Aggregate` and `FeatureEventAggregate` no longer imported.
