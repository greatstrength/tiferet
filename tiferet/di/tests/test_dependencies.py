# *** imports

# ** infra
import pytest

# ** app
from ...assets.exceptions import TiferetError
from ..dependencies import DependenciesServiceProvider
from ..settings import ServiceProvider


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
def empty_provider() -> DependenciesServiceProvider:
    '''
    Fixture to create an empty DependenciesServiceProvider.

    :return: An empty provider instance.
    :rtype: DependenciesServiceProvider
    '''

    # Return a provider with no initial services.
    return DependenciesServiceProvider()


# ** fixture: populated_provider
@pytest.fixture
def populated_provider() -> DependenciesServiceProvider:
    '''
    Fixture to create a DependenciesServiceProvider pre-populated with a SimpleService.

    :return: A provider with SimpleService registered.
    :rtype: DependenciesServiceProvider
    '''

    # Return a provider with SimpleService registered under 'simple_service'.
    return DependenciesServiceProvider(services={'simple_service': SimpleService})


# *** tests

# ** test: init_empty
def test_init_empty(empty_provider: DependenciesServiceProvider):
    '''
    Test that an empty provider initializes with no services and a built injector.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DependenciesServiceProvider
    '''

    # Assert that the services dictionary is empty.
    assert empty_provider.services == {}

    # Injector is None until services are registered (empty scope is not allowed
    # by the dependencies library).
    assert empty_provider.injector is None


# ** test: init_with_services
def test_init_with_services(populated_provider: DependenciesServiceProvider):
    '''
    Test that a provider initialized with services registers them correctly.

    :param populated_provider: The pre-populated provider fixture.
    :type populated_provider: DependenciesServiceProvider
    '''

    # Assert that the service is present in the services dictionary.
    assert 'simple_service' in populated_provider.services
    assert populated_provider.services['simple_service'] is SimpleService


# ** test: is_service_provider
def test_is_service_provider(empty_provider: DependenciesServiceProvider):
    '''
    Test that DependenciesServiceProvider is an instance of ServiceProvider.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DependenciesServiceProvider
    '''

    # Assert that the provider satisfies the ServiceProvider contract.
    assert isinstance(empty_provider, ServiceProvider)


# ** test: new_static_factory
def test_new_static_factory():
    '''
    Test the new() static factory creates a correctly named and populated provider.
    '''

    # Create a provider via the static factory.
    provider = DependenciesServiceProvider.new('MyProvider', {'simple_service': SimpleService})

    # Assert the provider is the correct type.
    assert isinstance(provider, DependenciesServiceProvider)

    # Assert the services were registered.
    assert 'simple_service' in provider.services

    # Assert the injector name is set correctly.
    assert provider._name == 'MyProvider'


# ** test: add_service
def test_add_service(empty_provider: DependenciesServiceProvider):
    '''
    Test that add_service registers a service and makes it resolvable.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DependenciesServiceProvider
    '''

    # Add a single service.
    empty_provider.add_service('simple_service', SimpleService)

    # Assert it was added to the services dictionary.
    assert 'simple_service' in empty_provider.services

    # Assert the resolved instance is of the expected type.
    service = empty_provider.get_service('simple_service')
    assert isinstance(service, SimpleService)


# ** test: add_services
def test_add_services(empty_provider: DependenciesServiceProvider):
    '''
    Test that add_services registers multiple services at once.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DependenciesServiceProvider
    '''

    # Add multiple services.
    empty_provider.add_services({
        'simple_service': SimpleService,
        'dependent_service': DependentService,
    })

    # Assert both were added.
    assert 'simple_service' in empty_provider.services
    assert 'dependent_service' in empty_provider.services

    # Assert both resolve correctly.
    assert isinstance(empty_provider.get_service('simple_service'), SimpleService)
    assert isinstance(empty_provider.get_service('dependent_service'), DependentService)


# ** test: add_constants
def test_add_constants(empty_provider: DependenciesServiceProvider):
    '''
    Test that add_constants registers scalar values that are injected into
    dependent services as constructor parameters.

    Note: The dependencies library treats scalars as injection parameters only;
    they cannot be resolved directly via get_service.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DependenciesServiceProvider
    '''

    # Register a scalar constant and a service that depends on it.
    empty_provider.add_services({'configurable_service': ConfigurableService})
    empty_provider.add_constants({'config_value': 'test_config'})

    # Assert both were stored in the services dictionary.
    assert 'config_value' in empty_provider.services
    assert 'configurable_service' in empty_provider.services

    # Resolve the service and assert the constant was injected correctly.
    service = empty_provider.get_service('configurable_service')
    assert isinstance(service, ConfigurableService)
    assert service.config_value == 'test_config'


# ** test: get_service_success
def test_get_service_success(populated_provider: DependenciesServiceProvider):
    '''
    Test that get_service resolves a registered service to the correct type.

    :param populated_provider: The pre-populated provider fixture.
    :type populated_provider: DependenciesServiceProvider
    '''

    # Resolve the service.
    service = populated_provider.get_service('simple_service')

    # Assert it is an instance of SimpleService.
    assert isinstance(service, SimpleService)


# ** test: get_service_not_found
def test_get_service_not_found(empty_provider: DependenciesServiceProvider):
    '''
    Test that get_service raises TiferetError for an unregistered service ID.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DependenciesServiceProvider
    '''

    # Attempt to resolve a service that was never registered.
    with pytest.raises(TiferetError) as exc_info:
        empty_provider.get_service('nonexistent_service')

    # Assert the correct error code was raised.
    assert exc_info.value.error_code == 'INVALID_DEPENDENCY_ERROR'

    # Assert the dependency name is in the error kwargs.
    assert exc_info.value.kwargs.get('dependency_name') == 'nonexistent_service'


# ** test: remove_service
def test_remove_service(populated_provider: DependenciesServiceProvider):
    '''
    Test that remove_service deregisters a service from the provider.

    :param populated_provider: The pre-populated provider fixture.
    :type populated_provider: DependenciesServiceProvider
    '''

    # Remove the registered service.
    populated_provider.remove_service('simple_service')

    # Assert it was removed from the services dictionary.
    assert 'simple_service' not in populated_provider.services

    # Assert it is no longer resolvable.
    with pytest.raises(TiferetError):
        populated_provider.get_service('simple_service')


# ** test: remove_service_nonexistent
def test_remove_service_nonexistent(empty_provider: DependenciesServiceProvider):
    '''
    Test that remove_service is a no-op for an unregistered service ID.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DependenciesServiceProvider
    '''

    # Removing an ID that was never registered should not raise.
    empty_provider.remove_service('nonexistent_service')

    # Assert the services dictionary is still empty.
    assert empty_provider.services == {}


# ** test: build_injector_rebuilds_on_mutation
def test_build_injector_rebuilds_on_mutation(empty_provider: DependenciesServiceProvider):
    '''
    Test that each mutation rebuilds the injector to reflect the current services.

    :param empty_provider: The empty provider fixture.
    :type empty_provider: DependenciesServiceProvider
    '''

    # With no services the injector starts as None.
    assert empty_provider.injector is None

    # Add a service, which should trigger a rebuild.
    empty_provider.add_service('simple_service', SimpleService)

    # Assert the injector was created (no longer None).
    assert empty_provider.injector is not None

    # Assert the new injector resolves the added service.
    assert isinstance(empty_provider.get_service('simple_service'), SimpleService)
