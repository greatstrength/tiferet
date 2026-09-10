"""Tiferet Tests for Error Events"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events.error import (
    ErrorEvent,
    AddError,
    GetError,
    ListErrors,
    RenameError,
    SetErrorMessage,
    RemoveErrorMessage,
    RemoveError,
)
from tiferet.events.core import DomainEvent, TiferetError, a
from tiferet.domain import Error
from tiferet.interfaces import ErrorService
from tiferet.mappers import ErrorAggregate
from tiferet.blueprints.tester import use_tester

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

# *** testers

# ** tester: error_event_tester
class ErrorEventTester:
    '''
    Tests for the ErrorEvent base event shared by all error events.
    '''

    # * test: base_extends_domain_event
    def test_base_extends_domain_event(self):
        '''
        Test that ErrorEvent extends DomainEvent.
        '''

        # Assert the base event extends DomainEvent.
        assert issubclass(ErrorEvent, DomainEvent)

    # * test: concrete_events_extend_base
    def test_concrete_events_extend_base(self):
        '''
        Test that every concrete error event extends ErrorEvent.
        '''

        # Assert each concrete event extends the module base.
        for event_cls in (
            AddError,
            GetError,
            ListErrors,
            RenameError,
            SetErrorMessage,
            RemoveErrorMessage,
            RemoveError,
        ):
            assert issubclass(event_cls, ErrorEvent)

    # * test: service_injection
    def test_service_injection(self):
        '''
        Test that constructing an error event wires the shared service attribute.
        '''

        # Create a mock error service.
        service = mock.Mock(spec=ErrorService)

        # Assert the base and a concrete event both expose the injected service.
        assert ErrorEvent(error_service=service).error_service is service
        assert AddError(error_service=service).error_service is service

# ** tester: add_error_tester
@use_tester(
    type='domain_event',
    target_cls=AddError,
    dependencies={
        'error_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'ErrorService',
        },
    },
    sample_kwargs=dict(
        id='NEW_ERROR',
        name='New Error',
        message='This is a new error message.',
        lang='en_US',
        additional_messages={},
    ),
    required_params=['id', 'name', 'message'],
)
class AddErrorTester:
    '''
    Tests for AddError using the domain event test harness.
    '''

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

    # * test: success
    def test_success(self, test_ctx, mock_dependencies):
        '''
        Test adding a new error successfully.
        '''

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the error was created correctly.
        assert isinstance(result, Error)
        assert result.id == 'NEW_ERROR'
        assert result.name == 'New Error'
        assert any(msg.text == 'This is a new error message.' and msg.lang == 'en_US' for msg in result.message)

        # Assert the service was called correctly.
        mock_dependencies['error_service'].exists.assert_called_once_with('NEW_ERROR')
        mock_dependencies['error_service'].save.assert_called_once_with(result)

    # * test: with_additional_messages
    def test_with_additional_messages(self, test_ctx, mock_dependencies):
        '''
        Test adding a new error with additional language messages.
        '''

        # Execute with additional messages.
        result = test_ctx.handle(
            mock_dependencies,
            additional_messages={'es_ES': 'Este es un nuevo error.'},
        )

        # Assert both messages are present.
        assert len(result.message) == 2
        assert any(msg.text == 'This is a new error message.' and msg.lang == 'en_US' for msg in result.message)
        assert any(msg.text == 'Este es un nuevo error.' and msg.lang == 'es_ES' for msg in result.message)

    # * test: already_exists
    def test_already_exists(self, test_ctx, mock_dependencies):
        '''
        Test that adding an error with an existing ID raises an error.
        '''

        # Configure the service to report the ID already exists.
        mock_dependencies['error_service'].exists.return_value = True

        # Execute and expect an ERROR_ALREADY_EXISTS error.
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(mock_dependencies)

        # Assert the correct error code.
        assert exc_info.value.error_code == a.error.ERROR_ALREADY_EXISTS_ID

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        test_ctx.assert_missing_required_params()

# ** tester: get_error_tester
@use_tester(
    type='service_event',
    target_cls=GetError,
    dependencies={
        'error_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'ErrorService',
        },
    },
    sample_kwargs=dict(id='TEST_ERROR'),
    required_params=[],
    service_attr='error_service',
    not_found_error_code=a.error.ERROR_NOT_FOUND_ID,
)
class GetErrorTester:
    '''
    Tests for GetError using the service event test harness.
    '''

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

    # * test: found_in_repo
    def test_found_in_repo(self, test_ctx, mock_dependencies, error):
        '''
        Test retrieving an error found in the repository.
        '''

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the result matches the fixture.
        assert result == error
        mock_dependencies['error_service'].get.assert_called_once_with('TEST_ERROR')

    # * test: not_found_ignores_built_in_catalog
    def test_not_found_ignores_built_in_catalog(self, test_ctx, mock_dependencies):
        '''
        Test that a code present in CORE_DEFAULT_ERRORS but absent from the
        repository still raises ERROR_NOT_FOUND; the event never falls back
        to the built-in catalog.
        '''

        # Configure the service to return None (not in repo).
        mock_dependencies['error_service'].get.return_value = None

        # Execute with a code that exists in the built-in catalog.
        error_id = a.error.ERROR_NOT_FOUND_ID
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(mock_dependencies, id=error_id)

        # Assert the not-found error is raised rather than a default resolved.
        assert exc_info.value.error_code == a.error.ERROR_NOT_FOUND_ID
        mock_dependencies['error_service'].get.assert_called_once_with(error_id)

    # * test: not_found
    def test_not_found(self, test_ctx):
        '''Verify the configured not-found error when the service misses.'''

        test_ctx.assert_not_found()

# ** tester: list_errors_tester
@use_tester(
    type='domain_event',
    target_cls=ListErrors,
    dependencies={
        'error_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'ErrorService',
        },
    },
    sample_kwargs=dict(),
    required_params=[],
)
class ListErrorsTester:
    '''
    Tests for ListErrors using the domain event test harness.
    '''

    # * test: success
    def test_success(self, test_ctx, error):
        '''
        Test listing errors from the repository.
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Configure the mock to return a list with the error fixture.
        mock_dependencies['error_service'].list.return_value = [error]

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the result matches.
        assert result == [error]
        mock_dependencies['error_service'].list.assert_called_once()

# ** tester: rename_error_tester
@use_tester(
    type='service_event',
    target_cls=RenameError,
    dependencies={
        'error_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'ErrorService',
        },
    },
    sample_kwargs=dict(id='TEST_ERROR', new_name='Renamed Error'),
    required_params=['new_name'],
    service_attr='error_service',
    not_found_error_code=a.error.ERROR_NOT_FOUND_ID,
)
class RenameErrorTester:
    '''
    Tests for RenameError using the service event test harness.
    '''

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

    # * test: success
    def test_success(self, test_ctx, mock_dependencies, error):
        '''
        Test renaming an existing error successfully.
        '''

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the error was renamed.
        assert result == error
        assert error.name == 'Renamed Error'
        mock_dependencies['error_service'].get.assert_called_once_with('TEST_ERROR')
        mock_dependencies['error_service'].save.assert_called_once_with(error)

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        test_ctx.assert_missing_required_params()

    # * test: not_found
    def test_not_found(self, test_ctx):
        '''Verify the configured not-found error when the service misses.'''

        test_ctx.assert_not_found()

# ** tester: set_error_message_tester
@use_tester(
    type='service_event',
    target_cls=SetErrorMessage,
    dependencies={
        'error_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'ErrorService',
        },
    },
    sample_kwargs=dict(
        id='TEST_ERROR',
        message='Updated error message.',
        lang='en_US',
    ),
    required_params=['message'],
    service_attr='error_service',
    not_found_error_code=a.error.ERROR_NOT_FOUND_ID,
)
class SetErrorMessageTester:
    '''
    Tests for SetErrorMessage using the service event test harness.
    '''

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

    # * test: success
    def test_success(self, test_ctx, mock_dependencies, error):
        '''
        Test setting a message for an existing error successfully.
        '''

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the ID is returned and the message was updated.
        assert result == 'TEST_ERROR'
        assert any(msg.text == 'Updated error message.' and msg.lang == 'en_US' for msg in error.message)
        mock_dependencies['error_service'].get.assert_called_once_with('TEST_ERROR')
        mock_dependencies['error_service'].save.assert_called_once_with(error)

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        test_ctx.assert_missing_required_params()

    # * test: not_found
    def test_not_found(self, test_ctx):
        '''Verify the configured not-found error when the service misses.'''

        test_ctx.assert_not_found()

# ** tester: remove_error_message_tester
@use_tester(
    type='service_event',
    target_cls=RemoveErrorMessage,
    dependencies={
        'error_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'ErrorService',
        },
    },
    sample_kwargs=dict(id='TEST_ERROR', lang='es_ES'),
    required_params=[],
    service_attr='error_service',
    not_found_error_code=a.error.ERROR_NOT_FOUND_ID,
)
class RemoveErrorMessageTester:
    '''
    Tests for RemoveErrorMessage using the service event test harness.
    '''

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

    # * test: success
    def test_success(self, test_ctx, mock_dependencies, error):
        '''
        Test removing a message from an existing error successfully.
        '''

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the ID is returned and the message was removed.
        assert result == 'TEST_ERROR'
        assert all(msg.lang != 'es_ES' for msg in error.message)
        mock_dependencies['error_service'].get.assert_called_once_with('TEST_ERROR')
        mock_dependencies['error_service'].save.assert_called_once_with(error)

    # * test: no_messages_left
    def test_no_messages_left(self, test_ctx, mock_dependencies, error):
        '''
        Test that removing the last message raises NO_ERROR_MESSAGES.
        '''

        # Remove the es_ES message added by mock_dependencies so only en_US remains.
        error.remove_message('es_ES')

        # Execute removing the only remaining message (en_US).
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(mock_dependencies, lang='en_US')

        # Assert the correct error code.
        assert exc_info.value.error_code == a.error.NO_ERROR_MESSAGES_ID

    # * test: not_found
    def test_not_found(self, test_ctx):
        '''Verify the configured not-found error when the service misses.'''

        test_ctx.assert_not_found()

# ** tester: remove_error_tester
@use_tester(
    type='domain_event',
    target_cls=RemoveError,
    dependencies={
        'error_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'ErrorService',
        },
    },
    sample_kwargs=dict(id='TEST_ERROR'),
    required_params=['id'],
)
class RemoveErrorTester:
    '''
    Tests for RemoveError using the domain event test harness.
    '''

    # * test: success
    def test_success(self, test_ctx):
        '''
        Test removing an existing error successfully.
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the ID is returned and delete was called.
        assert result == 'TEST_ERROR'
        mock_dependencies['error_service'].delete.assert_called_once_with('TEST_ERROR')

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        mock_dependencies = test_ctx.mock_dependencies()

        test_ctx.assert_missing_required_params()

