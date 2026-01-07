# ** imports

# ** core
from typing import Any

# ** app
from ..models.feature import (
    Feature,
)
from ..contracts.feature import (
    FeatureService,
)
from ..assets.constants import (
    FEATURE_NOT_FOUND_ID,
    FEATURE_NAME_REQUIRED_ID,
    INVALID_FEATURE_ATTRIBUTE_ID,
    FEATURE_COMMAND_NOT_FOUND_ID,
    INVALID_FEATURE_COMMAND_ATTRIBUTE_ID,
    COMMAND_PARAMETER_REQUIRED_ID,
)
from ..assets import TiferetError
from .settings import Command


# *** commands

# ** command: remove_feature
class RemoveFeature(Command):
    '''
    Command to remove a feature configuration by its identifier.

    This operation is idempotent: attempting to remove a feature that does
    not exist will not raise an error.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * method: init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the RemoveFeature command.

        :param feature_service: The feature service used to manage feature
            configurations.
        :type feature_service: FeatureService
        '''

        # Set the feature service.
        self.feature_service = feature_service

    # * method: execute
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a feature by id.

        :param id: The feature identifier.
        :type id: str
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        :return: The identifier of the (attempted) removed feature.
        :rtype: str
        '''

        # Validate the required id parameter.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )

        # Delegate deletion to the feature service. The underlying repository
        # implementation is already effectively idempotent, so we do not need
        # to check for existence or raise an error if the feature is missing.
        self.feature_service.delete(id)

        # Return the id for convenience and consistency with other commands.
        return id


# ** command: get_feature
class GetFeature(Command):
    '''
    Command to retrieve a feature by its identifier.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * method: init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the GetFeature command.

        :param feature_service: The feature service to use for retrieving features.
        :type feature_service: FeatureService
        '''

        # Set the feature service.
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

        # Validate required id using base verify_parameter helper.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )

        # Retrieve the feature via the feature service.
        feature = self.feature_service.get_feature(id)

        # Verify the feature is not None; raise a FEATURE_NOT_FOUND error otherwise.
        if not feature:
            raise TiferetError(
                FEATURE_NOT_FOUND_ID,
                f'Feature not found: {id}',
                feature_id=id,
            )

        return feature


# ** command: add_feature
class AddFeature(Command):
    '''
    Command to add a new feature configuration.

    This command creates a new :class:`Feature` instance using the
    :meth:`Feature.new` factory method, validates the required parameters,
    verifies that the feature does not already exist using the configured
    :class:`FeatureService`, and then persists the new feature.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * method: init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the AddFeature command.

        :param feature_service: The feature service to use for managing
            feature configurations.
        :type feature_service: FeatureService
        '''

        # Set the feature service.
        self.feature_service = feature_service

    # * method: execute
    def execute(
        self,
        name: str,
        group_id: str,
        feature_key: str | None = None,
        id: str | None = None,
        description: str | None = None,
        **kwargs,
    ) -> Feature:
        '''
        Create and persist a new feature configuration.

        :param name: The name of the feature.
        :type name: str
        :param group_id: The context group identifier of the feature.
        :type group_id: str
        :param feature_key: Optional explicit feature key. If not provided,
            the key is derived from the name.
        :type feature_key: str | None
        :param id: Optional explicit feature identifier. If not provided, the
            identifier is computed as ``"{group_id}.{feature_key}"``.
        :type id: str | None
        :param description: Optional description of the feature. Defaults to
            the ``name`` if not provided.
        :type description: str | None
        :param kwargs: Additional keyword arguments passed through to
            :meth:`Feature.new` (for example, commands or log_params).
        :type kwargs: dict
        :return: The newly created feature.
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

        # Create the feature using the domain factory so that the effective id
        # and feature_key are computed consistently.
        feature = Feature.new(
            name=name,
            group_id=group_id,
            feature_key=feature_key,
            id=id,
            description=description,
            **kwargs,
        )

        # Ensure the feature does not already exist.
        exists = self.feature_service.exists(feature.id)
        self.verify(
            expression=exists is False,
            error_code='FEATURE_ALREADY_EXISTS',
            message=f'Feature with ID {feature.id} already exists.',
            id=feature.id,
        )

        # Persist and return the new feature.
        self.feature_service.save(feature)
        return feature

# ** command: list_features
class ListFeatures(Command):
    '''
    Command to list feature configurations.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * method: init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the ListFeatures command.

        :param feature_service: The feature service to use for retrieving
            feature configurations.
        :type feature_service: FeatureService
        '''

        # Set the feature service.
        self.feature_service = feature_service

    # * method: execute
    def execute(self, group_id: str | None = None, **kwargs) -> list[Feature]:
        '''
        List feature configurations.

        :param group_id: Optional group identifier used to filter the
            returned features. If omitted, all features are returned.
        :type group_id: str | None
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        :return: A list of feature configurations.
        :rtype: List[Feature]
        '''

        # List and return the features.
        return self.feature_service.list(group_id)


