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
    ATTRIBUTE_NOT_SETTABLE_ID,
    ModelError,
)
from tiferet.interfaces import AppService
from tiferet.mappers import AppSessionAggregate
from tiferet.blueprints.tester import use_tester

# *** fixtures

# ** fixture: app_interface
@pytest.fixture
def app_interface():
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

# *** testers

# ** tester: test_app_event
class TestAppEvent:
    '''
    Tests for the AppEvent base event shared by all app events.
    '''

    # * test: base_extends_domain_event
    def test_base_extends_domain_event(self):
        '''
        Test that AppEvent extends DomainEvent.
        '''

        # Assert the base event extends DomainEvent.
        assert issubclass(AppEvent, DomainEvent)

    # * test: concrete_events_extend_base
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

    # * test: service_injection
    def test_service_injection(self):
        '''
        Test that constructing an app event wires the shared service attribute.
        '''

        # Create a mock app service.
        service = mock.Mock(spec=AppService)

        # Assert the base and a concrete event both expose the injected service.
        assert AppEvent(app_service=service).app_service is service
        assert GetAppSession(app_service=service).app_service is service

# ** tester: test_add_app_session
@use_tester(
    type='domain_event',
    target_cls=AddAppSession,
    dependencies={
        'app_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'AppService',
        },
    },
    sample_kwargs=dict(
        id='test.interface',
        name='Test Interface',
    ),
    required_params=[
        'id',
        'name',
    ],
)
class TestAddAppSession:
    '''
    Tests for AddAppSession using the domain event test harness.
    '''

    # * test: minimal_success
    def test_minimal_success(self, test_ctx):
        '''
        Test that AddAppSession creates and persists an AppSession with required params.

        :param test_ctx: The bound domain-event tester context.
        :type test_ctx: DomainEventTesterContext
        '''

        # Build mocked constructor dependencies.
        mock_dependencies = test_ctx.mock_dependencies()

        # Execute via the harness handle helper.
        session = test_ctx.handle(mock_dependencies)

        # Assert the result is an AppSession instance with expected values.
        assert isinstance(session, AppSession)
        assert session.id == 'test.interface'
        assert session.name == 'Test Interface'
        assert session.description is None
        assert session.logger_id == 'default'
        assert session.flags == ['default']
        assert session.services == []
        assert session.constants == {}

        # Assert the session is persisted via the app service.
        mock_dependencies['app_service'].save.assert_called_once_with(session)

    # * test: full_parameters
    def test_full_parameters(self, test_ctx):
        '''
        Test that AddAppSession passes through optional parameters correctly.

        :param test_ctx: The bound domain-event tester context.
        :type test_ctx: DomainEventTesterContext
        '''

        # Build mocked constructor dependencies.
        mock_dependencies = test_ctx.mock_dependencies()

        # Execute with all optional parameters.
        session = test_ctx.handle(
            mock_dependencies,
            description='A test app interface.',
            logger_id='test_logger',
            flags=[
                'test_feature',
                'test_data',
            ],
            services=[
                {
                    'service_id': 'svc1',
                    'module_path': 'test.module',
                    'class_name': 'TestClass',
                    'parameters': {
                        'foo': 'bar',
                    },
                },
            ],
            constants={
                'CONST_KEY': 'VALUE',
            },
        )

        # Assert optional fields are set correctly.
        assert isinstance(session, AppSession)
        assert session.id == 'test.interface'
        assert session.description == 'A test app interface.'
        assert session.logger_id == 'test_logger'
        assert session.flags == ['test_feature', 'test_data']
        assert session.constants == {'CONST_KEY': 'VALUE'}
        assert len(session.services) == 1
        service = session.services[0]
        assert isinstance(service, AppServiceDependency)
        assert service.service_id == 'svc1'
        assert service.module_path == 'test.module'
        assert service.class_name == 'TestClass'
        assert service.parameters == {'foo': 'bar'}

        # Assert the session is persisted.
        mock_dependencies['app_service'].save.assert_called_once()

    # * test: default_fallbacks
    def test_default_fallbacks(self, test_ctx):
        '''
        Test that omitted logger and flag arguments fall back to defaults.

        :param test_ctx: The bound domain-event tester context.
        :type test_ctx: DomainEventTesterContext
        '''

        # Build mocked constructor dependencies.
        mock_dependencies = test_ctx.mock_dependencies()

        # Execute via the harness handle helper.
        session = test_ctx.handle(mock_dependencies)

        # Assert default logger and flags.
        assert session.logger_id == 'default'
        assert session.flags == ['default']

        # Assert the session is persisted.
        mock_dependencies['app_service'].save.assert_called_once_with(session)

    # * test: none_arguments_coerced
    def test_none_arguments_coerced(self, test_ctx):
        '''
        Test that None optional arguments are coerced to their defaults.

        :param test_ctx: The bound domain-event tester context.
        :type test_ctx: DomainEventTesterContext
        '''

        # Build mocked constructor dependencies.
        mock_dependencies = test_ctx.mock_dependencies()

        # Execute with explicit None optional arguments.
        session = test_ctx.handle(
            mock_dependencies,
            logger_id=None,
            flags=None,
            services=None,
            constants=None,
        )

        # Assert coerced defaults.
        assert session.logger_id == 'default'
        assert session.flags == ['default']
        assert session.services == []
        assert session.constants == {}

        # Assert the session is persisted.
        mock_dependencies['app_service'].save.assert_called_once_with(session)

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''
        Test that each required parameter raises COMMAND_PARAMETER_REQUIRED.

        :param test_ctx: The bound domain-event tester context.
        :type test_ctx: DomainEventTesterContext
        '''

        # Assert each required parameter, passed as None, raises the required error.
        test_ctx.assert_missing_required_params()

# ** tester: test_get_app_session
@use_tester(
    type='service_event',
    target_cls=GetAppSession,
    dependencies={
        'app_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'AppService',
        },
    },
    sample_kwargs=dict(
        id='test',
    ),
    required_params=[
        'id',
    ],
    service_attr='app_service',
    not_found_error_code=a.error.APP_SESSION_NOT_FOUND_ID,
    not_found_kwargs=dict(
        id='non_existent_id',
    ),
)
class TestGetAppSession:
    '''
    Tests for GetAppSession using the domain event test harness.
    '''

    # * test: success
    def test_success(self, test_ctx, app_interface):
        '''
        Test successful retrieval of an app session.

        :param test_ctx: The bound service-event tester context.
        :type test_ctx: ServiceEventTesterContext
        :param app_interface: The app interface fixture.
        :type app_interface: AppSessionAggregate
        '''

        # Configure the service mock to return the fixture session.
        mock_dependencies = test_ctx.mock_dependencies()
        mock_dependencies['app_service'].get.return_value = app_interface

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Assert the returned session matches the fixture.
        assert result == app_interface

    # * test: returns_domain_object_without_rewrap
    def test_returns_domain_object_without_rewrap(self, test_ctx):
        '''
        Test that GetAppSession returns the service object without re-wrapping it.

        :param test_ctx: The bound service-event tester context.
        :type test_ctx: ServiceEventTesterContext
        '''

        # Configure the service mock to return a domain object.
        mock_dependencies = test_ctx.mock_dependencies()
        app_session = AppSession(id='test.interface', name='Test Interface')
        mock_dependencies['app_service'].get.return_value = app_session

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies, id='test.interface')

        # Assert the same object is returned and looked up once.
        assert result is app_session
        mock_dependencies['app_service'].get.assert_called_once_with('test.interface')

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''
        Test that each required parameter raises COMMAND_PARAMETER_REQUIRED.

        :param test_ctx: The bound service-event tester context.
        :type test_ctx: ServiceEventTesterContext
        '''

        # Assert each required parameter, passed as None, raises the required error.
        test_ctx.assert_missing_required_params()

    # * test: not_found
    def test_not_found(self, test_ctx):
        '''
        Test that a missing session raises APP_SESSION_NOT_FOUND.

        :param test_ctx: The bound service-event tester context.
        :type test_ctx: ServiceEventTesterContext
        '''

        # Assert the primary service miss raises the configured not-found error.
        test_ctx.assert_not_found()

