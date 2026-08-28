# Technical Requirements Document: Mappers – Attribute Allow-List Consolidation

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet
**Date:** August 28, 2026
**Version:** 2.0.2
**Type:** Hotfix

## 1. Overview

Three `Aggregate` subclasses duplicate an identical ~15-line "settable-attribute allow-list guard": `AppSessionAggregate.set_attribute` (`tiferet/mappers/app.py:184`), `CliArgumentAggregate.set_attribute` and `CliCommandAggregate.set_attribute` (`tiferet/mappers/cli.py`). Each defines a local `supported = {...}` set, raises `ModelError.raise_error(ATTRIBUTE_NOT_SETTABLE_ID, ...)` with an identical message shape when the given attribute isn't in it, and otherwise calls `setattr(self, attribute, value)`. Only the set contents differ per class.

`mappers/core.py`'s `TransferObject` already establishes a declarative ClassVar idiom for exactly this kind of per-subclass configuration: `_ROLES: ClassVar[Dict[str, Dict[str, Any]]]`. This TRD mirrors that idiom on `Aggregate`: a `_SETTABLE_ATTRIBUTES` ClassVar that, when declared, restricts `set_attribute` to the named fields; when left at its default `None`, `set_attribute` behaves exactly as it does today — no restriction, any valid Pydantic field may be assigned. This is a pure structural consolidation with no observable behavior change for any existing aggregate.

## 2. Scope

### In Scope
- Add `_SETTABLE_ATTRIBUTES: ClassVar[Optional[set]] = None` to `Aggregate` in `tiferet/mappers/core.py`.
- Update `Aggregate.set_attribute` to enforce membership in `_SETTABLE_ATTRIBUTES` when it is not `None`, raising the identical `ModelError` shape the three duplicated methods raise today; fall through to the existing `setattr` / `ValidationError`→`ModelError` handling otherwise.
- Remove `AppSessionAggregate.set_attribute` (`tiferet/mappers/app.py`); declare `_SETTABLE_ATTRIBUTES = {'name', 'description', 'logger_id', 'flags'}` instead.
- Remove `CliArgumentAggregate.set_attribute` (`tiferet/mappers/cli.py`); declare `_SETTABLE_ATTRIBUTES = {'description', 'type', 'required', 'default', 'choices', 'nargs'}` instead.
- Remove `CliCommandAggregate.set_attribute` (`tiferet/mappers/cli.py`); declare `_SETTABLE_ATTRIBUTES = {'name', 'description', 'key', 'group_key'}` instead.
- Drop the now-unused `ATTRIBUTE_NOT_SETTABLE_ID` and `ModelError` imports from `tiferet/mappers/app.py` and `tiferet/mappers/cli.py` (each is referenced only inside the method being removed).

### Out of Scope
- **`ErrorAggregate`, `ServiceRegistrationAggregate`, `FeatureAggregate`.** None declares a `set_attribute` override or an allow-list today; leaving `_SETTABLE_ATTRIBUTES` at its default `None` preserves their current unrestricted behavior exactly.
- **`EventFeatureStepAggregate.set_attribute`** (`tiferet/mappers/feature.py`). It special-cases `parameters` and `pass_on_error`, then falls through to `super().set_attribute(attribute, value)` for every other field — a deliberate unrestricted path. `EventFeatureStepAggregate` declares no `_SETTABLE_ATTRIBUTES`, so the default `None` sentinel must leave that fallthrough exactly as unrestricted as it is today. This is the load-bearing reason the default is `None` (no restriction) rather than an empty set (restrict to nothing).
- **Test files.** `AggregateTestBase.test_set_attribute` (`tiferet/testing/mappers.py`) drives behavior generically through each subclass's `set_attribute_params`, asserting only the resulting value or `error_code` — never implementation. The existing `set_attribute_params` in `tests/mappers/test_app.py` and `tests/mappers/test_cli.py` are expected to pass unmodified; no test file changes are anticipated (verify in §5, AC 6).

