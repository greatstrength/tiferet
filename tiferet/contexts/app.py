"""Tiferet App Contexts"""

# *** imports

# ** core
import logging
import time
from typing import Any, Callable, Dict, Tuple

# ** app
from ..assets import (
    TiferetError,
    TiferetAPIError,
)
from ..assets.error import APP_ERROR_ID
from ..domain import AppSession, AppServiceDependency
from .core import BaseContext
from .cache import CacheContext
from .request import RequestContext

# *** constants

# ** constant: app_service_cache_prefix
APP_SERVICE_CACHE_PREFIX: Tuple[str, ...] = ('app', 'services')

# ** constant: app_constant_cache_prefix
APP_CONSTANT_CACHE_PREFIX: Tuple[str, ...] = ('app', 'constants')

# ** constant: admin_service_cache_prefix
ADMIN_SERVICE_CACHE_PREFIX: Tuple[str, ...] = ('admin', 'services')

# ** constant: admin_constant_cache_prefix
ADMIN_CONSTANT_CACHE_PREFIX: Tuple[str, ...] = ('admin', 'constants')

# ** constant: app_session_cache_prefix
APP_SESSION_CACHE_PREFIX: Tuple[str, ...] = ('app', 'sessions')

# *** functions

# ** function: add_default_app_services
def add_default_app_services(services: Dict[str, Any]) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with default app service
    dependency domain objects.

    Wraps a cache-builder callable so that, after the cache is constructed,
    each entry in ``services`` is reconstituted into an ``AppServiceDependency``
    domain object (with its ``service_id`` re-injected) and stored in the
    cache under the ``APP_SERVICE_CACHE_PREFIX`` namespace keyed by service id.

    :param services: A mapping of service ids to raw service dependency dicts
        (each value is the dependency without its ``service_id``).
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
            # domain object (re-injecting service_id) and cache it under the
            # services namespace.
            for service_id, service_data in services.items():
                cache.set(
                    service_id,
                    AppServiceDependency.model_validate({**service_data, 'service_id': service_id}),
                    *APP_SERVICE_CACHE_PREFIX,
                )

            # Return the populated cache context.
            return cache

        return wrapper

    return decorator

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

# ** function: add_default_admin_services
def add_default_admin_services(services: Dict[str, Any]) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with default admin service
    dependency domain objects.

    Mirrors ``add_default_app_services`` under the ``ADMIN_SERVICE_CACHE_PREFIX``
    namespace, giving the admin blueprints their own catalog distinct from the
    core app-service catalog.

    :param services: A mapping of service ids to raw service dependency dicts
        (each value is the dependency without its ``service_id``).
    :type services: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Return the decorator that wraps the cache-builder.
    def decorator(build_fn: Callable) -> Callable:

        # Build the cache, then populate it with the default admin service domain objects.
        def wrapper(*args, **kwargs) -> CacheContext:

            # Delegate to the wrapped cache-builder.
            cache = build_fn(*args, **kwargs)

            # Reconstitute each raw service dict into an AppServiceDependency
            # domain object (re-injecting service_id) and cache it under the
            # admin services namespace.
            for service_id, service_data in services.items():
                cache.set(
                    service_id,
                    AppServiceDependency.model_validate({**service_data, 'service_id': service_id}),
                    *ADMIN_SERVICE_CACHE_PREFIX,
                )

            # Return the populated cache context.
            return cache

        return wrapper

    return decorator

# ** function: add_default_admin_constants
def add_default_admin_constants(constants: Dict[str, Any]) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with default admin
    bootstrap constant values.

    Mirrors ``add_default_app_constants`` under the ``ADMIN_CONSTANT_CACHE_PREFIX``
    namespace.

    :param constants: A mapping of constant names to scalar values.
    :type constants: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Return the decorator that wraps the cache-builder.
    def decorator(build_fn: Callable) -> Callable:

        # Build the cache, then populate it with the default admin constant values.
        def wrapper(*args, **kwargs) -> CacheContext:

            # Delegate to the wrapped cache-builder.
            cache = build_fn(*args, **kwargs)

            # Store each scalar constant under the admin constants namespace.
            for name, value in constants.items():
                cache.set(name, value, *ADMIN_CONSTANT_CACHE_PREFIX)

            # Return the populated cache context.
            return cache

        return wrapper

    return decorator

