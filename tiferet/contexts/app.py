"""Tiferet App Contexts"""

# *** imports

# ** core
import time
from typing import Any, Callable, Dict, List, Tuple

# ** app
from ..assets import (
    TiferetError,
    TiferetAPIError,
)
from ..domain import AppSession, AppInterface, AppServiceDependency, Feature, CliCommand, Error
from ..events import DomainEvent
from .settings import BaseContext
from .cache import CacheContext
from .feature import FeatureContext, AsyncFeatureContext  # -- obsolete: AsyncFeatureContext import; remove at v2.0.0 stable
from .error import ErrorContext, ERROR_CACHE_PREFIX
from .logging import LoggingContext
from .request import RequestContext

# *** constants

# ** constant: app_service_cache_prefix
APP_SERVICE_CACHE_PREFIX: Tuple[str, ...] = ('app', 'services')

# ** constant: app_constant_cache_prefix
APP_CONSTANT_CACHE_PREFIX: Tuple[str, ...] = ('app', 'constants')

# *** functions

# ** function: add_default_app_services
def add_default_app_services(services: Dict[str, Any]) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with default app service
    dependency domain objects.

    Wraps a cache-builder callable so that, after the cache is constructed,
    each entry in ``services`` is reconstituted into an ``AppServiceDependency``
    domain object and stored in the cache under the ``APP_SERVICE_CACHE_PREFIX``
    namespace keyed by service id.

    :param services: A mapping of service ids to raw service dependency dicts.
    :type services: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Return the decorator that wraps the cache-builder.
    def decorator(build_fn: Callable) -> Callable:

        # Build the cache, then populate it with the default service domain objects.
        def wrapper(*args, **kwargs) -> CacheContext:

            # Delegate to the wrapped cache-builder.
            cache = build_fn(*args, **kwargs)

            # Reconstitute each raw service dict into an AppServiceDependency
            # domain object and cache it under the services namespace.
            for service_id, service_data in services.items():
                cache.set(
                    service_id,
                    AppServiceDependency.model_validate(service_data),
                    *APP_SERVICE_CACHE_PREFIX,
                )

            # Return the populated cache context.
            return cache

        return wrapper

    return decorator

# ** function: get_default_app_services
def get_default_app_services(cache: CacheContext) -> List[AppServiceDependency]:
    '''
    Return the default app service dependencies seeded on the cache.

    :param cache: The cache context to read.
    :type cache: CacheContext
    :return: The default app service dependency domain objects.
    :rtype: List[AppServiceDependency]
    '''

    # Pull all entries from the services namespace and return their values.
    return list(cache.get_by_prefix(*APP_SERVICE_CACHE_PREFIX).values())

# ** function: add_default_app_constants
def add_default_app_constants(constants: Dict[str, Any]) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with default bootstrap
    constant values.

    Wraps a cache-builder callable so that, after the cache is constructed,
    each scalar entry in ``constants`` is stored in the cache under the
    ``APP_CONSTANT_CACHE_PREFIX`` namespace keyed by constant name.

    :param constants: A mapping of constant names to scalar values.
    :type constants: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Return the decorator that wraps the cache-builder.
    def decorator(build_fn: Callable) -> Callable:

        # Build the cache, then populate it with the default constant values.
        def wrapper(*args, **kwargs) -> CacheContext:

            # Delegate to the wrapped cache-builder.
            cache = build_fn(*args, **kwargs)

            # Store each scalar constant under the constants namespace.
            for name, value in constants.items():
                cache.set(name, value, *APP_CONSTANT_CACHE_PREFIX)

            # Return the populated cache context.
            return cache

        return wrapper

    return decorator

# ** function: get_default_app_constants
def get_default_app_constants(cache: CacheContext) -> Dict[str, Any]:
    '''
    Return the default bootstrap constants seeded on the cache.

    :param cache: The cache context to read.
    :type cache: CacheContext
    :return: The default constants keyed by name.
    :rtype: Dict[str, Any]
    '''

    # Pull all entries from the constants namespace and return them directly.
    return dict(cache.get_by_prefix(*APP_CONSTANT_CACHE_PREFIX))

# ** function: build_feature_index
# -- obsolete: superseded by the assets-backed default catalog pattern (see add_default_app_services / add_default_app_constants); remove when feature defaults are fully migrated to the cache-seeding decorator approach
# ++ todo: migrate default feature bootstrapping to the add_default_* decorator factory pattern used by app services and constants
def build_feature_index(features: Dict[str, Dict[str, Any]] = None) -> Dict[str, Feature]:
    '''
    Materialize an id-keyed feature mapping into a typed Feature index.

    :param features: Id-keyed mapping of feature records (each value is the
        record minus its id).
    :type features: Dict[str, Dict[str, Any]] | None
    :return: A mapping of feature id to typed Feature objects.
    :rtype: Dict[str, Feature]
    '''

    # Feed each record into the Feature domain object, keyed by its id.
    return {
        feature_id: Feature.model_validate({**(record or {}), 'id': feature_id})
        for feature_id, record in (features or {}).items()
    }

