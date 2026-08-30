"""Tiferet Context Core Tests"""

# *** imports

# ** core
from typing import Callable

# ** infra
import pytest

# ** app
from tiferet.contexts.core import BaseContext, ContextMeta, add_default_cache_items
from tiferet.contexts.cache import CacheContext
from tiferet.domain import DomainObject, Error
from tiferet.events.core import TiferetError

# *** fixtures

# ** fixture: base_cache_builder
@pytest.fixture
def base_cache_builder() -> Callable:
    '''
    Fixture providing a plain cache-builder callable with no pre-seeding.

    :return: A callable that returns a fresh CacheContext.
    :rtype: Callable
    '''

    # Define a minimal cache-builder mirroring the unwrapped build_cache.
    def build_cache() -> CacheContext:
        return CacheContext()

    # Return the cache-builder.
    return build_cache

# *** classes

# ** class: registered_domain
class RegisteredDomain(DomainObject):
    '''
    A domain object type registered to ConcreteContext for testing.
    '''

    pass

# ** class: unregistered_domain
class UnregisteredDomain(DomainObject):
    '''
    A domain object type with no registered context, for negative-path tests.
    '''

    pass

# ** class: concrete_context
class ConcreteContext(BaseContext):
    '''
    A concrete context declaring domain_type in its own namespace, so it
    registers itself for RegisteredDomain.
    '''

    # * attribute: domain_type
    domain_type = RegisteredDomain

# ** class: child_context
class ChildContext(ConcreteContext):
    '''
    A subclass that inherits domain_type from ConcreteContext without
    re-declaring it, so it must not register itself in the ContextMeta registry.
    '''

    pass

# *** tests

# ** test: test_context_meta_registers_domain_type
def test_context_meta_registers_domain_type():
    '''
    Test that a concrete subclass declaring domain_type appears in the registry.
    '''

    # Assert the registry maps RegisteredDomain to ConcreteContext.
    assert ContextMeta.registry[RegisteredDomain] is ConcreteContext

# ** test: test_context_meta_skips_inherited_domain_type
def test_context_meta_skips_inherited_domain_type():
    '''
    Test that a subclass inheriting (but not re-declaring) domain_type does
    not clobber the parent's registration.
    '''

    # Assert the registry entry still resolves to the parent class, not the child.
    assert ContextMeta.registry[RegisteredDomain] is ConcreteContext
    assert ContextMeta.registry[RegisteredDomain] is not ChildContext

# ** test: test_base_context_init
def test_base_context_init():
    '''
    Test that a bare BaseContext initializes with no domain or services.
    '''

    # Construct a BaseContext with no arguments.
    context = BaseContext()

    # Assert both slots are None by default.
    assert context.domain is None
    assert context.services is None

# ** test: test_for_domain_success
def test_for_domain_success():
    '''
    Test that for_domain returns the registered context class for a known type.
    '''

    # Resolve the context class for the registered domain type.
    resolved = BaseContext.for_domain(RegisteredDomain)

    # Assert the registered context class is returned.
    assert resolved is ConcreteContext

# ** test: test_for_domain_not_found
def test_for_domain_not_found():
    '''
    Test that for_domain raises a structured error for an unregistered type.
    '''

    # Attempt to resolve a context for an unregistered domain type.
    with pytest.raises(TiferetError) as exc_info:
        BaseContext.for_domain(UnregisteredDomain)

    # Assert the structured CONTEXT_NOT_FOUND error code is raised.
    assert exc_info.value.error_code == 'CONTEXT_NOT_FOUND'

    # Assert a descriptive message naming the unregistered domain type is included.
    assert 'No context registered for domain type: UnregisteredDomain.' in str(exc_info.value)

# ** test: test_from_domain_on_base
def test_from_domain_on_base():
    '''
    Test that from_domain on BaseContext resolves via the registry and binds the domain.
    '''

    # Construct a domain object and a sentinel services collaborator.
    domain_obj = RegisteredDomain()
    services = object()

    # Construct the context via the base class's from_domain factory.
    context = BaseContext.from_domain(domain_obj, services=services)

    # Assert the registered context class was constructed with domain and services bound.
    assert isinstance(context, ConcreteContext)
    assert context.domain is domain_obj
    assert context.services is services

