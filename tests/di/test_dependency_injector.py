"""Tiferet DI Dependency Injector Container Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet import assets as a
from tiferet.assets.exceptions import TiferetError
from tiferet.domain import (
    ServiceDependency,
    AppServiceDependency,
    FlaggedDependency,
    ServiceRegistration,
)
from tiferet.interfaces.di import DIService
from tiferet.di.dependency_injector import (
    DIDynamicServiceContainer,
    DIAppServiceContainer,
    DIDynamicServiceResolver,
)

# *** constants

# ** constant: module_path
MODULE_PATH = 'tests.di.test_dependency_injector'

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

# ** fixture: simple_dependency
@pytest.fixture
def simple_dependency() -> ServiceDependency:
    '''
    Fixture providing a ServiceDependency pointing at SimpleService.

    :return: A ServiceDependency for SimpleService.
    :rtype: ServiceDependency
    '''

    # Return a dependency with no declared parameters.
    return ServiceDependency(module_path=MODULE_PATH, class_name='SimpleService')

# ** fixture: dependent_dependency
@pytest.fixture
def dependent_dependency() -> ServiceDependency:
    '''
    Fixture providing a ServiceDependency pointing at DependentService.

    :return: A ServiceDependency for DependentService.
    :rtype: ServiceDependency
    '''

    # Return a dependency with no declared parameters.
    return ServiceDependency(module_path=MODULE_PATH, class_name='DependentService')

# ** fixture: configurable_dependency
@pytest.fixture
def configurable_dependency() -> ServiceDependency:
    '''
    Fixture providing a ServiceDependency pointing at ConfigurableService with no parameters.

    :return: A ServiceDependency for ConfigurableService (no parameters).
    :rtype: ServiceDependency
    '''

    # Return a dependency with no declared parameters (constant must be pre-registered).
    return ServiceDependency(module_path=MODULE_PATH, class_name='ConfigurableService')

# ** fixture: configurable_with_params_dependency
@pytest.fixture
def configurable_with_params_dependency() -> ServiceDependency:
    '''
    Fixture providing a ServiceDependency for ConfigurableService with an inline parameter.

    :return: A ServiceDependency for ConfigurableService with a declared config_value.
    :rtype: ServiceDependency
    '''

    # Return a dependency whose declared parameters carry the config value.
    return ServiceDependency(
        module_path=MODULE_PATH,
        class_name='ConfigurableService',
        parameters={'config_value': 'param_value'},
    )

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
    Fixture providing a coherent set of service registrations for the resolver.

    :return: A list of service registrations (plain, flag-switched, constant-injected, no-type).
    :rtype: list
    '''

    # Build a registration set: a plain service, a flag-switched service, a
    # constant-injected service, and a registration that resolves to no type.
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

# *** tests

# ** test: init_empty
def test_init_empty():
    '''
    Test that an empty container initializes with no providers.
    '''

    # Assert the container has no registered providers.
    container = DIDynamicServiceContainer()
    assert len(container.container.providers) == 0

# ** test: add_service_resolves
def test_add_service_resolves(simple_dependency: ServiceDependency):
    '''
    Test that add_service registers a service and makes it resolvable.

    :param simple_dependency: The simple service dependency fixture.
    :type simple_dependency: ServiceDependency
    '''

    # Add a single service and assert it resolves to the expected type.
    container = DIDynamicServiceContainer()
    container.add_service('simple_service', simple_dependency)
    assert isinstance(container.get_dependency('simple_service'), SimpleService)

# ** test: add_service_new_instance_per_call
def test_add_service_new_instance_per_call(simple_dependency: ServiceDependency):
    '''
    Test that Factory providers resolve as new instances per call.

    :param simple_dependency: The simple service dependency fixture.
    :type simple_dependency: ServiceDependency
    '''

    # Resolve two instances of the same service.
    container = DIDynamicServiceContainer()
    container.add_service('simple_service', simple_dependency)
    instance_a = container.get_dependency('simple_service')
    instance_b = container.get_dependency('simple_service')

    # Assert both are SimpleService instances but distinct objects.
    assert isinstance(instance_a, SimpleService)
    assert isinstance(instance_b, SimpleService)
    assert instance_a is not instance_b

# ** test: add_constant_resolves
def test_add_constant_resolves():
    '''
    Test that add_constant registers a scalar value returned as-is.
    '''

    # Register a scalar constant and assert it resolves to the original value.
    container = DIDynamicServiceContainer()
    container.add_constant('config_value', 'test_config')
    assert container.get_dependency('config_value') == 'test_config'

# ** test: add_constant_injected_into_service
def test_add_constant_injected_into_service(configurable_dependency: ServiceDependency):
    '''
    Test that a pre-registered constant is injected into a service that depends on it.

    :param configurable_dependency: The configurable service dependency fixture.
    :type configurable_dependency: ServiceDependency
    '''

    # Register the constant first, then the service that depends on it.
    container = DIDynamicServiceContainer()
    container.add_constant('config_value', 'test_config')
    container.add_service('configurable_service', configurable_dependency)

    # Resolve the service and assert the constant was injected.
    service = container.get_dependency('configurable_service')
    assert isinstance(service, ConfigurableService)
    assert service.config_value == 'test_config'

# ** test: add_service_registers_parameters_as_constants
def test_add_service_registers_parameters_as_constants(
        configurable_with_params_dependency: ServiceDependency,
    ):
    '''
    Test that add_service registers declared parameters as constants before the factory.

    :param configurable_with_params_dependency: The dependency with an inline parameter.
    :type configurable_with_params_dependency: ServiceDependency
    '''

    # Register the service whose dependency carries the parameter value.
    container = DIDynamicServiceContainer()
    container.add_service('configurable_service', configurable_with_params_dependency)

    # Assert the parameter was injected into the resolved service.
    service = container.get_dependency('configurable_service')
    assert isinstance(service, ConfigurableService)
    assert service.config_value == 'param_value'

# ** test: add_service_parameter_wins_over_constant
def test_add_service_parameter_wins_over_constant(
        configurable_with_params_dependency: ServiceDependency,
    ):
    '''
    Test that a declared parameter on a dependency overwrites a pre-existing constant.

    :param configurable_with_params_dependency: The dependency with an inline parameter.
    :type configurable_with_params_dependency: ServiceDependency
    '''

    # Pre-register a constant with a different value.
    container = DIDynamicServiceContainer()
    container.add_constant('config_value', 'existing_value')

    # Register the service whose parameter carries a new value for the same key.
    container.add_service('configurable_service', configurable_with_params_dependency)

    # Assert the parameter value (from the dependency) wins over the pre-existing constant.
    service = container.get_dependency('configurable_service')
    assert isinstance(service, ConfigurableService)
    assert service.config_value == 'param_value'

# ** test: load_container_constants_before_services
def test_load_container_constants_before_services(configurable_dependency: ServiceDependency):
    '''
    Test that load_container registers constants before services so factory kwargs wire.

    :param configurable_dependency: The configurable service dependency fixture.
    :type configurable_dependency: ServiceDependency
    '''

    # Load constants and services together; constants must be available when the factory builds.
    container = DIDynamicServiceContainer(
        services={'configurable_service': configurable_dependency},
        constants={'config_value': 'test_config'},
    )

    # Assert the constant-injected service resolves correctly.
    service = container.get_dependency('configurable_service')
    assert isinstance(service, ConfigurableService)
    assert service.config_value == 'test_config'

# ** test: constructor_delegates_to_load_container
def test_constructor_delegates_to_load_container(simple_dependency: ServiceDependency):
    '''
    Test that the constructor with services and constants delegates to load_container.

    :param simple_dependency: The simple service dependency fixture.
    :type simple_dependency: ServiceDependency
    '''

    # Construct with both a service and a constant.
    container = DIDynamicServiceContainer(
        services={'simple_service': simple_dependency},
        constants={'config_value': 'test_config'},
    )

    # Assert both are registered and resolvable.
    assert isinstance(container.get_dependency('simple_service'), SimpleService)
    assert container.get_dependency('config_value') == 'test_config'

# ** test: get_dependency_missing_raises_raw_error
def test_get_dependency_missing_raises_raw_error():
    '''
    Test that get_dependency raises a raw (non-structured) error for a missing provider.
    '''

    # Attempt to resolve a dependency that was never registered.
    container = DIDynamicServiceContainer()
    with pytest.raises(Exception) as exc_info:
        container.get_dependency('missing_dependency')

    # Assert the engine raised a raw error, not a structured TiferetError.
    assert not isinstance(exc_info.value, TiferetError)

# ** test: remove_dependency_removes
def test_remove_dependency_removes(simple_dependency: ServiceDependency):
    '''
    Test that remove_dependency deregisters a dependency.

    :param simple_dependency: The simple service dependency fixture.
    :type simple_dependency: ServiceDependency
    '''

    # Register a service then remove it.
    container = DIDynamicServiceContainer()
    container.add_service('simple_service', simple_dependency)
    container.remove_dependency('simple_service')

    # Assert it was removed and is no longer resolvable.
    assert 'simple_service' not in container.container.providers
    with pytest.raises(Exception):
        container.get_dependency('simple_service')

# ** test: remove_dependency_idempotent
def test_remove_dependency_idempotent():
    '''
    Test that remove_dependency is a no-op for an unregistered dependency ID.
    '''

    # Removing an unregistered ID should not raise.
    container = DIDynamicServiceContainer()
    container.remove_dependency('missing_dependency')

    # Assert the container is still empty.
    assert len(container.container.providers) == 0

# ** test: cascading_dependency_injection
def test_cascading_dependency_injection(
        simple_dependency: ServiceDependency,
        dependent_dependency: ServiceDependency,
    ):
    '''
    Test that a service with a constructor dependency resolves both correctly.

    :param simple_dependency: The simple service dependency fixture.
    :type simple_dependency: ServiceDependency
    :param dependent_dependency: The dependent service dependency fixture.
    :type dependent_dependency: ServiceDependency
    '''

    # Register SimpleService first, then DependentService which depends on it.
    container = DIDynamicServiceContainer()
    container.add_service('simple_service', simple_dependency)
    container.add_service('dependent_service', dependent_dependency)

    # Resolve the dependent service and assert the cascade.
    service = container.get_dependency('dependent_service')
    assert isinstance(service, DependentService)
    assert isinstance(service.simple_service, SimpleService)

# ** test: app_container_singleton_identity
def test_app_container_singleton_identity():
    '''
    Test that DIAppServiceContainer registers services as singletons (one shared instance).
    '''

    # Build an app container from a single app service dependency.
    container = DIAppServiceContainer.from_dependencies(
        services=[
            AppServiceDependency(
                service_id='simple_service',
                module_path=MODULE_PATH,
                class_name='SimpleService',
            ),
        ],
    )

    # Resolve the service twice and assert the same instance is returned.
    first = container.get_dependency('simple_service')
    second = container.get_dependency('simple_service')
    assert isinstance(first, SimpleService)
    assert first is second

# ** test: app_container_event_receives_repo_singleton
def test_app_container_event_receives_repo_singleton():
    '''
    Test that a dependent service is wired to the same singleton as its sibling.
    '''

    # Build an app container with a repo-like service and an event-like dependent service.
    container = DIAppServiceContainer.from_dependencies(
        services=[
            AppServiceDependency(
                service_id='simple_service',
                module_path=MODULE_PATH,
                class_name='SimpleService',
            ),
            AppServiceDependency(
                service_id='dependent_service',
                module_path=MODULE_PATH,
                class_name='DependentService',
            ),
        ],
    )

    # Resolve the sibling and the dependent service.
    repo = container.get_dependency('simple_service')
    event = container.get_dependency('dependent_service')

    # Assert the dependent service received the shared singleton sibling.
    assert isinstance(event, DependentService)
    assert event.simple_service is repo

# ** test: app_container_constants_before_services
def test_app_container_constants_before_services():
    '''
    Test that from_dependencies registers constants before services so kwargs wire.
    '''

    # Build an app container with a constant and a service that depends on it.
    container = DIAppServiceContainer.from_dependencies(
        services=[
            AppServiceDependency(
                service_id='configurable_service',
                module_path=MODULE_PATH,
                class_name='ConfigurableService',
            ),
        ],
        constants={'config_value': 'shared'},
    )

    # Assert the constant-injected service resolves correctly.
    service = container.get_dependency('configurable_service')
    assert isinstance(service, ConfigurableService)
    assert service.config_value == 'shared'

# ** test: app_container_from_dependencies_core_catalog_resolves
def test_app_container_from_dependencies_core_catalog_resolves():
    '''
    Test that the full core service catalog resolves through the app container.
    '''

    # Reconstitute the core catalog into app service dependencies and constants.
    services = [
        AppServiceDependency.model_validate(record)
        for record in a.app.CORE_DEFAULT_SERVICES.values()
    ]
    constants = dict(a.app.CORE_DEFAULT_CONSTANTS)

    # Build the app container over the core catalog.
    container = DIAppServiceContainer.from_dependencies(services=services, constants=constants)

    # Assert every core service id resolves to a concrete instance.
    for service_id in a.app.CORE_DEFAULT_SERVICES:
        assert container.get_dependency(service_id) is not None

# ** test: resolver_build_container_default
def test_resolver_build_container_default(resolver_registrations, make_di_service):
    '''
    Test that build_container resolves default services and constant-injected parameters.

    :param resolver_registrations: The registration set fixture.
    :type resolver_registrations: list
    :param make_di_service: The mock DI service factory fixture.
    :type make_di_service: Callable
    '''

    # Build the default container from the mock DI service.
    resolver = DIDynamicServiceResolver(make_di_service(registrations=resolver_registrations))
    container = resolver.build_container([])

    # Assert it is a DIDynamicServiceContainer with the default service resolvable.
    assert isinstance(container, DIDynamicServiceContainer)
    assert isinstance(container.get_dependency('simple_service'), SimpleService)

    # Assert the constant-injected service resolves with its default parameter.
    configurable = container.get_dependency('configurable_service')
    assert isinstance(configurable, ConfigurableService)
    assert configurable.config_value == 'default_value'

# ** test: resolver_flagged_type_override
def test_resolver_flagged_type_override(resolver_registrations, make_di_service):
    '''
    Test that a flagged registration resolves to its overridden type.

    :param resolver_registrations: The registration set fixture.
    :type resolver_registrations: list
    :param make_di_service: The mock DI service factory fixture.
    :type make_di_service: Callable
    '''

    # Resolve the flagged service under the 'alt' flag.
    resolver = DIDynamicServiceResolver(make_di_service(registrations=resolver_registrations))
    service = resolver.get_dependency('flagged_service', 'alt')

    # Assert the flagged type override took effect.
    assert isinstance(service, DependentService)

# ** test: resolver_skips_no_type_registration
def test_resolver_skips_no_type_registration(resolver_registrations, make_di_service):
    '''
    Test that a registration resolving to no service is left unregistered.

    :param resolver_registrations: The registration set fixture.
    :type resolver_registrations: list
    :param make_di_service: The mock DI service factory fixture.
    :type make_di_service: Callable
    '''

    # Build the default container.
    resolver = DIDynamicServiceResolver(make_di_service(registrations=resolver_registrations))
    container = resolver.build_container([])

    # Assert the no-type registration was skipped.
    assert 'no_type_service' not in container.container.providers

# ** test: resolver_parse_parameter_applied
def test_resolver_parse_parameter_applied(make_di_service):
    '''
    Test that parse_parameter is applied to top-level constants and per-dependency parameters.

    :param make_di_service: The mock DI service factory fixture.
    :type make_di_service: Callable
    '''

    # Build a resolver with an injected transforming parser.
    registrations = [
        ServiceRegistration(
            id='configurable_service',
            module_path=MODULE_PATH,
            class_name='ConfigurableService',
            parameters={'config_value': 'raw'},
        ),
    ]
    resolver = DIDynamicServiceResolver(
        make_di_service(registrations=registrations, constants={'top': 'value'}),
        parse_parameter=lambda value: f'parsed:{value}',
    )
    container = resolver.build_container([])

    # Assert both the top-level constant and the dependency parameter were parsed once.
    assert container.get_dependency('top') == 'parsed:value'
    assert container.get_dependency('configurable_service').config_value == 'parsed:raw'

# ** test: resolver_caches_container_per_flag
def test_resolver_caches_container_per_flag(resolver_registrations, make_di_service):
    '''
    Test that the resolver caches the container per flag set (builds once).

    :param resolver_registrations: The registration set fixture.
    :type resolver_registrations: list
    :param make_di_service: The mock DI service factory fixture.
    :type make_di_service: Callable
    '''

    # Resolve twice under the same (empty) flag set.
    di_service = make_di_service(registrations=resolver_registrations)
    resolver = DIDynamicServiceResolver(di_service)
    resolver.get_dependency('simple_service')
    resolver.get_dependency('simple_service')

    # Assert the DI service was read once, proving the container was cached.
    assert di_service.list_all.call_count == 1

# ** test: resolver_cascading_get_dependency
def test_resolver_cascading_get_dependency(resolver_registrations, make_di_service):
    '''
    Test that a resolved service has its sibling dependency wired in.

    :param resolver_registrations: The registration set fixture.
    :type resolver_registrations: list
    :param make_di_service: The mock DI service factory fixture.
    :type make_di_service: Callable
    '''

    # Resolve the flagged (dependent) service under the 'alt' flag.
    resolver = DIDynamicServiceResolver(make_di_service(registrations=resolver_registrations))
    service = resolver.get_dependency('flagged_service', 'alt')

    # Assert the cascaded sibling was injected.
    assert isinstance(service.simple_service, SimpleService)
