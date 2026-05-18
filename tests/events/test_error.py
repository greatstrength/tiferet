"""Tiferet Tests for Error Events"""

# *** imports

# ** core
from typing import List

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events.error import (
    AddError,
    GetError,
    ListErrors,
    RenameError,
    SetErrorMessage,
    RemoveErrorMessage,
    RemoveError,
)
from tiferet.events.settings import DomainEvent, TiferetError, a
from tiferet.domain import Error
from tiferet.interfaces import ErrorService
from tiferet.mappers import ErrorAggregate
from tiferet.testing import DomainEventTestBase, ServiceEventTestBase

# *** fixtures

# ** fixture: error
@pytest.fixture
def error() -> ErrorAggregate:
    '''
    A sample Error aggregate for event tests.

    :return: An ErrorAggregate instance.
    :rtype: ErrorAggregate
    '''

    # Create a sample error aggregate.
    return ErrorAggregate(
        id='TEST_ERROR',
        name='Test Error',
        message=[{
            'lang': 'en_US',
            'text': 'This is a test error message.'
        }]
    )

# ** fixture: default_errors
@pytest.fixture
def default_errors() -> List[Error]:
    '''
    A list of default Error instances from constants.

    :return: A list of default Error instances.
    :rtype: List[Error]
    '''

    # Return a list of default Error aggregates.
    return [
        ErrorAggregate(**data) for data in a.DEFAULT_ERRORS.values()
    ]

# *** tests

# ** test: TestAddError
class TestAddError(DomainEventTestBase):
    '''
    Tests for AddError using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = AddError

    # * attribute: dependencies
    dependencies = {'error_service': ErrorService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='NEW_ERROR',
        name='New Error',
        message='This is a new error message.',
        lang='en_US',
        additional_messages=[],
    )

    # * attribute: required_params
    required_params = ['id', 'name', 'message']

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self) -> dict:
        '''
        Override to pre-configure exists to return False.
        '''

        # Create the mock error service.
        service = mock.Mock(spec=ErrorService)
        service.exists.return_value = False
        return {'error_service': service}

    # * method: test_success
    def test_success(self, mock_dependencies):
        '''
        Test adding a new error successfully.
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the error was created correctly.
        assert isinstance(result, Error)
        assert result.id == 'NEW_ERROR'
        assert result.name == 'New Error'
        assert any(msg.text == 'This is a new error message.' and msg.lang == 'en_US' for msg in result.message)

        # Assert the service was called correctly.
        mock_dependencies['error_service'].exists.assert_called_once_with('NEW_ERROR')
        mock_dependencies['error_service'].save.assert_called_once_with(result)

    # * method: test_with_additional_messages
    def test_with_additional_messages(self, mock_dependencies):
        '''
        Test adding a new error with additional language messages.
        '''

        # Execute with additional messages.
        result = self.handle(
            mock_dependencies,
            additional_messages=[{'lang': 'es_ES', 'text': 'Este es un nuevo error.'}],
        )

        # Assert both messages are present.
        assert len(result.message) == 2
        assert any(msg.text == 'This is a new error message.' and msg.lang == 'en_US' for msg in result.message)
        assert any(msg.text == 'Este es un nuevo error.' and msg.lang == 'es_ES' for msg in result.message)

    # * method: test_already_exists
    def test_already_exists(self, mock_dependencies):
        '''
        Test that adding an error with an existing ID raises an error.
        '''

        # Configure the service to report the ID already exists.
        mock_dependencies['error_service'].exists.return_value = True

        # Execute and expect an ERROR_ALREADY_EXISTS error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies)

        # Assert the correct error code.
        assert exc_info.value.error_code == a.const.ERROR_ALREADY_EXISTS_ID


