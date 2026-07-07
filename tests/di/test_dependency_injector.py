"""Tiferet DI Dependency Injector Container Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.assets.exceptions import TiferetError
from tiferet.domain import ServiceDependency
from tiferet.di.dependency_injector import DIDynamicServiceContainer

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
