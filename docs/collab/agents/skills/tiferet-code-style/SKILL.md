---
name: tiferet-code-style
description: Apply the Tiferet structured code style during any implementation session in a Tiferet-family repo. Read this at the start of every implementation session before touching any source file — it covers artifact comment hierarchy, spacing rules, docstrings, annotation artifacts, and the domain event test harness style.
---

# Structured Code Style – Tiferet

## When to use
- **Always** — read this at the start of every implementation session in a Tiferet-family repo.
- Before writing or editing any module: domain objects, events, mappers, interfaces, repos, contexts, utils, blueprints, assets, or tests.
- When unsure of comment label syntax, spacing rules, or docstring format.
- Component-specific skills (`tiferet-code-domain`, `tiferet-code-events`, etc.) add detail on top of this foundation.

## Artifact comment structure

Three structural tiers organize every module:

```
# *** <section>          ← top-level (preamble or construct group)
# ** <kind>: <name>      ← mid-level (category or individual component)
# * <component>          ← low-level (attribute, init, method)
```

**Top-level sections — preamble groups** (available in any module, in this order when present):
- `# *** imports` — all imports
- `# *** constants` — module-level constants
- `# *** functions` — side-effect-free module-level helpers (no `self`, no injected services, plain return values)
- `# *** classes` — generic/base classes not tied to a construct type (used in `settings.py` files)

**Top-level sections — construct groups** (one per module, based on what it defines):
- `# *** models`, `# *** events`, `# *** contexts`, `# *** interfaces`, `# *** mappers`, `# *** repos`, `# *** utils`, `# *** blueprints`
- `# *** exports` — only in `__init__.py`

**Sub-groups** — partition a large section with a parenthetical qualifier (kind preserved):
```python
# *** constants
# ** constant: en_us
EN_US = 'en_US'

# *** constants (error)
# ** constant: feature_not_found_id
FEATURE_NOT_FOUND_ID = 'FEATURE_NOT_FOUND'
```

**Mid-level labels by import group:** `# ** core`, `# ** infra`, `# ** app`

**Mid-level labels by construct:** `# ** model: <name>`, `# ** event: <name>`, `# ** context: <name>`, `# ** mapper: <name>`, `# ** interface: <name>`, `# ** repo: <name>`, `# ** util: <name>`, `# ** blueprint: <name>`, `# ** function: <name>`, `# ** constant: <name>`, `# ** class: <name>`

**Low-level labels within a class:**
- `# * attribute: <name>` — instance attributes
- `# * init` — constructor
- `# * method: <name>` — instance methods
- `# * method: <name> (static)` — static methods
- `# * method: <name> (validator)` — `@model_validator` methods on domain objects

## Key conventions

- **Spacing:** One empty line between top-level comment and first mid-level; one empty line between mid-level entries; one empty line between low-level (`# *`) sections; one empty line after docstrings; one empty line between code snippets within a method.
- **Docstrings:** RST format — include `:param`/`:type` for every parameter and `:return`/`:rtype` for every return value.
- **Parameter indentation:** For methods with >3 parameters, align subsequent params to the opening parenthesis.
- **Code snippets:** Each logical step is a separate snippet preceded by a 1–2 line comment describing intent.
- **Annotation artifacts** (transient lifecycle markers, placed immediately after the `# *` label they annotate):
  - `# ++ todo: <message>` — deferred work; remove when done.
  - `# -- obsolete: <reason>` — deprecated artifact; remove with the artifact. Shorthand: `# * method: foo (obsolete)`.
- **Pre-session scan:** Before editing, run `grep -rn "# ++\|# --" tiferet/` to find open annotations.

## Example

```python
# *** imports

# ** core
from typing import Any

# ** app
from .settings import DomainEvent, a
from ..domain import Feature
from ..interfaces import FeatureService

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

        :param feature_service: The feature service.
        :type feature_service: FeatureService
        '''

        # Set the feature service dependency.
        self.feature_service = feature_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> Feature:
        '''
        Retrieve a feature by ID.

        :param id: The feature ID.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The Feature domain object.
        :rtype: Feature
        '''

        # Retrieve the feature from the service.
        feature = self.feature_service.get(id)

        # Verify the feature exists; raise structured error if not.
        self.verify(
            expression=feature is not None,
            error_code=a.const.FEATURE_NOT_FOUND_ID,
            feature_id=id,
        )

        # Return the feature.
        return feature
```

## Canonical source
https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md
