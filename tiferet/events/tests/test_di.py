"""Tests for Tiferet DI Domain Events"""

# *** imports

# ** core
from typing import Tuple, Dict, Any, List

# ** infra
import pytest
from unittest import mock

# ** app
from ..di import (
    AddServiceConfiguration,
    SetDefaultServiceConfiguration,
    SetServiceDependency,
    RemoveServiceDependency,
    RemoveServiceConfiguration,
    SetServiceConstants,
    ListAllSettings,
)
from ..settings import DomainEvent, TiferetError, a
from ...domain.di import ServiceConfiguration, FlaggedDependency
from ...mappers.di import (
    ServiceConfigurationAggregate,
    FlaggedDependencyAggregate,
)
from ...mappers.settings import Aggregate
from ...interfaces.di import DIService
from .settings import DomainEventTestBase, ServiceEventTestBase

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
    return Aggregate.new(
        FlaggedDependencyAggregate,
        module_path='tiferet.repos.example',
        class_name='ExampleRepository',
        flag='test_alpha',
        parameters={
            'test_param': 'test_value',
            'param': 'value1',
        },
    )

# ** fixture: service_configuration_aggregate
@pytest.fixture
def service_configuration_aggregate(flagged_dependency_for_di) -> ServiceConfigurationAggregate:
    '''
    A service configuration aggregate for DI event tests.

    :param flagged_dependency_for_di: The flagged dependency fixture.
    :type flagged_dependency_for_di: FlaggedDependency
    :return: A ServiceConfigurationAggregate instance.
    :rtype: ServiceConfigurationAggregate
    '''

    # Create a service configuration aggregate with a default type and one dependency.
    return ServiceConfigurationAggregate.new(
        service_configuration_data=dict(
            id='svc_test',
            module_path='tiferet.repos.example',
            class_name='ExampleRepository',
            parameters={'param_1': 'value_1'},
            dependencies=[flagged_dependency_for_di],
        ),
    )

# *** tests

