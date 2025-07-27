# Tiferet - A Python Framework for Domain-Driven Design

## Introduction

Tiferet is a Python framework that elegantly distills Domain-Driven Design (DDD) into a practical, powerful tool. Drawing inspiration from the concept of beauty in balance as expressed in Kabbalah, Tiferet weaves purpose and functionality into software that not only performs but resonates deeply with its intended vision. As a cornerstone for crafting diverse applications, Tiferet empowers developers to build solutions with clarity, grace, and thoughtful design.

Tiferet embraces the complexity of real-world processes through DDD, transforming intricate business logic and evolving requirements into clear, manageable models. Far from merely navigating this labyrinth, Tiferet provides a graceful path to craft software that reflects its intended purpose with wisdom and precision, embodying beauty and balance in form and function. This tutorial guides you through building a simple calculator application, demonstrating how Tiferet harmonizes code and concept. By defining commands and their configurations, you’ll create a robust and extensible calculator that resonates with Tiferet’s philosophy.

## Getting Started with Tiferet
Embark on your Tiferet journey with a few simple steps to set up your Python environment. Whether you're new to Python or a seasoned developer, these instructions will prepare you to craft a calculator application with grace and precision.

### Installing Python
Tiferet requires Python 3.10 or later. Follow these steps to install it:

#### Windows

Visit python.org, navigate to the Downloads section, and select the Python 3.10 installer for Windows.
Run the installer, ensuring you check "Add Python 3.10 to PATH," then click "Install Now."

#### macOS

Download the Python 3.10 installer from python.org.
Open the .pkg file and follow the installation prompts.

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10
```

#### Verify the installation by running:
```bash
python3.10 --version
```

You should see Python 3.10.x if successful.

### Setting Up a Virtual Environment
To keep your project dependencies organized, create a virtual environment named `tiferet_app` for your calculator application:

#### Create the Environment

```bash
# Windows
python -m venv tiferet_app

# macOS/Linux
python3.10 -m venv tiferet_app
```

#### Activate the Environment
Activate the environment to isolate your project's dependencies:

```bash
# Windows (Command Prompt)
tiferet_app\Scripts\activate

# Windows (PowerShell)
.\tiferet_app\Scripts\Activate.ps1

# macOS/Linux
source tiferet_app/bin/activate
```

Your terminal should display `(tiferet_app)`, confirming the environment is active. You can now install Tiferet and other dependencies without affecting your system’s Python setup.
Deactivate the Environment
When finished, deactivate the environment with:
deactivate

## Your First Calculator App
With your `tiferet_app` virtual environment activated, you're ready to install Tiferet and start building your calculator application. Follow these steps to set up your project and begin crafting with Tiferet’s elegant approach.

### Installing Tiferet
Install the Tiferet package using pip in your activated virtual environment:

```bash
# Windows
pip install tiferet

# macOS/Linux
pip3 install tiferet
```

### Project Structure
Create a project directory structure to organize your calculator application:

```plaintext
project_root/
├── basic_calc.py
├── calc_cli.py
└── app/
    ├── commands/
    │   ├── __init__.py
    │   ├── calc.py
    │   └── settings.py
    └── configs/
        ├── __init__.py
        ├── app.yml
        ├── cli.yml
        ├── container.yml
        ├── error.yml
        ├── feature.yml
        └── logging.yml
