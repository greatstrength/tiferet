"""Tiferet DI Dependency Injector Tests"""

# *** imports

# ** core
from typing import List, Tuple

# ** infra
import pytest

# ** app
from tiferet.di.dependency_injector import (
    DIAppServiceContainer,
    DIDynamicServiceContainer,
    DIDynamicServiceResolver,
)
from tiferet.domain import AppServiceDependency, ServiceDependency, ServiceRegistration

# *** classes

# ** class: simple_service
class SimpleService:
    '''
    A no-arg support service used to exercise Factory/Singleton wiring.
    '''

    def __init__(self):
        pass

# ** class: configurable_service
class ConfigurableService:
    '''
    A support service that depends on a constant sibling provider.
    '''

    def __init__(self, config_value: str):
        self.config_value = config_value

# ** class: stub_di_service
class StubDIService:
    '''
    A minimal DIService stub returning a fixed list of registrations and constants.
    '''

    def __init__(self,
            registrations: List[ServiceRegistration] = None,
            constants: dict = None,
        ):
        self.registrations = registrations if registrations else []
        self.constants = constants if constants else {}

    def list_all(self) -> Tuple[List[ServiceRegistration], dict]:
        return self.registrations, self.constants

# *** fixtures

# ** fixture: dynamic_container
@pytest.fixture
def dynamic_container() -> DIDynamicServiceContainer:
    '''
    An empty DIDynamicServiceContainer for tests that register dependencies directly.

    :return: An empty dynamic service container.
    :rtype: DIDynamicServiceContainer
    '''

    # Return a freshly constructed, empty dynamic container.
    return DIDynamicServiceContainer()

# ** fixture: app_container
@pytest.fixture
def app_container() -> DIAppServiceContainer:
    '''
    An empty DIAppServiceContainer for tests that register dependencies directly.

    :return: An empty app service container.
    :rtype: DIAppServiceContainer
    '''

    # Return a freshly constructed, empty app container.
    return DIAppServiceContainer()

# *** tests

# ** test: di_dynamic_container_init_empty
def test_di_dynamic_container_init_empty(dynamic_container):
    '''
    An empty DIDynamicServiceContainer has no registered providers.

    :param dynamic_container: The empty dynamic container fixture.
    :type dynamic_container: DIDynamicServiceContainer
    '''

    # Neither a service nor a constant id should be registered.
    assert dynamic_container.has_dependency('anything') is False

# ** test: di_dynamic_container_add_constant
def test_di_dynamic_container_add_constant(dynamic_container):
    '''
    add_constant registers a value resolvable via get_dependency.

    :param dynamic_container: The empty dynamic container fixture.
    :type dynamic_container: DIDynamicServiceContainer
    '''

    # Register a constant directly on the empty container.
    dynamic_container.add_constant('k', 'v')

    # The constant should resolve to its registered value.
    assert dynamic_container.get_dependency('k') == 'v'

# ** test: di_dynamic_container_add_service_factory
def test_di_dynamic_container_add_service_factory(dynamic_container):
    '''
    add_service registers a Factory provider; each get_dependency call
    returns a new instance.

    :param dynamic_container: The empty dynamic container fixture.
    :type dynamic_container: DIDynamicServiceContainer
    '''

    # Register the support service as a Factory-backed dependency.
    container = dynamic_container
    container.add_service(
        'svc',
        ServiceDependency(
            module_path=__name__,
            class_name='SimpleService',
        ),
    )

    # Two resolutions should yield distinct instances.
    first = container.get_dependency('svc')
    second = container.get_dependency('svc')
    assert isinstance(first, SimpleService)
    assert first is not second

# ** test: di_dynamic_container_load_container_constants_first
def test_di_dynamic_container_load_container_constants_first():
    '''
    load_container registers constants before services, so a service that
    depends on a constant resolves correctly regardless of dict order.
    '''

    # Load a service and its dependent constant in a single call.
    container = DIDynamicServiceContainer(
        services={
            'svc': ServiceDependency(
                module_path=__name__,
                class_name='ConfigurableService',
                parameters={'config_value': 'constant_value'},
            ),
        },
        constants={},
    )

    # The service should resolve with the constant wired in.
    resolved = container.get_dependency('svc')
    assert resolved.config_value == 'constant_value'

# ** test: di_dynamic_container_has_dependency_true
def test_di_dynamic_container_has_dependency_true(dynamic_container):
    '''
    has_dependency returns True for a registered service.

    :param dynamic_container: The empty dynamic container fixture.
    :type dynamic_container: DIDynamicServiceContainer
    '''

    # Register a constant and verify its presence.
    dynamic_container.add_constant('k', 'v')

    assert dynamic_container.has_dependency('k') is True

