# Tiferet - A Python Framework for Domain-Driven Design

## Introduction

Tiferet is a Python framework that elegantly distills Domain-Driven Design (DDD) into a practical, powerful tool. Drawing inspiration from the Kabbalistic concept of beauty in balance, Tiferet weaves purpose and functionality into software that not only performs but resonates deeply with its intended vision. As a cornerstone for crafting diverse applications, Tiferet empowers developers to build solutions with clarity, grace, and thoughtful design.

Tiferet embraces the complexity of real-world processes through DDD, transforming intricate business logic and evolving requirements into clear, manageable models. Far from merely navigating this labyrinth, Tiferet provides a graceful path to craft software that reflects its intended purpose with wisdom and precision, embodying the Kabbalistic beauty of balanced form and function. This tutorial guides you through building a simple calculator application, demonstrating how Tiferet harmonizes code and concept. By defining a domain model, command classes, and feature-driven configurations, you’ll create a robust and extensible calculator that resonates with Tiferet’s philosophy.

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
    │   └── valid.py
    ├── configs/
    │   ├── __init__.py
    │   └── config.yml
    └── models/
        ├── __init__.py
        └── calc.py
```

The `app/models/` directory will house the calculator’s domain model, `app/commands/` will contain command classes for operations and validations, and `app/configs/` will store configuration files. The `basic_calc.py` script at the root will initialize and run the application. While the app directory name is customizable for package releases, we recommend retaining it for internal or proprietary projects to maintain simplicity and consistency. The `calc_cli.py` script is a versatile scriptable interface that integrates easily with shell scripts or external systems.

## Crafting the Calculator Application
With Tiferet installed and your project structured, it’s time to bring your calculator application to life. We’ll start by defining the domain model, then create command classes for arithmetic and validation, configure the application’s behavior through container attributes, features, errors, and context, and finally initialize and demonstrate the app with a script. This sequence showcases Tiferet’s harmonious design, weaving together models, commands, and configurations with grace.

### Defining the Number Model in `models/calc.py`
The calculator’s numerical values are represented by a `Number` value object, defined in `app/models/calc.py`. This model encapsulates a string-based numerical value, validated to ensure it represents an integer or float, and provides a method to format it as a number.

Create `app/models/calc.py` with the following content:

```python
from tiferet.models import *

class Number(ValueObject):
    '''
    A value object representing a numerical value in the calculator domain.
    '''
    value = StringType(
        required=True,
        regex=r'^-?\d*\.?\d*$',
        metadata=dict(
            description='A string representing an integer or float (e.g., "123", "-123.45", "0123", ".123", "123.").'
        )
    )

    def is_float(self) -> bool:
        '''
        Check if the value is formatted as a float.

        :return: True if the value contains a decimal point and valid digits, False otherwise.
        '''
        return '.' in self.value and self.value.strip('-.').replace('.', '').isdigit()

    def format(self) -> int | float:
        '''
        Convert the string value to an integer or float.

        :return: An integer if the value represents a whole number, otherwise a float.
        '''
        if self.is_float():
            return float(self.value)
        return int(self.value)
```

The Number class uses Tiferet’s ValueObject to ensure immutability, with a `StringType` attribute validated by a regex to accept integers and floats (e.g., `"123"`, `"-123.45"`, `".123"`). The is_float method checks for decimal points, and format converts the string to an int or float, enabling arithmetic operations.

### Defining Command Classes in commands/calc.py and commands/valid.py
Next, we define command classes to perform arithmetic operations and input validation. Arithmetic commands (`AddNumber`, `SubtractNumber`, `MultiplyNumber`, `DivideNumber`, `ExponentiateNumber`) are in `app/commands/calc.py`, while the validation command (`ValidateNumber`) is in `app/commands/valid.py`. All inherit from Tiferet’s Command base class, using the static `Command.handle` method for execution.

#### Arithmetic Commands in commands/calc.py
Create `app/commands/calc.py` with the following content:

```python
from tiferet.commands import *

from ..models.calc import Number

class AddNumber(Command):
    '''
    A command to perform addition of two numbers.
    '''
    def execute(self, a: Number, b: Number, **kwargs) -> Number:
        '''
        Execute the addition command.

        :param a: A Number object representing the first number.
        :type a: Number
        :param b: A Number object representing the second number.
        :type b: Number
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A Number object representing the sum of a and b.
        :rtype: Number
        '''

        # Add formatted values of a and b.
        result = a.format() + b.format()

        # Return a new Number object with the result.
        return result

