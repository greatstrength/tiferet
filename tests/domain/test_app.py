"""Tests for Tiferet Domain App"""

# *** imports

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from tiferet.domain.core import DomainObject, ServiceDependency
from tiferet.domain.app import (
    AppInterface,
    AppServiceDependency,
    AppSession,
)
from tiferet.domain.di import (
    FlaggedDependency,
    ServiceRegistration,
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

# ** test: app_service_dependency_inherits_service_dependency
def test_app_service_dependency_inherits_service_dependency() -> None:
    '''
    Test that AppServiceDependency is a subclass of ServiceDependency.
    '''

    # Assert the inheritance relationship.
    assert issubclass(AppServiceDependency, ServiceDependency)


# ** test: app_service_dependency_requires_service_id
def test_app_service_dependency_requires_service_id() -> None:
    '''
    Test that AppServiceDependency raises ValidationError when service_id is missing.
    '''

    # Attempt to create an AppServiceDependency without service_id.
    with pytest.raises(ValidationError):
        AppServiceDependency(
            module_path='some.module',
            class_name='SomeClass',
        )


# ** test: app_service_dependency_no_direct_module_path
def test_app_service_dependency_no_direct_module_path() -> None:
    '''
    Test that AppServiceDependency has no directly-declared module_path field.
    '''

    # Assert module_path is not declared directly on AppServiceDependency.
    assert 'module_path' not in AppServiceDependency.__annotations__


# ** test: app_session_flags_default
def test_app_session_flags_default() -> None:
    '''
    Test that AppSession.flags defaults to ["default"] when not provided.
    '''

    # Create an AppSession with only required fields.
    session = AppSession(id='x', name='x')

    # Assert the default flags list.
    assert session.flags == ['default']


# ** test: app_session_get_service_found
def test_app_session_get_service_found(app_dependency: AppServiceDependency) -> None:
    '''
    Test that AppSession.get_service returns the matching dependency by service_id.

    :param app_dependency: The AppServiceDependency fixture.
    :type app_dependency: AppServiceDependency
    '''

    # Create an AppSession with the fixture dependency.
    session = AppSession(id='test', name='Test', services=[app_dependency])

    # Retrieve the service by its id.
    result = session.get_service('test_service')

    # Assert the correct dependency is returned.
    assert result is not None
    assert result.service_id == 'test_service'


# ** test: app_session_get_service_not_found
def test_app_session_get_service_not_found() -> None:
    '''
    Test that AppSession.get_service returns None for an unknown service_id.
    '''

    # Create an AppSession with no services.
    session = AppSession(id='test', name='Test')

    # Assert None is returned for a non-existent service id.
    assert session.get_service('unknown') is None


# ** test: service_registration_resolve_service_flagged
def test_service_registration_resolve_service_flagged() -> None:
    '''
    Test that resolve_service returns a ServiceDependency matching the flagged override.
    '''

    # Build a ServiceRegistration with one flagged dependency.
    flagged = FlaggedDependency(
        flag='test',
        module_path='tiferet.domain.app',
        class_name='AppSession',
    )
    registration = ServiceRegistration(
        id='svc',
        module_path='tiferet.domain.app',
        class_name='AppInterface',
        dependencies=[flagged],
    )

    # Resolve the service for the matching flag.
    result = registration.resolve_service('test')

    # Assert the returned dependency has the flagged module/class.
    assert result is not None
    assert isinstance(result, ServiceDependency)
    assert result.module_path == 'tiferet.domain.app'
    assert result.class_name == 'AppSession'


# ** test: service_registration_resolve_service_default
def test_service_registration_resolve_service_default() -> None:
    '''
    Test that resolve_service falls back to the default definition when no flag matches.
    '''

    # Build a ServiceRegistration with no matching flagged dependency.
    registration = ServiceRegistration(
        id='svc',
        module_path='tiferet.domain.app',
        class_name='AppInterface',
    )

    # Resolve with a flag that has no override.
    result = registration.resolve_service('no_match')

    # Assert the default module/class is returned.
    assert result is not None
    assert isinstance(result, ServiceDependency)
    assert result.module_path == 'tiferet.domain.app'
    assert result.class_name == 'AppInterface'


# ** test: service_registration_resolve_service_none
def test_service_registration_resolve_service_none() -> None:
    '''
    Test that resolve_service returns None when neither a flag override
    nor a default definition is available.
    '''

    # Build a ServiceRegistration with no default type.
    registration = ServiceRegistration(
        id='svc_no_type',
        dependencies=[],
    )

    # Assert None is returned.
    assert registration.resolve_service('any_flag') is None


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
