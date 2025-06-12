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
To keep your project dependencies organized, create a virtual environment named tiferet_app for your calculator application:

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

Your terminal should display (tiferet_app), confirming the environment is active. You can now install Tiferet and other dependencies without affecting your system’s Python setup.
Deactivate the Environment
When finished, deactivate the environment with:
deactivate

## Your First Calculator App
With your tiferet_app virtual environment activated, you're ready to install Tiferet and start building your calculator application. Follow these steps to set up your project and begin crafting with Tiferet’s elegant approach.

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
└── app/
    ├── commands/
    │   ├── __init__.py
    │   ├── calc.py
    │   └── valid.py
    ├── configs/
    │   ├── __init__.py
    │   └── config.yaml
    └── models/
        ├── __init__.py
        └── calc.py
```

The app/models/ directory will house the calculator’s domain model, app/commands/ will contain command classes for operations and validations, and app/configs/ will store configuration files. The basic_calc.py script at the root will initialize and run the application. While the app directory name is customizable for package releases, we recommend retaining it for internal or proprietary projects to maintain simplicity and consistency.

## Crafting the Calculator Application
With Tiferet installed and your project structured, it’s time to bring your calculator application to life. We’ll start by defining the domain model, then create command classes for arithmetic and validation, configure the application’s behavior through container attributes, features, errors, and context, and finally initialize and demonstrate the app with a script. This sequence showcases Tiferet’s harmonious design, weaving together models, commands, and configurations with grace.

### Defining the Number Model in models/calc.py
The calculator’s numerical values are represented by a Number value object, defined in app/models/calc.py. This model encapsulates a string-based numerical value, validated to ensure it represents an integer or float, and provides a method to format it as a number.

Create app/models/calc.py with the following content:

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

The Number class uses Tiferet’s ValueObject to ensure immutability, with a StringType attribute validated by a regex to accept integers and floats (e.g., "123", "-123.45", ".123"). The is_float method checks for decimal points, and format converts the string to an int or float, enabling arithmetic operations.

### Defining Command Classes in commands/calc.py and commands/valid.py
Next, we define command classes to perform arithmetic operations and input validation. Arithmetic commands (AddNumber, SubtractNumber, MultiplyNumber, DivideNumber, ExponentiateNumber) are in app/commands/calc.py, while the validation command (ValidateNumber) is in app/commands/valid.py. All inherit from Tiferet’s Command base class, using the static Command.handle method for execution.

#### Arithmetic Commands in commands/calc.py
Create app/commands/calc.py with the following content:

```python
from ..commands import Command
from ..models import ModelObject
from ..models.calc import Number

class AddNumber(Command):
    '''
    A command to perform addition of two numbers.
    '''
    def execute(self, a: Number, b: Number) -> Number:
        '''
        Execute the addition command.

        :param a: A Number object representing the first number.
        :type a: Number
        :param b: A Number object representing the second number.
        :type b: Number
        :return: A Number object representing the sum of a and b.
        :rtype: Number
        '''
        return ModelObject.new(Number, value=str(a.format() + b.format()))

class SubtractNumber(Command):
    '''
    A command to perform subtraction of two numbers.
    '''
    def execute(self, a: Number, b: Number) -> Number:
        '''
        Execute the subtraction command.

        :param a: A Number object representing the first number.
        :type a: Number
        :param b: A Number object representing the second number.
        :type b: Number
        :return: A Number object representing the difference of a and b.
        :rtype: Number
        '''
        return ModelObject.new(Number, value=str(a.format() - b.format()))

class MultiplyNumber(Command):
    '''
    A command to perform multiplication of two numbers.
    '''
    def execute(self, a: Number, b: Number) -> Number:
        '''
        Execute the multiplication command.

        :param a: A Number object representing the first number.
        :type a: Number
        :param b: A Number object representing the second number.
        :type b: Number
        :return: A Number object representing the product of a and b.
        :rtype: Number
        '''
        return ModelObject.new(Number, value=str(a.format() * b.format()))

class DivideNumber(Command):
    '''
    A command to perform division of two numbers.
    '''
    def execute(self, a: Number, b: Number) -> Number:
        '''
        Execute the division command.

        :param a: A Number object representing the first number.
        :type a: Number
        :param b: A Number object representing the second number, must be non-zero.
        :type b: Number
        :return: A Number object representing the quotient of a and b.
        :rtype: Number
        '''
        self.verify(b.format() != 0, 'DIVISION_BY_ZERO')
        return ModelObject.new(Number, value=str(a.format() / b.format()))

