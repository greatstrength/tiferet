Tiferet - A Python Framework for Domain-Driven Design
Introduction
Tiferet is a Python framework that elegantly distills Domain-Driven Design (DDD) into a practical, powerful tool. Drawing inspiration from the Kabbalistic concept of beauty in balance, Tiferet weaves purpose and functionality into software that not only performs but resonates deeply with its intended vision. As a cornerstone for crafting diverse applications, Tiferet empowers developers to build solutions with clarity, grace, and thoughtful design.
Tiferet embraces the complexity of real-world processes through DDD, transforming intricate business logic and evolving requirements into clear, manageable models. Far from merely navigating this labyrinth, Tiferet provides a graceful path to craft software that reflects its intended purpose with wisdom and precision, embodying the Kabbalistic beauty of balanced form and function. To illustrate its power, this tutorial guides you through building a simple calculator application, demonstrating how Tiferet harmonizes code and concept. By defining discrete number classes and orchestrating their execution through well-crafted validations, Tiferet enables developers to create applications that are both robust and beautifully aligned with their vision, resonating with the soul of their purpose.
Getting Started with Tiferet
Embark on your Tiferet journey with a few simple steps to set up your Python environment. Whether you're new to Python or a seasoned developer, these instructions will prepare you to craft a calculator application with grace and precision.
Installing Python
Tiferet requires Python 3.10 or later. Follow these steps to install it:
Windows

Visit python.org, navigate to the Downloads section, and select the Python 3.10 installer for Windows.
Run the installer, ensuring you check "Add Python 3.10 to PATH," then click "Install Now."

macOS

Download the Python 3.10 installer from python.org.
Open the .pkg file and follow the installation prompts.

Linux (Ubuntu/Debian)
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10

Verify the installation by running:
python3.10 --version

You should see Python 3.10.x if successful.
Setting Up a Virtual Environment
To keep your project dependencies organized, create a virtual environment named tiferet_app for your calculator application:
Create the Environment
# Windows
python -m venv tiferet_app

# macOS/Linux
python3.10 -m venv tiferet_app

Activate the Environment
Activate the environment to isolate your project's dependencies:
# Windows (Command Prompt)
tiferet_app\Scripts\activate

# Windows (PowerShell)
.\tiferet_app\Scripts\Activate.ps1

# macOS/Linux
source tiferet_app/bin/activate

Your terminal should display (tiferet_app), confirming the environment is active. You can now install Tiferet and other dependencies without affecting your system’s Python setup.
Deactivate the Environment
When finished, deactivate the environment with:
deactivate

Your First Calculator App
With your tiferet_app virtual environment activated, you're ready to install Tiferet and start building your calculator application. Follow these steps to set up your project and begin crafting with Tiferet’s elegant approach.
Installing Tiferet
Install the Tiferet package using pip in your activated virtual environment:
# Windows
pip install tiferet

# macOS/Linux
pip3 install tiferet

Project Structure
Create a project directory structure to organize your calculator application:
project_root/
└── app/

The app directory will house your application's number and validation classes. While the directory name is customizable for package releases, we recommend retaining app for internal or proprietary projects to maintain simplicity and consistency.
Crafting Calculator Numbers and Validations
With Tiferet installed and your project structured, it's time to bring your calculator application to life by defining its core number and validation classes. The number classes, housed in app/calc.py, encapsulate arithmetic operations, while validation classes in app/valid.py ensure input integrity. Both inherit from Tiferet’s Command base class, leveraging type hints and the verify method for clarity and robustness. Tiferet’s static Command.handle method orchestrates execution, weaving modularity and elegance into your application. Below, we define number classes for addition, subtraction, multiplication, and division, and validation classes to check input types, showcasing Tiferet’s harmonious design.
Defining Arithmetic Numbers in calc.py
Create a file named calc.py in the app directory with the following content:
from typing import Union
from . import Command

Number = Union[int, float]

class AddNumber(Command):
    '''
    A command to perform addition of two numbers.
    '''
    def execute(self, a: Number, b: Number) -> Number:
        '''
        Execute the addition command.

        :param a: An integer or float representing the first number.
        :param b: An integer or float representing the second number.
        :return: An integer or float representing the sum of a and b.
        '''
        return a + b

class SubtractNumber(Command):
    '''
    A command to perform subtraction of two numbers.
    '''
    def execute(self, a: Number, b: Number) -> Number:
        '''
        Execute the subtraction command.

        :param a: An integer or float representing the first number.
        :param b: An integer or float representing the second number.
        :return: An integer or float representing the difference of a and b.
        '''
        return a - b

class MultiplyNumber(Command):
    '''
    A command to perform multiplication of two numbers.
    '''
    def execute(self, a: Number, b: Number) -> Number:
        '''
        Execute the multiplication command.

        :param a: An integer or float representing the first number.
        :param b: An integer or float representing the second number.
        :return: An integer or float representing the product of a and b.
        '''
        return a * b

class DivideNumber(Command):
    '''
    A command to perform division of two numbers.
    '''
    def execute(self, a: Number, b: Number) -> Number:
        '''
        Execute the division command.

        :param a: An integer or float representing the first number.
        :param b: An integer or float representing the second number, must be non-zero.
        :return: An integer or float representing the quotient of a and b.
        '''
        self.verify(b != 0, 'DIVISION_BY_ZERO', 'Cannot divide by zero')
        return a / b

Defining Validation Numbers in valid.py
To ensure robust input handling, create a file named valid.py in the app directory to validate input types for the calculator’s a and b parameters:
from typing import Any
from . import Command

class ValidateNumber(Command):
    '''
    A command to validate that a value is an integer or float.
    '''
    def execute(self, value: Any) -> None:
        '''
        Validate that the input value is a number (integer or float).

        :param value: Any value to validate.
        :raises TiferetError: If the value is not an integer or