# ** command: update_feature
class UpdateFeature(Command):
    '''
    Command to update feature information.

    This command supports updating either the ``name`` or ``description``
    attributes of an existing :class:`Feature`.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * method: init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the UpdateFeature command.

        :param feature_service: The feature service to use for retrieving and
            persisting features.
        :type feature_service: FeatureService
        '''

        # Set the feature service.
        self.feature_service = feature_service

    # * method: execute
    def execute(self, id: str, attribute: str, value, **kwargs) -> Feature:
        '''
        Update a feature attribute.

        :param id: The feature identifier.
        :type id: str
        :param attribute: The attribute to update (``name`` or ``description``).
        :type attribute: str
        :param value: The new value for the attribute.
        :type value: Any
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        :return: The updated feature.
        :rtype: Feature
        '''

        # Only the attribute parameter is formally verified here; the id is
        # implicitly validated by ensuring a feature is successfully
        # retrieved.
        self.verify_parameter(
            parameter=attribute,
            parameter_name='attribute',
            command_name=self.__class__.__name__,
        )

        # Retrieve the feature and verify that it exists.
        feature = self.feature_service.get_feature(id)
        self.verify(
            expression=feature is not None,
            error_code=FEATURE_NOT_FOUND_ID,
            message=f'Feature not found: {id}',
            feature_id=id,
        )

        # Validate the attribute using the base verify helper.
        self.verify(
            expression=attribute in {'name', 'description'},
            error_code=INVALID_FEATURE_ATTRIBUTE_ID,
            message=f'Invalid feature attribute: {attribute}',
            attribute=attribute,
        )

        # Apply the update based on the attribute, using verify for name
        # requirements as well.
        if attribute == 'name':
            self.verify(
                expression=value is not None,
                error_code=FEATURE_NAME_REQUIRED_ID,
                message='A feature name is required when updating the name attribute.',
            )
            feature.rename(value)
        elif attribute == 'description':
            feature.set_description(value)

        # Persist and return the updated feature.
        self.feature_service.save(feature)
        return feature

# ** command: add_feature_command
class AddFeatureCommand(Command):
    '''
    Adds a feature handler to a feature.
    '''

    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the command.
        
        :param feature_service: The feature service.
        :type feature_service: FeatureService
        '''

        # Set the feature service.
        self.feature_service = feature_service

    def execute(
        self,
        id: str,
        name: str,
        attribute_id: str,
        parameters: dict | None = None,
        data_key: str | None = None,
        position: int | None = None,
    ) -> str:
        '''
        Execute the command to add a feature handler to a feature.

        :param id: The feature ID.
        :type id: str
        :param name: The name of the feature command.
        :type name: str
        :param attribute_id: The container attribute ID for the feature command.
        :type attribute_id: str
        :param parameters: Optional custom parameters for the feature command.
        :type parameters: dict | None
        :param data_key: Optional data key to store the command result under.
        :type data_key: str | None
        :param position: The position of the handler. If ``None``, the command
            is appended.
        :type position: int | None
        :return: The feature ID.
        :rtype: str
        '''

        # Validate required parameters using the base command helper.
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

        # Get the feature using the feature ID.
        feature = self.feature_service.get(id)

        # Verify that the feature was successfully found.
        self.verify(
            expression=feature is not None,
            error_code=FEATURE_NOT_FOUND_ID,
            message=f'Feature not found: {id}',
            feature_id=id,
        )

        # Add the feature handler to the feature using raw attributes.
        feature.add_command(
            name=name,
            attribute_id=attribute_id,
            parameters=parameters or {},
            data_key=data_key,
            position=position,
        )

        # Save the updated feature and return its identifier.
        self.feature_service.save(feature)
        return id


# ** command: update_feature_command
class UpdateFeatureCommand(Command):
    '''
    Command to update a feature command within an existing feature.
    '''

    feature_service: FeatureService

    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the UpdateFeatureCommand.

        :param feature_service: The feature service to use for retrieving and
            persisting features.
        :type feature_service: FeatureService
        '''

        self.feature_service = feature_service

    def execute(
        self,
        id: str,
        position: int,
        attribute: str,
        value: Any | None = None,
        **kwargs,
    ) -> str:
        '''
        Update a feature command attribute.

        :param id: The feature identifier.
        :type id: str
        :param position: The index of the feature command in the feature's
            commands list.
        :type position: int
        :param attribute: The attribute to update. Must be one of:
            ``name``, ``attribute_id``, ``data_key``, ``pass_on_error``,
            or ``parameters``.
        :type attribute: str
        :param value: The new value for the attribute.
        :type value: Any
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        :return: The feature identifier.
        :rtype: str
        '''

        # Validate the attribute parameter itself.
        self.verify_parameter(
            parameter=attribute,
            parameter_name='attribute',
            command_name=self.__class__.__name__,
        )

        # Retrieve and verify the feature.
        feature = self.feature_service.get(id)
        self.verify(
            expression=feature is not None,
            error_code=FEATURE_NOT_FOUND_ID,
            message=f'Feature not found: {id}',
            feature_id=id,
        )

        # Retrieve and verify the feature command at the requested position.
        command = feature.get_command(position)
        self.verify(
            expression=command is not None,
            error_code=FEATURE_COMMAND_NOT_FOUND_ID,
            message=(
                f'Feature command not found for feature {id} at '
                f'position {position}.'
            ),
            feature_id=id,
            position=position,
        )

        # Validate that the attribute is supported.
        valid_attributes = {
            'name',
            'attribute_id',
            'data_key',
            'pass_on_error',
            'parameters',
        }
        self.verify(
            expression=attribute in valid_attributes,
            error_code=INVALID_FEATURE_COMMAND_ATTRIBUTE_ID,
            message=f'Invalid feature command attribute: {attribute}',
            attribute=attribute,
        )

        # For name and attribute_id, a non-empty value is required.
        if attribute in {'name', 'attribute_id'}:
            self.verify(
                expression=(
                    value is not None
                    and (not isinstance(value, str) or bool(value.strip()))
                ),
                error_code=COMMAND_PARAMETER_REQUIRED_ID,
                message=(
                    f'The "{attribute}" attribute value is required for '
                    f'UpdateFeatureCommand.'
                ),
                parameter=attribute,
                command=self.__class__.__name__,
            )

        # Delegate the actual mutation to the FeatureCommand helper.
        command.set_attribute(attribute, value)

        # Persist the updated feature and return its id.
        self.feature_service.save(feature)
        return id


