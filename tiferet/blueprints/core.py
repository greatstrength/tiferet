"""Tiferet Core Blueprints"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from ..contexts.cache import CacheContext
from ..contexts.error import add_default_errors
from ..contexts.app import (
    add_default_app_services,
    add_default_app_constants,
    get_default_app_services,
    get_default_app_constants,
)
from ..domain import AppInterface
from ..events import ParseParameter
from ..di import DIAppServiceContainer
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

# ** blueprint: build_app_service_container
def build_app_service_container(
    cache: CacheContext,
    app_instance: AppInterface,
    service_container: type = DIAppServiceContainer,
) -> DIAppServiceContainer:
    '''
    Build the app-level service container for a resolved interface.

    Pulls the framework default services and constants seeded on the shared
    cache (by the app-context cache-key prefixes), applies the interface's own
    services and constants as overrides, and builds a singleton-scoped app
    service container.

    :param cache: The shared cache context seeded with default services/constants.
    :type cache: CacheContext
    :param app_instance: The resolved application interface definition.
    :type app_instance: AppInterface
    :param service_container: The container class to build; defaults to DIAppServiceContainer.
    :type service_container: type
    :return: The loaded app service container.
    :rtype: DIAppServiceContainer
    '''

    # Pull the framework default services and constants seeded on the cache.
    default_services = get_default_app_services(cache)
    default_constants = get_default_app_constants(cache)

    # Merge services: defaults first, interface-provided services override by id.
    services_by_id = {service.service_id: service for service in default_services}
    for service in (app_instance.services or []):
        services_by_id[service.service_id] = service

    # Merge constants: defaults beneath interface-provided constants.
    constants = {**default_constants, **(app_instance.constants or {})}

    # Build and return the app service container.
    return service_container.from_dependencies(
        services=list(services_by_id.values()),
        constants=constants,
    )

# ** blueprint: parse_parameter
def parse_parameter(parameter: str) -> Any:
    '''
    Parse a configuration parameter value, resolving environment references.

    Thin blueprint-layer wrapper over the ParseParameter static event so the DI
    resolver receives its parser from the blueprint layer rather than importing
    the event directly.

    :param parameter: The parameter value to parse.
    :type parameter: str
    :return: The parsed parameter value.
    :rtype: Any
    '''

    # Delegate to the ParseParameter static event.
    return ParseParameter.execute(parameter)
