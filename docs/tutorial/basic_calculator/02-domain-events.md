# Step 2: Domain Events – Initial Version

Alright, now that we know what the finished calculator *looks* like when it runs, let's start building the heart of it: the **domain events**.

These are the little pieces that actually do the math. In Tiferet, domain events are super focused — each one handles one clear job, stays pure, and doesn't worry about validation or config stuff (we'll handle that later with utils and YAML).

For this first pass, we're keeping them dead simple: just take inputs and return results. No checks, no errors yet. We'll make them robust in the next step.

### 2.1 Create the events file

Make this folder/file if you haven't already:

```
app/
└── events/
    ├── __init__.py      # ← empty file, just makes this a proper Python package
    └── calc.py
```

### 2.2 Write the basic arithmetic events

**app/events/calc.py**

```python
from tiferet.events import DomainEvent

class AddNumber(DomainEvent):
    """Adds two numbers."""
    def execute(self, a: float, b: float, **kwargs) -> float:
        return a + b


class SubtractNumber(DomainEvent):
    """Subtracts b from a."""
    def execute(self, a: float, b: float, **kwargs) -> float:
        return a - b


class MultiplyNumber(DomainEvent):
    """Multiplies two numbers."""
    def execute(self, a: float, b: float, **kwargs) -> float:
        return a * b


class DivideNumber(DomainEvent):
    """Divides a by b."""
    def execute(self, a: float, b: float, **kwargs) -> float:
        return a / b


class Exponentiate(DomainEvent):
    """Raises a to the power of b (a^b)."""
    def execute(self, a: float, b: float, **kwargs) -> float:
        return a ** b
```

That's it for now!

### 2.3 What we just did

- We created `app/events/` as a proper Python package with an empty `__init__.py`
- Each class is a tiny domain event — one responsibility, one method (`execute`)
- We used `float` for inputs/outputs so everything works nicely with decimals
- No validation or error handling yet (that's coming next)
- No base class or inheritance beyond `DomainEvent` — keeping it as minimal as possible

These events are pure and ready to be wired up later via YAML.

### Quick note on future expansion

When we get to the CLI and script runner, these same events will power everything:
- `calc.add 7 11` → calls `AddNumber`
- `calc.sqrt 16` → calls `Exponentiate` with `b=0.5`
- etc.

For now, they just sit there waiting to be useful.

You've laid the foundation — nice work!  
Next up, we'll add a little helper utility to make these events safer and cleaner.

→ Ready to level them up?  
Head over to **[Step 3: Utilities & Refined Events](03-utils-and-refined-events.md)**
