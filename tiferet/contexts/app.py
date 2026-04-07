"""Tiferet App Contexts"""

# *** imports

# ** core
import time
from typing import Dict, Any

# ** app
from ..assets import TiferetError, TiferetAPIError
from .feature import FeatureContext
from .error import ErrorContext
from .logging import LoggingContext
from .request import RequestContext

# *** contexts

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

        # Execute feature context and return session.
        self.features.execute_feature(feature_id, request, **kwargs)

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

        # Get formatted response from ErrorContext.
        formatted_error = self.errors.handle_error(error)

        # Raise the API exception with the formatted payload.
        raise TiferetAPIError(**formatted_error)

    # * method: handle_response
    def handle_response(self, request: RequestContext, **kwargs) -> Any:
        '''
        Handle the response from the request.

        :param request: The request context.
        :type request: RequestContext
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
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

        # Start timing immediately.
        start_time = time.perf_counter()

        # Create the logger for the app interface context.
        logger = self.logging.build_logger()

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

        # Handle response.
        return self.handle_response(request)
