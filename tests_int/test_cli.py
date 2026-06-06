# *** imports

# ** core
import copy
import os
import subprocess
import sys
from pathlib import Path

# ** infra
import pytest
import yaml

# *** constants

# ** constant: test_calc_config
TEST_CALC_CONFIG = {
    'services': {
        'add_number_cmd': {
            'class_name': 'TestAddNumber',
            'module_path': 'tests_int',
        },
        'subtract_number_cmd': {
            'class_name': 'TestSubtractNumber',
            'module_path': 'tests_int',
        },
        'multiply_number_cmd': {
            'class_name': 'TestMultiplyNumber',
            'module_path': 'tests_int',
        },
        'divide_number_cmd': {
            'class_name': 'TestDivideNumber',
            'module_path': 'tests_int',
        },
    },
    'errors': {
        'DIVISION_BY_ZERO': {
            'name': 'Division by Zero',
            'description': 'This error occurs when an attempt is made to divide by zero.',
            'error_code': 'DIVISION_BY_ZERO',
            'message': [
                {
                    'lang': 'en_US',
                    'text': 'Division by zero is not allowed.',
                },
            ],
        },
    },
    'features': {
        'test_calc': {
            'add_number': {
                'commands': [
                    {
                        'service_id': 'add_number_cmd',
                        'name': 'Add Number Command',
                    },
                ],
                'description': 'Adds two numbers.',
                'name': 'Add Number Feature',
            },
            'subtract_number': {
                'commands': [
                    {
                        'service_id': 'subtract_number_cmd',
                        'name': 'Subtract Number Command',
                    },
                ],
                'description': 'Subtracts two numbers.',
                'name': 'Subtract Number Feature',
            },
            'multiply_number': {
                'commands': [
                    {
                        'service_id': 'multiply_number_cmd',
                        'name': 'Multiply Number Command',
                    },
                ],
                'description': 'Multiplies two numbers.',
                'name': 'Multiply Number Feature',
            },
            'divide_number': {
                'commands': [
                    {
                        'service_id': 'divide_number_cmd',
                        'name': 'Divide Number Command',
                    },
                ],
                'description': 'Divides two numbers.',
                'name': 'Divide Number Feature',
            },
            'square_number': {
                'commands': [
                    {
                        'service_id': 'multiply_number_cmd',
                        'name': 'Square Number Command',
                        'params': {
                            'b': '$r.a',
                        },
                    },
                ],
                'description': 'Squares a number.',
                'name': 'Square Number Feature',
            },
        },
    },
    'interfaces': {
        'test_calc': {
            'name': 'Integration Test - Basic Int Calculator',
            'description': 'The interface instance for testing the calculator features.',
            'constants': {
                'feature_config': None,
                'error_config': None,
                'di_config': None,
                'logging_config': None,
            },
        },
        'test_calc_cli': {
            'name': 'Integration Test - Basic Calculator CLI',
            'description': 'CLI interface for testing calculator features via CliBuilder.',
            'constants': {
                'feature_config': None,
                'error_config': None,
                'di_config': None,
                'logging_config': None,
                'cli_config': None,
            },
        },
    },
    'logging': {
        'formatters': {
            'default': {
                'name': 'Default Formatter',
                'format': '%(message)s',
            },
        },
        'handlers': {
            'default': {
                'name': 'Default Handler',
                'module_path': 'logging',
                'class_name': 'StreamHandler',
                'level': 'WARNING',
                'formatter': 'default',
                'stream': 'ext://sys.stderr',
            },
        },
        'loggers': {
            'root': {
                'name': 'Root Logger',
                'level': 'WARNING',
                'handlers': ['default'],
                'is_root': True,
            },
            'default': {
                'name': 'Default Logger',
                'level': 'WARNING',
                'handlers': ['default'],
            },
        },
    },
}