## 3. Components Affected

| Component | File/Path | Artifact action |
|-----------|-----------|-----------------|
| Mapper core base | `tiferet/mappers/core.py` | Update — `Aggregate`: add `_SETTABLE_ATTRIBUTES` ClassVar; update `set_attribute` |
| App mappers | `tiferet/mappers/app.py` | Remove — `AppSessionAggregate.set_attribute`; Add — `_SETTABLE_ATTRIBUTES`; Update — imports |
| CLI mappers | `tiferet/mappers/cli.py` | Remove — `CliArgumentAggregate.set_attribute`, `CliCommandAggregate.set_attribute`; Add — `_SETTABLE_ATTRIBUTES` on each; Update — imports |

## 4. Detailed Requirements

### 4.1 Update: `# ** class: aggregate` in `tiferet/mappers/core.py`

Add the import and the ClassVar, then update `set_attribute`.

| Element | Current | Target |
|---|---|---|
| `# ** app` import | `from ..domain import DomainObject, ModelError` | `from ..domain import ATTRIBUTE_NOT_SETTABLE_ID, DomainObject, ModelError` |
| New attribute | — | `# * attribute: _SETTABLE_ATTRIBUTES` — `_SETTABLE_ATTRIBUTES: ClassVar[Optional[set]] = None` |

`Optional` must be added to the `typing` import (`from typing import Any, ClassVar, Dict, Optional`).

```python
# * attribute: _SETTABLE_ATTRIBUTES
_SETTABLE_ATTRIBUTES: ClassVar[Optional[set]] = None

# * method: set_attribute
def set_attribute(self, attribute: str, value: Any) -> None:
    '''
    Update an attribute on the aggregate, converting any Pydantic validation
    failure (unknown attribute or invalid value) into a ModelError.

    When the subclass declares ``_SETTABLE_ATTRIBUTES`` (not None), only
    attributes in that set may be assigned; any other name raises a
    ModelError with ATTRIBUTE_NOT_SETTABLE_ID. The default None enforces no
    restriction beyond ordinary Pydantic field validation.

    :param attribute: The attribute name to update.
    :type attribute: str
    :param value: The new value to assign.
    :type value: Any
    :return: None
    :rtype: None
    '''

    # Enforce the declared allow-list, when the subclass declares one.
    settable = type(self)._SETTABLE_ATTRIBUTES
    if settable is not None and attribute not in settable:
        supported_names = ', '.join(sorted(settable))
        ModelError.raise_error(
            ATTRIBUTE_NOT_SETTABLE_ID,
            message=f'Invalid attribute: {attribute}. Supported attributes are {supported_names}.',
            model=self,
            attribute=attribute,
            supported=supported_names,
        )

    # Apply the update; validate_assignment=True triggers field validation.
    try:
        setattr(self, attribute, value)
    except ValidationError as error:
        ModelError.raise_for_validation(error, model=self, attribute=attribute)
```

### 4.2 Update: `AppSessionAggregate` in `tiferet/mappers/app.py`

| Action | Element |
|---|---|
| Remove | `# * method: set_attribute` (current lines 183–218) |
| Add | `# * attribute: _SETTABLE_ATTRIBUTES` — `_SETTABLE_ATTRIBUTES: ClassVar[set] = {'name', 'description', 'logger_id', 'flags'}` |
| Update import | Remove `ATTRIBUTE_NOT_SETTABLE_ID` and `ModelError` from the `..domain` import (both become unused in this file) |

### 4.3 Update: `CliArgumentAggregate` and `CliCommandAggregate` in `tiferet/mappers/cli.py`

