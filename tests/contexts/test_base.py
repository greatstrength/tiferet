"""Tiferet Base Context Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.assets import TiferetError
from tiferet.contexts.settings import BaseContext, ContextMeta
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.feature import FeatureContext, AsyncFeatureContext
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

# ** test: async_feature_context_not_registered
def test_async_feature_context_not_registered():
    '''
    Test that AsyncFeatureContext inherits domain_type without clobbering the
    Feature registry entry, leaving FeatureContext as the resolved context.
    '''

    # Assert Feature still resolves to the synchronous FeatureContext.
    assert ContextMeta.registry.get(Feature) is FeatureContext
    assert BaseContext.for_domain(Feature) is FeatureContext

    # Assert the async subclass is not registered for any domain type.
    assert AsyncFeatureContext not in ContextMeta.registry.values()

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