# ** test: di_dynamic_container_has_dependency_false
def test_di_dynamic_container_has_dependency_false(dynamic_container):
    '''
    has_dependency returns False for an unregistered id.

    :param dynamic_container: The empty dynamic container fixture.
    :type dynamic_container: DIDynamicServiceContainer
    '''

    # An empty container has no registrations.
    assert dynamic_container.has_dependency('missing') is False

# ** test: di_dynamic_container_remove_dependency
def test_di_dynamic_container_remove_dependency(dynamic_container):
    '''
    remove_dependency removes a previously registered dependency.

    :param dynamic_container: The empty dynamic container fixture.
    :type dynamic_container: DIDynamicServiceContainer
    '''

    # Register then remove a constant.
    dynamic_container.add_constant('k', 'v')
    dynamic_container.remove_dependency('k')

    assert dynamic_container.has_dependency('k') is False

# ** test: di_dynamic_container_remove_dependency_idempotent
def test_di_dynamic_container_remove_dependency_idempotent(dynamic_container):
    '''
    remove_dependency does not raise when the id is not registered.

    :param dynamic_container: The empty dynamic container fixture.
    :type dynamic_container: DIDynamicServiceContainer
    '''

    # Removing a nonexistent id should be a no-op.
    dynamic_container.remove_dependency('missing')

# ** test: di_app_service_container_add_service_singleton
def test_di_app_service_container_add_service_singleton(app_container):
    '''
    DIAppServiceContainer resolves the same shared instance on each
    get_dependency call for Singleton-registered services.

    :param app_container: The empty app container fixture.
    :type app_container: DIAppServiceContainer
    '''

    # Register the support service as a Singleton-backed dependency.
    container = app_container
    container.add_service(
        'svc',
        ServiceDependency(
            module_path=__name__,
            class_name='SimpleService',
        ),
    )

    # Two resolutions should yield the same shared instance.
    first = container.get_dependency('svc')
    second = container.get_dependency('svc')
    assert first is second

# ** test: di_app_service_container_from_dependencies
def test_di_app_service_container_from_dependencies():
    '''
    from_dependencies builds a loaded container keyed by service_id.
    '''

    # Build the container from a list of app service dependencies.
    container = DIAppServiceContainer.from_dependencies(
        services=[
            AppServiceDependency(
                service_id='svc',
                module_path=__name__,
                class_name='SimpleService',
            ),
        ],
    )

    # The container should resolve the service by its service_id.
    assert isinstance(container.get_dependency('svc'), SimpleService)

# ** test: di_dynamic_resolver_build_container
def test_di_dynamic_resolver_build_container():
    '''
    build_container returns a DIDynamicServiceContainer and excludes
    registrations that resolve to None for the given flags.
    '''

    # Set up one resolvable registration and one that resolves to None.
    di_service = StubDIService(
        registrations=[
            ServiceRegistration(
                id='resolvable',
                module_path=__name__,
                class_name='SimpleService',
            ),
            ServiceRegistration(id='unresolvable'),
        ],
    )
    resolver = DIDynamicServiceResolver(di_service=di_service)

    # Build the container directly for an empty flag list.
    container = resolver.build_container([])

    assert isinstance(container, DIDynamicServiceContainer)
    assert container.has_dependency('resolvable') is True
    assert container.has_dependency('unresolvable') is False

# ** test: di_dynamic_resolver_get_dependency_caches_container
def test_di_dynamic_resolver_get_dependency_caches_container():
    '''
    get_dependency builds and caches the container on the first call and
    reuses it on subsequent calls with the same flags.
    '''

    # Track how many times build_container is invoked.
    build_calls = []

    di_service = StubDIService(
        registrations=[
            ServiceRegistration(
                id='svc',
                module_path=__name__,
                class_name='SimpleService',
            ),
        ],
    )
    resolver = DIDynamicServiceResolver(di_service=di_service)

    original_build_container = resolver.build_container
    def tracking_build_container(flags):
        build_calls.append(flags)
        return original_build_container(flags)
    resolver.build_container = tracking_build_container

    # First call builds the container.
    resolver.get_dependency('svc')
    assert len(build_calls) == 1

    # Second call with the same flags reuses the cached container.
    resolver.get_dependency('svc')
    assert len(build_calls) == 1
