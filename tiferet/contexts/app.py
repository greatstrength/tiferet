"""Tiferet App Contexts"""

# *** imports

# ** core
import time
from typing import Any, Callable, Dict, List, Tuple

# ** app
from ..assets import TiferetError, TiferetAPIError
from ..domain import AppSession, AppServiceDependency, Feature
from ..events import DomainEvent
from ..events.app import GetAppSession
from ..interfaces import AppService
from .core import BaseContext
from .cache import CacheContext
from .feature import FeatureContext, FEATURE_CACHE_PREFIX
from .logging import LoggingContext
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
                    AppServiceDependency.model_validate(service_data),
                    *APP_SERVICE_CACHE_PREFIX,
                )

            # Return the populated cache context.
            return cache

        # Return the cache-builder wrapper.
        return wrapper

    # Return the decorator.
    return decorator

# ** function: get_default_app_services
def get_default_app_services(cache: CacheContext) -> List[AppServiceDependency]:
    '''
    Return the default app service dependencies seeded on the cache.

    :param cache: The cache context to read.
    :type cache: CacheContext
    :return: The list of seeded app service dependencies.
    :rtype: List[AppServiceDependency]
    '''

    # Return the seeded app service dependencies as a list.
    return list(cache.get_by_prefix(*APP_SERVICE_CACHE_PREFIX).values())

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

# ** function: get_default_app_constants
def get_default_app_constants(cache: CacheContext) -> Dict[str, Any]:
    '''
    Return the default app constants seeded on the cache.

    :param cache: The cache context to read.
    :type cache: CacheContext
    :return: The mapping of seeded app constants.
    :rtype: Dict[str, Any]
    '''

    # Return the seeded app constants.
    return cache.get_by_prefix(*APP_CONSTANT_CACHE_PREFIX)

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
                    AppServiceDependency.model_validate(service_data),
                    *ADMIN_SERVICE_CACHE_PREFIX,
                )

            # Return the populated cache context.
            return cache

        # Return the cache-builder wrapper.
        return wrapper

    # Return the decorator.
    return decorator

# ** function: get_default_admin_services
def get_default_admin_services(cache: CacheContext) -> List[AppServiceDependency]:
    '''
    Return the default admin service dependencies seeded on the cache.

    :param cache: The cache context to read.
    :type cache: CacheContext
    :return: The list of seeded admin service dependencies.
    :rtype: List[AppServiceDependency]
    '''

    # Return the seeded admin service dependencies as a list.
    return list(cache.get_by_prefix(*ADMIN_SERVICE_CACHE_PREFIX).values())

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

# ** function: get_default_admin_constants
def get_default_admin_constants(cache: CacheContext) -> Dict[str, Any]:
    '''
    Return the default admin constants seeded on the cache.

    :param cache: The cache context to read.
    :type cache: CacheContext
    :return: The mapping of seeded admin constants.
    :rtype: Dict[str, Any]
    '''

    # Return the seeded admin constants.
    return cache.get_by_prefix(*ADMIN_CONSTANT_CACHE_PREFIX)

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
                    AppSession.model_validate(session_data),
                    *APP_SESSION_CACHE_PREFIX,
                )

            # Return the populated cache context.
            return cache

        # Return the cache-builder wrapper.
        return wrapper

    # Return the decorator.
    return decorator

# ** function: get_default_app_session
def get_default_app_session(cache: CacheContext, session_id: str) -> AppSession | None:
    '''
    Return a default app session seeded on the cache by id.

    :param cache: The cache context to read.
    :type cache: CacheContext
    :param session_id: The identifier of the app session to retrieve.
    :type session_id: str
    :return: The seeded app session, or None when absent.
    :rtype: AppSession | None
    '''

    # Return the seeded app session, or None when absent.
    return cache.get(session_id, *APP_SESSION_CACHE_PREFIX)

# *** contexts

