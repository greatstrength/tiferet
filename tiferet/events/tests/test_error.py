"""Tiferet Tests for Error Commands"""

# *** imports

# ** core
from typing import List

# ** infra
import pytest
from unittest import mock

# ** app
from ..error import (
    Error,
    ErrorService, 
    AddError,
    GetError,
    ListErrors,
    RenameError,
    SetErrorMessage,
    RemoveErrorMessage,
    RemoveError,
    a
)
from ..settings import assets, TiferetError
from ...mappers import ErrorAggregate
from ...mappers.settings import Aggregate

# *** fixtures
@pytest.fixture
def error() -> Error:
    '''
    Fixture to create a sample Error instance.

    :return: A sample Error instance.
    :rtype: Error
    '''

    # Return a sample Error aggregate.
    return Aggregate.new(
        ErrorAggregate,
        id='TEST_ERROR',
        name='Test Error',
        description='A detailed description of the test error.',
        message=[{
            'lang': 'en_US',
            'text': 'This is a test error message.'
        }]
    )

# ** fixture: default_errors
@pytest.fixture
def default_errors() -> List[Error]:
    '''
    Fixture to create a list of default Error instances.

    :return: A list of default Error instances.
    :rtype: List[Error]
    '''

    # Return a list of default Error aggregates.
    return [
        Aggregate.new(ErrorAggregate, **data) for data in a.DEFAULT_ERRORS.values()
    ]

# ** fixture: error_repo_mock
@pytest.fixture
def error_service_mock() -> mock.Mock:
    '''
    Fixture to create a mocked ErrorService.

    :return: A mocked ErrorService.
    :rtype: mock.Mock
    '''

    # Create and return the mock.
    return mock.Mock(spec=ErrorService)

# ** fixture: add_error_command
@pytest.fixture
def add_error_command(error_service_mock: mock.Mock) -> AddError:
    '''
    Fixture to create an AddError command instance with a mocked ErrorService.

    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :return: The AddError command instance.
    :rtype: AddError
    '''

    # Return the AddError command with the mocked repository.
    return AddError(error_service=error_service_mock)

# ** fixture: get_error_command
@pytest.fixture
def get_error_command(error_service_mock: mock.Mock) -> GetError:
    '''
    Fixture to create a GetError command instance with a mocked ErrorService.

    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :return: The GetError command instance.
    :rtype: GetError
    '''

    # Return the GetError command with the mocked repository.
    return GetError(error_service=error_service_mock)

# ** fixture: list_errors_command
@pytest.fixture
def list_errors_command(error_service_mock: mock.Mock) -> ListErrors:
    '''
    Fixture to create a ListErrors command instance with a mocked ErrorService.

    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :return: The ListErrors command instance.
    :rtype: ListErrors
    '''

    # Return the ListErrors command with the mocked repository.
    return ListErrors(error_service=error_service_mock)

# ** fixture: rename_error_command
@pytest.fixture
def rename_error_command(error_service_mock: mock.Mock) -> RenameError:
    '''
    Fixture to create a RenameError command instance with a mocked ErrorService.

    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :return: The RenameError command instance.
    :rtype: RenameError
    '''

    # Return the RenameError command with the mocked repository.
    return RenameError(error_service=error_service_mock)

# ** fixture: set_error_message_command
@pytest.fixture
def set_error_message_command(error_service_mock: mock.Mock) -> SetErrorMessage:
    '''
    Fixture to create a SetErrorMessage command instance with a mocked ErrorService.

    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :return: The SetErrorMessage command instance.
    :rtype: SetErrorMessage
    '''

    # Return the SetErrorMessage command with the mocked repository.
    return SetErrorMessage(error_service=error_service_mock)

# ** fixture: remove_error_message_command
@pytest.fixture
def remove_error_message_command(error_service_mock: mock.Mock) -> RemoveErrorMessage:
    '''
    Fixture to create a RemoveErrorMessage command instance with a mocked ErrorService.

    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :return: The RemoveErrorMessage command instance.
    :rtype: RemoveErrorMessage
    '''

    # Return the RemoveErrorMessage command with the mocked repository.
    return RemoveErrorMessage(error_service=error_service_mock)

