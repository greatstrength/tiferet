# *** imports

# ** infra
import pytest

# ** app
from tiferet.assets.exceptions import TiferetError
from tiferet.di.dynamic import DynamicServiceProvider
from tiferet.di.settings import ServiceProvider


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

# ** fixture: empty_provider
@pytest.fixture
def empty_provider() -> DynamicServiceProvider:
    '''
    Fixture to create an empty DynamicServiceProvider.

    :return: An empty provider instance.
    :rtype: DynamicServiceProvider
    '''

    # Return a provider with no initial services.
    return DynamicServiceProvider()


# ** fixture: populated_provider
@pytest.fixture
def populated_provider() -> DynamicServiceProvider:
    '''
    Fixture to create a DynamicServiceProvider pre-populated with a SimpleService.

    :return: A provider with SimpleService registered.
    :rtype: DynamicServiceProvider
    '''

    # Return a provider with SimpleService registered under 'simple_service'.
    return DynamicServiceProvider(services={'simple_service': SimpleService})


# *** tests

# ** test: init_empty
def test_init_empty(empty_provider: DynamicServiceProvider):
    '''
    Test that an empty provider initializes with no providers in the container.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DynamicServiceProvider
    '''

    # Assert that the container has no registered providers.
    assert len(empty_provider.container.providers) == 0


# ** test: init_with_services
def test_init_with_services(populated_provider: DynamicServiceProvider):
    '''
    Test that a provider initialized with services registers them correctly.

    :param populated_provider: The pre-populated provider fixture.
    :type populated_provider: DynamicServiceProvider
    '''

    # Assert that the service is present in the container providers.
    assert 'simple_service' in populated_provider.container.providers


# ** test: is_service_provider
def test_is_service_provider(empty_provider: DynamicServiceProvider):
    '''
    Test that DynamicServiceProvider is an instance of ServiceProvider.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DynamicServiceProvider
    '''

    # Assert that the provider satisfies the ServiceProvider contract.
    assert isinstance(empty_provider, ServiceProvider)


# ** test: add_service
def test_add_service(empty_provider: DynamicServiceProvider):
    '''
    Test that add_service registers a service and makes it resolvable.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DynamicServiceProvider
    '''

    # Add a single service.
    empty_provider.add_service('simple_service', SimpleService)

    # Assert it was added to the container.
    assert 'simple_service' in empty_provider.container.providers

    # Assert the resolved instance is of the expected type.
    service = empty_provider.get_service('simple_service')
    assert isinstance(service, SimpleService)


# ** test: add_service_new_instance_per_call
def test_add_service_new_instance_per_call(populated_provider: DynamicServiceProvider):
    '''
    Test that Factory providers resolve as new instances per call.

    :param populated_provider: The pre-populated provider fixture.
    :type populated_provider: DynamicServiceProvider
    '''

    # Resolve two instances of the same service.
    instance_a = populated_provider.get_service('simple_service')
    instance_b = populated_provider.get_service('simple_service')

    # Assert that both are SimpleService instances but are distinct objects.
    assert isinstance(instance_a, SimpleService)
    assert isinstance(instance_b, SimpleService)
    assert instance_a is not instance_b


# ** test: add_services
def test_add_services(empty_provider: DynamicServiceProvider):
    '''
    Test that add_services registers multiple services at once.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DynamicServiceProvider
    '''

    # Add multiple services.
    empty_provider.add_services({
        'simple_service': SimpleService,
        'dependent_service': DependentService,
    })

    # Assert both were added.
    assert 'simple_service' in empty_provider.container.providers
    assert 'dependent_service' in empty_provider.container.providers

    # Assert both resolve correctly.
    assert isinstance(empty_provider.get_service('simple_service'), SimpleService)
    assert isinstance(empty_provider.get_service('dependent_service'), DependentService)


# ** test: add_constants
def test_add_constants(empty_provider: DynamicServiceProvider):
    '''
    Test that add_constants registers scalar values returned as-is on resolution.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DynamicServiceProvider
    '''

    # Register a scalar constant.
    empty_provider.add_constants({'config_value': 'test_config'})

    # Assert the constant was stored in the container.
    assert 'config_value' in empty_provider.container.providers

    # Assert the constant resolves to the original value.
    assert empty_provider.get_service('config_value') == 'test_config'


