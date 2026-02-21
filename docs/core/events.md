# Domain Events in Tiferet

Domain Events are the primary operational units in the Tiferet framework. They encapsulate focused domain actions, validation, and service interactions in a consistent, injectable, and testable way.

This document describes the structure, design principles, and best practices for writing Domain Events, using the feature event suite as an example.

## What is a Domain Event?

A Domain Event is a class that performs a single, well-defined domain operation (e.g., `AddFeature`, `GetFeature`, `SetAppConstants`). Key characteristics:
- Extends the base `DomainEvent` class (`tiferet/events/settings.py`).
- Receives dependencies via constructor injection (usually a service or repository).
- Exposes an `execute(**kwargs)` method as the entry point.
- Uses `@DomainEvent.parameters_required([...])` for declarative input validation.
- Uses `verify` for domain-specific rule enforcement.
- Raises structured `TiferetError` instances via `raise_error`.
- Is invoked in production and tests via the static `DomainEvent.handle` method.

Domain Events are called by Contexts (often through injected handler callables) and return domain models, identifiers, or results.

### Role in Runtime
- **Execution**: Contexts use events to perform business logic (e.g., `FeatureContext` loads and executes feature events).
- **Validation**: Declarative parameter checks and domain rule enforcement prevent invalid operations.
- **Error Handling**: Consistent structured errors via `TiferetError`.
- **Dependency Injection**: Events are wired via `DomainEvent.handle` or container.

## Structured Code Design of Domain Events

Domain Events follow a strict artifact comment structure:

- `# *** events` – top-level section.
- `# ** event: <name>` – individual event (snake_case).
- `# * attribute: <name>` – injected dependencies.
- `# * init` – constructor.
- `# * method: execute` – main execution method.

**Spacing rules:**
- One empty line between `# *** events` and first `# ** event`.
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets.

**Example** – `tiferet/events/feature.py`:
```python
# *** imports

# ** core
from typing import List, Any

# ** app
from ..entities import Feature
from ..interfaces import FeatureService
from ..mappers import FeatureAggregate
from .settings import DomainEvent, a

# *** events

# ** event: add_feature
class AddFeature(DomainEvent):
    '''
    Event to add a new feature configuration.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the AddFeature event.

        :param feature_service: The feature service to use for managing feature configurations.
        :type feature_service: FeatureService
        '''

        # Set the feature service dependency.
        self.feature_service = feature_service

    # * method: execute
    @DomainEvent.parameters_required(['name', 'group_id'])
    def execute(self,
            name: str,
            group_id: str,
            feature_key: str | None = None,
            id: str | None = None,
            description: str | None = None,
            commands: list | None = None,
            log_params: dict | None = None,
            **kwargs,
        ) -> Feature:
        '''
        Add a new feature.

        :param name: Required feature name.
        :type name: str
        :param group_id: Required group identifier.
        :type group_id: str
        :param feature_key: Optional explicit key.
        :type feature_key: str | None
        :param id: Optional explicit full ID.
        :type id: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created Feature.
        :rtype: Feature
        '''

        # Create feature using the aggregate factory.
        feature = FeatureAggregate.new(
            name=name,
            group_id=group_id,
            feature_key=feature_key,
            id=id,
            description=description,
            commands=commands or [],
            log_params=log_params or {},
            **kwargs,
        )

        # Check for duplicate feature identifier.
        self.verify(
            expression=not self.feature_service.exists(feature.id),
            error_code=a.const.FEATURE_ALREADY_EXISTS_ID,
            message=f'Feature with ID {feature.id} already exists.',
            id=feature.id,
        )

        # Persist the new feature.
        self.feature_service.save(feature)

        # Return the created feature.
        return feature
```

## Parameter Validation

### Declarative: `@parameters_required`

The `@DomainEvent.parameters_required([...])` decorator is placed directly above the `execute` method. It validates all listed parameters **before** the method body runs and raises a single aggregated `TiferetError` if any fail.

A parameter is **invalid** if it is:
- Missing from `kwargs`
- `None`
- A `str` that is empty after `.strip()`

**Falsy-but-valid** values pass validation: `0`, `0.0`, `False`, `[]`, `{}`.

```python
# * method: execute
@DomainEvent.parameters_required(['id', 'name', 'attribute_id'])
def execute(self, id: str, name: str, attribute_id: str, **kwargs) -> str:
    ...
```

### Domain Rules: `verify`

