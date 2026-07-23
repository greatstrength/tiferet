# Step 4: Configurations

We've got the math events and a nice validation utility — now it's time to make everything come alive through configuration.  
In Tiferet v2, everything is consolidated into a single root `config.yml` file. This one file defines interfaces, dependency mappings, features, and errors.

### 4.1 config.yml – The complete wiring diagram

Create `config.yml` in your project root (next to `basic_calc.py` and `calc_cli.py`).

**config.yml**

```yaml
# Application interfaces
interfaces:
  basic_calc:
    name: Basic Calculator
    description: Simple arithmetic operations via script or direct call

# Dependency injection mappings
# These map friendly names (used in features) to actual Python classes
services:
  add_event:
    module_path: app.events.calc
    class_name: AddNumber
  subtract_event:
    module_path: app.events.calc
    class_name: SubtractNumber
  multiply_event:
    module_path: app.events.calc
    class_name: MultiplyNumber
  divide_event:
    module_path: app.events.calc
    class_name: DivideNumber
  exp_event:
    module_path: app.events.calc
    class_name: ExponentiateNumber

# Feature workflows
features:
  calc:
    add:
      name: Addition
      description: Add two numbers
      steps:
        - service_id: add_event

    subtract:
      name: Subtraction
      description: Subtract second number from first
      steps:
        - service_id: subtract_event

    multiply:
      name: Multiplication
      description: Multiply two numbers
      steps:
        - service_id: multiply_event

    divide:
      name: Division
      description: Divide first number by second
      steps:
        - service_id: divide_event

    exp:
      name: Exponentiation
      description: Raise first number to the power of second
      steps:
        - service_id: exp_event

    sqrt:
      name: Square Root
      description: Calculates the square root of a number
      steps:
        - service_id: exp_event
          params:
            b: 0.5    # fixed exponent for square root (a^(1/2))

    safe_divide:
      name: Safe Divide
      description: Divides only when denominator is non-zero
      steps:
        - service_id: divide_event
          condition: '$r.b != 0'    # skip when b is zero instead of raising

# Structured error messages
errors:
  INVALID_INPUT:
    name: Invalid Input
    message:
      - lang: en_US
        text: "Invalid number: {value}"

  DIVISION_BY_ZERO:
    name: Division by Zero
    message:
      - lang: en_US
        text: "Cannot divide by zero"
```

### 4.2 Why a single config.yml?

- **Simpler structure** — No more hunting through multiple files.
- **Easier to manage** — Everything related to how the app behaves is in one place.
- **Still fully flexible** — You can define multiple interfaces, complex features, and rich error handling.
- Pass `app_config='config.yml'` when calling `App('basic_calc', app_config='config.yml')`.

### 4.3 Conditional steps

Notice `calc.safe_divide` — it uses a `condition` on the step. The expression `$r.b != 0` is evaluated against the request data at runtime. If `b` is zero, the step is silently skipped instead of raising a division-by-zero error. This enables declarative, configuration-driven conditional branching without writing custom flow-control events.

Conditions support `$r.<key>` references for any value in the request data and simple boolean comparisons (e.g., `$r.mode == 'advanced'`, `$r.x > 0`). When `condition` is omitted, the step always executes.

### 4.4 Quick recap

In this single `config.yml` file we defined:

- **Interfaces** (`basic_calc`) — the entry point for our script runner
- **Services** (`services`) — links friendly names like `add_event` to the actual Python classes in `app/events/calc.py`
- **Features** (`calc.add`, `calc.sqrt`, `calc.safe_divide`, etc.) — defines the workflows and which event to run for each operation
- **Conditional steps** — declarative `condition` expressions on feature steps for runtime branching
- **Errors** — user-friendly, structured error messages with support for multiple languages

When you run `app = App('basic_calc', app_config='config.yml')`, Tiferet reads this file and wires everything together automatically.

No code changes needed here — just this one YAML file.

→ Ready to see it all run?  
Head to **[Step 5: Running the Script Runner](05-running-the-script.md)**
