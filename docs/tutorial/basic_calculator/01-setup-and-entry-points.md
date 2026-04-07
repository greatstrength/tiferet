Here's the **corrected and updated documentation** with `config.yml` now placed at the **root** of the project (next to `basic_calc.py` and `calc_cli.py`), as you requested.

### Updated Step 1: Setup & Entry Points

```markdown
# Step 1: Setup & Entry Points

Hey! 👋  
Let's get the playground set up first and peek at what our finished calculator will actually *do* when we run it. This way you can see the goal right away — super motivating before we dive into the code.

### 1.1 Quick environment setup

Open your terminal (or command prompt) and run:

```bash
# Create a fresh virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate          # On Windows: venv\Scripts\activate

# Install Tiferet
pip install tiferet
```

You're good to go! 🎉

### 1.2 Start with this folder structure

Create an empty folder called `basic-calculator` (or whatever name you like) and set up these empty files/folders for now:

```
basic-calculator/
├── basic_calc.py               # ← our simple test runner
├── calc_cli.py                 # ← the cool CLI version
├── config.yml                  # ← ← ALL configuration lives here
└── app/
    ├── events/                 # ← domain events go here
    │   ├── __init__.py
    │   └── calc.py
    └── utils/                  # ← reusable helpers (we'll add soon)
        ├── __init__.py
        └── calc.py
```

**Important change in Tiferet v2.0:**  
All configuration (app interfaces, features, errors, CLI commands, logging, DI, etc.) has been consolidated into a **single file** called `config.yml` located at the **project root**. No more separate files inside `app/configs/`.

### 1.3 The two main entry points (what you'll run)

These are the files people will actually use. Let's look at them now so you know what success looks like.

**basic_calc.py** — a simple script that runs a few test cases automatically

```python
from tiferet import App, TiferetError

app = App()  # loads everything from the root config.yml

# Some fun test cases
tests = [
    ("calc.add",      {"a": 7,  "b": 11},   "{} + {} = {}"),
    ("calc.subtract", {"a": 20, "b": 8},    "{} - {} = {}"),
    ("calc.multiply", {"a": 6,  "b": 7},    "{} × {} = {}"),
    ("calc.divide",   {"a": 15, "b": 3},    "{} ÷ {} = {}"),
    ("calc.divide",   {"a": 10, "b": 0},    "{} ÷ {} → error"),
    ("calc.exp",      {"a": 2,  "b": 3},    "{} ^ {} = {}"),
    ("calc.sqrt",     {"a": 16},            "√{} = {}"),
    ("calc.add",      {"a": "hello", "b": 5}, "Bad input → error"),
]

print("Running calculator tests...\n")

for feature_id, data, fmt in tests:
    try:
        result = app.run("basic_calc", feature_id, data=data)
        if "b" in data:
            print(fmt.format(data["a"], data["b"], result))
        else:
            print(fmt.format(data["a"], result))
    except TiferetError as e:
        print(f"Error: {e.message}")
```

**What you'll see when it works** (after we build the rest):

```
Running calculator tests...

7 + 11 = 18.0
20 - 8 = 12.0
6 × 7 = 42.0
15 ÷ 3 = 5.0
Error: Cannot divide by zero
2 ^ 3 = 8.0
√16 = 4.0
Error: Invalid number: 'hello'
```

**calc_cli.py** — the interactive command-line version

```python
from tiferet import App

app = App()
cli = app.load_interface("calc_cli")   # connects to root config.yml

if __name__ == "__main__":
    cli.run()
```

**What using it feels like** (once everything's wired):

```bash
python calc_cli.py calc add 19 23
# → 42.0

python calc_cli.py calc sqrt 144
# → 12.0

python calc_cli.py calc divide 10 0
# → Error: Cannot divide by zero
```

Pretty neat, right? These two files are the "front door" — everything else we build (events, utils, and the single root `config.yml`) is just to make these work beautifully.

No pressure — we're just looking ahead.  
In the next step we'll start writing the actual math operations.

→ Ready for the fun part?  
Jump to **[Step 2: Domain Events – Initial Version](02-domain-events.md)**