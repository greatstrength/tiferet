"""Tests for Tiferet Domain DI"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.domain.core import DomainObject, ServiceDependency
from tiferet.domain.di import (
    FlaggedDependency,
    ServiceRegistration,
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
    return FlaggedDependency(flag='test_alpha',
        module_path='tests.domain.test_di',
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
    return FlaggedDependency(flag='test_beta',
        module_path='tests.domain.test_di',
        class_name='TestDependencyBeta',
        parameters={'test_param': 'test_value', 'param': 'value2'},
    )

# ** fixture: service_registration
@pytest.fixture
def service_registration(flagged_dependency: FlaggedDependency) -> ServiceRegistration:
    '''
    Fixture for a ServiceRegistration with a default type and one flagged override.

    :param flagged_dependency: The FlaggedDependency fixture.
    :type flagged_dependency: FlaggedDependency
    :return: The ServiceRegistration instance.
    :rtype: ServiceRegistration
    '''

    # Create and return a new ServiceRegistration.
    return ServiceRegistration(id='test_service',
        module_path='tests.domain.test_di',
        class_name='TestDependency',
        dependencies=[flagged_dependency],
    )

# ** fixture: service_registration_no_default_type
@pytest.fixture
def service_registration_no_default_type(flagged_dependency: FlaggedDependency) -> ServiceRegistration:
    '''
    Fixture for a ServiceRegistration with no default type, only flagged overrides.

    :param flagged_dependency: The FlaggedDependency fixture.
    :type flagged_dependency: FlaggedDependency
    :return: The ServiceRegistration instance.
    :rtype: ServiceRegistration
    '''

    # Create and return a new ServiceRegistration without default type.
    return ServiceRegistration(id='test_service_no_default',
        dependencies=[flagged_dependency],
    )

# ** fixture: service_registration_multiple_deps
@pytest.fixture
def service_registration_multiple_deps(
        flagged_dependency: FlaggedDependency,
        flagged_dependency_to_add: FlaggedDependency,
    ) -> ServiceRegistration:
    '''
    Fixture for a ServiceRegistration with a default type and two flagged overrides.

    :param flagged_dependency: The FlaggedDependency fixture (test_alpha).
    :type flagged_dependency: FlaggedDependency
    :param flagged_dependency_to_add: The FlaggedDependency fixture (test_beta).
    :type flagged_dependency_to_add: FlaggedDependency
    :return: The ServiceRegistration instance.
    :rtype: ServiceRegistration
    '''

    # Create and return a new ServiceRegistration with multiple dependencies.
    return ServiceRegistration(id='test_service_multi',
        module_path='tests.domain.test_di',
        class_name='TestDependency',
        dependencies=[flagged_dependency, flagged_dependency_to_add],
    )

# *** tests

# ** test: service_registration_get_dependency
def test_service_registration_get_dependency(service_registration: ServiceRegistration) -> None:
    '''
    Test successful retrieval of a flagged dependency by flag.

    :param service_registration: The ServiceRegistration fixture.
    :type service_registration: ServiceRegistration
    '''

    # Retrieve the flagged dependency by flag.
    dep = service_registration.get_dependency('test_alpha')

    # Assert the flagged dependency fields match.
    assert dep.flag == 'test_alpha'
    assert dep.module_path == 'tests.domain.test_di'
    assert dep.class_name == 'TestDependencyAlpha'
    assert dep.parameters == {'test_param': 'test_value', 'param': 'value1'}

# ** test: service_registration_get_dependency_invalid
def test_service_registration_get_dependency_invalid(service_registration: ServiceRegistration) -> None:
    '''
    Test that get_dependency returns None for an unknown flag.

    :param service_registration: The ServiceRegistration fixture.
    :type service_registration: ServiceRegistration
    '''

    # Attempt to retrieve a non-existent flagged dependency.
    dep = service_registration.get_dependency('invalid')

    # Assert None is returned.
    assert dep is None

# ** test: service_registration_get_dependency_multiple_flags
def test_service_registration_get_dependency_multiple_flags(
        service_registration_multiple_deps: ServiceRegistration,
    ) -> None:
    '''
    Test priority order: first matching flag in the argument tuple wins.

    :param service_registration_multiple_deps: The ServiceRegistration fixture with multiple dependencies.
    :type service_registration_multiple_deps: ServiceRegistration
    '''

    # Retrieve with test_alpha first — should return alpha.
    dep_alpha_first = service_registration_multiple_deps.get_dependency('test_alpha', 'test_beta')
    assert dep_alpha_first.flag == 'test_alpha'
    assert dep_alpha_first.class_name == 'TestDependencyAlpha'

    # Retrieve with test_beta first — should return beta.
    dep_beta_first = service_registration_multiple_deps.get_dependency('test_beta', 'test_alpha')
    assert dep_beta_first.flag == 'test_beta'
    assert dep_beta_first.class_name == 'TestDependencyBeta'

# ** test: service_registration_get_service_type_default
def test_service_registration_get_service_type_default(
        service_registration: ServiceRegistration,
    ) -> None:
    '''
    Test that get_service_type returns the default type when no flags match.

    :param service_registration: The ServiceRegistration fixture.
    :type service_registration: ServiceRegistration
    '''

    # Resolve with no flags — should return the default TestDependency.
    resolved = service_registration.get_service_type()

    # Assert the default type is returned.
    assert resolved.__qualname__ == TestDependency.__qualname__

# ** test: service_registration_get_service_type_flagged
def test_service_registration_get_service_type_flagged(
        service_registration: ServiceRegistration,
    ) -> None:
    '''
    Test that get_service_type resolves the flagged dependency type when a matching flag is provided.

    :param service_registration: The ServiceRegistration fixture.
    :type service_registration: ServiceRegistration
    '''

    # Resolve with the test_alpha flag — should return TestDependencyAlpha.
    resolved = service_registration.get_service_type('test_alpha')

    # Assert the flagged type takes priority over the default.
    assert resolved.__qualname__ == TestDependencyAlpha.__qualname__

# ** test: service_registration_get_service_type_no_match
def test_service_registration_get_service_type_no_match(
        service_registration_no_default_type: ServiceRegistration,
    ) -> None:
    '''
    Test that get_service_type returns None when no flag matches and there is no default.

    :param service_registration_no_default_type: ServiceRegistration with no default type.
    :type service_registration_no_default_type: ServiceRegistration
    '''

    # Resolve with an unknown flag and no default — should return None.
    resolved = service_registration_no_default_type.get_service_type('unknown_flag')

    # Assert None is returned.
    assert resolved is None

# ** test: service_registration_get_service_type_flag_priority
def test_service_registration_get_service_type_flag_priority(
        service_registration_multiple_deps: ServiceRegistration,
    ) -> None:
    '''
    Test that get_service_type respects flag priority order — first matching flag wins.

    :param service_registration_multiple_deps: ServiceRegistration with two flagged overrides.
    :type service_registration_multiple_deps: ServiceRegistration
    '''

    # test_alpha first — should resolve alpha.
    resolved = service_registration_multiple_deps.get_service_type('test_alpha', 'test_beta')
    assert resolved.__qualname__ == TestDependencyAlpha.__qualname__

    # test_beta first — should resolve beta.
    resolved = service_registration_multiple_deps.get_service_type('test_beta', 'test_alpha')
    assert resolved.__qualname__ == TestDependencyBeta.__qualname__

# ** test: service_registration_resolve_service_flagged
def test_service_registration_resolve_service_flagged(
        service_registration: ServiceRegistration,
    ) -> None:
    '''
    Test that resolve_service returns the flagged dependency's effective definition.

    :param service_registration: The ServiceRegistration fixture.
    :type service_registration: ServiceRegistration
    '''

    # Resolve the effective dependency under the matching flag.
    dependency = service_registration.resolve_service('test_alpha')

    # Assert it is a core ServiceDependency carrying the flagged type and parameters.
    assert isinstance(dependency, ServiceDependency)
    assert dependency.module_path == 'tests.domain.test_di'
    assert dependency.class_name == 'TestDependencyAlpha'
    assert dependency.parameters == {'test_param': 'test_value', 'param': 'value1'}

# ** test: service_registration_resolve_service_default
def test_service_registration_resolve_service_default(
        service_registration: ServiceRegistration,
    ) -> None:
    '''
    Test that resolve_service falls back to the registration's default definition.

    :param service_registration: The ServiceRegistration fixture.
    :type service_registration: ServiceRegistration
    '''

    # Resolve with no flags — should fall back to the default definition.
    dependency = service_registration.resolve_service()

    # Assert the default type is returned as a core ServiceDependency.
    assert isinstance(dependency, ServiceDependency)
    assert dependency.module_path == 'tests.domain.test_di'
    assert dependency.class_name == 'TestDependency'

# ** test: service_registration_resolve_service_none
def test_service_registration_resolve_service_none(
        service_registration_no_default_type: ServiceRegistration,
    ) -> None:
    '''
    Test that resolve_service returns None when no flag matches and there is no default.

    :param service_registration_no_default_type: ServiceRegistration with no default type.
    :type service_registration_no_default_type: ServiceRegistration
    '''

    # Resolve with an unknown flag and no default — should return None.
    dependency = service_registration_no_default_type.resolve_service('unknown_flag')

    # Assert None is returned.
    assert dependency is None

# ** test: service_registration_resolve_service_default_parameter_carry_through
def test_service_registration_resolve_service_default_parameter_carry_through() -> None:
    '''
    Test that resolve_service carries the registration's default parameters through.
    '''

    # Build a registration with default parameters.
    registration = ServiceRegistration(
        id='param_service',
        module_path='tests.domain.test_di',
        class_name='TestDependency',
        parameters={'p': 'v'},
    )

    # Resolve with no flags and assert the default parameters are preserved.
    dependency = registration.resolve_service()
    assert dependency.parameters == {'p': 'v'}
