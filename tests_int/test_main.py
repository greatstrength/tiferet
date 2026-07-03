# *** imports

# ** core
import copy

# ** infra
import pytest
import yaml

# ** app
from tiferet import App, TiferetAPIError

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
    },
    'logging': {},
}

# *** fixtures

# ** fixture: test_calc_yaml_file
@pytest.fixture
def test_calc_yaml_file(tmp_path):
    '''
    Write TEST_CALC_CONFIG to a temporary YAML file using tmp_path.

    :param tmp_path: The pytest temporary directory path.
    :type tmp_path: pathlib.Path
    :return: The path to the temporary YAML file.
    :rtype: str
    '''

    # Define the temporary file path.
    file_path = tmp_path / 'test_calc.yml'

    # Deep copy the config and set all yaml file paths to the temp file.
    config = copy.deepcopy(TEST_CALC_CONFIG)
    for key in ('feature_config', 'error_config', 'di_config', 'logging_config'):
        config['interfaces']['test_calc']['constants'][key] = str(file_path)

    # Write the configuration to the temporary YAML file.
    with open(str(file_path), 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f)

    # Return the file path as a string.
    return str(file_path)

# ** fixture: basic_calc
@pytest.fixture
def basic_calc(test_calc_yaml_file):
    '''
    Build the basic calculator interface context using the functional blueprint API.

    :param test_calc_yaml_file: The path to the temporary test calculator YAML file.
    :type test_calc_yaml_file: str
    :return: The loaded basic calculator interface context.
    :rtype: AppInterfaceContext
    '''

    # Build and return the test_calc interface context.
    return App('test_calc', app_config=test_calc_yaml_file)

# *** tests

# ** test: basic_calc_add_numbers
def test_basic_calc_add_numbers(basic_calc):
    """
    Test the addition operation of the basic calculator.
    """

    # Perform addition using the basic_calc interface.
    result = basic_calc.run(
        'test_calc.add_number',
        data=dict(
            a=5,
            b=3
        )
    )

    # Assert that the result is as expected.
    assert result == 8, f"Expected 8, got {result}"

# ** test: basic_calc_subtract_numbers
def test_basic_calc_subtract_numbers(basic_calc):   
    """
    Test the subtraction operation of the basic calculator.
    """

    # Perform subtraction using the basic_calc interface.
    result = basic_calc.run(
        'test_calc.subtract_number',
        data=dict(
            a=5,
            b=3
        )
    )

    # Assert that the result is as expected.
    assert result == 2, f"Expected 2, got {result}"

# ** test: basic_calc_multiply_numbers
def test_basic_calc_multiply_numbers(basic_calc):
    """
    Test the multiplication operation of the basic calculator.
    """

    # Perform multiplication using the basic_calc interface.
    result = basic_calc.run(
        'test_calc.multiply_number',
        data=dict(
            a=5,
            b=3
        )
    )

    # Assert that the result is as expected.
    assert result == 15, f"Expected 15, got {result}"

# ** test: basic_calc_divide_numbers
def test_basic_calc_divide_numbers(basic_calc):
    """
    Test the division operation of the basic calculator.
    """

    # Perform division using the basic_calc interface.
    result = basic_calc.run(
        'test_calc.divide_number',
        data=dict(
            a=6,
            b=3
        )
    )

    # Assert that the result is as expected.
    assert result == 2, f"Expected 2, got {result}"

# ** test: basic_calc_divide_by_zero
def test_basic_calc_divide_by_zero(basic_calc):
    """
    Test the division by zero operation of the basic calculator.
    """

    # Perform division by zero using the basic_calc interface.
    with pytest.raises(TiferetAPIError) as exc_info:
        basic_calc.run(
            'test_calc.divide_number',
            data=dict(
                a=6,
                b=0
            )
        )

    assert exc_info.value.error_code == 'DIVISION_BY_ZERO'
    assert exc_info.value.message == 'Division by zero is not allowed.'


# ** test: basic_calc_square_number
def test_basic_calc_square_number(basic_calc):
    """
    Test the squaring operation of the basic calculator.
    """

    # Perform squaring using the basic_calc interface.
    result = basic_calc.run(
        'test_calc.square_number',
        data=dict(
            a=4
        )
    )

    # Assert that the result is as expected.
    assert result == 16, f"Expected 16, got {result}"