# ** context: app_session_context
class AppSessionContext(BaseContext):
    '''
    The application session hub binds a loaded ``AppSession`` domain object
    and delegates feature execution, error handling, request construction,
    and response building to four injected FE4 template-method handlers.
    '''

    # * attribute: domain_type
    domain_type = AppSession

    # * attribute: get_dependency
    get_dependency: Callable

    # * attribute: cache
    cache: CacheContext

    # * attribute: logging (private)
    _logging: LoggingContext

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
            logging_context: LoggingContext = None,
            cache: CacheContext = None,
            execute_feature_handler: Callable = None,
            create_request_handler: Callable = None,
            raise_error_handler: Callable = None,
            response_handler: Callable = None):
        '''
        Initialize the application session hub.

        :param get_dependency: The DI resolution handler injected by the blueprint.
        :type get_dependency: Callable
        :param logging_context: The logging context bound at bootstrap.
        :type logging_context: LoggingContext
        :param cache: The shared bootstrap cache.
        :type cache: CacheContext
        :param execute_feature_handler: The FE4 feature-execution handler.
        :type execute_feature_handler: Callable
        :param create_request_handler: The FE4 request-construction handler.
        :type create_request_handler: Callable
        :param raise_error_handler: The FE4 error-handling handler.
        :type raise_error_handler: Callable
        :param response_handler: The FE4 response-building handler.
        :type response_handler: Callable
        '''

        # Initialize the base context.
        super().__init__()

        # Store the DI resolution handler and shared bootstrap cache.
        self.get_dependency = get_dependency
        self.cache = cache or CacheContext()

        # Store the logging context.
        self._logging = logging_context

        # Store the FE4 template-method handlers.
        self._execute_feature = execute_feature_handler
        self._create_request = create_request_handler
        self._raise_error = raise_error_handler
        self._build_response = response_handler

    # * method: load (static)
    @classmethod
    def load(cls, interface_id: str, app_service: AppService) -> AppSession:
        '''
        Retrieve an app session by id without importing the events layer directly.

        :param interface_id: The identifier of the app session to load.
        :type interface_id: str
        :param app_service: The app service used to resolve the session.
        :type app_service: AppService
        :return: The loaded app session.
        :rtype: AppSession
        '''

        # Delegate to the GetAppSession domain event.
        return DomainEvent.handle(
            GetAppSession,
            dependencies=dict(app_service=app_service),
            id=interface_id,
        )

    # * method: load_logging_context
    def load_logging_context(self) -> LoggingContext:
        '''
        Return the logging context bound at bootstrap.

        :return: The bound logging context.
        :rtype: LoggingContext
        '''

        # Return the bound logging context.
        return self._logging

    # * method: build_request
    def build_request(self,
            feature_id: str,
            headers: Dict[str, str] = {},
            data: Dict[str, Any] = {}) -> RequestContext:
        '''
        Build the request context for a feature execution.

        :param feature_id: The identifier of the feature to execute.
        :type feature_id: str
        :param headers: The request headers.
        :type headers: Dict[str, str]
        :param data: The request data.
        :type data: Dict[str, Any]
        :return: The constructed request context.
        :rtype: RequestContext
        '''

        # Delegate to the injected request-construction handler when wired.
        if self._create_request:
            return self._create_request(self.domain.id, feature_id, headers, data)

        # Otherwise construct the request context directly, stamping the
        # interface id onto the request headers.
        return RequestContext(
            headers={**(headers or {}), 'interface_id': self.domain.id},
            data=data,
            feature_id=feature_id,
        )

    # * method: execute_feature
    def execute_feature(self, feature_id: str, request: RequestContext, **kwargs) -> Any:
        '''
        Execute a feature against the given request.

        :param feature_id: The identifier of the feature to execute.
        :type feature_id: str
        :param request: The request context object.
        :type request: RequestContext
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of the feature execution.
        :rtype: Any
        '''

        # Delegate to the injected feature-execution handler when wired.
        if self._execute_feature:
            return self._execute_feature(feature_id, request, **kwargs)

        # Otherwise resolve the registered FeatureContext and drive it directly
        # against a feature pre-seeded on the shared cache.
        feature_context_cls = BaseContext.for_domain(Feature)
        feature_context = feature_context_cls(get_dependency=self.get_dependency, cache=self.cache)
        feature = self.cache.get(feature_id, *FEATURE_CACHE_PREFIX)
        return feature_context.execute_feature(feature, request, **kwargs)

    # * method: handle_error
    def handle_error(self, error: Exception, **kwargs) -> Any:
        '''
        Handle an error raised during feature execution.

        :param error: The error to handle.
        :type error: Exception
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The error response.
        :rtype: Any
        '''

        # Delegate to the injected error-handling handler when wired.
        if self._raise_error:
            return self._raise_error(error, **kwargs)

        # Wrap bare exceptions in a TiferetError.
        if not isinstance(error, TiferetError):
            error = TiferetError(
                'APP_ERROR',
                f'An error occurred in the app: {str(error)}',
                error=str(error),
            )

        # Raise a structured API error built from the wrapped error.
        raise TiferetAPIError(
            error_code=error.error_code,
            name=error.error_code,
            message=str(error),
            **error.kwargs,
        )

    # * method: build_response
    def build_response(self, request: RequestContext) -> Any:
        '''
        Build the final response from the executed request.

        :param request: The request context object.
        :type request: RequestContext
        :return: The response.
        :rtype: Any
        '''

        # Delegate to the injected response-building handler when wired.
        if self._build_response:
            return self._build_response(request)

        # Otherwise delegate directly to the request context.
        return request.handle_response()

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
        logger = self.load_logging_context().build_logger()

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

