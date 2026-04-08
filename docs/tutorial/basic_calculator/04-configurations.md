# Step 4: Configurations

We've got the math events and a nice validation utility — now it's time to make everything come alive through configuration.  
In Tiferet v2.0, everything is consolidated into a single root `config.yml` file. This one file defines interfaces, dependency mappings, features, and errors.

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
attrs:
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
        - attribute_id: add_event

    subtract:
      name: Subtraction
      description: Subtract second number from first
      steps:
        - attribute_id: subtract_event

    multiply:
      name: Multiplication
      description: Multiply two numbers
      steps:
        - attribute_id: multiply_event

    divide:
      name: Division
      description: Divide first number by second
      steps:
        - attribute_id: divide_event

    exp:
      name: Exponentiation
      description: Raise first number to the power of second
      steps:
        - attribute_id: exp_event

    sqrt:
      name: Square Root
      description: Calculates the square root of a number
      steps:
        - attribute_id: exp_event
          params:
            b: 0.5    # fixed exponent for square root (a^(1/2))

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
- Tiferet automatically loads `config.yml` from the project root when you create `App()`.

### 4.3 Quick recap

In this single `config.yml` file we defined:

- **Interfaces** (`basic_calc`) — the entry point for our script runner
- **Dependency mappings** (`attrs`) — links friendly names like `add_event` to the actual Python classes in `app/events/calc.py`
- **Features** (`calc.add`, `calc.sqrt`, etc.) — defines the workflows and which event to run for each operation
- **Errors** — user-friendly, structured error messages with support for multiple languages

When you run `app = App()`, Tiferet reads this `config.yml` and wires everything together automatically.

No code changes needed here — just this one YAML file.

→ Ready to see it all run?  
Head to **[Step 5: Running the Script Runner](05-running-the-script.md)**