# ** tester: test_list_app_sessions
@use_tester(
    type='domain_event',
    target_cls=ListAppSessions,
    dependencies={
        'app_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'AppService',
        },
    },
    sample_kwargs=dict(),
)
class TestListAppSessions:
    '''
    Tests for ListAppSessions using the domain event test harness.
    '''

    # * test: empty
    def test_empty(self, test_ctx):
        '''
        Test that ListAppSessions returns an empty list when the service does.

        :param test_ctx: The bound domain-event tester context.
        :type test_ctx: DomainEventTesterContext
        '''

        # Configure the service to return no sessions.
        mock_dependencies = test_ctx.mock_dependencies()
        mock_dependencies['app_service'].list.return_value = []

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Assert the empty list is returned and list was called once.
        assert result == []
        mock_dependencies['app_service'].list.assert_called_once_with()

    # * test: multiple
    def test_multiple(self, test_ctx, app_interface):
        '''
        Test that ListAppSessions returns the list returned by the app service.

        :param test_ctx: The bound domain-event tester context.
        :type test_ctx: DomainEventTesterContext
        :param app_interface: The app interface fixture.
        :type app_interface: AppSessionAggregate
        '''

        # Configure the service to return a list of sessions.
        mock_dependencies = test_ctx.mock_dependencies()
        sessions = [
            app_interface,
            AppSessionAggregate(id='other', name='Other App'),
        ]
        mock_dependencies['app_service'].list.return_value = sessions

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Assert the returned list matches the configured sessions.
        assert result == sessions
        mock_dependencies['app_service'].list.assert_called_once_with()

