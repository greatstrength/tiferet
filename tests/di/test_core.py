"""Tests for tiferet.di.core — ABCs and pure DI helper functions."""

# *** imports

# ** core
import pytest
from typing import List

# ** app
from tiferet.di.core import (
    ServiceContainer,
    ServiceResolver,
    injectable_parameter_names,
    normalize_flags,
)

# *** tests

# ** test: injectable_parameter_names_basic
def test_injectable_parameter_names_basic():
    '''
    injectable_parameter_names returns the correct parameter names for a
    simple __init__ with named parameters.
    '''

    # Define a simple service class with two named parameters.
    class MyService:
        def __init__(self, dep_a, dep_b):
            pass

    # Verify both parameter names are returned.
    assert injectable_parameter_names(MyService) == ['dep_a', 'dep_b']

# ** test: injectable_parameter_names_skips_self_and_variadics
def test_injectable_parameter_names_skips_self_and_variadics():
    '''
    injectable_parameter_names excludes self, *args, and **kwargs from
    the returned parameter list.
    '''

    # Define a class whose __init__ includes variadic parameters.
    class MyService:
        def __init__(self, dep_a, *args, dep_b=None, **kwargs):
            pass

    # Only named parameters (excluding self and variadics) should be returned.
    result = injectable_parameter_names(MyService)
    assert 'self' not in result
    assert 'args' not in result
    assert 'kwargs' not in result
    assert 'dep_a' in result
    assert 'dep_b' in result

# ** test: injectable_parameter_names_uninspectable
def test_injectable_parameter_names_uninspectable():
    '''
    injectable_parameter_names returns an empty list for types whose
    constructor cannot be inspected (e.g. built-in C-extension types).
    '''

    # int.__init__ is a C-extension; inspect.signature raises TypeError.
    result = injectable_parameter_names(int)

    # Result should be an empty list, not an exception.
    assert result == []

# ** test: normalize_flags_strings
def test_normalize_flags_strings():
    '''
    normalize_flags returns a flat list of strings unchanged when all
    flags are already strings.
    '''

    # Pass three string flags.
    result = normalize_flags('a', 'b', 'c')

    # Result should equal the original strings in order.
    assert result == ['a', 'b', 'c']

# ** test: normalize_flags_expands_list
def test_normalize_flags_expands_list():
    '''
    normalize_flags flattens a list argument into the result, expanding
    its members alongside any surrounding scalar flags.
    '''

    # Mix a list with a trailing scalar.
    result = normalize_flags(['a', 'b'], 'c')

    # The list should be expanded into the flat result.
    assert result == ['a', 'b', 'c']

# ** test: normalize_flags_coerces_to_str
def test_normalize_flags_coerces_to_str():
    '''
    normalize_flags coerces non-string scalars and list members to strings.
    '''

    # Mix integer scalars and a list of integers.
    result = normalize_flags(['a', 'b'], 'c', 42)

    # All elements should be strings.
    assert result == ['a', 'b', 'c', '42']

# ** test: service_container_is_abstract
def test_service_container_is_abstract():
    '''
    ServiceContainer cannot be instantiated directly; it raises TypeError
    because abstract methods are left unimplemented.
    '''

    # Attempt to instantiate the ABC directly.
    with pytest.raises(TypeError):
        ServiceContainer()

# ** test: service_resolver_is_abstract
def test_service_resolver_is_abstract():
    '''
    ServiceResolver cannot be instantiated directly; it raises TypeError
    because build_container is left unimplemented.
    '''

    # Attempt to instantiate the ABC directly.
    with pytest.raises(TypeError):
        ServiceResolver()

# ** test: service_resolver_add_and_get_container
def test_service_resolver_add_and_get_container():
    '''
    add_container stores a container under the normalized flag tuple and
    get_container retrieves it using the same flags.
    '''

    # Build a minimal concrete resolver with a stub build_container.
    class ConcreteResolver(ServiceResolver):
        def build_container(self, flags: List[str]):
            raise NotImplementedError('not needed for this test')

    # Build a minimal concrete container stub.
    class ConcreteContainer(ServiceContainer):
        def add_service(self, service_id, service): pass
        def add_constant(self, constant_id, value): pass
        def get_dependency(self, dependency_id): pass
        def has_dependency(self, dependency_id): return False
        def remove_dependency(self, dependency_id): pass
        def load_container(self, services=None, constants=None): pass

    resolver = ConcreteResolver()
    container = ConcreteContainer()

    # Store the container under a set of flags.
    resolver.add_container(container, 'flag_a', 'flag_b')

    # Retrieve the container using the same flags.
    retrieved = resolver.get_container('flag_a', 'flag_b')
    assert retrieved is container

    # A different flag combination should return None.
    assert resolver.get_container('flag_c') is None

# ** test: service_resolver_get_dependency_calls_build_on_miss
def test_service_resolver_get_dependency_calls_build_on_miss():
    '''
    get_dependency calls build_container when no cached container exists
    for the given flags, then caches and uses the result.
    '''

    # Track how many times build_container is called.
    build_calls = []

    class ConcreteContainer(ServiceContainer):
        def __init__(self, value):
            self._value = value
        def add_service(self, service_id, service): pass
        def add_constant(self, constant_id, value): pass
        def get_dependency(self, dependency_id): return self._value
        def has_dependency(self, dependency_id): return True
        def remove_dependency(self, dependency_id): pass
        def load_container(self, services=None, constants=None): pass

    class ConcreteResolver(ServiceResolver):
        def build_container(self, flags: List[str]) -> ServiceContainer:
            build_calls.append(flags)
            return ConcreteContainer('resolved_value')

    resolver = ConcreteResolver()

    # First call triggers build_container.
    result = resolver.get_dependency('my_service', 'flag_x')
    assert result == 'resolved_value'
    assert len(build_calls) == 1

    # Second call with same flags reuses the cached container.
    result = resolver.get_dependency('my_service', 'flag_x')
    assert result == 'resolved_value'
    assert len(build_calls) == 1
