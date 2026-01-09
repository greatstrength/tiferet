"""Tiferet Feature Commands"""

# *** imports

# ** app
from ..models.feature import (
    Feature,
    FeatureCommand,
)
from ..contracts.feature import FeatureService
from ..assets.constants import FEATURE_NOT_FOUND_ID
from .settings import Command


# *** commands

# ** command: get_feature
class GetFeature(Command):
    '''
    Command to retrieve a feature by its identifier.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the GetFeature command.

        :param feature_service: The feature service to use for retrieving features.
        :type feature_service: FeatureService
        '''

        # Set the feature service dependency.
        self.feature_service = feature_service

    # * method: execute
    def execute(self, id: str, **kwargs) -> Feature:
        '''
        Execute the command to retrieve a feature.

        :param id: The feature identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The retrieved feature.
        :rtype: Feature
        '''

        # Validate the required feature identifier.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )

        # Retrieve the feature from the feature service.
        feature = self.feature_service.get(id)

        # Verify that the feature exists; raise FEATURE_NOT_FOUND if it does not.
        self.verify(
            expression=feature is not None,
            error_code=FEATURE_NOT_FOUND_ID,
            feature_id=id,
        )

        # Return the retrieved feature.
        return feature