# ** constant: test_calc_cli_config
TEST_CALC_CLI_CONFIG = {
    'cli': {
        'cmds': {
            'test-calc': {
                'add-number': {
                    'group_key': 'test-calc',
                    'key': 'add-number',
                    'name': 'Add Number Command',
                    'description': 'Adds two numbers.',
                    'args': [
                        {
                            'name_or_flags': ['a'],
                            'description': 'The first number to add.',
                        },
                        {
                            'name_or_flags': ['b'],
                            'description': 'The second number to add.',
                        },
                    ],
                },
                'subtract-number': {
                    'group_key': 'test-calc',
                    'key': 'subtract-number',
                    'name': 'Subtract Number Command',
                    'description': 'Subtracts two numbers.',
                    'args': [
                        {
                            'name_or_flags': ['a'],
                            'description': 'The number to subtract from.',
                        },
                        {
                            'name_or_flags': ['b'],
                            'description': 'The number to subtract.',
                        },
                    ],
                },
                'multiply-number': {
                    'group_key': 'test-calc',
                    'key': 'multiply-number',
                    'name': 'Multiply Number Command',
                    'description': 'Multiplies two numbers.',
                    'args': [
                        {
                            'name_or_flags': ['a'],
                            'description': 'The first number to multiply.',
                        },
                        {
                            'name_or_flags': ['b'],
                            'description': 'The second number to multiply.',
                        },
                    ],
                },
                'divide-number': {
                    'group_key': 'test-calc',
                    'key': 'divide-number',
                    'name': 'Divide Number Command',
                    'description': 'Divides two numbers.',
                    'args': [
                        {
                            'name_or_flags': ['a'],
                            'description': 'The numerator.',
                        },
                        {
                            'name_or_flags': ['b'],
                            'description': 'The denominator.',
                        },
                    ],
                },
                'square-number': {
                    'group_key': 'test-calc',
                    'key': 'square-number',
                    'name': 'Square Number Command',
                    'description': 'Squares a number.',
                    'args': [
                        {
                            'name_or_flags': ['a'],
                            'description': 'The number to square.',
                        },
                    ],
                },
            },
        },
    },
}

# *** fixtures

# ** fixture: test_calc_cli_yaml_file
@pytest.fixture
def test_calc_cli_yaml_file(tmp_path):
    '''
    Write TEST_CALC_CLI_CONFIG to a temporary CLI YAML file using tmp_path.

    :param tmp_path: The pytest temporary directory path.
    :type tmp_path: pathlib.Path
    :return: The path to the temporary CLI YAML file.
    :rtype: str
    '''

    # Define the temporary CLI configuration file path.
    file_path = tmp_path / 'test_calc_cli.yml'

    # Write the CLI configuration to the temporary YAML file.
    with open(str(file_path), 'w', encoding='utf-8') as f:
        yaml.safe_dump(TEST_CALC_CLI_CONFIG, f)

    # Return the file path as a string.
    return str(file_path)

# ** fixture: test_calc_yaml_file
@pytest.fixture
def test_calc_yaml_file(tmp_path, test_calc_cli_yaml_file):
    '''
    Write TEST_CALC_CONFIG to a temporary main YAML file using tmp_path.

    The main YAML file references the CLI YAML file path for the
    ``test_calc_cli`` interface's ``cli_yaml_file`` constant.

    :param tmp_path: The pytest temporary directory path.
    :type tmp_path: pathlib.Path
    :param test_calc_cli_yaml_file: The path to the temporary CLI YAML file.
    :type test_calc_cli_yaml_file: str
    :return: The path to the temporary main YAML file.
    :rtype: str
    '''

    # Define the temporary main configuration file path.
    file_path = tmp_path / 'test_calc.yml'

    # Deep copy the config and wire the shared YAML file paths.
    config = copy.deepcopy(TEST_CALC_CONFIG)

    # Point the test_calc interface constants at the main YAML file.
    for key in ('feature_config', 'error_config', 'di_config', 'logging_config'):
        config['interfaces']['test_calc']['constants'][key] = str(file_path)

    # Point the test_calc_cli interface constants at the main and CLI YAML files.
    for key in ('feature_config', 'error_config', 'di_config', 'logging_config'):
        config['interfaces']['test_calc_cli']['constants'][key] = str(file_path)
    config['interfaces']['test_calc_cli']['constants']['cli_config'] = test_calc_cli_yaml_file

    # Write the configuration to the temporary YAML file.
    with open(str(file_path), 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f)

    # Return the file path as a string.
    return str(file_path)

# ** fixture: test_calc_cli_script
@pytest.fixture
def test_calc_cli_script(tmp_path, test_calc_yaml_file):
    '''
    Generate a temporary CLI script that loads the ``test_calc_cli`` interface.

    The script is written into ``tmp_path`` and references the temporary main
    YAML file via string injection so the CLI interface resolves entirely from
    temporary files.

    :param tmp_path: The pytest temporary directory path.
    :type tmp_path: pathlib.Path
    :param test_calc_yaml_file: The path to the temporary main YAML file.
    :type test_calc_yaml_file: str
    :return: The path to the temporary CLI script.
    :rtype: str
    '''

    # Build the CLI script with the main YAML file path injected.
    script = (
        "import sys\n"
        "from tiferet import CLI\n"
        "\n"
        "if __name__ == '__main__':\n"
        "    CLI('test_calc_cli', app_config={main_yaml!r})\n"
    ).format(main_yaml=test_calc_yaml_file)

    # Write the CLI script to a temporary file.
    script_path = tmp_path / 'test_calc_cli.py'
    script_path.write_text(script, encoding='utf-8')

    # Return the script path as a string.
    return str(script_path)

