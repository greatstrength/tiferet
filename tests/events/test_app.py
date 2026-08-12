"""Tiferet App Commands Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events.app import (
    AppEvent,
    AddAppSession,
    GetAppSession,
    UpdateAppSession,
    ListAppSessions,
    RemoveAppSession,
    SetAppConstants,
    SetServiceDependency,
    RemoveServiceDependency,
)
from tiferet.events.core import DomainEvent, TiferetError, a
from tiferet.domain import (
    AppSession,
    AppServiceDependency,
)
from tiferet.interfaces import AppService
from tiferet.mappers import AppSessionAggregate
from tiferet.testing import DomainEventTestBase, ServiceEventTestBase

# *** fixtures

# ** fixture: app_session
@pytest.fixture
def app_session():
    '''
    Fixture to create an AppSession aggregate for testing.

    :return: An AppSessionAggregate instance.
    :rtype: AppSessionAggregate
    '''

    # Create a test AppSession instance.
    return AppSessionAggregate(
        id='test',
        name='Test App',
        description='The test app.',
        flags=['test'],
        services=[
            AppServiceDependency(
                service_id='test_service',
                module_path='test_module_path',
                class_name='test_class_name',
            ),
        ],
    )

# *** tests

# ** class: TestAppEvent
class TestAppEvent:
    '''
    Tests for the AppEvent base event shared by all app events.
    '''

    # * method: test_base_extends_domain_event
    def test_base_extends_domain_event(self):
        '''
        Test that AppEvent extends DomainEvent.
        '''

        # Assert the base event extends DomainEvent.
        assert issubclass(AppEvent, DomainEvent)

    # * method: test_concrete_events_extend_base
    def test_concrete_events_extend_base(self):
        '''
        Test that every concrete app event extends AppEvent.
        '''

        # Assert each concrete event extends the module base.
        for event_cls in (
            AddAppSession,
            GetAppSession,
            UpdateAppSession,
            ListAppSessions,
            RemoveAppSession,
            SetAppConstants,
            SetServiceDependency,
            RemoveServiceDependency,
        ):
            assert issubclass(event_cls, AppEvent)

    # * method: test_service_injection
    def test_service_injection(self):
        '''
        Test that constructing an app event wires the shared service attribute.
        '''

        # Create a mock app service.
        service = mock.Mock(spec=AppService)

        # Assert the base and a concrete event both expose the injected service.
        assert AppEvent(app_service=service).app_service is service
        assert GetAppSession(app_service=service).app_service is service

# ** test: TestSetServiceDependency
class TestSetServiceDependency(ServiceEventTestBase):
    '''
    Tests for SetServiceDependency using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = SetServiceDependency

    # * attribute: dependencies
    dependencies = {'app_service': AppService}

    # * attribute: service_attr
    service_attr = 'app_service'

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='test',
        service_id='new_dependency',
        module_path='new.module.path',
        class_name='NewClass',
    )

    # * attribute: required_params
    required_params = ['id', 'service_id', 'module_path', 'class_name']

    # * attribute: not_found_error_code
    not_found_error_code = a.error.APP_SESSION_NOT_FOUND_ID

    # * attribute: not_found_kwargs
    not_found_kwargs = dict(
        id='missing.session',
        service_id='dep',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
    )

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, app_session):
        '''
        Override to provide a service mock pre-configured with an app_session.
        '''

        # Create a mock AppService that returns the app_session on get.
        service = mock.Mock(spec=AppService)
        service.get.return_value = app_session
        return {'app_service': service}

    # * method: test_creates_new_service
    def test_creates_new_service(self, mock_dependencies, app_session):
        '''
        Test that SetServiceDependency creates a new dependency when it does not exist.
        '''

        # Ensure no service with the target id exists initially.
        assert app_session.get_service('new_dependency') is None

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies, parameters={'param1': 'value1'})

        # Command should return the session id.
        assert result == app_session.id

        # A new service dependency should be created with the provided values.
        new_svc = app_session.get_service('new_dependency')
        assert new_svc is not None
        assert new_svc.module_path == 'new.module.path'
        assert new_svc.class_name == 'NewClass'
        assert new_svc.parameters == {'param1': 'value1'}

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_session)

    # * method: test_updates_existing_and_merges_parameters
    def test_updates_existing_and_merges_parameters(self, mock_dependencies, app_session):
        '''
        Test that SetServiceDependency updates an existing dependency and merges parameters.
        '''

        # Precondition: existing service from fixture.
        existing_svc = app_session.get_service('test_service')
        existing_svc.parameters = {'keep': 'value', 'override': 'old', 'remove': 'to_be_removed'}

        # Execute via the harness handle helper with updated fields.
        result = self.handle(
            mock_dependencies,
            service_id='test_service',
            module_path='updated.module.path',
            class_name='UpdatedClass',
            parameters={
                'override': 'new',
                'remove': None,
                'new_param': 'new_value',
            },
        )

        # Command should return the session id.
        assert result == app_session.id

        # Service dependency should be updated.
        updated_svc = app_session.get_service('test_service')
        assert updated_svc.module_path == 'updated.module.path'
        assert updated_svc.class_name == 'UpdatedClass'
        assert updated_svc.parameters == {
            'keep': 'value',
            'override': 'new',
            'new_param': 'new_value',
        }

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_session)

    # * method: test_parameters_none_clears_existing
    def test_parameters_none_clears_existing(self, mock_dependencies, app_session):
        '''
        Test that passing parameters=None clears existing parameters.
        '''

        # Precondition: existing service has parameters.
        existing_svc = app_session.get_service('test_service')
        existing_svc.parameters = {'key': 'value'}

        # Execute via the harness handle helper with parameters=None.
        result = self.handle(
            mock_dependencies,
            service_id='test_service',
            module_path='tiferet.contexts.app',
            class_name='AppContext',
            parameters=None,
        )

        # Command should return the session id.
        assert result == app_session.id

        # Parameters should be cleared.
        cleared_svc = app_session.get_service('test_service')
        assert cleared_svc.parameters == {}

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_session)

# ** test: TestSetAppConstants
class TestSetAppConstants(ServiceEventTestBase):
    '''
    Tests for SetAppConstants using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = SetAppConstants

    # * attribute: dependencies
    dependencies = {'app_service': AppService}

    # * attribute: service_attr
    service_attr = 'app_service'

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='test',
        constants={'KEY': 'VALUE'},
    )

    # * attribute: required_params
    required_params = ['id']

    # * attribute: not_found_error_code
    not_found_error_code = a.error.APP_SESSION_NOT_FOUND_ID

    # * attribute: not_found_kwargs
    not_found_kwargs = dict(
        id='missing.session',
        constants={'KEY': 'VALUE'},
    )

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, app_session):
        '''
        Override to provide a service mock pre-configured with an app_session.
        '''

        # Create a mock AppService that returns the app_session on get.
        service = mock.Mock(spec=AppService)
        service.get.return_value = app_session
        return {'app_service': service}

    # * method: test_full_clear
    def test_full_clear(self, mock_dependencies, app_session):
        '''
        Test that SetAppConstants clears all constants when constants=None.
        '''

        # Seed existing constants on the session.
        app_session.constants = {
            'EXISTING': 'value',
            'OTHER': 'other_value',
        }

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies, constants=None)

        # Command should return the session id.
        assert result == app_session.id

        # All constants should be cleared.
        assert app_session.constants == {}

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_session)

    # * method: test_merge_override_and_remove
    def test_merge_override_and_remove(self, mock_dependencies, app_session):
        '''
        Test that SetAppConstants merges, overrides, and removes None-valued keys.
        '''

        # Seed existing constants.
        app_session.constants = {
            'KEEP': 'keep_value',
            'OVERRIDE': 'old',
            'REMOVE': 'to_be_removed',
        }

        # Execute via the harness handle helper with mixed updates.
        result = self.handle(
            mock_dependencies,
            constants={
                'OVERRIDE': 'new',
                'REMOVE': None,
                'ADD': 'added',
            },
        )

        # Command should return the session id.
        assert result == app_session.id

        # Constants should be merged/updated with None-valued keys removed.
        assert app_session.constants == {
            'KEEP': 'keep_value',
            'OVERRIDE': 'new',
            'ADD': 'added',
        }

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_session)

    # * method: test_add_new_constants
    def test_add_new_constants(self, mock_dependencies, app_session):
        '''
        Test that SetAppConstants adds new constants when none exist.
        '''

        # Precondition: no constants defined.
        assert app_session.constants == {}

        # Execute via the harness handle helper with new constants.
        result = self.handle(
            mock_dependencies,
            constants={
                'NEW_ONE': 'one',
                'NEW_TWO': 'two',
            },
        )

        # Command should return the session id.
        assert result == app_session.id

        # All new constants should be present.
        assert app_session.constants == {
            'NEW_ONE': 'one',
            'NEW_TWO': 'two',
        }

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_session)

# ** test: TestRemoveServiceDependency
class TestRemoveServiceDependency(ServiceEventTestBase):
    '''
    Tests for RemoveServiceDependency using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = RemoveServiceDependency

    # * attribute: dependencies
    dependencies = {'app_service': AppService}

    # * attribute: service_attr
    service_attr = 'app_service'

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='test',
        service_id='test_service',
    )

    # * attribute: required_params
    required_params = ['id', 'service_id']

    # * attribute: not_found_error_code
    not_found_error_code = a.error.APP_SESSION_NOT_FOUND_ID

    # * attribute: not_found_kwargs
    not_found_kwargs = dict(
        id='missing.session',
        service_id='dep',
    )

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, app_session):
        '''
        Override to provide a service mock pre-configured with an app_session.
        '''

        # Create a mock AppService that returns the app_session on get.
        service = mock.Mock(spec=AppService)
        service.get.return_value = app_session
        return {'app_service': service}

    # * method: test_removes_existing
    def test_removes_existing(self, mock_dependencies, app_session):
        '''
        Test that RemoveServiceDependency removes an existing service dependency.
        '''

        # Precondition: the service dependency exists on the session.
        existing_svc = app_session.get_service('test_service')
        assert existing_svc is not None
        initial_count = len(app_session.services)

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Command should return the session id.
        assert result == app_session.id

        # The service dependency should be removed.
        assert app_session.get_service('test_service') is None
        assert len(app_session.services) == initial_count - 1

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_session)

    # * method: test_missing_service_is_idempotent
    def test_missing_service_is_idempotent(self, mock_dependencies, app_session):
        '''
        Test that removing a non-existent service dependency is idempotent.
        '''

        # Precondition: no service dependency with the given id exists.
        assert app_session.get_service('missing_service') is None
        initial_count = len(app_session.services)

        # Execute via the harness handle helper with a non-existent service id.
        result = self.handle(mock_dependencies, service_id='missing_service')

        # Command should return the session id.
        assert result == app_session.id

        # Services list should remain unchanged.
        assert app_session.get_service('missing_service') is None
        assert len(app_session.services) == initial_count

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_session)

# ** test: TestAddAppSession
class TestAddAppSession(DomainEventTestBase):
    '''
    Tests for AddAppSession using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = AddAppSession

    # * attribute: dependencies
    dependencies = {'app_service': AppService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='test.session',
        name='Test Session',
    )

    # * attribute: required_params
    required_params = ['id', 'name']

    # * method: test_add_app_session_success
    def test_add_app_session_success(self, mock_dependencies):
        '''
        Test that AddAppSession creates and persists an AppSession with required params.
        '''

        # Execute via the harness handle helper.
        session = self.handle(mock_dependencies)

        # Assert the result is an AppSession instance with expected values.
        assert isinstance(session, AppSession)
        assert session.id == 'test.session'
        assert session.name == 'Test Session'
        assert session.description is None
        assert session.logger_id == 'default'
        assert session.flags == ['default']
        assert session.services == []
        assert session.constants == {}

        # Assert the session is persisted via the app service.
        mock_dependencies['app_service'].save.assert_called_once_with(session)

    # * method: test_add_app_session_full_parameters
    def test_add_app_session_full_parameters(self, mock_dependencies):
        '''
        Test that AddAppSession passes through optional parameters correctly.
        '''

        # Execute with all optional parameters.
        session = self.handle(
            mock_dependencies,
            description='A full session.',
            logger_id='custom_logger',
            flags=['flag_a', 'flag_b'],
            services=[
                {
                    'service_id': 'svc1',
                    'module_path': 'some.module',
                    'class_name': 'SomeClass',
                    'parameters': {},
                }
            ],
            constants={'KEY': 'VAL'},
        )

        # Assert optional fields are set correctly.
        assert session.description == 'A full session.'
        assert session.logger_id == 'custom_logger'
        assert session.flags == ['flag_a', 'flag_b']
        assert session.constants == {'KEY': 'VAL'}
        assert len(session.services) == 1
        assert session.services[0].service_id == 'svc1'

        # Assert the session is persisted.
        mock_dependencies['app_service'].save.assert_called_once()

# ** test: TestGetAppSession
class TestGetAppSession(ServiceEventTestBase):
    '''
    Tests for GetAppSession using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = GetAppSession

    # * attribute: dependencies
    dependencies = {'app_service': AppService}

    # * attribute: service_attr
    service_attr = 'app_service'

    # * attribute: sample_kwargs
    sample_kwargs = dict(id='test.session')

    # * attribute: required_params
    required_params = ['id']

    # * attribute: not_found_error_code
    not_found_error_code = a.error.APP_SESSION_NOT_FOUND_ID

    # * attribute: not_found_kwargs
    not_found_kwargs = dict(id='nonexistent.session')

    # * method: test_get_app_session_success
    def test_get_app_session_success(self, mock_dependencies):
        '''
        Test successful retrieval of an app session.
        '''

        # Configure the service mock to return a session.
        app_session = AppSessionAggregate(
            id='test.session',
            name='Test Session',
        )
        mock_dependencies['app_service'].get.return_value = app_session

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Assert the returned session matches expectations.
        assert result is app_session
        mock_dependencies['app_service'].get.assert_called_once_with('test.session')

    # * method: test_get_app_session_not_found
    def test_get_app_session_not_found(self, mock_dependencies):
        '''
        Test that GetAppSession raises APP_SESSION_NOT_FOUND_ID when the session is missing.
        '''

        # Configure the service mock to return None.
        mock_dependencies['app_service'].get.return_value = None

        # Execute and expect the not-found error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, id='missing.session')

        # Assert the correct error code.
        assert exc_info.value.error_code == a.error.APP_SESSION_NOT_FOUND_ID

# ** test: TestUpdateAppSession
class TestUpdateAppSession(ServiceEventTestBase):
    '''
    Tests for UpdateAppSession using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = UpdateAppSession

    # * attribute: dependencies
    dependencies = {'app_service': AppService}

    # * attribute: service_attr
    service_attr = 'app_service'

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='test.session',
        name='Updated Session',
    )

    # * attribute: required_params
    required_params = ['id']

    # * attribute: not_found_error_code
    not_found_error_code = a.error.APP_SESSION_NOT_FOUND_ID

    # * attribute: not_found_kwargs
    not_found_kwargs = dict(id='missing.session')

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self):
        '''
        Override to provide a service mock pre-configured with an app session.
        '''

        # Create a mock AppService that returns an AppSessionAggregate on get.
        session = AppSessionAggregate(id='test.session', name='Test Session')
        service = mock.Mock(spec=AppService)
        service.get.return_value = session
        return {'app_service': service}

    # * method: test_update_app_session_success
    def test_update_app_session_success(self, mock_dependencies):
        '''
        Test that UpdateAppSession updates provided scalar attributes and persists the session.
        '''

        # Execute via the harness handle helper with all optional fields.
        result = self.handle(
            mock_dependencies,
            description='Updated description.',
            logger_id='updated_logger',
        )

        # Assert the attributes were updated on the returned session.
        assert result.name == 'Updated Session'
        assert result.description == 'Updated description.'
        assert result.logger_id == 'updated_logger'

        # Assert the updated session was persisted.
        mock_dependencies['app_service'].save.assert_called_once_with(result)

    # * method: test_update_app_session_not_found
    def test_update_app_session_not_found(self, mock_dependencies):
        '''
        Test that UpdateAppSession raises APP_SESSION_NOT_FOUND_ID when the session is missing.
        '''

        # Configure the service mock to report the session as missing.
        mock_dependencies['app_service'].get.return_value = None

        # Execute and expect the not-found error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, id='missing.session')

        # Assert the correct error code was raised.
        assert exc_info.value.error_code == a.error.APP_SESSION_NOT_FOUND_ID

        # Assert the error carries the id kwarg the message template formats on.
        assert exc_info.value.kwargs.get('id') == 'missing.session'

        # Assert no save was attempted for a missing session.
        mock_dependencies['app_service'].save.assert_not_called()

    # * method: test_update_app_session_missing_id
    def test_update_app_session_missing_id(self, mock_dependencies):
        '''
        Test that UpdateAppSession enforces the required id parameter.
        '''

        # Execute without an id and expect the required-parameter error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, id=None)

        # Assert the correct error code names the missing parameter.
        assert exc_info.value.error_code == a.error.COMMAND_PARAMETER_REQUIRED_ID
        assert 'id' in str(exc_info.value)

        # Assert the service was never consulted.
        mock_dependencies['app_service'].get.assert_not_called()

    # * method: test_update_app_session_partial_leaves_unset_fields_unchanged
    def test_update_app_session_partial_leaves_unset_fields_unchanged(self, mock_dependencies):
        '''
        Test that omitted optional fields are left unchanged.
        '''

        # Execute via the harness handle helper with only the name field.
        result = self.handle(mock_dependencies, name='Only Name Updated')

        # Assert only the provided field changed.
        assert result.name == 'Only Name Updated'
        assert result.logger_id == 'default'

# ** test: TestListAppSessions
class TestListAppSessions(DomainEventTestBase):
    '''
    Tests for ListAppSessions using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = ListAppSessions

    # * attribute: dependencies
    dependencies = {'app_service': AppService}

    # * attribute: sample_kwargs
    sample_kwargs = dict()

    # * method: test_list_app_sessions_success
    def test_list_app_sessions_success(self, mock_dependencies):
        '''
        Test that ListAppSessions returns the list returned by the app service.
        '''

        # Configure the service to return a list of sessions.
        sessions = [AppSessionAggregate(id='a', name='A'), AppSessionAggregate(id='b', name='B')]
        mock_dependencies['app_service'].list.return_value = sessions

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Assert the returned list matches the configured sessions.
        assert result == sessions
        mock_dependencies['app_service'].list.assert_called_once_with()

# ** test: TestRemoveAppSession
class TestRemoveAppSession(DomainEventTestBase):
    '''
    Tests for RemoveAppSession using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = RemoveAppSession

    # * attribute: dependencies
    dependencies = {'app_service': AppService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(id='test.session')

    # * attribute: required_params
    required_params = ['id']

    # * method: test_remove_app_session_success
    def test_remove_app_session_success(self, mock_dependencies):
        '''
        Test that RemoveAppSession deletes the session via the app service.
        '''

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Command returns None and delegates deletion to the service.
        assert result is None
        mock_dependencies['app_service'].delete.assert_called_once_with('test.session')

    # * method: test_remove_app_session_missing_is_idempotent
    def test_remove_app_session_missing_is_idempotent(self, mock_dependencies):
        '''
        Test that removing a non-existent session is idempotent.
        '''

        # Execute via the harness handle helper with a different id.
        result = self.handle(mock_dependencies, id='missing.session')

        # Command returns None and still calls delete exactly once.
        assert result is None
        mock_dependencies['app_service'].delete.assert_called_once_with('missing.session')