# ** fixture: remove_error_command
@pytest.fixture
def remove_error_command(error_service_mock: mock.Mock) -> RemoveError:
    '''
    Fixture to create a RemoveError command instance with a mocked ErrorService.

    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :return: The RemoveError command instance.
    :rtype: RemoveError
    '''

    # Return the RemoveError command with the mocked repository.
    return RemoveError(error_service=error_service_mock)

# *** tests

# ** test: add_error_success
def test_add_error_success(add_error_command: AddError, error_service_mock: mock.Mock):
    '''
    Test adding a new error successfully.

    :param add_error_command: The AddError command instance.
    :type add_error_command: AddError
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    '''

    # Arrange the parameters for adding an error.
    error_id = 'NEW_ERROR'
    error_name = 'New Error'
    error_message = 'This is a new error message.'
    lang = 'en_US'
    additional_messages = [{'lang': 'es_ES', 'text': 'Este es un mensaje de error nuevo.'}]

    # Configure the mock to indicate the error does not exist.
    error_service_mock.exists.return_value = False

    # Act to add the new error.
    result = add_error_command.execute(
        id=error_id,
        name=error_name,
        message=error_message,
        lang=lang,
        additional_messages=additional_messages
    )

    # Assert that the error was added correctly.
    assert result.id == error_id, 'Error ID does not match.'
    assert result.name == error_name, 'Error name does not match.'
    assert any(msg.text == error_message and msg.lang == lang for msg in result.message), 'Primary error message does not match.'
    assert any(msg.text == 'Este es un mensaje de error nuevo.' and msg.lang == 'es_ES' for msg in result.message), 'Additional error message does not match.'
    error_service_mock.exists.assert_called_once_with(error_id), 'Exists method was not called correctly.'
    error_service_mock.save.assert_called_once_with(result), 'Save method was not called correctly.'

# * test: add_error_already_invalid_parameters
def test_add_error_already_invalid_parameters(add_error_command: AddError):
    '''
    Test adding an error with invalid parameters.

    :param add_error_command: The AddError command instance.
    :type add_error_command: AddError
    '''

    # Test with empty ID.
    with pytest.raises(TiferetError) as exc_info:
        add_error_command.execute(
            id='',
            name='Some Name',
            message='Some message.'
        )
    assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
    assert exc_info.value.kwargs.get('parameter') == 'id'
    assert exc_info.value.kwargs.get('command') == 'AddError'

    # Test with empty name.
    with pytest.raises(TiferetError) as exc_info:
        add_error_command.execute(
            id='VALID_ID',
            name='',
            message='Some message.'
        )
    assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
    assert exc_info.value.kwargs.get('parameter') == 'name'
    assert exc_info.value.kwargs.get('command') == 'AddError'

    # Test with empty message.
    with pytest.raises(TiferetError) as exc_info:
        add_error_command.execute(
            id='VALID_ID',
            name='Some Name',
            message=''
        )
    assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
    assert exc_info.value.kwargs.get('parameter') == 'message'
    assert exc_info.value.kwargs.get('command') == 'AddError'

# ** test: add_error_already_exists
def test_add_error_already_exists(add_error_command: AddError, error_service_mock: mock.Mock):
    '''
    Test adding an error that already exists.

    :param add_error_command: The AddError command instance.
    :type add_error_command: AddError
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    '''

    # Arrange the parameters for adding an error.
    error_id = 'EXISTING_ERROR'
    error_name = 'Existing Error'
    error_message = 'This error already exists.'
    lang = 'en_US'
    additional_messages = []

    # Configure the mock to indicate the error already exists.
    error_service_mock.exists.return_value = True

    # Act & Assert that adding the error raises the expected exception.
    with pytest.raises(TiferetError) as exc_info:
        add_error_command.execute(
            id=error_id,
            name=error_name,
            message=error_message,
            lang=lang,
            additional_messages=additional_messages
        )

    # Verify the exception message.
    assert exc_info.value.error_code == a.const.ERROR_ALREADY_EXISTS_ID, 'Error code does not match.'
    assert exc_info.value.kwargs.get('id') == error_id, 'Error ID in exception does not match.'
    assert f'An error with ID {error_id} already exists.' in str(exc_info.value), 'Exception message does not match.'
    error_service_mock.exists.assert_called_once_with(error_id), 'Exists method was not called correctly.'

