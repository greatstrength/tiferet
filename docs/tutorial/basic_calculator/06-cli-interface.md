# Step 6: CLI Interface & Commands

We've got a working calculator through the script runner — now let's make it feel like a real tool people can use from the terminal.  
Enter the command-line interface (CLI): fast, scriptable, and perfect for quick calculations.

### 6.1 Update the consolidated config.yml

Since we're using a single `config.yml` at the project root, we'll add the CLI command definitions to it.

Open (or create) **`config.yml`** in the root of your project and add the `cli` section at the bottom:

**config.yml** (add this section)

```yaml
# ... (previous interfaces, attrs, features, and errors sections remain above)

# CLI command definitions
cli:
  cmds:
    calc:
      add:
        group_key: calc
        key: add
        name: Add Command
        description: Add two numbers
        args:
          - name_or_flags:
              - a
            description: First number
          - name_or_flags:
              - b
            description: Second number

      subtract:
        group_key: calc
        key: subtract
        name: Subtract Command
        description: Subtract second number from first
        args:
          - name_or_flags:
              - a
            description: First number
          - name_or_flags:
              - b
            description: Second number

      multiply:
        group_key: calc
        key: multiply
        name: Multiply Command
        description: Multiply two numbers
        args:
          - name_or_flags:
              - a
            description: First number
          - name_or_flags:
              - b
            description: Second number

      divide:
        group_key: calc
        key: divide
        name: Divide Command
        description: Divide first number by second
        args:
          - name_or_flags:
              - a
            description: Numerator
          - name_or_flags:
              - b
            description: Denominator

      exp:
        group_key: calc
        key: exp
        name: Exponentiate Command
        description: Raise first number to the power of second
        args:
          - name_or_flags:
              - a
            description: Base
          - name_or_flags:
              - b
            description: Exponent

      sqrt:
        group_key: calc
        key: sqrt
        name: Square Root Command
        description: Calculate square root of a number
        args:
          - name_or_flags:
              - a
            description: The number to take the square root of
```

Each command needs `group_key`, `key`, and `name`. Tiferet uses these to automatically build the argument parser and map commands to the features you defined earlier.

### 6.2 Update the interfaces section in config.yml

Make sure your `interfaces` section includes the CLI interface. Your full `interfaces` block should now look like this:

```yaml
interfaces:
  basic_calc:
    name: Basic Calculator
    description: Simple arithmetic operations via script or direct call

  calc_cli:
    name: Calculator CLI
    description: Command-line interface for calculator operations
    module_path: tiferet.contexts.cli
    class_name: CliContext
```

### 6.3 The CLI entry point script

**calc_cli.py** (this stays very short)

```python
from tiferet import App

app = App()  # loads everything from the root config.yml

# Load the CLI interface
cli = app.load_interface("calc_cli")

if __name__ == "__main__":
    cli.run()
```

That's it!  
`app.load_interface("calc_cli")` tells Tiferet to use the built-in `CliContext`, which reads the CLI commands from the same `config.yml`.

### 6.4 Run and play with it

With your virtual environment activated, try these commands:

```bash
# Basic usage
python calc_cli.py calc add 19 23
# → 42.0

python calc_cli.py calc exp 2 10
# → 1024.0

# Square root
python calc_cli.py calc sqrt 144
# → 12.0

# Error cases
python calc_cli.py calc divide 10 0
# → Error: Cannot divide by zero

python calc_cli.py calc add hello 5
# → Error: Invalid number: 'hello'
```

### 6.5 Bonus: Make it feel like a native command

Want to run it as simply `calc add 19 23` instead of typing `python calc_cli.py` every time?

1. Make the script executable (macOS/Linux):
   ```bash
   chmod +x calc_cli.py
   ```

2. Add a shebang at the very top of `calc_cli.py`:
   ```python
   #!/usr/bin/env python3
   ```

3. Run it directly:
   ```bash
   ./calc_cli.py calc add 19 23
   ```

You can also create a shell alias or symlink for even smoother use.

### 6.6 Why this feels so good

- No extra code for argument parsing — everything is defined in `config.yml`
- The same domain events power both the script runner and the CLI
- Error messages are consistent across interfaces
- Adding new commands is as simple as editing the `cli` section in `config.yml`

You've now built a complete, dual-mode calculator:  
- `basic_calc.py` → great for testing and automation  
- `calc_cli.py` → perfect for everyday terminal use

→ And that's a wrap on the basic calculator!  
Feel free to experiment — add more operations, improve error messages, or even build a web/TUI version next.

Thanks for building this with me — hope it was as fun to make as it was to guide! 🚀