# ** test: TestAddServiceConfiguration
class TestAddServiceConfiguration(DomainEventTestBase):
    '''
    Tests for AddServiceConfiguration using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = AddServiceConfiguration

    # * attribute: dependencies
    dependencies = {'di_service': DIService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='svc_new',
        module_path='tiferet.repos.example',
        class_name='ExampleRepository',
        parameters={'param': 'value'},
        flagged_dependencies=[],
    )

    # * attribute: required_params
    required_params = ['id']

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self) -> dict:
        '''
        Override to pre-configure configuration_exists to return False.
        '''

        # Create the mock DI service.
        service = mock.Mock(spec=DIService)
        service.configuration_exists.return_value = False
        return {'di_service': service}

    # * method: test_default_type_only
    def test_default_type_only(self, mock_dependencies):
        '''
        Test adding a configuration with only a default type.
        '''

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Assert the result is a ServiceConfiguration instance.
        assert isinstance(result, ServiceConfiguration)
        assert result.id == 'svc_new'
        assert result.module_path == 'tiferet.repos.example'
        assert result.class_name == 'ExampleRepository'
        assert result.parameters == {'param': 'value'}
        assert result.dependencies == []

        # Assert the service was called to check existence and save.
        mock_dependencies['di_service'].configuration_exists.assert_called_once_with('svc_new')
        mock_dependencies['di_service'].save_configuration.assert_called_once_with(result)

    # * method: test_dependencies_only
    def test_dependencies_only(self, mock_dependencies):
        '''
        Test adding a configuration with only flagged dependencies.
        '''

        # Execute via the harness with flagged_dependencies and no default type.
        result = self.handle(
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

        # Assert the configuration was created with dependencies.
        assert isinstance(result, ServiceConfiguration)
        assert result.id == 'svc_new'
        assert result.module_path is None
        assert result.class_name is None
        assert len(result.dependencies) == 1

        # Assert the dependency was materialized correctly.
        dep = result.dependencies[0]
        assert dep.flag == 'alpha'
        assert dep.module_path == 'tiferet.repos.example'

    # * method: test_default_and_dependencies
    def test_default_and_dependencies(self, mock_dependencies):
        '''
        Test adding a configuration with both a default type and dependencies.
        '''

        # Execute via the harness with both default type and flagged_dependencies.
        result = self.handle(
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

    # * method: test_duplicate_id
    def test_duplicate_id(self, mock_dependencies):
        '''
        Test that adding a configuration with an existing ID raises an error.
        '''

        # Configure the service to report the ID already exists.
        mock_dependencies['di_service'].configuration_exists.return_value = True

        # Execute and expect a CONFIGURATION_ALREADY_EXISTS error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies)

        assert exc_info.value.error_code == a.const.CONFIGURATION_ALREADY_EXISTS_ID

    # * method: test_no_type_source
    def test_no_type_source(self, mock_dependencies):
        '''
        Test that adding a configuration with no default type and no dependencies fails.
        '''

        # Execute with neither default type nor flagged dependencies.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(
                mock_dependencies,
                module_path=None,
                class_name=None,
                flagged_dependencies=[],
            )

        assert exc_info.value.error_code == a.const.INVALID_SERVICE_CONFIGURATION_ID


# ** test: TestSetDefaultServiceConfiguration
class TestSetDefaultServiceConfiguration(ServiceEventTestBase):
    '''
    Tests for SetDefaultServiceConfiguration using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = SetDefaultServiceConfiguration

    # * attribute: dependencies
    dependencies = {'di_service': DIService}

    # * attribute: service_attr
    service_attr = 'di_service'

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='svc_test',
        module_path='new.module',
        class_name='NewClass',
        parameters={'param': 'value'},
    )

    # * attribute: not_found_error_code
    not_found_error_code = a.const.SERVICE_CONFIGURATION_NOT_FOUND_ID

    # * attribute: not_found_kwargs
    not_found_kwargs = dict(
        id='missing',
        module_path='mod',
        class_name='Cls',
    )

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, service_configuration_aggregate) -> dict:
        '''
        Override to pre-configure get_configuration to return the fixture.
        '''

        # Create the mock DI service.
        service = mock.Mock(spec=DIService)
        service.get_configuration.return_value = service_configuration_aggregate
        return {'di_service': service}

    # * method: test_full_update
    def test_full_update(self, mock_dependencies, service_configuration_aggregate):
        '''
        Test updating both default type and parameters.
        '''

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Assert the configuration was updated.
        assert result is service_configuration_aggregate
        assert result.module_path == 'new.module'
        assert result.class_name == 'NewClass'
        assert result.parameters == {'param': 'value'}

        # Assert the service was called to save.
        mock_dependencies['di_service'].save_configuration.assert_called_once_with(result)

    # * method: test_parameters_only
    def test_parameters_only(self, mock_dependencies, service_configuration_aggregate):
        '''
        Test updating only parameters when module_path and class_name are not provided.
        '''

        # Execute with no type update, just parameters.
        result = self.handle(
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

    # * method: test_clear_parameters
    def test_clear_parameters(self, mock_dependencies, service_configuration_aggregate):
        '''
        Test clearing parameters when parameters is None.
        '''

        # Execute with parameters=None to clear.
        result = self.handle(
            mock_dependencies,
            module_path=None,
            class_name=None,
            parameters=None,
        )

        # Parameters should be cleared.
        assert result.parameters == {}
        assert result.module_path == 'tiferet.repos.example'

    # * method: test_incomplete_type
    def test_incomplete_type(self, mock_dependencies):
        '''
        Test that providing only one of module_path or class_name raises an error.
        '''

        # Execute with only module_path (no class_name).
        with pytest.raises(TiferetError) as exc_info:
            self.handle(
                mock_dependencies,
                module_path='new.module',
                class_name=None,
                parameters={'param': 'value'},
            )

        assert exc_info.value.error_code == a.const.INVALID_SERVICE_CONFIGURATION_ID

    # * method: test_not_found
    def test_not_found(self, mock_dependencies):
        '''
        Test that the event raises SERVICE_CONFIGURATION_NOT_FOUND when
        the DI service returns None.
        '''

        # Configure the service mock to return None.
        mock_dependencies['di_service'].get_configuration.return_value = None

        # Execute and expect the not-found error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, **self.not_found_kwargs)

        assert exc_info.value.error_code == a.const.SERVICE_CONFIGURATION_NOT_FOUND_ID


# ** test: TestSetServiceDependency
class TestSetServiceDependency(ServiceEventTestBase):
    '''
    Tests for SetServiceDependency using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = SetServiceDependency

    # * attribute: dependencies
    dependencies = {'di_service': DIService}

    # * attribute: service_attr
    service_attr = 'di_service'

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='svc_test',
        flag='alpha',
        module_path='tiferet.repos.example',
        class_name='ExampleAlpha',
        parameters={'param': 'value'},
    )

    # * attribute: required_params
    required_params = ['flag']

    # * attribute: not_found_error_code
    not_found_error_code = a.const.SERVICE_CONFIGURATION_NOT_FOUND_ID

    # * attribute: not_found_kwargs
    not_found_kwargs = dict(
        id='missing',
        flag='alpha',
        module_path='tiferet.repos.example',
        class_name='ExampleAlpha',
    )

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, service_configuration_aggregate) -> dict:
        '''
        Override to pre-configure get_configuration to return the fixture.
        '''

        # Create the mock DI service.
        service = mock.Mock(spec=DIService)
        service.get_configuration.return_value = service_configuration_aggregate
        return {'di_service': service}

    # * method: test_add_new
    def test_add_new(self, mock_dependencies, service_configuration_aggregate):
        '''
        Test adding a new flagged dependency when the flag does not yet exist.
        '''

        # Remove existing dependencies to test adding a fresh one.
        service_configuration_aggregate.dependencies = []

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Assert the dependency was added.
        assert result == 'svc_test'
        dep = service_configuration_aggregate.get_dependency('alpha')
        assert dep is not None
        assert dep.module_path == 'tiferet.repos.example'
        assert dep.class_name == 'ExampleAlpha'
        assert dep.parameters == {'param': 'value'}

        # Assert save was called.
        mock_dependencies['di_service'].save_configuration.assert_called_once()

    # * method: test_update_existing
    def test_update_existing(self, mock_dependencies, service_configuration_aggregate):
        '''
        Test updating an existing flagged dependency.
        '''

        # Execute with the same flag as the fixture dependency.
        result = self.handle(
            mock_dependencies,
            flag='test_alpha',
            module_path='tiferet.repos.updated',
            class_name='UpdatedAlpha',
            parameters={'test_param': 'updated', 'extra': None},
        )

        # Assert the dependency was updated.
        assert result == 'svc_test'
        dep = service_configuration_aggregate.get_dependency('test_alpha')
        assert dep.module_path == 'tiferet.repos.updated'
        assert dep.class_name == 'UpdatedAlpha'
        # Parameters should be cleaned (None removed) and merged.
        assert dep.parameters == {
            'test_param': 'updated',
            'param': 'value1',
        }

    # * method: test_incomplete_type
    def test_incomplete_type(self, mock_dependencies):
        '''
        Test that providing an empty class_name raises INVALID_FLAGGED_DEPENDENCY.
        '''

        # Execute with an empty class_name.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(
                mock_dependencies,
                flag='alpha',
                module_path='tiferet.repos.example',
                class_name='',
            )

        assert exc_info.value.error_code == a.const.INVALID_FLAGGED_DEPENDENCY_ID

    # * method: test_not_found
    def test_not_found(self, mock_dependencies):
        '''
        Test that the event raises SERVICE_CONFIGURATION_NOT_FOUND when
        the DI service returns None.
        '''

        # Configure the service mock to return None.
        mock_dependencies['di_service'].get_configuration.return_value = None

        # Execute and expect the not-found error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, **self.not_found_kwargs)

        assert exc_info.value.error_code == a.const.SERVICE_CONFIGURATION_NOT_FOUND_ID


# ** test: TestRemoveServiceDependency
class TestRemoveServiceDependency(ServiceEventTestBase):
    '''
    Tests for RemoveServiceDependency using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = RemoveServiceDependency

    # * attribute: dependencies
    dependencies = {'di_service': DIService}

    # * attribute: service_attr
    service_attr = 'di_service'

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='svc_test',
        flag='test_alpha',
    )

    # * attribute: required_params
    required_params = ['flag']

    # * attribute: not_found_error_code
    not_found_error_code = a.const.SERVICE_CONFIGURATION_NOT_FOUND_ID

    # * attribute: not_found_kwargs
    not_found_kwargs = dict(
        id='missing_attr',
        flag='alpha',
    )

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, service_configuration_aggregate) -> dict:
        '''
        Override to pre-configure get_configuration to return the fixture.
        '''

        # Create the mock DI service.
        service = mock.Mock(spec=DIService)
        service.get_configuration.return_value = service_configuration_aggregate
        return {'di_service': service}

    # * method: test_success_with_remaining_default
    def test_success_with_remaining_default(self, mock_dependencies, service_configuration_aggregate):
        '''
        Test removing a dependency while a default type remains configured.
        '''

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Assert the dependency was removed but default type remains.
        assert result == 'svc_test'
        assert service_configuration_aggregate.get_dependency('test_alpha') is None
        assert service_configuration_aggregate.module_path == 'tiferet.repos.example'
        assert service_configuration_aggregate.class_name == 'ExampleRepository'

        # Assert save was called.
        mock_dependencies['di_service'].save_configuration.assert_called_once()

    # * method: test_nonexistent_flag
    def test_nonexistent_flag(self, mock_dependencies, service_configuration_aggregate):
        '''
        Test removing a non-existent flag is idempotent when type sources remain.
        '''

        # Execute with a flag that doesn't exist.
        result = self.handle(mock_dependencies, flag='non_existent_flag')

        # Dependencies and default type remain unchanged.
        assert result == 'svc_test'
        assert service_configuration_aggregate.get_dependency('test_alpha') is not None
        assert service_configuration_aggregate.module_path == 'tiferet.repos.example'

    # * method: test_invalid_after_removal
    def test_invalid_after_removal(self, mock_dependencies, flagged_dependency_for_di):
        '''
        Test that removing the last type source raises INVALID_SERVICE_CONFIGURATION.
        '''

        # Create a configuration with only a dependency and no default type.
        config = ServiceConfigurationAggregate.new(
            service_configuration_data=dict(
                id='svc_only_deps',
                dependencies=[flagged_dependency_for_di],
                parameters={},
            ),
        )
        mock_dependencies['di_service'].get_configuration.return_value = config

        # Execute and expect INVALID_SERVICE_CONFIGURATION.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, id='svc_only_deps', flag='test_alpha')

        assert exc_info.value.error_code == a.const.INVALID_SERVICE_CONFIGURATION_ID

    # * method: test_not_found
    def test_not_found(self, mock_dependencies):
        '''
        Test that the event raises SERVICE_CONFIGURATION_NOT_FOUND when
        the DI service returns None.
        '''

        # Configure the service mock to return None.
        mock_dependencies['di_service'].get_configuration.return_value = None

        # Execute and expect the not-found error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, **self.not_found_kwargs)

        assert exc_info.value.error_code == a.const.SERVICE_CONFIGURATION_NOT_FOUND_ID