```

The `app/commands/` directory holds command classes for arithmetic operations (`calc.py`) and input validation (`settings.py`). The `app/configs/` directory contains configuration files for application settings (`app.yml`), CLI commands (`cli.yml`), dependency injection (`container.yml`), error handling (`error.yml`), feature workflows (`feature.yml`), and logging (`logging.yml`). The `basic_calc.py` script at the root initializes and runs the application. We recommend keeping the `app` directory name for internal projects to ensure consistency, though it can be customized for package releases. The `calc_cli.py` script provides a flexible command-line interface, easily integrated with shell scripts or external systems.

## Crafting the Calculator Application
With Tiferet installed and your project structured, it’s time to build your calculator application. This section guides you through creating a base command for numeric validation, defining arithmetic commands, and setting up the application’s behavior with configurations. By weaving together commands and configurations, you’ll experience Tiferet’s elegant design, harmonizing functionality with clarity and precision.

### Defining Base and Arithmetic Command Classes
Start by creating command classes for numeric validation and arithmetic operations. The `BasicCalcCommand` in `app/commands/settings.py` provides validation logic, while arithmetic commands (`AddNumber`, `SubtractNumber`, `MultiplyNumber`, `DivideNumber`, `ExponentiateNumber`) in `app/commands/calc.py` perform calculations. All arithmetic commands inherit from `BasicCalcCommand`, which extends Tiferet’s `Command` class, ensuring robust numeric validation and core command functionality.

#### Base Command in commands/settings.py
Numeric validation is critical to ensure the calculator handles inputs correctly, preventing errors from invalid data. The `BasicCalcCommand` class centralizes validation logic, making it reusable across all arithmetic commands by converting string inputs to integers or floats.

Create `app/commands/settings.py` with the following contents:

```python
# *** imports

# ** infra
from tiferet.commands import *

# *** commands

# ** command: basic_calc_command
class BasicCalcCommand(Command):
    '''
    A command to validate that a value can be a Number object.
    '''
    
    # * method: verify_number
    def verify_number(self, value: str) -> int | float:
        '''
        Verify that the value can be converted to an integer or float.
        
        :param value: The value to verify.
        :type value: str
        :return: The numeric value as an integer or float.
        :rtype: int | float
        '''
        
        # Check if the value is a valid number.
        is_valid = isinstance(value, str) and (value.isdigit() or (value.replace('.', '', 1).isdigit() and value.count('.') < 2))

        # Verify the value.
        self.verify(
            is_valid,
            'INVALID_INPUT',
            f"Invalid number: {value}",
            value
        )

        # If valid, return the value as a float or int.
        if '.' in value:
            return float(value)
        return int(value)
```

The `BasicCalcCommand` extends Tiferet’s `Command` class, providing a `verify_number` method that validates string inputs and returns them as `int` or `float`. It raises an `INVALID_INPUT` error for invalid inputs, ensuring all arithmetic commands inherit robust validation.

#### Arithmetic Commands in commands/calc.py
The arithmetic commands are the heart of the calculator, delivering core mathematical operations: addition, subtraction, multiplication, division, and exponentiation. These commands leverage Python’s numeric capabilities, processing validated inputs to produce precise results.

Create `app/commands/calc.py` with the following content:

```python
# *** imports

# ** core
from typing import Any

# ** infra
from tiferet.commands import *

# ** app
from .settings import BasicCalcCommand

# *** commands

# ** command: add_number
class AddNumber(BasicCalcCommand):
    '''
    A command to perform addition of two numbers.
    '''
    def execute(self, a: Any, b: Any, **kwargs) -> int | float:
        '''
        Execute the addition command.

        :param a: A number representing the first operand.
        :type a: Any
        :param b: A number representing the second operand.
        :type b: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The sum of a and b.
        :rtype: int | float
        '''
        # Verify numeric inputs
        a_verified = self.verify_number(str(a))
        b_verified = self.verify_number(str(b))

        # Add verified values of a and b.
        result = a_verified + b_verified

        # Return the result.
        return result

# ** command: subtract_number
class SubtractNumber(BasicCalcCommand):
    '''
    A command to perform subtraction of two numbers.
    '''
    def execute(self, a: Any, b: Any, **kwargs) -> int | float:
        '''
        Execute the subtraction command.

        :param a: A number representing the first operand.
        :type a: Any
        :param b: A number representing the second operand.
        :type b: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The difference of a and b.
        :rtype: int | float
        '''
        # Verify numeric inputs
        a_verified = self.verify_number(str(a))
        b_verified = self.verify_number(str(b))

        # Subtract verified values of b from a.
        result = a_verified - b_verified

        # Return the result.
        return result

