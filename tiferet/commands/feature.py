"""Tiferet Feature Commands"""

# *** imports

# ** core
from typing import List

# ** app
from ..models.feature import (
    Feature,
    FeatureCommand,
)
from ..contracts.feature import FeatureService
from ..assets.constants import (
    FEATURE_NOT_FOUND_ID,
    FEATURE_ALREADY_EXISTS_ID,
)
from .settings import Command


# *** commands

# ** command: add_feature
class AddFeature(Command):
    '''
    Command to add a new feature configuration.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the AddFeature command.

        :param feature_service: The feature service to use for managing feature configurations.
        :type feature_service: FeatureService
        '''

        # Set the feature service dependency.
        self.feature_service = feature_service

    # * method: execute
    def execute(
            self,
            name: str,
            group_id: str,
            feature_key: str | None = None,
            id: str | None = None,
            description: str | None = None,
            commands: list | None = None,
            log_params: dict | None = None,
            **kwargs,
        ) -> Feature:
        '''
        Add a new feature.

        :param name: Required feature name.
        :type name: str
        :param group_id: Required group identifier.
        :type group_id: str
        :param feature_key: Optional explicit key (defaults to snake_case of name).
        :type feature_key: str | None
        :param id: Optional explicit full ID (defaults to f'{group_id}.{feature_key}').
        :type id: str | None
        :param description: Optional description (defaults to name).
        :type description: str | None
        :param commands: Optional list of initial commands.
        :type commands: list | None
        :param log_params: Optional logging parameters.
        :type log_params: dict | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created Feature model.
        :rtype: Feature
        '''

        # Validate required parameters.
        self.verify_parameter(
            parameter=name,
            parameter_name='name',
            command_name=self.__class__.__name__,
        )
        self.verify_parameter(
            parameter=group_id,
            parameter_name='group_id',
            command_name=self.__class__.__name__,
        )

        # Create feature using the model factory.
        feature = Feature.new(
            name=name,
            group_id=group_id,
            feature_key=feature_key,
            id=id,
            description=description,
            commands=commands or [],
            log_params=log_params or {},
            **kwargs,
        )

        # Check for duplicate feature identifier.
        self.verify(
            expression=not self.feature_service.exists(feature.id),
            error_code=FEATURE_ALREADY_EXISTS_ID,
            message=f'Feature with ID {feature.id} already exists.',
            id=feature.id,
        )

        # Persist the new feature.
        self.feature_service.save(feature)

        # Return the created feature.
        return feature


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

# ** command: list_features
class ListFeatures(Command):
    '''
    Command to list feature configurations.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the ListFeatures command.

        :param feature_service: The feature service to use for listing features.
        :type feature_service: FeatureService
        '''

        # Set the feature service dependency.
        self.feature_service = feature_service

    # * method: execute
    def execute(self, group_id: str | None = None, **kwargs) -> List[Feature]:
        '''
        List features, optionally filtered by group_id.

        :param group_id: Optional group identifier to filter results.
        :type group_id: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: List of Feature models.
        :rtype: List[Feature]
        '''

        # Delegate to the feature service.
        return self.feature_service.list(group_id=group_id)
