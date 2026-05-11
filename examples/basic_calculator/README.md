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
├── config.yml             # Consolidated application configuration
└── app/
    └── events/
        ├── __init__.py
        ├── settings.py    # BasicCalcEvent (numeric validation)
        └── calc.py        # Arithmetic domain events
```

## Running the Application

### App Entry Point

Run the demonstration script from this directory:

```bash
python basic_calc.py
```

Expected output:

```
1 + 2 = 3
5 - 3 = 2
4 * 3 = 12
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
```

## Features

- **Addition** (`calc.add`) — Adds two numbers
- **Subtraction** (`calc.subtract`) — Subtracts one number from another
- **Multiplication** (`calc.multiply`) — Multiplies two numbers
- **Division** (`calc.divide`) — Divides two numbers with zero-check
- **Exponentiation** (`calc.exp`) — Raises a number to a power
- **Square Root** (`calc.sqrt`) — Calculates square root (reuses exponentiation with `b=0.5`)

## Tutorial

For a step-by-step guide to building this application, see the [Tiferet tutorial documentation](https://github.com/greatstrength/tiferet#getting-started).
