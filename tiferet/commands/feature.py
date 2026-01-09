"""Tiferet Feature Commands"""

# *** imports

# ** core
from typing import List, Any

# ** app
from ..models.feature import (
    Feature,
    FeatureCommand,
)
from ..contracts.feature import FeatureService
from ..assets.constants import (
    FEATURE_NOT_FOUND_ID,
    FEATURE_ALREADY_EXISTS_ID,
    FEATURE_NAME_REQUIRED_ID,
    INVALID_FEATURE_ATTRIBUTE_ID,
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

# ** command: update_feature
class UpdateFeature(Command):
    '''
    Command to update basic metadata of an existing feature.

    Supports updating the ``name`` or ``description`` attributes using the
    Feature model helpers.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * init
    def __init__(self, feature_service: FeatureService) -> None:
        '''
        Initialize the UpdateFeature command.

        :param feature_service: The feature service used to retrieve and
            persist features.
        :type feature_service: FeatureService
        '''

        # Set the feature service dependency.
        self.feature_service = feature_service

    # * method: execute
    def execute(
            self,
            id: str,
            attribute: str,
            value: Any,
            **kwargs,
        ) -> Feature:
        '''
        Update a feature's ``name`` or ``description`` attribute.

        :param id: The identifier of the feature to update.
        :type id: str
        :param attribute: The attribute to update (``"name"`` or
            ``"description"``).
        :type attribute: str
        :param value: The new value for the attribute.
        :type value: Any
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The updated Feature instance.
        :rtype: Feature
        '''

        # Validate required parameters.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )
        self.verify_parameter(
            parameter=attribute,
            parameter_name='attribute',
            command_name=self.__class__.__name__,
        )

        # Validate that the attribute is supported.
        self.verify(
            expression=attribute in ('name', 'description'),
            error_code=INVALID_FEATURE_ATTRIBUTE_ID,
            message=f'Invalid feature attribute: {attribute}',
            attribute=attribute,
        )

        # When updating the name, ensure a non-empty value is provided.
        if attribute == 'name':
            self.verify(
                expression=isinstance(value, str) and bool(value.strip()),
                error_code=FEATURE_NAME_REQUIRED_ID,
                message='A feature name is required when updating the name attribute.',
            )

        # Retrieve the feature from the feature service.
        feature = self.feature_service.get(id)

        # Verify that the feature exists.
        self.verify(
            expression=feature is not None,
            error_code=FEATURE_NOT_FOUND_ID,
            feature_id=id,
        )

        # Apply the requested update using model helpers.
        if attribute == 'name':
            feature.rename(value)
        elif attribute == 'description':
            feature.set_description(value)

        # Persist the updated feature.
        self.feature_service.save(feature)

        # Return the updated feature.
        return feature


# ** command: add_feature_command
class AddFeatureCommand(Command):
    '''
    Command to add a command to an existing feature.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the AddFeatureCommand command.

        :param feature_service: The feature service to use.
        :type feature_service: FeatureService
        '''

        # Set the feature service dependency.
        self.feature_service = feature_service

    # * method: execute
    def execute(
            self,
            id: str,
            name: str,
            attribute_id: str,
            parameters: dict | None = None,
            data_key: str | None = None,
            pass_on_error: bool = False,
            position: int | None = None,
            **kwargs,
        ) -> str:
        '''
        Add a command to an existing feature.

        :param id: The feature ID.
        :type id: str
        :param name: The command name.
        :type name: str
        :param attribute_id: The container attribute ID.
        :type attribute_id: str
        :param parameters: Optional command parameters.
        :type parameters: dict | None
        :param data_key: Optional result data key.
        :type data_key: str | None
        :param pass_on_error: Whether to pass on errors from this command.
        :type pass_on_error: bool
        :param position: Insertion position (None to append).
        :type position: int | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The feature ID.
        :rtype: str
        '''

        # Validate required parameters.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )
        self.verify_parameter(
            parameter=name,
            parameter_name='name',
            command_name=self.__class__.__name__,
        )
        self.verify_parameter(
            parameter=attribute_id,
            parameter_name='attribute_id',
            command_name=self.__class__.__name__,
        )

        # Retrieve the feature from the feature service.
        feature = self.feature_service.get(id)
        self.verify(
            expression=feature is not None,
            error_code=FEATURE_NOT_FOUND_ID,
            message=f'Feature not found: {id}',
            feature_id=id,
        )

        # Add the command using the Feature model helper.
        feature.add_command(
            name=name,
            attribute_id=attribute_id,
            parameters=parameters or {},
            data_key=data_key,
            pass_on_error=pass_on_error,
            position=position,
        )

        # Persist the updated feature.
        self.feature_service.save(feature)

        # Return the feature identifier.
        return id