# ** fixture: test_calc_group
@pytest.fixture
def test_calc_group():
    '''
    Provide the CLI group key used by the calculator commands.

    :return: The CLI group key.
    :rtype: str
    '''

    # Return the group key for the test calculator CLI.
    return 'test-calc'

# ** fixture: cli_subprocess_env
@pytest.fixture
def cli_subprocess_env():
    '''
    Build the environment for CLI subprocesses with PYTHONPATH set to the
    repository root so the spawned interpreter can resolve the
    ``tiferet`` package and its ``tests_int`` subpackage even when the
    package is not installed in the active interpreter.

    :return: A copy of the current environment with PYTHONPATH prefixed by
        the repository root.
    :rtype: dict
    '''

    # Resolve the repository root from this test module's location
    # (tests_int/test_cli.py -> repository root is one parent up).
    repo_root = str(Path(__file__).resolve().parents[1])

    # Copy the current environment to avoid mutating the test process env.
    env = os.environ.copy()

    # Prefix the existing PYTHONPATH with the repository root so the
    # subprocess can import tiferet and tiferet.tests_int regardless of
    # whether the package is installed in the active interpreter.
    existing_pythonpath = env.get('PYTHONPATH', '')
    env['PYTHONPATH'] = (
        f'{repo_root}{os.pathsep}{existing_pythonpath}'
        if existing_pythonpath
        else repo_root
    )

    # Return the augmented environment for use in subprocess.run.
    return env

# *** tests

# ** test: basic_calc_cli_add_numbers
def test_basic_calc_cli_add_numbers(test_calc_cli_script, test_calc_group, cli_subprocess_env):
    '''
    Test the addition operation of the basic calculator CLI.

    :param test_calc_cli_script: The path to the generated CLI script.
    :type test_calc_cli_script: str
    :param test_calc_group: The CLI group key for the calculator.
    :type test_calc_group: str
    :param cli_subprocess_env: The environment for the CLI subprocess with
        PYTHONPATH set to the repository root.
    :type cli_subprocess_env: dict
    '''

    # Run the CLI command for addition via subprocess.
    result = subprocess.run(
        [sys.executable, test_calc_cli_script, test_calc_group, 'add-number', '5', '3'],
        capture_output=True,
        text=True,
        env=cli_subprocess_env,
    )

    # Assert the command succeeded and produced the expected sum.
    assert result.returncode == 0, f"Command failed with return code {result.returncode}: {result.stderr}"
    assert result.stdout.strip() == '8', f"Expected output '8', got '{result.stdout.strip()}'"

# ** test: basic_calc_cli_subtract_numbers
def test_basic_calc_cli_subtract_numbers(test_calc_cli_script, test_calc_group, cli_subprocess_env):
    '''
    Test the subtraction operation of the basic calculator CLI.

    :param test_calc_cli_script: The path to the generated CLI script.
    :type test_calc_cli_script: str
    :param test_calc_group: The CLI group key for the calculator.
    :type test_calc_group: str
    :param cli_subprocess_env: The environment for the CLI subprocess with
        PYTHONPATH set to the repository root.
    :type cli_subprocess_env: dict
    '''

    # Run the CLI command for subtraction via subprocess.
    result = subprocess.run(
        [sys.executable, test_calc_cli_script, test_calc_group, 'subtract-number', '5', '3'],
        capture_output=True,
        text=True,
        env=cli_subprocess_env,
    )

    # Assert the command succeeded and produced the expected difference.
    assert result.returncode == 0, f"Command failed with return code {result.returncode}: {result.stderr}"
    assert result.stdout.strip() == '2', f"Expected output '2', got '{result.stdout.strip()}'"

# ** test: basic_calc_cli_multiply_numbers
def test_basic_calc_cli_multiply_numbers(test_calc_cli_script, test_calc_group, cli_subprocess_env):
    '''
    Test the multiplication operation of the basic calculator CLI.

    :param test_calc_cli_script: The path to the generated CLI script.
    :type test_calc_cli_script: str
    :param test_calc_group: The CLI group key for the calculator.
    :type test_calc_group: str
    :param cli_subprocess_env: The environment for the CLI subprocess with
        PYTHONPATH set to the repository root.
    :type cli_subprocess_env: dict
    '''

    # Run the CLI command for multiplication via subprocess.
    result = subprocess.run(
        [sys.executable, test_calc_cli_script, test_calc_group, 'multiply-number', '5', '3'],
        capture_output=True,
        text=True,
        env=cli_subprocess_env,
    )

    # Assert the command succeeded and produced the expected product.
    assert result.returncode == 0, f"Command failed with return code {result.returncode}: {result.stderr}"
    assert result.stdout.strip() == '15', f"Expected output '15', got '{result.stdout.strip()}'"

