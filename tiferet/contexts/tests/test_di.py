# *** imports

# ** infra
import pytest
from unittest import mock
from typing import List, Dict, Tuple

# ** app
from ..di import DIContext
from ...domain.di import ServiceConfiguration, FlaggedDependency
from ...domain import DomainObject
from ...assets.exceptions import TiferetError
from ...assets.constants import DEPENDENCY_TYPE_NOT_FOUND_ID
from ...events.di import ListAllSettings   # assuming this still exists


# *** classes

# ** class: TestService
class TestService:
    '''
    A mock service class for testing.
    '''

    # * attribute: test_config
    test_config: str

    # * attribute: param_config
    param_config: str

    # * attribute: flagged_config
    flagged_config: str

    # * init
    def __init__(self, test_config: str, param_config: str = None, flagged_config: str = None):
        '''
        Initialize the service with a test configuration.

        :param test_config: The base test configuration value.
        :type test_config: str
        :param param_config: Optional parameter configuration.
        :type param_config: str
        :param flagged_config: Optional flagged configuration.
        :type flagged_config: str
        '''
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
                    parameters=dict(flagged_config='flagged_value'),
                )
            ],
            parameters=dict(param_config='param_value'),
        ),
    ]

    constants = dict(test_config='test_value')

    return configurations, constants


# ** fixture: di_list_all_configs_evt_mock
@pytest.fixture
def di_list_all_configs_evt_mock(di_service_content):
    '''
    Fixture to create a mock ListAllSettings event.
    '''
    evt = mock.Mock(spec=ListAllSettings)
    evt.execute.return_value = di_service_content
    return evt


# ** fixture: di_context
@pytest.fixture
def di_context(di_list_all_configs_evt_mock):
    '''
    Fixture to create a DIContext with a mock DI service.
    '''
    return DIContext(
        di_list_all_configs_evt=di_list_all_configs_evt_mock,
        # create_service_provider is auto-set to default in __init__ for tests
    )


# *** tests

# ** test: di_context_create_cache_key
def test_di_context_create_cache_key(di_context: DIContext):
    '''
    Test the creation of a cache key in the DIContext.
    '''
    assert di_context.create_cache_key() == "feature_services"
    assert di_context.create_cache_key(['test', 'test2']) == "feature_services_test_test2"


# ** test: di_context_build_service_provider
def test_di_context_build_service_provider(di_context: DIContext):
    '''
    Test building a service provider (no flags and with flags).
    '''
    # No flags
    provider = di_context.build_service_provider()
    assert provider is not None

    service = provider.get_service('test_service')
    assert service.test_config == 'test_value'
    assert service.param_config == 'param_value'
    assert service.flagged_config is None

    assert di_context.cache.get('feature_services') is provider

    # With flag
    provider = di_context.build_service_provider(['test'])
    assert provider is not None

    service = provider.get_service('test_service')
    assert service.test_config == 'test_value'
    assert service.param_config is None   # flagged overrides
    assert service.flagged_config == 'flagged_value'

    assert di_context.cache.get('feature_services_test') is provider


# ** test: di_context_build_service_provider_with_missing_dependency_type
def test_di_context_build_service_provider_with_missing_dependency_type(
    di_context: DIContext,
    di_list_all_configs_evt_mock,
    di_service_content,
):
    '''
    Test that missing dependency type raises the correct error.
    '''
    configurations, constants = di_service_content
    configurations[0].module_path = None
    configurations[0].class_name = None
    di_list_all_configs_evt_mock.execute.return_value = (configurations, constants)

    with pytest.raises(TiferetError) as exc_info:
        di_context.build_service_provider(['missing_flag'])

    assert exc_info.value.error_code == DEPENDENCY_TYPE_NOT_FOUND_ID
    assert exc_info.value.kwargs.get('configuration_id') == 'test_service'


# ** test: di_context_build_service_provider_with_cached_provider
def test_di_context_build_service_provider_with_cached_provider(di_context: DIContext):
    '''
    Test that caching works correctly for service providers.
    '''
    first = di_context.build_service_provider()
    second = di_context.build_service_provider()  # should hit cache
    assert second is first


# ** test: di_context_get_dependency
def test_di_context_get_dependency(di_context: DIContext):
    '''
    Test retrieving a dependency via get_dependency.
    '''
    service = di_context.get_dependency('test_service')
    assert service.test_config == 'test_value'
    assert service.param_config == 'param_value'

    service = di_context.get_dependency('test_service', ['test'])
    assert service.flagged_config == 'flagged_value'


# ** test: di_context_get_configuration_type
def test_di_context_get_configuration_type(di_context: DIContext, di_service_content):
    '''
    Test get_configuration_type with default and flagged paths.
    '''
    configurations, _ = di_service_content
    config = configurations[0]

    assert di_context.get_configuration_type(config) == TestService
    assert di_context.get_configuration_type(config, 'test') == TestService


# ** test: di_context_get_configuration_type_none
def test_di_context_get_configuration_type_none(di_context: DIContext):
    '''
    Test that get_configuration_type returns None when no type is available.
    '''
    config = DomainObject.new(
        ServiceConfiguration,
        id='no_type',
        dependencies=[],
    )
    assert di_context.get_configuration_type(config) is None
    assert di_context.get_configuration_type(config, 'missing') is None


# ** test: di_context_load_constants_with_flagged_dependencies
def test_di_context_load_constants_with_flagged_dependencies(
    di_context: DIContext, di_service_content
):
    '''
    Test load_constants behavior with and without flags.
    '''
    configurations, constants = di_service_content

    no_flags = di_context.load_constants(configurations, constants)
    assert no_flags['test_config'] == 'test_value'
    assert no_flags['param_config'] == 'param_value'
    assert 'flagged_config' not in no_flags

    with_flags = di_context.load_constants(configurations, constants, ['test'])
    assert with_flags['test_config'] == 'test_value'
    assert with_flags.get('param_config') is None   # overridden
    assert with_flags['flagged_config'] == 'flagged_value'