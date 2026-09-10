"""Tests for Tiferet DI Domain Events"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events.di import (
    DIEvent,
    AddServiceRegistration,
    SetDefaultServiceRegistration,
    SetServiceDependency,
    RemoveServiceDependency,
    RemoveServiceRegistration,
    SetServiceConstants,
    ListAllSettings,
)
from tiferet.events.core import DomainEvent, TiferetError, a
from tiferet.domain.di import ServiceRegistration, FlaggedDependency
from tiferet.mappers.di import (
    ServiceRegistrationAggregate,
    FlaggedDependencyAggregate,
)
from tiferet.interfaces.di import DIService
from tiferet.blueprints.tester import use_tester

# *** fixtures

# ** fixture: flagged_dependency_for_di
@pytest.fixture
def flagged_dependency_for_di() -> FlaggedDependency:
    '''
    A flagged dependency instance for DI event tests.

    :return: A FlaggedDependencyAggregate instance.
    :rtype: FlaggedDependencyAggregate
    '''

    # Create a flagged dependency aggregate.
    return FlaggedDependencyAggregate(
        module_path='tiferet.repos.example',
        class_name='ExampleRepository',
        flag='test_alpha',
        parameters={
            'test_param': 'test_value',
            'param': 'value1',
        },
    )

# ** fixture: service_registration_aggregate
@pytest.fixture
def service_registration_aggregate(flagged_dependency_for_di) -> ServiceRegistrationAggregate:
    '''
    A service registration aggregate for DI event tests.

    :param flagged_dependency_for_di: The flagged dependency fixture.
    :type flagged_dependency_for_di: FlaggedDependency
    :return: A ServiceRegistrationAggregate instance.
    :rtype: ServiceRegistrationAggregate
    '''

    # Create a service registration aggregate with a default type and one dependency.
    return ServiceRegistrationAggregate(
        id='svc_test',
        module_path='tiferet.repos.example',
        class_name='ExampleRepository',
        parameters={'param_1': 'value_1'},
        dependencies=[flagged_dependency_for_di],
    )

# *** testers

# ** tester: test_di_event
class TestDIEvent:
    '''
    Tests for the DIEvent base event shared by all DI events.
    '''

    # * test: base_extends_domain_event
    def test_base_extends_domain_event(self):
        '''
        Test that DIEvent extends DomainEvent.
        '''

        # Assert the base event extends DomainEvent.
        assert issubclass(DIEvent, DomainEvent)

    # * test: concrete_events_extend_base
    def test_concrete_events_extend_base(self):
        '''
        Test that every concrete DI event extends DIEvent.
        '''

        # Assert each concrete event extends the module base.
        for event_cls in (
            AddServiceRegistration,
            SetDefaultServiceRegistration,
            SetServiceDependency,
            RemoveServiceDependency,
            RemoveServiceRegistration,
            SetServiceConstants,
            ListAllSettings,
        ):
            assert issubclass(event_cls, DIEvent)

    # * test: service_injection
    def test_service_injection(self):
        '''
        Test that constructing a DI event wires the shared service attribute.
        '''

        # Create a mock DI service.
        service = mock.Mock(spec=DIService)

        # Assert the base and a concrete event both expose the injected service.
        assert DIEvent(di_service=service).di_service is service
        assert AddServiceRegistration(di_service=service).di_service is service

# ** tester: test_add_service_registration
@use_tester(
    type='domain_event',
    target_cls=AddServiceRegistration,
    dependencies={
        'di_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'DIService',
        },
    },
    sample_kwargs=dict(
        id='svc_new',
        module_path='tiferet.repos.example',
        class_name='ExampleRepository',
        parameters={'param': 'value'},
        flagged_dependencies=[],
    ),
    required_params=['id'],
)
class TestAddServiceRegistration:
    '''
    Tests for AddServiceRegistration using the domain event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self) -> dict:
        '''
        Override to pre-configure registration_exists to return False.
        '''

        # Create the mock DI service.
        service = mock.Mock(spec=DIService)
        service.registration_exists.return_value = False
        return {'di_service': service}

    # * test: default_type_only
    def test_default_type_only(self, test_ctx, mock_dependencies):
        '''
        Test adding a registration with only a default type.
        '''

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Assert the result is a ServiceRegistration instance.
        assert isinstance(result, ServiceRegistration)
        assert result.id == 'svc_new'
        assert result.module_path == 'tiferet.repos.example'
        assert result.class_name == 'ExampleRepository'
        assert result.parameters == {'param': 'value'}
        assert result.dependencies == []

        # Assert the service was called to check existence and save.
        mock_dependencies['di_service'].registration_exists.assert_called_once_with('svc_new')
        mock_dependencies['di_service'].save_registration.assert_called_once_with(result)

    # * test: dependencies_only
    def test_dependencies_only(self, test_ctx, mock_dependencies):
        '''
        Test adding a registration with only flagged dependencies.
        '''

        # Execute via the harness with flagged_dependencies and no default type.
        result = test_ctx.handle(
            mock_dependencies,
            module_path=None,
            class_name=None,
            parameters={},
            flagged_dependencies=[
                dict(
                    module_path='tiferet.repos.example',
                    class_name='ExampleRepository',
                    flag='alpha',
                    parameters={'flag_param': 'x'},
                )
            ],
        )

        # Assert the registration was created with dependencies.
        assert isinstance(result, ServiceRegistration)
        assert result.id == 'svc_new'
        assert result.module_path is None
        assert result.class_name is None
        assert len(result.dependencies) == 1

        # Assert the dependency was materialized correctly.
        dep = result.dependencies[0]
        assert dep.flag == 'alpha'
        assert dep.module_path == 'tiferet.repos.example'

    # * test: default_and_dependencies
    def test_default_and_dependencies(self, test_ctx, mock_dependencies):
        '''
        Test adding a registration with both a default type and dependencies.
        '''

        # Execute via the harness with both default type and flagged_dependencies.
        result = test_ctx.handle(
            mock_dependencies,
            flagged_dependencies=[
                dict(
                    module_path='tiferet.repos.other',
                    class_name='OtherRepository',
                    flag='beta',
                    parameters={},
                )
            ],
        )

        # Assert both default type and dependencies are present.
        assert result.module_path == 'tiferet.repos.example'
        assert result.class_name == 'ExampleRepository'
        assert len(result.dependencies) == 1
        assert result.dependencies[0].flag == 'beta'

    # * test: duplicate_id
    def test_duplicate_id(self, test_ctx, mock_dependencies):
        '''
        Test that adding a registration with an existing ID raises an error.
        '''

        # Configure the service to report the ID already exists.
        mock_dependencies['di_service'].registration_exists.return_value = True

        # Execute and expect a SERVICE_REGISTRATION_ALREADY_EXISTS error.
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(mock_dependencies)

        assert exc_info.value.error_code == a.error.SERVICE_REGISTRATION_ALREADY_EXISTS_ID

    # * test: no_type_source
    def test_no_type_source(self, test_ctx, mock_dependencies):
        '''
        Test that adding a registration with no default type and no dependencies fails.
        '''

        # Execute with neither default type nor flagged dependencies.
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(
                mock_dependencies,
                module_path=None,
                class_name=None,
                flagged_dependencies=[],
            )

        assert exc_info.value.error_code == a.error.INVALID_SERVICE_REGISTRATION_ID

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        test_ctx.assert_missing_required_params()

# ** tester: test_set_default_service_registration
@use_tester(
    type='service_event',
    target_cls=SetDefaultServiceRegistration,
    dependencies={
        'di_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'DIService',
        },
    },
    sample_kwargs=dict(
        id='svc_test',
        module_path='new.module',
        class_name='NewClass',
        parameters={'param': 'value'},
    ),
    service_attr='di_service',
    not_found_error_code=a.error.SERVICE_REGISTRATION_NOT_FOUND_ID,
    not_found_kwargs=dict(
        id='missing',
        module_path='mod',
        class_name='Cls',
    ),
)
class TestSetDefaultServiceRegistration:
    '''
    Tests for SetDefaultServiceRegistration using the domain event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, service_registration_aggregate) -> dict:
        '''
        Override to pre-configure get_registration to return the fixture.
        '''

        # Create the mock DI service.
        service = mock.Mock(spec=DIService)
        service.get_registration.return_value = service_registration_aggregate
        return {'di_service': service}

    # * test: full_update
    def test_full_update(self, test_ctx, mock_dependencies, service_registration_aggregate):
        '''
        Test updating both default type and parameters.
        '''

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Assert the registration was updated.
        assert result is service_registration_aggregate
        assert result.module_path == 'new.module'
        assert result.class_name == 'NewClass'
        assert result.parameters == {'param': 'value'}

        # Assert the service was called to save.
        mock_dependencies['di_service'].save_registration.assert_called_once_with(result)

    # * test: parameters_only
    def test_parameters_only(self, test_ctx, mock_dependencies, service_registration_aggregate):
        '''
        Test updating only parameters when module_path and class_name are not provided.
        '''

        # Execute with no type update, just parameters.
        result = test_ctx.handle(
            mock_dependencies,
            module_path=None,
            class_name=None,
            parameters={'param_1': 'updated', 'drop': None},
        )

        # Default type should remain unchanged.
        assert result.module_path == 'tiferet.repos.example'
        assert result.class_name == 'ExampleRepository'
        # Parameters should be cleaned via set_default_type.
        assert result.parameters == {'param_1': 'updated'}

    # * test: clear_parameters
    def test_clear_parameters(self, test_ctx, mock_dependencies, service_registration_aggregate):
        '''
        Test clearing parameters when parameters is None.
        '''

        # Execute with parameters=None to clear.
        result = test_ctx.handle(
            mock_dependencies,
            module_path=None,
            class_name=None,
            parameters=None,
        )

        # Parameters should be cleared.
        assert result.parameters == {}
        assert result.module_path == 'tiferet.repos.example'

    # * test: incomplete_type
    def test_incomplete_type(self, test_ctx, mock_dependencies):
        '''
        Test that providing only one of module_path or class_name raises an error.
        '''

        # Execute with only module_path (no class_name).
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(
                mock_dependencies,
                module_path='new.module',
                class_name=None,
                parameters={'param': 'value'},
            )

        assert exc_info.value.error_code == a.error.INVALID_SERVICE_REGISTRATION_ID

    # * test: not_found
    def test_not_found(self, test_ctx, mock_dependencies):
        '''
        Test that the event raises SERVICE_REGISTRATION_NOT_FOUND when
        the DI service returns None.
        '''

        # Configure the service mock to return None.
        mock_dependencies['di_service'].get_registration.return_value = None

        # Execute and expect the not-found error.
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(mock_dependencies, **test_ctx.domain.not_found_kwargs)

        assert exc_info.value.error_code == a.error.SERVICE_REGISTRATION_NOT_FOUND_ID

# ** tester: test_set_service_dependency
@use_tester(
    type='service_event',
    target_cls=SetServiceDependency,
    dependencies={
        'di_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'DIService',
        },
    },
    sample_kwargs=dict(
        id='svc_test',
        flag='alpha',
        module_path='tiferet.repos.example',
        class_name='ExampleAlpha',
        parameters={'param': 'value'},
    ),
    required_params=['flag'],
    service_attr='di_service',
    not_found_error_code=a.error.SERVICE_REGISTRATION_NOT_FOUND_ID,
    not_found_kwargs=dict(
        id='missing',
        flag='alpha',
        module_path='tiferet.repos.example',
        class_name='ExampleAlpha',
    ),
)
class TestSetServiceDependency:
    '''
    Tests for SetServiceDependency using the domain event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, service_registration_aggregate) -> dict:
        '''
        Override to pre-configure get_registration to return the fixture.
        '''

        # Create the mock DI service.
        service = mock.Mock(spec=DIService)
        service.get_registration.return_value = service_registration_aggregate
        return {'di_service': service}

    # * test: add_new
    def test_add_new(self, test_ctx, mock_dependencies, service_registration_aggregate):
        '''
        Test adding a new flagged dependency when the flag does not yet exist.
        '''

        # Remove existing dependencies to test adding a fresh one.
        service_registration_aggregate.dependencies = []

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Assert the dependency was added.
        assert result == 'svc_test'
        dep = service_registration_aggregate.get_dependency('alpha')
        assert dep is not None
        assert dep.module_path == 'tiferet.repos.example'
        assert dep.class_name == 'ExampleAlpha'
        assert dep.parameters == {'param': 'value'}

        # Assert save was called.
        mock_dependencies['di_service'].save_registration.assert_called_once()

    # * test: update_existing
    def test_update_existing(self, test_ctx, mock_dependencies, service_registration_aggregate):
        '''
        Test updating an existing flagged dependency.
        '''

        # Execute with the same flag as the fixture dependency.
        result = test_ctx.handle(
            mock_dependencies,
            flag='test_alpha',
            module_path='tiferet.repos.updated',
            class_name='UpdatedAlpha',
            parameters={'test_param': 'updated', 'extra': None},
        )

        # Assert the dependency was updated.
        assert result == 'svc_test'
        dep = service_registration_aggregate.get_dependency('test_alpha')
        assert dep.module_path == 'tiferet.repos.updated'
        assert dep.class_name == 'UpdatedAlpha'
        # Parameters should be cleaned (None removed) and merged.
        assert dep.parameters == {
            'test_param': 'updated',
            'param': 'value1',
        }

    # * test: incomplete_type
    def test_incomplete_type(self, test_ctx, mock_dependencies):
        '''
        Test that providing an empty class_name raises INVALID_FLAGGED_DEPENDENCY.
        '''

        # Execute with an empty class_name.
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(
                mock_dependencies,
                flag='alpha',
                module_path='tiferet.repos.example',
                class_name='',
            )

        assert exc_info.value.error_code == a.error.INVALID_FLAGGED_DEPENDENCY_ID

    # * test: not_found
    def test_not_found(self, test_ctx, mock_dependencies):
        '''
        Test that the event raises SERVICE_REGISTRATION_NOT_FOUND when
        the DI service returns None.
        '''

        # Configure the service mock to return None.
        mock_dependencies['di_service'].get_registration.return_value = None

        # Execute and expect the not-found error.
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(mock_dependencies, **test_ctx.domain.not_found_kwargs)

        assert exc_info.value.error_code == a.error.SERVICE_REGISTRATION_NOT_FOUND_ID

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        test_ctx.assert_missing_required_params()

# ** tester: test_remove_service_dependency
@use_tester(
    type='service_event',
    target_cls=RemoveServiceDependency,
    dependencies={
        'di_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'DIService',
        },
    },
    sample_kwargs=dict(
        id='svc_test',
        flag='test_alpha',
    ),
    required_params=['flag'],
    service_attr='di_service',
    not_found_error_code=a.error.SERVICE_REGISTRATION_NOT_FOUND_ID,
    not_found_kwargs=dict(
        id='missing_attr',
        flag='alpha',
    ),
)
class TestRemoveServiceDependency:
    '''
    Tests for RemoveServiceDependency using the domain event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, service_registration_aggregate) -> dict:
        '''
        Override to pre-configure get_registration to return the fixture.
        '''

        # Create the mock DI service.
        service = mock.Mock(spec=DIService)
        service.get_registration.return_value = service_registration_aggregate
        return {'di_service': service}

    # * test: success_with_remaining_default
    def test_success_with_remaining_default(self, test_ctx, mock_dependencies, service_registration_aggregate):
        '''
        Test removing a dependency while a default type remains configured.
        '''

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Assert the dependency was removed but default type remains.
        assert result == 'svc_test'
        assert service_registration_aggregate.get_dependency('test_alpha') is None
        assert service_registration_aggregate.module_path == 'tiferet.repos.example'
        assert service_registration_aggregate.class_name == 'ExampleRepository'

        # Assert save was called.
        mock_dependencies['di_service'].save_registration.assert_called_once()

    # * test: nonexistent_flag
    def test_nonexistent_flag(self, test_ctx, mock_dependencies, service_registration_aggregate):
        '''
        Test removing a non-existent flag is idempotent when type sources remain.
        '''

        # Execute with a flag that doesn't exist.
        result = test_ctx.handle(mock_dependencies, flag='non_existent_flag')

        # Dependencies and default type remain unchanged.
        assert result == 'svc_test'
        assert service_registration_aggregate.get_dependency('test_alpha') is not None
        assert service_registration_aggregate.module_path == 'tiferet.repos.example'

    # * test: invalid_after_removal
    def test_invalid_after_removal(self, test_ctx, mock_dependencies, flagged_dependency_for_di):
        '''
        Test that removing the last type source raises INVALID_SERVICE_REGISTRATION.
        '''

        # Create a registration with only a dependency and no default type.
        config = ServiceRegistrationAggregate(
            id='svc_only_deps',
            dependencies=[flagged_dependency_for_di],
            parameters={},
        )
        mock_dependencies['di_service'].get_registration.return_value = config

        # Execute and expect INVALID_SERVICE_REGISTRATION.
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(mock_dependencies, id='svc_only_deps', flag='test_alpha')

        assert exc_info.value.error_code == a.error.INVALID_SERVICE_REGISTRATION_ID

    # * test: not_found
    def test_not_found(self, test_ctx, mock_dependencies):
        '''
        Test that the event raises SERVICE_REGISTRATION_NOT_FOUND when
        the DI service returns None.
        '''

        # Configure the service mock to return None.
        mock_dependencies['di_service'].get_registration.return_value = None

        # Execute and expect the not-found error.
        with pytest.raises(TiferetError) as exc_info:
            test_ctx.handle(mock_dependencies, **test_ctx.domain.not_found_kwargs)

        assert exc_info.value.error_code == a.error.SERVICE_REGISTRATION_NOT_FOUND_ID

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        test_ctx.assert_missing_required_params()

# ** tester: test_remove_service_registration
@use_tester(
    type='domain_event',
    target_cls=RemoveServiceRegistration,
    dependencies={
        'di_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'DIService',
        },
    },
    sample_kwargs=dict(id='svc_to_delete'),
    required_params=['id'],
)
class TestRemoveServiceRegistration:
    '''
    Tests for RemoveServiceRegistration using the domain event test harness.
    '''

    # * test: existing
    def test_existing(self, test_ctx):
        '''
        Test removing an existing service registration.
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Assert the result is the deleted ID.
        assert result == 'svc_to_delete'
        mock_dependencies['di_service'].delete_registration.assert_called_once_with('svc_to_delete')

    # * test: nonexistent_is_idempotent
    def test_nonexistent_is_idempotent(self, test_ctx):
        '''
        Test that removing a non-existent registration is idempotent.
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Execute with a non-existent ID.
        result = test_ctx.handle(mock_dependencies, id='missing_id')

        # Assert the result is the ID and delete was called.
        assert result == 'missing_id'
        mock_dependencies['di_service'].delete_registration.assert_called_once_with('missing_id')

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        mock_dependencies = test_ctx.mock_dependencies()

        test_ctx.assert_missing_required_params()

# ** tester: test_set_service_constants
@use_tester(
    type='domain_event',
    target_cls=SetServiceConstants,
    dependencies={
        'di_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'DIService',
        },
    },
    sample_kwargs=dict(constants={'key': 'value'}),
)
class TestSetServiceConstants:
    '''
    Tests for SetServiceConstants using the domain event test harness.
    '''

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self) -> dict:
        '''
        Override to pre-configure list_all to return existing constants.
        '''

        # Create the mock DI service with existing constants.
        service = mock.Mock(spec=DIService)
        service.list_all.return_value = ([], {'existing': 'old'})
        return {'di_service': service}

    # * test: clear_all_with_none
    def test_clear_all_with_none(self, test_ctx, mock_dependencies):
        '''
        Test clearing all constants when None is passed.
        '''

        # Execute with constants=None.
        result = test_ctx.handle(mock_dependencies, constants=None)

        # Assert all constants were cleared.
        assert result == {}
        mock_dependencies['di_service'].save_constants.assert_called_once_with({})

    # * test: partial_removal
    def test_partial_removal(self, test_ctx, mock_dependencies):
        '''
        Test removing keys with None values while preserving others.
        '''

        # Configure existing constants with a key to remove.
        mock_dependencies['di_service'].list_all.return_value = (
            [],
            {'keep': 'value', 'remove': 'to_delete'},
        )

        # Execute with a removal.
        result = test_ctx.handle(mock_dependencies, constants={'remove': None})

        # Assert only the kept key remains.
        assert result == {'keep': 'value'}
        mock_dependencies['di_service'].save_constants.assert_called_once_with({'keep': 'value'})

    # * test: add_new
    def test_add_new(self, test_ctx, mock_dependencies):
        '''
        Test adding new constants on top of existing ones.
        '''

        # Execute with a new constant.
        result = test_ctx.handle(mock_dependencies, constants={'new': 'value'})

        # Assert both existing and new constants are present.
        assert result == {'existing': 'old', 'new': 'value'}
        mock_dependencies['di_service'].save_constants.assert_called_once_with(
            {'existing': 'old', 'new': 'value'}
        )

    # * test: update_existing
    def test_update_existing(self, test_ctx, mock_dependencies):
        '''
        Test updating existing constant values.
        '''

        # Execute with an updated constant.
        result = test_ctx.handle(mock_dependencies, constants={'existing': 'new'})

        # Assert the constant was updated.
        assert result == {'existing': 'new'}
        mock_dependencies['di_service'].save_constants.assert_called_once_with({'existing': 'new'})

    # * test: mixed_operations
    def test_mixed_operations(self, test_ctx, mock_dependencies):
        '''
        Test adding, updating, and removing constants in a single call.
        '''

        # Configure multiple existing constants.
        mock_dependencies['di_service'].list_all.return_value = (
            [],
            {'keep': 'value', 'remove': 'to_delete', 'update': 'old'},
        )

        # Execute with mixed operations.
        result = test_ctx.handle(
            mock_dependencies,
            constants={
                'remove': None,
                'update': 'new',
                'add': 'added',
            },
        )

        # Assert the expected result.
        expected = {'keep': 'value', 'update': 'new', 'add': 'added'}
        assert result == expected
        mock_dependencies['di_service'].save_constants.assert_called_once_with(expected)

    # * test: empty_dict
    def test_empty_dict(self, test_ctx, mock_dependencies):
        '''
        Test that an empty dict is idempotent (no changes).
        '''

        # Execute with an empty dict.
        result = test_ctx.handle(mock_dependencies, constants={})

        # Assert existing constants remain unchanged.
        assert result == {'existing': 'old'}
        mock_dependencies['di_service'].save_constants.assert_called_once_with({'existing': 'old'})

    # * test: omitted_is_noop
    def test_omitted_is_noop(self, test_ctx, mock_dependencies):
        '''
        Test that omitting the constants argument preserves existing
        constants (the sentinel default is a no-op on omit, distinct from
        an explicit None which clears all).
        '''

        # Execute without passing the constants argument at all.
        result = DomainEvent.handle(
            SetServiceConstants,
            dependencies=mock_dependencies,
        )

        # Assert existing constants are returned and persisted unchanged.
        assert result == {'existing': 'old'}
        mock_dependencies['di_service'].save_constants.assert_called_once_with({'existing': 'old'})

# ** tester: test_list_all_settings
@use_tester(
    type='domain_event',
    target_cls=ListAllSettings,
    dependencies={
        'di_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'DIService',
        },
    },
    sample_kwargs=dict(),
)
class TestListAllSettings:
    '''
    Tests for ListAllSettings using the domain event test harness.
    '''

    # * test: calls_list_all
    def test_calls_list_all(self, test_ctx, service_registration_aggregate):
        '''
        Test that ListAllSettings delegates to the DI service list_all method.
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Configure the service to return a registration and constants.
        expected = ([service_registration_aggregate], {'constant_1': 'value'})
        mock_dependencies['di_service'].list_all.return_value = expected

        # Execute via the harness handle helper.
        result = test_ctx.handle(mock_dependencies)

        # Assert the result matches the expected tuple.
        assert result == expected
        mock_dependencies['di_service'].list_all.assert_called_once()

