# *** imports

# ** core
import subprocess

# ** infra
import pytest

# ** app
from .. import App


# *** fixtures

# ** fixture: app_context
@pytest.fixture
def app_context():

    return App(settings=dict(
        app_repo_module_path='tiferet.proxies.yaml.app',
        app_repo_class_name='AppYamlProxy',
        app_repo_params=dict(
            app_config_file='tiferet/configs/tests/test_calc.yml'
        )
    ))

# ** fixture: basic_calc_cli
@pytest.fixture
def basic_calc_cli(app_context):
    """
    Fixture to load the basic calculator CLI from the app context.
    """

    # Load the basic_calc CLI using the app context.
    return app_context.load_interface('test_calc_cli')

# *** tests

# ** test: basic_calc_cli_add_numbers
def test_basic_calc_cli_add_numbers():
    """
    Test the addition operation of the basic calculator CLI.
    """

    # Run the CLI command for addition using subprocess.
    result = subprocess.run(
        ['python3', 'calc_cli.py', 'test-calc', 'add-number', '5', '3'],
        capture_output=True,
        text=True
    )

    # Assert that the result is as expected.
    assert result.returncode == 0, f"Command failed with return code {result.returncode}"
    assert result.stdout.strip() == '8', f"Expected output '8', got '{result.stdout.strip()}'"

# ** test: basic_calc_cli_subtract_numbers
def test_basic_calc_cli_subtract_numbers():
    """
    Test the subtraction operation of the basic calculator CLI.
    """

    # Run the CLI command for subtraction using subprocess.
    result = subprocess.run(
        ['python3', 'calc_cli.py', 'test-calc', 'subtract-number', '5', '3'],
        capture_output=True,
        text=True
    )

    # Assert that the result is as expected.
    assert result.returncode == 0, f"Command failed with return code {result.returncode}"
    assert result.stdout.strip() == '2', f"Expected output '2', got '{result.stdout.strip()}'"

# ** test: basic_calc_cli_multiply_numbers
def test_basic_calc_cli_multiply_numbers():
    """
    Test the multiplication operation of the basic calculator CLI.
    """

    # Run the CLI command for multiplication using subprocess.
    result = subprocess.run(
        ['python3', 'calc_cli.py', 'test-calc', 'multiply-number', '5', '3'],
        capture_output=True,
        text=True
    )

    # Assert that the result is as expected.
    assert result.returncode == 0, f"Command failed with return code {result.returncode}"
    assert result.stdout.strip() == '15', f"Expected output '15', got '{result.stdout.strip()}'"

# ** test: basic_calc_cli_divide_numbers
def test_basic_calc_cli_divide_numbers():
    """
    Test the division operation of the basic calculator CLI.
    """

    # Run the CLI command for division using subprocess.
    result = subprocess.run(
        ['python3', 'calc_cli.py', 'test-calc', 'divide-number', '6', '3'],
        capture_output=True,
        text=True
    )

    # Assert that the result is as expected.
    assert result.returncode == 0, f"Command failed with return code {result.returncode}"
    assert result.stdout.strip() == '2.0', f"Expected output '2.0', got '{result.stdout.strip()}'"

# ** test: basic_calc_cli_divide_by_zero
def test_basic_calc_cli_divide_by_zero():
    """
    Test the division by zero operation of the basic calculator CLI.
    """

    # Run the CLI command for division by zero using subprocess.
    result = subprocess.run(
        ['python3', 'calc_cli.py', 'test-calc', 'divide-number', '6', '0'],
        capture_output=True,
        text=True
    )

    # Assert that the command fails with an error message.
    assert result.returncode != 0, f"Command should have failed but returned {result.returncode}"
    assert "DIVISION_BY_ZERO" in result.stderr, f"Expected error message about division by zero, got '{result.stderr}'"

# ** test: basic_calc_cli_square_number
def test_basic_calc_cli_square_number():
    """
    Test the square operation of the basic calculator CLI.
    """

    # Run the CLI command for squaring a number using subprocess.
    result = subprocess.run(
        ['python3', 'calc_cli.py', 'test-calc', 'square-number', '4'],
        capture_output=True,
        text=True
    )

    # Assert that the result is as expected.
    assert result.returncode == 0, f"Command failed with return code {result.returncode}"
    assert result.stdout.strip() == '16', f"Expected output '16', got '{result.stdout.strip()}'"


# ** test: basic_calc_cli_invalid_command
def test_basic_calc_cli_invalid_command():
    """
    Test the handling of an invalid command in the basic calculator CLI.
    """

    # Run the CLI command with an invalid command using subprocess.
    result = subprocess.run(
        ['python3', 'calc_cli.py', 'test-calc', 'invalid-command'],
        capture_output=True,
        text=True
    )

    # Assert that the command fails with an error message.
    assert result.returncode != 0, f"Command should have failed but returned {result.returncode}"
    assert "error: argument command: invalid choice" in result.stderr, f"Expected error message about command not found, got '{result.stderr}'"