# ** tester: test_set_service_dependency
@use_tester(
    type='service_event',
    target_cls=SetServiceDependency,
    dependencies={
        'app_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'AppService',
        },
    },
    sample_kwargs=dict(
        id='test',
        service_id='new_dependency',
        module_path='new.module.path',
        class_name='NewClass',
    ),
    required_params=[
        'id',
        'service_id',
        'module_path',
        'class_name',
    ],
    service_attr='app_service',
    not_found_error_code=a.error.APP_SESSION_NOT_FOUND_ID,
    not_found_kwargs=dict(
        id='missing.interface',
        service_id='dep',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
    ),
)
class TestSetServiceDependency:
    '''
    Tests for SetServiceDependency using the domain event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, app_interface):
        '''
        Override to provide a service mock pre-configured with an app_session.
        '''

        # Create a mock AppService that returns the app_session on get.
        service = mock.Mock(spec=AppService)
        service.get.return_value = app_interface
        return {'app_service': service}

    # * test: creates_new_service
    def test_creates_new_service(self,
                                 test_ctx,
                                 mock_dependencies,
                                 app_interface):
        '''
        Test that SetServiceDependency creates a new dependency when it does not exist.
        '''

        # Ensure no service with the target id exists initially.
        assert app_interface.get_service('new_dependency') is None

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies, parameters={'param1': 'value1'})

        # Command should return the session id.
        assert result == app_interface.id

        # A new service dependency should be created with the provided values.
        new_svc = app_interface.get_service('new_dependency')
        assert new_svc is not None
        assert new_svc.module_path == 'new.module.path'
        assert new_svc.class_name == 'NewClass'
        assert new_svc.parameters == {'param1': 'value1'}

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

    # * test: updates_existing_and_merges_parameters
    def test_updates_existing_and_merges_parameters(self,
                                                    test_ctx,
                                                    mock_dependencies,
                                                    app_interface):
        '''
        Test that SetServiceDependency updates an existing dependency and merges parameters.
        '''

        # Precondition: existing service from fixture.
        existing_svc = app_interface.get_service('test_service')
        existing_svc.parameters = {'keep': 'value', 'override': 'old', 'remove': 'to_be_removed'}

        # Execute via the harness handle helper with updated fields.
        result = test_ctx.handle(
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
        assert result == app_interface.id

        # Service dependency should be updated.
        updated_svc = app_interface.get_service('test_service')
        assert updated_svc.module_path == 'updated.module.path'
        assert updated_svc.class_name == 'UpdatedClass'
        assert updated_svc.parameters == {
            'keep': 'value',
            'override': 'new',
            'new_param': 'new_value',
        }

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

    # * test: parameters_none_clears_existing
    def test_parameters_none_clears_existing(self,
                                             test_ctx,
                                             mock_dependencies,
                                             app_interface):
        '''
        Test that passing parameters=None clears existing parameters.
        '''

        # Precondition: existing service has parameters.
        existing_svc = app_interface.get_service('test_service')
        existing_svc.parameters = {'key': 'value'}

        # Execute via the harness handle helper with parameters=None.
        result = test_ctx.handle(
            mock_dependencies,
            service_id='test_service',
            module_path='tiferet.contexts.app',
            class_name='AppContext',
            parameters=None,
        )

        # Command should return the session id.
        assert result == app_interface.id

        # Parameters should be cleared.
        cleared_svc = app_interface.get_service('test_service')
        assert cleared_svc.parameters == {}

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''
        Test that each required parameter raises COMMAND_PARAMETER_REQUIRED.

        :param test_ctx: The bound service-event tester context.
        :type test_ctx: ServiceEventTesterContext
        '''

        # Assert each required parameter, passed as None, raises the required error.
        test_ctx.assert_missing_required_params()

    # * test: not_found
    def test_not_found(self, test_ctx):
        '''
        Test that a missing session raises APP_SESSION_NOT_FOUND.

        :param test_ctx: The bound service-event tester context.
        :type test_ctx: ServiceEventTesterContext
        '''

        # Assert the primary service miss raises the configured not-found error.
        test_ctx.assert_not_found()

