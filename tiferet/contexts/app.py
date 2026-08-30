"""Tiferet App Contexts"""

# *** imports

# ** core
import logging
import time
from typing import Any, Callable, Dict, List, Tuple

# ** app
from ..assets import TiferetError, TiferetAPIError
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

# ** function: raise_unwired_handler_error
def raise_unwired_handler_error(handler_name: str, session_id: str, **kwargs) -> None:
    '''
    Raise a structured API error when a required hub handler is unwired.

    Always raises; never returns. Callers treat this as a terminal statement.

    :param handler_name: The name of the missing handler slot.
    :type handler_name: str
    :param session_id: The app session id that expected the handler.
    :type session_id: str
    :param kwargs: Additional context forwarded onto the API error.
    :type kwargs: dict
    '''

    # Compose a message naming the missing handler and the session that needed it.
    message = (
        f'No {handler_name} is wired on the app session context for session '
        f'{session_id}; the blueprint must supply {handler_name}.'
    )

    # Raise a structured API error; this function never returns.
    raise TiferetAPIError(
        error_code=APP_ERROR_ID,
        name='App Error',
        message=message,
        **kwargs,
    )

# ** function: add_default_app_services
def add_default_app_services(services: Dict[str, Any]) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with default app service dependencies.

    :param services: A mapping of service id to raw service dependency definition dicts.
    :type services: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Return the decorator that wraps the cache-builder.
    def decorator(build_fn: Callable) -> Callable:

        # Build the cache, then populate it with the default service dependencies.
        def wrapper(*args, **kwargs) -> CacheContext:

            # Delegate to the wrapped cache-builder.
            cache = build_fn(*args, **kwargs)

            # Reconstitute each raw service dict into an AppServiceDependency and
            # cache it under the app service namespace keyed by service id.
            for service_id, service_data in services.items():
                cache.set(
                    service_id,
                    AppServiceDependency.model_validate({**service_data, 'service_id': service_id}),
                    *APP_SERVICE_CACHE_PREFIX,
                )

            # Return the populated cache context.
            return cache

        # Return the cache-builder wrapper.
        return wrapper

    # Return the decorator.
    return decorator

# ** function: add_default_app_constants
def add_default_app_constants(constants: Dict[str, Any]) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with default app constants.

    :param constants: A mapping of constant id to scalar value.
    :type constants: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Return the decorator that wraps the cache-builder.
    def decorator(build_fn: Callable) -> Callable:

        # Build the cache, then populate it with the default constants.
        def wrapper(*args, **kwargs) -> CacheContext:

            # Delegate to the wrapped cache-builder.
            cache = build_fn(*args, **kwargs)

            # Cache each scalar constant under the app constants namespace.
            for constant_id, value in constants.items():
                cache.set(constant_id, value, *APP_CONSTANT_CACHE_PREFIX)

            # Return the populated cache context.
            return cache

        # Return the cache-builder wrapper.
        return wrapper

    # Return the decorator.
    return decorator

# ** function: add_default_admin_services
def add_default_admin_services(services: Dict[str, Any]) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with default admin service dependencies.

    :param services: A mapping of service id to raw service dependency definition dicts.
    :type services: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Return the decorator that wraps the cache-builder.
    def decorator(build_fn: Callable) -> Callable:

        # Build the cache, then populate it with the default admin service dependencies.
        def wrapper(*args, **kwargs) -> CacheContext:

            # Delegate to the wrapped cache-builder.
            cache = build_fn(*args, **kwargs)

            # Reconstitute each raw service dict into an AppServiceDependency and
            # cache it under the admin service namespace keyed by service id.
            for service_id, service_data in services.items():
                cache.set(
                    service_id,
                    AppServiceDependency.model_validate({**service_data, 'service_id': service_id}),
                    *ADMIN_SERVICE_CACHE_PREFIX,
                )

            # Return the populated cache context.
            return cache

        # Return the cache-builder wrapper.
        return wrapper

    # Return the decorator.
    return decorator