# ** test: TestGetError
class TestGetError(ServiceEventTestBase):
    '''
    Tests for GetError using the service event test harness.
    '''

    # * attribute: event_cls
    event_cls = GetError

    # * attribute: dependencies
    dependencies = {'error_service': ErrorService}

    # * attribute: service_attr
    service_attr = 'error_service'

    # * attribute: not_found_error_code
    not_found_error_code = a.const.ERROR_NOT_FOUND_ID

    # * attribute: sample_kwargs
    sample_kwargs = dict(id='TEST_ERROR')

    # * attribute: required_params
    required_params = []

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, error) -> dict:
        '''
        Override to pre-configure get to return the error fixture.
        '''

        # Create the mock error service.
        service = mock.Mock(spec=ErrorService)
        service.get.return_value = error
        return {'error_service': service}

    # * method: test_found_in_repo
    def test_found_in_repo(self, mock_dependencies, error):
        '''
        Test retrieving an error found in the repository.
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the result matches the fixture.
        assert result == error
        mock_dependencies['error_service'].get.assert_called_once_with('TEST_ERROR')

    # * method: test_found_in_defaults
    def test_found_in_defaults(self, mock_dependencies):
        '''
        Test retrieving an error from built-in defaults when not in repository.
        '''

        # Configure the service to return None (not in repo).
        mock_dependencies['error_service'].get.return_value = None

        # Execute with include_defaults and a known default error ID.
        error_id = a.const.ERROR_NOT_FOUND_ID
        result = self.handle(
            mock_dependencies,
            id=error_id,
            include_defaults=True,
        )

        # Assert the result matches the expected default error.
        expected = ErrorAggregate(**a.DEFAULT_ERRORS.get(error_id))
        assert result == expected
        mock_dependencies['error_service'].get.assert_called_once_with(error_id)


# ** test: TestListErrors
class TestListErrors(DomainEventTestBase):
    '''
    Tests for ListErrors using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = ListErrors

    # * attribute: dependencies
    dependencies = {'error_service': ErrorService}

    # * attribute: sample_kwargs
    sample_kwargs = dict()

    # * attribute: required_params
    required_params = []

    # * method: test_success
    def test_success(self, mock_dependencies, error):
        '''
        Test listing errors from the repository.
        '''

        # Configure the mock to return a list with the error fixture.
        mock_dependencies['error_service'].list.return_value = [error]

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the result matches.
        assert result == [error]
        mock_dependencies['error_service'].list.assert_called_once()

    # * method: test_with_defaults
    def test_with_defaults(self, mock_dependencies, default_errors):
        '''
        Test listing errors including default errors.
        '''

        # Configure the mock to return a list with an additional error.
        existing_error = ErrorAggregate(
            id='EXISTING_ERROR',
            name='Existing Error',
            message=[{
                'lang': 'en_US',
                'text': 'This is an existing error message.'
            }]
        )
        mock_dependencies['error_service'].list.return_value = [existing_error]

        # Execute with include_defaults.
        result = self.handle(mock_dependencies, include_defaults=True)

        # Assert the result includes both existing and default errors.
        expected_errors = [existing_error] + default_errors
        assert len(result) == len(expected_errors)
        for err in expected_errors:
            assert err in result

    # * method: test_with_defaults_and_override
    def test_with_defaults_and_override(self, mock_dependencies, default_errors):
        '''
        Test listing errors with a repository error that overrides a default.
        '''

        # Create a repo error that overrides the default ERROR_NOT_FOUND.
        overriding_error = ErrorAggregate(
            id=a.const.ERROR_NOT_FOUND_ID,
            name='Overriding Not Found Error',
            message=[{
                'lang': 'en_US',
                'text': 'This is an overridden not found error message.'
            }]
        )
        mock_dependencies['error_service'].list.return_value = [overriding_error]

        # Execute with include_defaults.
        result = self.handle(mock_dependencies, include_defaults=True)

        # Assert the override replaces the default.
        expected_errors = [overriding_error] + [
            err for err in default_errors if err.id != a.const.ERROR_NOT_FOUND_ID
        ]
        assert len(result) == len(expected_errors)
        for err in expected_errors:
            assert err in result

    # * method: test_no_errors_with_defaults
    def test_no_errors_with_defaults(self, mock_dependencies, default_errors):
        '''
        Test listing errors when repository is empty and only defaults exist.
        '''

        # Configure the mock to return an empty list.
        mock_dependencies['error_service'].list.return_value = []

        # Execute with include_defaults.
        result = self.handle(mock_dependencies, include_defaults=True)

        # Assert only default errors are returned.
        assert len(result) == len(default_errors)
        for err in default_errors:
            assert err in result


