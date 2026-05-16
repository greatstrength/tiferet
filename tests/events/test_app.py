"""Tiferet App Commands Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events.app import (
    GetAppInterface,
    AddAppInterface,
    ListAppInterfaces,
    UpdateAppInterface,
    SetAppConstants,
    SetServiceDependency,
    RemoveServiceDependency,
    RemoveAppInterface,
)
from tiferet.events.settings import TiferetError, DomainEvent, a
from tiferet.domain import (
    AppInterface,
    AppServiceDependency,
)
from tiferet.interfaces import AppService
from tiferet.mappers import AppInterfaceAggregate
from tiferet_testing import DomainEventTestBase, ServiceEventTestBase

# *** fixtures

# ** fixture: app_interface
@pytest.fixture
def app_interface():
    '''
    Fixture to create an AppInterface aggregate for testing.

    :return: An AppInterfaceAggregate instance.
    :rtype: AppInterfaceAggregate
    '''

    # Create a test AppInterface instance.
    return AppInterfaceAggregate(
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
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

# ** test: TestAddAppInterface
class TestAddAppInterface(DomainEventTestBase):
    '''
    Tests for AddAppInterface using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = AddAppInterface

    # * attribute: dependencies
    dependencies = {'app_service': AppService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='test.interface',
        name='Test Interface',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
    )

    # * attribute: required_params
    required_params = ['id', 'name', 'module_path', 'class_name']

    # * method: test_minimal_success
    def test_minimal_success(self, mock_dependencies):
        '''
        Test creating a minimal app interface with only required parameters.
        '''

        # Execute via the harness handle helper.
        interface = self.handle(mock_dependencies)

        # Assert the result is an AppInterface instance with expected defaults.
        assert isinstance(interface, AppInterface)
        assert interface.id == 'test.interface'
        assert interface.name == 'Test Interface'
        assert interface.module_path == 'tiferet.contexts.app'
        assert interface.class_name == 'AppContext'
        assert interface.description is None
        assert interface.logger_id == 'default'
        assert interface.flags == ['default']
        assert interface.services == []
        assert interface.constants == {}

        # Assert the interface is saved via the app service.
        mock_dependencies['app_service'].save.assert_called_once_with(interface)

    # * method: test_full_parameters
    def test_full_parameters(self, mock_dependencies):
        '''
        Test creating an app interface with all parameters populated.
        '''

        # Execute via the harness handle helper with full parameters.
        interface = self.handle(
            mock_dependencies,
            description='A test app interface.',
            logger_id='test_logger',
            flags=['test_feature', 'test_data'],
            services=[
                {
                    'service_id': 'svc1',
                    'module_path': 'test.module',
                    'class_name': 'TestClass',
                    'parameters': {'foo': 'bar'},
                }
            ],
            constants={'CONST_KEY': 'VALUE'},
        )

        # Assert core fields.
        assert isinstance(interface, AppInterface)
        assert interface.id == 'test.interface'
        assert interface.description == 'A test app interface.'
        assert interface.logger_id == 'test_logger'
        assert interface.flags == ['test_feature', 'test_data']
        assert interface.constants == {'CONST_KEY': 'VALUE'}

        # Assert services are materialized as AppServiceDependency models.
        assert len(interface.services) == 1
        svc = interface.services[0]
        assert isinstance(svc, AppServiceDependency)
        assert svc.service_id == 'svc1'
        assert svc.module_path == 'test.module'
        assert svc.class_name == 'TestClass'
        assert svc.parameters == {'foo': 'bar'}

        # Assert the interface is saved.
        mock_dependencies['app_service'].save.assert_called_once()

    # * method: test_default_fallbacks
    def test_default_fallbacks(self, mock_dependencies):
        '''
        Test that logger_id and flags fall back to defaults.
        '''

        # Execute via the harness handle helper with defaults.
        interface = self.handle(mock_dependencies)

        # All flags should be normalized to 'default'.
        assert interface.logger_id == 'default'
        assert interface.flags == ['default']

        # Assert the interface is saved.
        mock_dependencies['app_service'].save.assert_called_once_with(interface)


# ** test: TestGetAppInterface
class TestGetAppInterface(ServiceEventTestBase):
    '''
    Tests for GetAppInterface using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = GetAppInterface

    # * attribute: dependencies
    dependencies = {'app_service': AppService}

    # * attribute: service_attr
    service_attr = 'app_service'

    # * attribute: sample_kwargs
    sample_kwargs = dict(interface_id='test')

    # * attribute: required_params
    required_params = ['interface_id']

    # * attribute: not_found_error_code
    not_found_error_code = a.const.APP_INTERFACE_NOT_FOUND_ID

    # * attribute: not_found_kwargs
    not_found_kwargs = dict(interface_id='non_existent_id')

    # * method: test_success
    def test_success(self, mock_dependencies, app_interface):
        '''
        Test successful retrieval of an app interface.
        '''

        # Configure the service mock to return the app interface.
        mock_dependencies['app_service'].get.return_value = app_interface

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Assert that the returned interface matches the expected app interface.
        assert result == app_interface

    # * method: test_merges_missing_default_services_only
    def test_merges_missing_default_services_only(self, mock_dependencies, app_interface):
        '''
        Test that default services are merged only when service_id is missing.
        '''

        # Configure the service mock to return the app interface.
        mock_dependencies['app_service'].get.return_value = app_interface

        # Create default services with one duplicate and one missing service_id.
        default_services = [
            AppServiceDependency(
                service_id='test_service',
                module_path='ignored.module',
                class_name='IgnoredClass',
                parameters={'ignored': 'value'},
            ),
            AppServiceDependency(
                service_id='new_service',
                module_path='new.module',
                class_name='NewClass',
                parameters={'new': 'value'},
            ),
        ]

        # Execute the event with default services.
        result = self.handle(
            mock_dependencies,
            default_services=default_services,
        )

        # Assert the existing dependency remains and only the missing dependency is added.
        assert result.get_service('test_service').module_path == 'test_module_path'
        assert result.get_service('new_service').module_path == 'new.module'
        assert len(result.services) == 2

    # * method: test_merges_missing_default_constants_only
    def test_merges_missing_default_constants_only(self, mock_dependencies, app_interface):
        '''
        Test that default constants are merged without overwriting existing values.
        '''

        # Configure the service mock to return the app interface.
        mock_dependencies['app_service'].get.return_value = app_interface

        # Seed interface constants with an existing key that should be preserved.
        app_interface.constants = {
            'di_yaml_file': 'custom.yml',
            'custom_key': 'custom_value',
        }

        # Execute the event with default constants.
        result = self.handle(
            mock_dependencies,
            default_constants={
                'di_yaml_file': 'config.yml',
                'feature_yaml_file': 'config.yml',
            },
        )

        # Assert existing keys are preserved and missing keys are added.
        assert result.constants['di_yaml_file'] == 'custom.yml'
        assert result.constants['feature_yaml_file'] == 'config.yml'
        assert result.constants['custom_key'] == 'custom_value'

    # * method: test_converts_to_aggregate_and_merges_services_and_constants
    def test_converts_to_aggregate_and_merges_services_and_constants(self, mock_dependencies):
        '''
        Test aggregate conversion before applying default services and constants.
        '''

        # Configure the service mock to return a plain AppInterface domain object.
        domain_interface = AppInterface(
            id='test.interface',
            name='Test Interface',
            module_path='tiferet.contexts.app',
            class_name='AppContext',
            services=[
                AppServiceDependency(
                    service_id='existing_service',
                    module_path='existing.module',
                    class_name='ExistingClass',
                    parameters={},
                ),
            ],
            constants={'di_yaml_file': 'custom.yml'},
        )
        mock_dependencies['app_service'].get.return_value = domain_interface

        # Execute the event with both defaults provided.
        result = self.handle(
            mock_dependencies,
            interface_id='test.interface',
            default_services=[
                AppServiceDependency(
                    service_id='new_service',
                    module_path='new.module',
                    class_name='NewClass',
                    parameters={'key': 'value'},
                ),
            ],
            default_constants={
                'di_yaml_file': 'config.yml',
                'feature_yaml_file': 'config.yml',
            },
        )

        # Assert conversion to aggregate and correct merge behavior.
        assert isinstance(result, AppInterfaceAggregate)
        assert result.get_service('existing_service') is not None
        assert result.get_service('new_service') is not None
        assert result.constants['di_yaml_file'] == 'custom.yml'
        assert result.constants['feature_yaml_file'] == 'config.yml'


# ** test: TestListAppInterfaces
class TestListAppInterfaces(DomainEventTestBase):
    '''
    Tests for ListAppInterfaces using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = ListAppInterfaces

    # * attribute: dependencies
    dependencies = {'app_service': AppService}

    # * attribute: sample_kwargs
    sample_kwargs = dict()

    # * method: test_empty
    def test_empty(self, mock_dependencies):
        '''
        Test that ListAppInterfaces returns an empty list when no interfaces are configured.
        '''

        # Configure the service to return an empty list.
        mock_dependencies['app_service'].list.return_value = []

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Assert that an empty list is returned and the service was called.
        assert result == []
        mock_dependencies['app_service'].list.assert_called_once_with()

    # * method: test_multiple
    def test_multiple(self, mock_dependencies, app_interface):
        '''
        Test that ListAppInterfaces returns multiple interfaces when configured.
        '''

        # Configure the service to return multiple interfaces.
        another_interface = AppInterfaceAggregate(
            id='other',
            name='Other App',
            module_path='tiferet.contexts.app',
            class_name='OtherAppContext',
        )
        mock_dependencies['app_service'].list.return_value = [app_interface, another_interface]

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Assert that the returned list matches the configured interfaces.
        assert result == [app_interface, another_interface]
        mock_dependencies['app_service'].list.assert_called_once_with()


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
    not_found_error_code = a.const.APP_INTERFACE_NOT_FOUND_ID

    # * attribute: not_found_kwargs
    not_found_kwargs = dict(
        id='missing.interface',
        service_id='dep',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
    )

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, app_interface):
        '''
        Override to provide a service mock pre-configured with an app_interface.
        '''

        # Create a mock AppService that returns the app_interface on get.
        service = mock.Mock(spec=AppService)
        service.get.return_value = app_interface
        return {'app_service': service}

    # * method: test_creates_new_service
    def test_creates_new_service(self, mock_dependencies, app_interface):
        '''
        Test that SetServiceDependency creates a new dependency when it does not exist.
        '''

        # Ensure no service with the target id exists initially.
        assert app_interface.get_service('new_dependency') is None

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies, parameters={'param1': 'value1'})

        # Command should return the interface id.
        assert result == app_interface.id

        # A new service dependency should be created with the provided values.
        new_svc = app_interface.get_service('new_dependency')
        assert new_svc is not None
        assert new_svc.module_path == 'new.module.path'
        assert new_svc.class_name == 'NewClass'
        assert new_svc.parameters == {'param1': 'value1'}

        # The updated interface should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

    # * method: test_updates_existing_and_merges_parameters
    def test_updates_existing_and_merges_parameters(self, mock_dependencies, app_interface):
        '''
        Test that SetServiceDependency updates an existing dependency and merges parameters.
        '''

        # Precondition: existing service from fixture.
        existing_svc = app_interface.get_service('test_service')
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

        # Command should return the interface id.
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

        # The updated interface should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

    # * method: test_parameters_none_clears_existing
    def test_parameters_none_clears_existing(self, mock_dependencies, app_interface):
        '''
        Test that passing parameters=None clears existing parameters.
        '''

        # Precondition: existing service has parameters.
        existing_svc = app_interface.get_service('test_service')
        existing_svc.parameters = {'key': 'value'}

        # Execute via the harness handle helper with parameters=None.
        result = self.handle(
            mock_dependencies,
            service_id='test_service',
            module_path='tiferet.contexts.app',
            class_name='AppContext',
            parameters=None,
        )

        # Command should return the interface id.
        assert result == app_interface.id

        # Parameters should be cleared.
        cleared_svc = app_interface.get_service('test_service')
        assert cleared_svc.parameters == {}

        # The updated interface should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

# ** test: TestUpdateAppInterface
class TestUpdateAppInterface(ServiceEventTestBase):
    '''
    Tests for UpdateAppInterface using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = UpdateAppInterface

    # * attribute: dependencies
    dependencies = {'app_service': AppService}

    # * attribute: service_attr
    service_attr = 'app_service'

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='test',
        attribute='name',
        value='Updated Name',
    )

    # * attribute: required_params
    required_params = ['id', 'attribute']

    # * attribute: not_found_error_code
    not_found_error_code = a.const.APP_INTERFACE_NOT_FOUND_ID

    # * attribute: not_found_kwargs
    not_found_kwargs = dict(
        id='missing.interface',
        attribute='name',
        value='Updated Name',
    )

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, app_interface):
        '''
        Override to provide a service mock pre-configured with an app_interface.
        '''

        # Create a mock AppService that returns the app_interface on get.
        service = mock.Mock(spec=AppService)
        service.get.return_value = app_interface
        return {'app_service': service}

    # * method: test_success_supported_attributes
    @pytest.mark.parametrize(
        'attribute,new_value',
        [
            ('name', 'Updated Name'),
            ('description', 'Updated description'),
            ('module_path', 'updated.module.path'),
            ('class_name', 'UpdatedClass'),
            ('logger_id', 'updated_logger'),
            ('flags', ['updated_flags']),
        ],
    )
    def test_success_supported_attributes(
        self, mock_dependencies, app_interface, attribute, new_value
    ):
        '''
        Test updating each supported scalar attribute via UpdateAppInterface.
        '''

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies, id=app_interface.id, attribute=attribute, value=new_value)

        # Command should return the interface id.
        assert result == app_interface.id

        # The attribute on the interface should be updated.
        assert getattr(app_interface, attribute) == new_value

        # The updated interface should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

    # * method: test_invalid_attribute_raises_model_error
    def test_invalid_attribute_raises_model_error(self, mock_dependencies, app_interface):
        '''
        Test that an invalid attribute name raises INVALID_MODEL_ATTRIBUTE.
        '''

        # Execute the command with an unsupported attribute name.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, id=app_interface.id, attribute='invalid_attribute', value='value')

        # The underlying model validation should raise INVALID_MODEL_ATTRIBUTE.
        assert exc_info.value.error_code == a.const.INVALID_MODEL_ATTRIBUTE_ID
        mock_dependencies['app_service'].save.assert_not_called()

    # * method: test_invalid_type_attributes_empty_value
    @pytest.mark.parametrize('attribute', ['module_path', 'class_name'])
    def test_invalid_type_attributes_empty_value(self, mock_dependencies, app_interface, attribute):
        '''
        Test that empty values for module_path or class_name are rejected by the model.
        '''

        # Execute the command with an empty value for a type-constrained attribute.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, id=app_interface.id, attribute=attribute, value='')

        # The underlying model validation should raise INVALID_APP_INTERFACE_TYPE.
        assert exc_info.value.error_code == a.const.INVALID_APP_INTERFACE_TYPE_ID
        mock_dependencies['app_service'].save.assert_not_called()

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
    not_found_error_code = a.const.APP_INTERFACE_NOT_FOUND_ID

    # * attribute: not_found_kwargs
    not_found_kwargs = dict(
        id='missing.interface',
        constants={'KEY': 'VALUE'},
    )

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, app_interface):
        '''
        Override to provide a service mock pre-configured with an app_interface.
        '''

        # Create a mock AppService that returns the app_interface on get.
        service = mock.Mock(spec=AppService)
        service.get.return_value = app_interface
        return {'app_service': service}

    # * method: test_full_clear
    def test_full_clear(self, mock_dependencies, app_interface):
        '''
        Test that SetAppConstants clears all constants when constants=None.
        '''

        # Seed existing constants on the interface.
        app_interface.constants = {
            'EXISTING': 'value',
            'OTHER': 'other_value',
        }

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies, constants=None)

        # Command should return the interface id.
        assert result == app_interface.id

        # All constants should be cleared.
        assert app_interface.constants == {}

        # The updated interface should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

    # * method: test_merge_override_and_remove
    def test_merge_override_and_remove(self, mock_dependencies, app_interface):
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
        result = self.handle(
            mock_dependencies,
            constants={
                'OVERRIDE': 'new',
                'REMOVE': None,
                'ADD': 'added',
            },
        )

        # Command should return the interface id.
        assert result == app_interface.id

        # Constants should be merged/updated with None-valued keys removed.
        assert app_interface.constants == {
            'KEEP': 'keep_value',
            'OVERRIDE': 'new',
            'ADD': 'added',
        }

        # The updated interface should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

    # * method: test_add_new_constants
    def test_add_new_constants(self, mock_dependencies, app_interface):
        '''
        Test that SetAppConstants adds new constants when none exist.
        '''

        # Precondition: no constants defined.
        assert app_interface.constants == {}

        # Execute via the harness handle helper with new constants.
        result = self.handle(
            mock_dependencies,
            constants={
                'NEW_ONE': 'one',
                'NEW_TWO': 'two',
            },
        )

        # Command should return the interface id.
        assert result == app_interface.id

        # All new constants should be present.
        assert app_interface.constants == {
            'NEW_ONE': 'one',
            'NEW_TWO': 'two',
        }

        # The updated interface should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)


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
    not_found_error_code = a.const.APP_INTERFACE_NOT_FOUND_ID

    # * attribute: not_found_kwargs
    not_found_kwargs = dict(
        id='missing.interface',
        service_id='dep',
    )

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self, app_interface):
        '''
        Override to provide a service mock pre-configured with an app_interface.
        '''

        # Create a mock AppService that returns the app_interface on get.
        service = mock.Mock(spec=AppService)
        service.get.return_value = app_interface
        return {'app_service': service}

    # * method: test_removes_existing
    def test_removes_existing(self, mock_dependencies, app_interface):
        '''
        Test that RemoveServiceDependency removes an existing service dependency.
        '''

        # Precondition: the service dependency exists on the interface.
        existing_svc = app_interface.get_service('test_service')
        assert existing_svc is not None
        initial_count = len(app_interface.services)

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Command should return the interface id.
        assert result == app_interface.id

        # The service dependency should be removed.
        assert app_interface.get_service('test_service') is None
        assert len(app_interface.services) == initial_count - 1

        # The updated interface should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

    # * method: test_missing_service_is_idempotent
    def test_missing_service_is_idempotent(self, mock_dependencies, app_interface):
        '''
        Test that removing a non-existent service dependency is idempotent.
        '''

        # Precondition: no service dependency with the given id exists.
        assert app_interface.get_service('missing_service') is None
        initial_count = len(app_interface.services)

        # Execute via the harness handle helper with a non-existent service id.
        result = self.handle(mock_dependencies, service_id='missing_service')

        # Command should return the interface id.
        assert result == app_interface.id

        # Services list should remain unchanged.
        assert app_interface.get_service('missing_service') is None
        assert len(app_interface.services) == initial_count

        # The updated interface should be saved.
        mock_dependencies['app_service'].save.assert_called_once_with(app_interface)

# ** test: TestRemoveAppInterface
class TestRemoveAppInterface(DomainEventTestBase):
    '''
    Tests for RemoveAppInterface using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = RemoveAppInterface

    # * attribute: dependencies
    dependencies = {'app_service': AppService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(id='existing.interface')

    # * attribute: required_params
    required_params = ['id']

    # * method: test_success_existing
    def test_success_existing(self, mock_dependencies):
        '''
        Test that RemoveAppInterface deletes an existing app interface and returns the ID.
        '''

        # Execute via the harness handle helper.
        result = self.handle(mock_dependencies)

        # Command should return the interface id and delegate deletion to the service.
        assert result == 'existing.interface'
        mock_dependencies['app_service'].delete.assert_called_once_with('existing.interface')

    # * method: test_success_missing_is_idempotent
    def test_success_missing_is_idempotent(self, mock_dependencies):
        '''
        Test that removing a non-existent interface is idempotent and still succeeds.
        '''

        # Execute via the harness handle helper with a different id.
        result = self.handle(mock_dependencies, id='missing.interface')

        # Command should return the interface id and still call delete exactly once.
        assert result == 'missing.interface'
        mock_dependencies['app_service'].delete.assert_called_once_with('missing.interface')