# ** command: multiply_number
class MultiplyNumber(BasicCalcCommand):
    '''
    A command to perform multiplication of two numbers.
    '''
    def execute(self, a: Any, b: Any, **kwargs) -> int | float:
        '''
        Execute the multiplication command.

        :param a: A number representing the first operand.
        :type a: Any
        :param b: A number representing the second operand.
        :type b: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The product of a and b.
        :rtype: int | float
        '''
        # Verify numeric inputs
        a_verified = self.verify_number(str(a))
        b_verified = self.verify_number(str(b))

        # Multiply the verified values of a and b.
        result = a_verified * b_verified

        # Return the result.
        return result

# ** command: divide_number
class DivideNumber(BasicCalcCommand):
    '''
    A command to perform division of two numbers.
    '''
    def execute(self, a: Any, b: Any, **kwargs) -> int | float:
        '''
        Execute the division command.

        :param a: A number representing the numerator.
        :type a: Any
        :param b: A number representing the denominator, must be non-zero.
        :type b: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The quotient of a and b.
        :rtype: int | float
        '''
        # Verify numeric inputs
        a_verified = self.verify_number(str(a))
        b_verified = self.verify_number(str(b))

        # Check if b is zero to avoid division by zero.
        self.verify(b_verified != 0, 'DIVISION_BY_ZERO')

        # Divide the verified values of a by b.
        result = a_verified / b_verified

        # Return the result.
        return result

# ** command: exponentiate_number
class ExponentiateNumber(BasicCalcCommand):
    '''
    A command to perform exponentiation of two numbers.
    '''
    def execute(self, a: Any, b: Any, **kwargs) -> int | float:
        '''
        Execute the exponentiation command.

        :param a: A number representing the base.
        :type a: Any
        :param b: A number representing the exponent.
        :type b: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of a raised to the power of b.
        :rtype: int | float
        '''
        # Verify numeric inputs
        a_verified = self.verify_number(str(a))
        b_verified = self.verify_number(str(b))

        # Exponentiate the verified value of a by b.
        result = a_verified ** b_verified

        # Return the result.
        return result
```

These commands perform arithmetic operations on flexible input values, validated by `BasicCalcCommand.verify_number` to ensure they are valid integers or floats. The method converts string inputs to `int` or `float` before computation, returning the result as a numeric value. The `DivideNumber` command includes a check to prevent division by zero, raising a configured `DIVISION_BY_ZERO` error if needed.

### Configuring the Calculator Application
With command classes defined, it’s time to configure the Tiferet application to recognize and orchestrate them, enabling seamless user interaction through features and interfaces. This section guides you through setting up the application interface (`app/configs/app.yml`), defining command classes as container attributes (`app/configs/container.yml`), specifying error messages (`app/configs/error.yml`), and organizing features (`app/configs/feature.yml`). These configurations weave together Tiferet’s dependency injection and feature-driven design, ensuring a robust and extensible calculator.

#### Configuring the App Interface in `configs/app.yml`
Define the calculator’s user interface in `app/configs/app.yml` to specify the interface type and its core attributes. This configuration enables Tiferet to initialize the application with default settings, supporting multiple interfaces for flexible command execution.

Create `app/configs/app.yml` with the following content:

```yaml
interfaces:
  basic_calc:
    name: Basic Calculator
    description: Perform basic calculator operations
```

The `interfaces` section configures the `basic_calc` interface with a name and description, using Tiferet’s default settings to streamline application setup. This setup aligns with the project structure, preparing the calculator for command and feature integration.

#### Configuring the Container in `configs/container.yml`
Expose command classes to Tiferet by defining them as container attributes in `app/configs/container.yml`. This configuration maps each command to its module and class, enabling dependency injection for seamless feature execution.

Create the `app/configs/container.yml` with the following content:

```yaml
attrs:
  add_number_cmd:
    module_path: app.commands.calc
    class_name: AddNumber
  subtract_number_cmd:
    module_path: app.commands.calc
    class_name: SubtractNumber
  multiply_number_cmd:
    module_path: app.commands.calc
    class_name: MultiplyNumber
  divide_number_cmd:
    module_path: app.commands.calc
    class_name: DivideNumber
  exponentiate_number_cmd:
    module_path: app.commands.calc
    class_name: ExponentiateNumber
