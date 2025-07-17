# *** imports

# ** core
import os, subprocess

# ** infra
import pytest

# ** app
from .. import App

# *** fixtures

# ** fixture: test_calc_cli
@pytest.fixture
def test_calc_cli():
    '''
    Fixture to provide the path to the basic calculator CLI script.
    This is used to run CLI commands in tests.
    '''
    script = '''
# *** imports

from tiferet import App

# *** code

# Create an instance of the App class with the specified settings.
app = App(settings=dict(
    app_repo_module_path='tiferet.proxies.yaml.app',
    app_repo_class_name='AppYamlProxy',
    app_repo_params=dict(
        app_config_file='tiferet/configs/tests/test_calc.yml'
    )
))

# Load the CLI interface for the calculator.
calc_cli = app.load_interface('test_calc_cli')

# Run the CLI interface according to the provided arguments.
if __name__ == '__main__':
    calc_cli.run()'''
    
    with open('test_calc_cli.py', 'w') as f:
        f.write(script)
    
    return 'test_calc_cli.py'

# ** fixture: test_calc
@pytest.fixture
def test_calc():
    '''
    Fixture to provide the name of the test calculator group.
    This is used to identify the calculator group in CLI commands.
    '''
    return 'test-calc'

# *** tests

# ** test: basic_calc_cli_add_numbers
def test_basic_calc_cli_add_numbers(test_calc_cli, test_calc):
    '''
    Test the addition operation of the basic calculator CLI.
    '''
    # Run the CLI command for addition using subprocess.
    result = subprocess.run(
        ['python3', test_calc_cli, test_calc, 'add-number', '5', '3'],
        capture_output=True,
        text=True
    )
    
    # Assert that the result is as expected.
    assert result.returncode == 0, f"Command failed with return code {result.returncode}"
    assert result.stdout.strip() == '8', f"Expected output '8', got '{result.stdout.strip()}'"
    
    # Remove the temporary file created for the CLI script.
    if os.path.exists(test_calc_cli):
        os.remove(test_calc_cli)

# ** test: basic_calc_cli_subtract_numbers
def test_basic_calc_cli_subtract_numbers(test_calc_cli, test_calc):
    '''
    Test the subtraction operation of the basic calculator CLI.
    '''
    # Run the CLI command for subtraction using subprocess.
    result = subprocess.run(
        ['python3', test_calc_cli, test_calc, 'subtract-number', '5', '3'],
        capture_output=True,
        text=True
    )
    
    # Assert that the result is as expected.
    assert result.returncode == 0, f"Command failed with return code {result.returncode}"
    assert result.stdout.strip() == '2', f"Expected output '2', got '{result.stdout.strip()}'"
    
    # Remove the temporary file created for the CLI script.
    if os.path.exists(test_calc_cli):
        os.remove(test_calc_cli)

# ** test: basic_calc_cli_multiply_numbers
def test_basic_calc_cli_multiply_numbers(test_calc_cli, test_calc):
    '''
    Test the multiplication operation of the basic calculator CLI.
    '''
    # Run the CLI command for multiplication using subprocess.
    result = subprocess.run(
        ['python3', test_calc_cli, test_calc, 'multiply-number', '5', '3'],
        capture_output=True,
        text=True
    )
    
    # Assert that the result is as expected.
    assert result.returncode == 0, f"Command failed with return code {result.returncode}"
    assert result.stdout.strip() == '15', f"Expected output '15', got '{result.stdout.strip()}'"
    
    # Remove the temporary file created for the CLI script.
    if os.path.exists(test_calc_cli):
        os.remove(test_calc_cli)

# ** test: basic_calc_cli_divide_numbers
def test_basic_calc_cli_divide_numbers(test_calc_cli, test_calc):
    '''
    Test the division operation of the basic calculator CLI.
    '''
    # Run the CLI command for division using subprocess.
    result = subprocess.run(
        ['python3', test_calc_cli, test_calc, 'divide-number', '6', '3'],
        capture_output=True,
        text=True
    )
    
    # Assert that the result is as expected.
    assert result.returncode == 0, f"Command failed with return code {result.returncode}"
    assert result.stdout.strip() == '2.0', f"Expected output '2.0', got '{result.stdout.strip()}'"
    
    # Remove the temporary file created for the CLI script.
    if os.path.exists(test_calc_cli):
        os.remove(test_calc_cli)

# ** test: basic_calc_cli_divide_by_zero
def test_basic_calc_cli_divide_by_zero(test_calc_cli, test_calc):
    '''
    Test the division by zero operation of the basic calculator CLI.
    '''
    # Run the CLI command for division by zero using subprocess.
    result = subprocess.run(
        ['python3', test_calc_cli, test_calc, 'divide-number', '6', '0'],
        capture_output=True,
        text=True
    )
    
    # Assert that the command fails with an error message.
    assert result.returncode != 0, f"Command should have failed but returned {result.returncode}"
    assert "DIVISION_BY_ZERO" in result.stderr, f"Expected error message about division by zero, got '{result.stderr}'"
    
    # Remove the temporary file created for the CLI script.
    if os.path.exists(test_calc_cli):
        os.remove(test_calc_cli)

# ** test: basic_calc_cli_square_number
def test_basic_calc_cli_square_number(test_calc_cli, test_calc):
    '''
    Test the square operation of the basic calculator CLI.
    '''
    # Run the CLI command for squaring a number using subprocess.
    result = subprocess.run(
        ['python3', test_calc_cli, test_calc, 'square-number', '4'],
        capture_output=True,
        text=True
    )
    
    # Assert that the result is as expected.
    assert result.returncode == 0, f"Command failed with return code {result.returncode}"
    assert result.stdout.strip() == '16', f"Expected output '16', got '{result.stdout.strip()}'"
    
    # Remove the temporary file created for the CLI script.
    if os.path.exists(test_calc_cli):
        os.remove(test_calc_cli)

# ** test: basic_calc_cli_invalid_command
def test_basic_calc_cli_invalid_command(test_calc_cli, test_calc):
    '''
    Test the handling of an invalid command in the basic calculator CLI.
    '''
    # Run the CLI command with an invalid command using subprocess.
    result = subprocess.run(
        ['python3', test_calc_cli, test_calc, 'invalid-command'],
        capture_output=True,
        text=True
    )
    
    # Assert that the command fails with an error message.
    assert result.returncode != 0, f"Command should have failed but returned {result.returncode}"
    assert "error: argument command: invalid choice" in result.stderr, f"Expected error message about command not found, got '{result.stderr}'"
    
    # Remove the temporary file created for the CLI script.
    if os.path.exists(test_calc_cli):
        os.remove(test_calc_cli)