class SubtractNumber(Command):
    '''
    A command to perform subtraction of two numbers.
    '''
    def execute(self, a: Number, b: Number, **kwargs) -> Number:
        '''
        Execute the subtraction command.

        :param a: A Number object representing the first number.
        :type a: Number
        :param b: A Number object representing the second number.
        :type b: Number
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A Number object representing the difference of a and b.
        :rtype: Number
        '''
        
        # Subtract formatted values of b from a.
        result = a.format() - b.format()

        # Return a new Number object with the result.
        return result

class MultiplyNumber(Command):
    '''
    A command to perform multiplication of two numbers.
    '''
    def execute(self, a: Number, b: Number, **kwargs) -> Number:
        '''
        Execute the multiplication command.

        :param a: A Number object representing the first number.
        :type a: Number
        :param b: A Number object representing the second number.
        :type b: Number
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A Number object representing the product of a and b.
        :rtype: Number
        '''
        
        # Multiply the formatted values of a and b.
        result = a.format() * b.format()

        # Return a new Number object with the result.
        return result

class DivideNumber(Command):
    '''
    A command to perform division of two numbers.
    '''
    def execute(self, a: Number, b: Number, **kwargs) -> Number:
        '''
        Execute the division command.

        :param a: A Number object representing the first number.
        :type a: Number
        :param b: A Number object representing the second number, must be non-zero.
        :type b: Number
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A Number object representing the quotient of a and b.
        :rtype: Number
        '''
        # Check if b is zero to avoid division by zero.
        self.verify(b.format() != 0, 'DIVISION_BY_ZERO')

        # Divide the formatted values of a by b.
        result = a.format() / b.format()

        # Return a new Number object with the result.
        return result


class ExponentiateNumber(Command):
    '''
    A command to perform exponentiation of two numbers.
    '''
    def execute(self, a: Number, b: Number, **kwargs) -> Number:
        '''
        Execute the exponentiation command.

        :param a: A Number object representing the base number.
        :type a: Number
        :param b: A Number object representing the exponent.
        :type b: Number
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A Number object representing a raised to the power of b.
        :rtype: Number
        '''
        
        # Exponentiate the formatted value of a by b.
        result = a.format() ** b.format()

        # Return a new Number object with the result.
        return result
```

These commands perform arithmetic operations on `Number` objects, using `format()` to extract numerical values and `ModelObject.new` to return results as new `Number` objects. The `DivideNumber` command includes a verify check to prevent division by zero, referencing a configured error.

#### Validation Command in `commands/valid.py`
Create `app/commands/valid.py` with the following content:

```python
from tiferet.commands import *

from ..models.calc import Number

class ValidateNumber(Command):
    '''
    A command to validate that a value can be a Number object.
    '''
    def execute(self, value: str, **kwargs) -> None:
        '''
        Validate that the input value can be used to create a Number object.

        :param value: Any string value to validate.
        :type value: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :raises TiferetError: If the value cannot be a Number.
        '''
        try:
            return ModelObject.new(Number, value=str(value))
        except Exception as e:
            self.verify(False, 'INVALID_INPUT', value)
