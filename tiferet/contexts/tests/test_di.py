# *** imports

# ** infra
import pytest
from unittest import mock
from typing import Tuple, List, Dict

# ** app
from ..di import *
from ...domain.di import *
from ...events.di import ListAllSettings


# *** classes

# ** class: TestService
class TestService():
        '''
        A mock service class for testing.
        '''
        
        # * attribute: test_config
        test_config: str

        # * attribute: param_config
        param_config: str

        # * attribute: flagged_config
        flagged_config: str

        def __init__(self, test_config: str, param_config: str = None, flagged_config: str = None):
            '''Initialize the service with a test configuration.'''
            self.test_config = test_config
            self.param_config = param_config
            self.flagged_config = flagged_config

# *** fixtures

# ** fixture: di_service_content
@pytest.fixture
def di_service_content() -> Tuple[List[ServiceConfiguration], Dict[str, str]]:
    '''
    Fixture to provide content for the DI service.
    '''

    # Create a list of service configurations.
    configurations = [
        DomainObject.new(
            ServiceConfiguration,
            id='test_service',
            module_path='tiferet.contexts.tests.test_di',
            class_name='TestService',
            dependencies=[
                DomainObject.new(
                    FlaggedDependency,
                    module_path='tiferet.contexts.tests.test_di',
                    class_name='TestService',
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

    # Return the configurations and constants.
    return configurations, constants


# ** fixture: dependency_type
@pytest.fixture
def dependency_type() -> type:
    '''
    Fixture to provide a mock dependency type.
    '''

    # Return the mock service class.
    return TestService


# ** fixture: test_service
@pytest.fixture
def test_service(dependency_type: type) -> TestService:
    '''
    Fixture to create a mock test service.

    :param dependency_type: The dependency type to use.
    :type dependency_type: type
    :return: An instance of the mock test service.
    :rtype: TestService
    '''
    
    # Create an instance of the mock service class.
    return dependency_type(
        test_config='test_value',
        param_config='param_value',
        flagged_config=None
    )

# ** fixture: di_list_all_configs_evt_mock
@pytest.fixture
def di_list_all_configs_evt_mock(di_service_content: Tuple[List[ServiceConfiguration], Dict[str, str]]):
    '''
    Fixture to create a mock ListAllSettings event.

    :param di_service_content: The content for the DI service.
    :type di_service_content: Tuple[List[ServiceConfiguration], Dict[str, str]]
    :return: A mock ListAllSettings event.
    :rtype: ListAllSettings
    '''

    # Create a mock ListAllSettings event.
    evt = mock.Mock(spec=ListAllSettings)

    # Mock the execute method to return the content.
    evt.execute.return_value = di_service_content

    # Return the mock event.
    return evt

# ** fixture: di_context
@pytest.fixture
def di_context(di_list_all_configs_evt_mock: DomainEvent) -> DIContext:
    '''
    Fixture to create a DIContext with a mock DI service.
    
    :param di_list_all_configs_evt_mock: The mock ListAllSettings event.
    :type di_list_all_configs_evt_mock: DomainEvent
    :return: A DIContext instance.
    :rtype: DIContext
    '''
    return DIContext(di_list_all_configs_evt=di_list_all_configs_evt_mock)


# ** fixture: injector
@pytest.fixture
def injector(di_context: DIContext) -> Injector:
    '''
    Fixture to create an injector using the DIContext.
    
    :param di_context: The DI context to use.
    :type di_context: DIContext
    :return: An Injector instance.
    :rtype: Injector
    '''

    # Build the injector with no flags.
    return di_context.build_injector()

# *** tests

# ** test: di_context_get_cache_key
def test_di_context_get_cache_key(di_context: DIContext):
    '''
    Test the creation of a cache key in the DIContext.
    
    :param di_context: The DI context to test.
    :type di_context: DIContext
    '''
    
    # Test with no flags.
    assert di_context.create_cache_key() == "feature_services"
    
    # Test with flags.
    assert di_context.create_cache_key(flags=['test', 'test2']) == "feature_services_test_test2"


# ** test: di_context_build_injector
def test_di_context_build_injector(di_context: DIContext):
    '''
    Test the building of an injector in the DIContext.
    
    :param di_context: The DI context to test.
    :type di_context: DIContext
    '''

    # Build the injector with no flags.
    injector = di_context.build_injector()

    # Assert that the injector is not None.
    assert injector

    # Get the test_service configuration from the injector.
    test_service = get_dependency.execute(
        injector,
        'test_service'
    )

    # Assert that the test_service is an instance of the expected type.
    assert test_service.test_config == 'test_value'
    assert test_service.param_config == 'param_value'
    assert test_service.flagged_config is None

    # Assert that the feature_services is in the DI context cache.
    assert di_context.cache.get('feature_services') == injector

    # Build the injector with flags.
    injector = di_context.build_injector(flags=['test'])

    # Assert that the injector is not None.
    assert injector
    # Get the test_service configuration from the injector.
    test_service = get_dependency.execute(
        injector,
        'test_service'
    )
    
    # Assert that the test_service is an instance of the expected type.
    assert test_service.test_config == 'test_value'
    assert test_service.param_config is None
    assert test_service.flagged_config == 'flagged_value'

    # Assert that the feature_services_test is in the DI context cache.
    assert di_context.cache.get('feature_services_test') == injector

# ** test: di_context_build_injector_with_missing_dependency_type
def test_di_context_build_injector_with_missing_dependency_type(
        di_context: DIContext,
        di_list_all_configs_evt_mock: DomainEvent,
        di_service_content: Tuple[List[ServiceConfiguration], Dict[str, str]]):
    '''
    Test building an injector with a missing dependency type in the DIContext.
    
    :param di_context: The DI context to test.
    :type di_context: DIContext
    :param di_list_all_configs_evt_mock: The mock ListAllSettings event.
    :type di_list_all_configs_evt_mock: DomainEvent
    :param di_service_content: The content for the DI service.
    :type di_service_content: Tuple[List[ServiceConfiguration], Dict[str, str]]
    '''

    # Update the configuration in the DI service content to have no module_path and class_name.
    configurations, constants = di_service_content
    configurations[0].module_path = None
    configurations[0].class_name = None

    # Mock the execute method to return the updated configurations.
    di_list_all_configs_evt_mock.execute.return_value = (configurations, constants)

    # Attempt to build the injector and expect a RaiseError due to missing dependency type.
    with pytest.raises(TiferetError) as exc_info:
        di_context.build_injector(flags=['missing_flag'])

    # Assert that the exception message contains the expected error ID.
    assert exc_info.value.error_code == DEPENDENCY_TYPE_NOT_FOUND_ID
    assert exc_info.value.kwargs.get('configuration_id') == 'test_service'
    assert exc_info.value.kwargs.get('flags') == ['missing_flag']

# ** test: di_context_build_injector_with_cached_injector
def test_di_context_build_injector_with_cached_injector(di_context, injector):
    '''Test building an injector with a cached injector in the DIContext.'''

    # Assert that there is a cached injector.
    assert di_context.cache.get('feature_services')

    # Call the build_injector method again with no flags to test caching.
    cached_injector = di_context.build_injector()

    # Assert that the cached injector is the same as the original injector.
    assert cached_injector is injector


# ** test: di_context_get_dependency
def test_di_context_get_dependency(di_context, test_service):
    '''Test retrieving a dependency from the DIContext.'''

    # Retrieve the dependency using the injector.
    dependency = di_context.get_dependency(
        'test_service',
    )

    # Assert that the retrieved dependency is the same as the test_service.
    assert dependency.test_config == test_service.test_config
    assert dependency.param_config == test_service.param_config
    assert dependency.flagged_config == test_service.flagged_config

# ** test: di_context_get_configuration_type_success_default
def test_di_context_get_configuration_type_success_default(
    di_context: DIContext,
    di_service_content,
):
    '''
    Test that get_configuration_type resolves the correct type with and without flags.

    :param di_context: The DI context to test.
    :type di_context: DIContext
    :param di_service_content: The content for the DI service.
    :type di_service_content: Tuple[List[ServiceConfiguration], Dict[str, str]]
    '''

    # Unpack the DI service content.
    configurations, _ = di_service_content
    config = configurations[0]

    # Get the type without flags (should use default module_path/class_name).
    dep_type = di_context.get_configuration_type(config)

    # Assert the type is correct.
    assert dep_type == TestService

    # Get the type with the test flag (should resolve the flagged dependency).
    dep_type = di_context.get_configuration_type(config, 'test')

    # Assert the type is still TestService (same class in fixture).
    assert dep_type == TestService

# ** test: di_context_get_configuration_type_none
def test_di_context_get_configuration_type_none(
    di_context: DIContext,
):
    '''
    Test that get_configuration_type returns None when no type is found.

    :param di_context: The DI context to test.
    :type di_context: DIContext
    '''

    # Create a service configuration with no default type and no matching dependencies.
    config = DomainObject.new(
        ServiceConfiguration,
        id='no_type',
        dependencies=[],
    )

    # Get the type without flags (should return None).
    dep_type = di_context.get_configuration_type(config)

    # Assert the type is None.
    assert dep_type is None

    # Get the type with an invalid flag (should return None).
    dep_type = di_context.get_configuration_type(config, 'missing_flag')

    # Assert the type is None.
    assert dep_type is None

# ** test: di_context_load_constants_with_flagged_dependencies
def test_di_context_load_constants_with_flagged_dependencies(
        di_context: DIContext, 
        di_service_content: Tuple[List[ServiceConfiguration], Dict[str, str]]):
    '''
    Test the load_constants method with flagged dependencies in the DIContext.

    :param di_context: The DI context to test.
    :type di_context: DIContext
    :param di_service_content: The content for the DI service.
    :type di_service_content: Tuple[List[ServiceConfiguration], Dict[str, str]]
    '''

    # Unpack the DI service content.
    configurations, constants = di_service_content

    # Load constants from the configurations.
    constants_no_flags = di_context.load_constants(
        configurations=configurations,
        constants=constants
    )

    # Assert that the result contains parsed constants and parameters.
    constants_no_flags == {
        'test_config': 'test_value',
        'param_config': 'param_value'
    }

    # Call the load_constants method with flags.
    constants_with_flags = di_context.load_constants(
        configurations=configurations,
        constants=constants,
        flags=['test']
    )

    # Assert that the result with flags contains parsed constants and parameters.
    assert constants_with_flags == {
        'test_config': 'test_value',
        'flagged_config': 'flagged_value'
    }