# ** test: get_error_found_in_repo
def test_get_error_found_in_repo(error: Error, error_service_mock: mock.Mock, get_error_command: GetError):
    '''
    Test retrieving an error that exists in the repository.

    :param error: The sample Error instance.
    :type error: Error
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :param get_error_command: The GetError command instance.
    :type get_error_command: GetError
    '''

    # Arrange the mock to return the error.
    error_id = 'TEST_ERROR'
    error_service_mock.get.return_value = error

    # Act to retrieve the error.
    result = get_error_command.execute(id=error_id)

    # Assert the result matches the expected error.
    assert result == error
    error_service_mock.get.assert_called_once_with(error_id)

# ** test: get_error_found_in_defaults
def test_get_error_found_in_defaults(error_service_mock: mock.Mock, get_error_command: GetError):
    '''
    Test retrieving an error that exists in the default errors.

    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :param get_error_command: The GetError command instance.
    :type get_error_command: GetError
    '''

    # Arrange the mock to return None.
    error_id = a.ERROR_NOT_FOUND_ID
    error_service_mock.get.return_value = None

    # Act to retrieve the error.
    result = get_error_command.execute(id=error_id, include_defaults=True)

    # Assert the result matches the expected default error.
    expected_error = Aggregate.new(ErrorAggregate, **a.DEFAULT_ERRORS.get(error_id))
    assert result == expected_error
    error_service_mock.get.assert_called_once_with(error_id)

# ** test: get_error_not_found
def test_get_error_not_found(error_service_mock: mock.Mock, get_error_command: GetError):
    '''
    Test retrieving an error that does not exist in the repository or defaults.

    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :param get_error_command: The GetError command instance.
    :type get_error_command: GetError
    '''

    # Arrange the mock to return None.
    error_id = 'NON_EXISTENT_ERROR'
    error_service_mock.get.return_value = None

    # Act & Assert that retrieving the error raises the expected exception.
    with pytest.raises(TiferetError) as exc_info:
        get_error_command.execute(id=error_id, include_defaults=False)

    # Verify the exception message.
    assert exc_info.value.error_code == a.ERROR_NOT_FOUND_ID
    assert exc_info.value.kwargs.get('id') == error_id
    assert f'Error not found: {error_id}.' in str(exc_info.value)
    error_service_mock.get.assert_called_once_with(error_id)

# ** test: list_errors_success
def test_list_errors_success(list_errors_command: ListErrors, error_service_mock: mock.Mock, error: Error):
    '''
    Test listing all errors successfully.

    :param list_errors_command: The ListErrors command instance.
    :type list_errors_command: ListErrors
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :param error: The sample Error instance.
    :type error: Error
    '''

    # Arrange the mock to return a list of errors.
    error_service_mock.list.return_value = [error]

    # Act to list the errors.
    result = list_errors_command.execute()

    # Assert the result matches the expected list of errors.
    assert result == [error], 'The list of errors does not match the expected result.'
    error_service_mock.list.assert_called_once(), 'List method was not called correctly.'

# ** test: list_errors_with_defaults
def test_list_errors_with_defaults(list_errors_command: ListErrors, error_service_mock: mock.Mock, default_errors: List[Error]):
    '''
    Test listing all errors including default errors.

    :param list_errors_command: The ListErrors command instance.
    :type list_errors_command: ListErrors
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :param default_errors: The list of default Error instances.
    :type default_errors: List[Error]
    '''

    # Arrange the mock to return a list of errors.
    existing_error = Aggregate.new(
        ErrorAggregate,
        id='EXISTING_ERROR',
        name='Existing Error',
        description='An existing error in the repository.',
        message=[{
            'lang': 'en_US',
            'text': 'This is an existing error message.'
        }]
    )
    error_service_mock.list.return_value = [existing_error]

    # Act to list the errors including defaults.
    result = list_errors_command.execute(include_defaults=True)

    # Assert the result includes both existing and default errors.
    expected_errors = [existing_error] + default_errors
    assert len(result) == len(expected_errors), 'The number of errors does not match the expected result.'
    for error in expected_errors:
        assert error in result, f'Error {error.id} not found in the result.'
    error_service_mock.list.assert_called_once(), 'List method was not called correctly.'

