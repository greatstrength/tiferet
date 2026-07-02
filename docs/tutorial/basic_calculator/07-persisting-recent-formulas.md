# Step 7: Persisting Recent Formulas with the File Loader

Our calculator works great — but the moment it finishes, every calculation vanishes.
Let's give it a little memory by saving the **most recently executed formulas** to a file.

This is the perfect excuse to meet one of Tiferet's handy infrastructure helpers: the **file loader**.

### 7.1 Why a file loader?

Tiferet ships small, reusable utilities for reading and writing files. They all build on a base `FileLoader` that manages the open/close lifecycle for you, plus format-specific loaders on top:

- `File` / `FileLoader` — raw stream handling
- `Json` / `JsonLoader` — read/write JSON (what we'll use here)
- `Yaml`, `Csv`, `Sqlite`, … — more of the same idea

Because `Json` builds on `FileLoader`, we get safe, structured reads and writes in one line — no manual `open()`/`close()` juggling.

### 7.2 Add the history events

We'll add two domain events: one to **record** a calculation, one to **list** recent calculations. They use `Json` directly and inject no service, so they simply extend `DomainEvent`.

**app/events/history.py**

```python
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tiferet.events import *
from tiferet import Json


class RecordCalculation(DomainEvent):
    """Append the most recent calculation to a JSON history file."""

    def execute(self, result: Any, operator: str, a: Any = None, b: Any = None,
                history_file: str = 'history.json', max_entries: int = 10, **kwargs) -> Any:
        # Build a friendly expression string.
        expression = f'{operator}{a}' if b is None else f'{a} {operator} {b}'

        # Read existing entries (if any), append, and trim to the most recent.
        entries = Json(history_file).load() if Path(history_file).exists() else []
        entries.append(dict(
            expression=expression, a=a, b=b, operator=operator,
            result=result, timestamp=datetime.now(timezone.utc).isoformat(),
        ))
        entries = entries[-max_entries:]

        # Persist via the file loader and return the result unchanged.
        Json(history_file, mode='w').save(entries)
        return result


class ListRecentFormulas(DomainEvent):
    """Render the most recently executed calculations as a friendly string."""

    def execute(self, history_file: str = 'history.json', limit: int | None = None, **kwargs) -> str:
        if not Path(history_file).exists():
            return 'No recent calculations yet.'
        entries = Json(history_file).load()
        if limit:
            entries = entries[-limit:]
        if not entries:
            return 'No recent calculations yet.'
        return '\n'.join(f"{e['expression']} = {e['result']}" for e in entries)
```

Notice `RecordCalculation` **returns `result` unchanged** — that's important, and we'll see why in a second.

### 7.3 Wire it up in config.yml

First, register the two events under `services`:

```yaml
services:
  # ... existing calc events ...
  record_calculation_event:
    module_path: app.events.history
    class_name: RecordCalculation
  list_recent_formulas_event:
    module_path: app.events.history
    class_name: ListRecentFormulas
```

Now the fun part. We turn each arithmetic feature into a **two-step workflow**: compute, then record. The trick is `data_key`:

```yaml
features:
  calc:
    add:
      name: Add Number
      description: Adds one number to another
      params_schema:
        a: int
        b: int
      steps:
        - service_id: add_number_event
          name: Add `a` and `b`
          data_key: result          # store this step's result in request data
        - service_id: record_calculation_event
          name: Record the calculation
          params:
            operator: '+'           # a literal passed to the record step
```

How it flows:

- The compute step stores its result under `data_key: result`, so it lands in the request data instead of becoming the final response.
- The record step has **no** `data_key`, so *its* return value becomes what `app.run(...)` gives back. Since `RecordCalculation` returns `result` unchanged, the feature still returns the number — we just persisted a history entry along the way.
- The record step reads `a`, `b`, and `result` straight from the request data; `operator` is a literal step param.

Add the same compute-then-record pair to `subtract`, `multiply`, `divide`, `exp`, and `sqrt` (use operators `-`, `*`, `/`, `**`, and `√`).

Finally, add a feature to read the history back:

```yaml
    history:
      name: Recent Calculations
      description: Lists the most recently executed calculations
      steps:
        - service_id: list_recent_formulas_event
          name: List recent calculations
```

> **Tip:** `params_schema` (added in v2.0.0b12) validates and coerces request data before any step runs — that's why `a` and `b` arrive as real numbers.

### 7.4 Add a CLI command (optional)

```yaml
cli:
  cmds:
    calc:
      # ... existing commands ...
      history:
        group_key: calc
        key: history
        name: Recent Calculations Command
        description: Lists the most recently executed calculations.
```

### 7.5 See it work

```bash
python basic_calc.py
```

After the arithmetic output, you'll see:

```
Recent calculations:
1 + 2 = 3
5 - 3 = 2
4 * 3 = 12
8 / 2.0 = 4.0
2 ** 3 = 8
√16 = 4.0
```

And a `history.json` file appears next to your script. From the CLI:

```bash
python calc_cli.py calc history
```

### 7.6 Why this is nice

- Persistence with zero boilerplate — the file loader handles the file lifecycle.
- The compute-then-record pattern shows how `data_key` lets steps share data without changing the feature's return value.
- Failed calculations (like divide-by-zero) raise before the record step, so they never pollute the history.

→ Next, let's go from remembering calculations to **saving reusable, variablized formulas** with domain models and a repository.
Head to **[Step 8: Saving & Variablizing Formulas](08-saving-and-variablizing-formulas.md)**
