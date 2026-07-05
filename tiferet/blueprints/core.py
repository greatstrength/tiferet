"""Tiferet Core Blueprints"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from ..contexts.cache import CacheContext
from ..contexts.error import add_default_errors
from .. import assets as a

# *** blueprints

# ** blueprint: build_cache
@add_default_errors(a.error.CORE_DEFAULT_ERRORS)
def build_cache(
    cache: Dict[str, Any] = None,
) -> CacheContext:
    '''
    Build a standalone cache context for managing in-memory cache operations.

    Constructs a ``CacheContext`` independently of any interface or service
    resolver, then pre-seeds it with the framework's built-in error domain
    objects via the ``add_default_errors`` decorator. Pass an existing dict
    to seed the cache with additional pre-populated values; omit it to start
    with a fresh empty cache.

    :param cache: An optional dict used to pre-seed the cache.
    :type cache: Dict[str, Any]
    :return: The initialized and error-seeded cache context.
    :rtype: CacheContext
    '''

    # Construct and return the cache context.
    return CacheContext(cache=cache)
