"""Tiferet Error YAML Proxy Tests Exports"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from ....configs import TiferetError
from ....data import DataObject, ErrorConfigData
from ..error import ErrorYamlProxy

# *** fixtures

# ** fixture: error_config_file
@pytest.fixture
def error_config_file(tmp_path) -> str:
    '''
    Fixture to provide the path to the error YAML configuration file.

    :return: The error YAML configuration file path.
    :rtype: str
    '''

    # Create a temporary YAML file with sample error configuration content.
    file_path = tmp_path / 'test_error.yaml'

    # Write the sample error configuration to the YAML file.
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump({
            'errors': {
                'test_error': {
                    'name': 'Test Error',
                    'error_code': 'TEST_ERROR_CODE',
                    'message': [
                        {
                            'lang': 'en',
                            'text': 'This is a test error message.'
                        }
                    ]
                },
                'test_formatted_error': {
                    'name': 'Test Formatted Error',
                    'error_code': 'TEST_FORMATTED_ERROR_CODE',
                    'message': [
                        {
                            'lang': 'en',
                            'text': 'This is a test formatted error message with a placeholder: {placeholder}.'
                        }
                    ]
                }
            }
        }, f)

    # Return the file path as a string.
    return str(file_path)

# ** fixture: error_yaml_proxy
@pytest.fixture
def error_yaml_proxy(error_config_file: str) -> ErrorYamlProxy:
    '''
    Fixture to create an instance of the ErrorYamlProxy.

    :param error_read_config_file: The error YAML configuration file path.
    :type error_ModelObject_file: str
    '''

    # Create and return the ErrorYamlProxy instance.
    return ErrorYamlProxy(error_config_file)

# *** tests

# ** test_int: error_yaml_proxy_load_yaml
def test_int_error_yaml_proxy_load_yaml(error_yaml_proxy: ErrorYamlProxy):
    """
    Test the error YAML proxy load YAML method.

    :param error_yaml_proxy: The error YAML proxy.
    :type error_yaml_proxy: ErrorYamlProxy
    """

    # Load the YAML file.
    data = error_yaml_proxy.load_yaml()

    # Check the loaded data.
    assert data
    assert data.get('errors')
    assert len(data['errors']) > 0

# ** test_int: error_yaml_proxy_load_yaml_file_not_found
def test_int_error_yaml_proxy_load_yaml_file_not_found(error_yaml_proxy: ErrorYamlProxy):
    """
    Test the error YAML proxy load YAML method with a file not found error.

    :param error_yaml_proxy: The error YAML proxy.
    :type error_yaml_proxy: ErrorYamlProxy
    """

    # Set a non-existent configuration file.
    error_yaml_proxy.yaml_file = 'non_existent_file.yml'

    # Attempt to load the YAML file.
    with pytest.raises(TiferetError) as exc_info:
        error_yaml_proxy.load_yaml()

    # Check the exception message.
    assert exc_info.value.error_code == 'ERROR_CONFIG_LOADING_FAILED'
    assert 'Unable to load error configuration file' in str(exc_info.value)

# ** test_int: error_yaml_proxy_list_errors
def test_int_error_yaml_proxy_list(
        error_yaml_proxy: ErrorYamlProxy,
    ):
    '''
    Test the list method of the ErrorYamlProxy.

    :param error_yaml_proxy: The error YAML proxy.
    :type error_yaml_proxy: ErrorYamlProxy
    :param errors: The dictionary of expected errors.
    :type errors: Dict[str, Error]
    '''

    # List the errors.
    test_errors = error_yaml_proxy.list()

    # Check the errors.
    assert test_errors
    assert len(test_errors) == 2
    error_ids = [error.id for error in test_errors]
    assert 'test_error' in error_ids
    assert 'test_formatted_error' in error_ids

# ** test_int: error_yaml_proxy_exists
def test_int_error_yaml_proxy_exists(error_yaml_proxy: ErrorYamlProxy):
    '''
    Test the exists method of the ErrorYamlProxy.

    :param error_yaml_proxy: The error YAML proxy.
    :type error_yaml_proxy: ErrorYamlProxy
    '''

    # Check if the error exists.
    assert error_yaml_proxy.exists('test_error')
    assert error_yaml_proxy.exists('test_formatted_error')

# ** test_int: error_yaml_proxy_exists_not_found
def test_int_error_yaml_proxy_exists_not_found(error_yaml_proxy: ErrorYamlProxy):
    '''
    Test the exists method of the ErrorYamlProxy for a non-existent error.

    :param error_yaml_proxy: The error YAML proxy.
    :type error_yaml_proxy: ErrorYamlProxy
    '''

    # Check if the error exists.
    assert not error_yaml_proxy.exists('not_found')

# ** test_int: error_yaml_proxy_get
def test_int_error_yaml_proxy_get(
        error_yaml_proxy: ErrorYamlProxy,
    ):
    '''
    Test the get method of the ErrorYamlProxy.

    :param error_yaml_proxy: The error YAML proxy.
    :type error_yaml_proxy: ErrorYamlProxy
    :param errors: The dictionary of expected errors.
    :type errors: Dict[str, Error]
    '''

    # Get the error.
    test_error = error_yaml_proxy.get('test_error')
    test_formatted_error = error_yaml_proxy.get('test_formatted_error')

    # Check the error.
    assert test_error
    assert test_error.id == 'test_error'
    assert test_error.name == 'Test Error'
    assert test_error.error_code == 'TEST_ERROR_CODE'
    assert len(test_error.message) == 1
    assert test_error.message[0].lang == 'en'
    assert test_error.message[0].text == 'This is a test error message.'

    # Check the formatted error.
    assert test_formatted_error
    assert test_formatted_error.id == 'test_formatted_error'
    assert test_formatted_error.name == 'Test Formatted Error'
    assert test_formatted_error.error_code == 'TEST_FORMATTED_ERROR_CODE'
    assert len(test_formatted_error.message) == 1
    assert test_formatted_error.message[0].lang == 'en'
    assert test_formatted_error.message[0].text == 'This is a test formatted error message with a placeholder: {placeholder}.'

# ** test_int: error_yaml_proxy_get_not_found
def test_int_error_yaml_proxy_get_not_found(error_yaml_proxy: ErrorYamlProxy):
    '''
    Test the get method of the ErrorYamlProxy for a non-existent error.

    :param error_yaml_proxy: The error YAML proxy.
    :type error_yaml_proxy: ErrorYamlProxy
    '''
    
    # Get the error.
    test_error = error_yaml_proxy.get('not_found')

    # Check the error.
    assert not test_error

# ** test_int: error_yaml_proxy_save
def test_int_error_yaml_proxy_save(error_yaml_proxy: ErrorYamlProxy):
    '''
    Test the save method of the ErrorYamlProxy.

    :param error_yaml_proxy: The error YAML proxy.
    :type error_yaml_proxy: ErrorYamlProxy
    '''

    # Create new error.
    error = DataObject.from_data(
        ErrorConfigData,
        id='new_test_error',
        name='New Test Error',
        error_code='NEW_TEST_ERROR_CODE',
        message=[{
            'lang': 'en',
            'text': 'This is a new test error message.'
        }]
    ).map()

    # Save the modified error.
    error_yaml_proxy.save(error)

    # Reload the error to verify the changes.
    modified_error = error_yaml_proxy.get('new_test_error')
    assert modified_error
    assert modified_error.id == 'new_test_error'
    assert modified_error.name == 'New Test Error'
    assert modified_error.error_code == 'NEW_TEST_ERROR_CODE'
    assert len(modified_error.message) == 1
    assert modified_error.message[0].lang == 'en'
    assert modified_error.message[0].text == 'This is a new test error message.'

# ** test_int: error_yaml_proxy_delete
def test_int_error_yaml_proxy_delete(error_yaml_proxy: ErrorYamlProxy):
    '''
    Test the delete method of the ErrorYamlProxy.

    :param error_yaml_proxy: The error YAML proxy.
    :type error_yaml_proxy: ErrorYamlProxy
    '''

    # Delete an existing error.
    error_yaml_proxy.delete('test_formatted_error')

    # Attempt to get the deleted error.
    deleted_error = error_yaml_proxy.get('test_formatted_error')

    # Check that the error is None.
    assert not deleted_error