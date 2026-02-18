# *** imports

# ** infra
import pytest
from unittest import mock
from typing import Tuple, List, Dict

# ** app
from ..container import *
from ...entities.container import *


# *** classes

# ** class: TestContainer
class TestContainer():
        '''
        A mock container class for testing.
        '''
        
        # * attribute: test_config
        test_config: str

        # * attribute: param_config
        param_config: str

        # * attribute: flagged_config
        flagged_config: str

        def __init__(self, test_config: str, param_config: str = None, flagged_config: str = None):
            '''Initialize the container with a test configuration.'''
            self.test_config = test_config
            self.param_config = param_config
            self.flagged_config = flagged_config

# *** fixtures

# ** fixture: container_service_content
@pytest.fixture
def container_service_content() -> Tuple[List[ContainerAttribute], Dict[str, str]]:
    '''
    Fixture to provide content for the container service.
    '''

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
def test_container(dependency_type: type) -> TestContainer:
    '''
    Fixture to create a mock test container

    :param dependency_type: The dependency type to use.
    :type dependency_type: type
    :return: An instance of the mock test container.
    :rtype: TestContainer
    '''
    
    # Create an instance of the mock container class.
    return dependency_type(
        test_config='test_value',
        param_config='param_value',
        flagged_config=None
    )

# ** fixture: container_list_all_cmd_mock
@pytest.fixture
def container_list_all_cmd_mock(container_service_content: Tuple[List[ContainerAttribute], Dict[str, str]]):
    '''
    Fixture to create a mock ListAllSettings command.

    :param container_service_content: The content for the container service.
    :type container_service_content: Tuple[List[ContainerAttribute], Dict[str, str]]
    :return: A mock ListAllSettings command.
    :rtype: ListAllSettings
    '''

    # Create a mock ContainerService with the specified content.
    command = mock.Mock(spec=ListAllSettings)

    # Mock the execute method to return the content.
    command.execute.return_value = container_service_content

    # Return the mock service.
    return command

# ** fixture: container_context
@pytest.fixture
def container_context(container_list_all_cmd_mock: ListAllSettings) -> ContainerContext:
    '''
    Fixture to create a ContainerContext with a mock container service.
    
    :param container_list_all_cmd_mock: The mock ListAllSettings command.
    :type container_list_all_cmd_mock: ListAllSettings
    :return: A ContainerContext instance.
    :rtype: ContainerContext
    '''
    return ContainerContext(container_list_all_cmd=container_list_all_cmd_mock)


# ** fixture: injector
@pytest.fixture
def injector(container_context: ContainerContext) -> Injector:
    '''
    Fixture to create an injector using the ContainerContext.
    
    :param container_context: The container context to use.
    :type container_context: ContainerContext
    :return: An Injector instance.
    :rtype: Injector
    '''

    # Build the injector with no flags.
    return container_context.build_injector()

# *** tests

# ** test

# ** test: container_context_get_cache_key
def test_container_context_get_cache_key(container_context: ContainerContext):
    '''
    Test the creation of a cache key in the ContainerContext.
    
    :param container_context: The container context to test.
    :type container_context: ContainerContext
    '''
    
    # Test with no flags
    assert container_context.create_cache_key() == "feature_container"
    
    # Test with flags
    assert container_context.create_cache_key(flags=['test', 'test2']) == "feature_container_test_test2"


# ** test: container_context_build_injector
def test_container_context_build_injector(container_context: ContainerContext):
    '''
    Test the building of an injector in the ContainerContext.
    
    :param container_context: The container context to test.
    :type container_context: ContainerContext
    '''

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

# ** test: container_context_build_injector_with_missing_dependency_type
def test_container_context_build_injector_with_missing_dependency_type(
        container_context: ContainerContext,
        container_list_all_cmd_mock: ListAllSettings,
        container_service_content: Tuple[List[ContainerAttribute], Dict[str, str]]):
    '''
    Test building an injector with a missing dependency type in the ContainerContext.
    
    :param container_context: The container context to test.
    :type container_context: ContainerContext
    :param container_list_all_cmd_mock: The mock ListAllSettings command.
    :type container_list_all_cmd_mock: ListAllSettings
    :param container_service_content: The content for the container service.
    :type container_service_content: Tuple[List[ContainerAttribute], Dict[str, str]]
    '''

    # Update the attribute in the container service content to have no module_path and class_name.
    attributes, constants = container_service_content
    attributes[0].module_path = None
    attributes[0].class_name = None

    # Mock the get_dependency_type method to return the updated attributes.
    container_list_all_cmd_mock.execute.return_value = (attributes, constants)

    # Attempt to build the injector and expect a RaiseError due to missing dependency type.
    with pytest.raises(TiferetError) as exc_info:
        container_context.build_injector(flags=['missing_flag'])

    # Assert that the exception message contains the expected error ID.
    assert exc_info.value.error_code == DEPENDENCY_TYPE_NOT_FOUND_ID
    assert exc_info.value.kwargs.get('attribute_id') == 'test_container'
    assert exc_info.value.kwargs.get('flags') == ['missing_flag']

# ** test: container_context_build_injector_with_cached_injector
def test_container_context_build_injector_with_cached_injector(container_context, injector):
    '''Test building an injector with a cached injector in the ContainerContext.'''

    # Assert that there is a cached injector.
    assert container_context.cache.get('feature_container')

    # Call the build_injector method again with no flags to test caching.
    cached_injector = container_context.build_injector()

    # Assert that the cached injector is the same as the original injector.
    assert cached_injector is injector


# ** test: container_context_get_dependency
def test_container_context_get_dependency(container_context, test_container):
    '''Test retrieving a dependency from the ContainerContext.'''

    # Retrieve the dependency using the injector.
    dependency = container_context.get_dependency(
        'test_container',
    )

    # Assert that the retrieved dependency is the same as the test_container.
    assert dependency.test_config == test_container.test_config
    assert dependency.param_config == test_container.param_config
    assert dependency.flagged_config == test_container.flagged_config

# ** test: test_container_handler_load_constants_with_flagged_dependencies
def test_container_handler_load_constants_with_flagged_dependencies(
        container_context: ContainerContext, 
        container_service_content: Tuple[List[ContainerAttribute], Dict[str, str]]):
    '''
    Test the load_constants method with flagged dependencies in the ContainerContext.

    :param container_context: The container context to test.
    :type container_context: ContainerContext
    :param container_service_content: The content for the container service.
    :type container_service_content: Tuple[List[ContainerAttribute], Dict[str, str]]
    '''

    # Unpack the container service content.
    attributes, constants = container_service_content

    # Load constants from the attributes.
    constants_no_flags = container_context.load_constants(
        attributes=attributes,
        constants=constants
    )

    # Assert that the result contains parsed constants and parameters.
    constants_no_flags == {
        'test_config': 'test_value',
        'param_config': 'param_value'
    }

    # Call the load_constants method with flags.
    constants_with_flags = container_context.load_constants(
        attributes=attributes,
        constants=constants,
        flags=['test']
    )

    # Assert that the result with flags contains parsed constants and parameters.
    assert constants_with_flags == {
        'test_config': 'test_value',
        'flagged_config': 'flagged_value'
    }