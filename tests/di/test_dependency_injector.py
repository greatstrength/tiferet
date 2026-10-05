"""Tiferet DI Dependency Injector Container Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet import assets as a
from tiferet.assets import TiferetError
from tiferet.di.dependency_injector import (
    DIAppServiceContainer,
    DIDynamicServiceContainer,
    DIDynamicServiceResolver,
    DI_DEPENDENCY_NOT_REGISTERED_ID,
)
from tiferet.domain import (
    AppServiceDependency,
    FlaggedDependency,
    ServiceDependency,
    ServiceRegistration,
)
from tiferet.interfaces import DIService, ServiceError

# *** constants

# ** constant: module_path
MODULE_PATH = 'tests.di.test_dependency_injector'

# *** classes

# ** class: simple_service
class SimpleService:
    '''
    A no-arg service used to exercise Factory and Singleton wiring.
    '''

    pass

# ** class: dependent_service
class DependentService:
    '''
    A service that depends on a sibling SimpleService.
    '''

    # * attribute: simple_service
    simple_service: SimpleService

    # * init
    def __init__(self, simple_service: SimpleService):
        '''
        Initialize the dependent service.

        :param simple_service: The injected simple service.
        :type simple_service: SimpleService
        '''

        # Assign the injected simple service.
        self.simple_service = simple_service

# ** class: configurable_service
class ConfigurableService:
    '''
    A service configured by a scalar value.
    '''

    # * attribute: config_value
    config_value: str

    # * init
    def __init__(self, config_value: str):
        '''
        Initialize the configurable service.

        :param config_value: The injected configuration value.
        :type config_value: str
        '''

        # Assign the injected configuration value.
        self.config_value = config_value

# *** fixtures

# ** fixture: simple_dependency
@pytest.fixture
def simple_dependency() -> ServiceDependency:
    '''
    A ServiceDependency bound to SimpleService.

    :return: The simple service dependency.
    :rtype: ServiceDependency
    '''

    # Bind the fixture module's SimpleService.
    return ServiceDependency(
        module_path=MODULE_PATH,
        class_name='SimpleService',
    )

# ** fixture: dependent_dependency
@pytest.fixture
def dependent_dependency() -> ServiceDependency:
    '''
    A ServiceDependency bound to DependentService.

    :return: The dependent service dependency.
    :rtype: ServiceDependency
    '''

    # Bind the fixture module's DependentService.
    return ServiceDependency(
        module_path=MODULE_PATH,
        class_name='DependentService',
    )

# ** fixture: configurable_dependency
@pytest.fixture
def configurable_dependency() -> ServiceDependency:
    '''
    A ServiceDependency bound to ConfigurableService with no parameters.

    :return: The configurable service dependency.
    :rtype: ServiceDependency
    '''

    # Bind ConfigurableService without declared parameters.
    return ServiceDependency(
        module_path=MODULE_PATH,
        class_name='ConfigurableService',
    )

# ** fixture: configurable_with_params_dependency
@pytest.fixture
def configurable_with_params_dependency() -> ServiceDependency:
    '''
    A ServiceDependency whose parameters supply config_value.

    :return: The parameterized configurable service dependency.
    :rtype: ServiceDependency
    '''

    # Declare the scalar parameter on the dependency itself.
    return ServiceDependency(
        module_path=MODULE_PATH,
        class_name='ConfigurableService',
        parameters={'config_value': 'param_value'},
    )

# ** fixture: make_di_service
@pytest.fixture
def make_di_service():
    '''
    A factory that builds a DIService mock from registrations and constants.

    :return: The DIService factory.
    :rtype: Callable
    '''

    # Return a mock whose list_all yields the supplied catalogs.
    def _make(registrations=None, constants=None) -> DIService:
        '''
        Build a DIService mock.

        :param registrations: The registrations list_all should return.
        :type registrations: list
        :param constants: The constants list_all should return.
        :type constants: dict
        :return: The mocked DI service.
        :rtype: DIService
        '''

        # Spec the mock and fix list_all's return value.
        di_service = mock.Mock(spec=DIService)
        di_service.list_all.return_value = (
            list(registrations or []),
            dict(constants or {}),
        )
        return di_service

    return _make

# ** fixture: resolver_registrations
@pytest.fixture
def resolver_registrations() -> list:
    '''
    The four service registrations used by resolver tests.

    :return: The registration rows, in catalog order.
    :rtype: list
    '''

    # Return the catalog rows in the required order.
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
    An empty dynamic container has no providers.

    :return: None
    :rtype: None
    '''

    # A freshly constructed container has an empty provider registry.
    assert len(DIDynamicServiceContainer().container.providers) == 0

# ** test: add_service_resolves
def test_add_service_resolves(simple_dependency):
    '''
    add_service registers a service that resolves to SimpleService.

    :param simple_dependency: The simple service dependency.
    :type simple_dependency: ServiceDependency
    :return: None
    :rtype: None
    '''

    # Register and resolve the simple service.
    container = DIDynamicServiceContainer()
    container.add_service('simple_service', simple_dependency)

    # The resolved value is a SimpleService.
    assert isinstance(container.get_dependency('simple_service'), SimpleService)

# ** test: add_service_new_instance_per_call
def test_add_service_new_instance_per_call(simple_dependency):
    '''
    Factory scope returns a new SimpleService on each resolution.

    :param simple_dependency: The simple service dependency.
    :type simple_dependency: ServiceDependency
    :return: None
    :rtype: None
    '''

    # Register the simple service once.
    container = DIDynamicServiceContainer()
    container.add_service('simple_service', simple_dependency)
    first = container.get_dependency('simple_service')
    second = container.get_dependency('simple_service')

    # Each resolution is a distinct SimpleService.
    assert isinstance(first, SimpleService)
    assert isinstance(second, SimpleService)
    assert first is not second

# ** test: add_constant_resolves
def test_add_constant_resolves():
    '''
    add_constant registers a value resolvable by id.

    :return: None
    :rtype: None
    '''

    # Register a scalar constant.
    container = DIDynamicServiceContainer()
    container.add_constant('config_value', 'test_config')

    # The constant resolves to its registered value.
    assert container.get_dependency('config_value') == 'test_config'

# ** test: add_constant_injected_into_service
def test_add_constant_injected_into_service(configurable_dependency):
    '''
    A constant registered before a service is injected into that service.

    :param configurable_dependency: The configurable service dependency.
    :type configurable_dependency: ServiceDependency
    :return: None
    :rtype: None
    '''

    # Register the constant before the service that consumes it.
    container = DIDynamicServiceContainer()
    container.add_constant('config_value', 'test_config')
    container.add_service('configurable_service', configurable_dependency)

    # The resolved service received the constant.
    assert container.get_dependency('configurable_service').config_value == 'test_config'

# ** test: add_service_registers_parameters_as_constants
def test_add_service_registers_parameters_as_constants(configurable_with_params_dependency):
    '''
    add_service alone registers declared parameters as constants.

    :param configurable_with_params_dependency: The parameterized dependency.
    :type configurable_with_params_dependency: ServiceDependency
    :return: None
    :rtype: None
    '''

    # Register only the parameterized service.
    container = DIDynamicServiceContainer()
    container.add_service('configurable_service', configurable_with_params_dependency)

    # The declared parameter is injected.
    assert container.get_dependency('configurable_service').config_value == 'param_value'

# ** test: add_service_parameter_wins_over_constant
def test_add_service_parameter_wins_over_constant(configurable_with_params_dependency):
    '''
    A service parameter overrides a pre-registered constant of the same id.

    :param configurable_with_params_dependency: The parameterized dependency.
    :type configurable_with_params_dependency: ServiceDependency
    :return: None
    :rtype: None
    '''

    # Pre-register a constant, then add the parameterized service.
    container = DIDynamicServiceContainer()
    container.add_constant('config_value', 'existing_value')
    container.add_service('configurable_service', configurable_with_params_dependency)

    # The service parameter wins.
    assert container.get_dependency('configurable_service').config_value == 'param_value'

# ** test: load_container_constants_before_services
def test_load_container_constants_before_services(configurable_dependency):
    '''
    Construction registers constants before services.

    :param configurable_dependency: The configurable service dependency.
    :type configurable_dependency: ServiceDependency
    :return: None
    :rtype: None
    '''

    # Load the service and its constant together.
    container = DIDynamicServiceContainer(
        services={'configurable_service': configurable_dependency},
        constants={'config_value': 'test_config'},
    )

    # The constant was available when the service was wired.
    assert container.get_dependency('configurable_service').config_value == 'test_config'

# ** test: constructor_delegates_to_load_container
def test_constructor_delegates_to_load_container(simple_dependency):
    '''
    The constructor loads both the given service and constants.

    :param simple_dependency: The simple service dependency.
    :type simple_dependency: ServiceDependency
    :return: None
    :rtype: None
    '''

    # Construct with a service and a constant.
    container = DIDynamicServiceContainer(
        services={'simple_service': simple_dependency},
        constants={'config_value': 'test_config'},
    )

    # Both the service and the constant resolve.
    assert isinstance(container.get_dependency('simple_service'), SimpleService)
    assert container.get_dependency('config_value') == 'test_config'

# ** test: has_dependency_present
def test_has_dependency_present(simple_dependency):
    '''
    has_dependency is True after add_service.

    :param simple_dependency: The simple service dependency.
    :type simple_dependency: ServiceDependency
    :return: None
    :rtype: None
    '''

    # Register the simple service.
    container = DIDynamicServiceContainer()
    container.add_service('simple_service', simple_dependency)

    # The registered id is present.
    assert container.has_dependency('simple_service') is True

# ** test: has_dependency_absent
def test_has_dependency_absent():
    '''
    has_dependency is False for an empty container.

    :return: None
    :rtype: None
    '''

    # An empty container has no missing id.
    assert DIDynamicServiceContainer().has_dependency('missing') is False

# ** test: has_dependency_app_container
def test_has_dependency_app_container(simple_dependency):
    '''
    An app container reports present and absent ids.

    :param simple_dependency: Unused sibling fixture kept for catalog shape.
    :type simple_dependency: ServiceDependency
    :return: None
    :rtype: None
    '''

    # Build an app container from one app service dependency.
    container = DIAppServiceContainer.from_dependencies(
        services=[
            AppServiceDependency(
                service_id='simple_service',
                module_path=MODULE_PATH,
                class_name='SimpleService',
            ),
        ],
    )

    # The registered id is present; an unknown id is not.
    assert container.has_dependency('simple_service') is True
    assert container.has_dependency('not_registered') is False

# ** test: get_dependency_missing_raises_service_error
def test_get_dependency_missing_raises_service_error():
    '''
    A missing provider raises ServiceError, not TiferetError.

    :return: None
    :rtype: None
    '''

    # Resolve an unregistered id.
    with pytest.raises(ServiceError) as exc_info:
        DIDynamicServiceContainer().get_dependency('missing_dependency')

    # The error carries the DI code and is not a TiferetError.
    error = exc_info.value
    assert error.error_code == DI_DEPENDENCY_NOT_REGISTERED_ID
    assert error.kwargs['dependency_id'] == 'missing_dependency'
    assert not isinstance(error, TiferetError)

# ** test: remove_dependency_removes
def test_remove_dependency_removes(simple_dependency):
    '''
    remove_dependency deletes a present provider.

    :param simple_dependency: The simple service dependency.
    :type simple_dependency: ServiceDependency
    :return: None
    :rtype: None
    '''

    # Add then remove the simple service.
    container = DIDynamicServiceContainer()
    container.add_service('simple_service', simple_dependency)
    container.remove_dependency('simple_service')

    # The provider is gone, and resolution fails.
    assert 'simple_service' not in container.container.providers
    with pytest.raises(Exception):
        container.get_dependency('simple_service')

# ** test: remove_dependency_idempotent
def test_remove_dependency_idempotent():
    '''
    remove_dependency does not raise for a missing id.

    :return: None
    :rtype: None
    '''

    # Removing a missing id is a no-op.
    container = DIDynamicServiceContainer()
    container.remove_dependency('missing_dependency')

    # The registry stays empty.
    assert len(container.container.providers) == 0

# ** test: cascading_dependency_injection
def test_cascading_dependency_injection(simple_dependency, dependent_dependency):
    '''
    A dependent service receives the registered simple service.

    :param simple_dependency: The simple service dependency.
    :type simple_dependency: ServiceDependency
    :param dependent_dependency: The dependent service dependency.
    :type dependent_dependency: ServiceDependency
    :return: None
    :rtype: None
    '''

    # Register the simple service before the dependent service.
    container = DIDynamicServiceContainer()
    container.add_service('simple_service', simple_dependency)
    container.add_service('dependent_service', dependent_dependency)
    resolved = container.get_dependency('dependent_service')

    # The dependent instance holds a SimpleService.
    assert isinstance(resolved, DependentService)
    assert isinstance(resolved.simple_service, SimpleService)

# ** test: app_container_singleton_identity
def test_app_container_singleton_identity():
    '''
    An app container returns the same SimpleService instance twice.

    :return: None
    :rtype: None
    '''

    # Build an app container with one service.
    container = DIAppServiceContainer.from_dependencies(
        services=[
            AppServiceDependency(
                service_id='simple_service',
                module_path=MODULE_PATH,
                class_name='SimpleService',
            ),
        ],
    )
    first = container.get_dependency('simple_service')
    second = container.get_dependency('simple_service')

    # Singleton scope shares one instance.
    assert isinstance(first, SimpleService)
    assert first is second

# ** test: app_container_event_receives_repo_singleton
def test_app_container_event_receives_repo_singleton():
    '''
    A dependent singleton receives the same simple-service instance.

    :return: None
    :rtype: None
    '''

    # Register the repo and the event that depends on it.
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
    repo = container.get_dependency('simple_service')
    event = container.get_dependency('dependent_service')

    # The event holds the same repo instance.
    assert event.simple_service is repo

# ** test: app_container_constants_before_services
def test_app_container_constants_before_services():
    '''
    App-container constants are available when services are wired.

    :return: None
    :rtype: None
    '''

    # Build the app container with a shared constant.
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

    # The service received the shared constant.
    assert container.get_dependency('configurable_service').config_value == 'shared'

# ** test: app_container_from_dependencies_core_catalog_resolves
def test_app_container_from_dependencies_core_catalog_resolves():
    '''
    The core default catalog resolves every service id.

    :return: None
    :rtype: None
    '''

    # Materialize the core catalog into app service dependencies.
    services = [
        AppServiceDependency.model_validate({**record, 'service_id': service_id})
        for service_id, record in a.app.CORE_DEFAULT_SERVICES.items()
    ]
    container = DIAppServiceContainer.from_dependencies(
        services=services,
        constants=dict(a.app.CORE_DEFAULT_CONSTANTS),
    )

    # Every catalogued service id resolves.
    for service_id in a.app.CORE_DEFAULT_SERVICES:
        assert container.get_dependency(service_id) is not None

# ** test: resolver_build_container_default
def test_resolver_build_container_default(resolver_registrations, make_di_service):
    '''
    build_container returns a dynamic container with default registrations.

    :param resolver_registrations: The catalog registrations.
    :type resolver_registrations: list
    :param make_di_service: The DIService factory.
    :type make_di_service: Callable
    :return: None
    :rtype: None
    '''

    # Build a container from the catalog with an empty flag list.
    resolver = DIDynamicServiceResolver(
        di_service=make_di_service(registrations=resolver_registrations),
    )
    container = resolver.build_container([])

    # The default bindings resolve.
    assert isinstance(container, DIDynamicServiceContainer)
    assert isinstance(container.get_dependency('simple_service'), SimpleService)
    assert container.get_dependency('configurable_service').config_value == 'default_value'

# ** test: resolver_flagged_type_override
def test_resolver_flagged_type_override(resolver_registrations, make_di_service):
    '''
    A flagged resolution uses the flagged type override.

    :param resolver_registrations: The catalog registrations.
    :type resolver_registrations: list
    :param make_di_service: The DIService factory.
    :type make_di_service: Callable
    :return: None
    :rtype: None
    '''

    # Resolve the flagged service under the alt flag.
    resolver = DIDynamicServiceResolver(
        di_service=make_di_service(registrations=resolver_registrations),
    )

    # The override type is DependentService.
    assert isinstance(
        resolver.get_dependency('flagged_service', 'alt'),
        DependentService,
    )

# ** test: resolver_skips_no_type_registration
def test_resolver_skips_no_type_registration(resolver_registrations, make_di_service):
    '''
    A registration with no type is omitted from the container.

    :param resolver_registrations: The catalog registrations.
    :type resolver_registrations: list
    :param make_di_service: The DIService factory.
    :type make_di_service: Callable
    :return: None
    :rtype: None
    '''

    # Build the default container.
    resolver = DIDynamicServiceResolver(
        di_service=make_di_service(registrations=resolver_registrations),
    )
    container = resolver.build_container([])

    # The typeless registration was skipped.
    assert 'no_type_service' not in container.container.providers

# ** test: resolver_parse_parameter_applied
def test_resolver_parse_parameter_applied(make_di_service):
    '''
    parse_parameter is applied to constants and dependency parameters.

    :param make_di_service: The DIService factory.
    :type make_di_service: Callable
    :return: None
    :rtype: None
    '''

    # Register one configurable service and one top-level constant.
    registration = ServiceRegistration(
        id='configurable_service',
        module_path=MODULE_PATH,
        class_name='ConfigurableService',
        parameters={'config_value': 'raw'},
    )
    resolver = DIDynamicServiceResolver(
        di_service=make_di_service(
            registrations=[registration],
            constants={'top': 'value'},
        ),
        parse_parameter=lambda value: f'parsed:{value}',
    )

    # Both the constant and the parameter were parsed once.
    assert resolver.get_dependency('top') == 'parsed:value'
    assert resolver.get_dependency('configurable_service').config_value == 'parsed:raw'

# ** test: resolver_caches_container_per_flag
def test_resolver_caches_container_per_flag(resolver_registrations, make_di_service):
    '''
    Repeated resolution of the same flags calls list_all once.

    :param resolver_registrations: The catalog registrations.
    :type resolver_registrations: list
    :param make_di_service: The DIService factory.
    :type make_di_service: Callable
    :return: None
    :rtype: None
    '''

    # Resolve the same service twice.
    di_service = make_di_service(registrations=resolver_registrations)
    resolver = DIDynamicServiceResolver(di_service=di_service)
    resolver.get_dependency('simple_service')
    resolver.get_dependency('simple_service')

    # The container was built once.
    assert di_service.list_all.call_count == 1

# ** test: resolver_cascading_get_dependency
def test_resolver_cascading_get_dependency(resolver_registrations, make_di_service):
    '''
    A flagged dependent service receives the default simple service.

    :param resolver_registrations: The catalog registrations.
    :type resolver_registrations: list
    :param make_di_service: The DIService factory.
    :type make_di_service: Callable
    :return: None
    :rtype: None
    '''

    # Resolve the flagged override, which depends on simple_service.
    resolver = DIDynamicServiceResolver(
        di_service=make_di_service(registrations=resolver_registrations),
    )
    resolved = resolver.get_dependency('flagged_service', 'alt')

    # The cascade wired a SimpleService.
    assert isinstance(resolved.simple_service, SimpleService)
