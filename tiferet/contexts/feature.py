# *** imports

# ** core
from typing import Dict, Any, List

# ** app
from ..configs import *
from ..models.feature import Feature, Request
from ..commands.feature import Command, ParseRequest


# *** contexts

# ** context: feature_context
class FeatureContext(object):
    '''
    The feature context is a class that is used to manage features in the application.
    It provides methods to parse requests, get features, add features, and execute feature requests.
    '''

    # * attribute: features
    features: Dict[str, Feature] = {}

    # * method: init
    def __init__(self, features: List[Feature]):
        '''
        Initialize the feature context.

        :param features: The list of features to initialize the context with.
        :type features: List[Feature]
        '''

        # Map the features to the features dictionary.
        try:
            self.features = {feature.id: feature for feature in features}
        except Exception as e:
            raise TiferetError(
                'FEATURE_CONTEXT_INIT_ERROR',
                f'Error initializing feature context: {str(e)}'
            )

    # * method: parse_request
    def parse_request(
            self,
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
        :return: The request.
        :rtype: Request
        '''

        # Use the command to parse the request.
        return Command.handle(
            ParseRequest,
            data=data,
            headers=headers,
            **kwargs
        )
    
    # * method: get_feature
    def get_feature(self, feature_id: str) -> Feature:
        '''
        Get the feature by ID.

        :param feature_id: The feature ID.
        :type feature_id: str
        :return: The feature object.
        :rtype: Feature
        '''
        
        # Get the feature and throw an error if it does not exist.
        try:
            return self.features[feature_id]
        except KeyError:
            raise TiferetError(
                'FEATURE_NOT_FOUND',
                f'Feature not found: {feature_id}.',
                feature_id
            )

    # * method: add_feature
    def add_feature(self, feature: Feature):
        '''
        Add a feature to the context.

        :param feature: The feature to add.
        :type feature: Feature
        '''

        # Add the feature to the features dictionary.
        self.features[feature.id] = feature

    # * method: execute_feature
    def execute_feature(self, feature_id: str, data: Dict[str, Any], headers: Dict[str, str] = {}, debug: bool = False, **kwargs) -> Any:
        '''
        Execute the feature request.
        
        :param request: The request context object.
        :type request: Request
        :param debug: Debug flag.
        :type debug: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of the feature execution.
        :rtype: Any
        '''

        # Get the feature by ID.
        request: Request = self.parse_request(
            data=data,
            headers=headers,
            **kwargs
        )

        # Get the feature from the context.
        feature: Feature = self.get_feature(feature_id)

        # Execute the feature with the request.
        return feature.execute(
            request=request,
            debug=debug,
            **kwargs
        )