# ** test: add_constants_injected_into_service
def test_add_constants_injected_into_service(empty_provider: DynamicServiceProvider):
    '''
    Test that constants registered via add_constants are injected into
    services that depend on them via constructor parameters.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DynamicServiceProvider
    '''

    # Register a constant first, then a service that depends on it.
    empty_provider.add_constants({'config_value': 'test_config'})
    empty_provider.add_service('configurable_service', ConfigurableService)

    # Resolve the service and assert the constant was injected correctly.
    service = empty_provider.get_service('configurable_service')
    assert isinstance(service, ConfigurableService)
    assert service.config_value == 'test_config'


# ** test: get_service_success
def test_get_service_success(populated_provider: DynamicServiceProvider):
    '''
    Test that get_service resolves a registered service to the correct type.

    :param populated_provider: The pre-populated provider fixture.
    :type populated_provider: DynamicServiceProvider
    '''

    # Resolve the service.
    service = populated_provider.get_service('simple_service')

    # Assert it is an instance of SimpleService.
    assert isinstance(service, SimpleService)


# ** test: get_service_not_found
def test_get_service_not_found(empty_provider: DynamicServiceProvider):
    '''
    Test that get_service raises TiferetError for an unregistered service ID.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DynamicServiceProvider
    '''

    # Attempt to resolve a service that was never registered.
    with pytest.raises(TiferetError) as exc_info:
        empty_provider.get_service('nonexistent_service')

    # Assert the correct error code was raised.
    assert exc_info.value.error_code == 'INVALID_DEPENDENCY_ERROR'

    # Assert the dependency name is in the error kwargs.
    assert exc_info.value.kwargs.get('dependency_name') == 'nonexistent_service'


# ** test: remove_service
def test_remove_service(populated_provider: DynamicServiceProvider):
    '''
    Test that remove_service deregisters a service from the provider.

    :param populated_provider: The pre-populated provider fixture.
    :type populated_provider: DynamicServiceProvider
    '''

    # Remove the registered service.
    populated_provider.remove_service('simple_service')

    # Assert it was removed from the container.
    assert 'simple_service' not in populated_provider.container.providers

    # Assert it is no longer resolvable.
    with pytest.raises(TiferetError):
        populated_provider.get_service('simple_service')


# ** test: remove_service_nonexistent
def test_remove_service_nonexistent(empty_provider: DynamicServiceProvider):
    '''
    Test that remove_service is a no-op for an unregistered service ID.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DynamicServiceProvider
    '''

    # Removing an ID that was never registered should not raise.
    empty_provider.remove_service('nonexistent_service')

    # Assert the container is still empty.
    assert len(empty_provider.container.providers) == 0


# ** test: add_services_mixed_types_and_scalars
def test_add_services_mixed_types_and_scalars(empty_provider: DynamicServiceProvider):
    '''
    Test that add_services routes class types to Factory providers and
    non-type values to Object providers when given a mixed dict.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DynamicServiceProvider
    '''

    # Register a mix of types and scalars in a single call.
    empty_provider.add_services({
        'config_value': 'test_config',
        'configurable_service': ConfigurableService,
    })

    # Assert the scalar resolves as-is.
    assert empty_provider.get_service('config_value') == 'test_config'

    # Assert the service resolves with the scalar injected.
    service = empty_provider.get_service('configurable_service')
    assert isinstance(service, ConfigurableService)
    assert service.config_value == 'test_config'


# ** test: cascading_dependency_injection
def test_cascading_dependency_injection(empty_provider: DynamicServiceProvider):
    '''
    Test that cascading DI works: a service with a constructor dependency
    on another registered service resolves both correctly.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DynamicServiceProvider
    '''

    # Register SimpleService first, then DependentService which depends on it.
    empty_provider.add_service('simple_service', SimpleService)
    empty_provider.add_service('dependent_service', DependentService)

    # Resolve the dependent service.
    service = empty_provider.get_service('dependent_service')

    # Assert the dependent service is the correct type.
    assert isinstance(service, DependentService)

    # Assert the injected dependency is the correct type.
    assert isinstance(service.simple_service, SimpleService)