# ** tester: test_update_app_session
@use_tester(
    type='service_event',
    target_cls=UpdateAppSession,
    dependencies={
        'app_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'AppService',
        },
    },
    sample_kwargs=dict(
        id='test',
        attribute='name',
        value='Updated Name',
    ),
    required_params=[
        'id',
        'attribute',
    ],
    service_attr='app_service',
    not_found_error_code=a.error.APP_SESSION_NOT_FOUND_ID,
    not_found_kwargs=dict(
        id='missing.interface',
        attribute='name',
        value='Updated Name',
    ),
)
class TestUpdateAppSession:
    '''
    Tests for UpdateAppSession using the domain event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, app_interface):
        '''
        Override to provide a service mock pre-configured with an app_session.
        '''

        # Create a mock AppService that returns the app_session on get.
        service = mock.Mock(spec=AppService)
        service.get.return_value = app_interface
        return {'app_service': service}

    # * test: success_supported_attributes
    @pytest.mark.parametrize('attribute,new_value', [
        ('name', 'Updated Name'),
        ('description', 'Updated description'),
        ('logger_id', 'updated_logger'),
        ('flags', ['updated_flags']),
    ])
    def test_success_supported_attributes(self,
                                          test_ctx,
                                          mock_dependencies,
                                          app_interface,
                                          attribute,
                                          new_value):
        '''
        Test that UpdateAppSession sets a supported attribute and persists the session.

        :param test_ctx: The bound service-event tester context.
        :type test_ctx: ServiceEventTesterContext
        :param mock_dependencies: The preconfigured service dependency mapping.
        :type mock_dependencies: dict
        :param app_interface: The app interface fixture.
        :type app_interface: AppSessionAggregate
        :param attribute: The attribute name under test.
        :type attribute: str
        :param new_value: The value to assign.
        :type new_value: Any
        '''

        # Execute via the harness handle helper for the parametrized attribute.
        result = test_ctx.handle(
            mock_dependencies,
            id=app_interface.id,
            attribute=attribute,
            value=new_value,
        )

        # Command should return the session id and apply the attribute.
        assert result == app_interface.id
        assert getattr(app_interface, attribute) == new_value

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

    # * test: invalid_attribute_raises_model_error
    def test_invalid_attribute_raises_model_error(self,
                                                  test_ctx,
                                                  mock_dependencies,
                                                  app_interface):
        '''
        Test that an unknown attribute raises ModelError and is not saved.

        :param test_ctx: The bound service-event tester context.
        :type test_ctx: ServiceEventTesterContext
        :param mock_dependencies: The preconfigured service dependency mapping.
        :type mock_dependencies: dict
        :param app_interface: The app interface fixture.
        :type app_interface: AppSessionAggregate
        '''

        # Execute with an unknown attribute and expect a model error.
        with pytest.raises(ModelError) as exc_info:
            test_ctx.handle(
                mock_dependencies,
                id=app_interface.id,
                attribute='invalid_attribute',
                value='value',
            )

        # Assert the model error code and that nothing was saved.
        assert exc_info.value.error_code == ATTRIBUTE_NOT_SETTABLE_ID
        mock_dependencies['app_service'].save.assert_not_called()

    # * test: model_error_is_not_a_domain_error
    def test_model_error_is_not_a_domain_error(self,
                                               test_ctx,
                                               mock_dependencies,
                                               app_interface):
        '''
        Test that an unknown attribute raises ModelError rather than TiferetError.

        :param test_ctx: The bound service-event tester context.
        :type test_ctx: ServiceEventTesterContext
        :param mock_dependencies: The preconfigured service dependency mapping.
        :type mock_dependencies: dict
        :param app_interface: The app interface fixture.
        :type app_interface: AppSessionAggregate
        '''

        # Execute with an unknown attribute and expect a model error.
        with pytest.raises(ModelError) as exc_info:
            test_ctx.handle(
                mock_dependencies,
                id=app_interface.id,
                attribute='invalid_attribute',
                value='value',
            )

        # Assert the model error is not a domain error.
        assert not isinstance(exc_info.value, TiferetError)

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''
        Test that each required parameter raises COMMAND_PARAMETER_REQUIRED.

        :param test_ctx: The bound service-event tester context.
        :type test_ctx: ServiceEventTesterContext
        '''

        # Assert each required parameter, passed as None, raises the required error.
        test_ctx.assert_missing_required_params()

    # * test: not_found
    def test_not_found(self, test_ctx):
        '''
        Test that a missing session raises APP_SESSION_NOT_FOUND.

        :param test_ctx: The bound service-event tester context.
        :type test_ctx: ServiceEventTesterContext
        '''

        # Assert the primary service miss raises the configured not-found error.
        test_ctx.assert_not_found()