# ** function: add_default_app_sessions
def add_default_app_sessions(sessions: Dict[str, Any]) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with default app session
    domain objects.

    Wraps a cache-builder callable so that, after the cache is constructed,
    each entry in ``sessions`` is reconstituted into an ``AppSession`` domain
    object (with its id re-injected) and stored in the cache under the
    ``APP_SESSION_CACHE_PREFIX`` namespace keyed by session id.

    :param sessions: A mapping of session ids to raw session definition dicts
        (each value is the definition without its id).
    :type sessions: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Return the decorator that wraps the cache-builder.
    def decorator(build_fn: Callable) -> Callable:

        # Build the cache, then populate it with the default session domain objects.
        def wrapper(*args, **kwargs) -> CacheContext:

            # Delegate to the wrapped cache-builder.
            cache = build_fn(*args, **kwargs)

            # Reconstitute each raw session dict into an AppSession domain
            # object (re-injecting the id) and cache it under the sessions
            # namespace keyed by session id.
            for session_id, session_data in sessions.items():
                cache.set(
                    session_id,
                    AppSession.model_validate({**session_data, 'id': session_id}),
                    *APP_SESSION_CACHE_PREFIX,
                )

            # Return the populated cache context.
            return cache

        return wrapper

    return decorator

# ** function: raise_unwired_handler_error
def raise_unwired_handler_error(handler_name: str, session_id: str, **kwargs) -> None:
    '''
    Raise the structured API error for an unwired template-method handler.

    An absent handler is a composition bug rather than a condition to degrade
    around, so the hub raises instead of reimplementing the handler's work. The
    error is raised as a ``TiferetAPIError`` — already the formatted,
    consumer-facing representation — so it passes through ``handle_error``
    verbatim. The function always raises; it never returns, echoing the
    ``TiferetError.raise_error`` convention.

    :param handler_name: The name of the handler slot the blueprint failed to supply.
    :type handler_name: str
    :param session_id: The id of the app session the handler was expected on.
    :type session_id: str
    :param kwargs: Additional context kwargs carried on the error.
    :type kwargs: dict
    '''

    # Compose the message naming the missing handler and the session it belongs to.
    message = (
        f'No {handler_name} is wired on the app session context for session '
        f'{session_id}; the blueprint must supply {handler_name}.'
    )

    # Raise the formatted API error naming the missing handler.
    raise TiferetAPIError(
        error_code=APP_ERROR_ID,
        name='App Error',
        message=message,
        **kwargs,
    )

# *** contexts