```

The `attrs` section lists each command with a unique identifier (ending in `_cmd`), specifying its module path and class name. This setup ensures Tiferet can instantiate and execute the calculator’s arithmetic commands efficiently.

#### Configuring the Errors in `configs/error.yml`
Handle errors gracefully by defining error messages in `app/configs/error.yml`. This configuration specifies error codes and multilingual messages, ensuring clear feedback for invalid inputs or operations.

Create `app/configs/error.yml` with the following content:

```yaml
errors:
  invalid_input:
    name: Invalid Numeric Input
    message:
      - lang: en_US
        text: 'Value {} must be a number'
      - lang: es_ES
        text: 'El valor {} debe ser un número'
  division_by_zero:
    name: Division By Zero
    message:
      - lang: en_US
        text: 'Cannot divide by zero'
      - lang: es_ES
        text: 'No se puede dividir por cero'
```

The `errors` section defines `invalid_input` for failed numeric validations and `division_by_zero` for division errors, supporting English (`en_US`) and Spanish (`es_ES`) messages. This configuration enhances user experience with localized, precise error handling.

#### Configuring the Features in `configs/feature.yml`
Orchestrate command execution by defining features in `app/configs/feature.yml`. This configuration organizes arithmetic operations into reusable workflows, mapping each feature to its corresponding command for streamlined execution.

Create `app/configs/feature.yml` with the following content:

```yaml
features:
  calc.add:
    name: 'Add Number'
    description: 'Adds one number to another'
    commands:
      - attribute_id: add_number_cmd
        name: Add `a` and `b`
  calc.subtract:
    name: 'Subtract Number'
    description: 'Subtracts one number from another'
    commands:
      - attribute_id: subtract_number_cmd
        name: Subtract `b` from `a`
  calc.multiply:
    name: 'Multiply Number'
    description: 'Multiplies one number by another'
    commands:
      - attribute_id: multiply_number_cmd
        name: Multiply `a` and `b`
  calc.divide:
    name: 'Divide Number'
    description: 'Divides one number by another'
    commands:
      - attribute_id: divide_number_cmd
        name: Divide `a` by `b`
  calc.exp:
    name: 'Exponentiate Number'
    description: 'Raises one number to the power of another'
    commands:
      - attribute_id: exponentiate_number_cmd
        name: Raise `a` to the power of `b`
  calc.sqrt:
    name: 'Square Root'
    description: 'Calculates the square root of a number'
    commands:
      - attribute_id: exponentiate_number_cmd
        name: Calculate square root of `a`
        params:
          b: '0.5'  # Square root is equivalent to raising to the power of 0.5
```

The `features` section maps each operation (e.g., `calc.add`, `calc.sqrt`) to its command via `attribute_id`, with descriptive names and parameters. The `calc.sqrt` feature reuses `exponentiate_number_cmd` with a fixed `b` value of `0.5`, showcasing Tiferet’s flexible workflow design.

### Initializing and Demonstrating the Calculator in basic_calc.py
Bring the Tiferet calculator to life with `basic_calc.py`, a script that initializes the application and demonstrates its arithmetic prowess. This script leverages Tiferet’s `App` class to load the `basic_calc` interface and execute features, showcasing robust calculations and error handling.

Create `basic_calc.py` with the following content:

```python
from tiferet import App, TiferetError

# Initialize the Tiferet application with configuration settings.
app = App()