# ** test: list_errors_with_defaults_and_override
def test_list_errors_with_defaults_and_override(list_errors_command: ListErrors, error_service_mock: mock.Mock, default_errors: List[Error]):
    '''
    Test listing all errors including default errors with an override.

    :param list_errors_command: The ListErrors command instance.
    :type list_errors_command: ListErrors
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :param default_errors: The list of default Error instances.
    :type default_errors: List[Error]
    '''

    # Arrange the mock to return a list of errors that overrides a default error.
    overriding_error = Aggregate.new(
        ErrorAggregate,
        id=a.const.ERROR_NOT_FOUND_ID,
        name='Overriding Not Found Error',
        description='An overriding error for not found.',
        message=[{
            'lang': 'en_US',
            'text': 'This is an overridden not found error message.'
        }]
    )
    error_service_mock.list.return_value = [overriding_error]

    # Act to list the errors including defaults.
    result = list_errors_command.execute(include_defaults=True)

    # Assert the result includes the overriding error instead of the default.
    expected_errors = [overriding_error] + [
    error for error in default_errors if error.id != a.const.ERROR_NOT_FOUND_ID
    ]
    assert len(result) == len(expected_errors), 'The number of errors does not match the expected result.'
    for error in expected_errors:
        assert error in result, f'Error {error.id} not found in the result.'
    error_service_mock.list.assert_called_once(), 'List method was not called correctly.'   

# ** test: list_errors_no_errors_and_with_defaults
def test_list_errors_no_errors_and_defaults(list_errors_command: ListErrors, error_service_mock: mock.Mock, default_errors: List[Error]):
    '''
    Test listing all errors when there are no errors in the repository and only defaults.

    :param list_errors_command: The ListErrors command instance.
    :type list_errors_command: ListErrors
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    '''

    # Arrange the mock to return an empty list.
    error_service_mock.list.return_value = []

    # Act to list the errors including defaults.
    result = list_errors_command.execute(include_defaults=True)

    # Assert the result is an empty list containing only default errors.
    expected_errors = default_errors
    assert len(result) == len(expected_errors), 'The number of errors does not match the expected result.'
    for error in expected_errors:
        assert error in result, f'Error {error.id} not found in the result.'
    error_service_mock.list.assert_called_once(), 'List method was not called correctly.'

# ** test: rename_error_success
def test_rename_error_success(rename_error_command: RenameError, error_service_mock: mock.Mock, error: Error):
    '''
    Test renaming an existing error successfully.

    :param rename_error_command: The RenameError command instance.
    :type rename_error_command: RenameError
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :param error: The sample Error instance.
    :type error: Error
    '''

    # Arrange the parameters for renaming an error.
    error_id = error.id
    new_name = 'Renamed Test Error'

    # Configure the mock to return the existing error.
    error_service_mock.get.return_value = error

    # Act to rename the error.
    rename_error_command.execute(
        id=error_id,
        new_name=new_name
    )

    # Assert that the error was renamed correctly.
    assert error.name == new_name, 'Error name was not updated correctly.'
    error_service_mock.get.assert_called_once_with(error_id), 'Get method was not called correctly.'
    error_service_mock.save.assert_called_once_with(error), 'Save method was not called correctly.'

# ** test: rename_error_empty_name
def test_rename_error_empty_name(rename_error_command: RenameError, error_service_mock: mock.Mock, error: Error):
    '''
    Test renaming an error with an empty new name.

    :param rename_error_command: The RenameError command instance.
    :type rename_error_command: RenameError
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :param error: The sample Error instance.
    :type error: Error
    '''

    # Arrange the parameters for renaming an error.
    error_id = error.id
    new_name = ''

    # Configure the mock to return the existing error.
    error_service_mock.get.return_value = error

    # Act & Assert that renaming the error raises the expected exception.
    with pytest.raises(TiferetError) as exc_info:
        rename_error_command.execute(
            id=error_id,
            new_name=new_name
        )

    # Verify the exception message.
    assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID, 'Error code does not match.'
    assert exc_info.value.kwargs.get('parameter') == 'new_name', 'Parameter in exception does not match.'
    assert exc_info.value.kwargs.get('command') == 'RenameError', 'Command in exception does not match.'

# ** test: rename_error_not_found
def test_rename_error_not_found(rename_error_command: RenameError, error_service_mock: mock.Mock):
    '''
    Test renaming an error that does not exist.

    :param rename_error_command: The RenameError command instance.
    :type rename_error_command: RenameError
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    '''

    # Arrange the parameters for renaming an error.
    error_id = 'NON_EXISTENT_ERROR'
    new_name = 'Renamed Error'

    # Configure the mock to return None (error not found).
    error_service_mock.get.return_value = None

    # Act & Assert that renaming the error raises the expected exception.
    with pytest.raises(TiferetError) as exc_info:
        rename_error_command.execute(
            id=error_id,
            new_name=new_name
        )

    # Verify the exception message.
    assert exc_info.value.error_code == a.const.ERROR_NOT_FOUND_ID, 'Error code does not match.'
    assert exc_info.value.kwargs.get('id') == error_id, 'Error ID in exception does not match.'
    error_service_mock.get.assert_called_once_with(error_id), 'Get method was not called correctly.'

