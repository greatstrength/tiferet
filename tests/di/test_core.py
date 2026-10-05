"""Tiferet DI Core Tests"""

# *** imports

# ** app
from tiferet.di.core import (
    ServiceContainer,
    ServiceResolver,
    injectable_parameter_names,
    normalize_flags,
)

# *** classes

# ** class: simple_service
class SimpleService:
    '''
    A no-arg service used to exercise injectable parameter inspection.
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

# ** class: stub_container
class StubContainer(ServiceContainer):
    '''
    A ServiceContainer stub that records requested dependency ids.
    '''

    # * init
    def __init__(self, resolved: dict = None):
        '''
        Initialize the stub container.

        :param resolved: The mapping of dependency id to resolved value.
        :type resolved: dict
        '''

        # Store the resolved mapping and the requested ids.
        self.resolved = resolved or {}
        self.requested = []

    # * method: add_service
    def add_service(self, service_id, service):
        '''
        No-op service registration.

        :param service_id: The service identifier.
        :type service_id: str
        :param service: The service dependency.
        :type service: Any
        '''

        pass

    # * method: add_constant
    def add_constant(self, constant_id, value):
        '''
        No-op constant registration.

        :param constant_id: The constant identifier.
        :type constant_id: str
        :param value: The constant value.
        :type value: Any
        '''

        pass

    # * method: get_dependency
    def get_dependency(self, dependency_id):
        '''
        Record the requested id and return the stored value.

        :param dependency_id: The dependency identifier.
        :type dependency_id: str
        :return: The stored resolved value, or None.
        :rtype: Any
        '''

        # Record the requested identifier.
        self.requested.append(dependency_id)

        # Return the stored value.
        return self.resolved.get(dependency_id)

    # * method: has_dependency
    def has_dependency(self, dependency_id):
        '''
        Return whether the id is present in the resolved mapping.

        :param dependency_id: The dependency identifier.
        :type dependency_id: str
        :return: True when the id is present.
        :rtype: bool
        '''

        # Membership is the resolved mapping, not a provider registry.
        return dependency_id in self.resolved

    # * method: remove_dependency
    def remove_dependency(self, dependency_id):
        '''
        No-op dependency removal.

        :param dependency_id: The dependency identifier.
        :type dependency_id: str
        '''

        pass

    # * method: load_container
    def load_container(self, services: dict = None, constants: dict = None):
        '''
        No-op bulk load.

        :param services: The service mapping.
        :type services: dict
        :param constants: The constant mapping.
        :type constants: dict
        '''

        pass

# ** class: counting_resolver
class CountingResolver(ServiceResolver):
    '''
    A ServiceResolver that counts build_container calls and returns a stub.
    '''

    # * init
    def __init__(self, container: StubContainer):
        '''
        Initialize the counting resolver.

        :param container: The stub container returned by build_container.
        :type container: StubContainer
        '''

        # Initialize the resolver cache and the build counter.
        super().__init__()
        self._stub = container
        self.build_count = 0

    # * method: build_container
    def build_container(self, flags=None) -> StubContainer:
        '''
        Increment the build counter and return the stored stub.

        :param flags: The optional flag list.
        :type flags: list
        :return: The stored stub container.
        :rtype: StubContainer
        '''

        # Count the build and return the stored stub.
        self.build_count += 1
        return self._stub

# *** tests

# ** test: injectable_parameter_names_no_args
def test_injectable_parameter_names_no_args():
    '''
    injectable_parameter_names returns no names for a no-arg constructor.

    :return: None
    :rtype: None
    '''

    # A no-arg constructor has no injectable parameters.
    assert injectable_parameter_names(SimpleService) == []

# ** test: injectable_parameter_names_with_dependency
def test_injectable_parameter_names_with_dependency():
    '''
    injectable_parameter_names returns the sibling dependency name.

    :return: None
    :rtype: None
    '''

    # The dependent constructor exposes one injectable parameter.
    assert injectable_parameter_names(DependentService) == ['simple_service']

# ** test: injectable_parameter_names_scalar
def test_injectable_parameter_names_scalar():
    '''
    injectable_parameter_names returns the scalar parameter name.

    :return: None
    :rtype: None
    '''

    # The configurable constructor exposes one scalar parameter.
    assert injectable_parameter_names(ConfigurableService) == ['config_value']

# ** test: normalize_flags_mixed
def test_normalize_flags_mixed():
    '''
    normalize_flags flattens mixed strings, lists, and tuples.

    :return: None
    :rtype: None
    '''

    # Flatten one level of mixed flag groups.
    assert normalize_flags('a', ['b', 'c'], ('d', 'e')) == ['a', 'b', 'c', 'd', 'e']

# ** test: normalize_flags_empty
def test_normalize_flags_empty():
    '''
    normalize_flags returns an empty list when called with no arguments.

    :return: None
    :rtype: None
    '''

    # No arguments normalize to an empty list.
    assert normalize_flags() == []

# ** test: normalize_flags_coerces_non_string
def test_normalize_flags_coerces_non_string():
    '''
    normalize_flags coerces non-string scalars and members to strings.

    :return: None
    :rtype: None
    '''

    # Integers are coerced to strings, including nested members.
    assert normalize_flags(1, [2, 3], (4,)) == ['1', '2', '3', '4']

# ** test: service_resolver_container_cache_round_trip
def test_service_resolver_container_cache_round_trip():
    '''
    add_container caches a container retrievable by equivalent flag shapes.

    :return: None
    :rtype: None
    '''

    # Cache a second stub under a flag pair.
    resolver = CountingResolver(StubContainer())
    second = StubContainer()
    cached = resolver.add_container(second, 'a', 'b')

    # The same container is returned for equivalent flag shapes.
    assert cached is second
    assert resolver.get_container('a', 'b') is second
    assert resolver.get_container(['a', 'b']) is second
    assert resolver.get_container('c') is None

# ** test: service_resolver_get_dependency_builds_once
def test_service_resolver_get_dependency_builds_once():
    '''
    get_dependency builds the container once and reuses it.

    :return: None
    :rtype: None
    '''

    # Resolve the same id twice from a preloaded stub.
    stub = StubContainer(resolved={'svc': 'RESOLVED'})
    resolver = CountingResolver(stub)
    first = resolver.get_dependency('svc')
    second = resolver.get_dependency('svc')

    # Both resolutions return the stored value from one build.
    assert first == 'RESOLVED'
    assert second == 'RESOLVED'
    assert resolver.build_count == 1

# ** test: service_resolver_get_dependency_delegates_to_container
def test_service_resolver_get_dependency_delegates_to_container():
    '''
    get_dependency asks the container for the service id, not the flags.

    :return: None
    :rtype: None
    '''

    # Resolve with a flag so the container records only the service id.
    stub = StubContainer()
    resolver = CountingResolver(stub)
    resolver.get_dependency('svc', 'flag')

    # The container was asked for the service id alone.
    assert stub.requested == ['svc']
