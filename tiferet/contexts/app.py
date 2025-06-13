# *** imports

# ** core
from uuid import uuid4

# ** app
from ..configs import *
from ..commands.app import *
from ..models.feature import Request
from ..models.app import *

# ** app - contexts
from .feature import FeatureContext
from .error import ErrorContext, raise_error
from .cache import CacheContext


# *** contexts

# ** context: app_context
class AppContext(object):
    '''
    The application interface context is a class that is used to create and run the application interface.
    '''

    # * attribute: name
    name: str

    # * attribute: features
    features: FeatureContext

    # * attribute: errors
    errors: ErrorContext

    # * attribute: cache
    cache: CacheContext = CacheContext()

    # * method: init
    def __init__(self, app_name: str, feature_context: FeatureContext, error_context: ErrorContext, cache_context: CacheContext = None):
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

        # Set the application name.
        self.name = app_name

        # Set the cache context if provided.
        if cache_context:
            self.cache = cache_context

        # Set the feature and error contexts.
        self.features = feature_context
        self.errors = error_context

    # * method: parse_request
    def parse_request(self,
        feature_id: str,
        data: Dict[str, Any] = {},
        headers: Dict[str, str] = {},
        **kwargs) -> Request:
        '''
        Parse the incoming request.

        :param feature_id: The feature ID.
        :type feature_id: str
        :param data: The data.
        :type data: dict
        :param headers: The headers.
        :type headers: dict
        :return: The request context.
        :rtype: Request
        '''

        # Parse the incoming data type value.
        for key, value in data.items():

            # If if the value is a string, integer, float, or boolean, continue to the next iteration.
            if isinstance(value, (str, int, float, bool)):
                continue

            # If the value is a list, dictionary, convert it to a JSON string.
            elif isinstance(value, (list, dict)):
                data[key] = json.dumps(value)

            # If the value is a model, convert it to a primitive dictionary and then to a JSON string.
            elif isinstance(value, Model):
                data[key] = json.dumps(value.to_primitive())

            # If the value is not a string, integer, float, boolean, list, dictionary, or model, raise an error.
            else:
                raise_error(
                    'REQUEST_DATA_INVALID',
                    key,
                    str(value)
                )
            
        # Add app interface id and name to the headers.
        headers.update(dict(
            feature_id=feature_id,
            app_session_id=str(uuid4()),
            app_name=self.name
        ))

        # Parse request.
        return ModelObject.new(
            Request,
            feature_id=feature_id,
            data=data,
            headers=headers
        )
    
    # * method: execute_feature
    def execute_feature(self, feature_id: str, **kwargs) -> Any:
        '''
        Execute the feature request.

        :param feature_id: The feature ID to execute.
        :type feature_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Parse the request.
        request = self.parse_request(feature_id, **kwargs)

        # Execute feature context.
        self.features.execute_feature(request, cache=self.cache, **kwargs)

        # Handle the response from the request.
        return request.handle_response(**kwargs)

    # * method: handle_error
    def handle_error(self, exception: Exception, **kwargs) -> Any:
        '''
        Handle passed exceptions as an error.

        :param exception: An exception thrown during a feature request.
        :type exception: Exception
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The error data.
        :rtype: Any
        '''
        
        print('Error:', exception)
        return self.errors.handle_error(exception, **kwargs)
