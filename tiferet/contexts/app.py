"""Tiferet App Contexts"""

# *** imports

# ** core
import asyncio
import threading
import time
from typing import Dict, Any, List, Callable

# ** app
from ..assets import (
    TiferetError,
    TiferetAPIError,
    ERROR_NOT_FOUND_ID,
    DEFAULT_ERRORS,
)
from ..domain import AppInterface, Feature, CliCommand, Error
from ..events import DomainEvent
from .base import BaseContext
from .cache import CacheContext
from .feature import FeatureContext, AsyncFeatureContext
from .error import ErrorContext
from .logging import LoggingContext
from .request import RequestContext

# *** contexts

# ** context: app_interface_context
class AppInterfaceContext(BaseContext):
    '''
    The application interface context is a minimal hub that builds operational
    sub-contexts on demand from a loaded ``AppInterface`` domain object and
    orchestrates feature execution, error handling, and logging.
    '''

    # * attribute: domain_type
    domain_type = AppInterface

    # * attribute: get_feature_evt
    get_feature_evt: DomainEvent

    # * attribute: get_error_evt
    get_error_evt: DomainEvent

    # * attribute: logging_list_all_evt
    logging_list_all_evt: DomainEvent

    # * attribute: get_dependency
    get_dependency: Callable

    # * init
    def __init__(self,
            get_feature_evt: DomainEvent,
            get_error_evt: DomainEvent,
            logging_list_all_evt: DomainEvent,
            get_dependency: Callable,
            cache: CacheContext = None,
            default_features: List[Dict[str, Any]] = None,
            default_commands: List[Dict[str, Any]] = None,
        ):
        '''
        Initialize the application interface hub.

        The bound ``AppInterface`` domain object (set via ``from_domain``)
        supplies the interface id and logger id on demand, so no standalone
        ``interface_id`` is stored.

        :param get_feature_evt: The event used to retrieve features.
        :type get_feature_evt: DomainEvent
        :param get_error_evt: The event used to retrieve errors.
        :type get_error_evt: DomainEvent
        :param logging_list_all_evt: The event used to list logging configurations.
        :type logging_list_all_evt: DomainEvent
        :param get_dependency: The injected service-resolution handler used to resolve feature step events and middleware.
        :type get_dependency: Callable
        :param cache: The shared cache context for all sub-contexts.
        :type cache: CacheContext
        :param default_features: Optional raw feature dicts for bootstrap fallback.
        :type default_features: List[Dict[str, Any]]
        :param default_commands: Optional raw CLI command dicts for bootstrap fallback.
        :type default_commands: List[Dict[str, Any]]
        '''

        # Initialize the shared cache via the base context.
        super().__init__(cache=cache)

        # Store the retrieval/configuration events and the service-resolution handler.
        self.get_feature_evt = get_feature_evt
        self.get_error_evt = get_error_evt
        self.logging_list_all_evt = logging_list_all_evt
        self.get_dependency = get_dependency

        # Validate raw bootstrap feature dicts into a typed index keyed by id.
        self.default_feature_index = {
            feature.id: feature
            for feature in (Feature.model_validate(data) for data in (default_features or []))
        }

        # Validate raw bootstrap command dicts into a typed list.
        self.default_commands_list = [
            CliCommand.model_validate(data) for data in (default_commands or [])
        ]

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
                cache=self.cache,
            )

        # Return the shared logging context.
        return self._logging

    # * method: load_feature_domain
    def load_feature_domain(self, feature_id: str) -> Feature:
        '''
        Load a feature domain object by id, using the shared cache and the
        bootstrap default feature index as an execute-time fallback.

        :param feature_id: The feature identifier.
        :type feature_id: str
        :return: The loaded feature domain object.
        :rtype: Feature
        '''

        # Try the shared cache first.
        feature = self.cache.get(feature_id)

        # Retrieve via the get-feature event and cache the result when absent.
        if not feature:
            feature = self.get_feature_evt.execute(
                id=feature_id,
                default_feature_index=self.default_feature_index,
            )
            self.cache.set(feature_id, feature)

        # Return the loaded feature.
        return feature

    # * method: load_error_domain
    def load_error_domain(self, error_code: str) -> Error:
        '''
        Load an error domain object by its code, falling back to the built-in
        ``ERROR_NOT_FOUND`` definition when the code cannot be resolved.

        :param error_code: The error code to resolve.
        :type error_code: str
        :return: The loaded error domain object.
        :rtype: Error
        '''

        # Retrieve the error by code, including built-in defaults.
        try:
            return self.get_error_evt.execute(error_code, include_defaults=True)

        # On lookup failure, raise the API error using the ERROR_NOT_FOUND details.
        except TiferetError:
            error = Error(**DEFAULT_ERRORS.get(ERROR_NOT_FOUND_ID))
            raise TiferetAPIError(
                error_code=error.id,
                name=error.name,
                message=error.format_message(),
                id=error_code,
            )

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

    # * method: _run_coroutine (static)
    @staticmethod
    def _run_coroutine(coro: Any) -> Any:
        '''
        Drive a coroutine to completion from synchronous code.

        Uses ``asyncio.run`` when no event loop is running. When called while a
        loop is already running (e.g. inside an async host), the coroutine is
        executed on a short-lived dedicated thread with its own event loop so
        the synchronous ``run`` entrypoint never raises ``RuntimeError``.

        :param coro: The coroutine to execute.
        :type coro: Any
        :return: The coroutine result.
        :rtype: Any
        '''

        # Use asyncio.run directly when no event loop is currently running.
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)

        # A loop is already running; execute the coroutine on a dedicated
        # thread with its own event loop, capturing the result or error.
        box: Dict[str, Any] = {}

        def _runner():
            try:
                box['result'] = asyncio.run(coro)
            except BaseException as error:  # re-raised on the calling thread
                box['error'] = error

        # Run the worker thread to completion.
        thread = threading.Thread(target=_runner)
        thread.start()
        thread.join()

        # Re-raise any error captured on the worker thread.
        if 'error' in box:
            raise box['error']

        # Return the captured coroutine result.
        return box.get('result')

    # * method: execute_feature
    def execute_feature(self, feature_id: str, request: RequestContext, **kwargs):
        '''
        Execute the feature request.

        Selects the synchronous :class:`FeatureContext` or the
        :class:`AsyncFeatureContext` based on the loaded feature's ``is_async``
        flag. Async features are driven to completion while keeping this
        entrypoint synchronous.

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

        # Build the async feature context and drive it to completion when the
        # loaded feature is flagged async.
        if feature.is_async:
            async_context = AsyncFeatureContext(
                get_dependency=self.get_dependency,
                cache=self.cache,
                context_data={'default_commands_list': self.default_commands_list},
            )
            self._run_coroutine(
                async_context.execute_feature_async(feature, request, **kwargs)
            )
            return

        # Otherwise build the synchronous feature context on demand (resolved
        # via the registry) and execute the loaded feature through it.
        feature_context_cls = BaseContext.for_domain(Feature)
        feature_context = feature_context_cls(
            get_dependency=self.get_dependency,
            cache=self.cache,
            context_data={'default_commands_list': self.default_commands_list},
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
        error_domain = self.load_error_domain(error.error_code)

        # Build the error context on demand (resolved via the registry) and
        # format the response for the loaded error.
        error_context_cls = BaseContext.for_domain(Error)
        formatted_error = error_context_cls(cache=self.cache).format_response(error_domain, error)

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
