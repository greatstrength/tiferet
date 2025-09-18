# *** imports

# ** core
from typing import Dict, Any

# ** app
from .feature import FeatureContext
from .error import ErrorContext
from .logging import LoggingContext
from .request import RequestContext
from ..configs.app import DEFAULT_ATTRIBUTES
from ..models.app import *
from ..handlers.app import (
    AppService,
    AppHandler,
    AppRepository,
)
from ..commands import (
    Command,
    TiferetError
)
from ..commands.app import GetAppInterface

# *** contexts

# ** context: app_manager_context
class AppManagerContext(object):
    '''
    The AppManagerContext is responsible for managing the application context.
    It provides methods to load the application interface and run features.
    '''

    # * attribute: settings
    settings: Dict[str, Any]

    # * attribute: app_service
    app_service: AppService

    # * init
    def __init__(self, settings: Dict[str, Any], app_service: AppService = AppHandler()):
        '''
        Initialize the AppManagerContext with an application service.

        :param settings: The application settings.
        :type settings: dict
        :param app_service: The application service to use.
        :type app_service: AppService
        '''

        # Set the settings.
        self.settings = settings

        # Set the app service.
        self.app_service = app_service

    # * method: load_interface
    def load_interface(self, interface_id: str) -> 'AppInterfaceContext':
        '''
        Load the application interface.

        :param interface_id: The interface ID.
        :type interface_id: str
        :return: The application interface context.
        :rtype: AppInterfaceContext
        '''

        # Load the app repository.
        app_repo: AppRepository = self.app_service.load_app_repository(**self.settings)

        # Get the app interface settings.
        app_interface = Command.handle(
            GetAppInterface,
            dependencies=dict(
                app_repo=app_repo
            ),
            interface_id=interface_id
        )

        # Retrieve the default attributes from the configuration.
        default_attrs = [ModelObject.new(
            AppAttribute,
            **attr_data,
            validate=False
        ) for attr_data in DEFAULT_ATTRIBUTES]
        
        # Create the app interface context.
        app_interface_context = self.app_service.load_app_instance(app_interface, default_attrs=default_attrs)

        # Verify that the app interface context is valid.
        if not isinstance(app_interface_context, AppInterfaceContext):
            raise TiferetError(
                'APP_INTERFACE_INVALID',
                f'App context for interface is not valid: {interface_id}.',
                interface_id
            )
        
        # Return the app interface context.
        return app_interface_context
    
    # * method: run
    def run(self,
            interface_id: str,
            feature_id: str,
            headers: Dict[str, str] = {},
            data: Dict[str, Any] = {},
            debug: bool = False,
            **kwargs
        ) -> Any:
        '''
        Run the application interface.

        :param interface_id: The interface ID.
        :type interface_id: str
        :param dependencies: The dependencies.
        :type dependencies: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The response.
        :rtype: Any
        '''

        # Load the interface.
        app_interface = self.load_interface(interface_id)

        # Run the interface.
        return app_interface.run(
            feature_id, 
            headers, 
            data, 
            debug=debug,
            **kwargs
        )

# ** context: app_interface_context
class AppInterfaceContext(object): 
    '''
    The application interface context is a class that is used to create and run the application interface.
    '''

    # * attribute: interface_id
    interface_id: str

    # * attribute: features
    features: FeatureContext

    # * attribute: errors
    errors: ErrorContext

    # * attribute: logging
    logging: LoggingContext

    # * init
    def __init__(self, interface_id: str, features: FeatureContext, errors: ErrorContext, logging: LoggingContext):
        '''
        Initialize the application interface context.

        :param interface_id: The interface ID.
        :type interface_id: str
        :param features: The feature context.
        :type features: FeatureContext
        :param errors: The error context.
        :type errors: ErrorContext
        '''

        # Assign instance variables.
        self.interface_id = interface_id
        self.features = features
        self.errors = errors
        self.logging = logging

    # * method: parse_request
    def parse_request(self, headers: Dict[str, str] = {}, data: Dict[str, Any] = {}, feature_id: str = None) -> RequestContext:
        '''
        Parse the incoming request.

        :param headers: The request headers.
        :type headers: dict
        :param data: The request data.
        :type data: dict
        :param feature_id: The feature identifier if provided.
        :type feature_id: str
        :return: The parsed request as a request context.
        :rtype: RequestContext
        '''

        # Add the interface id to the request headers.
        headers.update(dict(
            interface_id=self.interface_id,
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
        Execute the feature context.

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

        # Execute feature context and return session.
        self.features.execute_feature(feature_id, request, **kwargs)

    # * method: handle_error
    def handle_error(self, error: Exception) -> Any:
        '''
        Handle the error and return the response.

        :param error: The error to handle.
        :type error: Exception
        :return: The error response.
        :rtype: Any
        '''

        # If the error is not a TiferetError, wrap it in one.
        if not isinstance(error, TiferetError):
            error = TiferetError(
                'APP_ERROR',
                f'An error occurred in the app: {str(error)}',
                str(error)
            )

        # Handle the error and return the response.
        return self.errors.handle_error(error)

    # * method: handle_response
    def handle_response(self, request: RequestContext) -> Any:
        '''
        Handle the response from the request.

        :param request: The request context.
        :type request: RequestContext
        :return: The response.
        :rtype: Any
        '''

        # Handle the response and return it.
        return request.handle_response()
    
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

        # Create the logger for the app interface context.
        logger = self.logging.build_logger()
        
        # Parse request.
        logger.debug(f'Parsing request for feature: {feature_id}')
        request = self.parse_request(headers, data)

        # Execute feature context and return session.
        try:
            logger.info(f'Executing feature: {feature_id}')
            logger.debug(f'Executing feature: {feature_id} with request: {request.data}')
            self.execute_feature(
                feature_id=feature_id, 
                request=request, 
                logger=logger,
                **kwargs)

        # Handle error and return response if triggered.
        except TiferetError as e:
            logger.error(f'Error executing feature {feature_id}: {str(e)}')
            return self.handle_error(e)

        # Handle response.
        logger.debug(f'Feature {feature_id} executed successfully, handling response.')
        return self.handle_response(request)

# ** context: app_context (obsolete)
class AppContext(AppManagerContext):
    '''
    The AppContext is an obsolete class that extends the AppManagerContext.
    It is kept for backward compatibility but should not be used in new code.
    '''

    # * init
    def __init__(self, settings: Dict[str, Any] = {}, app_service: AppService = AppHandler()):
        super().__init__(settings, app_service)