# ** tester: test_set_app_constants
@use_tester(
    type='service_event',
    target_cls=SetAppConstants,
    dependencies={
        'app_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'AppService',
        },
    },
    sample_kwargs=dict(
        id='test',
        constants={
            'KEY': 'VALUE',
        },
    ),
    required_params=[
        'id',
    ],
    service_attr='app_service',
    not_found_error_code=a.error.APP_SESSION_NOT_FOUND_ID,
    not_found_kwargs=dict(
        id='missing.interface',
        constants={
            'KEY': 'VALUE',
        },
    ),
)
class TestSetAppConstants:
    '''
    Tests for SetAppConstants using the domain event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, app_interface):
        '''
        Override to provide a service mock pre-configured with an app_session.
        '''

        # Create a mock AppService that returns the app_session on get.
        service = mock.Mock(spec=AppService)
        service.get.return_value = app_interface
        return {'app_service': service}

    # * test: full_clear
    def test_full_clear(self,
                        test_ctx,
                        mock_dependencies,
                        app_interface):
        '''
        Test that SetAppConstants clears all constants when constants=None.
        '''

        # Seed existing constants on the session.
        app_interface.constants = {
            'EXISTING': 'value',
            'OTHER': 'other_value',
        }

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies, constants=None)

        # Command should return the session id.
        assert result == app_interface.id

        # All constants should be cleared.
        assert app_interface.constants == {}

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

    # * test: merge_override_and_remove
    def test_merge_override_and_remove(self,
                                       test_ctx,
                                       mock_dependencies,
                                       app_interface):
        '''
        Test that SetAppConstants merges, overrides, and removes None-valued keys.
        '''

        # Seed existing constants.
        app_interface.constants = {
            'KEEP': 'keep_value',
            'OVERRIDE': 'old',
            'REMOVE': 'to_be_removed',
        }

        # Execute via the harness handle helper with mixed updates.
        result = test_ctx.handle(
            mock_dependencies,
            constants={
                'OVERRIDE': 'new',
                'REMOVE': None,
                'ADD': 'added',
            },
        )

        # Command should return the session id.
        assert result == app_interface.id

        # Constants should be merged/updated with None-valued keys removed.
        assert app_interface.constants == {
            'KEEP': 'keep_value',
            'OVERRIDE': 'new',
            'ADD': 'added',
        }

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

    # * test: add_new_constants
    def test_add_new_constants(self,
                               test_ctx,
                               mock_dependencies,
                               app_interface):
        '''
        Test that SetAppConstants adds new constants when none exist.
        '''

        # Precondition: no constants defined.
        assert app_interface.constants == {}

        # Execute via the harness handle helper with new constants.
        result = test_ctx.handle(
            mock_dependencies,
            constants={
                'NEW_ONE': 'one',
                'NEW_TWO': 'two',
            },
        )

        # Command should return the session id.
        assert result == app_interface.id

        # All new constants should be present.
        assert app_interface.constants == {
            'NEW_ONE': 'one',
            'NEW_TWO': 'two',
        }

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''
        Test that each required parameter raises COMMAND_PARAMETER_REQUIRED.

        :param test_ctx: The bound service-event tester context.
        :type test_ctx: ServiceEventTesterContext
        '''

        # Assert each required parameter, passed as None, raises the required error.
        test_ctx.assert_missing_required_params()

    # * test: not_found
    def test_not_found(self, test_ctx):
        '''
        Test that a missing session raises APP_SESSION_NOT_FOUND.

        :param test_ctx: The bound service-event tester context.
        :type test_ctx: ServiceEventTesterContext
        '''

        # Assert the primary service miss raises the configured not-found error.
        test_ctx.assert_not_found()