| Action | Class | Element |
|---|---|---|
| Remove | `CliArgumentAggregate` | `# * method: set_attribute` (current lines 23–60) |
| Add | `CliArgumentAggregate` | `_SETTABLE_ATTRIBUTES: ClassVar[set] = {'description', 'type', 'required', 'default', 'choices', 'nargs'}` |
| Remove | `CliCommandAggregate` | `# * method: set_attribute` (current lines 120–155) |
| Add | `CliCommandAggregate` | `_SETTABLE_ATTRIBUTES: ClassVar[set] = {'name', 'description', 'key', 'group_key'}` |
| Update import | — | `from ..domain import CliArgument, CliCommand` (drop `ATTRIBUTE_NOT_SETTABLE_ID`, `ModelError`, both unused in this file after removal) |

`CliCommandAggregate.add_argument` is untouched.

## 5. Acceptance Criteria

1. `Aggregate` (`mappers/core.py`) declares `_SETTABLE_ATTRIBUTES: ClassVar[Optional[set]] = None` and a `set_attribute` that enforces it only when not `None`.
2. `AppSessionAggregate`, `CliArgumentAggregate`, `CliCommandAggregate` each declare `_SETTABLE_ATTRIBUTES` with their respective field sets and define no `set_attribute` method of their own (i.e. `'set_attribute' not in vars(AppSessionAggregate)` and likewise for the other two).
3. `ErrorAggregate`, `ServiceRegistrationAggregate`, `FeatureAggregate` are unmodified and continue to accept any valid field via `set_attribute`.
4. `EventFeatureStepAggregate.set_attribute`'s fallthrough (`super().set_attribute(...)` for attributes other than `parameters`/`pass_on_error`) continues to accept any valid field — e.g. setting `service_id`, `flags`, `data_key`, `is_async`, `condition`, or `middleware` via `set_attribute` succeeds with no `ATTRIBUTE_NOT_SETTABLE` error.
5. Calling `set_attribute` with an attribute not in the declared allow-list on any of the three consolidated aggregates raises `ModelError` with `error_code == ATTRIBUTE_NOT_SETTABLE_ID`, the same message format, and the same `model`/`attribute`/`supported` kwargs as before.
6. `pytest tests/mappers/test_app.py tests/mappers/test_cli.py tests/mappers/test_feature.py tests/mappers/test_error.py tests/mappers/test_di.py` passes with zero modifications to those test files.
7. `tiferet/mappers/app.py` and `tiferet/mappers/cli.py` import neither `ATTRIBUTE_NOT_SETTABLE_ID` nor `ModelError`.
8. The full suite passes: `pytest tests/ tiferet/tests_int/`.

## 6. Non-Functional Requirements

- Zero behavior change for any existing aggregate or caller; this is a pure internal consolidation.
- Structured code style (`# ***` / `# **` / `# *`, RST docstrings, snippet comments) per `tiferet-code-style` and `tiferet-code-mappers`.
- Commit is functional-only (no docs/config changes required).

## 7. Prerequisites

| Dependency | Status in `main` |
|------------|-------------------|
| `Aggregate.set_attribute` base implementation (`mappers/core.py:28`) | Present |
| `TransferObject._ROLES` declarative ClassVar precedent (`mappers/core.py:97`) | Present |
| `AggregateTestBase.test_set_attribute` behavior-only harness (`tiferet/testing/mappers.py:180`) | Present |

**Defect statement.** Three `Aggregate` subclasses re-implement an identical attribute-allow-list guard rather than sharing one mechanism, despite the base class already establishing the declarative-ClassVar idiom (`_ROLES`) this fix mirrors.

**Why prototype was not consulted.** This is a mechanical DRY consolidation of code already on trunk, established by reading the current trunk source; it introduces no new domain concept and no freeze applies.

## 8. Related Code Style Documentation

- `tiferet-code-style` — always.
- `tiferet-code-mappers` — the `Aggregate`/`_ROLES`-style ClassVar convention this TRD extends.
- `tiferet-code-testing` — `AggregateTestBase.set_attribute_params` harness this TRD must not require changes to.