# ** function: add_default_admin_constants
def add_default_admin_constants(constants: Dict[str, Any]) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with default admin constants.

    :param constants: A mapping of constant id to scalar value.
    :type constants: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Return the decorator that wraps the cache-builder.
    def decorator(build_fn: Callable) -> Callable:

        # Build the cache, then populate it with the default admin constants.
        def wrapper(*args, **kwargs) -> CacheContext:

            # Delegate to the wrapped cache-builder.
            cache = build_fn(*args, **kwargs)

            # Cache each scalar constant under the admin constants namespace.
            for constant_id, value in constants.items():
                cache.set(constant_id, value, *ADMIN_CONSTANT_CACHE_PREFIX)

            # Return the populated cache context.
            return cache

        # Return the cache-builder wrapper.
        return wrapper

    # Return the decorator.
    return decorator

# ** function: add_default_app_sessions
def add_default_app_sessions(sessions: Dict[str, Any]) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with default app sessions.

    :param sessions: A mapping of session id to raw app session definition dicts.
    :type sessions: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Return the decorator that wraps the cache-builder.
    def decorator(build_fn: Callable) -> Callable:

        # Build the cache, then populate it with the default app sessions.
        def wrapper(*args, **kwargs) -> CacheContext:

            # Delegate to the wrapped cache-builder.
            cache = build_fn(*args, **kwargs)

            # Reconstitute each raw session dict into an AppSession and cache
            # it under the app session namespace keyed by session id.
            for session_id, session_data in sessions.items():
                cache.set(
                    session_id,
                    AppSession.model_validate({**session_data, 'id': session_id}),
                    *APP_SESSION_CACHE_PREFIX,
                )

            # Return the populated cache context.
            return cache

        # Return the cache-builder wrapper.
        return wrapper

    # Return the decorator.
    return decorator

# *** contexts

