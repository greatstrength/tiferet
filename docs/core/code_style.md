# Structured Code Style in Tiferet

The Tiferet framework enforces a structured code style to ensure consistency, readability, extensibility, and AI-parsability across all components. This style relies on **artifact comments** for hierarchical organization and strict formatting conventions for docstrings, parameters, snippets, and spacing.

This document defines the required code style for all modules in the `tiferet` package and serves as a guide for application-level code.

## Artifact Comments: Hierarchy and Purpose

Artifact comments provide a predictable, machine-readable structure that organizes code into clear sections and sub-sections.

### Top-Level (`# ***`)
Top-level comments denote major module sections, which fall into two kinds: **preamble groups** (available in every module) and **construct groups** (the module's primary body).

**Preamble artifact section groups** are available in *any* module, regardless of its construct type (`# *** events`, `# *** utils`, etc.). There are four, and they appear in this order when present:
- `# *** imports` — all import statements.
- `# *** constants` — module-level constant definitions.
- `# *** functions` — module-level, side-effect-free helper functions. A helper belongs here when it takes only its arguments and returns a plain value: no `self`, no injected services, and no domain-object returns. Prefer this over duplicating the same logic as a static method across classes.
- `# *** classes` — generic or base classes not tied to a specific construct type (e.g., the base classes defined in a `settings.py`).

**Construct groups** form the primary body of a module and are selected by what the module defines — for example `# *** models`, `# *** events`, `# *** contexts`, `# *** interfaces`, `# *** mappers`, `# *** repos`, `# *** utils`, `# *** blueprints`. The `# *** exports` group lists the public API and appears only in `__init__.py`.

A module combines its preamble groups with its construct group(s), ordered `imports` → `constants` → `functions`, then `classes` and/or the construct group(s). For example, a domain-event module that needs a pure helper is laid out as:
```python
# *** imports
...

# *** functions

# ** function: _is_valid_identifier
def _is_valid_identifier(name: str) -> bool:
    '''
    Validate that a name is a valid SQLite identifier.

    :param name: The identifier to validate
    :type name: str
    :return: True if valid, False otherwise
    :rtype: bool
    '''

    # Basic check: alphanumeric and underscore only, doesn't start with digit
    if not name:
        return False
    if name[0].isdigit():
        return False
    return all(c.isalnum() or c == '_' for c in name)

# *** events
...
```

**Spacing**: One empty line between top-level comment and first mid-level comment.

### Sub-Groups (`# *** <kind> (<sub-group>)`)
A large section may be partitioned into **sub-groups** by adding a parenthetical qualifier to the top-level comment. The section/artifact kind is preserved — only the parenthetical names a partition within that kind. This reuses the same parenthetical-qualifier idea already applied to methods with `(static)`.

Use a sub-group only when a single section grows large enough that partitioning aids navigation; small sections stay ungrouped. A module may therefore contain one plain section plus one or more sub-grouped sections of the same kind. For example, `constants.py` keeps language constants under `# *** constants` and error-id constants under `# *** constants (error)`:
```python
# *** constants

# ** constant: en_us
EN_US = 'en_US'

# *** constants (error)

# ** constant: error_not_found_id
ERROR_NOT_FOUND_ID = 'ERROR_NOT_FOUND'
```
The most common use is grouping unit tests by the class or method under test, so a single test module can hold several focused groups:
```python
# *** tests (GetFeature)

# ** test: TestGetFeatureSuccess
...

# *** tests (AddFeature)

# ** test: TestAddFeatureSuccess
...
```
**Grammar rules:**
- Preserve the kind: the word after `# ***` stays the normal section kind (`constants`, `tests`, ...); the parenthetical is only a label.
- The parenthetical names the sub-group; keep it short and consistent within the module.
- Sub-groups do not nest — use at most one parenthetical qualifier per top-level comment.
- Order any plain (ungrouped) section of a kind before its sub-grouped variants.
- Individual artifacts keep their standard mid-level label (`# ** constant:`, `# ** test:`); the sub-group never changes the `# **` line.

**Interim scope**: this convention exists primarily so agents editing source directly (and their human handlers) can navigate large sections consistently. Treat this document as the canonical reference until the full grammar is formalized.

**Spacing**: One empty line between a sub-group comment and its first mid-level comment, the same as any top-level section.

### Mid-Level (`# **`)
Specifies categories or individual components:
- For imports: `# ** core`, `# ** infra`, `# ** app`.
- For functions: `# ** function: <snake_case_name>`.
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

## Annotation Artifacts

Annotation artifacts are **transient lifecycle markers** — a fourth tier below the structural `# ***` / `# **` / `# *` hierarchy. Unlike structural comments, annotations describe *state* rather than *shape* and are expected to be resolved over time.

Two annotation types are defined:

### `# ++ todo: <message>`
Signals deferred work attached to a specific artifact. The `++` prefix is semantic: *something needs to be added or grown here*. Use it to leave a machine-scannable note for the next agent or developer who touches this artifact.

### `# -- obsolete: <reason or target version>`
Signals that an artifact is deprecated and slated for removal. The `--` prefix is semantic: *this is being reduced or removed*. Replaces the informal `# NOTE:` docstring approach with a single, consistently placed annotation line.

**Placement grammar** — annotations appear immediately after the structural comment they annotate, on their own line, before the code body:

```python
# * method: remove_service
# ++ todo: remove attribute_id parameter once app event test dependency is resolved
def remove_service(self, service_id: str | None = None, attribute_id: str | None = None):
    ...

# * attribute: return_to_data
# -- obsolete: superseded by data_key; remove in v2.1
return_to_data: bool = Field(default=False, ...)
```

Annotations may also appear below `# **` (mid-level) or `# ***` (top-level) comments when the todo or obsolescence applies to an entire section or class. Inside method bodies, `# ++ todo:` follows the same inline-before-snippet placement as any other snippet comment.

**Label-level shorthand** — the `(obsolete)` parenthetical suffix on a `# *` or `# **` label remains valid shorthand when no further reason is needed:

```python
# * method: handle_command (obsolete)
```

When a reason or target version is meaningful, prefer `# -- obsolete:` on its own line.

**Resolution expectations**
- `# ++ todo:` annotations should be removed once the described work is complete. Reference the GitHub issue number in the message when the work is tracked (`# ++ todo: #123 — remove attribute_id once ...`).
- `# -- obsolete:` annotations should be removed together with the artifact they annotate. Verify no callers remain before deletion.
- Both types should be surfaced in Collaboration Reports when introduced or resolved during a session.

**Agent scan procedure** — before beginning any implementation session, scan affected files for open annotations:

```bash
grep -rn "# ++\|# --" tiferet/
```

This gives an immediate picture of outstanding technical debt and deprecated code in scope.

## Example: Complete Class with Formatting

**Domain Event Example** – `GetFeature`:
```python
# *** imports

# ** app
from .settings import DomainEvent, a
from ..interfaces import FeatureService
from ..domain import Feature

# *** events

# ** event: get_feature
class GetFeature(DomainEvent):
    '''
    Domain event to retrieve a feature by its identifier.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * init
    def __init__(self, feature_service: FeatureService) -> None:
        '''
        Initialize the GetFeature event.
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
                a.const.FEATURE_NOT_FOUND_ID,
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
from tiferet.events.settings import DomainEvent
from tiferet.events.feature import GetFeature
from tiferet.interfaces import FeatureService
from tiferet.domain import Feature

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
    return Feature(id='test.feature', name='Test Feature')

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

    result = DomainEvent.handle(
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

# ** test: TestAddAppSession
class TestAddAppSession(DomainEventTestBase):
    '''
    Tests for AddAppSession using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = AddAppSession

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

        # Assert the result is an AppSession instance.
        assert isinstance(interface, AppSession)

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
    def mock_dependencies(self, app_session):
        '''
        Override to provide a service mock pre-configured with an app_session.
        '''

        # Create a mock AppService that returns the app_session on get.
        service = mock.Mock(spec=AppService)
        service.get.return_value = app_session
        return {'app_service': service}
```

### Spacing Rules

Harness test classes follow the same spacing conventions as production code:
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets within methods.
- One empty line between test classes.

## Best Practices Summary

- Use artifact comments consistently.
- Partition large sections into sub-groups (`# *** <kind> (<sub-group>)`) when it aids navigation, preserving the section kind and per-artifact labels.
- Explicitly mark static methods with `(static)`.
- Deprecate obsolete methods with clear notes.
- Write clear RST docstrings.
- Break methods into commented snippets.
- Maintain consistent spacing.
- Place module-level, side-effect-free helpers under `# *** functions` instead of duplicating them as static methods across classes.
- Prefer the domain event test harness (`DomainEventTestBase` / `ServiceEventTestBase`) for all new event tests.

These practices ensure Tiferet code remains consistent, maintainable, and AI-friendly. Explore source modules in `tiferet/` for implementation examples.

## Additional Linked Code Style Documents

The Tiferet framework maintains a suite of focused documentation in `docs/core/` to guide consistent implementation across different component types. These documents complement the main **Structured Code Style** guidelines and provide domain-specific conventions.

For implementation agents, the **`tiferet-code-<component>` skills** (see `docs/collab/agents/skills/`) are the preferred access path — they embed key conventions and a working example offline. Each entry below lists the companion skill alongside the full doc as the authoritative fallback.

- **`tiferet-code-assets`** / **[assets.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/assets.md)** – Assets layer conventions (imports, constants, functions, standalone classes, exports).
- **`tiferet-code-blueprints`** / **[blueprints.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/blueprints.md)** – Blueprint orchestration conventions.
- **`tiferet-code-contexts`** / **[contexts.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/contexts.md)** – Context conventions (high-level and low-level runtime shape).
- **`tiferet-code-di`** / **[di.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/di.md)** – Dependency injection layer conventions.
- **`tiferet-code-domain`** / **[domain.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/domain.md)** – Domain object conventions (dual role, factory methods, read-only design).
- **`tiferet-code-events`** / **[events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md)** – Domain event conventions (dependency injection, validation, test harness).
- **`tiferet-code-interfaces`** / **[interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md)** – Service interface conventions.
- **`tiferet-code-mappers`** / **[mappers.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/mappers.md)** – Aggregate and TransferObject conventions.
- **`tiferet-code-repos`** / **[repos.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/repos.md)** – Repository implementation conventions.
- **`tiferet-code-testing`** / **[testing.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/testing.md)** – Testing harness conventions (AggregateTestBase, TransferObjectTestBase, DomainEventTestBase).
- **`tiferet-code-utils`** / **[utils.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/utils.md)** – Utility and infrastructure conventions.
