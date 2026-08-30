"""Tiferet Base Context Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.assets import TiferetError
from tiferet.contexts.core import BaseContext, ContextMeta, add_default_cache_items
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.feature import FeatureContext
from tiferet.contexts.error import ErrorContext
from tiferet.contexts.app import AppSessionContext
from tiferet.domain import Feature, Error, AppSession

# *** tests

# ** test: context_meta_registers_domain_types
def test_context_meta_registers_domain_types():
    '''
    Test that the metaclass registers contexts by their declared domain type.
    '''

    # Assert the known domain-to-context mappings are registered.
    assert ContextMeta.registry.get(Feature) is FeatureContext
    assert ContextMeta.registry.get(Error) is ErrorContext
    assert ContextMeta.registry.get(AppSession) is AppSessionContext

# ** test: base_context_not_registered
def test_base_context_not_registered():
    '''
    Test that BaseContext itself is not registered (domain_type is None).
    '''

    # Assert no registry entry maps to BaseContext.
    assert BaseContext not in ContextMeta.registry.values()

# ** test: for_domain_success
def test_for_domain_success():
    '''
    Test that for_domain resolves the registered context class for a domain type.
    '''

    # Assert the resolved class matches the registered context.
    assert BaseContext.for_domain(Feature) is FeatureContext
    assert BaseContext.for_domain(Error) is ErrorContext

# ** test: for_domain_not_found
def test_for_domain_not_found():
    '''
    Test that for_domain raises CONTEXT_NOT_FOUND for an unregistered domain type.
    '''

    # Define an unregistered domain-like type.
    class Unregistered:
        pass

    # Assert that resolving an unregistered type raises a structured error.
    with pytest.raises(TiferetError) as exc_info:
        BaseContext.for_domain(Unregistered)

    # Assert the error code and supplied kwarg.
    assert exc_info.value.error_code == 'CONTEXT_NOT_FOUND'
    assert exc_info.value.kwargs.get('domain_type') == 'Unregistered'

# ** test: from_domain_binds_domain
def test_from_domain_binds_domain():
    '''
    Test that from_domain resolves the context via the registry and binds the
    domain object when called on BaseContext.
    '''

    # Build a sample error domain object.
    error = Error(id='sample_error', name='Sample Error')

    # Construct the context from the domain object.
    context = BaseContext.from_domain(error)

    # Assert the resolved context type and bound domain.
    assert isinstance(context, ErrorContext)
    assert context.domain is error

# ** test: from_domain_explicit_subclass
def test_from_domain_explicit_subclass():
    '''
    Test that from_domain uses the concrete subclass when called on a subclass
    directly, forwarding constructor kwargs and binding the domain.
    '''

    # Build a sample feature domain object and a shared cache.
    feature = Feature(
        id='group.sample',
        group_id='group',
        feature_key='sample',
        name='Sample',
    )
    cache = CacheContext()

    # Construct the feature context explicitly via from_domain.
    context = FeatureContext.from_domain(feature, get_dependency=None, cache=cache)

    # Assert the context type, shared cache, and bound domain.
    assert isinstance(context, FeatureContext)
    assert context.cache is cache
    assert context.domain is feature

# ** test: add_default_cache_items_no_model_caches_raw_value
def test_add_default_cache_items_no_model_caches_raw_value():
    '''
    Test that add_default_cache_items with no model caches each raw value
    from items under the given prefix, unchanged.
    '''

    # Wrap a plain cache-builder with scalar constant items.
    items = {'cli_config': 'config.yml', 'di_config': 'config.yml'}
    wrapped = add_default_cache_items(items, ('app', 'constants'))(lambda: CacheContext())
    cache = wrapped()

    # Assert each raw value is cached unchanged under the prefix.
    for key, value in items.items():
        assert cache.get(key, 'app', 'constants') == value

# ** test: add_default_cache_items_model_without_id_field
def test_add_default_cache_items_model_without_id_field():
    '''
    Test that add_default_cache_items with a model but no id_field validates
    each raw dict directly into the model, with no key reinjection.
    '''

    # Wrap a plain cache-builder with a pre-existing 'id' baked into each dict.
    items = {
        'sample_error': {'id': 'sample_error', 'name': 'Sample Error'},
    }
    wrapped = add_default_cache_items(items, ('app', 'errors'), model=Error)(lambda: CacheContext())
    cache = wrapped()

    # Assert the item validated directly into the model.
    cached = cache.get('sample_error', 'app', 'errors')
    assert isinstance(cached, Error)
    assert cached.id == 'sample_error'

# ** test: add_default_cache_items_model_with_id_field_reinjects_key
def test_add_default_cache_items_model_with_id_field_reinjects_key():
    '''
    Test that add_default_cache_items reinjects the group-dict key as the
    given id_field before validating into the model.
    '''

    # Wrap a plain cache-builder with items lacking their own id.
    items = {
        'group.sample': {'group_id': 'group', 'feature_key': 'sample', 'name': 'Sample'},
    }
    wrapped = add_default_cache_items(
        items, ('app', 'features'), model=Feature, id_field='id',
    )(lambda: CacheContext())
    cache = wrapped()

    # Assert the group-dict key was reinjected as the model's id field.
    cached = cache.get('group.sample', 'app', 'features')
    assert isinstance(cached, Feature)
    assert cached.id == 'group.sample'

# ** test: add_default_cache_items_empty_dict_leaves_cache_clean
def test_add_default_cache_items_empty_dict_leaves_cache_clean():
    '''
    Test that add_default_cache_items with an empty items dict leaves the
    cache with no entries under the target prefix.
    '''

    # Wrap a plain cache-builder with no items.
    wrapped = add_default_cache_items({}, ('app', 'errors'), model=Error)(lambda: CacheContext())
    cache = wrapped()

    # Assert the target namespace has no entries.
    assert cache.get_by_prefix('app', 'errors') == {}

# ** test: add_default_cache_items_isolates_by_prefix
def test_add_default_cache_items_isolates_by_prefix():
    '''
    Test that two distinct prefixes seeded via add_default_cache_items do not
    collide with each other.
    '''

    # Build a cache seeded under two distinct prefixes via stacked decorators.
    def base_build():
        return CacheContext()

    build_errors = add_default_cache_items(
        {'sample_error': {'id': 'sample_error', 'name': 'Sample Error'}},
        ('app', 'errors'),
        model=Error,
    )(base_build)

    build_both = add_default_cache_items(
        {'cli_config': 'config.yml'},
        ('app', 'constants'),
    )(build_errors)

    cache = build_both()

    # Assert each prefix holds only its own entries.
    assert cache.get('sample_error', 'app', 'errors') is not None
    assert cache.get('cli_config', 'app', 'constants') == 'config.yml'
    assert cache.get('cli_config', 'app', 'errors') is None
    assert cache.get('sample_error', 'app', 'constants') is None
