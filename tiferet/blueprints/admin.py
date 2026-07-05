"""Tiferet Admin Blueprints"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from . import core
from ..contexts.cache import CacheContext
from ..contexts.error import add_default_errors
from .. import assets as a

# *** blueprints

# ** blueprint: build_cache
@add_default_errors(a.error.ADMIN_DEFAULT_ERRORS)
def build_cache(
    cache: Dict[str, Any] = None,
) -> CacheContext:
    '''
    Build an admin cache context pre-seeded with both core and admin default errors.

    Delegates to the core blueprint's ``build_cache`` to obtain a cache already
    populated with the framework's core error definitions, then layers the admin
    error definitions on top via the ``add_default_errors`` decorator.

    :param cache: An optional dict used to pre-seed the cache.
    :type cache: Dict[str, Any]
    :return: The initialized cache context seeded with core and admin errors.
    :rtype: CacheContext
    '''

    # Delegate to the core blueprint to obtain the core-seeded cache.
    return core.build_cache(cache=cache)