class ExponentiateNumber(Command):
    '''
    A command to perform exponentiation of two numbers.
    '''
    def execute(self, a: Number, b: Number) -> Number:
        '''
        Execute the exponentiation command.

        :param a: A Number object representing the base number.
        :type a: Number
        :param b: A Number object representing the exponent.
        :type b: Number
        :return: A Number object representing a raised to the power of b.
        :rtype: Number
        '''
        return ModelObject.new(Number, value=str(a.format() ** b.format()))
```

These commands perform arithmetic operations on Number objects, using format() to extract numerical values and ModelObject.new to return results as new Number objects. The DivideNumber command includes a verify check to prevent division by zero, referencing a configured error.

#### Validation Command in commands/valid.py
Create app/commands/valid.py with the following content:

```python
from ..commands import Command
from ..models.calc import Number

class ValidateNumber(Command):
    '''
    A command to validate that a value can be a Number object.
    '''
    def execute(self, value: str) -> None:
        '''
        Validate that the input value can be used to create a Number object.

        :param value: Any string value to validate.
        :type value: str
        :raises TiferetError: If the value cannot be a Number.
        '''
        try:
            ModelObject.new(Number, value=str(value))
        except Exception as e:
            self.verify(False, 'INVALID_INPUT', value)
```

The ValidateNumber command ensures inputs can be converted to Number objects, raising a configured error for invalid values.

### Configuring the Application in configs/config.yaml
The calculator’s behavior is defined in app/configs/config.yaml, which configures container attributes, features, errors, and the application context. This centralized configuration enables Tiferet’s dependency injection container to orchestrate commands and features gracefully.

Create app/configs/config.yaml with the following content:

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
        return_to_data: true
        data_key: a
        params:
          value: $r.a
      - attribute_id: validate_number_cmd
        name: Validate `b` input
        return_to_data: true
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
        return_to_data: true
        data_key: a
        params:
          value: $r.a
      - attribute_id: validate_number_cmd
        name: Validate `b` input
        return_to_data: true
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
        return_to_data: true
        data_key: a
        params:
          value: $r.a
      - attribute_id: validate_number_cmd
        name: Validate `b` input
        return_to_data: true
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
        return_to_data: true
        data_key: a
        params:
          value: $r.a
      - attribute_id: validate_number_cmd
        name: Validate `b` input
        return_to_data: true
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
        return_to_data: true
        data_key: a
        params:
          value: $r.a
      - attribute_id: validate_number_cmd
        name: Validate `b` input
        return_to_data: true
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
          value: '0.5
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

contexts:
  basic_calc:
    name: Basic Calculator
    description: Perform basic calculator operations
    const:
      container_config_file: 'app/configs/config.yaml'
      feature_config_file: 'app/configs/config.yaml'
      error_config_file: 'app/configs/config.yaml'
```

attrs: Defines container attributes for dependency injection, mapping to command classes (e.g., add_number_cmd to AddNumber).


features: Configures feature workflows, sequencing validation and arithmetic commands (e.g., calc.add validates a and b, then adds them). The calc.sqrt feature reuses exponentiate_number_cmd with b: "0.5" for square roots.

errors: Specifies error messages for invalid_input and division_by_zero, supporting en_US and es_ES for multilingual extensibility.

contexts: Defines the basic_calc application instance, linking to the configuration file for container, features, and errors.

### Initializing and Demonstrating the Calculator in basic_calc.py
Finally, we initialize the calculator with an initializer script, basic_calc.py, at the project root. This script uses Tiferet’s App class to load the basic_calc context and execute features, demonstrating the calculator’s functionality.
Create basic_calc.py with the following content:

```python
from tiferet import App

# Create new app (manager) instance.
app = App(config_file='app/configs/config.yaml')

# Execute the add feature to add the values.
a = 1
b = 2
addition = app.execute_feature('basic_calc', 'calc.add', a=str(a), b=str(b))

print(f'{a} + {b} = {addition.format()}')
```

### Demonstrating the Calculator
To run the calculator, ensure your tiferet_app virtual environment is activated and Tiferet is installed. Execute the initializer script:
```bash
python basic_calc
```