# ** tester: test_remove_service_dependency
@use_tester(
    type='service_event',
    target_cls=RemoveServiceDependency,
    dependencies={
        'app_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'AppService',
        },
    },
    sample_kwargs=dict(
        id='test',
        service_id='test_service',
    ),
    required_params=[
        'id',
        'service_id',
    ],
    service_attr='app_service',
    not_found_error_code=a.error.APP_SESSION_NOT_FOUND_ID,
    not_found_kwargs=dict(
        id='missing.interface',
        service_id='dep',
    ),
)
class TestRemoveServiceDependency:
    '''
    Tests for RemoveServiceDependency using the domain event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, app_interface):
        '''
        Override to provide a service mock pre-configured with an app_session.
        '''

        # Create a mock AppService that returns the app_session on get.
        service = mock.Mock(spec=AppService)
        service.get.return_value = app_interface
        return {'app_service': service}

    # * test: removes_existing
    def test_removes_existing(self,
                              test_ctx,
                              mock_dependencies,
                              app_interface):
        '''
        Test that RemoveServiceDependency removes an existing service dependency.
        '''

        # Precondition: the service dependency exists on the session.
        existing_svc = app_interface.get_service('test_service')
        assert existing_svc is not None
        initial_count = len(app_interface.services)

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Command should return the session id.
        assert result == app_interface.id

        # The service dependency should be removed.
        assert app_interface.get_service('test_service') is None
        assert len(app_interface.services) == initial_count - 1

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

    # * test: missing_service_is_idempotent
    def test_missing_service_is_idempotent(self,
                                           test_ctx,
                                           mock_dependencies,
                                           app_interface):
        '''
        Test that removing a non-existent service dependency is idempotent.
        '''

        # Precondition: no service dependency with the given id exists.
        assert app_interface.get_service('missing_service') is None
        initial_count = len(app_interface.services)

        # Execute via the harness handle helper with a non-existent service id.
        result = test_ctx.handle(mock_dependencies, service_id='missing_service')

        # Command should return the session id.
        assert result == app_interface.id

        # Services list should remain unchanged.
        assert app_interface.get_service('missing_service') is None
        assert len(app_interface.services) == initial_count

        # The updated session should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''
        Test that each required parameter raises COMMAND_PARAMETER_REQUIRED.

        :param test_ctx: The bound service-event tester context.
        :type test_ctx: ServiceEventTesterContext
        '''

        # Assert each required parameter, passed as None, raises the required error.
        test_ctx.assert_missing_required_params()

    # * test: not_found
    def test_not_found(self, test_ctx):
        '''
        Test that a missing session raises APP_SESSION_NOT_FOUND.

        :param test_ctx: The bound service-event tester context.
        :type test_ctx: ServiceEventTesterContext
        '''

        # Assert the primary service miss raises the configured not-found error.
        test_ctx.assert_not_found()

