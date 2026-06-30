"""Tiferet DI Runtime Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.assets.exceptions import TiferetError
from tiferet.domain import FlaggedDependency, ServiceRegistration
from tiferet.interfaces.di import DIService
from tiferet.di.settings import (
    ServiceContainer,
    ServiceResolver,
    injectable_parameter_names,
    normalize_flags,
    create_cache_key,
    merge_settings,
)


# *** constants

# ** constant: module_path
MODULE_PATH = 'tests.di.test_settings'


# *** classes

# ** class: simple_service
class SimpleService:
    '''A dependency-free service used for testing.'''

    pass


# ** class: dependent_service
class DependentService:
    '''A service with a constructor dependency on SimpleService.'''

    # * attribute: simple_service
    simple_service: SimpleService

    # * init
    def __init__(self, simple_service: SimpleService):
        '''
        Initialize the dependent service.

        :param simple_service: The injected simple service.
        :type simple_service: SimpleService
        '''

        # Assign the injected dependency.
        self.simple_service = simple_service


# ** class: configurable_service
class ConfigurableService:
    '''A service with a scalar constructor parameter, used to test constant injection.'''

    # * attribute: config_value
    config_value: str

    # * init
    def __init__(self, config_value: str):
        '''
        Initialize the configurable service.

        :param config_value: A scalar configuration value injected at construction.
        :type config_value: str
        '''

        # Assign the injected constant.
        self.config_value = config_value


# *** fixtures

# ** fixture: make_di_service
@pytest.fixture
def make_di_service():
    '''
    Fixture returning a factory that builds a mock DIService.

    :return: A factory that produces a mock DIService with a stubbed list_all.
    :rtype: Callable
    '''

    # Build a factory returning a spec'd mock DIService with list_all stubbed.
    def _make(registrations=None, constants=None) -> DIService:
        di_service = mock.Mock(spec=DIService)
        di_service.list_all.return_value = (list(registrations or []), dict(constants or {}))
        return di_service

    # Return the factory.
    return _make


# ** fixture: resolver_registrations
@pytest.fixture
def resolver_registrations() -> list:
    '''
    Fixture providing a fresh set of service registrations for the resolver.

    :return: A list of service registrations.
    :rtype: list
    '''

    # Build a coherent registration set: a plain service, a flag-switched
    # service, a constant-injected service, and a registration that resolves
    # to no type.
    return [
        ServiceRegistration(
            id='simple_service',
            module_path=MODULE_PATH,
            class_name='SimpleService',
        ),
        ServiceRegistration(
            id='flagged_service',
            module_path=MODULE_PATH,
            class_name='SimpleService',
            dependencies=[
                FlaggedDependency(
                    module_path=MODULE_PATH,
                    class_name='DependentService',
                    flag='alt',
                ),
            ],
        ),
        ServiceRegistration(
            id='configurable_service',
            module_path=MODULE_PATH,
            class_name='ConfigurableService',
            parameters={'config_value': 'default_value'},
        ),
        ServiceRegistration(
            id='no_type_service',
        ),
    ]


# ** fixture: resolver
@pytest.fixture
def resolver(resolver_registrations: list, make_di_service) -> ServiceResolver:
    '''
    Fixture providing a ServiceResolver backed by a mock DI service.

    :param resolver_registrations: The registration set fixture.
    :type resolver_registrations: list
    :param make_di_service: The mock DI service factory fixture.
    :type make_di_service: Callable
    :return: A configured ServiceResolver.
    :rtype: ServiceResolver
    '''

    # Build a resolver with a mock DI service and identity parameter parsing.
    return ServiceResolver(make_di_service(registrations=resolver_registrations))


# ** fixture: flagged_param_registration
@pytest.fixture
def flagged_param_registration() -> ServiceRegistration:
    '''
    Fixture providing a registration with default and flagged parameters.

    :return: A service registration with a flagged parameter override.
    :rtype: ServiceRegistration
    '''

    # Build a registration whose 'alt' flag overrides the default parameters.
    return ServiceRegistration(
        id='svc',
        module_path=MODULE_PATH,
        class_name='ConfigurableService',
        parameters={'config_value': 'default_value'},
        dependencies=[
            FlaggedDependency(
                module_path=MODULE_PATH,
                class_name='ConfigurableService',
                flag='alt',
                parameters={'config_value': 'alt_value'},
            ),
        ],
    )


# *** tests

# ** test: injectable_parameter_names_no_args
def test_injectable_parameter_names_no_args():
    '''
    Test that a dependency-free service yields no injectable parameter names.
    '''

    # Assert a service with no constructor parameters returns an empty list.
    assert injectable_parameter_names(SimpleService) == []


# ** test: injectable_parameter_names_with_dependency
def test_injectable_parameter_names_with_dependency():
    '''
    Test that a service with a constructor dependency yields its parameter name.
    '''

    # Assert the injected dependency parameter is identified.
    assert injectable_parameter_names(DependentService) == ['simple_service']


# ** test: injectable_parameter_names_scalar
def test_injectable_parameter_names_scalar():
    '''
    Test that a service with a scalar parameter yields its parameter name.
    '''

    # Assert the scalar parameter is identified.
    assert injectable_parameter_names(ConfigurableService) == ['config_value']


# ** test: normalize_flags_mixed
def test_normalize_flags_mixed():
    '''
    Test that normalize_flags flattens strings, lists, and tuples.
    '''

    # Assert mixed flag inputs are flattened into a single list.
    assert normalize_flags('a', ['b', 'c'], ('d', 'e')) == ['a', 'b', 'c', 'd', 'e']


# ** test: normalize_flags_empty
def test_normalize_flags_empty():
    '''
    Test that normalize_flags returns an empty list when given no flags.
    '''

    # Assert no flags produces an empty list.
    assert normalize_flags() == []


# ** test: normalize_flags_coerces_non_string
def test_normalize_flags_coerces_non_string():
    '''
    Test that normalize_flags coerces non-string scalars and nested members to strings.
    '''

    # Assert scalar and nested non-string flags are stringified per the List[str] contract.
    assert normalize_flags(1, [2, 3], (4,)) == ['1', '2', '3', '4']


# ** test: normalize_flags_coerces_none
def test_normalize_flags_coerces_none():
    '''
    Test that normalize_flags coerces None consistently whether scalar or nested.
    '''

    # Assert both a scalar None and a None nested in a list become the string 'None'.
    assert normalize_flags(None, [None]) == ['None', 'None']


# ** test: create_cache_key_no_flags
def test_create_cache_key_no_flags():
    '''
    Test that create_cache_key returns the base key without flags.
    '''

    # Assert the base cache key is returned for empty/none flags.
    assert create_cache_key() == 'feature_services'
    assert create_cache_key([]) == 'feature_services'


# ** test: create_cache_key_with_flags
def test_create_cache_key_with_flags():
    '''
    Test that create_cache_key appends underscore-joined flags.
    '''

    # Assert flags are appended to the cache key.
    assert create_cache_key(['a', 'b']) == 'feature_services_a_b'


# ** test: merge_settings_appends_and_prioritizes
def test_merge_settings_appends_and_prioritizes():
    '''
    Test that merge_settings appends default-only configs and prioritizes repository constants.
    '''

    # Arrange an existing repository registration and constants.
    existing = ServiceRegistration(id='a', module_path=MODULE_PATH, class_name='SimpleService')
    configs = [existing]
    constants = {'shared': 'repo', 'repo_only': 'repo'}

    # Arrange default index (one overlapping id, one new) and default constants.
    default_index = {
        'a': ServiceRegistration(id='a', module_path=MODULE_PATH, class_name='ConfigurableService'),
        'b': ServiceRegistration(id='b', module_path=MODULE_PATH, class_name='SimpleService'),
    }
    default_constants = {'shared': 'default', 'default_only': 'default'}

    # Act on the merge.
    merged_configs, merged_constants = merge_settings(
        configs,
        constants,
        default_index,
        default_constants,
    )

    # Assert the default-only config is appended and the existing one is kept as-is.
    assert [config.id for config in merged_configs] == ['a', 'b']
    assert merged_configs[0] is existing

    # Assert repository constants win and default-only constants are merged in.
    assert merged_constants == {'shared': 'repo', 'repo_only': 'repo', 'default_only': 'default'}


# ** test: service_container_init_empty
def test_service_container_init_empty():
    '''
    Test that an empty container initializes with no providers.
    '''

    # Assert the container has no registered providers.
    container = ServiceContainer()
    assert len(container.container.providers) == 0


# ** test: service_container_init_with_services
def test_service_container_init_with_services():
    '''
    Test that a container initialized with services registers them.
    '''

    # Assert the initial service is registered.
    container = ServiceContainer(services={'simple_service': SimpleService})
    assert 'simple_service' in container.container.providers


# ** test: service_container_add_service
def test_service_container_add_service():
    '''
    Test that add_service registers a service and makes it resolvable.
    '''

    # Add a single service.
    container = ServiceContainer()
    container.add_service('simple_service', SimpleService)

    # Assert it was registered and resolves to the expected type.
    assert 'simple_service' in container.container.providers
    assert isinstance(container.get_service('simple_service'), SimpleService)


# ** test: service_container_add_service_new_instance_per_call
def test_service_container_add_service_new_instance_per_call():
    '''
    Test that Factory providers resolve as new instances per call.
    '''

    # Resolve two instances of the same service.
    container = ServiceContainer(services={'simple_service': SimpleService})
    instance_a = container.get_service('simple_service')
    instance_b = container.get_service('simple_service')

    # Assert both are SimpleService instances but distinct objects.
    assert isinstance(instance_a, SimpleService)
    assert isinstance(instance_b, SimpleService)
    assert instance_a is not instance_b


# ** test: service_container_add_services
def test_service_container_add_services():
    '''
    Test that add_services registers multiple services at once.
    '''

    # Add multiple services.
    container = ServiceContainer()
    container.add_services({
        'simple_service': SimpleService,
        'dependent_service': DependentService,
    })

    # Assert both were registered and resolve correctly.
    assert isinstance(container.get_service('simple_service'), SimpleService)
    assert isinstance(container.get_service('dependent_service'), DependentService)


# ** test: service_container_add_constants
def test_service_container_add_constants():
    '''
    Test that add_constants registers scalar values returned as-is.
    '''

    # Register a scalar constant.
    container = ServiceContainer()
    container.add_constants({'config_value': 'test_config'})

    # Assert the constant resolves to the original value.
    assert container.get_service('config_value') == 'test_config'


# ** test: service_container_add_constants_injected_into_service
def test_service_container_add_constants_injected_into_service():
    '''
    Test that constants are injected into services that depend on them.
    '''

    # Register a constant first, then a service that depends on it.
    container = ServiceContainer()
    container.add_constants({'config_value': 'test_config'})
    container.add_service('configurable_service', ConfigurableService)

    # Resolve the service and assert the constant was injected.
    service = container.get_service('configurable_service')
    assert isinstance(service, ConfigurableService)
    assert service.config_value == 'test_config'


# ** test: service_container_add_services_two_pass
def test_service_container_add_services_two_pass():
    '''
    Test that add_services registers scalars before types so factory kwargs wire.
    '''

    # Register a scalar and a dependent service in a single mixed call.
    container = ServiceContainer()
    container.add_services({
        'config_value': 'test_config',
        'configurable_service': ConfigurableService,
    })

    # Assert the scalar resolves as-is and is injected into the service.
    assert container.get_service('config_value') == 'test_config'
    service = container.get_service('configurable_service')
    assert isinstance(service, ConfigurableService)
    assert service.config_value == 'test_config'


# ** test: service_container_get_service_not_found
def test_service_container_get_service_not_found():
    '''
    Test that get_service raises a raw (non-structured) error for a missing provider.
    '''

    # Attempt to resolve a service that was never registered.
    container = ServiceContainer()
    with pytest.raises(Exception) as exc_info:
        container.get_service('missing_service')

    # Assert the engine raised a raw error, not a structured TiferetError.
    assert not isinstance(exc_info.value, TiferetError)


# ** test: service_container_remove_service
def test_service_container_remove_service():
    '''
    Test that remove_service deregisters a service.
    '''

    # Remove the registered service.
    container = ServiceContainer(services={'simple_service': SimpleService})
    container.remove_service('simple_service')

    # Assert it was removed and is no longer resolvable.
    assert 'simple_service' not in container.container.providers
    with pytest.raises(Exception):
        container.get_service('simple_service')


# ** test: service_container_remove_service_nonexistent
def test_service_container_remove_service_nonexistent():
    '''
    Test that remove_service is a no-op for an unregistered service ID.
    '''

    # Removing an unregistered ID should not raise.
    container = ServiceContainer()
    container.remove_service('missing_service')

    # Assert the container is still empty.
    assert len(container.container.providers) == 0


# ** test: service_container_cascading_dependency_injection
def test_service_container_cascading_dependency_injection():
    '''
    Test that a service with a constructor dependency resolves both correctly.
    '''

    # Register SimpleService first, then DependentService which depends on it.
    container = ServiceContainer()
    container.add_service('simple_service', SimpleService)
    container.add_service('dependent_service', DependentService)

    # Resolve the dependent service and assert the cascade.
    service = container.get_service('dependent_service')
    assert isinstance(service, DependentService)
    assert isinstance(service.simple_service, SimpleService)


# ** test: service_resolver_create_cache_key
def test_service_resolver_create_cache_key(resolver: ServiceResolver):
    '''
    Test that the resolver delegates create_cache_key to the module helper.

    :param resolver: The resolver fixture.
    :type resolver: ServiceResolver
    '''

    # Assert the cache key with and without flags.
    assert resolver.create_cache_key() == 'feature_services'
    assert resolver.create_cache_key(['a', 'b']) == 'feature_services_a_b'


# ** test: service_resolver_normalize_flags
def test_service_resolver_normalize_flags():
    '''
    Test that the resolver static normalize_flags flattens mixed inputs.
    '''

    # Assert mixed flag inputs are flattened.
    assert ServiceResolver.normalize_flags('a', ['b', 'c'], ('d',)) == ['a', 'b', 'c', 'd']


# ** test: service_resolver_build_container_default
def test_service_resolver_build_container_default(resolver: ServiceResolver):
    '''
    Test that build_container resolves default services and constants.

    :param resolver: The resolver fixture.
    :type resolver: ServiceResolver
    '''

    # Build the default container.
    container = resolver.build_container([])

    # Assert it is a ServiceContainer with the default services resolvable.
    assert isinstance(container, ServiceContainer)
    assert isinstance(container.get_service('simple_service'), SimpleService)

    # Assert the constant-injected service resolves with its default parameter.
    configurable = container.get_service('configurable_service')
    assert isinstance(configurable, ConfigurableService)
    assert configurable.config_value == 'default_value'


# ** test: service_resolver_build_container_flagged
def test_service_resolver_build_container_flagged(resolver: ServiceResolver):
    '''
    Test that build_container honors flagged type overrides.

    :param resolver: The resolver fixture.
    :type resolver: ServiceResolver
    '''

    # Build the flagged container.
    container = resolver.build_container(['alt'])

    # Assert the flagged service resolves to the overridden type with its cascade.
    service = container.get_service('flagged_service')
    assert isinstance(service, DependentService)
    assert isinstance(service.simple_service, SimpleService)


# ** test: service_resolver_build_container_cached
def test_service_resolver_build_container_cached(resolver: ServiceResolver):
    '''
    Test that build_container caches containers per flag key.

    :param resolver: The resolver fixture.
    :type resolver: ServiceResolver
    '''

    # Build the default container twice.
    first = resolver.build_container([])
    second = resolver.build_container([])

    # Assert the same cached instance is returned.
    assert first is second


# ** test: service_resolver_build_container_skips_no_type
def test_service_resolver_build_container_skips_no_type(resolver: ServiceResolver):
    '''
    Test that registrations resolving to no type are left unregistered.

    :param resolver: The resolver fixture.
    :type resolver: ServiceResolver
    '''

    # Build the default container.
    container = resolver.build_container([])

    # Assert the no-type registration was skipped.
    assert 'no_type_service' not in container.container.providers


# ** test: service_resolver_get_dependency_default
def test_service_resolver_get_dependency_default(resolver: ServiceResolver):
    '''
    Test that get_dependency resolves a service with no flags.

    :param resolver: The resolver fixture.
    :type resolver: ServiceResolver
    '''

    # Assert the default resolution returns the expected type.
    assert isinstance(resolver.get_dependency('simple_service'), SimpleService)


# ** test: service_resolver_get_dependency_varargs_flag
def test_service_resolver_get_dependency_varargs_flag(resolver: ServiceResolver):
    '''
    Test that get_dependency accepts flags as varargs.

    :param resolver: The resolver fixture.
    :type resolver: ServiceResolver
    '''

    # Assert the varargs flag form resolves the flagged type.
    service = resolver.get_dependency('flagged_service', 'alt')
    assert isinstance(service, DependentService)


# ** test: service_resolver_get_dependency_list_flag
def test_service_resolver_get_dependency_list_flag(resolver: ServiceResolver):
    '''
    Test that get_dependency accepts flags as a list.

    :param resolver: The resolver fixture.
    :type resolver: ServiceResolver
    '''

    # Assert the list flag form resolves the flagged type.
    service = resolver.get_dependency('flagged_service', ['alt'])
    assert isinstance(service, DependentService)


# ** test: service_resolver_load_constants_default
def test_service_resolver_load_constants_default(
        resolver: ServiceResolver,
        flagged_param_registration: ServiceRegistration,
    ):
    '''
    Test that load_constants uses default parameters when no flag matches.

    :param resolver: The resolver fixture.
    :type resolver: ServiceResolver
    :param flagged_param_registration: The flagged-parameter registration fixture.
    :type flagged_param_registration: ServiceRegistration
    '''

    # Load constants with no flags.
    result = resolver.load_constants(
        configurations=[flagged_param_registration],
        constants={'top': 'value'},
        flags=[],
    )

    # Assert the top-level constant and default parameter are present.
    assert result == {'top': 'value', 'config_value': 'default_value'}


# ** test: service_resolver_load_constants_flagged
def test_service_resolver_load_constants_flagged(
        resolver: ServiceResolver,
        flagged_param_registration: ServiceRegistration,
    ):
    '''
    Test that load_constants uses flagged parameters when a flag matches.

    :param resolver: The resolver fixture.
    :type resolver: ServiceResolver
    :param flagged_param_registration: The flagged-parameter registration fixture.
    :type flagged_param_registration: ServiceRegistration
    '''

    # Load constants with the matching flag.
    result = resolver.load_constants(
        configurations=[flagged_param_registration],
        constants={'top': 'value'},
        flags=['alt'],
    )

    # Assert the flagged parameter overrides the default.
    assert result == {'top': 'value', 'config_value': 'alt_value'}


# ** test: service_resolver_list_all_settings_merges_defaults
def test_service_resolver_list_all_settings_merges_defaults(make_di_service):
    '''
    Test that list_all_settings merges bootstrap defaults beneath repository settings.

    :param make_di_service: The mock DI service factory fixture.
    :type make_di_service: Callable
    '''

    # Arrange a mock DI service with one repository registration and constants.
    repo_registration = ServiceRegistration(id='repo_svc', module_path=MODULE_PATH, class_name='SimpleService')
    fake = make_di_service(
        registrations=[repo_registration],
        constants={'shared': 'repo', 'repo_only': 'repo'},
    )

    # Arrange default index (one overlapping id, one new) and default constants.
    default_index = {
        'repo_svc': ServiceRegistration(id='repo_svc', module_path=MODULE_PATH, class_name='ConfigurableService'),
        'default_svc': ServiceRegistration(id='default_svc', module_path=MODULE_PATH, class_name='SimpleService'),
    }
    default_constants = {'shared': 'default', 'default_only': 'default'}

    # Build a resolver with the defaults and read the merged settings.
    merged_resolver = ServiceResolver(
        fake,
        default_config_index=default_index,
        default_di_constants=default_constants,
    )
    configs, constants = merged_resolver.list_all_settings()

    # Assert the default-only config is appended and the repository one is kept.
    assert {config.id for config in configs} == {'repo_svc', 'default_svc'}
    assert len(configs) == 2

    # Assert repository constants win and default-only constants are merged in.
    assert constants['shared'] == 'repo'
    assert constants['repo_only'] == 'repo'
    assert constants['default_only'] == 'default'


# ** test: service_resolver_parse_parameter_identity_default
def test_service_resolver_parse_parameter_identity_default(make_di_service):
    '''
    Test that the default parse_parameter leaves constant values unchanged.

    :param make_di_service: The mock DI service factory fixture.
    :type make_di_service: Callable
    '''

    # Build a resolver with the identity default parser.
    identity_resolver = ServiceResolver(make_di_service())

    # Assert constant values pass through unchanged.
    result = identity_resolver.load_constants(constants={'key': 'value'})
    assert result == {'key': 'value'}


# ** test: service_resolver_parse_parameter_injection
def test_service_resolver_parse_parameter_injection(make_di_service):
    '''
    Test that an injected parse_parameter transforms constant values.

    :param make_di_service: The mock DI service factory fixture.
    :type make_di_service: Callable
    '''

    # Build a resolver with an injected transforming parser.
    parsing_resolver = ServiceResolver(
        make_di_service(),
        parse_parameter=lambda value: f'parsed:{value}',
    )

    # Assert constant values are transformed by the injected parser.
    result = parsing_resolver.load_constants(constants={'key': 'value'})
    assert result == {'key': 'parsed:value'}
