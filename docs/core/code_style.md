# Structured Code Style in Tiferet

The Tiferet framework enforces a structured code style to ensure consistency, readability, extensibility, and AI-parsability across all components. This style relies on **artifact comments** for hierarchical organization and strict formatting conventions for docstrings, parameters, snippets, and spacing.

This document defines the required code style for all modules in the `tiferet` package and serves as a guide for application-level code.

## Artifact Comments: Hierarchy and Purpose

Artifact comments provide a predictable, machine-readable structure that organizes code into clear sections and sub-sections.

### Top-Level (`# ***`)
Denotes major module sections:
- `# *** imports` — all import statements.
- `# *** exports` — public API (only in `__init__.py`).
- `# *** models`, `# *** commands`, `# *** contexts`, `# *** contracts`, `# *** data`, `# *** repositories`, `# *** proxies` — component groups.

**Spacing**: One empty line between top-level comment and first mid-level comment.

### Mid-Level (`# **`)
Specifies categories or individual components:
- For imports: `# ** core`, `# ** infra`, `# ** app`.
- For components: `# ** model: <snake_case_name>`, `# ** command: <snake_case_name>`, etc.

**Spacing**: One empty line between mid-level comments.

### Low-Level (`# *`)
Defines subcomponents within a class:
- `# * attribute: <name>` — instance attributes.
- `# * init` — constructor.
- `# * method: <name>` — instance methods.
- `# * method: <name> (static)` — **static methods** (e.g., `ParseParameter.execute`).

**Spacing**: One empty line between low-level comments and code blocks.

**Enhancement**: The `(static)` suffix explicitly distinguishes static utilities from instance methods, improving clarity for readers and AI tools.

## Code Formatting Conventions

### Docstrings
- Use reStructuredText (RST) format.
- Include description, `:param`/`:type`, `:return`/`:rtype` for all parameters and returns.
- One empty line after docstring before first code snippet.

### Parameter Indentation
For methods with >3 parameters, indent to align with opening parenthesis:
```python
def execute(self,
            id: str,
            name: str,
            module_path: str,
            class_name: str,
            **kwargs):
```

### Code Snippets
- Each logical step is a separate snippet.
- Precede with 1–2 comment lines describing intent.
- One empty line between snippets.

**Example of code snippets within a method** (`FeatureContext.load_feature`):
```python
# * method: load_feature
def load_feature(self, feature_id: str) -> Feature:
    '''
    Load a feature by its ID, using the cache when possible.
    '''

    # Try to get the feature from the cache first.
    feature = self.cache.get(feature_id)

    # If not in cache, retrieve via command and cache the result.
    if not feature:
        feature = self.get_feature_handler(id=feature_id)
        self.cache.set(feature_id, feature)

    # Return the loaded feature.
    return feature
```

### Spacing Rules
- One empty line between:
  - Top-level sections and first mid-level.
  - Mid-level comments.
  - Low-level comments and code.
  - Code snippets within a method.
  - Methods/attributes within a class.
  - Classes within a component group.

## Deprecation Handling

Mark obsolete methods with:
- A comment note (e.g., `# NOTE: This method is obsolete and will be removed in v2`).
- A docstring note indicating deprecation and preferred alternative.

**Example**:
```python
# * method: handle_command (obsolete)
def handle_command(self, ...):
    '''
    Handle the execution of a command.
    
    NOTE: This method is obsolete and will be consolidated in v2.
    Use handle_feature_command instead.
    '''
    ...
```

**Purpose**: Prevents accidental use of legacy APIs and guides developers to modern patterns.

## Example: Complete Class with Formatting

**Command Example** – `GetFeature`:
```python
# *** imports

# ** app
from .settings import Command
from ..contracts.feature import FeatureService
from ..models.feature import Feature

# *** commands

# ** command: get_feature
class GetFeature(Command):
    '''
    Command to retrieve a feature by its identifier.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * init
    def __init__(self, feature_service: FeatureService) -> None:
        '''
        Initialize the GetFeature command.
        '''
        self.feature_service = feature_service

    # * method: execute
    def execute(self, id: str, **kwargs) -> Feature:
        '''
        Retrieve a feature by ID.

        :param id: The feature ID.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The Feature model.
        :rtype: Feature
        '''

        # Retrieve the feature from the service.
        feature = self.feature_service.get(id)

        # If not found, raise structured error.
        if not feature:
            self.raise_error(
                const.FEATURE_NOT_FOUND_ID,
                f'Feature not found: {id}',
                feature_id=id
            )

        # Return the loaded feature.
        return feature
```

## Brief Test Example with Formatting

