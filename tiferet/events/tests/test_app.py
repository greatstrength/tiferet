"""Tiferet App Commands Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ..app import (
    GetAppInterface,
    AddAppInterface,
    ListAppInterfaces,
    UpdateAppInterface,
    SetAppConstants,
    SetServiceDependency,
    RemoveServiceDependency,
    RemoveAppInterface,
)
from ..settings import TiferetError, DomainEvent, a
from ...domain import (
    AppInterface,
    AppServiceDependency,
    DomainObject,
)
from ...interfaces import AppService
from ...mappers import Aggregate, AppInterfaceAggregate
from .settings import DomainEventTestBase, ServiceEventTestBase


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
    return Aggregate.new(
        AppInterfaceAggregate,
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
        description='The test app.',
        flags=['test'],
        services=[
            DomainObject.new(
                AppServiceDependency,
                service_id='test_service',
                module_path='test_module_path',
                class_name='test_class_name',
            ),
        ],
        constants={},  # ensure constants dict exists
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

    # * method: test_with_default_constants
    def test_with_default_constants(self, mock_dependencies, app_interface):
        '''
        Test that default_constants are properly merged via set_constants().
        '''

        mock_dependencies['app_service'].get.return_value = app_interface

        default_constants = {
            'cli_yaml_file': 'config.yml',
            'error_yaml_file': 'config.yml',
        }

        result = self.handle(
            mock_dependencies,
            default_constants=default_constants
        )

        # The interface should have received the constants via set_constants
        assert result.constants == default_constants

    # * method: test_with_default_services_and_constants
    def test_with_default_services_and_constants(self, mock_dependencies, app_interface):
        '''
        Test merging both default_services and default_constants.
        '''

        mock_dependencies['app_service'].get.return_value = app_interface

        default_services = [
            DomainObject.new(
                AppServiceDependency,
                service_id='new_service',
                module_path='tiferet.repos.new',
                class_name='NewRepo',
            )
        ]

        default_constants = {'feature_yaml_file': 'config.yml'}

        result = self.handle(
            mock_dependencies,
            default_services=default_services,
            default_constants=default_constants
        )

        # Verify default service was added (since it didn't exist)
        assert any(dep.service_id == 'new_service' for dep in result.services)

        # Verify constants were merged
        assert result.constants == default_constants


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
        another_interface = Aggregate.new(
            AppInterfaceAggregate,
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