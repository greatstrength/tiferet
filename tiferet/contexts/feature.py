# *** imports

# ** app
from .container import ContainerContext
from .cache import CacheContext
from .request import RequestContext
from ..models.feature import *
from ..repos.feature import FeatureRepository
from ..handlers.feature import FeatureHandler
from ..commands import parse_parameter, raise_error


# *** contexts

# ** context: feature_context
class FeatureContext(object):

    # * attribute: feature_handler
    feature_handler: FeatureHandler

    # * method: init
    def __init__(self, 
            feature_repo: FeatureRepository = None, 
            container_context: ContainerContext = None, 
            cache: CacheContext = None,
            feature_handler: FeatureHandler = None):
        '''
        Initialize the feature context.

        :param feature_repo: The feature repository.
        :type feature_repo: FeatureRepository
        :param container_context: The container context.
        :type container_context: ContainerContext
        '''

        # Create the feature handler.
        if feature_handler:
            self.feature_handler = feature_handler

        # If the feature handler is not provided, create it from the feature repository and container context.
        elif not feature_repo or not container_context:
            raise_error.execute(
                'FEATURE_CONTEXT_LOADING_FAILED',
                'A feature repository and container context are required to initialize the feature context.')
        
        # Create the feature handler with the provided repository and container context.
        else:  
            self.feature_handler = FeatureHandler(
                feature_repo=feature_repo,
                container_service=container_context,
                cache=cache if cache else CacheContext()
            )

    # * method: parse_parameter (obsolete)
    def parse_parameter(self, parameter: str) -> str:
        '''
        Parse a parameter.

        :param parameter: The parameter to parse.
        :type parameter: str
        :return: The parsed parameter.
        :rtype: str
        '''

        # Parse the parameter.
        return parse_parameter.execute(parameter)
        
    # * method: execute
    def execute(self, request: RequestContext, debug: bool = False, **kwargs):
        '''
        Execute the feature request.
        
        :param request: The request context object.
        :type request: r.RequestContext
        :param debug: Debug flag.
        :type debug: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Convert the request context to a request object.
        # This is necessary to prevent breaking changes for version 1. (warning)
        request_obj: Request = ValueObject.new(
            Request,
            headers=request.headers,
            data=request.data,
        )

        # Get the feature and check if it exists.
        # If it does not exist, raise an error.
        feature = self.feature_handler.get_feature(request.feature_id)

        # Loop through the feature commands and handle them.
        for command in feature.commands:

            # Execute the feature handler.
            self.feature_handler.handle_command(
                feature_command=command,
                request=request_obj,
                debug=debug,
                **kwargs
            )

        # Return the result from the request.
        return request_obj.handle_response() if request_obj.result else None

            