# ** context: app_session_context
class AppSessionContext(BaseContext):
    '''
    The application session hub binds a loaded ``AppSession`` domain object
    and delegates feature execution, error handling, request construction,
    response building, and logger construction to five injected template-method
    handlers. An unwired handler is a composition bug and fails loudly.
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
            response_handler: Callable = None):
        '''
        Initialize the application session hub.

        :param get_dependency: The DI resolution handler injected by the blueprint.
        :type get_dependency: Callable
        :param cache: The shared bootstrap cache.
        :type cache: CacheContext
        :param build_logger_handler: The logger-construction handler.
        :type build_logger_handler: Callable
        :param execute_feature_handler: The feature-execution handler.
        :type execute_feature_handler: Callable
        :param create_request_handler: The request-construction handler.
        :type create_request_handler: Callable
        :param raise_error_handler: The error-handling handler.
        :type raise_error_handler: Callable
        :param response_handler: The response-building handler.
        :type response_handler: Callable
        '''

        # Initialize the base context.
        super().__init__()

        # Store the DI resolution handler and shared bootstrap cache.
        self.get_dependency = get_dependency
        self.cache = cache or CacheContext()

        # Store the five template-method handlers (validated lazily on first use).
        self._build_logger = build_logger_handler
        self._execute_feature = execute_feature_handler
        self._create_request = create_request_handler
        self._raise_error = raise_error_handler
        self._build_response = response_handler

    # * method: build_logger
    def build_logger(self) -> logging.Logger:
        '''
        Build the logger for this session run.

        Delegates to the injected handler; fails loudly via
        ``raise_unwired_handler_error`` when unwired. Domain errors raised by
        the handler are formatted through ``handle_error`` so the pre-try
        region of ``run`` surfaces only ``TiferetAPIError``.

        :return: The configured logger instance.
        :rtype: logging.Logger
        '''

        # Fail loudly when the logger-construction handler is unwired.
        if self._build_logger is None:
            raise_unwired_handler_error('build_logger_handler', self.domain.id)

        # Delegate to the injected handler, formatting domain errors as API errors.
        try:
            return self._build_logger(self.domain.logger_id)

        # Format domain errors through handle_error rather than propagating raw.
        except TiferetError as e:
            return self.handle_error(e)

    # * method: build_request
    def build_request(self,
            feature_id: str,
            headers: Dict[str, str] = {},
            data: Dict[str, Any] = {}) -> RequestContext:
        '''
        Build the request context for a feature execution.

        Delegates to the injected handler; fails loudly via
        ``raise_unwired_handler_error`` when unwired.

        :param feature_id: The identifier of the feature to execute.
        :type feature_id: str
        :param headers: The request headers.
        :type headers: Dict[str, str]
        :param data: The request data.
        :type data: Dict[str, Any]
        :return: The constructed request context.
        :rtype: RequestContext
        '''

        # Fail loudly when the request-construction handler is unwired.
        if self._create_request is None:
            raise_unwired_handler_error(
                'create_request_handler',
                self.domain.id,
                feature_id=feature_id,
            )

        # Delegate to the injected request-construction handler.
        return self._create_request(self.domain.id, feature_id, headers, data)

    # * method: execute_feature
    def execute_feature(self, feature_id: str, request: RequestContext, **kwargs):
        '''
        Execute a feature against the given request.

        Delegates to the injected handler; fails loudly via
        ``raise_unwired_handler_error`` when unwired. The execution result is
        accumulated on the request context; result extraction is the
        responsibility of the response step.

        :param feature_id: The identifier of the feature to execute.
        :type feature_id: str
        :param request: The request context object.
        :type request: RequestContext
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Fail loudly when the feature-execution handler is unwired.
        if self._execute_feature is None:
            raise_unwired_handler_error(
                'execute_feature_handler',
                self.domain.id,
                feature_id=feature_id,
            )

        # Delegate to the injected feature-execution handler.
        self._execute_feature(feature_id, request, **kwargs)

    # * method: handle_error
    def handle_error(self, error: Exception, **kwargs) -> Any:
        '''
        Handle an error raised during feature execution.

        Re-raises an incoming ``TiferetAPIError`` verbatim. Otherwise delegates
        to the injected handler; fails loudly via ``raise_unwired_handler_error``
        when unwired.

        :param error: The error to handle.
        :type error: Exception
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The error response.
        :rtype: Any
        '''

        # Pass through an already-formatted API error without modification.
        if isinstance(error, TiferetAPIError):
            raise error

        # Fail loudly when the error-handling handler is unwired.
        if self._raise_error is None:
            raise_unwired_handler_error(
                'raise_error_handler',
                self.domain.id,
                original_error_code=getattr(error, 'error_code', None),
                original_error_message=str(error),
            )

        # Delegate to the injected error-handling handler.
        return self._raise_error(error, **kwargs)

    # * method: build_response
    def build_response(self, request: RequestContext) -> Any:
        '''
        Build the final response from the executed request.

        Delegates to the injected handler; fails loudly via
        ``raise_unwired_handler_error`` when unwired.

        :param request: The request context object.
        :type request: RequestContext
        :return: The response.
        :rtype: Any
        '''

        # Fail loudly when the response-building handler is unwired.
        if self._build_response is None:
            raise_unwired_handler_error('response_handler', self.domain.id)

        # Delegate to the injected response-building handler.
        return self._build_response(request)

    # * method: run
    def run(self,
            feature_id: str,
            headers: Dict[str, str] = {},
            data: Dict[str, Any] = {},
            **kwargs) -> Any:
        '''
        Run the application session by executing the requested feature.

        :param feature_id: The identifier of the feature to execute.
        :type feature_id: str
        :param headers: The request headers.
        :type headers: Dict[str, str]
        :param data: The request data.
        :type data: Dict[str, Any]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The response.
        :rtype: Any
        '''

        # Start timing immediately.
        start_time = time.perf_counter()

        # Build the logger for this session run.
        logger = self.build_logger()

        # Build the request context.
        logger.debug(f'Building request for feature: {feature_id}')
        request = self.build_request(feature_id, headers or {}, data or {})

        # Execute the feature, handling any structured error.
        try:
            logger.debug(f'Executing feature: {feature_id} with request: {request.data}')
            self.execute_feature(feature_id, request, logger=logger, **kwargs)

        # Handle the error and return the error response if one is raised.
        except TiferetError as e:
            logger.error(f'Error executing feature {feature_id}: {str(e)}')
            return self.handle_error(e, **kwargs)

        # Calculate execution duration in milliseconds.
        duration_ms = round((time.perf_counter() - start_time) * 1000)

        # Log successful execution with timing.
        logger.debug(f'Feature {feature_id} executed successfully, building response.')
        logger.info(f'Executed Feature - {feature_id} ({duration_ms}ms)')

        # Build and return the response.
        return self.build_response(request)

