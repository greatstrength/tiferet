# Basic Calculator Example

A complete calculator application built with the [Tiferet](https://github.com/greatstrength/tiferet) framework, demonstrating Domain-Driven Design with domain events, feature workflows, and configuration-driven architecture.

## Prerequisites

- Python 3.10+
- Tiferet (`pip install tiferet`)

## Project Structure

```
basic_calculator/
├── basic_calc.py          # App blueprint entry point
├── calc_cli.py            # CLI blueprint entry point
├── calc_fluent.py         # Fluent calculator context entry point
├── config.yml             # Consolidated application configuration
├── formulas.yml           # Saved formulas store
└── app/
    ├── assets/            # Operator constants, precedence table, cache prefix
    │   └── calc.py
    ├── domain/            # Formula + Expression domain models
    │   ├── formula.py
    │   └── expression.py
    ├── events/
    │   ├── settings.py    # BasicCalcEvent (numeric validation)
    │   ├── calc.py        # Arithmetic domain events
    │   ├── history.py     # Recent-calculation events
    │   └── formula.py     # Formula domain events
    ├── interfaces/        # FormulaService contract
    │   └── formula.py
    ├── mappers/           # Formula aggregate + config object
    │   └── formula.py
    ├── repos/             # FormulaConfigRepository
    │   └── formula.py
    ├── contexts/          # ExpressionContext + CalculatorAppContext
    │   ├── expression.py
    │   └── calc.py
    └── blueprints/        # create_calculator_app
        └── calc.py
```

`history.json` is created automatically at runtime to store the most recent calculations.

## Running the Application

### App Entry Point

Run the demonstration script from this directory:

```bash
python basic_calc.py
```

Expected output:

```
1 + 2 = 3.0
5 - 3 = 2.0
4 * 3 = 12.0
8 / 2 = 4.0
Error: Cannot divide by zero
2 ** 3 = 8
√16 = 4.0
```

### CLI Entry Point

Run individual operations via the command line:

```bash
# Addition
python calc_cli.py calc add 1 2

# Subtraction
python calc_cli.py calc subtract 5 3

# Multiplication
python calc_cli.py calc multiply 4 3

# Division
python calc_cli.py calc divide 8 2

# Exponentiation
python calc_cli.py calc exp 2 3

# Square root
python calc_cli.py calc sqrt 4

# Recent calculations
python calc_cli.py calc history

# Save, list, and evaluate a variablized formula
python calc_cli.py formula save "Rectangle Area" "width * height"
python calc_cli.py formula list
python calc_cli.py formula eval rectangle_area '{"width": 3, "height": 4}'
```

### Fluent Calculator Entry Point

Run a chainable, PEMDAS-aware calculator client from this directory:

```bash
python calc_fluent.py
```

Expected output:

```
1 + 3 - 5 * 2 = -6.0
2 + 3 * 4 - 1 = 13.0
3 * 4 + 5 / 2 = 14.5

Recent calculations:
1.0 + 3.0 = 4.0
5.0 * 2.0 = 10.0
4.0 - 10.0 = -6.0
3.0 * 4.0 = 12.0
2.0 + 12.0 = 14.0
14.0 - 1.0 = 13.0
3.0 * 4.0 = 12.0
5.0 / 2.0 = 2.5
12.0 + 2.5 = 14.5
```

See [Step 9 of the tutorial](https://github.com/greatstrength/tiferet/blob/main/docs/tutorial/basic_calculator/09-fluent-calculator-context.md) for how `create_calculator_app()`, `CalculatorAppContext`, and the PEMDAS scheduling algorithm work.

## Features

- **Addition** (`calc.add`) — Adds two numbers
- **Subtraction** (`calc.subtract`) — Subtracts one number from another
- **Multiplication** (`calc.multiply`) — Multiplies two numbers
- **Division** (`calc.divide`) — Divides two numbers with zero-check
- **Exponentiation** (`calc.exp`) — Raises a number to a power
- **Square Root** (`calc.sqrt`) — Calculates square root (reuses exponentiation with `b=0.5`)
- **Recent Calculations** (`calc.history`) — Lists the most recently executed calculations, persisted to `history.json` via the file loader
- **Save Formula** (`formula.save`) — Saves a named, variablized formula to `formulas.yml`
- **Get Formula** (`formula.get`) — Retrieves a saved formula by id
- **List Formulas** (`formula.list`) — Lists all saved formulas
- **Evaluate Formula** (`formula.eval`) — Evaluates a saved formula with concrete variable values
- **Fluent Calculator** (`create_calculator_app()`) — A chainable `CalculatorAppContext` exposing `add`/`add_to`, `subtract`/`subtract_from`, `multiply`/`multiply_by`, and `divide`/`divide_by`, plus `.result`, `.pending`, and `.reset()`. Evaluates chained operations with standard operator precedence (PEMDAS), dispatching every reduction through the existing `calc.*` features so validation and history recording keep working unchanged.

## Tutorial

For a step-by-step guide to building this application, see the [Tiferet tutorial documentation](https://github.com/greatstrength/tiferet#getting-started).