# Define test cases for calculator features.
test_cases = [
    ('calc.add', dict(a=1, b=2), '{} + {} = {}'),
    ('calc.subtract', dict(a=5, b=3), '{} - {} = {}'),
    ('calc.multiply', dict(a=4, b=3), '{} * {} = {}'),
    ('calc.divide', dict(a=8, b=2), '{} / {} = {}'),
    ('calc.divide', dict(a=8, b=0), '{} / {} = {}'),  # Expect error
    ('calc.exp', dict(a=2, b=3), '{} ** {} = {}'),
    ('calc.sqrt', dict(a=16), '√{} = {}')
]

# Execute each test case, demonstrating calculator features.
for feature_id, data, format_str in test_cases:
    a, b = data.get('a'), data.get('b', None)
    try:
        result = app.run('basic_calc', feature_id, data=data)
        print(format_str.format(a, b if b is not None else a, result))
    except TiferetError as e:
        print(f'Error: {e.message}')
```

The `basic_calc.py` script initializes the Tiferet application with settings from `app/configs/app.yml`, executes a series of test cases for arithmetic features, and handles errors gracefully. It demonstrates the calculator’s core functionality, from addition to square root, with clear output formatting.

### Demonstrating the Calculator

Run the calculator to see its features in action, ensuring Tiferet’s power is fully unleashed. Activate your `tiferet_app` virtual environment and confirm Tiferet is installed, then execute the script to observe the results.

Execute the following command:

```bash
python basic_calc.py
```

This command runs `basic_calc.py`, producing output for each arithmetic operation and error case, leveraging configurations from `app/configs/` to deliver precise, user-friendly results.

## The Calculator as a CLI App
Unleash the calculator’s full potential with a dynamic command-line interface (CLI) powered by Tiferet’s `CliContext`. Implemented in `calc_cli.py` at the project root, this script offers a scriptable, user-friendly interface that complements the `basic_calc.py` test script for debugging. Leveraging Tiferet’s `App` class and `CliContext`, it executes features defined in `app/configs/feature.yml`, accepting command-line arguments for operations like addition (`calc.add`), subtraction (`calc.subtract`), multiplication (`calc.multiply`), division (`calc.divide`), exponentiation (`calc.exp`), and square root (`calc.sqrt`). This CLI interface seamlessly integrates with shell scripts and external systems, showcasing Tiferet’s flexibility in runtime environments.

### Configure CLI Commands in configs/cli.yml
Define the CLI’s command structure in `app/configs/cli.yml` to enable `CliContext` to parse user inputs. This configuration specifies commands, their arguments, and descriptions, ensuring intuitive interaction with the calculator’s features.

Create `app/configs/cli.yml` with the following content:

```yaml
cli:
  cmds:
    calc.add:
      group_key: calc
      key: add
      description: Adds two numbers.
      args:
        - name_or_flags:
            - a
          description: The first number to add.
        - name_or_flags:
            - b
          description: The second number to add.
      name: Add Number Command
    calc.subtract:
      group_key: calc
      key: subtract
      description: Subtracts one number from another.
      args:
        - name_or_flags:
            - a
          description: The number to subtract from.
        - name_or_flags:
            - b
          description: The number to subtract.
      name: Subtract Number Command
    calc.multiply:
      group_key: calc
      key: multiply
      description: Multiplies two numbers.
      args:
        - name_or_flags:
            - a
          description: The first number to multiply.
        - name_or_flags:
            - b
          description: The second number to multiply.
      name: Multiply Number Command
    calc.divide:
      group_key: calc
      key: divide
      description: Divides one number by another.
      args:
        - name_or_flags:
            - a
          description: The numerator.
        - name_or_flags:
            - b
          description: The denominator.
      name: Divide Number Command
    calc.sqrt:
      group_key: calc
      key: sqrt
      description: Calculates the square root of a number.
      args:
        - name_or_flags:
            - a
          description: The number to square root.
      name: Square Root Command
