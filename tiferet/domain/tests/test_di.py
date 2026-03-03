"""Tiferet DI Models Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..di import (
    DomainObject,
    FlaggedDependency,
    ServiceConfiguration,
)

# *** classes

# ** class: test_dependency
class TestDependency:
    '''
    A test class for container dependency testing.
    '''

    pass

# ** class: test_dependency_alpha
class TestDependencyAlpha(TestDependency):
    '''
    An alpha test class for container dependency testing.
    '''

    pass

# ** class: test_dependency_beta
class TestDependencyBeta(TestDependency):
    '''
    A beta test class for container dependency testing.
    '''

    pass

# *** fixtures

# ** fixture: flagged_dependency
@pytest.fixture
def flagged_dependency() -> FlaggedDependency:
    '''
    Fixture to create a FlaggedDependency instance for testing.
    '''

    # Create a flagged dependency.
    return DomainObject.new(
        FlaggedDependency,
        module_path='tiferet.domain.tests.test_di',
        class_name='TestDependencyAlpha',
        flag='test_alpha',
        parameters=dict(
            test_param='test_value',
            param='value1',
        )
    )

# ** fixture: flagged_dependency_to_add
@pytest.fixture
def flagged_dependency_to_add() -> FlaggedDependency:
    '''
    Fixture to create a FlaggedDependency instance for testing addition.
    '''

    # Create a new flagged dependency.
    return DomainObject.new(
        FlaggedDependency,
        module_path='tiferet.domain.tests.test_di',
        class_name='TestDependencyBeta',
        flag='test_beta',
        parameters=dict(
            test_param='test_value',
            param='value2'
        )
    )

# ** fixture: service_configuration
@pytest.fixture
def service_configuration(flagged_dependency: FlaggedDependency) -> ServiceConfiguration:
    '''
    Fixture to create a ServiceConfiguration instance for testing.

    :param flagged_dependency: The flagged dependency to add to the service configuration.
    :type flagged_dependency: FlaggedDependency
    :return: The created service configuration.
    :rtype: ServiceConfiguration
    '''

    # Create a service configuration with a flagged dependency.
    return DomainObject.new(
        ServiceConfiguration,
        id='test_dependency',
        module_path='tiferet.domain.tests.test_di',
        class_name='TestDependency',
        dependencies=[
            flagged_dependency
        ],
        parameters=dict(
            test_param='test_value',
            param='value0'
        )
    )

# ** fixture: service_configuration_no_default_type
@pytest.fixture
def service_configuration_no_default_type(flagged_dependency: FlaggedDependency) -> ServiceConfiguration:
    '''
    Fixture to create a ServiceConfiguration instance without a default type for testing.

    :param flagged_dependency: The flagged dependency to add to the service configuration.
    :type flagged_dependency: FlaggedDependency
    :return: The created service configuration.
    :rtype: ServiceConfiguration
    '''

    # Create a service configuration with a flagged dependency but no default type.
    return DomainObject.new(
        ServiceConfiguration,
        id='test_dependency_no_default',
        dependencies=[
            flagged_dependency
        ],
        parameters=dict(
            test_param='test_value',
            param='value0'
        )
    )

# ** fixture: service_configuration_multiple_deps
@pytest.fixture
def service_configuration_multiple_deps(
    flagged_dependency: FlaggedDependency,
    flagged_dependency_to_add: FlaggedDependency
) -> ServiceConfiguration:
    '''
    Fixture to create a ServiceConfiguration instance with multiple flagged dependencies for testing.

    :param flagged_dependency: The first flagged dependency (test_alpha).
    :type flagged_dependency: FlaggedDependency
    :param flagged_dependency_to_add: The second flagged dependency (test_beta).
    :type flagged_dependency_to_add: FlaggedDependency
    :return: The created service configuration.
    :rtype: ServiceConfiguration
    '''

    # Create a service configuration with multiple flagged dependencies.
    return DomainObject.new(
        ServiceConfiguration,
        id='test_dependency_multi',
        module_path='tiferet.domain.tests.test_di',
        class_name='TestDependency',
        dependencies=[
            flagged_dependency,
            flagged_dependency_to_add
        ],
        parameters=dict(
            test_param='test_value',
            param='value0'
        )
    )

# *** tests

# ** test: service_configuration_get_dependency
def test_service_configuration_get_dependency(
    service_configuration: ServiceConfiguration,
    flagged_dependency: FlaggedDependency
):
    '''
    Test that the service configuration can retrieve a flagged dependency.

    :param service_configuration: The service configuration to test.
    :type service_configuration: ServiceConfiguration
    :param flagged_dependency: The flagged dependency to test.
    :type flagged_dependency: FlaggedDependency
    '''

    # Get the flagged dependency.
    dependency = service_configuration.get_dependency('test_alpha')

    # Assert the dependency is valid.
    assert dependency.module_path == flagged_dependency.module_path
    assert dependency.class_name == flagged_dependency.class_name
    assert dependency.flag == flagged_dependency.flag
    assert dependency.parameters == flagged_dependency.parameters

# ** test: service_configuration_get_dependency_invalid
def test_service_configuration_get_dependency_invalid(service_configuration: ServiceConfiguration):
    '''
    Test that the service configuration returns None for an invalid dependency.

    :param service_configuration: The service configuration to test.
    :type service_configuration: ServiceConfiguration
    '''

    # Assert the dependency is invalid.
    assert service_configuration.get_dependency('invalid') is None


# ** test: service_configuration_get_dependency_multiple_flags
def test_service_configuration_get_dependency_multiple_flags(
    service_configuration_multiple_deps: ServiceConfiguration,
    flagged_dependency: FlaggedDependency,
    flagged_dependency_to_add: FlaggedDependency
):
    '''
    Test that the service configuration can retrieve a flagged dependency with multiple flags.

    :param service_configuration_multiple_deps: The service configuration with multiple dependencies.
    :type service_configuration_multiple_deps: ServiceConfiguration
    :param flagged_dependency: The first flagged dependency (test_alpha).
    :type flagged_dependency: FlaggedDependency
    :param flagged_dependency_to_add: The second flagged dependency (test_beta).
    :type flagged_dependency_to_add: FlaggedDependency
    '''

    # Assert that the test_alpha dependency is returned when it comes first.
    dependency = service_configuration_multiple_deps.get_dependency('test_alpha', 'test_beta')
    assert dependency.module_path == flagged_dependency.module_path
    assert dependency.class_name == flagged_dependency.class_name
    assert dependency.flag == flagged_dependency.flag
    assert dependency.parameters == flagged_dependency.parameters

    # Assert that the test_beta dependency is returned when flipping the order.
    dependency = service_configuration_multiple_deps.get_dependency('test_beta', 'test_alpha')
    assert dependency.module_path == flagged_dependency_to_add.module_path
    assert dependency.class_name == flagged_dependency_to_add.class_name
    assert dependency.flag == flagged_dependency_to_add.flag
    assert dependency.parameters == flagged_dependency_to_add.parameters

