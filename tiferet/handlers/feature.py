# *** imports

# ** app
from ..commands import *
from ..contracts.feature import *


# *** handlers

# ** handler: feature_handler
class FeatureHandler(FeatureService):
    '''
    Feature handler for executing feature requests.
    '''

    # * attribute: feature_repo
    feature_repo: FeatureRepository

    # * method: __init__
    def __init__(self, feature_repo: FeatureRepository):
        '''
        Initialize the feature handler.

        :param feature_repo: The feature repository to use for retrieving features.
        :type feature_repo: FeatureRepository
        '''

        # Assign the feature repository.
        self.feature_repo = feature_repo

    # * method: parse_parameter
    def parse_parameter(self, parameter: str, request: Request = None) -> str:
        '''
        Parse a parameter.

        
        :param parameter: The parameter to parse.
        :type parameter: str:
        param request: The request object containing data for parameter parsing.
        :type request: Request
        :return: The parsed parameter.
        :rtype: str
        '''

        # Parse the parameter if it not a request parameter.
        if not parameter.startswith('$r.'):
            return parse_parameter.execute(parameter)
        
        # Raise an error if the request is and the parameter comes from the request.
        if not request and parameter.startswith('$r.'):
            raise_error.execute(
                'REQUEST_NOT_FOUND',
                'Request data is not available for parameter parsing.',
                parameter
            )
    
        # Parse the parameter from the request if provided.
        result = request.data.get(parameter[3:], None)
        
        # Raise an error if the parameter is not found in the request data.
        if result is None:
            raise_error.execute(
                'PARAMETER_NOT_FOUND',
                f'Parameter {parameter} not found in request data.',
                parameter
            )

        # Return the parsed parameter.
        return result

    # * method: get_feature
    def get_feature(self, feature_id: str) -> Feature:
        '''
        Get a feature by its ID.

        :param feature_id: The ID of the feature to retrieve.
        :type feature_id: str
        :return: The feature model contract.
        :rtype: Feature
        '''

        # Retrieve the feature from the repository.
        feature = self.feature_repo.get(feature_id)

        # Verify the feature is not None.
        if not feature:
            raise_error.execute(
                'FEATURE_NOT_FOUND',
                f'Feature not found: {feature_id}',
                feature_id
            )

        # Return the feature.
        return feature