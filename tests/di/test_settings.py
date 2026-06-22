"""Tiferet DI Settings Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock
from typing import Tuple, List, Dict

# ** app
from tiferet.di.settings import ServiceContainer, ServiceResolver, merge_settings
from tiferet.domain import ServiceRegistration, FlaggedDependency
from tiferet.interfaces.di import DIService


# *** classes

# ** class: simple_service
class SimpleService:
    '''A dependency-free service used for testing.'''

    pass


# ** class: dependent_service
class DependentService:
    '''A service with a constructor dependency on SimpleService.'''

    # * init
    def __init__(self, simple_service: SimpleService):
        '''Initialize the dependent service.'''

        # Assign the injected dependency.
        self.simple_service = simple_service


# ** class: configurable_service
class ConfigurableService:
    '''A service with a scalar constructor parameter, used to test constant injection.'''

    # * init
    def __init__(self, config_value: str):
        '''Initialize the configurable service.'''

        # Assign the injected constant.
        self.config_value = config_value


# ** class: test_service
class TestService:
    '''A mock service class used for ServiceResolver tests.'''

    # Prevent pytest from collecting this helper class as a test case.
    __test__ = False

    # * init
    def __init__(self, test_config: str, param_config: str = None, flagged_config: str = None):
        '''Initialize the service with a test configuration.'''

        # Assign the injected configuration values.
        self.test_config = test_config
        self.param_config = param_config
        self.flagged_config = flagged_config


# *** fixtures

# ** fixture: empty_container
@pytest.fixture
def empty_container() -> ServiceContainer:
    '''
    Fixture to create an empty ServiceContainer.

    :return: An empty container instance.
    :rtype: ServiceContainer
    '''

    # Return a container with no initial services.
    return ServiceContainer()


# ** fixture: populated_container
@pytest.fixture
def populated_container() -> ServiceContainer:
    '''
    Fixture to create a ServiceContainer pre-populated with a SimpleService.

    :return: A container with SimpleService registered.
    :rtype: ServiceContainer
    '''

    # Return a container with SimpleService registered under 'simple_service'.
    return ServiceContainer(services={'simple_service': SimpleService})


# ** fixture: di_service_content
@pytest.fixture
def di_service_content() -> Tuple[List[ServiceRegistration], Dict[str, str]]:
    '''
    Fixture to provide content for the DI service.

    :return: A tuple of service configurations and constants.
    :rtype: Tuple[List[ServiceRegistration], Dict[str, str]]
    '''

    # Create a list of service configurations.
    configurations = [
        ServiceRegistration(
            id='test_service',
            module_path='tests.di.test_settings',
            class_name='TestService',
            dependencies=[
                FlaggedDependency(
                    module_path='tests.di.test_settings',
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


# ** fixture: di_service_mock
@pytest.fixture
def di_service_mock(di_service_content: Tuple[List[ServiceRegistration], Dict[str, str]]):
    '''
    Fixture to create a mock DIService whose ``list_all`` returns the content.

    :param di_service_content: The content for the DI service.
    :type di_service_content: Tuple[List[ServiceRegistration], Dict[str, str]]
    :return: A mock DIService.
    :rtype: DIService
    '''

    # Create a mock DIService and stub list_all to return the content.
    svc = mock.Mock(spec=DIService)
    svc.list_all.return_value = di_service_content

    # Return the mock service.
    return svc


# ** fixture: resolver
@pytest.fixture
def resolver(di_service_mock) -> ServiceResolver:
    '''
    Fixture to create a ServiceResolver backed by a mock DIService.

    :param di_service_mock: The mock DIService.
    :type di_service_mock: mock.Mock
    :return: A ServiceResolver instance.
    :rtype: ServiceResolver
    '''

    # Return a ServiceResolver instance.
    return ServiceResolver(di_service=di_service_mock)


# *** tests

# ** test: container_init_empty
def test_container_init_empty(empty_container: ServiceContainer):
    '''
    Test that an empty container initializes with no providers.

    :param empty_container: The empty container fixture.
    :type empty_container: ServiceContainer
    '''

    # Assert that the container has no registered providers.
    assert len(empty_container.container.providers) == 0


# ** test: container_init_with_services
def test_container_init_with_services(populated_container: ServiceContainer):
    '''
    Test that a container initialized with services registers them correctly.

    :param populated_container: The pre-populated container fixture.
    :type populated_container: ServiceContainer
    '''

    # Assert that the service is present in the container providers.
    assert 'simple_service' in populated_container.container.providers


# ** test: container_add_service
def test_container_add_service(empty_container: ServiceContainer):
    '''
    Test that add_service registers a service and makes it resolvable.

    :param empty_container: The empty container fixture.
    :type empty_container: ServiceContainer
    '''

    # Add a single service.
    empty_container.add_service('simple_service', SimpleService)

    # Assert it was added to the container.
    assert 'simple_service' in empty_container.container.providers

    # Assert the resolved instance is of the expected type.
    service = empty_container.get_service('simple_service')
    assert isinstance(service, SimpleService)


# ** test: container_add_service_new_instance_per_call
def test_container_add_service_new_instance_per_call(populated_container: ServiceContainer):
    '''
    Test that Factory providers resolve as new instances per call.

    :param populated_container: The pre-populated container fixture.
    :type populated_container: ServiceContainer
    '''

    # Resolve two instances of the same service.
    instance_a = populated_container.get_service('simple_service')
    instance_b = populated_container.get_service('simple_service')

    # Assert that both are SimpleService instances but are distinct objects.
    assert isinstance(instance_a, SimpleService)
    assert isinstance(instance_b, SimpleService)
    assert instance_a is not instance_b


# ** test: container_add_services
def test_container_add_services(empty_container: ServiceContainer):
    '''
    Test that add_services registers multiple services at once.

    :param empty_container: The empty container fixture.
    :type empty_container: ServiceContainer
    '''

    # Add multiple services.
    empty_container.add_services({
        'simple_service': SimpleService,
        'dependent_service': DependentService,
    })

    # Assert both were added and resolve correctly.
    assert 'simple_service' in empty_container.container.providers
    assert 'dependent_service' in empty_container.container.providers
    assert isinstance(empty_container.get_service('simple_service'), SimpleService)
    assert isinstance(empty_container.get_service('dependent_service'), DependentService)


# ** test: container_add_constants
def test_container_add_constants(empty_container: ServiceContainer):
    '''
    Test that add_constants registers scalar values returned as-is on resolution.

    :param empty_container: The empty container fixture.
    :type empty_container: ServiceContainer
    '''

    # Register a scalar constant.
    empty_container.add_constants({'config_value': 'test_config'})

    # Assert the constant was stored and resolves to the original value.
    assert 'config_value' in empty_container.container.providers
    assert empty_container.get_service('config_value') == 'test_config'


# ** test: container_add_constants_injected_into_service
def test_container_add_constants_injected_into_service(empty_container: ServiceContainer):
    '''
    Test that constants are injected into services that depend on them.

    :param empty_container: The empty container fixture.
    :type empty_container: ServiceContainer
    '''

    # Register a constant first, then a service that depends on it.
    empty_container.add_constants({'config_value': 'test_config'})
    empty_container.add_service('configurable_service', ConfigurableService)

    # Resolve the service and assert the constant was injected correctly.
    service = empty_container.get_service('configurable_service')
    assert isinstance(service, ConfigurableService)
    assert service.config_value == 'test_config'


# ** test: container_get_service_not_found
def test_container_get_service_not_found(empty_container: ServiceContainer):
    '''
    Test that get_service raises a raw error for an unregistered service ID
    (best-case: a missing provider is not callable).

    :param empty_container: The empty container fixture.
    :type empty_container: ServiceContainer
    '''

    # Attempt to resolve a service that was never registered; the missing
    # provider raises a raw error for the caller (with event access) to convert.
    with pytest.raises(TypeError):
        empty_container.get_service('nonexistent_service')


# ** test: container_remove_service
def test_container_remove_service(populated_container: ServiceContainer):
    '''
    Test that remove_service deregisters a service from the container.

    :param populated_container: The pre-populated container fixture.
    :type populated_container: ServiceContainer
    '''

    # Remove the registered service.
    populated_container.remove_service('simple_service')

    # Assert it was removed and is no longer resolvable (raw error, best-case).
    assert 'simple_service' not in populated_container.container.providers
    with pytest.raises(TypeError):
        populated_container.get_service('simple_service')


# ** test: container_remove_service_nonexistent
def test_container_remove_service_nonexistent(empty_container: ServiceContainer):
    '''
    Test that remove_service is a no-op for an unregistered service ID.

    :param empty_container: The empty container fixture.
    :type empty_container: ServiceContainer
    '''

    # Removing an ID that was never registered should not raise.
    empty_container.remove_service('nonexistent_service')

    # Assert the container is still empty.
    assert len(empty_container.container.providers) == 0


# ** test: container_cascading_dependency_injection
def test_container_cascading_dependency_injection(empty_container: ServiceContainer):
    '''
    Test that cascading DI resolves a service and its constructor dependency.

    :param empty_container: The empty container fixture.
    :type empty_container: ServiceContainer
    '''

    # Register SimpleService first, then DependentService which depends on it.
    empty_container.add_service('simple_service', SimpleService)
    empty_container.add_service('dependent_service', DependentService)

    # Resolve the dependent service and assert both types resolve correctly.
    service = empty_container.get_service('dependent_service')
    assert isinstance(service, DependentService)
    assert isinstance(service.simple_service, SimpleService)


# ** test: resolver_create_cache_key
def test_resolver_create_cache_key(resolver: ServiceResolver):
    '''
    Test the creation of a cache key in the ServiceResolver.

    :param resolver: The service resolver to test.
    :type resolver: ServiceResolver
    '''

    # Test with no flags and with flags.
    assert resolver.create_cache_key() == 'feature_services'
    assert resolver.create_cache_key(flags=['test', 'test2']) == 'feature_services_test_test2'


# ** test: resolver_build_container
def test_resolver_build_container(resolver: ServiceResolver):
    '''
    Test the building of a service container in the ServiceResolver.

    :param resolver: The service resolver to test.
    :type resolver: ServiceResolver
    '''

    # Build the container with no flags.
    container = resolver.build_container()

    # Assert the container is valid and resolves with default parameters.
    assert container
    assert isinstance(container, ServiceContainer)
    test_service = container.get_service('test_service')
    assert test_service.test_config == 'test_value'
    assert test_service.param_config == 'param_value'
    assert test_service.flagged_config is None

    # Assert the container is cached on the resolver.
    assert resolver._containers.get('feature_services') is container

    # Build the container with flags and assert flagged parameters resolve.
    flagged_container = resolver.build_container(flags=['test'])
    assert flagged_container
    flagged_service = flagged_container.get_service('test_service')
    assert flagged_service.test_config == 'test_value'
    assert flagged_service.param_config is None
    assert flagged_service.flagged_config == 'flagged_value'

    # Assert the flagged container is cached.
    assert resolver._containers.get('feature_services_test') is flagged_container


# ** test: resolver_build_container_skips_missing_dependency_type
def test_resolver_build_container_skips_missing_dependency_type(
        resolver: ServiceResolver,
        di_service_mock,
        di_service_content: Tuple[List[ServiceRegistration], Dict[str, str]]):
    '''
    Test that a configuration resolving to no type is skipped (best-case),
    leaving the service unregistered rather than raising a DI-specific error.

    :param resolver: The service resolver to test.
    :type resolver: ServiceResolver
    :param di_service_mock: The mock DIService.
    :param di_service_content: The content for the DI service.
    :type di_service_content: Tuple[List[ServiceRegistration], Dict[str, str]]
    '''

    # Update the configuration to have no module_path and class_name.
    configurations, constants = di_service_content
    configurations[0].module_path = None
    configurations[0].class_name = None
    di_service_mock.list_all.return_value = (configurations, constants)

    # Build the container; the no-type configuration is simply skipped.
    container = resolver.build_container(flags=['missing_flag'])

    # Assert the unresolved service is not registered and resolving it raises
    # a raw error for the caller to convert.
    assert 'test_service' not in container.container.providers
    with pytest.raises(TypeError):
        container.get_service('test_service')


# ** test: resolver_build_container_cached
def test_resolver_build_container_cached(resolver: ServiceResolver):
    '''
    Test that build_container returns the cached container on subsequent calls.

    :param resolver: The service resolver to test.
    :type resolver: ServiceResolver
    '''

    # Build the container once, then again, and assert the same instance returns.
    container = resolver.build_container()
    assert resolver._containers.get('feature_services')
    cached_container = resolver.build_container()
    assert cached_container is container


# ** test: resolver_get_dependency
def test_resolver_get_dependency(resolver: ServiceResolver):
    '''
    Test retrieving a dependency from the ServiceResolver.

    :param resolver: The service resolver to test.
    :type resolver: ServiceResolver
    '''

    # Retrieve the dependency and assert it resolves with default parameters.
    service = resolver.get_dependency('test_service')
    assert service.test_config == 'test_value'
    assert service.param_config == 'param_value'
    assert service.flagged_config is None


# ** test: resolver_get_dependency_with_varargs
def test_resolver_get_dependency_with_varargs(resolver: ServiceResolver):
    '''
    Test retrieving a dependency using *flags varargs.

    :param resolver: The service resolver to test.
    :type resolver: ServiceResolver
    '''

    # Retrieve the dependency with a single string flag.
    service = resolver.get_dependency('test_service', 'test')
    assert service.test_config == 'test_value'
    assert service.flagged_config == 'flagged_value'


# ** test: resolver_get_dependency_with_list_flag
def test_resolver_get_dependency_with_list_flag(resolver: ServiceResolver):
    '''
    Test retrieving a dependency passing a list as a flag argument.

    :param resolver: The service resolver to test.
    :type resolver: ServiceResolver
    '''

    # Retrieve the dependency with a list flag (normalized to individual flags).
    service = resolver.get_dependency('test_service', ['test'])
    assert service.test_config == 'test_value'
    assert service.flagged_config == 'flagged_value'


# ** test: resolver_normalize_flags
def test_resolver_normalize_flags():
    '''
    Test the normalize_flags static method handles mixed input types.
    '''

    # Single, multiple, list, tuple, mixed, and empty inputs.
    assert ServiceResolver.normalize_flags('a') == ['a']
    assert ServiceResolver.normalize_flags('a', 'b') == ['a', 'b']
    assert ServiceResolver.normalize_flags(['a', 'b']) == ['a', 'b']
    assert ServiceResolver.normalize_flags(('a', 'b')) == ['a', 'b']
    assert ServiceResolver.normalize_flags('a', ['b', 'c'], ('d',)) == ['a', 'b', 'c', 'd']
    assert ServiceResolver.normalize_flags() == []


# ** test: resolver_load_constants_with_flagged_dependencies
def test_resolver_load_constants_with_flagged_dependencies(
        resolver: ServiceResolver,
        di_service_content: Tuple[List[ServiceRegistration], Dict[str, str]]):
    '''
    Test the load_constants method with and without flags.

    :param resolver: The service resolver to test.
    :type resolver: ServiceResolver
    :param di_service_content: The content for the DI service.
    :type di_service_content: Tuple[List[ServiceRegistration], Dict[str, str]]
    '''

    # Unpack the service content.
    configurations, constants = di_service_content

    # Load constants without flags -- uses default parameters.
    constants_no_flags = resolver.load_constants(
        configurations=configurations,
        constants=constants,
    )
    assert constants_no_flags == {
        'test_config': 'test_value',
        'param_config': 'param_value',
    }

    # Load constants with the test flag -- uses flagged parameters.
    constants_with_flags = resolver.load_constants(
        configurations=configurations,
        constants=constants,
        flags=['test'],
    )
    assert constants_with_flags == {
        'test_config': 'test_value',
        'flagged_config': 'flagged_value',
    }


# ** test: resolver_list_all_settings_merges_defaults
def test_resolver_list_all_settings_merges_defaults(di_service_mock):
    '''
    Test that list_all_settings merges bootstrap defaults beneath repository values.

    :param di_service_mock: The mock DIService.
    :type di_service_mock: mock.Mock
    '''

    # Repository returns only the test_service configuration and a constant.
    default_config = ServiceRegistration(
        id='default_only_service',
        module_path='tests.di.test_settings',
        class_name='TestService',
    )

    # Build a resolver with a default config index and default constants.
    resolver = ServiceResolver(
        di_service=di_service_mock,
        default_config_index={'default_only_service': default_config},
        default_di_constants={'test_config': 'default_value', 'extra': 'extra_value'},
    )

    # List all settings and assert defaults are merged without overriding repo values.
    configs, constants = resolver.list_all_settings()
    config_ids = {c.id for c in configs}
    assert 'test_service' in config_ids
    assert 'default_only_service' in config_ids
    assert constants['test_config'] == 'test_value'
    assert constants['extra'] == 'extra_value'


# ** test: merge_settings_merges_defaults
def test_merge_settings_merges_defaults():
    '''
    Test that the merge_settings helper appends default configs for missing ids
    and merges default constants beneath repository constants.
    '''

    # Define a repository configuration and a default-only configuration.
    repo_config = ServiceRegistration(id='repo_service', module_path='m', class_name='C')
    default_config = ServiceRegistration(id='default_only', module_path='m', class_name='C')

    # Merge repository values with the bootstrap defaults.
    configs, constants = merge_settings(
        [repo_config],
        {'shared': 'repo'},
        {'default_only': default_config, 'repo_service': repo_config},
        {'shared': 'default', 'extra': 'extra_value'},
    )

    # Assert the default-only config is appended and repo constants take priority.
    config_ids = {c.id for c in configs}
    assert config_ids == {'repo_service', 'default_only'}
    assert constants['shared'] == 'repo'
    assert constants['extra'] == 'extra_value'


# ** test: resolver_parse_parameter_injection
def test_resolver_parse_parameter_injection(di_service_mock):
    '''
    Test that an injected parse_parameter callable is applied to constants.

    :param di_service_mock: The mock DIService.
    :type di_service_mock: mock.Mock
    '''

    # Inject a custom parser that tags each parsed value.
    resolver = ServiceResolver(
        di_service=di_service_mock,
        parse_parameter=lambda v: f'parsed:{v}',
    )

    # Load constants and assert the injected parser was applied.
    constants = resolver.load_constants(constants={'test_config': 'value'})
    assert constants['test_config'] == 'parsed:value'


# ** test: resolver_parse_parameter_defaults_to_identity
def test_resolver_parse_parameter_defaults_to_identity(di_service_mock):
    '''
    Test that the default parse_parameter is an identity function.

    :param di_service_mock: The mock DIService.
    :type di_service_mock: mock.Mock
    '''

    # Build a resolver without injecting a parser.
    resolver = ServiceResolver(di_service=di_service_mock)

    # Load constants and assert values pass through unchanged.
    constants = resolver.load_constants(constants={'test_config': 'value'})
    assert constants['test_config'] == 'value'