```

The `cli.cmds` section maps each feature (e.g., `calc.add`) to its command group (`calc`), key (e.g., `add`), and arguments (`a`, `b`), enabling `CliContext` to parse inputs and execute features with precision.

### Configuring the CLI Interface in configs/app.yml
Enable the CLI interface by adding the `calc_cli` interface to `app/configs/app.yml`. This configuration integrates `CliContext` with its dependencies, `CliYamlProxy` and `CliHandler`, to manage command-line interactions.

Add the `calc_cli` interface to the `interfaces` section:

```yaml
interfaces:
  basic_calc:
    name: Basic Calculator
    description: Perform basic calculator operations
  calc_cli:
    name: Calculator CLI
    description: Perform basic calculator operations via CLI
    module_path: tiferet.contexts.cli
    class_name: CliContext
    attrs:
      cli_repo:
        module_path: tiferet.proxies.yaml.cli
        class_name: CliYamlProxy
        params:
          cli_config_file: app/configs/cli.yml
      cli_service:
        module_path: tiferet.handlers.cli
        class_name: CliHandler
```

The `calc_cli` interface specifies `CliContext` as its implementation, with `cli_repo` and `cli_service` attributes linking to `CliYamlProxy` (loading `cli.yml`) and `CliHandler` for command processing. This setup ensures robust CLI functionality within Tiferet’s ecosystem.

### Creating the CLI Script
Craft a streamlined CLI script in `calc_cli.py` to initialize and run the calculator’s command-line interface. This script uses Tiferet’s `App` class to load the `calc_cli` interface, powered by `CliContext`, for seamless command execution.

Create `calc_cli.py` with the following content:

```python
from tiferet import App

# Create new app (manager) instance.
app = App()

# Load the CLI app instance.
cli = app.load_interface('calc_cli')

# Run the CLI app.
if __name__ == '__main__':
    cli.run()
```

The `calc_cli.py` script initializes the `App`, loads the `calc_cli` interface, and executes commands via `CliContext`, with error handling to ensure user-friendly feedback for invalid inputs or operations.

### Demonstrating the CLI Calculator
Experience the calculator’s CLI in action by running commands that showcase its arithmetic and error-handling capabilities. Ensure the `tiferet_app` virtual environment is activated and Tiferet is installed, then execute the script with feature-specific arguments.

Run the CLI with commands like:

```bash
# Add two numbers
python calc_cli.py calc add 1 2
# Output: 1 + 2 = 3

# Calculate square root
python calc_cli.py calc sqrt 4
# Output: √4 = 2.0

# Division by zero
python calc_cli.py calc divide 5 0
# Output: Error: Cannot divide by zero
```

The `calc_cli.py` script offers a versatile, scriptable interface that integrates effortlessly with shell scripts or external systems, powered by `CliContext` for robust command execution. For quick testing or debugging, use `basic_calc.py` to run individual features with predefined values, while the CLI provides precise, argument-driven control.

## Conclusion
Embark on a journey of elegance and precision with Tiferet’s Domain-Driven Design framework, as this tutorial has crafted a robust calculator application. You’ve defined arithmetic and validation commands in `app/commands/calc.py` and `app/commands/settings.py`, orchestrated them with configurations in `app/configs/app.yml`, `app/configs/feature.yml`, and `app/configs/cli.yml`, and brought them to life through `basic_calc.py` and the `CliContext`-powered `calc_cli.py`. This configuration-driven approach, enriched with dependency injection and multilingual error handling, reflects Tiferet’s harmonious balance of clarity and power, making development both functional and delightful.

Extend your calculator’s potential with Tiferet’s modular design. Create a terminal user interface (TUI) in `calc_tui.py`, leveraging `CliContext` for interactive operation, or define a scientific calculator interface (`sci_calc`) in `app/configs/app.yml` with advanced features like trigonometric functions. Integrate the calculator into larger systems, such as financial modeling, by adding new commands and features in `app/configs/feature.yml`. Experiment with `calc_cli.py` to test additional operations, tweak configurations in `app/configs/`, or explore Tiferet’s documentation for advanced DDD techniques. Let Tiferet’s graceful framework guide you to solutions that resonate with purpose and precision, transforming complexity into clarity.
