# *** imports

# ** core
from typing import Any 

# ** app
from .request import RequestContext
from .feature import FeatureContext
from .error import ErrorContext


# *** contexts

# ** context: app_interface_context
class AppInterfaceContext(): 

    # * field: name
    name: str

    # * field: features
    features: FeatureContext

    # * field: errors
    errors: ErrorContext

    # * method: init
    def __init__(self, app_name: str, feature_context: FeatureContext, error_context: ErrorContext):
        '''
        Initialize the application interface context.

        :param app_name: The application name.
        :type app_name: str
        :param feature_context: The feature context.
        :type feature_context: FeatureContext
        :param error_context: The error context.
        :type error_context: ErrorContext
        '''

        # Set the context fields.
        self.name: str = app_name
        self.features: FeatureContext = feature_context
        self.errors: ErrorContext = error_context

    # * method: parse_request
    def parse_request(self, request: Any, **kwargs) -> RequestContext:
        '''
        Parse the incoming request.

        :param request: The incoming request.
        :type request: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The request context.
        :rtype: RequestContext
        '''

        # Parse request.
        return request
    
    # * method: execute_feature
    def execute_feature(self, request: RequestContext, **kwargs):
        '''
        Execute the feature context.

        :param request: The request context.
        :type request: RequestContext
        '''

        # Execute feature context and return session.
        self.features.execute(request, **kwargs)
    
    # * method: handle_response
    def handle_response(self, request: RequestContext) -> Any:
        '''
        Handle the response.

        :param request: The request context.
        :type request: RequestContext
        :return: The response.
        :rtype: Any
        '''
        
        # Map response.
        return request.map_response()
    
    # * method: run
    def run(self, **kwargs):
        '''
        Run the application interface.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''
        
        # Parse request.
        request = self.parse_request(**kwargs)

        # Execute feature context and return session.
        # Handle error and return response if triggered.
        has_error, message = self.errors.handle_error(lambda: self.execute_feature(request, **kwargs))

        # Handle error if present.
        if has_error:
            return message

        # Handle response.
        return self.handle_response(request)