# ** function: build_command_list
# -- obsolete: superseded by the assets-backed default catalog pattern; removal to be handled as part of the CLI context/blueprint refactor
# ++ todo: migrate default command bootstrapping to the CLI context/blueprint layer
def build_command_list(commands: Dict[str, Dict[str, Any]] = None) -> List[CliCommand]:
    '''
    Materialize an id-keyed command mapping into a typed CliCommand list.

    :param commands: Id-keyed mapping of command records (each value is the
        record minus its id).
    :type commands: Dict[str, Dict[str, Any]] | None
    :return: A list of typed CliCommand objects.
    :rtype: List[CliCommand]
    '''

    # Feed each record into the CliCommand domain object, keyed by its id.
    return [
        CliCommand.model_validate({**(record or {}), 'id': command_id})
        for command_id, record in (commands or {}).items()
    ]

# ** function: resolve_default_interface
# -- obsolete: superseded by the assets-backed default catalog pattern (see add_default_app_services / add_default_app_constants); remove when interface defaults are fully migrated to the cache-seeding decorator approach
# ++ todo: migrate default interface resolution to the add_default_* decorator factory pattern used by app services and constants
def resolve_default_interface(
    interface_id: str,
    default_interfaces: List[Dict[str, Any]],
) -> AppSession | None:
    '''
    Construct an app session from the bootstrap default session definitions,
    or return ``None`` when no default matches the requested id.

    Materializes a default session definition into a typed ``AppSession``,
    mirroring ``build_feature_index`` / ``build_command_list`` for the bootstrap
    session fallback consumed by the blueprint during interface resolution.

    :param interface_id: The interface ID to look up.
    :type interface_id: str
    :param default_interfaces: Session definition dicts, each with an ``id`` key.
    :type default_interfaces: List[Dict[str, Any]]
    :return: The matching app session, or None.
    :rtype: AppSession | None
    '''

    # Find the first default whose id matches the requested interface_id.
    matching = next(
        (definition for definition in (default_interfaces or []) if definition.get('id') == interface_id),
        None,
    )

    # Construct and return the session, or None when no default matches.
    return AppSession(**matching) if matching else None

# *** contexts

