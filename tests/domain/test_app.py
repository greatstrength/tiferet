"""Tests for Tiferet Domain App"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.domain.core import DomainObject
from tiferet.domain.app import (
    AppInterface,
    AppServiceDependency,
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
    used for testing get_service_type().

    :return: The AppServiceDependency instance.
    :rtype: AppServiceDependency
    '''

    # Use an import-safe domain module path so import_module resolves correctly.
    # (The contexts layer is intentionally broken on main during this milestone.)
    return AppServiceDependency(service_id='resolvable_service',
        module_path='tiferet.domain.app',
        class_name='AppInterface',
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
    assert service_type is AppInterface


# ** test: app_interface_apply_defaults_merges_missing_only
def test_app_interface_apply_defaults_merges_missing_only(app_interface: AppInterface) -> None:
    '''
    Test that apply_defaults adds only missing services and constants, leaving
    existing entries untouched.

    :param app_interface: The AppInterface fixture.
    :type app_interface: AppInterface
    '''

    # Seed an existing constant on a copy of the fixture that must be preserved.
    interface = app_interface.model_copy(update=dict(constants={'di_config': 'custom.yml'}))

    # Apply defaults with one duplicate and one missing service plus constants.
    result = interface.apply_defaults(
        default_services=[
            AppServiceDependency(service_id='test_service', module_path='ignored', class_name='Ignored'),
            AppServiceDependency(service_id='new_service', module_path='new.module', class_name='NewClass'),
        ],
        default_constants={'di_config': 'config.yml', 'feature_config': 'config.yml'},
    )

    # Assert existing entries win and only missing ones are added.
    assert isinstance(result, AppInterface)
    assert result.get_service('test_service').module_path == 'test_module_path'
    assert result.get_service('new_service').module_path == 'new.module'
    assert result.constants['di_config'] == 'custom.yml'
    assert result.constants['feature_config'] == 'config.yml'

# ** test: app_interface_apply_defaults_non_mutating
def test_app_interface_apply_defaults_non_mutating(app_interface: AppInterface) -> None:
    '''
    Test that apply_defaults returns a new interface and leaves the original unchanged.

    :param app_interface: The AppInterface fixture.
    :type app_interface: AppInterface
    '''

    # Capture the original service count before applying defaults.
    original_service_count = len(app_interface.services)

    # Apply a missing default service and constant.
    result = app_interface.apply_defaults(
        default_services=[
            AppServiceDependency(service_id='new_service', module_path='new.module', class_name='NewClass'),
        ],
        default_constants={'feature_config': 'config.yml'},
    )

    # Assert a new interface is returned with the defaults applied.
    assert result is not app_interface
    assert result.get_service('new_service') is not None
    assert result.constants.get('feature_config') == 'config.yml'

    # Assert the original interface is left unchanged (non-mutating).
    assert len(app_interface.services) == original_service_count
    assert 'feature_config' not in app_interface.constants
