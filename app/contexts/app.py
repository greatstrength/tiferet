# *** imports

# ** core
from typing import Any 

# ** app
from .request import RequestContext #*** app
from .feature import FeatureContext #*** app
from .error import ErrorContext #*** app


# *** contexts

# ** context: app_interface_context
class AppInterfaceContext(): 

    # * field: name
    name: str

    # * field: features
    features: FeatureContext

    # * field: errors
    errors: ErrorContext

    # * field: lang
    lang: str = 'en_US'

    # * method: init
    def __init__(self, app_name: str, feature_context: FeatureContext, error_context: ErrorContext, app_lang: str = 'en_US'):
        self.name: str = app_name
        self.features: FeatureContext = feature_context
        self.errors: ErrorContext = error_context
        self.lang: str = app_lang

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
        session = self.features.execute(request, **kwargs)

        if session.error:
            return self.handle_error(session.error, **request.headers)
        
        # Set the result of the request.
        request.result = session.result
    
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

    # * method: handle_error
    def handle_error(self, error_message: str, **kwargs) -> str:
        '''
        Handle the error.

        :param error: The error message.
        :type error: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The error message.
        :rtype: str
        '''
        
        # Format error.
        error = self.errors.format_error(error_message, lang=self.lang, **kwargs)

        # Return error.
        return error
    
    # * method: run
    def run(self, **kwargs):
        
        # Parse request.
        request = self.parse_request(**kwargs)

        # Execute feature context and return session.
        self.execute_feature(request, **kwargs)

        # Handle response.
        return self.handle_response(request)
