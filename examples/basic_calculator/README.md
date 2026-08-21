# Basic Calculator Example

A complete calculator application built with the [Tiferet](https://github.com/greatstrength/tiferet) framework, demonstrating Domain-Driven Design with domain events, feature workflows, and configuration-driven architecture.

## Prerequisites

- Python 3.10+
- Tiferet (`pip install tiferet`)

## Project Structure

```
basic_calculator/
├── calc_client.py         # Plain, non-fluent client entry point
├── calc_cli.py            # CLI entry point
├── calc_fluent.py         # Fluent, chainable calculator entry point
├── config.yml             # Consolidated application configuration
├── formulas.yml           # Saved formulas store
└── app/
    ├── assets/            # Operator constants, precedence table, default catalogs
    │   ├── core.py        # Operator/feature/event id constants + CALC_DEFAULT_SERVICES
    │   ├── feature.py     # CALC_DEFAULT_FEATURES (calc.add/.../resolve)
    │   └── error.py       # CALC_DEFAULT_ERRORS
    ├── domain/            # Formula + Expression domain models
    │   ├── formula.py
    │   └── expression.py  # Expression.resolve (PEMDAS scheduling)
    ├── events/
    │   ├── settings.py    # BasicCalcEvent (numeric validation)
    │   ├── calc.py        # Arithmetic domain events
    │   ├── expression.py  # ResolveExpression (fluent chain resolution)
    │   ├── history.py     # Recent-calculation events
    │   └── formula.py     # Formula domain events
    ├── interfaces/        # FormulaService contract
    │   └── formula.py
    ├── mappers/           # Formula aggregate + config object
    │   └── formula.py
    ├── repos/             # FormulaConfigRepository
    │   └── formula.py
    ├── contexts/          # CalculatorAppContext + CalculatorFluentContext
    │   ├── calc.py        # The plain client + session-level record_run
    │   └── fluent.py      # FluentRequestContext + the chainable surface
    └── blueprints/        # create_calculator_app/create_calculator_cli/create_calculator_fluent
        ├── calc.py
        └── fluent.py
```

The arithmetic operators (`calc.add`/`.../calc.resolve`) and their events ship
as calculator-local bounded-context defaults, seeded by `build_calculator_cache`
regardless of what `config.yml` declares. `history.json` is created
automatically at runtime to store the most recent calculations, one entry per
successful run (recorded at the session level via `record_run`, not as a
per-feature step).

## Running the Application

### Client Entry Point

Run the demonstration script from this directory:

```bash
python calc_client.py
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
1.0 + 3.0 - 5.0 * 2.0 = -6.0
2.0 + 3.0 * 4.0 - 1.0 = 13.0
3.0 * 4.0 + 5.0 / 2.0 = 14.5
```

Each entire chain -- not each pairwise reduction -- collapses into a single
`calc.resolve` feature run and one whole-expression history entry. See
[Chapters 9-11 of the tutorial](https://github.com/greatstrength/tiferet/blob/main/docs/tutorial/basic_calculator/index.md)
for how `create_calculator_fluent()`, `CalculatorFluentContext`, and the
`Expression.resolve` PEMDAS scheduling algorithm work.

## Features

- **Addition** (`calc.add`) — Adds two numbers
- **Subtraction** (`calc.subtract`) — Subtracts one number from another
- **Multiplication** (`calc.multiply`) — Multiplies two numbers
- **Division** (`calc.divide`) — Divides two numbers with zero-check
- **Exponentiation** (`calc.exp`) — Raises a number to a power
- **Square Root** (`calc.sqrt`) — Calculates square root (reuses exponentiation with `b=0.5`)
- **Resolve Expression** (`calc.resolve`) — Resolves a fluent chain's fully-logged expression into its final value in one feature run
- **Recent Calculations** (`calc.history`) — Lists the most recently executed calculations, persisted to `history.json` via the file loader
- **Save Formula** (`formula.save`) — Saves a named, variablized formula to `formulas.yml`
- **Get Formula** (`formula.get`) — Retrieves a saved formula by id
- **List Formulas** (`formula.list`) — Lists all saved formulas
- **Evaluate Formula** (`formula.eval`) — Evaluates a saved formula with concrete variable values
- **Fluent Calculator** (`create_calculator_fluent()`) — A chainable `CalculatorFluentContext` exposing `add`/`add_to`, `subtract`/`subtract_from`, `multiply`/`multiply_by`, and `divide`/`divide_by`, plus `.pending` and `.reset()`. Every call just logs a term; calling `run()` -- the same verb the plain client uses to execute any feature -- collapses the whole chain into one `calc.resolve` run when a chain is active, resolving standard operator precedence (PEMDAS) via `Expression.resolve` and reusing the same arithmetic events (validation, division-by-zero handling) as the plain client.

## Tutorial

For a step-by-step guide to building this application, see the [Tiferet tutorial documentation](https://github.com/greatstrength/tiferet/blob/main/docs/tutorial/basic_calculator/index.md).
