# Step 8: Saving & Variablizing Formulas

Recording recent calculations was fun — but what if we want to save a **reusable, named formula** like `width * height` and evaluate it later with different values?

That's a real domain concept, so this time we'll use the full Tiferet stack: a **domain model**, a **mapper**, a **service interface**, a **repository**, and a few **domain events**. We'll persist everything to a `formulas.yml` file.

This chapter mirrors how the framework's own domains (errors, features, …) are built, so it's a great template for your own data.

### 8.1 The domain model

A `Formula` has a name, an expression, and the variables it depends on. We derive the `id` from the name and infer the variables from the expression, so callers only have to supply the essentials.

**app/domain/formula.py**

```python
import re
from typing import Any, List

from pydantic import Field, model_validator
from tiferet import DomainObject

class Formula(DomainObject):
    """A saved, variablized calculator formula (e.g. width * height)."""

    id: str = Field(..., description='The unique identifier of the formula.')
    name: str = Field(..., description='The human-readable name of the formula.')
    expression: str = Field(..., description='The arithmetic expression using named variables.')
    variables: List[str] = Field(default_factory=list, description='The named variables the expression depends on.')
    description: str | None = Field(default=None, description='An optional description of the formula.')

    @model_validator(mode='before')
    @classmethod
    def _derive_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        data = dict(data)

        # Derive a snake_case id from the name.
        if not data.get('id') and data.get('name'):
            data['id'] = str(data['name']).strip().lower().replace(' ', '_')

        # Infer the variables from the expression identifiers.
        if not data.get('variables') and data.get('expression'):
            identifiers = re.findall(r'[A-Za-z_][A-Za-z0-9_]*', str(data['expression']))
            data['variables'] = list(dict.fromkeys(identifiers))

        return data

    # Read-only presentation: a friendly one-liner, also used as __str__.
    def display(self) -> str:
        summary = f'{self.name}: {self.expression}'
        if self.variables:
            summary += f" (variables: {', '.join(self.variables)})"
        return summary

    def __str__(self) -> str:
        return self.display()
```

### 8.2 The mappers

Domain objects are read-only. Mutation lives in an **Aggregate**, and serialization lives in a **ConfigObject**.

**app/mappers/formula.py**

```python
import re
from typing import Any, ClassVar, Dict

from tiferet.mappers import Aggregate, TransferObject
from ..domain.formula import Formula

class FormulaAggregate(Formula, Aggregate):
    """A mutable formula aggregate."""

    def rename(self, new_name: str) -> None:
        self.name = new_name

    def set_expression(self, expression: str) -> None:
        self.expression = expression
        identifiers = re.findall(r'[A-Za-z_][A-Za-z0-9_]*', expression)
        self.variables = list(dict.fromkeys(identifiers))

class FormulaConfigObject(Formula, TransferObject):
    """A configuration (YAML/JSON) representation of a formula."""

    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {'by_alias': True, 'exclude': {'id'}},   # id is the mapping key
    }

    def map(self, **overrides) -> FormulaAggregate:
        return super().map(FormulaAggregate, **overrides)
```

### 8.3 The service interface

The contract our events depend on — five familiar operations:

**app/interfaces/formula.py**

```python
from abc import abstractmethod
from typing import List

from tiferet.interfaces import Service
from ..mappers.formula import FormulaAggregate

class FormulaService(Service):
    """Service interface for managing saved formulas."""

    @abstractmethod
    def exists(self, id: str) -> bool: ...

    @abstractmethod
    def get(self, id: str) -> FormulaAggregate | None: ...

    @abstractmethod
    def list(self) -> List[FormulaAggregate]: ...

    @abstractmethod
    def save(self, formula: FormulaAggregate) -> None: ...

    @abstractmethod
    def delete(self, id: str) -> None: ...
```

### 8.4 The repository

`ConfigurationRepository` gives us format-agnostic load/save. We store formulas under a `formulas` root node and tolerate a missing file so the example just works the first time.

**app/repos/formula.py** (the essentials)

```python
from pathlib import Path
from typing import List

from tiferet.repos.core import ConfigurationRepository
from ..interfaces.formula import FormulaService
from ..mappers.formula import FormulaAggregate, FormulaConfigObject

class FormulaConfigRepository(FormulaService, ConfigurationRepository):
    """Persists formulas under the `formulas` node of a config file."""

    def __init__(self, formula_config: str, encoding: str = 'utf-8') -> None:
        ConfigurationRepository.__init__(self, config_file=formula_config, encoding=encoding)

    def _load_full(self) -> dict:
        if not Path(self.config_file).exists():
            return {}
        return self._load() or {}

    def _load_formulas(self) -> dict:
        return (self._load_full().get('formulas') or {})

    def get(self, id: str) -> FormulaAggregate | None:
        data = self._load_formulas().get(id)
        if not data:
            return None
        return FormulaConfigObject.model_validate({**data, 'id': id}).map()

    def save(self, formula: FormulaAggregate) -> None:
        full = self._load_full()
        full.setdefault('formulas', {})[formula.id] = \
            FormulaConfigObject.from_model(formula).to_primitive(self.default_role)
        self._save(data=full)

    # exists / list / delete follow the same pattern.
```

Seed an empty store so the file exists from the start:

**formulas.yml**

```yaml
formulas: {}
```

### 8.5 The events

Each single-service event module defines a small **base event** that holds the shared service. Concrete events extend it and define only `execute`.

**app/events/formula.py** (highlights)