**Test Example** – `test_get_feature_success`:
```python
# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.commands.feature import GetFeature
from tiferet.models.feature import Feature

# *** fixtures

# ** fixture: mock_feature_service
@pytest.fixture
def mock_feature_service() -> FeatureService:
    '''
    Mock FeatureService for testing.
    '''
    return mock.Mock(spec=FeatureService)

# ** fixture: sample_feature
@pytest.fixture
def sample_feature() -> Feature:
    '''
    Sample Feature instance for testing.
    '''
    return ModelObject.new(Feature, id='test.feature', name='Test Feature')

# *** tests

# ** test: get_feature_success
def test_get_feature_success(mock_feature_service: FeatureService, sample_feature: Feature) -> None:
    '''
    Test successful retrieval of a feature.

    :param mock_feature_service: Mocked service.
    :type mock_feature_service: FeatureService
    :param sample_feature: Sample feature instance.
    :type sample_feature: Feature
    '''
    mock_feature_service.get.return_value = sample_feature

    result = Command.handle(
        GetFeature,
        dependencies={'feature_service': mock_feature_service},
        id='test.feature'
    )

    assert result is sample_feature
    mock_feature_service.get.assert_called_once_with('test.feature')
```

## Domain Event Test Harness Style

Domain event tests use a class-based harness that provides auto-mocking, auto-parametrized validation tests, and a consistent invocation helper. All harness-based test classes follow these conventions.

### Artifact Comments

Harness test classes use `# ** test: TestClassName` (PascalCase) as the mid-level comment. Within each class:

- `# * attribute: <name>` — class-level configuration attributes.
- `# * fixture: <name>` — fixture overrides.
- `# * method: <name>` — custom test methods.

```python
# *** tests

# ** test: TestAddAppInterface
class TestAddAppInterface(DomainEventTestBase):
    '''
    Tests for AddAppInterface using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = AddAppInterface

    # * attribute: dependencies
    dependencies = {'app_service': AppService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='test.interface',
        name='Test Interface',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
    )

    # * attribute: required_params
    required_params = ['id', 'name', 'module_path', 'class_name']

    # * method: test_minimal_success
    def test_minimal_success(self, mock_dependencies):
        '''
        Test creating a minimal app interface with only required parameters.
        '''

        # Execute via the harness handle helper.
        interface = self.handle(mock_dependencies)

        # Assert the result is an AppInterface instance.
        assert isinstance(interface, AppInterface)

        # Assert the interface is saved via the app service.
        mock_dependencies['app_service'].save.assert_called_once_with(interface)
```

### Required Class Attributes

Every harness test class must declare these attributes with `# * attribute:` comments:

| Attribute | Base | Description |
|---|---|---|
| `event_cls` | `DomainEventTestBase` | The `DomainEvent` subclass under test |
| `dependencies` | `DomainEventTestBase` | Dict of dependency name → type (auto-mocked) |
| `sample_kwargs` | `DomainEventTestBase` | Default kwargs for a successful `execute()` |
| `required_params` | `DomainEventTestBase` | List of param names for auto validation tests |
| `service_attr` | `ServiceEventTestBase` | Dependency name for the primary service |
| `not_found_error_code` | `ServiceEventTestBase` | Error code for the not-found auto-test |
| `not_found_kwargs` | `ServiceEventTestBase` | Kwargs that trigger the not-found path |

### Fixture Overrides

When a test class needs a pre-configured service mock (e.g., `get()` returns a real aggregate), override `mock_dependencies` as a fixture within the class:

```python
    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, app_interface):
        '''
        Override to provide a service mock pre-configured with an app_interface.
        '''

        # Create a mock AppService that returns the app_interface on get.
        service = mock.Mock(spec=AppService)
        service.get.return_value = app_interface
        return {'app_service': service}
```

### Spacing Rules

Harness test classes follow the same spacing conventions as production code:
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets within methods.
- One empty line between test classes.

## Best Practices Summary

- Use artifact comments consistently.
- Explicitly mark static methods with `(static)`.
- Deprecate obsolete methods with clear notes.
- Write clear RST docstrings.
- Break methods into commented snippets.
- Maintain consistent spacing.
- Prefer the domain event test harness (`DomainEventTestBase` / `ServiceEventTestBase`) for all new event tests.

These practices ensure Tiferet code remains consistent, maintainable, and AI-friendly. Explore source modules in `tiferet/` for implementation examples.

## Additional Linked Code Style Documents

The Tiferet framework maintains a suite of focused documentation in `docs/core/` to guide consistent implementation across different component types. These documents complement the main **Structured Code Style** guidelines and provide domain-specific conventions.

- **[assets.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/assets.md)** – Assets layer conventions (imports, constants, functions, standalone classes, exports).
- **[domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md)** – Domain object conventions (dual role, factory methods, read-only design).
- **[events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md)** – Domain event conventions (dependency injection, validation, test harness).
- **[mappers.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/mappers.md)** – Aggregate and TransferObject conventions.
- **[interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md)** – Service interface conventions.
- **[repos.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/repos.md)** – Repository implementation conventions.
- **[utils.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/utils.md)** – Utility and infrastructure conventions.

Additional component-style documents (e.g., contexts) will be added as the framework evolves. Refer to this list for the current set of authoritative style guides.