# ** test: test_from_domain_on_subclass
def test_from_domain_on_subclass():
    '''
    Test that from_domain on a concrete subclass constructs that subclass
    directly, without consulting the registry.
    '''

    # Construct a domain object of a type with no registration to ConcreteContext.
    domain_obj = UnregisteredDomain()

    # Construct via the subclass's own from_domain, bypassing registry lookup.
    context = ConcreteContext.from_domain(domain_obj)

    # Assert the subclass was constructed directly and the domain object is bound.
    assert isinstance(context, ConcreteContext)
    assert context.domain is domain_obj

# ** test: test_add_default_cache_items_no_model_caches_raw_value
def test_add_default_cache_items_no_model_caches_raw_value(base_cache_builder: Callable):
    '''
    Test that add_default_cache_items with no model caches each raw value
    unchanged, keyed by its dict key.
    '''

    # Wrap the builder with a scalar constants catalog and invoke it.
    wrapped = add_default_cache_items({'FOO': 'bar'}, ('app', 'constants'))(base_cache_builder)
    cache = wrapped()

    # Assert the raw value is cached unchanged under the given prefix.
    assert cache.get('FOO', 'app', 'constants') == 'bar'

# ** test: test_add_default_cache_items_model_without_id_field
def test_add_default_cache_items_model_without_id_field(base_cache_builder: Callable):
    '''
    Test that add_default_cache_items with a model but no id_field validates
    each raw dict directly, with no key reinjection.
    '''

    # Wrap the builder with a catalog whose records already embed their own id.
    errors = {'ERR_ONE': {'id': 'ERR_ONE', 'name': 'Error One'}}
    wrapped = add_default_cache_items(errors, ('app', 'errors'), model=Error)(base_cache_builder)
    cache = wrapped()

    # Assert the record was validated into the model unchanged.
    cached = cache.get('ERR_ONE', 'app', 'errors')
    assert isinstance(cached, Error)
    assert cached.id == 'ERR_ONE'
    assert cached.name == 'Error One'

# ** test: test_add_default_cache_items_model_with_id_field_reinjects_key
def test_add_default_cache_items_model_with_id_field_reinjects_key(base_cache_builder: Callable):
    '''
    Test that add_default_cache_items reinjects the group-dict key under
    id_field before validating into the model.
    '''

    # Wrap the builder with a catalog whose records omit their own id.
    errors = {'ERR_TWO': {'name': 'Error Two'}}
    wrapped = add_default_cache_items(errors, ('app', 'errors'), model=Error, id_field='id')(base_cache_builder)
    cache = wrapped()

    # Assert the group-dict key was reinjected as the id before validation.
    cached = cache.get('ERR_TWO', 'app', 'errors')
    assert isinstance(cached, Error)
    assert cached.id == 'ERR_TWO'
    assert cached.name == 'Error Two'

# ** test: test_add_default_cache_items_empty_dict_leaves_cache_clean
def test_add_default_cache_items_empty_dict_leaves_cache_clean(base_cache_builder: Callable):
    '''
    Test that add_default_cache_items with an empty dict leaves the target
    namespace empty.
    '''

    # Wrap the builder with an empty catalog and invoke it.
    wrapped = add_default_cache_items({}, ('app', 'errors'), model=Error, id_field='id')(base_cache_builder)
    cache = wrapped()

    # Assert the namespace holds no entries.
    assert cache.get_by_prefix('app', 'errors') == {}

# ** test: test_add_default_cache_items_isolates_by_prefix
def test_add_default_cache_items_isolates_by_prefix(base_cache_builder: Callable):
    '''
    Test that two distinct prefixes seeded by separate calls do not collide.
    '''

    # Wrap the builder twice with distinct prefixes sharing an overlapping key.
    wrapped = add_default_cache_items({'FOO': 'app-value'}, ('app', 'constants'))(base_cache_builder)
    wrapped = add_default_cache_items({'FOO': 'admin-value'}, ('admin', 'constants'))(wrapped)
    cache = wrapped()

    # Assert each prefix's value is isolated from the other.
    assert cache.get('FOO', 'app', 'constants') == 'app-value'
    assert cache.get('FOO', 'admin', 'constants') == 'admin-value'