# ** test: set_error_message_success
def test_set_error_message_success(set_error_message_command: SetErrorMessage, error_service_mock: mock.Mock, error: Error):
    '''
    Test setting a new message for an existing error successfully.

    :param set_error_message_command: The SetErrorMessage command instance.
    :type set_error_message_command: SetErrorMessage
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :param error: The sample Error instance.
    :type error: Error
    '''

    # Arrange the parameters for setting a new error message.
    error_id = error.id
    new_message = 'This is an updated test error message.'
    lang = 'en_US'

    # Configure the mock to return the existing error.
    error_service_mock.get.return_value = error

    # Act to set the new error message.
    error_id = set_error_message_command.execute(
        id=error_id,
        message=new_message,
        lang=lang
    )

    # Assert that the error message was updated correctly.
    assert error_id == error.id, 'Returned error ID does not match.'
    assert any(msg.text == new_message and msg.lang == lang for msg in error.message), 'Error message was not updated correctly.'
    error_service_mock.get.assert_called_once_with(error_id), 'Get method was not called correctly.'
    error_service_mock.save.assert_called_once_with(error), 'Save method was not called correctly.'

# ** test: set_error_message_empty_message
def test_set_error_message_empty_message(set_error_message_command: SetErrorMessage, error_service_mock: mock.Mock, error: Error):
    '''
    Test setting an empty message for an existing error.

    :param set_error_message_command: The SetErrorMessage command instance.
    :type set_error_message_command: SetErrorMessage
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :param error: The sample Error instance.
    :type error: Error
    '''

    # Arrange the parameters for setting a new error message.
    error_id = error.id
    new_message = ''
    lang = 'en_US'

    # Configure the mock to return the existing error.
    error_service_mock.get.return_value = error

    # Act & Assert that setting the empty message raises the expected exception.
    with pytest.raises(TiferetError) as exc_info:
        set_error_message_command.execute(
            id=error_id,
            message=new_message,
            lang=lang
        )

    # Verify the exception message.
    assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID, 'Error code does not match.'
    assert exc_info.value.kwargs.get('parameter') == 'message', 'Parameter in exception does not match.'
    assert exc_info.value.kwargs.get('command') == 'SetErrorMessage', 'Command in exception does not match.'

# ** test: set_error_message_not_found
def test_set_error_message_not_found(set_error_message_command: SetErrorMessage, error_service_mock: mock.Mock):
    '''
    Test setting a message for an error that does not exist.

    :param set_error_message_command: The SetErrorMessage command instance.
    :type set_error_message_command: SetErrorMessage
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    '''

    # Arrange the parameters for setting a new error message.
    error_id = 'NON_EXISTENT_ERROR'
    new_message = 'This is a new message.'
    lang = 'en_US'

    # Configure the mock to return None (error not found).
    error_service_mock.get.return_value = None

    # Act & Assert that setting the message raises the expected exception.
    with pytest.raises(TiferetError) as exc_info:
        set_error_message_command.execute(
            id=error_id,
            message=new_message,
            lang=lang
        )

    # Verify the exception message.
    assert exc_info.value.error_code == a.const.ERROR_NOT_FOUND_ID, 'Error code does not match.'
    assert exc_info.value.kwargs.get('id') == error_id, 'Error ID in exception does not match.'
    error_service_mock.get.assert_called_once_with(error_id), 'Get method was not called correctly.'