# ** tester: test_remove_app_session
@use_tester(
    type='domain_event',
    target_cls=RemoveAppSession,
    dependencies={
        'app_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'AppService',
        },
    },
    sample_kwargs=dict(
        id='existing.interface',
    ),
    required_params=[
        'id',
    ],
)
class TestRemoveAppSession:
    '''
    Tests for RemoveAppSession using the domain event test harness.
    '''

    # * test: success_existing
    def test_success_existing(self, test_ctx):
        '''
        Test that RemoveAppSession deletes an existing session and returns its id.

        :param test_ctx: The bound domain-event tester context.
        :type test_ctx: DomainEventTesterContext
        '''

        # Build mocked constructor dependencies.
        mock_dependencies = test_ctx.mock_dependencies()

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Command returns the deleted id and delegates deletion to the service.
        assert result == 'existing.interface'
        mock_dependencies['app_service'].delete.assert_called_once_with('existing.interface')

    # * test: success_missing_is_idempotent
    def test_success_missing_is_idempotent(self, test_ctx):
        '''
        Test that removing a non-existent session is idempotent and returns its id.

        :param test_ctx: The bound domain-event tester context.
        :type test_ctx: DomainEventTesterContext
        '''

        # Build mocked constructor dependencies.
        mock_dependencies = test_ctx.mock_dependencies()

        # Execute via the harness handle helper with a missing id.
        result = test_ctx.handle(mock_dependencies, id='missing.interface')

        # Command returns the missing id and still calls delete exactly once.
        assert result == 'missing.interface'
        mock_dependencies['app_service'].delete.assert_called_once_with('missing.interface')

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''
        Test that each required parameter raises COMMAND_PARAMETER_REQUIRED.

        :param test_ctx: The bound domain-event tester context.
        :type test_ctx: DomainEventTesterContext
        '''

        # Assert each required parameter, passed as None, raises the required error.
        test_ctx.assert_missing_required_params()
