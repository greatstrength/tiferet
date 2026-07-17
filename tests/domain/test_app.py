"""Tests for Tiferet Domain App"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.domain.core import DomainObject
from tiferet.domain.app import (
    AppSession,
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

# ** fixture: app_interface
@pytest.fixture
def app_interface(app_dependency: AppServiceDependency) -> AppSession:
    '''
    Fixture for an AppSession instance.

    :param app_dependency: The AppServiceDependency fixture.
    :type app_dependency: AppServiceDependency
    :return: The AppSession instance.
    :rtype: AppSession
    '''

    # Create and return a new AppSession.
    return AppSession(id='test',
        name='Test App',
        description='The test app.',
        flags=['test'],
        services=[app_dependency],
    )

# *** tests

# ** test: app_interface_get_service
def test_app_interface_get_service(app_interface: AppSession) -> None:
    '''
    Test successful retrieval of a service dependency by service id.

    :param app_interface: The AppSession fixture.
    :type app_interface: AppSession
    '''

    # Retrieve the service dependency by service id.
    service = app_interface.get_service('test_service')

    # Assert the service dependency fields match.
    assert service.module_path == 'test_module_path'
    assert service.class_name == 'test_class_name'
    assert service.service_id == 'test_service'
    assert service.parameters == {'param1': 'value1', 'param2': 'value2'}

# ** test: app_interface_get_service_invalid
def test_app_interface_get_service_invalid(app_interface: AppSession) -> None:
    '''
    Test that get_service returns None for an invalid service id.

    :param app_interface: The AppSession fixture.
    :type app_interface: AppSession
    '''

    # Attempt to retrieve a non-existent service dependency.
    service = app_interface.get_service('invalid')

    # Assert None is returned.
    assert service is None