# ** context: app_session_context
class AppSessionContext(BaseContext):
    '''
    The application session context is a minimal hub that builds operational
    sub-contexts on demand from a loaded ``AppSession`` domain object and
    orchestrates feature execution, error handling, and logging.
    '''

    # * attribute: domain_type
    domain_type = AppSession

    # * attribute: get_feature_evt (obsolete)
    # -- obsolete: superseded by the injected _get_feature callable; remove at v2.0.0 stable
    get_feature_evt: DomainEvent

    # * attribute: _get_feature
    _get_feature: Callable

    # * attribute: get_error_evt (obsolete)
    # -- obsolete: superseded by the injected _get_error callable; remove at v2.0.0 stable
    get_error_evt: DomainEvent

    # * attribute: _get_error
    _get_error: Callable

    # * attribute: logging_list_all_evt
    logging_list_all_evt: DomainEvent

    # * attribute: get_dependency
    get_dependency: Callable

    # * attribute: cache
    cache: CacheContext

    # * init
    def __init__(self,
            get_feature_evt: DomainEvent,
            get_error_evt: DomainEvent,
            logging_list_all_evt: DomainEvent,
            get_dependency: Callable,
            cache: CacheContext = None,
            get_feature: Callable = None,
            get_error: Callable = None,
            default_features: Dict[str, Dict[str, Any]] = None,
            default_commands: Dict[str, Dict[str, Any]] = None,
        ):
        '''
        Initialize the application session hub.

        The bound ``AppSession`` domain object (set via ``from_domain``)
        supplies the session id and logger id on demand, so no standalone
        ``interface_id`` is stored.

        :param get_feature_evt: The event used to retrieve features. Obsolete: superseded by
            the injected ``get_feature`` callable.
        :type get_feature_evt: DomainEvent
        :param get_error_evt: The event used to retrieve errors. Obsolete: superseded by
            the injected ``get_error`` callable.
        :type get_error_evt: DomainEvent
        :param logging_list_all_evt: The event used to list logging configurations.
        :type logging_list_all_evt: DomainEvent
        :param get_dependency: The injected service-resolution handler used to resolve feature step events and middleware.
        :type get_dependency: Callable
        :param cache: The shared cache context for all sub-contexts.
        :type cache: CacheContext
        :param get_feature: An optional feature-retrieval callable produced by the ``get_feature``
            blueprint in ``blueprints/core.py``. When provided, the ``_get_feature`` handler is
            used for all feature lookups; when absent, the legacy ``get_feature_evt`` path applies.
        :type get_feature: Callable
        :param get_error: An optional error-retrieval callable produced by the ``get_error``
            blueprint in ``blueprints/core.py``. When provided, the ``_get_error`` handler is
            used for all error lookups; when absent, the legacy ``get_error_evt`` path applies.
        :type get_error: Callable
        :param default_features: Optional id-keyed feature records for bootstrap fallback.
        :type default_features: Dict[str, Dict[str, Any]]
        :param default_commands: Optional id-keyed CLI command records for bootstrap fallback.
        :type default_commands: Dict[str, Dict[str, Any]]
        '''

        # Initialize the base context.
        super().__init__()

        # Wire in the shared cache context, defaulting to a fresh one.
        self.cache = cache if cache is not None else CacheContext()

        # Store the retrieval/configuration events and the service-resolution handler.
        self.get_feature_evt = get_feature_evt
        self.get_error_evt = get_error_evt
        self.logging_list_all_evt = logging_list_all_evt
        self.get_dependency = get_dependency

        # Store the injected feature- and error-retrieval handlers (new path).
        self._get_feature = get_feature
        self._get_error = get_error

        # Materialize the id-keyed bootstrap defaults into typed domain objects.
        self.default_feature_index = build_feature_index(default_features)
        self.default_commands_list = build_command_list(default_commands)

        # Initialize the lazily-built logging sub-context cache. The feature
        # and error contexts are built on demand.
        self._logging = None

    # * method: load_logging_context
    def load_logging_context(self) -> LoggingContext:
        '''
        Build (once) and return the logging context.

        :return: The shared logging context.
        :rtype: LoggingContext
        '''

        # Build the logging context on first access, reading the logger id from the domain.
        if self._logging is None:
            self._logging = LoggingContext(
                logging_list_all_evt=self.logging_list_all_evt,
                logger_id=self.domain.logger_id,
            )

        # Return the shared logging context.
        return self._logging

    # * method: load_feature_domain
    def load_feature_domain(self, feature_id: str) -> Feature:
        '''
        Load a feature domain object by id.

        Delegates to the injected ``_get_feature`` handler when available
        (new path). Falls back to the legacy cache-then-event path when
        the handler has not been injected (backward compatibility).

        :param feature_id: The feature identifier.
        :type feature_id: str
        :return: The loaded feature domain object.
        :rtype: Feature
        '''

        # Delegate to the injected handler when available (new path).
        if self._get_feature is not None:
            return self._get_feature(feature_id)

        # Legacy fallback: try the shared cache first.
        feature = self.cache.get(feature_id)

        # Retrieve via the get-feature event, falling back to the bootstrap
        # default index when the repository does not contain the feature.
        if not feature:
            try:
                feature = self.get_feature_evt.execute(id=feature_id)
            except TiferetError:
                feature = self.default_feature_index.get(feature_id)
                if feature is None:
                    raise
            self.cache.set(feature_id, feature)

        # Return the loaded feature.
        return feature

    # * method: get_error
    def get_error(self, error_code: str) -> Error:
        '''
        Load an error domain object by its code.

        Delegates to the injected ``_get_error`` handler when available
        (new path). Falls back to the legacy cache-then-event path when
        the handler has not been injected (backward compatibility).

        :param error_code: The error code to resolve.
        :type error_code: str
        :return: The loaded error domain object.
        :rtype: Error
        '''

        # Delegate to the injected handler when available (new path).
        if self._get_error is not None:
            return self._get_error(error_code)

        # Legacy fallback: try the shared cache first (pre-seeded with the default errors).
        error = self.cache.get(error_code, *ERROR_CACHE_PREFIX)

        # Retrieve via the get-error event when not cached, then cache it.
        if not error:
            error = self.get_error_evt.execute(error_code, include_defaults=False)
            self.cache.set(error_code, error, *ERROR_CACHE_PREFIX)

        # Return the loaded error.
        return error

    # * method: parse_request
    def parse_request(self, headers: Dict[str, str] = {}, data: Dict[str, Any] = {}, feature_id: str = None, **kwargs) -> RequestContext:
        '''
        Parse the incoming request.

        :param headers: The request headers.
        :type headers: dict
        :param data: The request data.
        :type data: dict
        :param feature_id: The feature identifier if provided.
        :type feature_id: str
        :kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The parsed request as a request context.
        :rtype: RequestContext
        '''

        # Add the interface id (from the bound domain) to the request headers.
        headers.update(dict(
            interface_id=self.domain.id,
        ))

        # Create the request context object.
        request = RequestContext(
            headers=headers,
            data=data,
            feature_id=feature_id,
        )

        # Return the request model object.
        return request

    # * method: _run_coroutine (static, obsolete)
    # -- obsolete: superseded by contexts.feature.run_coroutine; remove at v2.0.0 stable
    @staticmethod
    def _run_coroutine(coro: Any) -> Any:
        '''
        Drive a coroutine to completion from synchronous code.

        NOTE: Obsolete — superseded by :func:`tiferet.contexts.feature.run_coroutine`.
        This method is retained for one increment for backward compatibility.

        :param coro: The coroutine to execute.
        :type coro: Any
        :return: The coroutine result.
        :rtype: Any
        '''

        # Delegate to the module-level run_coroutine in contexts.feature.
        from .feature import run_coroutine
        return run_coroutine(coro)

    # * method: execute_feature
    def execute_feature(self, feature_id: str, request: RequestContext, **kwargs):
        '''
        Execute the feature request.

        Resolves the registered ``FeatureContext`` via the ``BaseContext``
        registry and delegates execution. Sync/async dispatch is handled
        internally by ``FeatureContext.execute_feature`` based on
        ``feature.is_async`` and ``step.is_async``.

        :param feature_id: The feature identifier.
        :type feature_id: str
        :param request: The request context object.
        :type request: RequestContext
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Add the feature id to the request headers.
        request.headers.update(dict(
            feature_id=feature_id
        ))

        # Load the feature domain object for execution.
        feature = self.load_feature_domain(feature_id)

        # Resolve the feature context via the registry and execute.
        feature_context_cls = BaseContext.for_domain(Feature)
        feature_context = feature_context_cls(
            get_dependency=self.get_dependency,
            cache=self.cache,
        )
        feature_context.execute_feature(feature, request, **kwargs)

    # * method: handle_error
    def handle_error(self, error: Exception, **kwargs) -> Any:
        '''
        Handle the error by formatting it via ErrorContext and raising TiferetAPIError.

        :param error: The error to handle.
        :type error: Exception
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The error response.
        :rtype: Any
        '''

        # If the error is not a TiferetError, wrap it in one.
        if not isinstance(error, TiferetError):
            error = TiferetError(
                'APP_ERROR',
                f'An error occurred in the app: {str(error)}',
                error=str(error)
            )

        # Load the error domain object for the error code.
        error_domain = self.get_error(error.error_code)

        # Build the error context on demand (resolved via the registry) and
        # format the response for the loaded error.
        error_context_cls = BaseContext.for_domain(Error)
        formatted_error = error_context_cls().format_response(error_domain, error)

        # Raise the API exception with the formatted payload.
        raise TiferetAPIError(**formatted_error)

    # * method: run
    def run(self, 
            feature_id: str, 
            headers: Dict[str, str] = {}, 
            data: Dict[str, Any] = {},
            **kwargs) -> Any:
        '''
        Run the application interface by executing the feature.

        :param feature_id: The feature identifier.
        :type feature_id: str
        :param headers: The request headers.
        :type headers: dict
        :param data: The request data.
        :type data: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Start timing immediately.
        start_time = time.perf_counter()

        # Create the logger for the app interface context.
        logger = self.load_logging_context().build_logger()

        # Parse request.
        logger.debug(f'Parsing request for feature: {feature_id}')
        request = self.parse_request(headers, data, feature_id)

        # Execute feature context and return session.
        try:
            logger.debug(f'Executing feature: {feature_id} with request: {request.data}')
            self.execute_feature(
                feature_id=feature_id, 
                request=request, 
                logger=logger,
                **kwargs)

        # Handle error and return response if triggered.
        except TiferetError as e:
            logger.error(f'Error executing feature {feature_id}: {str(e)}')
            return self.handle_error(e, **kwargs)

        # Calculate execution duration in milliseconds.
        duration_ms = round((time.perf_counter() - start_time) * 1000)
        duration_str = f" ({duration_ms}ms)"

        # Log successful execution with timing.
        logger.debug(f'Feature {feature_id} executed successfully, handling response.')
        logger.info(f'Executed Feature - {feature_id}{duration_str}')

        # Handle the response via the request context.
        return request.handle_response()


# ** context: app_interface_context (obsolete)
# -- obsolete: superseded by AppSessionContext; remove at v2.0.0 stable
AppInterfaceContext = AppSessionContext