```

The `ValidateNumber` command ensures inputs can be converted to `Number` objects, raising a configured error for invalid values.

### Configuring the Application in `configs/config.yml`
The calculator’s behavior is defined in `app/configs/config.yml`, which configures container attributes, features, errors, and the application context. This centralized configuration enables Tiferet’s dependency injection container to orchestrate commands and features gracefully.

Create `app/configs/config.yml` with the following content:

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
  validate_number_cmd:
    module_path: app.commands.valid
    class_name: ValidateNumber

features:
  calc.add:
    name: 'Add Number'
    description: 'Adds one number to another'
    commands:
      - attribute_id: validate_number_cmd
        name: Validate `a` input
        data_key: a
        params:
          value: $r.a
      - attribute_id: validate_number_cmd
        name: Validate `b` input
        data_key: b
        params:
          value: $r.b
      - attribute_id: add_number_cmd
        name: Add `a` and `b`
  calc.subtract:
    name: 'Subtract Number'
    description: 'Subtracts one number from another'
    commands:
      - attribute_id: validate_number_cmd
        name: Validate `a` input
        data_key: a
        params:
          value: $r.a
      - attribute_id: validate_number_cmd
        name: Validate `b` input
        data_key: b
        params:
          value: $r.b
      - attribute_id: subtract_number_cmd
        name: Subtract `b` from `a`
  calc.multiply:
    name: 'Multiply Number'
    description: 'Multiplies one number by another'
    commands:
      - attribute_id: validate_number_cmd
        name: Validate `a` input
        data_key: a
        params:
          value: $r.a
      - attribute_id: validate_number_cmd
        name: Validate `b` input
        data_key: b
        params:
          value: $r.b
      - attribute_id: multiply_number_cmd
        name: Multiply `a` and `b`
  calc.divide:
    name: 'Divide Number'
    description: 'Divides one number by another'
    commands:
      - attribute_id: validate_number_cmd
        name: Validate `a` input
        data_key: a
        params:
          value: $r.a
      - attribute_id: validate_number_cmd
        name: Validate `b` input
        data_key: b
        params:
          value: $r.b
      - attribute_id: divide_number_cmd
        name: Divide `a` by `b`
  calc.exp:
    name: 'Exponentiate Number'
    description: 'Raises one number to the power of another'
    commands:
      - attribute_id: validate_number_cmd
        name: Validate `a` input
        data_key: a
        params:
          value: $r.a
      - attribute_id: validate_number_cmd
        name: Validate `b` input
        data_key: b
        params:
          value: $r.b
      - attribute_id: exponentiate_number_cmd
        name: Raise `a` to the power of `b`
  calc.sqrt:
    name: 'Square Root'
    description: 'Calculates the square root of a number'
    commands:
      - attribute_id: validate_number_cmd
        name: Validate `a` input
        data_key: a
        params:
          value: $r.a
      - attribute_id: validate_number_cmd
        name: Convert `b` to number
        data_key: b
        params:
          value: '0.5'
      - attribute_id: exponentiate_number_cmd
        name: Calculate square root of `a`

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

interfaces:
  basic_calc:
    name: Basic Calculator
    description: Perform basic calculator operations
    const:
      container_config_file: 'app/configs/config.yml'
      feature_config_file: 'app/configs/config.yml'
      error_config_file: 'app/configs/config.yml'
```

`attrs`: Defines container attributes for dependency injection, mapping to command classes (e.g., `add_number_cmd` to `AddNumber`).

`features`: Configures feature workflows, sequencing validation and arithmetic commands (e.g., `calc.add` validates `a` and `b`, then adds them). The `calc.sqrt` feature reuses `exponentiate_number_cmd` with `b: "0.5"` for square roots.

`errors`: Specifies error messages for `invalid_input` and `division_by_zero`, supporting `en_US` and `es_ES` for multilingual extensibility.

`interfaces`: Defines the `basic_calc` interface instance, linking to the configuration file for container, features, and errors.

### Initializing and Demonstrating the Calculator in basic_calc.py
Finally, we initialize the calculator with an initializer script, `basic_calc.py`, at the project root. This script uses Tiferet’s App class to load the `basic_calc` context and execute features, demonstrating the calculator’s functionality.
Create `basic_calc.py` with the following content:

```python
from tiferet import App

# Create new app (manager) instance.
app = App(dict(
    app_repo_module_path='tiferet.proxies.yaml.app',
    app_repo_class_name='AppYamlProxy',
    app_repo_params=dict(
        app_config_file='app/configs/config.yml',
    )
))

# Execute the add feature to add the values.
a = 1
b = 2
addition = app.run(
    'basic_calc', 
    'calc.add', 
    data=dict(
        a=a,
        b=b,
    )
)

print(f'{a} + {b} = {addition}')
```

### Demonstrating the Calculator
To run the calculator, ensure your `tiferet_app` virtual environment is activated and Tiferet is installed. Execute the initializer script:
```bash
python basic_calc
```

### Running the Calculator as a CLI
For a flexible and scriptable interface, the calculator includes a command-line interface (CLI) implemented in `calc_cli.py` at the project root. This script complements the `basic_calc.py` test script, which remains available for debugging and simple feature execution. The `calc_cli.py` script leverages Tiferet’s App class to execute features defined in `app/configs/config.yml`, accepting command-line arguments for operations and input values. It supports all calculator features: addition (calc.add), subtraction (calc.subtract), multiplication (`calc.multiply`), division (`calc.divide`), exponentiation (`calc.exp`), and square root (`calc.sqrt`).
The `calc_cli.py` script uses Python’s argparse to define subcommands for each feature, with required arguments `-a` (first number) and `-b` (second number, except for sqrt). The script executes the specified feature in the `basic_calc` context, returning the result as an integer or float.