# ** context: app_session_context
# >> see: @guides/contexts.md#appsessioncontext
class AppSessionContext(BaseContext):
    '''
    The application session hub binds a loaded ``AppSession`` domain object
    and delegates logger construction, feature execution, error handling,
    request construction, and response building to five injected
    template-method handlers.

    All five handlers are required: an unwired handler is a composition bug,
    so each template method raises ``APP_ERROR`` naming the missing handler
    rather than degrading to a fallback implementation. Because that error is
    already a ``TiferetAPIError``, ``handle_error`` passes it through verbatim.
    '''

    # * attribute: domain_type
    domain_type = AppSession

    # * attribute: get_dependency
    get_dependency: Callable

    # * attribute: cache
    cache: CacheContext

    # * attribute: build_logger (private)
    _build_logger: Callable

    # * attribute: execute_feature (private)
    _execute_feature: Callable

    # * attribute: create_request (private)
    _create_request: Callable

    # * attribute: raise_error (private)
    _raise_error: Callable

    # * attribute: build_response (private)
    _build_response: Callable

    # * init
    def __init__(self,
            get_dependency: Callable,
            cache: CacheContext = None,
            build_logger_handler: Callable = None,
            execute_feature_handler: Callable = None,
            create_request_handler: Callable = None,
            raise_error_handler: Callable = None,
            response_handler: Callable = None,
        ):
        '''
        Initialize the application session hub.

        The bound ``AppSession`` domain object (set via ``from_domain``)
        supplies the session id and logger id on demand, so no standalone
        ``interface_id`` is stored.

        :param get_dependency: The injected service-resolution handler used to
            resolve feature step events and middleware.
        :type get_dependency: Callable
        :param cache: The shared cache context for all sub-contexts.
        :type cache: CacheContext
        :param build_logger_handler: The logger-construction callable produced by
            the ``build_logger_handler`` blueprint.
        :type build_logger_handler: Callable
        :param execute_feature_handler: The feature-execution callable produced by
            the ``execute_feature_handler`` blueprint.
        :type execute_feature_handler: Callable
        :param create_request_handler: The request-creation callable produced by
            the ``create_session_request`` blueprint.
        :type create_request_handler: Callable
        :param raise_error_handler: The error-raising callable produced by the
            ``raise_error_handler`` blueprint.
        :type raise_error_handler: Callable
        :param response_handler: The response-extraction callable produced by the
            ``response_handler`` blueprint.
        :type response_handler: Callable
        '''

        # Initialize the base context.
        super().__init__()

        # Wire in the shared cache context, defaulting to a fresh one.
        self.cache = cache if cache is not None else CacheContext()

        # Store the service-resolution handler.
        self.get_dependency = get_dependency

        # Store the five injected handler callables.
        self._build_logger = build_logger_handler
        self._execute_feature = execute_feature_handler
        self._create_request = create_request_handler
        self._raise_error = raise_error_handler
        self._build_response = response_handler

    # * method: build_logger
    def build_logger(self) -> logging.Logger:
        '''
        Build the logger for this session run.

        Template method override point. Delegates to the injected
        ``_build_logger`` callable, which the blueprint layer wires from
        ``build_logger_handler``. An unwired handler raises ``APP_ERROR``
        naming the missing slot. A ``TiferetError`` raised by the handler is
        formatted into its ``TiferetAPIError`` representation via
        ``handle_error`` rather than left to propagate, so the pre-try region
        of ``run`` raises only ``TiferetAPIError``.

        :return: The constructed logger for this session.
        :rtype: logging.Logger
        '''

        # Fail loudly when the blueprint-supplied logger factory is absent.
        if self._build_logger is None:
            raise_unwired_handler_error(
                'build_logger_handler',
                self.domain.id,
            )

        # Delegate logger construction to the injected handler, formatting a
        # domain error into its API representation so the pre-try region of
        # run raises only TiferetAPIError.
        try:
            return self._build_logger(self.domain.logger_id)
        except TiferetError as e:
            return self.handle_error(e)

    # * method: build_request
    def build_request(self, feature_id: str, headers: Dict[str, str] = {}, data: Dict[str, Any] = {}) -> RequestContext:
        '''
        Build the request context for a feature execution.

        Template method override point. Delegates to the injected
        ``_create_request`` callable, which the blueprint layer wires from
        ``create_session_request``. An unwired handler raises ``APP_ERROR``
        naming the missing ``create_request_handler``.

        :param feature_id: The feature identifier.
        :type feature_id: str
        :param headers: The request headers.
        :type headers: dict
        :param data: The request data.
        :type data: dict
        :return: The composed request context.
        :rtype: RequestContext
        '''

        # Fail loudly when the blueprint-supplied request factory is absent.
        if self._create_request is None:
            raise_unwired_handler_error(
                'create_request_handler',
                self.domain.id,
                feature_id=feature_id,
            )

        # Delegate request construction to the injected handler.
        return self._create_request(self.domain.id, feature_id, headers, data)

    # * method: execute_feature
    def execute_feature(self, feature_id: str, request: RequestContext, **kwargs):
        '''
        Execute the feature request.

        Template method override point. Delegates to the injected
        ``_execute_feature`` callable, which the blueprint layer wires from
        ``execute_feature_handler``. Sync/async dispatch is handled internally by
        ``FeatureContext.execute_feature`` based on ``feature.is_async`` and
        ``step.is_async``.

        An unwired handler is a composition bug rather than a condition to
        degrade around, so it raises ``APP_ERROR`` instead of executing the
        feature by some other route. That error is already a
        ``TiferetAPIError``, so it reaches the caller verbatim when ``run``
        routes the failure through ``handle_error``.

        :param feature_id: The feature identifier.
        :type feature_id: str
        :param request: The request context object.
        :type request: RequestContext
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Fail loudly when the blueprint-supplied execution handler is absent.
        if self._execute_feature is None:
            raise_unwired_handler_error(
                'execute_feature_handler',
                self.domain.id,
                feature_id=feature_id,
            )

        # Delegate execution to the injected handler.
        self._execute_feature(feature_id, request, **kwargs)

    # * method: handle_error
    def handle_error(self, error: Exception, **kwargs) -> Any:
        '''
        Handle the error.

        Template method override point. A ``TiferetAPIError`` is already the
        formatted, consumer-facing representation, so it is re-raised verbatim
        rather than round-tripped through the handler, which would re-derive
        its name and message from the error catalog. Every other error is
        delegated to the injected ``_raise_error`` callable, which the
        blueprint layer wires from ``raise_error_handler``; an unwired handler
        raises ``APP_ERROR`` naming it, carrying the original error's code and
        message so the wiring bug does not destroy the underlying failure.

        :param error: The error to handle.
        :type error: Exception
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The error response.
        :rtype: Any
        '''

        # Pass a formatted API error straight through to the caller.
        if isinstance(error, TiferetAPIError):
            raise error

        # Fail loudly when the blueprint-supplied error handler is absent,
        # preserving the original failure as error context.
        if self._raise_error is None:
            raise_unwired_handler_error(
                'raise_error_handler',
                self.domain.id,
                original_error_code=getattr(error, 'error_code', None),
                original_error_message=str(error),
            )

        # Delegate error handling to the injected handler.
        return self._raise_error(error, **kwargs)

    # * method: build_response
    def build_response(self, request: RequestContext) -> Any:
        '''
        Build the response from a completed request context.

        Template method override point. Delegates to the injected
        ``_build_response`` callable, which the blueprint layer wires from
        ``response_handler``; an unwired handler raises ``APP_ERROR`` naming it.
        Subclasses override this method to produce context-specific output
        (e.g. a ``CliSessionContext`` serialises to stdout; a
        ``FlaskApiContext`` wraps in a JSON response).

        :param request: The completed request context.
        :type request: RequestContext
        :return: The handled feature response.
        :rtype: Any
        '''

        # Fail loudly when the blueprint-supplied response handler is absent.
        if self._build_response is None:
            raise_unwired_handler_error(
                'response_handler',
                self.domain.id,
            )

        # Delegate response extraction to the injected handler.
        return self._build_response(request)

    # * method: run
    def run(self,
            feature_id: str,
            headers: Dict[str, str] = {},
            data: Dict[str, Any] = {},
            **kwargs) -> Any:
        '''
        Run the application session by executing the feature.

        Pure orchestrator that calls the four template methods in order:
        ``build_request`` → ``execute_feature`` → ``handle_error`` (on error)
        → ``build_response``. Each method is a stable subclass override point.

        :param feature_id: The feature identifier.
        :type feature_id: str
        :param headers: The request headers.
        :type headers: dict
        :param data: The request data.
        :type data: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The feature response.
        :rtype: Any
        '''

        # Start timing immediately.
        start_time = time.perf_counter()

        # Build the logger for this session run via the template method.
        logger = self.build_logger()

        # Build request via the template method.
        logger.debug(f'Building request for feature: {feature_id}')
        request = self.build_request(feature_id, headers or {}, data or {})

        # Execute feature via the template method.
        try:
            logger.debug(f'Executing feature: {feature_id} with request: {request.data}')
            self.execute_feature(feature_id, request, logger=logger, **kwargs)

        # Handle error and return response if triggered.
        except TiferetError as e:
            logger.error(f'Error executing feature {feature_id}: {str(e)}')
            return self.handle_error(e, **kwargs)

        # Calculate execution duration in milliseconds.
        duration_ms = round((time.perf_counter() - start_time) * 1000)

        # Log successful execution with timing.
        logger.debug(f'Feature {feature_id} executed successfully, building response.')
        logger.info(f'Executed Feature - {feature_id} ({duration_ms}ms)')

        # Build and return the response via the template method.
        return self.build_response(request)

