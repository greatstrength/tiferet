"""Tiferet Core Blueprints"""

# *** imports

# ** core
from typing import Any, Callable, Dict

# ** app
from ..contexts.cache import CacheContext
from ..contexts.error import add_default_errors
from ..contexts.app import (
    AppInterface,
    AppServiceDependency,
    add_default_app_services,
    add_default_app_constants,
    get_default_app_services,
    get_default_app_constants,
)
from ..events import DomainEvent, ParseParameter
from ..events.app import GetAppInterface
from ..di import DIAppServiceContainer, DIDynamicServiceContainer
from ..di.core import ServiceResolver
from ..di.dependency_injector import DIDynamicServiceResolver
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

# ** blueprint: create_app_service
def create_app_service(
    module_path: str = a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
    parameters: Dict[str, Any] = None,
    service_container: type = DIDynamicServiceContainer,
) -> Any:
    '''
    Compose and return an app service instance via a single-use dynamic container.

    Describes the app service as a single id-keyed ``AppServiceDependency`` and
    resolves it through a function-scoped ``DIDynamicServiceContainer`` so its
    declared ``parameters`` are wired into the constructor by name (mirroring the
    legacy direct-import ``load_app_service``). When no parameters are supplied,
    the framework default (``a.app.DEFAULT_APP_SERVICE_PARAMETERS``) is used.

    :param module_path: The module path of the app service; defaults to the framework app repo.
    :type module_path: str
    :param class_name: The class name of the app service; defaults to AppConfigRepository.
    :type class_name: str
    :param parameters: The app service constructor parameters; defaults to the framework app service parameters.
    :type parameters: Dict[str, Any] | None
    :param service_container: The dynamic container class to compose with; defaults to DIDynamicServiceContainer.
    :type service_container: type
    :return: The composed app service instance.
    :rtype: Any
    '''

    # Fall back to the framework default parameters when none are supplied.
    parameters = parameters if parameters else a.app.DEFAULT_APP_SERVICE_PARAMETERS

    # Describe the app service as a single id-keyed dependency.
    service = AppServiceDependency(
        service_id='app_service',
        module_path=module_path,
        class_name=class_name,
        parameters=parameters,
    )

    # Build a single-use, function-scoped dynamic container to compose the app service.
    container = service_container(services={'app_service': service})

    # Resolve and return the composed app service instance.
    return container.get_dependency('app_service')

# ** blueprint: get_app_interface
def get_app_interface(
    interface_id: str,
    module_path: str = a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
    class_name: str = a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
    **parameters,
) -> AppInterface:
    '''
    Retrieve an app interface by id, composing the app service dependency first.

    Composes the ``app_service`` dependency via :func:`create_app_service`, then
    retrieves the requested interface through the ``GetAppInterface`` domain
    event. Any keyword arguments are forwarded as the app service constructor
    parameters (e.g. ``app_config='config.yml'``); when omitted,
    :func:`create_app_service` applies the framework default parameters.

    :param interface_id: The id of the app interface to retrieve.
    :type interface_id: str
    :param module_path: The module path of the app service; defaults to the framework app repo.
    :type module_path: str
    :param class_name: The class name of the app service; defaults to AppConfigRepository.
    :type class_name: str
    :param parameters: The app service constructor parameters.
    :type parameters: dict
    :return: The retrieved app interface.
    :rtype: AppInterface
    '''

    # Compose the app service via a single-use container.
    app_service = create_app_service(module_path, class_name, parameters)

    # Retrieve the interface via the GetAppInterface event.
    return DomainEvent.handle(
        GetAppInterface,
        dependencies=dict(app_service=app_service),
        interface_id=interface_id,
    )

# ** blueprint: build_app_service_container
def build_app_service_container(
    cache: CacheContext,
    app_instance: AppInterface = None,
    service_container: type = DIAppServiceContainer,
) -> DIAppServiceContainer:
    '''
    Build the app-level service container from cache defaults, then layer the
    interface's own constants and services as overrides.

    Builds a singleton-scoped container from the framework default services and
    constants seeded on the shared cache (by the app-context cache-key prefixes).
    When an ``app_instance`` is provided, its constants are layered first so that
    (re)registered services wire to them, then its services are layered to
    override defaults by id. When ``app_instance`` is ``None``, a defaults-only
    container is returned.

    :param cache: The shared cache context seeded with default services/constants.
    :type cache: CacheContext
    :param app_instance: The resolved application interface definition, or None for defaults only.
    :type app_instance: AppInterface | None
    :param service_container: The container class to build; defaults to DIAppServiceContainer.
    :type service_container: type
    :return: The loaded app service container.
    :rtype: DIAppServiceContainer
    '''

    # Build the container from the framework defaults seeded on the cache.
    container = service_container.from_dependencies(
        services=get_default_app_services(cache),
        constants=get_default_app_constants(cache),
    )

    # Return the defaults-only container when no interface is provided.
    if app_instance is None:
        return container

    # Layer interface constants first so (re)registered services wire to them.
    for name, value in (app_instance.constants or {}).items():
        container.add_constant(name, value)

    # Layer interface services, overriding defaults by id and wiring to the latest constants.
    for service in (app_instance.services or []):
        container.add_service(service.service_id, service)

    # Return the composed app service container.
    return container

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

# ** blueprint: build_service_resolver
def build_service_resolver(
    app_service_container: DIAppServiceContainer,
    parse_parameter: Callable = parse_parameter,
) -> ServiceResolver:
    '''
    Build the feature-level service resolver from a composed app service container.

    Resolves the DI service registration from the app service container, composes
    a concrete DIDynamicServiceResolver around it, then caches the same app
    service container on the resolver under the ``app`` flag so app-scoped
    services resolve through ``get_dependency(<id>, 'app')``.

    :param app_service_container: The composed app service container (defaults + interface overrides).
    :type app_service_container: DIAppServiceContainer
    :param parse_parameter: The parameter parser injected into the resolver; defaults to the blueprint parser.
    :type parse_parameter: Callable
    :return: The composed feature-level service resolver.
    :rtype: ServiceResolver
    '''

    # Resolve the DI service registration from the app service container.
    di_service = app_service_container.get_dependency('di_service')

    # Compose the concrete per-flag feature resolver, injecting the parameter parser.
    resolver = DIDynamicServiceResolver(
        di_service=di_service,
        parse_parameter=parse_parameter,
    )

    # Cache the app service container under the app flag so app-scoped
    # dependencies resolve through it.
    resolver.add_container(app_service_container, 'app')

    # Return the composed service resolver.
    return resolver
