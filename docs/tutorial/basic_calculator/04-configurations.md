# Step 4: Configurations

We've got the math events and a nice validation utility — now it's time to make everything come alive through configuration.  
In Tiferet v2.0, everything is consolidated into a single root `config.yml` file. This one file defines interfaces, dependency mappings, features, and errors.

### 4.1 config.yml – The complete wiring diagram

Create `config.yml` in your project root (next to `basic_calc.py` and `calc_cli.py`).

**config.yml**

```yaml
interfaces:
  basic_calc:
    name: Basic Calculator
    description: Simple arithmetic operations via script or direct call

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
    class_name: Exponentiate

features:
  calc:
    add:
      name: Addition
      description: Add two numbers
      commands:
        - attribute_id: add_event

    subtract:
      name: Subtraction
      description: Subtract second number from first
      commands:
        - attribute_id: subtract_event

    multiply:
      name: Multiplication
      description: Multiply two numbers
      commands:
        - attribute_id: multiply_event

    divide:
      name: Division
      description: Divide first number by second
      commands:
        - attribute_id: divide_event

    exp:
      name: Exponentiation
      description: Raise first number to the power of second
      commands:
        - attribute_id: exp_event

    sqrt:
      name: Square Root
      description: Calculates the square root of a number
      commands:
        - attribute_id: exp_event
          params:
            b: 0.5    # fixed exponent for square root (a^(1/2))

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

### 4.2 How to read this file

- `interfaces` defines the app entry points (`basic_calc` now, `calc_cli` in Step 6)
- `attrs` maps friendly names to domain event classes
- `features` defines workflows (for example, `calc.add` → `add_event`)
- `errors` defines structured response messages

This gives Tiferet everything it needs to execute features and format errors from one configuration source.

### 4.3 Quick recap

All configuration now lives in root `config.yml`:

- Interface definition
- Domain event dependency mapping
- Feature workflow wiring
- Error message definitions

No code changes needed here — just YAML in one place.

→ Ready to see it all run?  
Head to **[Step 5: Running the Script Runner](05-running-the-script.md)**