```python
import json
from typing import Any, Dict, List

from tiferet.events import DomainEvent
from ..interfaces.formula import FormulaService
from ..mappers.formula import FormulaAggregate

class FormulaEvent(DomainEvent):
    """Base event holding the shared FormulaService."""

    def __init__(self, formula_service: FormulaService):
        self.formula_service = formula_service

class SaveFormula(FormulaEvent):
    @DomainEvent.parameters_required(['name', 'expression'])
    def execute(self, name, expression, description=None, **kwargs) -> FormulaAggregate:
        formula = FormulaAggregate(name=name, expression=expression, description=description)
        self.formula_service.save(formula)   # save is an upsert
        return formula

class EvaluateFormula(FormulaEvent):
    @DomainEvent.parameters_required(['id'])
    def execute(self, id, values=None, **kwargs) -> int | float:
        formula = self.formula_service.get(id)
        self.verify(formula is not None, 'FORMULA_NOT_FOUND', f'Formula not found: {id}', id=id)

        if isinstance(values, str):
            values = json.loads(values)          # CLI passes JSON text
        provided: Dict[str, Any] = dict(values or {})

        resolved: Dict[str, Any] = {}
        for variable in formula.variables:
            self.verify(variable in provided, 'MISSING_VARIABLE',
                        f'Missing value for variable: {variable}', variable=variable)
            resolved[variable] = self.coerce_number(provided[variable])

        # Evaluate with no builtins exposed — only the formula's variables.
        return eval(formula.expression, {'__builtins__': {}}, resolved)
```

`GetFormula` returns the formula entity (which prints nicely thanks to `__str__`). `ListFormulas` is a **view** — it renders the saved formulas into a friendly string (`'\n'.join(f.display() for f in …)`) so the CLI prints clean lines instead of raw objects. `coerce_number` lives on the base event and turns inputs into ints/floats, raising `INVALID_INPUT` on junk.

> **Heads up on `eval`:** this is tutorial-grade. We lock it down by exposing no builtins and only the formula's own variables. For untrusted input in production, prefer a real expression parser.

### 8.6 Wire it all up in config.yml

Register the repository (with its file path as a parameter) and the events under `services`:

```yaml
services:
  # ... existing events ...
  formula_service:
    module_path: app.repos.formula
    class_name: FormulaConfigRepository
    params:
      formula_config: formulas.yml
  save_formula_event:
    module_path: app.events.formula
    class_name: SaveFormula
  get_formula_event:
    module_path: app.events.formula
    class_name: GetFormula
  list_formulas_event:
    module_path: app.events.formula
    class_name: ListFormulas
  evaluate_formula_event:
    module_path: app.events.formula
    class_name: EvaluateFormula
```

The `params` block becomes a DI constant, so `formula_config` is injected straight into the repository's constructor.

Now the features. Note `steps:` (Tiferet accepts `steps` for the workflow list) and `params_schema` for validation:

```yaml
features:
  formula:
    save:
      name: Save Formula
      description: Saves a named, variablized formula
      params_schema:
        name: str
        expression: str
        description:
          type: str
          required: false
      steps:
        - service_id: save_formula_event
          name: Save the formula
    list:
      name: List Formulas
      description: Lists all saved formulas
      steps:
        - service_id: list_formulas_event
          name: List the formulas
    eval:
      name: Evaluate Formula
      description: Evaluates a saved formula with variable values
      params_schema:
        id: str
      steps:
        - service_id: evaluate_formula_event
          name: Evaluate the formula
```

(Add a `get` feature the same way, with `params_schema: {id: str}`.)

Add the error messages our events raise:

```yaml
errors:
  FORMULA_NOT_FOUND:
    name: Formula Not Found
    message:
      - lang: en_US
        text: 'Formula not found: {id}'
  MISSING_VARIABLE:
    name: Missing Variable
    message:
      - lang: en_US
        text: 'Missing value for variable: {variable}'
  FORMULA_EVALUATION_FAILED:
    name: Formula Evaluation Failed
    message:
      - lang: en_US
        text: 'Could not evaluate formula {id}: {error}'
```

And, optionally, CLI commands under `cli.cmds` (the `eval` command takes the values as a JSON string):

```yaml
      eval:
        group_key: formula
        key: eval
        name: Evaluate Formula Command
        description: Evaluates a saved formula with variable values.
        args:
          - name_or_flags:
              - id
            description: The formula identifier.
          - name_or_flags:
              - values
            description: A JSON object mapping variable names to values.
```

### 8.7 See it work

From the script:

```
Formulas:
Saved Rectangle Area: width * height (variables: width, height)
Rectangle Area: width * height (variables: width, height)
rectangle_area(width=3, height=4) = 12
```

From the CLI:

```bash
python calc_cli.py formula save "Rectangle Area" "width * height"
python calc_cli.py formula list
python calc_cli.py formula eval rectangle_area '{"width": 3, "height": 4}'
# → 12
```

### 8.8 Recap

- A **domain model** (`Formula`) captures the concept; an **aggregate** handles mutation; a **config object** handles serialization.
- A **service interface** + **repository** persist formulas to `formulas.yml` with the same pattern the framework uses internally.
- **Events** orchestrate the domain logic, and `params_schema` validates input before they run.

You've now seen both styles of persistence in Tiferet: lightweight file-loader storage (Step 7) and a full domain-model repository (Step 8). From here, try adding `formula delete`, richer expressions, or a SQLite-backed repository.

→ Back to the **[tutorial index](index.md)**.
