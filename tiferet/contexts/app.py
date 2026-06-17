"""Tiferet App Contexts"""

# *** imports

# ** core
import time
from typing import Dict, Any, List

# ** app
from ..assets import (
    TiferetError,
    TiferetAPIError,
    ERROR_NOT_FOUND_ID,
    DEFAULT_ERRORS,
)
from ..domain import AppInterface, Feature, CliCommand, ServiceConfiguration, Error
from ..events import DomainEvent
from .base import BaseContext
from .cache import CacheContext
from .di import DIContext
from .feature import FeatureContext
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

    # * attribute: di_list_all_configs_evt
    di_list_all_configs_evt: DomainEvent

    # * attribute: logging_list_all_evt
    logging_list_all_evt: DomainEvent

    # * attribute: create_service_provider
    create_service_provider: Any

    # * init
    def __init__(self,
            get_feature_evt: DomainEvent,
            get_error_evt: DomainEvent,
            di_list_all_configs_evt: DomainEvent,
            logging_list_all_evt: DomainEvent,
            create_service_provider: Any = None,
            cache: CacheContext = None,
            default_features: List[Dict[str, Any]] = None,
            default_commands: List[Dict[str, Any]] = None,
            default_configurations: List[Dict[str, Any]] = None,
            default_constants: Dict[str, Any] = None,
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
        :param di_list_all_configs_evt: The event used to list DI configurations.
        :type di_list_all_configs_evt: DomainEvent
        :param logging_list_all_evt: The event used to list logging configurations.
        :type logging_list_all_evt: DomainEvent
        :param create_service_provider: Optional factory for creating service providers.
        :type create_service_provider: Any
        :param cache: The shared cache context for all sub-contexts.
        :type cache: CacheContext
        :param default_features: Optional raw feature dicts for bootstrap fallback.
        :type default_features: List[Dict[str, Any]]
        :param default_commands: Optional raw CLI command dicts for bootstrap fallback.
        :type default_commands: List[Dict[str, Any]]
        :param default_configurations: Optional raw service configuration dicts for bootstrap fallback.
        :type default_configurations: List[Dict[str, Any]]
        :param default_constants: Optional default DI constants for bootstrap fallback.
        :type default_constants: Dict[str, Any]
        '''

        # Initialize the shared cache via the base context.
        super().__init__(cache=cache)

        # Store the retrieval and configuration events plus the provider factory.
        self.get_feature_evt = get_feature_evt
        self.get_error_evt = get_error_evt
        self.di_list_all_configs_evt = di_list_all_configs_evt
        self.logging_list_all_evt = logging_list_all_evt
        self.create_service_provider = create_service_provider

        # Validate raw bootstrap feature dicts into a typed index keyed by id.
        self.default_feature_index = {
            feature.id: feature
            for feature in (Feature.model_validate(data) for data in (default_features or []))
        }

        # Validate raw bootstrap command dicts into a typed list.
        self.default_commands_list = [
            CliCommand.model_validate(data) for data in (default_commands or [])
        ]

        # Validate raw bootstrap configuration dicts into a typed index keyed by id.
        self.default_config_index = {
            config.id: config
            for config in (ServiceConfiguration.model_validate(data) for data in (default_configurations or []))
        }

        # Copy the bootstrap DI constants, defaulting to an empty mapping.
        self.default_di_constants = dict(default_constants) if default_constants else {}

        # Initialize lazily-built sub-context caches for the shared DI and
        # logging contexts. Feature and error contexts are built on demand.
        self._services = None
        self._logging = None

    # * method: get_service_type_mapping (static)
    @staticmethod
    def get_service_type_mapping(app_interface: AppInterface) -> Dict[str, Any]:
        '''
        Build the dependency type mapping for an app interface.

        Assembles the interface's scalars, constants, and service dependency
        types (plus their parameters) into a single mapping consumed by the
        service provider. The hub itself is constructed declaratively by the
        blueprint, so it is intentionally not registered here.

        :param app_interface: The loaded app interface definition.
        :type app_interface: AppInterface
        :return: A mapping of service IDs to their types and constant values.
        :rtype: Dict[str, Any]
        '''

        # Register interface scalars first.
        dependencies: Dict[str, Any] = {
            'interface_id': app_interface.id,
            'logger_id': getattr(app_interface, 'logger_id', None),
        }

        # Add the interface constants.
        dependencies.update(app_interface.constants)

        # Add each service dependency type and its parameters.
        for dep in app_interface.services:
            dependencies[dep.service_id] = dep.get_service_type()
            for param, value in dep.parameters.items():
                dependencies[param] = value

        # Return the assembled dependency mapping.
        return dependencies

    # * method: _get_services
    def _get_services(self) -> DIContext:
        '''
        Build (once) and return the shared DI context.

        :return: The shared DI context.
        :rtype: DIContext
        '''

        # Build the DI context on first access, wiring bootstrap defaults.
        if self._services is None:
            self._services = DIContext(
                di_list_all_configs_evt=self.di_list_all_configs_evt,
                cache=self.cache,
                create_service_provider=self.create_service_provider,
                default_config_index=self.default_config_index,
                default_di_constants=self.default_di_constants,
            )

        # Return the shared DI context.
        return self._services

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

    # * method: execute_feature
    def execute_feature(self, feature_id: str, request: RequestContext, **kwargs):
        '''
        Execute the feature request.

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

        # Build the feature context on demand (resolved via the registry) and
        # execute the loaded feature through it.
        feature_context_cls = BaseContext.for_domain(Feature)
        feature_context = feature_context_cls(
            services=self._get_services(),
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
