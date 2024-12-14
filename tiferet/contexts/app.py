# *** imports

# ** core
from typing import Any, Tuple

# ** app
from .request import RequestContext
from .feature import FeatureContext
from .error import ErrorContext
from ..domain import *


# *** contexts

# ** context: app_interface_context
class AppInterfaceContext(Model): 
    '''
    The application interface context is a class that is used to create and run the application interface.
    '''

    # * attribute: interface_id
    interface_id = StringType(
        required=True,
        metadata=dict(
            description='The interface ID.'
        ),
    )

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The application name.'
        ),
    )

    # * field: features
    features = ModelType(
        FeatureContext,
        required=True,
        metadata=dict(
            description='The feature context.'
        ),
    )

    # * field: errors
    errors = ModelType(
        ErrorContext,
        required=True,
        metadata=dict(
            description='The error context.'
        ),
    )

    # * method: init
    def __init__(self, interface_id: str, app_name: str, feature_context: FeatureContext, error_context: ErrorContext):
        '''
        Initialize the application interface context.

        :param interface_id: The interface ID.
        :type interface_id: str
        :param app_name: The application name.
        :type app_name: str
        :param feature_context: The feature context.
        :type feature_context: FeatureContext
        :param error_context: The error context.
        :type error_context: ErrorContext
        '''

        # Initialize the model.
        super().__init__(dict(
            interface_id=interface_id,
            name=app_name
        ))
        self.features = feature_context
        self.errors = error_context

    # * method: parse_request
    def parse_request(self, request: Any, **kwargs) -> Tuple[RequestContext, dict]:
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
        return request, kwargs
    
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
        
        # Import the JSON module.
        import json

        # Return the response.
        return json.loads(request.result) if request.result else ''
    
    # * method: run
    def run(self, **kwargs):
        '''
        Run the application interface.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''
        
        # Parse request.
        request, kwargs = self.parse_request(**kwargs)

        # Execute feature context and return session.
        # Handle error and return response if triggered.
        try:
            self.execute_feature(request, **kwargs)
        except Exception as e:
            print('Error:', e)
            return self.errors.handle_error(e)

        # Handle response.
        return self.handle_response(request)
