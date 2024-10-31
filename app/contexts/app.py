#** imports

from typing import Any #*** core

from ..objects.error import Error #*** app
from .request import RequestContext #*** app
from .feature import FeatureContext #*** app
from .error import ErrorContext #*** app

#** contexts

class AppContext(): #*** context: app_context

    name: str
    features: FeatureContext
    errors: ErrorContext
    lang: str = 'en_US'

    def __init__(self, app_name: str, feature_context: FeatureContext, error_context: ErrorContext, app_lang: str = 'en_US'):
        self.name: str = app_name
        self.features: FeatureContext = feature_context
        self.errors: ErrorContext = error_context
        self.lang: str = app_lang

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

    def handle_error(self, error: str, **kwargs) -> str:
        '''
        Handle the error.

        :param error: The error message.
        :type error: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The error message.
        :rtype: str
        '''
        
        # Handle error.
        error: Error = self.errors.handle_error(error, lang=self.lang, **kwargs)
        return error.get_message()
        
    def run(self, **kwargs):
        
        # Parse request.
        request = self.parse_request(**kwargs)

        # Execute feature context and return session.
        self.execute_feature(request, **kwargs)

        # Handle response.
        return self.handle_response(request)
