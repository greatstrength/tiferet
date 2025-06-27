# *** imports

# ** core
import os

# ** infra
import pytest, yaml

# ** app
from ..error import *
from ....models.error import *


# *** fixtures

# ** fixture: error_config_file
@pytest.fixture
def error_read_config_file():
    """Fixture to provide the path to the error configuration file."""
    
    return 'tiferet/configs/tests/test.yml'


# ** fixture: error_yaml_proxy
@pytest.fixture
def error_yaml_proxy(error_read_config_file):
    """Fixture to create an instance of the ErrorYamlProxy."""

    return ErrorYamlProxy(error_read_config_file)


# ** fixture: errors
@pytest.fixture
def errors():
    """Fixture to create a list of error objects for testing."""

    return dict(test_error=Error.new(
            name='Test Error',
            error_code='TEST_ERROR',
            message=[
                ValueObject.new(
                    ErrorMessage,
                    lang='en_US',
                    text='An error occurred.'
                )
            ]
        ),
        test_formatted_error=Error.new(
            name='Test Formatted Error',
            error_code='TEST_FORMATTED_ERROR',
            message=[
                ErrorMessage.new(
                    ErrorMessage,
                    lang='en_US',
                    text='An error occurred: {}.'
                )
            ]
        )
    )


# *** tests

# ** test_int: error_yaml_proxy_list_errors
def test_int_error_yaml_proxy_list(
    error_yaml_proxy,
    errors
):

    # List the errors.
    test_errors = error_yaml_proxy.list()

    # Check the errors.
    assert len(test_errors) == len(errors.values())
    for error_id in errors:
        assert error_id in [error.id for error in test_errors]


# ** test_int: error_yaml_proxy_exists
def test_int_error_yaml_proxy_exists(error_yaml_proxy):

    # Check if the error exists.
    assert error_yaml_proxy.exists('test_error')
    assert error_yaml_proxy.exists('test_formatted_error')


# ** test_int: error_yaml_proxy_exists_not_found
def test_int_error_yaml_proxy_exists_not_found(error_yaml_proxy):

    # Check if the error exists.
    assert not error_yaml_proxy.exists('not_found')


# ** test_int: error_yaml_proxy_get
def test_int_error_yaml_proxy_get(error_yaml_proxy, errors):

    # Get the error.
    test_error = error_yaml_proxy.get('test_error')
    test_formatted_error = error_yaml_proxy.get('test_formatted_error')

    # Check the error.
    assert test_error
    assert test_error.id == 'test_error'
    assert test_error.name == errors['test_error'].name
    assert test_error.error_code == errors['test_error'].error_code
    assert test_error.message[0].lang == errors['test_error'].message[0].lang
    assert test_error.message[0].text == errors['test_error'].message[0].text
    assert test_formatted_error
    assert test_formatted_error.id == 'test_formatted_error'
    assert test_formatted_error.name == errors['test_formatted_error'].name
    assert test_formatted_error.error_code == errors['test_formatted_error'].error_code
    assert test_formatted_error.message[0].lang == errors['test_formatted_error'].message[0].lang
    assert test_formatted_error.message[0].text == errors['test_formatted_error'].message[0].text


# ** test_int: error_yaml_proxy_get_not_found
def test_int_error_yaml_proxy_get_not_found(error_yaml_proxy):
    
    # Get the error.
    test_error = error_yaml_proxy.get('not_found')

    # Check the error.
    assert not test_error


# ** test_int: error_yaml_proxy_save
def test_int_error_yaml_proxy_save(errors):

    # Create a test error configuration file.
    file_path = 'tiferet/configs/tests/test_error.yml'
    with open(file_path, 'w') as file:
        yaml.dump(dict(errors={}), file)

    # Create an instance of the ErrorYamlProxy for writing.
    error_write_yaml_proxy = ErrorYamlProxy(file_path)

    # Save the errors.
    for error in errors.values():
        error_write_yaml_proxy.save(error)
    
    # List the errors.
    test_errors = error_write_yaml_proxy.list()

    # Check the errors.
    assert len(test_errors) == len(errors.values())
    for error_id in errors:
        assert error_id in [error.id for error in test_errors]

    # Remove the test file after saving.
    try:
        import os
        os.remove(file_path)
    except OSError as e:
        print(f"Error removing test file: {e}")