# ** test: remove_error_message_success
def test_remove_error_message_success(remove_error_message_command: RemoveErrorMessage, error_service_mock: mock.Mock, error: Error):
    '''
    Test removing a message for an existing error successfully.

    :param remove_error_message_command: The RemoveErrorMessage command instance.
    :type remove_error_message_command: RemoveErrorMessage
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :param error: The sample Error instance.
    :type error: Error
    '''

    # Add a new message to ensure there is something to remove.
    lang_to_remove = 'es_ES'
    error.set_message(lang_to_remove, 'Este es un mensaje de error de prueba.')

    # Configure the mock to return the existing error.
    error_service_mock.get.return_value = error

    # Act to remove the error message.
    error_id = remove_error_message_command.execute(
        id=error.id,
        lang=lang_to_remove
    )

    # Assert that the error message was removed correctly.
    assert error_id == error.id, 'Returned error ID does not match.'
    assert all(msg.lang != lang_to_remove for msg in error.message), 'Error message was not removed correctly.'
    error_service_mock.get.assert_called_once_with(error_id), 'Get method was not called correctly.'
    error_service_mock.save.assert_called_once_with(error), 'Save method was not called correctly.'

# ** test: remove_error_message_not_found
def test_remove_error_message_not_found(remove_error_message_command: RemoveErrorMessage, error_service_mock: mock.Mock):
    '''
    Test removing a message for an error that does not exist.

    :param remove_error_message_command: The RemoveErrorMessage command instance.
    :type remove_error_message_command: RemoveErrorMessage
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    '''

    # Arrange the parameters for removing an error message.
    error_id = 'NON_EXISTENT_ERROR'
    lang_to_remove = 'en_US'

    # Configure the mock to return None (error not found).
    error_service_mock.get.return_value = None

    # Act & Assert that removing the message raises the expected exception.
    with pytest.raises(TiferetError) as exc_info:
        remove_error_message_command.execute(
            id=error_id,
            lang=lang_to_remove
        )

    # Verify the exception message.
    assert exc_info.value.error_code == a.const.ERROR_NOT_FOUND_ID, 'Error code does not match.'
    assert exc_info.value.kwargs.get('id') == error_id, 'Error ID in exception does not match.'
    error_service_mock.get.assert_called_once_with(error_id), 'Get method was not called correctly.'

# ** test: remove_error_message_no_error_messages
def test_remove_error_message_no_error_messages(remove_error_message_command: RemoveErrorMessage, error_service_mock: mock.Mock, error: Error):
    '''
    Test removing a message when no messages exist for the error.

    :param remove_error_message_command: The RemoveErrorMessage command instance.
    :type remove_error_message_command: RemoveErrorMessage
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :param error: The sample Error instance.
    :type error: Error
    '''

    # Prepare the input parameters to remove the only existing message.
    lang_to_remove = 'en_US'

    # Configure the mock to return the existing error.
    error_service_mock.get.return_value = error

    # Act & Assert that removing the message raises the expected exception.
    with pytest.raises(TiferetError) as exc_info:
        remove_error_message_command.execute(
            id=error.id,
            lang=lang_to_remove
        )

    # Verify the exception message.
    assert exc_info.value.error_code == a.const.NO_ERROR_MESSAGES_ID, 'Error code does not match.'
    assert exc_info.value.kwargs.get('id') == error.id, 'Error ID in exception does not match.'
    error_service_mock.get.assert_called_once_with(error.id), 'Get method was not called correctly.'

# ** test: remove_error_success
def test_remove_error_success(remove_error_command: RemoveError, error_service_mock: mock.Mock, error: Error):
    '''
    Test removing an existing error successfully.

    :param remove_error_command: The RemoveError command instance.
    :type remove_error_command: RemoveError
    :param error_service_mock: The mocked ErrorService.
    :type error_service_mock: mock.Mock
    :param error: The sample Error instance.
    :type error: Error
    '''

    # Arrange the parameters for removing an error.
    error_id = error.id

    # Act to remove the error.
    removed_error_id = remove_error_command.execute(
        id=error_id
    )

    # Assert that the error was removed correctly.
    assert removed_error_id == error_id, 'Returned error ID does not match.'
    error_service_mock.delete.assert_called_once_with(error_id), 'Delete method was not called correctly.'

# ** test: remove_error_invalid_parameters
def test_remove_error_invalid_parameters(remove_error_command: RemoveError):
    '''
    Test removing an error with invalid parameters.

    :param remove_error_command: The RemoveError command instance.
    :type remove_error_command: RemoveError
    '''

    # Test with empty ID.
    with pytest.raises(TiferetError) as exc_info:
        remove_error_command.execute(
            id=''
        )
    assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
    assert exc_info.value.kwargs.get('parameter') == 'id'
    assert exc_info.value.kwargs.get('command') == 'RemoveError'
