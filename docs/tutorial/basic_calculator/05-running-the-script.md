# Step 5: Running the Script Runner

Alright, we've wired up the events, added our validation utility, and connected everything with YAML configs — now it's showtime!  
Let's fire up `basic_calc.py` and see the calculator in action.

### 5.1 The final basic_calc.py script

This is the simple test runner we looked at way back in Step 1 — now it should work perfectly with all the pieces in place.

**basic_calc.py**

```python
from tiferet import App, TiferetError

app = App()  # loads everything from app/configs/

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

### 5.2 Run it!

In your terminal (with the venv activated):

```bash
python basic_calc.py
```

### 5.3 Expected output (success + error cases)

You should see something like this:

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

- All math operations work smoothly (thanks to `CalcUtil.verify_number`)
- Division by zero is caught cleanly
- Square root is just exponentiation with 0.5 — no extra event needed
- Bad input (like "hello") raises a nice, configured error

### 5.4 Quick troubleshooting tips

- Error "No such feature" → double-check `feature.yml` keys match the `feature_id` in tests
- Import error → make sure paths in `container.yml` point to `app.events.calc`
- Validation not working → confirm `app/utils/calc.py` is importable (check the `__init__.py` files)

If you see the output above (or very close), congratulations — your core calculator is fully functional!

You've gone from empty folder to a working, configuration-driven app.  
Now let's add the final polish: the command-line interface.

→ Ready for the CLI experience?  
Head to **[Step 6: CLI Interface & Commands](06-cli-interface.md)**
