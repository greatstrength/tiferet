# Step 4: Configurations

We've got the math events and a nice validation utility — now it's time to make everything come alive through configuration.  
In Tiferet, YAML files are the "wiring diagram": they tell the framework what events exist, how features map to them, and what errors look like.

We'll go through each file one by one, explaining what it does and why each piece matters.

### 4.1 app/configs/app.yml – Application interfaces

This file defines the "entry points" or interfaces your app exposes. For now we'll just set up the basic script interface — we'll add the CLI interface in Step 6.

**app/configs/app.yml**

```yaml
interfaces:
  basic_calc:
    name: Basic Calculator
    description: Simple arithmetic operations via script or direct call
```

- `basic_calc`: our simple script interface (uses default Tiferet behavior — no custom context needed)

### 4.2 app/configs/container.yml – Dependency injection

This maps event names to actual Python classes so Tiferet can instantiate them when needed.

**app/configs/container.yml**

```yaml
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
```

These are the "service names" our features will reference later.

### 4.3 app/configs/feature.yml – Workflow orchestration

This defines the actual calculator features and which event(s) they run.

**app/configs/feature.yml**

```yaml
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
```

- Each sub-key under `calc` is a feature ID (e.g., `calc.add`)
- `commands` lists the events to run (we only need one per feature here)
- `attribute_id` matches the names we defined in `container.yml`

### 4.4 app/configs/error.yml – Structured error messages

This defines user-friendly, multilingual error messages.

**app/configs/error.yml**

```yaml
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

- Keys match the `error_code` strings we use in `RaiseError.execute(...)` and `CalcUtil`
- Supports multiple languages (we'll stick to `en_US` for now)
- `{value}` is a placeholder filled from the keyword arguments passed to `RaiseError`

### 4.5 Quick recap

- `app.yml`: defines interfaces (script for now, CLI in Step 6)
- `container.yml`: maps Python classes to injectable names
- `feature.yml`: defines workflows (feature → event)
- `error.yml`: provides nice error messages

All these files work together so Tiferet knows:  
"When someone runs `calc.add`, instantiate `AddNumber` from `app.events.calc`, run it, and format any errors nicely."

No code changes needed here — just YAML.

→ Ready to see it all run?  
Head to **[Step 5: Running the Script Runner](05-running-the-script.md)**