# ** command: remove_feature_command
class RemoveFeatureCommand(Command):
    '''
    Command to remove a feature command from an existing feature.
    '''

    feature_service: FeatureService

    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the RemoveFeatureCommand.

        :param feature_service: The feature service to use for retrieving and
            persisting features.
        :type feature_service: FeatureService
        '''

        self.feature_service = feature_service

    def execute(self, id: str, position: int, **kwargs) -> str:
        '''
        Remove a feature command at the given position from the feature.

        :param id: The feature identifier.
        :type id: str
        :param position: The index of the feature command to remove.
        :type position: int
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        :return: The feature identifier.
        :rtype: str
        '''

        # Verify that the feature exists.
        feature = self.feature_service.get(id)
        self.verify(
            expression=feature is not None,
            error_code=FEATURE_NOT_FOUND_ID,
            message=f'Feature not found: {id}',
            feature_id=id,
        )

        # Remove the command at the given position (idempotent if out-of-range).
        feature.remove_command(position)

        # Persist the updated feature and return its identifier.
        self.feature_service.save(feature)
        return id


# ** command: reorder_feature_command
class ReorderFeatureCommand(Command):
    '''
    Command to reorder a feature command within an existing feature.
    '''

    feature_service: FeatureService

    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the ReorderFeatureCommand.

        :param feature_service: The feature service to use for retrieving and
            persisting features.
        :type feature_service: FeatureService
        '''

        self.feature_service = feature_service

    def execute(
        self,
        id: str,
        start_position: int,
        end_position: int,
        **kwargs,
    ) -> str:
        '''
        Reorder a feature command from start_position to end_position.

        :param id: The feature identifier.
        :type id: str
        :param start_position: The current index of the feature command.
        :type start_position: int
        :param end_position: The desired index for the feature command.
        :type end_position: int
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        :return: The feature identifier.
        :rtype: str
        '''

        # Verify that required position parameters are present.
        self.verify_parameter(
            parameter=start_position,
            parameter_name='start_position',
            command_name=self.__class__.__name__,
        )
        self.verify_parameter(
            parameter=end_position,
            parameter_name='end_position',
            command_name=self.__class__.__name__,
        )

        # Retrieve and verify the feature.
        feature = self.feature_service.get(id)
        self.verify(
            expression=feature is not None,
            error_code=FEATURE_NOT_FOUND_ID,
            message=f'Feature not found: {id}',
            feature_id=id,
        )

        # Delegate reordering to the model helper. This is effectively
        # idempotent if the start_position is out of range.
        feature.reorder_command(start_position, end_position)

        # Persist the updated feature and return its identifier.
        self.feature_service.save(feature)
        return id
