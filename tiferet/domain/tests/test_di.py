"""Tests for Tiferet Domain DI"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import DomainObject
from ..di import (
    FlaggedDependency,
    ServiceConfiguration,
)

# *** classes

# ** class: test_dependency
class TestDependency:
    '''
    A stub dependency class for testing.
    '''

    pass

# ** class: test_dependency_alpha
class TestDependencyAlpha(TestDependency):
    '''
    A stub alpha dependency class for testing.
    '''

    pass

# ** class: test_dependency_beta
class TestDependencyBeta(TestDependency):
    '''
    A stub beta dependency class for testing.
    '''

    pass

# *** fixtures

# ** fixture: flagged_dependency
@pytest.fixture
def flagged_dependency() -> FlaggedDependency:
    '''
    Fixture for a FlaggedDependency instance with flag test_alpha.

    :return: The FlaggedDependency instance.
    :rtype: FlaggedDependency
    '''

    # Create and return a new FlaggedDependency.
    return DomainObject.new(
        FlaggedDependency,
        flag='test_alpha',
        module_path='tiferet.domain.tests.test_di',
        class_name='TestDependencyAlpha',
        parameters={'test_param': 'test_value', 'param': 'value1'},
    )

# ** fixture: flagged_dependency_to_add
@pytest.fixture
def flagged_dependency_to_add() -> FlaggedDependency:
    '''
    Fixture for a FlaggedDependency instance with flag test_beta.

    :return: The FlaggedDependency instance.
    :rtype: FlaggedDependency
    '''

    # Create and return a new FlaggedDependency.
    return DomainObject.new(
        FlaggedDependency,
        flag='test_beta',
        module_path='tiferet.domain.tests.test_di',
        class_name='TestDependencyBeta',
        parameters={'test_param': 'test_value', 'param': 'value2'},
    )

# ** fixture: service_configuration
@pytest.fixture
def service_configuration(flagged_dependency: FlaggedDependency) -> ServiceConfiguration:
    '''
    Fixture for a ServiceConfiguration with a default type and one flagged override.

    :param flagged_dependency: The FlaggedDependency fixture.
    :type flagged_dependency: FlaggedDependency
    :return: The ServiceConfiguration instance.
    :rtype: ServiceConfiguration
    '''

    # Create and return a new ServiceConfiguration.
    return DomainObject.new(
        ServiceConfiguration,
        id='test_service',
        module_path='tiferet.domain.tests.test_di',
        class_name='TestDependency',
        dependencies=[flagged_dependency],
    )

# ** fixture: service_configuration_no_default_type
@pytest.fixture
def service_configuration_no_default_type(flagged_dependency: FlaggedDependency) -> ServiceConfiguration:
    '''
    Fixture for a ServiceConfiguration with no default type, only flagged overrides.

    :param flagged_dependency: The FlaggedDependency fixture.
    :type flagged_dependency: FlaggedDependency
    :return: The ServiceConfiguration instance.
    :rtype: ServiceConfiguration
    '''

    # Create and return a new ServiceConfiguration without default type.
    return DomainObject.new(
        ServiceConfiguration,
        id='test_service_no_default',
        dependencies=[flagged_dependency],
    )

# ** fixture: service_configuration_multiple_deps
@pytest.fixture
def service_configuration_multiple_deps(
        flagged_dependency: FlaggedDependency,
        flagged_dependency_to_add: FlaggedDependency,
    ) -> ServiceConfiguration:
    '''
    Fixture for a ServiceConfiguration with a default type and two flagged overrides.

    :param flagged_dependency: The FlaggedDependency fixture (test_alpha).
    :type flagged_dependency: FlaggedDependency
    :param flagged_dependency_to_add: The FlaggedDependency fixture (test_beta).
    :type flagged_dependency_to_add: FlaggedDependency
    :return: The ServiceConfiguration instance.
    :rtype: ServiceConfiguration
    '''

    # Create and return a new ServiceConfiguration with multiple dependencies.
    return DomainObject.new(
        ServiceConfiguration,
        id='test_service_multi',
        module_path='tiferet.domain.tests.test_di',
        class_name='TestDependency',
        dependencies=[flagged_dependency, flagged_dependency_to_add],
    )

# *** tests

# ** test: service_configuration_get_dependency
def test_service_configuration_get_dependency(service_configuration: ServiceConfiguration) -> None:
    '''
    Test successful retrieval of a flagged dependency by flag.

    :param service_configuration: The ServiceConfiguration fixture.
    :type service_configuration: ServiceConfiguration
    '''

    # Retrieve the flagged dependency by flag.
    dep = service_configuration.get_dependency('test_alpha')

    # Assert the flagged dependency fields match.
    assert dep.flag == 'test_alpha'
    assert dep.module_path == 'tiferet.domain.tests.test_di'
    assert dep.class_name == 'TestDependencyAlpha'
    assert dep.parameters == {'test_param': 'test_value', 'param': 'value1'}

# ** test: service_configuration_get_dependency_invalid
def test_service_configuration_get_dependency_invalid(service_configuration: ServiceConfiguration) -> None:
    '''
    Test that get_dependency returns None for an unknown flag.

    :param service_configuration: The ServiceConfiguration fixture.
    :type service_configuration: ServiceConfiguration
    '''

    # Attempt to retrieve a non-existent flagged dependency.
    dep = service_configuration.get_dependency('invalid')

    # Assert None is returned.
    assert dep is None

# ** test: service_configuration_get_dependency_multiple_flags
def test_service_configuration_get_dependency_multiple_flags(
        service_configuration_multiple_deps: ServiceConfiguration,
    ) -> None:
    '''
    Test priority order: first matching flag in the argument tuple wins.

    :param service_configuration_multiple_deps: The ServiceConfiguration fixture with multiple dependencies.
    :type service_configuration_multiple_deps: ServiceConfiguration
    '''

    # Retrieve with test_alpha first — should return alpha.
    dep_alpha_first = service_configuration_multiple_deps.get_dependency('test_alpha', 'test_beta')
    assert dep_alpha_first.flag == 'test_alpha'
    assert dep_alpha_first.class_name == 'TestDependencyAlpha'

    # Retrieve with test_beta first — should return beta.
    dep_beta_first = service_configuration_multiple_deps.get_dependency('test_beta', 'test_alpha')
    assert dep_beta_first.flag == 'test_beta'
    assert dep_beta_first.class_name == 'TestDependencyBeta'