# ** test: TestRenameError
class TestRenameError(ServiceEventTestBase):
    '''
    Tests for RenameError using the service event test harness.
    '''

    # * attribute: event_cls
    event_cls = RenameError

    # * attribute: dependencies
    dependencies = {'error_service': ErrorService}

    # * attribute: service_attr
    service_attr = 'error_service'

    # * attribute: not_found_error_code
    not_found_error_code = a.const.ERROR_NOT_FOUND_ID

    # * attribute: sample_kwargs
    sample_kwargs = dict(id='TEST_ERROR', new_name='Renamed Error')

    # * attribute: required_params
    required_params = ['new_name']

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, error) -> dict:
        '''
        Override to pre-configure get to return the error fixture.
        '''

        # Create the mock error service.
        service = mock.Mock(spec=ErrorService)
        service.get.return_value = error
        return {'error_service': service}

    # * method: test_success
    def test_success(self, mock_dependencies, error):
        '''
        Test renaming an existing error successfully.
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the error was renamed.
        assert result == error
        assert error.name == 'Renamed Error'
        mock_dependencies['error_service'].get.assert_called_once_with('TEST_ERROR')
        mock_dependencies['error_service'].save.assert_called_once_with(error)


# ** test: TestSetErrorMessage
class TestSetErrorMessage(ServiceEventTestBase):
    '''
    Tests for SetErrorMessage using the service event test harness.
    '''

    # * attribute: event_cls
    event_cls = SetErrorMessage

    # * attribute: dependencies
    dependencies = {'error_service': ErrorService}

    # * attribute: service_attr
    service_attr = 'error_service'

    # * attribute: not_found_error_code
    not_found_error_code = a.const.ERROR_NOT_FOUND_ID

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='TEST_ERROR',
        message='Updated error message.',
        lang='en_US',
    )

    # * attribute: required_params
    required_params = ['message']

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, error) -> dict:
        '''
        Override to pre-configure get to return the error fixture.
        '''

        # Create the mock error service.
        service = mock.Mock(spec=ErrorService)
        service.get.return_value = error
        return {'error_service': service}

    # * method: test_success
    def test_success(self, mock_dependencies, error):
        '''
        Test setting a message for an existing error successfully.
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the ID is returned and the message was updated.
        assert result == 'TEST_ERROR'
        assert any(msg.text == 'Updated error message.' and msg.lang == 'en_US' for msg in error.message)
        mock_dependencies['error_service'].get.assert_called_once_with('TEST_ERROR')
        mock_dependencies['error_service'].save.assert_called_once_with(error)


# ** test: TestRemoveErrorMessage
class TestRemoveErrorMessage(ServiceEventTestBase):
    '''
    Tests for RemoveErrorMessage using the service event test harness.
    '''

    # * attribute: event_cls
    event_cls = RemoveErrorMessage

    # * attribute: dependencies
    dependencies = {'error_service': ErrorService}

    # * attribute: service_attr
    service_attr = 'error_service'

    # * attribute: not_found_error_code
    not_found_error_code = a.const.ERROR_NOT_FOUND_ID

    # * attribute: sample_kwargs
    sample_kwargs = dict(id='TEST_ERROR', lang='es_ES')

    # * attribute: required_params
    required_params = []

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, error) -> dict:
        '''
        Override to pre-configure get with an error that has two messages.
        '''

        # Add a second message so the remove succeeds.
        error.set_message('es_ES', 'Este es un mensaje de error de prueba.')

        # Create the mock error service.
        service = mock.Mock(spec=ErrorService)
        service.get.return_value = error
        return {'error_service': service}

    # * method: test_success
    def test_success(self, mock_dependencies, error):
        '''
        Test removing a message from an existing error successfully.
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the ID is returned and the message was removed.
        assert result == 'TEST_ERROR'
        assert all(msg.lang != 'es_ES' for msg in error.message)
        mock_dependencies['error_service'].get.assert_called_once_with('TEST_ERROR')
        mock_dependencies['error_service'].save.assert_called_once_with(error)

    # * method: test_no_messages_left
    def test_no_messages_left(self, mock_dependencies, error):
        '''
        Test that removing the last message raises NO_ERROR_MESSAGES.
        '''

        # Remove the es_ES message added by mock_dependencies so only en_US remains.
        error.remove_message('es_ES')

        # Execute removing the only remaining message (en_US).
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, lang='en_US')

        # Assert the correct error code.
        assert exc_info.value.error_code == a.const.NO_ERROR_MESSAGES_ID


# ** test: TestRemoveError
class TestRemoveError(DomainEventTestBase):
    '''
    Tests for RemoveError using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = RemoveError

    # * attribute: dependencies
    dependencies = {'error_service': ErrorService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(id='TEST_ERROR')

    # * attribute: required_params
    required_params = ['id']

    # * method: test_success
    def test_success(self, mock_dependencies):
        '''
        Test removing an existing error successfully.
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the ID is returned and delete was called.
        assert result == 'TEST_ERROR'
        mock_dependencies['error_service'].delete.assert_called_once_with('TEST_ERROR')
