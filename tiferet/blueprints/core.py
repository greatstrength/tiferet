"""Tiferet Core Blueprints"""

# *** imports

# ** core
from typing import Any, Callable, Dict

# ** app
from ..contexts.app import get_default_app_constants, get_default_app_services
from ..contexts.cache import CacheContext
from ..di import DIAppServiceContainer, DIDynamicServiceResolver
from ..di.core import ServiceResolver
from ..events import ParseParameter

# *** blueprints

# ** blueprint: parse_parameter
def parse_parameter(parameter: Any) -> Any:
    '''
    Thin, injectable wrapper over the ParseParameter static event.

    Passed as the injected parameter-parser to DIDynamicServiceResolver so the
    DI layer never imports from the events layer directly.

    :param parameter: The parameter to parse.
    :type parameter: Any
    :return: The parsed parameter.
    :rtype: Any
    '''

    # Delegate to the static parse parameter event.
    return ParseParameter.execute(parameter)

# ** blueprint: build_app_service_container
def build_app_service_container(cache,
        app_instance: Any = None,
        service_container: type = DIAppServiceContainer) -> DIAppServiceContainer:
    '''
    Build the singleton app service container from cache-seeded defaults
    merged with the session's own service and constant overrides.

    Session overrides are merged with the cache defaults before building the
    container (not layered afterward), so session constants reach all
    default services the session does not redeclare.

    :param cache: The bootstrap cache seeded with framework defaults.
    :type cache: CacheContext
    :param app_instance: The loaded app session whose own services and
        constants override the cache defaults.
    :type app_instance: Any
    :param service_container: The concrete DI app service container class.
    :type service_container: type
    :return: The built app service container.
    :rtype: DIAppServiceContainer
    '''

    # Retrieve the cache-seeded default services and constants.
    default_services = get_default_app_services(cache)
    default_constants = get_default_app_constants(cache)

    # Retrieve the session's own service and constant overrides.
    session_services = list(getattr(app_instance, 'services', None) or [])
    session_constants = dict(getattr(app_instance, 'constants', None) or {})

    # Merge session services over defaults, keyed by service_id.
    merged_services_by_id = {service.service_id: service for service in default_services}
    merged_services_by_id.update({service.service_id: service for service in session_services})

    # Merge session constants over defaults before building the container, and
    # register the shared cache-snapshot closure so services can read shared
    # bootstrap state without a direct cache reference.
    merged_constants = {**default_constants, **session_constants}
    merged_constants['load_cache'] = load_cache(cache)

    # Build and return the app service container from the merged dependencies.
    return service_container.from_dependencies(
        services=list(merged_services_by_id.values()),
        constants=merged_constants,
    )

# ** blueprint: build_service_resolver
def build_service_resolver(app_service_container: DIAppServiceContainer,
        parse_parameter: Callable = parse_parameter) -> ServiceResolver:
    '''
    Compose the feature-level service resolver, registering the app service
    container under the ``'app'`` flag for the hub's collaborators.

    :param app_service_container: The built app service container.
    :type app_service_container: DIAppServiceContainer
    :param parse_parameter: The parameter-parsing callable injected into the resolver.
    :type parse_parameter: Callable
    :return: The composed service resolver.
    :rtype: ServiceResolver
    '''

    # Resolve the DI repository service from the app container.
    di_service = app_service_container.get_dependency('di_service')

    # Construct the dynamic service resolver with the injected parameter parser.
    resolver = DIDynamicServiceResolver(di_service=di_service, parse_parameter=parse_parameter)

    # Register the app service container under the 'app' flag.
    resolver.add_container(app_service_container, 'app')

    # Return the composed resolver.
    return resolver

# ** blueprint: load_cache
def load_cache(cache: CacheContext) -> Callable[[], Dict[str, Any]]:
    '''
    Build a zero-arg closure returning a root-namespace snapshot of the cache.

    Passed as a constant into the app service container so services can read
    shared bootstrap state without a direct cache reference.

    :param cache: The bootstrap cache to snapshot.
    :type cache: CacheContext
    :return: A zero-arg callable returning the root-namespace cache snapshot.
    :rtype: Callable[[], Dict[str, Any]]
    '''

    # Return the snapshot closure bound to the cache.
    def snapshot() -> Dict[str, Any]:
        return cache.get_by_prefix()

    # Return the closure.
    return snapshot