# ** test: TestRemoveServiceConfiguration
class TestRemoveServiceConfiguration(DomainEventTestBase):
    '''
    Tests for RemoveServiceConfiguration using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = RemoveServiceConfiguration

    # * attribute: dependencies
    dependencies = {'di_service': DIService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(id='svc_to_delete')

    # * attribute: required_params
    required_params = ['id']

    # * method: test_existing
    def test_existing(self, mock_dependencies):
        '''
        Test removing an existing service configuration.
        '''

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Assert the result is the deleted ID.
        assert result == 'svc_to_delete'
        mock_dependencies['di_service'].delete_configuration.assert_called_once_with('svc_to_delete')

    # * method: test_nonexistent_is_idempotent
    def test_nonexistent_is_idempotent(self, mock_dependencies):
        '''
        Test that removing a non-existent configuration is idempotent.
        '''

        # Execute with a non-existent ID.
        result = self.handle(mock_dependencies, id='missing_id')

        # Assert the result is the ID and delete was called.
        assert result == 'missing_id'
        mock_dependencies['di_service'].delete_configuration.assert_called_once_with('missing_id')


# ** test: TestSetServiceConstants
class TestSetServiceConstants(DomainEventTestBase):
    '''
    Tests for SetServiceConstants using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = SetServiceConstants

    # * attribute: dependencies
    dependencies = {'di_service': DIService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(constants={'key': 'value'})

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

    # * method: test_clear_all_with_none
    def test_clear_all_with_none(self, mock_dependencies):
        '''
        Test clearing all constants when None is passed.
        '''

        # Execute with constants=None.
        result = self.handle(mock_dependencies, constants=None)

        # Assert all constants were cleared.
        assert result == {}
        mock_dependencies['di_service'].save_constants.assert_called_once_with({})

    # * method: test_partial_removal
    def test_partial_removal(self, mock_dependencies):
        '''
        Test removing keys with None values while preserving others.
        '''

        # Configure existing constants with a key to remove.
        mock_dependencies['di_service'].list_all.return_value = (
            [],
            {'keep': 'value', 'remove': 'to_delete'},
        )

        # Execute with a removal.
        result = self.handle(mock_dependencies, constants={'remove': None})

        # Assert only the kept key remains.
        assert result == {'keep': 'value'}
        mock_dependencies['di_service'].save_constants.assert_called_once_with({'keep': 'value'})

    # * method: test_add_new
    def test_add_new(self, mock_dependencies):
        '''
        Test adding new constants on top of existing ones.
        '''

        # Execute with a new constant.
        result = self.handle(mock_dependencies, constants={'new': 'value'})

        # Assert both existing and new constants are present.
        assert result == {'existing': 'old', 'new': 'value'}
        mock_dependencies['di_service'].save_constants.assert_called_once_with(
            {'existing': 'old', 'new': 'value'}
        )

    # * method: test_update_existing
    def test_update_existing(self, mock_dependencies):
        '''
        Test updating existing constant values.
        '''

        # Execute with an updated constant.
        result = self.handle(mock_dependencies, constants={'existing': 'new'})

        # Assert the constant was updated.
        assert result == {'existing': 'new'}
        mock_dependencies['di_service'].save_constants.assert_called_once_with({'existing': 'new'})

    # * method: test_mixed_operations
    def test_mixed_operations(self, mock_dependencies):
        '''
        Test adding, updating, and removing constants in a single call.
        '''

        # Configure multiple existing constants.
        mock_dependencies['di_service'].list_all.return_value = (
            [],
            {'keep': 'value', 'remove': 'to_delete', 'update': 'old'},
        )

        # Execute with mixed operations.
        result = self.handle(
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

    # * method: test_empty_dict
    def test_empty_dict(self, mock_dependencies):
        '''
        Test that an empty dict is idempotent (no changes).
        '''

        # Execute with an empty dict.
        result = self.handle(mock_dependencies, constants={})

        # Assert existing constants remain unchanged.
        assert result == {'existing': 'old'}
        mock_dependencies['di_service'].save_constants.assert_called_once_with({'existing': 'old'})


# ** test: TestListAllSettings
class TestListAllSettings(DomainEventTestBase):
    '''
    Tests for ListAllSettings using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = ListAllSettings

    # * attribute: dependencies
    dependencies = {'di_service': DIService}

    # * attribute: sample_kwargs
    sample_kwargs = dict()

    # * method: test_calls_list_all
    def test_calls_list_all(self, mock_dependencies, service_configuration_aggregate):
        '''
        Test that ListAllSettings delegates to the DI service list_all method.
        '''

        # Configure the service to return a configuration and constants.
        expected = ([service_configuration_aggregate], {'constant_1': 'value'})
        mock_dependencies['di_service'].list_all.return_value = expected

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Assert the result matches the expected tuple.
        assert result == expected
        mock_dependencies['di_service'].list_all.assert_called_once()
