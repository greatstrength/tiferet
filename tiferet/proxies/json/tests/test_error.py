"""Tiferet Error JSON Proxy Tests Exports"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, json

# ** app
from ....configs import TiferetError
from ....data import DataObject, ErrorConfigData
from ..error import ErrorJsonProxy

# *** fixtures

# ** fixture: error_config_file
@pytest.fixture
def error_config_file(tmp_path) -> str:
    '''
    Fixture to provide the path to the error JSON configuration file.

    :return: The error JSON configuration file path.
    :rtype: str
    '''

    # Create a temporary JSON file with sample error configuration content.
    file_path = tmp_path / 'test_error.json'

    # Write the sample error configuration to the JSON file.
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
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

# ** fixture: error_json_proxy
@pytest.fixture
def error_json_proxy(error_config_file: str) -> ErrorJsonProxy:
    '''
    Fixture to create an instance of the ErrorJsonProxy.

    :param error_read_config_file: The error JSON configuration file path.
    :type error_ModelObject_file: str
    '''

    # Create and return the ErrorJsonProxy instance.
    return ErrorJsonProxy(error_config_file)

# *** tests

# ** test_int: error_json_proxy_load_json
def test_int_error_json_proxy_load_json(error_json_proxy: ErrorJsonProxy):
    """
    Test the error JSON proxy load JSON method.

    :param error_json_proxy: The error JSON proxy.
    :type error_json_proxy: ErrorJsonProxy
    """

    # Load the JSON file.
    data = error_json_proxy.load_json()

    # Check the loaded data.
    assert data
    assert data.get('errors')
    assert len(data['errors']) > 0

# ** test_int: error_json_proxy_load_json_file_not_found
def test_int_error_json_proxy_load_json_file_not_found(error_json_proxy: ErrorJsonProxy):
    """
    Test the error JSON proxy load JSON method with a file not found error.

    :param error_json_proxy: The error JSON proxy.
    :type error_json_proxy: ErrorJsonProxy
    """

    # Set a non-existent configuration file.
    error_json_proxy.json_file = 'non_existent_file.yml'

    # Attempt to load the JSON file.
    with pytest.raises(TiferetError) as exc_info:
        error_json_proxy.load_json()

    # Check the exception message.
    assert exc_info.value.error_code == 'ERROR_CONFIG_LOADING_FAILED'
    assert 'Unable to load error configuration file' in str(exc_info.value)

# ** test_int: error_json_proxy_list_errors
def test_int_error_json_proxy_list(
        error_json_proxy: ErrorJsonProxy,
    ):
    '''
    Test the list method of the ErrorJsonProxy.

    :param error_json_proxy: The error JSON proxy.
    :type error_json_proxy: ErrorJsonProxy
    :param errors: The dictionary of expected errors.
    :type errors: Dict[str, Error]
    '''

    # List the errors.
    test_errors = error_json_proxy.list()

    # Check the errors.
    assert test_errors
    assert len(test_errors) == 2
    error_ids = [error.id for error in test_errors]
    assert 'test_error' in error_ids
    assert 'test_formatted_error' in error_ids

# ** test_int: error_json_proxy_exists
def test_int_error_json_proxy_exists(error_json_proxy: ErrorJsonProxy):
    '''
    Test the exists method of the ErrorJsonProxy.

    :param error_json_proxy: The error JSON proxy.
    :type error_json_proxy: ErrorJsonProxy
    '''

    # Check if the error exists.
    assert error_json_proxy.exists('test_error')
    assert error_json_proxy.exists('test_formatted_error')

# ** test_int: error_json_proxy_exists_not_found
def test_int_error_json_proxy_exists_not_found(error_json_proxy: ErrorJsonProxy):
    '''
    Test the exists method of the ErrorJsonProxy for a non-existent error.

    :param error_json_proxy: The error JSON proxy.
    :type error_json_proxy: ErrorJsonProxy
    '''

    # Check if the error exists.
    assert not error_json_proxy.exists('not_found')

# ** test_int: error_json_proxy_get
def test_int_error_json_proxy_get(
        error_json_proxy: ErrorJsonProxy,
    ):
    '''
    Test the get method of the ErrorJsonProxy.

    :param error_json_proxy: The error JSON proxy.
    :type error_json_proxy: ErrorJsonProxy
    :param errors: The dictionary of expected errors.
    :type errors: Dict[str, Error]
    '''

    # Get the error.
    test_error = error_json_proxy.get('test_error')
    test_formatted_error = error_json_proxy.get('test_formatted_error')

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

# ** test_int: error_json_proxy_get_not_found
def test_int_error_json_proxy_get_not_found(error_json_proxy: ErrorJsonProxy):
    '''
    Test the get method of the ErrorJsonProxy for a non-existent error.

    :param error_json_proxy: The error JSON proxy.
    :type error_json_proxy: ErrorJsonProxy
    '''
    
    # Get the error.
    test_error = error_json_proxy.get('not_found')

    # Check the error.
    assert not test_error

# ** test_int: error_json_proxy_save
def test_int_error_json_proxy_save(error_json_proxy: ErrorJsonProxy):
    '''
    Test the save method of the ErrorJsonProxy.

    :param error_json_proxy: The error JSON proxy.
    :type error_json_proxy: ErrorJsonProxy
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
    error_json_proxy.save(error)

    # Reload the error to verify the changes.
    modified_error = error_json_proxy.get('new_test_error')
    assert modified_error
    assert modified_error.id == 'new_test_error'
    assert modified_error.name == 'New Test Error'
    assert modified_error.error_code == 'NEW_TEST_ERROR_CODE'
    assert len(modified_error.message) == 1
    assert modified_error.message[0].lang == 'en'
    assert modified_error.message[0].text == 'This is a new test error message.'

# ** test_int: error_json_proxy_delete
def test_int_error_json_proxy_delete(error_json_proxy: ErrorJsonProxy):
    '''
    Test the delete method of the ErrorJsonProxy.

    :param error_json_proxy: The error JSON proxy.
    :type error_json_proxy: ErrorJsonProxy
    '''

    # Delete an existing error.
    error_json_proxy.delete('test_formatted_error')

    # Attempt to get the deleted error.
    deleted_error = error_json_proxy.get('test_formatted_error')

    # Check that the error is None.
    assert not deleted_error