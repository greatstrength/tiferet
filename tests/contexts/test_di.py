# *** imports

# ** infra
import pytest
from unittest import mock
from typing import Tuple, List, Dict

# ** app
from tiferet.contexts.di import DIContext
from tiferet.contexts.cache import CacheContext
from tiferet.assets.exceptions import TiferetError
from tiferet.assets.constants import DEPENDENCY_TYPE_NOT_FOUND_ID
from tiferet.di import ServiceProvider, DynamicServiceProvider
from tiferet.domain import (
    ServiceConfiguration,
    FlaggedDependency,
)
from tiferet.events.di import ListAllSettings


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
        ServiceConfiguration(
            id='test_service',
            module_path='tests.contexts.test_di',
            class_name='TestService',
            dependencies=[
                FlaggedDependency(
                    module_path='tests.contexts.test_di',
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
def di_context(di_list_all_configs_evt_mock) -> DIContext:
    '''
    Fixture to create a DIContext with a mock DI service.

    :param di_list_all_configs_evt_mock: The mock ListAllSettings event.
    :type di_list_all_configs_evt_mock: mock.Mock
    :return: A DIContext instance.
    :rtype: DIContext
    '''

    # Return a DIContext instance.
    return DIContext(
        di_list_all_configs_evt=di_list_all_configs_evt_mock,
        cache=CacheContext(cache={}),
    )


# ** fixture: provider
@pytest.fixture
def provider(di_context: DIContext) -> ServiceProvider:
    '''
    Fixture to build a service provider using the DIContext.

    :param di_context: The DI context to use.
    :type di_context: DIContext
    :return: A ServiceProvider instance.
    :rtype: ServiceProvider
    '''

    # Build the provider with no flags.
    return di_context.build_service_provider()


# *** tests

# ** test: di_context_get_cache_key
def test_di_context_get_cache_key(di_context: DIContext):
    '''
    Test the creation of a cache key in the DIContext.

    :param di_context: The DI context to test.
    :type di_context: DIContext
    '''

    # Test with no flags.
    assert di_context.create_cache_key() == 'feature_services'

    # Test with flags.
    assert di_context.create_cache_key(flags=['test', 'test2']) == 'feature_services_test_test2'

# ** test: di_context_default_service_provider_factory
def test_di_context_default_service_provider_factory():
    '''
    Test the default DIContext service provider factory.
    '''

    # Build a provider with a type map and injected constants.
    provider = DIContext.default_service_provider(
        type_map={'test_service': TestService},
        test_config='factory_value',
    )

    # Assert the provider type and service resolution behavior.
    assert isinstance(provider, ServiceProvider)
    resolved_service = provider.get_service('test_service')
    assert resolved_service.test_config == 'factory_value'


# ** test: di_context_custom_service_provider_factory
def test_di_context_custom_service_provider_factory(di_list_all_configs_evt_mock):
    '''
    Test that DIContext uses a custom service provider factory when injected.
    '''

    # Create a custom factory mock and provider return value.
    provider = DynamicServiceProvider()
    create_factory = mock.Mock(return_value=provider)

    # Create context with custom provider factory and build provider.
    context = DIContext(
        di_list_all_configs_evt=di_list_all_configs_evt_mock,
        cache=CacheContext(cache={}),
        create_service_provider=create_factory,
    )
    result = context.build_service_provider()

    # Assert custom factory was called with expected type map/constants.
    create_factory.assert_called_once()
    kwargs = create_factory.call_args.kwargs
    assert kwargs['type_map']['test_service'].__qualname__ == TestService.__qualname__
    assert kwargs['test_config'] == 'test_value'
    assert kwargs['param_config'] == 'param_value'

    # Assert the factory output provider is used and returned.
    assert result is provider


# ** test: di_context_build_service_provider
def test_di_context_build_service_provider(di_context: DIContext):
    '''
    Test the building of a service provider in the DIContext.

    :param di_context: The DI context to test.
    :type di_context: DIContext
    '''

    # Build the provider with no flags.
    provider = di_context.build_service_provider()

    # Assert that the provider is not None and is a ServiceProvider.
    assert provider
    assert isinstance(provider, ServiceProvider)

    # Get the test_service from the provider.
    test_service = provider.get_service('test_service')

    # Assert the service was resolved with default parameters.
    assert test_service.test_config == 'test_value'
    assert test_service.param_config == 'param_value'
    assert test_service.flagged_config is None

    # Assert that the provider is cached.
    assert di_context.cache.get('feature_services') is provider

    # Build the provider with flags.
    flagged_provider = di_context.build_service_provider(flags=['test'])

    # Assert the flagged provider is not None.
    assert flagged_provider

    # Get the test_service from the flagged provider.
    flagged_service = flagged_provider.get_service('test_service')

    # Assert the service was resolved with flagged parameters.
    assert flagged_service.test_config == 'test_value'
    assert flagged_service.param_config is None
    assert flagged_service.flagged_config == 'flagged_value'

    # Assert that the flagged provider is cached.
    assert di_context.cache.get('feature_services_test') is flagged_provider


# ** test: di_context_build_service_provider_with_missing_dependency_type
def test_di_context_build_service_provider_with_missing_dependency_type(
        di_context: DIContext,
        di_list_all_configs_evt_mock,
        di_service_content: Tuple[List[ServiceConfiguration], Dict[str, str]]):
    '''
    Test building a provider with a missing dependency type raises an error.

    :param di_context: The DI context to test.
    :type di_context: DIContext
    :param di_list_all_configs_evt_mock: The mock ListAllSettings event.
    :param di_service_content: The content for the DI service.
    :type di_service_content: Tuple[List[ServiceConfiguration], Dict[str, str]]
    '''

    # Update the configuration to have no module_path and class_name.
    configurations, constants = di_service_content
    configurations[0].module_path = None
    configurations[0].class_name = None

    # Mock the execute method to return the updated configurations.
    di_list_all_configs_evt_mock.execute.return_value = (configurations, constants)

    # Attempt to build the provider and expect an error.
    with pytest.raises(TiferetError) as exc_info:
        di_context.build_service_provider(flags=['missing_flag'])

    # Assert the correct error code and kwargs.
    assert exc_info.value.error_code == DEPENDENCY_TYPE_NOT_FOUND_ID
    assert exc_info.value.kwargs.get('configuration_id') == 'test_service'
    assert exc_info.value.kwargs.get('flags') == ['missing_flag']


# ** test: di_context_build_service_provider_with_cached_provider
def test_di_context_build_service_provider_with_cached_provider(di_context: DIContext, provider: ServiceProvider):
    '''
    Test that build_service_provider returns the cached provider on subsequent calls.

    :param di_context: The DI context to test.
    :type di_context: DIContext
    :param provider: The pre-built service provider fixture.
    :type provider: ServiceProvider
    '''

    # Assert that a provider is cached.
    assert di_context.cache.get('feature_services')

    # Call build_service_provider again with no flags.
    cached_provider = di_context.build_service_provider()

    # Assert the same provider instance is returned.
    assert cached_provider is provider


# ** test: di_context_get_dependency
def test_di_context_get_dependency(di_context: DIContext):
    '''
    Test retrieving a dependency from the DIContext.

    :param di_context: The DI context to test.
    :type di_context: DIContext
    '''

    # Retrieve the dependency.
    service = di_context.get_dependency('test_service')

    # Assert the service was resolved correctly.
    assert service.test_config == 'test_value'
    assert service.param_config == 'param_value'
    assert service.flagged_config is None


# ** test: di_context_get_dependency_with_varargs
def test_di_context_get_dependency_with_varargs(di_context: DIContext):
    '''
    Test retrieving a dependency using *flags varargs.

    :param di_context: The DI context to test.
    :type di_context: DIContext
    '''

    # Retrieve the dependency with a single string flag.
    service = di_context.get_dependency('test_service', 'test')

    # Assert the service was resolved with flagged parameters.
    assert service.test_config == 'test_value'
    assert service.flagged_config == 'flagged_value'


# ** test: di_context_get_dependency_with_list_flag
def test_di_context_get_dependency_with_list_flag(di_context: DIContext):
    '''
    Test retrieving a dependency passing a list as a flag argument.

    :param di_context: The DI context to test.
    :type di_context: DIContext
    '''

    # Retrieve the dependency with a list flag (normalized to individual flags).
    service = di_context.get_dependency('test_service', ['test'])

    # Assert the service was resolved with flagged parameters.
    assert service.test_config == 'test_value'
    assert service.flagged_config == 'flagged_value'


# ** test: di_context_normalize_flags
def test_di_context_normalize_flags():
    '''
    Test the normalize_flags static method handles mixed input types.
    '''

    # Single string.
    assert DIContext.normalize_flags('a') == ['a']

    # Multiple strings.
    assert DIContext.normalize_flags('a', 'b') == ['a', 'b']

    # List.
    assert DIContext.normalize_flags(['a', 'b']) == ['a', 'b']

    # Tuple.
    assert DIContext.normalize_flags(('a', 'b')) == ['a', 'b']

    # Mixed.
    assert DIContext.normalize_flags('a', ['b', 'c'], ('d',)) == ['a', 'b', 'c', 'd']

    # Empty.
    assert DIContext.normalize_flags() == []


# ** test: di_context_load_constants_with_flagged_dependencies
def test_di_context_load_constants_with_flagged_dependencies(
        di_context: DIContext,
        di_service_content: Tuple[List[ServiceConfiguration], Dict[str, str]]):
    '''
    Test the load_constants method with and without flags.

    :param di_context: The DI context to test.
    :type di_context: DIContext
    :param di_service_content: The content for the DI service.
    :type di_service_content: Tuple[List[ServiceConfiguration], Dict[str, str]]
    '''

    # Unpack the service content.
    configurations, constants = di_service_content

    # Load constants without flags — uses default parameters.
    constants_no_flags = di_context.load_constants(
        configurations=configurations,
        constants=constants,
    )
    assert constants_no_flags == {
        'test_config': 'test_value',
        'param_config': 'param_value',
    }

    # Load constants with the test flag — uses flagged parameters.
    constants_with_flags = di_context.load_constants(
        configurations=configurations,
        constants=constants,
        flags=['test'],
    )
    assert constants_with_flags == {
        'test_config': 'test_value',
        'flagged_config': 'flagged_value',
    }
