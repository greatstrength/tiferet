# *** imports

# ** infra
import pytest

# ** app
from .. import App, TiferetAPIError

# *** fixtures

# ** fixture: app_context
@pytest.fixture
def app_context():

    return App(
        {
            'app_repo_module_path': 'tiferet.repos.app',
            'app_repo_class_name': 'AppYamlRepository',
            'app_repo_params': {
                'app_yaml_file': 'tiferet/assets/tests/test_calc.yml',
            },
        }
    )

# ** fixture: basic_calc
@pytest.fixture
def basic_calc(app_context):
    """
    Fixture to load the basic calculator interface from the app context.
    """

    # Load the basic_calc interface using the app context.
    return app_context.load_interface('test_calc')

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
