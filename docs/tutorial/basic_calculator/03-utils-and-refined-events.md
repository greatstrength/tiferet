# Step 3: Utilities & Refined Events

Now that our events can do the math, let's make them a lot safer and cleaner.  
Right now they blindly trust whatever numbers get passed in — not great for a real calculator.  
We want to validate inputs properly (convert strings to numbers, catch junk input, prevent division by zero, etc.).

Instead of repeating validation code inside every event, we'll create a small **utility** class.  
This is a perfect Tiferet moment: utilities are reusable infrastructure helpers that live outside the domain events, keeping events focused on business logic.

### 3.1 Create the utils package

Add this folder/file:

```
app/
└── utils/
    ├── __init__.py      # empty, just makes utils a package
    └── calc.py          # our calculator-specific helpers
```

**app/utils/__init__.py**  
(leave it empty)

```python
# Empty file to make app.utils a proper Python package
```

### 3.2 Build the CalcUtil

**app/utils/calc.py**

```python
from tiferet.events import RaiseError

class CalcUtil:
    """Reusable calculator utilities – mostly number validation for now."""

    @staticmethod
    def verify_number(value) -> float:
        """
        Convert any reasonable input to float and validate it's a real number.
        Raises a structured Tiferet error if invalid.
        """
        try:
            num = float(value)
        except (ValueError, TypeError):
            RaiseError.execute(
                error_code='INVALID_INPUT',
                value=value,
            )
        return num
```

This is a static method so we can call it easily without instantiating anything.  
It uses Tiferet's built-in `RaiseError` for consistent, structured errors (we'll configure the messages in YAML later).

### 3.3 Update the events to use the utility

Now let's refine our events to call `CalcUtil.verify_number()` instead of trusting raw inputs.

**app/events/calc.py** (updated)

```python
from tiferet.events import DomainEvent, RaiseError
from ..utils.calc import CalcUtil

class AddNumber(DomainEvent):
    """Adds two numbers."""
    def execute(self, a, b, **kwargs) -> float:
        a_val = CalcUtil.verify_number(a)
        b_val = CalcUtil.verify_number(b)
        return a_val + b_val


class SubtractNumber(DomainEvent):
    """Subtracts b from a."""
    def execute(self, a, b, **kwargs) -> float:
        a_val = CalcUtil.verify_number(a)
        b_val = CalcUtil.verify_number(b)
        return a_val - b_val


class MultiplyNumber(DomainEvent):
    """Multiplies two numbers."""
    def execute(self, a, b, **kwargs) -> float:
        a_val = CalcUtil.verify_number(a)
        b_val = CalcUtil.verify_number(b)
        return a_val * b_val


class DivideNumber(DomainEvent):
    """Divides a by b."""
    def execute(self, a, b, **kwargs) -> float:
        a_val = CalcUtil.verify_number(a)
        b_val = CalcUtil.verify_number(b)
        if b_val == 0:
            RaiseError.execute(
                error_code='DIVISION_BY_ZERO',
            )
        return a_val / b_val


class Exponentiate(DomainEvent):
    """Raises a to the power of b (a^b)."""
    def execute(self, a, b, **kwargs) -> float:
        a_val = CalcUtil.verify_number(a)
        b_val = CalcUtil.verify_number(b)
        return a_val ** b_val
```

### 3.4 What changed & why it matters

- Events now safely convert and validate inputs using the shared utility
- Validation logic lives in one place (`CalcUtil`) — easy to update or extend
- We added a zero-division check right in `DivideNumber` (a domain rule!)
- `RaiseError` is imported and used directly for the division-by-zero case
- Still pure domain logic — no config or YAML awareness here

This is classic Tiferet separation:  
- Events = business rules + orchestration  
- Utils = reusable infrastructure helpers

Much cleaner, much safer.  
Now our calculator is ready for real inputs (strings, numbers, etc.) without crashing on bad data.

→ Next: Let's connect everything with configuration magic!  
Head to **[Step 4: Configurations](04-configurations.md)**