Domain-specific checks (existence, uniqueness, attribute validity, etc.) remain as manual `self.verify(…)` calls inside `execute`:

```python
# Verify that the feature exists.
self.verify(
    expression=feature is not None,
    error_code=a.const.FEATURE_NOT_FOUND_ID,
    feature_id=id,
)
```

### When to Use Which

- **`@parameters_required`**: Required input presence — applied to `execute` as a decorator.
- **`verify`**: Business rules, existence checks, constraint enforcement — called inside `execute`.
- **`raise_error`**: Direct error raising when `verify` is not appropriate (e.g., inside `if` blocks).

## Creating New and Extending Existing Domain Events

### 1. Define the Event Class
- Place under `# *** events` in a domain-specific module.
- Extend `DomainEvent`.
- Declare dependencies under `# * attribute`.
- Implement `__init__` and `execute`.
- Add `@DomainEvent.parameters_required([...])` for required inputs.

**Example** – `GetFeature`:
```python
# ** event: get_feature
class GetFeature(DomainEvent):
    '''
    Event to retrieve a feature by its identifier.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the GetFeature event.

        :param feature_service: The feature service to use for retrieving features.
        :type feature_service: FeatureService
        '''

        # Set the feature service dependency.
        self.feature_service = feature_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> Feature:
        '''
        Retrieve a feature by ID.

        :param id: The feature identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The retrieved feature.
        :rtype: Feature
        '''

        # Retrieve the feature from the feature service.
        feature = self.feature_service.get(id)

        # Verify that the feature exists; raise FEATURE_NOT_FOUND if it does not.
        self.verify(
            expression=feature is not None,
            error_code=a.const.FEATURE_NOT_FOUND_ID,
            feature_id=id,
        )

        # Return the retrieved feature.
        return feature
```

### 2. Use in Context or Integration
- Inject event instance into contexts.
- Call via `event.execute(...)` or `DomainEvent.handle` in tests.

### Best Practices
- Use `# * attribute`, `# * init`, `# * method: execute` consistently.
- Use `@DomainEvent.parameters_required([...])` for all required input parameters.
- Use `verify` for domain rules.
- Raise structured errors via `raise_error`.
- Return domain models or identifiers.
- Keep events focused on one operation.

## Testing Domain Events

Tests validate parameter validation, service interactions, and error handling.

**Structure:**
- `# *** fixtures`
- `# ** fixture: <name>`
- `# *** tests`
- `# ** test: <name>`

**Invocation**: Always use `DomainEvent.handle` in tests.

**Example** – `GetFeature` tests:
```python
# ** test: get_feature_success
def test_get_feature_success(mock_feature_service: FeatureService, sample_feature: Feature) -> None:
    '''
    Test successful retrieval of a feature via GetFeature.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param sample_feature: The sample feature instance.
    :type sample_feature: Feature
    '''

    # Arrange the feature service to return the sample feature.
    mock_feature_service.get.return_value = sample_feature

    # Execute the command via the static DomainEvent.handle interface.
    result = DomainEvent.handle(
        GetFeature,
        dependencies={'feature_service': mock_feature_service},
        id='group.sample_feature',
    )

    # Assert that the feature is returned and the service was called as expected.
    assert result is sample_feature
    mock_feature_service.get.assert_called_once_with('group.sample_feature')
```

### Best Practices
- Mock injected services.
- Test success, validation failures, and not-found cases.
- Verify service calls and return values.

## Conclusion

Domain Events are the operational core of Tiferet applications, providing validated, injectable domain operations. Their structured design ensures consistency, testability, and extensibility.

### Key Architectural Concepts
- **Entities** (`tiferet/entities/`) — Read-only domain structure. Define the shape of domain objects (e.g., `Feature`, `FeatureEvent`).
- **Aggregates** (`tiferet/mappers/`) — Extend entities with creation and mutation behavior (e.g., `FeatureAggregate` provides `new`, `add_event`, `rename`, `reorder_event`). Events use aggregates for all creation and mutation operations.
- **Interfaces** (`tiferet/interfaces/`) — Service contracts consumed by events (e.g., `FeatureService`).

Developers can create new events by following the artifact pattern, using `@DomainEvent.parameters_required` for input validation, and invoking via `DomainEvent.handle`. Explore `tiferet/events/` for the base class and domain event implementations, `tiferet/mappers/` for aggregates, and corresponding `tests/` directories for test examples.
