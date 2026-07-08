"""Tiferet DI Core Tests"""

# *** imports

# ** app
from tiferet.di.core import (
    injectable_parameter_names,
    normalize_flags,
    ServiceContainer,
    ServiceResolver,
)

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

# ** class: stub_container
class StubContainer(ServiceContainer):
    '''A minimal concrete ServiceContainer that records get_dependency calls.'''

    # * init
    def __init__(self, resolved: dict = None):
        '''
        Initialize the stub container with a fixed resolution map.

        :param resolved: The id-to-value map returned by get_dependency.
        :type resolved: dict
        '''

        # Store the fixed resolution map and a call log.
        self.resolved = resolved if resolved is not None else {}
        self.requested = []

    # * method: add_service
    def add_service(self, service_id: str, service):
        '''No-op service registration for the stub.'''

        pass

    # * method: add_constant
    def add_constant(self, constant_id: str, value):
        '''No-op constant registration for the stub.'''

        pass

    # * method: get_dependency
    def get_dependency(self, dependency_id: str):
        '''Record the request and return the fixed value for the id.'''

        # Log the requested id and return its fixed value.
        self.requested.append(dependency_id)
        return self.resolved.get(dependency_id)

    # * method: remove_dependency
    def remove_dependency(self, dependency_id: str):
        '''No-op removal for the stub.'''

        pass

    # * method: load_container
    def load_container(self, services: dict = None, constants: dict = None):
        '''No-op bulk load for the stub.'''

        pass

# ** class: counting_resolver
class CountingResolver(ServiceResolver):
    '''A concrete ServiceResolver that returns a fixed stub container and counts builds.'''

    # * init
    def __init__(self, container: StubContainer):
        '''
        Initialize the resolver with a fixed stub container.

        :param container: The stub container returned by build_container.
        :type container: StubContainer
        '''

        # Initialize the base per-flag cache and store the fixed container.
        super().__init__()
        self._stub = container
        self.build_count = 0

    # * method: build_container
    def build_container(self, flags=None) -> StubContainer:
        '''Return the fixed stub container, counting each build.'''

        # Count the build and return the fixed stub container.
        self.build_count += 1
        return self._stub

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

# ** test: service_resolver_container_cache_round_trip
def test_service_resolver_container_cache_round_trip():
    '''
    Test that add_container/get_container round-trip by the normalized flag key.
    '''

    # Cache a container under a two-flag key.
    resolver = CountingResolver(StubContainer())
    container = StubContainer()
    returned = resolver.add_container(container, 'a', 'b')

    # Assert the cached container is returned and retrievable across flag forms.
    assert returned is container
    assert resolver.get_container('a', 'b') is container
    assert resolver.get_container(['a', 'b']) is container

    # Assert an unmatched flag set resolves to None.
    assert resolver.get_container('c') is None

# ** test: service_resolver_get_dependency_builds_once
def test_service_resolver_get_dependency_builds_once():
    '''
    Test that get_dependency builds a container once, then serves it from cache.
    '''

    # Resolve the same id twice under the same flags.
    stub = StubContainer(resolved={'svc': 'RESOLVED'})
    resolver = CountingResolver(stub)
    first = resolver.get_dependency('svc')
    second = resolver.get_dependency('svc')

    # Assert both resolve to the stub's value and the container was built once.
    assert first == 'RESOLVED'
    assert second == 'RESOLVED'
    assert resolver.build_count == 1

# ** test: service_resolver_get_dependency_delegates_to_container
def test_service_resolver_get_dependency_delegates_to_container():
    '''
    Test that get_dependency delegates resolution to the built container.
    '''

    # Resolve a dependency and assert the container received the id.
    stub = StubContainer(resolved={'svc': 'RESOLVED'})
    resolver = CountingResolver(stub)
    resolver.get_dependency('svc', 'flag')
    assert stub.requested == ['svc']
