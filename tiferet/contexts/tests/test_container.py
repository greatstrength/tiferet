# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ..container import *
from ...models.container import *


# *** classes

# ** class: TestContainer
class TestContainer():
        """A mock container class for testing."""
        
        # * attribute: test_config
        test_config: str

        # * attribute: param_config
        param_config: str

        # * attribute: flagged_config
        flagged_config: str

        def __init__(self, test_config: str, param_config: str = None, flagged_config: str = None):
            """Initialize the container with a test configuration."""
            self.test_config = test_config
            self.param_config = param_config
            self.flagged_config = flagged_config

# *** fixtures

# ** fixture: container_service_content
@pytest.fixture
def container_service_content():
    """Fixture to provide content for the container service."""

    # Create a list of container attributes.
    attributes = [
        ModelObject.new(
            ContainerAttribute,
            id='test_container',
            module_path='tiferet.contexts.tests.test_container',
            class_name='TestContainer',
            dependencies=[
                ModelObject.new(
                    FlaggedDependency,
                    module_path='tiferet.contexts.tests.test_container',
                    class_name='TestContainer',
                    flag='test',
                    parameters=dict(
                        flagged_config='flagged_value',
                    )
                )
            ],
            parameters=dict(
                param_config='param_value',
            )
        ),
    ]

    # Create a dictionary of constants.
    constants = dict(
        test_config='test_value'
    )

    # Return the attributes and constants.
    return attributes, constants


# ** fixture: dependency_type
@pytest.fixture
def dependency_type() -> type:
    '''
    Fixture to provide a mock dependency type.
    '''

    # Return the mock container class.
    return TestContainer


# ** fixture: test_container
@pytest.fixture
def test_container(dependency_type):
    """Fixture to create a mock test container."""
    
    # Create an instance of the mock container class.
    return dependency_type(
        test_config='test_value',
        param_config='param_value',
        flagged_config=None
    )


# ** fixture: container_service
@pytest.fixture
def container_service(container_service_content, dependency_type):
    """Fixture to create a mock container service."""

    # Create a mock ContainerService with the specified content.
    service = mock.Mock(spec=ContainerService)

    # Mock the list_all method to return the content.
    service.list_all.return_value = container_service_content
    service.get_dependency_type.return_value = dependency_type

    # Return the mock service.
    return service


# ** fixture: container_context
@pytest.fixture
def container_context(container_service):
    """Fixture to create a ContainerContext with a mock container service."""
    return ContainerContext(container_service=container_service)


# ** fixture: injector
@pytest.fixture
def injector(container_context, container_service):
    """Fixture to create an injector using the ContainerContext."""
    
    # Set the load constants return value to reflect parameters from the default attribute.
    container_service.load_constants.return_value = dict(
        test_config='test_value',
        param_config='param_value',
    )

    # Build the injector with no flags.
    return container_context.build_injector()


# *** tests

# ** test

# ** test: container_context_get_cache_key
def test_container_context_get_cache_key(container_context):
    """Test the creation of a cache key in the ContainerContext."""
    
    # Test with no flags
    assert container_context.create_cache_key() == "feature_container"
    
    # Test with flags
    assert container_context.create_cache_key(flags=['test', 'test2']) == "feature_container_test_test2"


# ** test: container_context_build_injector
def test_container_context_build_injector(container_context, container_service_content, container_service):
    """Test the building of an injector in the ContainerContext."""

    # Set the load constants return value to reflect parameters from the default attribute.
    container_service.load_constants.return_value = dict(
        test_config='test_value',
        param_config='param_value',
    )

    # Build the injector with no flags.
    injector = container_context.build_injector()

    # Assert that the injector is not None.
    assert injector

    # Get the test_container attribute from the injector.
    test_container = get_dependency.execute(
        injector,
        'test_container'
    )

    # Assert that the test_container is an instance of the expected type.
    assert test_container.test_config == 'test_value'
    assert test_container.param_config == 'param_value'
    assert test_container.flagged_config is None

    # Assert that the feature_container is in the container context cache.
    assert container_context.cache.get('feature_container') == injector

    # Set the load constants return value to reflect parameters from the flagged dependency.
    container_service.load_constants.return_value = dict(
        test_config='test_value',
        flagged_config='flagged_value',
    )

    # Build the injector with flags.
    injector = container_context.build_injector(flags=['test'])

    # Assert that the injector is not None.
    assert injector
    # Get the test_container attribute from the injector.
    test_container = get_dependency.execute(
        injector,
        'test_container'
    )
    
    # Assert that the test_container is an instance of the expected type.
    assert test_container.test_config == 'test_value'
    assert test_container.param_config is None
    assert test_container.flagged_config == 'flagged_value'

    # Assert that the feature_container_test is in the container context cache.
    assert container_context.cache.get('feature_container_test') == injector


# ** test: container_context_build_injector_with_cached_injector
def test_container_context_build_injector_with_cached_injector(container_context, injector, container_service):
    """Test building an injector with a cached injector in the ContainerContext."""

    # Assert that there is a cached injector.
    assert container_context.cache.get('feature_container')

    # Call the build_injector method again with no flags to test caching.
    cached_injector = container_context.build_injector()

    # Assert that the cached injector is the same as the original injector.
    assert cached_injector is injector


# ** test: container_context_get_dependency
def test_container_context_get_dependency(container_context, injector, test_container):
    """Test retrieving a dependency from the ContainerContext."""

    # Retrieve the dependency using the injector.
    dependency = container_context.get_dependency(
        'test_container',
    )

    # Assert that the retrieved dependency is the same as the test_container.
    assert dependency.test_config == test_container.test_config
    assert dependency.param_config == test_container.param_config
    assert dependency.flagged_config == test_container.flagged_config