Create `calc_cli.py` with the following content:
```python
import argparse
from tiferet import App, TiferetError

def main():
    """Parse CLI arguments and execute the calculator feature."""
    parser = argparse.ArgumentParser(description="Basic Calculator CLI using Tiferet")
    parser.add_argument('--config', default='app/configs/config.yml', help='Path to config file')

    subparsers = parser.add_subparsers(dest='operation', required=True, help='Calculator operation')

    # Define subcommands for each feature
    operations = [
        ('add', 'Add two numbers', True),
        ('subtract', 'Subtract one number from another', True),
        ('multiply', 'Multiply two numbers', True),
        ('divide', 'Divide one number by another', True),
        ('exp', 'Raise one number to the power of another', True),
        ('sqrt', 'Calculate the square root of a number', False),
    ]

    for op, help_text, needs_b in operations:
        subparser = subparsers.add_parser(op, help=help_text)
        subparser.add_argument('-a', required=True, help='First number')
        if needs_b:
            subparser.add_argument('-b', required=True, help='Second number')

    args = parser.parse_args()

    # Map operation to feature ID
    feature_map = {
        'add': 'calc.add',
        'subtract': 'calc.subtract',
        'multiply': 'calc.multiply',
        'divide': 'calc.divide',
        'exp': 'calc.exp',
        'sqrt': 'calc.sqrt',
    }
    feature_id = feature_map[args.operation]

    # Prepare feature parameters
    params = {'a': str(args.a)}
    if args.operation != 'sqrt':
        params['b'] = str(args.b)

    # Create app instance
    # # Assume the default app settings is defined in a YAML file
    settings = dict(
        app_repo_module_path='tiferet.proxies.yaml.app',
        app_repo_class_name='AppYamlProxy',
        app_repo_params=dict(
            app_config_file=args.config,
        )
    )
    app = App(settings)

    try:
        # Execute feature with locale
        result = app.run('basic_calc', feature_id, data=params)

        # Display result
        if args.operation == 'sqrt':
            print(f"√{args.a} = {result}")
        else:
            op_symbol = {'add': '+', 'subtract': '-', 'multiply': '*', 'divide': '/', 'exp': '^'}[args.operation]
            print(f"{args.a} {op_symbol} {args.b} = {result}")
    except TiferetError as e:
        print(f"Error: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == '__main__':
    main()
```

Run the CLI with commands like:
```bash
# Add two numbers (default en_US)
python calc_cli.py add -a 1 -b 2
# Output: 1 + 2 = 3

# Calculate square root (en_US)
python calc_cli.py sqrt -a 4
# Output: √4 = 2.0

# Invalid input (es_ES)
python calc_cli.py add -a abc -b 2 --locale es_ES
# Output: Error: El valor abc debe ser un número

# Division by zero (en_US)
python calc_cli.py divide -a 5 -b 0
# Output: Error: Cannot divide by zero
```

The `calc_cli.py` script is scriptable and integrates easily with shell scripts or external systems, making it a versatile interface for the calculator. For quick testing or debugging, use `basic_calc.py`, which executes a single feature (e.g., `calc.add`) with hardcoded values. The CLI’s argument-driven design allows precise control over operations, showcasing Tiferet's flexibility in run-time environments.

## Conclusion
This tutorial has woven together the elegance of Tiferet’s Domain-Driven Design framework to create a robust and extensible basic calculator. From defining the immutable Number model to crafting command classes for arithmetic and validation, configuring features and errors, and launching the application via both a test script (`basic_calc.py`) and a CLI (`calc_cli.py`), you’ve experienced Tiferet’s balance of clarity and power. The configuration-driven approach, with dependency injection and multilingual error handling, embodies the Kabbalistic beauty of purposeful design, making the calculator both functional and a joy to develop.

With the foundation laid, you can extend this application in many directions. Consider adding a terminal user interface (TUI) in a new script, `calc_tui.py`, to wrap `calc_cli.py` for interactive menu-driven operation. Explore a scientific calculator context (`sci_calc`) with advanced features like trigonometric functions, reusing the `Number` model or introducing new ones. Or integrate the calculator into larger systems, leveraging Tiferet’s modularity for domains like financial modeling or data processing. Whatever path you choose, Tiferet’s graceful framework will guide you to solutions that resonate with both purpose and precision.
To continue your journey, try running additional features with `calc_cli.py`, experiment with new feature configurations in `app/configs/config.yml`, or dive into Tiferet’s documentation for advanced DDD techniques. The beauty of Tiferet lies in its ability to transform complexity into clarity—may your creations reflect this harmony.