# ** test: basic_calc_cli_divide_numbers
def test_basic_calc_cli_divide_numbers(test_calc_cli_script, test_calc_group, cli_subprocess_env):
    '''
    Test the division operation of the basic calculator CLI.

    :param test_calc_cli_script: The path to the generated CLI script.
    :type test_calc_cli_script: str
    :param test_calc_group: The CLI group key for the calculator.
    :type test_calc_group: str
    :param cli_subprocess_env: The environment for the CLI subprocess with
        PYTHONPATH set to the repository root.
    :type cli_subprocess_env: dict
    '''

    # Run the CLI command for division via subprocess.
    result = subprocess.run(
        [sys.executable, test_calc_cli_script, test_calc_group, 'divide-number', '6', '3'],
        capture_output=True,
        text=True,
        env=cli_subprocess_env,
    )

    # Assert the command succeeded and produced the expected quotient.
    assert result.returncode == 0, f"Command failed with return code {result.returncode}: {result.stderr}"
    assert result.stdout.strip() == '2.0', f"Expected output '2.0', got '{result.stdout.strip()}'"

# ** test: basic_calc_cli_divide_by_zero
def test_basic_calc_cli_divide_by_zero(test_calc_cli_script, test_calc_group, cli_subprocess_env):
    '''
    Test the division by zero handling of the basic calculator CLI.

    :param test_calc_cli_script: The path to the generated CLI script.
    :type test_calc_cli_script: str
    :param test_calc_group: The CLI group key for the calculator.
    :type test_calc_group: str
    :param cli_subprocess_env: The environment for the CLI subprocess with
        PYTHONPATH set to the repository root.
    :type cli_subprocess_env: dict
    '''

    # Run the CLI command for division by zero via subprocess.
    result = subprocess.run(
        [sys.executable, test_calc_cli_script, test_calc_group, 'divide-number', '6', '0'],
        capture_output=True,
        text=True,
        env=cli_subprocess_env,
    )

    # Assert the command failed with a DIVISION_BY_ZERO error in stderr.
    assert result.returncode != 0, f"Command should have failed but returned {result.returncode}"
    assert 'DIVISION_BY_ZERO' in result.stderr, f"Expected error message about division by zero, got '{result.stderr}'"

# ** test: basic_calc_cli_square_number
def test_basic_calc_cli_square_number(test_calc_cli_script, test_calc_group, cli_subprocess_env):
    '''
    Test the square operation of the basic calculator CLI.

    :param test_calc_cli_script: The path to the generated CLI script.
    :type test_calc_cli_script: str
    :param test_calc_group: The CLI group key for the calculator.
    :type test_calc_group: str
    :param cli_subprocess_env: The environment for the CLI subprocess with
        PYTHONPATH set to the repository root.
    :type cli_subprocess_env: dict
    '''

    # Run the CLI command for squaring a number via subprocess.
    result = subprocess.run(
        [sys.executable, test_calc_cli_script, test_calc_group, 'square-number', '4'],
        capture_output=True,
        text=True,
        env=cli_subprocess_env,
    )

    # Assert the command succeeded and produced the expected square.
    assert result.returncode == 0, f"Command failed with return code {result.returncode}: {result.stderr}"
    assert result.stdout.strip() == '16', f"Expected output '16', got '{result.stdout.strip()}'"

# ** test: basic_calc_cli_invalid_command
def test_basic_calc_cli_invalid_command(test_calc_cli_script, test_calc_group, cli_subprocess_env):
    '''
    Test the handling of an invalid command in the basic calculator CLI.

    :param test_calc_cli_script: The path to the generated CLI script.
    :type test_calc_cli_script: str
    :param test_calc_group: The CLI group key for the calculator.
    :type test_calc_group: str
    :param cli_subprocess_env: The environment for the CLI subprocess with
        PYTHONPATH set to the repository root.
    :type cli_subprocess_env: dict
    '''

    # Run the CLI with an invalid command via subprocess.
    result = subprocess.run(
        [sys.executable, test_calc_cli_script, test_calc_group, 'invalid-command'],
        capture_output=True,
        text=True,
        env=cli_subprocess_env,
    )

    # Assert the command failed with the argparse invalid choice error.
    assert result.returncode != 0, f"Command should have failed but returned {result.returncode}"
    assert 'error: argument command: invalid choice' in result.stderr, f"Expected error message about invalid command, got '{result.stderr}'"
