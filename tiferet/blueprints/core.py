"""Tiferet Core Blueprints"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from ..contexts.cache import CacheContext
from ..contexts.error import add_default_errors
from ..contexts.app import add_default_app_services, add_default_app_constants
from .. import assets as a

# *** blueprints

# ** blueprint: build_cache
@add_default_app_constants(a.app.CORE_DEFAULT_CONSTANTS)
@add_default_app_services(a.app.CORE_DEFAULT_SERVICES)
@add_default_errors(a.error.CORE_DEFAULT_ERRORS)
def build_cache(
    cache: Dict[str, Any] = None,
) -> CacheContext:
    '''
    Build a standalone cache context for managing in-memory cache operations.

    Constructs a ``CacheContext`` independently of any interface or service
    resolver, then pre-seeds it with the framework's built-in catalogs via the
    stacked seeding decorators: error domain objects (``add_default_errors``),
    app service dependency domain objects (``add_default_app_services``), and
    scalar bootstrap constants (``add_default_app_constants``). Each catalog is
    namespaced under its own cache-key prefix (``error_``, ``app_service_``,
    ``app_constant_``). Pass an existing dict to seed the cache with additional
    pre-populated values; omit it to start with a fresh empty cache.

    :param cache: An optional dict used to pre-seed the cache.
    :type cache: Dict[str, Any]
    :return: The initialized cache context seeded with errors, services, and constants.
    :rtype: CacheContext
    '''

    # Construct and return the cache context.
    return CacheContext(cache=cache)
