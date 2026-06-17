"""Tests for Tiferet Domain App"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.domain.settings import DomainObject
from tiferet.domain.app import (
    AppInterface,
    AppServiceDependency,
)
from tiferet.di import (
    ServiceProvider,
    DynamicServiceProvider,
)

# *** fixtures

# ** fixture: app_dependency
@pytest.fixture
def app_dependency() -> AppServiceDependency:
    '''
    Fixture for an AppServiceDependency instance.

    :return: The AppServiceDependency instance.
    :rtype: AppServiceDependency
    '''

    # Create and return a new AppServiceDependency.
    return AppServiceDependency(service_id='test_service',
        module_path='test_module_path',
        class_name='test_class_name',
        parameters={'param1': 'value1', 'param2': 'value2'},
    )

# ** fixture: resolvable_app_dependency
@pytest.fixture
def resolvable_app_dependency() -> AppServiceDependency:
    '''
    Fixture for an AppServiceDependency with a real module path,
    used for testing get_service_type_mapping().

    :return: The AppServiceDependency instance.
    :rtype: AppServiceDependency
    '''

    # Use a real module path so import_module resolves correctly.
    return AppServiceDependency(service_id='resolvable_service',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
        parameters={'param1': 'value1'},
    )

# ** fixture: app_interface
@pytest.fixture
def app_interface(app_dependency: AppServiceDependency) -> AppInterface:
    '''
    Fixture for an AppInterface instance.

    :param app_dependency: The AppServiceDependency fixture.
    :type app_dependency: AppServiceDependency
    :return: The AppInterface instance.
    :rtype: AppInterface
    '''

    # Create and return a new AppInterface.
    return AppInterface(id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
        description='The test app.',
        flags=['test'],
        services=[app_dependency],
    )

# *** tests

# ** test: app_interface_get_service
def test_app_interface_get_service(app_interface: AppInterface) -> None:
    '''
    Test successful retrieval of a service dependency by service id.

    :param app_interface: The AppInterface fixture.
    :type app_interface: AppInterface
    '''

    # Retrieve the service dependency by service id.
    service = app_interface.get_service('test_service')

    # Assert the service dependency fields match.
    assert service.module_path == 'test_module_path'
    assert service.class_name == 'test_class_name'
    assert service.service_id == 'test_service'
    assert service.parameters == {'param1': 'value1', 'param2': 'value2'}

# ** test: app_interface_get_service_invalid
def test_app_interface_get_service_invalid(app_interface: AppInterface) -> None:
    '''
    Test that get_service returns None for an invalid service id.

    :param app_interface: The AppInterface fixture.
    :type app_interface: AppInterface
    '''

    # Attempt to retrieve a non-existent service dependency.
    service = app_interface.get_service('invalid')

    # Assert None is returned.
    assert service is None


# ** test: app_interface_get_service_type_mapping
def test_app_interface_get_service_type_mapping(resolvable_app_dependency: AppServiceDependency) -> None:
    '''
    Test that get_service_type_mapping returns the correct service ID-to-type dict.

    :param resolvable_app_dependency: An AppServiceDependency with a real module path.
    :type resolvable_app_dependency: AppServiceDependency
    '''

    # Create an AppInterface with a resolvable service dependency.
    interface = AppInterface(id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
        services=[resolvable_app_dependency],
    )

    # Get the service type mapping (now owned by the app interface context).
    from tiferet.contexts.app import AppInterfaceContext
    mapping = AppInterfaceContext.get_service_type_mapping(interface)

    # Assert the mapping contains the expected keys.
    assert 'interface_id' in mapping
    assert 'logger_id' in mapping
    assert 'resolvable_service' in mapping

    # Assert the service types resolve correctly (the hub is built declaratively,
    # so app_context is intentionally not part of the mapping).
    assert mapping['resolvable_service'] is AppInterfaceContext
    assert mapping['interface_id'] == 'test'

    # Assert service parameters are included as injection constants.
    assert mapping.get('param1') == 'value1'


# ** test: app_interface_get_service_type_mapping_no_services
def test_app_interface_get_service_type_mapping_no_services() -> None:
    '''
    Test that get_service_type_mapping works correctly with no service dependencies.
    '''

    # Create an AppInterface with no services.
    interface = AppInterface(id='empty',
        name='Empty App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
        services=[],
    )

    # Get the service type mapping (now owned by the app interface context).
    from tiferet.contexts.app import AppInterfaceContext
    mapping = AppInterfaceContext.get_service_type_mapping(interface)

    # Assert only the base keys are present (interface_id, logger_id).
    assert 'interface_id' in mapping
    assert 'logger_id' in mapping
    assert len(mapping) == 2


# ** test: app_service_dependency_get_service_type
def test_app_service_dependency_get_service_type(resolvable_app_dependency: AppServiceDependency) -> None:
    '''
    Test that AppServiceDependency.get_service_type resolves the configured class type.

    :param resolvable_app_dependency: An AppServiceDependency with a real module path.
    :type resolvable_app_dependency: AppServiceDependency
    '''

    # Resolve the service type from the dependency.
    service_type = resolvable_app_dependency.get_service_type()

    # Assert the resolved type matches the expected class.
    from tiferet.contexts.app import AppInterfaceContext
    assert service_type is AppInterfaceContext


# ** test: app_interface_service_provider_defaults
def test_app_interface_service_provider_defaults() -> None:
    '''
    Test default service provider metadata values on AppInterface.
    '''

    # Create an AppInterface with minimal required data.
    interface = AppInterface(id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
        services=[],
    )

    # Assert default provider module path and class name values.
    assert interface.service_provider_path == 'tiferet.di.dynamic'
    assert interface.service_provider_class_name == 'DynamicServiceProvider'
