"""Tests for Tiferet Service Provider Settings"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import ServiceProvider

# *** fixtures

# ** fixture: dependency_with_constant
@pytest.fixture
def dependency_with_constant():
    """Fixture to create a dependency with a constant value for testing."""

    # Define a simple dependency class with a constant value.
    class TestDependency(object):
        """TestDependency class that holds a constant value."""

        # * attribute: const_value
        const_value: str

        def __init__(self, const_value: str):
            self.const_value = const_value

    return TestDependency

@pytest.fixture
def service_provider_with_dependency(dependency_with_constant):
    '''
    Fixture to create a ServiceProvider with a dependency.
    
    :param dependency_with_constant: The dependency class to include in the service provider.
    :type dependency_with_constant: type
    '''

    # Create map of dependencies and constants.
    dependencies = {
        'test_dependency': dependency_with_constant
    }
    constants = {
        'const_value': 'test_value'
    }

    # Create container.
    return type('ServiceProvider', (ServiceProvider,), {**dependencies, **constants})

# ***. tests

# ** test: create_injector_with_dependency
def test_create_injector_with_dependency(service_provider_with_dependency, dependency_with_constant):
    '''
    Test creating an injector with a dependency and retrieving the dependency instance.

    :param service_provider_with_dependency: The service provider class with the dependency.
    :type service_provider_with_dependency: type
    :param dependency_with_constant: The dependency class to verify.
    :type dependency_with_constant: type
    '''

    # Assert the instance has the correct constant value.
    assert service_provider_with_dependency
    assert isinstance(service_provider_with_dependency, ServiceProvider)
    assert hasattr(service_provider_with_dependency, 'test_dependency')

    # Get the dependency instance.
    test_dependency = service_provider_with_dependency.get_keyed_service('test_dependency')
    assert test_dependency
    assert isinstance(test_dependency, dependency_with_constant)
    assert test_dependency.const_value == 'test_value'