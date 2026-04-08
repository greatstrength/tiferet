# Step 6: CLI Interface & Commands

We've got a working calculator through the script runner — now let's make it feel like a real tool people can use from the terminal.  
Enter the command-line interface (CLI): fast, scriptable, and perfect for quick calculations.

### 6.1 Add the CLI config section

In Tiferet v2.0, CLI definitions live in root `config.yml`. Add this section to tell Tiferet how to parse commands like `calc add 19 23`.

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

Each command needs `group_key`, `key`, and `name` — Tiferet uses these to build the argument parser and map commands to features.  
The `args` list defines the positional arguments that get passed as `data` to your events.

### 6.2 Update config.yml to add the CLI interface

Now we need to tell Tiferet about the CLI interface. In the same root `config.yml`, update the `interfaces` block to add `calc_cli`:

**config.yml** (interfaces section)

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

- `calc_cli` tells Tiferet to use the built-in `CliContext` for command-line handling.
- CLI command definitions are read from the `cli` section in the same root `config.yml`.

### 6.3 The CLI entry point script

**calc_cli.py**

```python
from tiferet import App

app = App().load_app_service(app_yaml_file="config.yml")

# Load the CLI interface we defined in config.yml
cli = app.load_interface("calc_cli")

if __name__ == "__main__":
    cli.run()
```

That's it — super short!  
`app.load_interface("calc_cli")` pulls in `CliContext` from root `config.yml`, which also contains the CLI command definitions.

### 6.4 Run and play with it

With the venv activated:

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

### 6.5 Bonus: Make it feel even more like a native command

Want to run it as just `calc add 19 23` instead of `python calc_cli.py ...`?

1. Make the script executable (on macOS/Linux):
   ```bash
   chmod +x calc_cli.py
   ```

2. Add a shebang at the very top of `calc_cli.py` (first line):
   ```python
   #!/usr/bin/env python3
   ```

3. Run it directly:
   ```bash
   ./calc_cli.py calc add 19 23
   ```

(You can also symlink or alias it in your shell for even smoother use.)

### 6.6 Why this feels so good

- No extra code for argument parsing — YAML does it
- Same events power both script and CLI
- Errors are consistent and friendly across interfaces
- Easy to extend: add more commands by editing `config.yml`

You've now got a complete, dual-mode calculator: script for automation/testing, CLI for everyday use.

→ And that's a wrap on the basic calculator!  
Feel free to experiment — add more operations, tweak errors, or build a web version next.

Thanks for building this with me — hope it was as fun to make as it was to guide! 🚀
