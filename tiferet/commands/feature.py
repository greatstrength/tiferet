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
    FEATURE_COMMAND_NOT_FOUND_ID,
    INVALID_FEATURE_COMMAND_ATTRIBUTE_ID,
    COMMAND_PARAMETER_REQUIRED_ID,
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


# ** command: remove_feature
class RemoveFeature(Command):
    '''
    Command to remove an entire feature configuration by ID (idempotent).

    This command delegates deletion semantics to the underlying
    ``FeatureService.delete`` implementation, which is expected to behave
    idempotently when the feature does not exist.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the RemoveFeature command.

        :param feature_service: The feature service to use.
        :type feature_service: FeatureService
        '''

        # Set the feature service dependency.
        self.feature_service = feature_service

    # * method: execute
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a feature by ID.

        :param id: The feature ID.
        :type id: str
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The removed feature ID.
        :rtype: str
        '''

        # Validate required id.
        self.verify_parameter(id, 'id', self.__class__.__name__)

        # Delete the feature using the feature service. Deletion is idempotent
        # and treated as a successful no-op when the feature does not exist.
        self.feature_service.delete(id)

        # Return the feature identifier.
        return id


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

# ** command: update_feature_command
class UpdateFeatureCommand(Command):
    '''
    Command to update an existing ``FeatureCommand`` within a feature's
    command workflow.

    This command supports updating the following attributes on a
    ``FeatureCommand`` instance: ``name``, ``attribute_id``, ``data_key``,
    ``pass_on_error``, and ``parameters``.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * init
    def __init__(self, feature_service: FeatureService) -> None:
        '''
        Initialize the UpdateFeatureCommand command.

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
            position: int,
            attribute: str,
            value: Any | None = None,
            **kwargs,
        ) -> str:
        '''
        Update an attribute on a feature command at the given position.

        :param id: The identifier of the feature whose command will be
            updated.
        :type id: str
        :param position: The zero-based index of the command within the
            feature's command list.
        :type position: int
        :param attribute: The attribute to update. Supported values are
            ``"name"``, ``"attribute_id"``, ``"data_key"``,
            ``"pass_on_error"``, and ``"parameters"``.
        :type attribute: str
        :param value: The new value for the attribute. For ``name`` and
            ``attribute_id`` this must be a non-empty value.
        :type value: Any | None
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The feature identifier.
        :rtype: str
        '''

        # Validate required parameters.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )
        self.verify_parameter(
            parameter=position,
            parameter_name='position',
            command_name=self.__class__.__name__,
        )
        self.verify_parameter(
            parameter=attribute,
            parameter_name='attribute',
            command_name=self.__class__.__name__,
        )

        # Validate that the attribute name is supported.
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
            message=(
                'Invalid feature command attribute: {attribute}. '
                'Supported attributes are name, attribute_id, data_key, '
                'pass_on_error, and parameters.'
            ),
            attribute=attribute,
        )

        # For name and attribute_id, enforce a non-empty value.
        if attribute in {'name', 'attribute_id'}:
            self.verify(
                expression=(
                    value is not None
                    and (not isinstance(value, str) or bool(str(value).strip()))
                ),
                error_code=COMMAND_PARAMETER_REQUIRED_ID,
                message=(
                    f'The "value" parameter is required when updating the '
                    f'"{attribute}" attribute for the '
                    f'"{self.__class__.__name__}" command.'
                ),
                parameter='value',
                command=self.__class__.__name__,
            )

        # Retrieve the feature from the feature service.
        feature = self.feature_service.get(id)

        # Verify that the feature exists.
        self.verify(
            expression=feature is not None,
            error_code=FEATURE_NOT_FOUND_ID,
            feature_id=id,
        )

        # Retrieve the target command from the feature.
        command = feature.get_command(position)

        # Verify that the command exists at the given position.
        self.verify(
            expression=command is not None,
            error_code=FEATURE_COMMAND_NOT_FOUND_ID,
            message=(
                f'Feature command not found for feature {id} '
                f'at position {position}.'
            ),
            feature_id=id,
            position=position,
        )

        # Apply the attribute update using the FeatureCommand helper.
        command.set_attribute(attribute, value)

        # Persist the updated feature.
        self.feature_service.save(feature)

        # Return the feature identifier.
        return id

# ** command: remove_feature_command
class RemoveFeatureCommand(Command):
    '''
    Command to remove a command from an existing feature by position.

    This command is idempotent: invalid positions result in silent success
    with no mutation to the feature's command list.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * init
    def __init__(self, feature_service: FeatureService) -> None:
        '''
        Initialize the RemoveFeatureCommand command.

        :param feature_service: The feature service to use for retrieving and
            persisting features.
        :type feature_service: FeatureService
        '''

        # Set the feature service dependency.
        self.feature_service = feature_service

    # * method: execute
    def execute(
            self,
            id: str,
            position: int,
            **kwargs,
        ) -> str:
        '''
        Remove a command from the feature at the given position.

        :param id: The feature identifier.
        :type id: str
        :param position: The index of the command to remove.
        :type position: int
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The feature identifier.
        :rtype: str
        '''

        # Validate required parameters.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )
        self.verify_parameter(
            parameter=position,
            parameter_name='position',
            command_name=self.__class__.__name__,
        )

        # Retrieve the feature from the feature service.
        feature = self.feature_service.get(id)

        # Verify that the feature exists.
        self.verify(
            expression=feature is not None,
            error_code=FEATURE_NOT_FOUND_ID,
            message=f'Feature not found: {id}',
            feature_id=id,
        )

        # Attempt safe removal of the command at the given position. The
        # underlying Feature.remove_command helper is idempotent and will
        # return None without raising if the position is invalid.
        feature.remove_command(position)

        # Persist the feature, even if no command was removed.
        self.feature_service.save(feature)

        # Return the feature identifier.
        return id


# ** command: reorder_feature_command
class ReorderFeatureCommand(Command):
    '''
    Command to reorder an existing feature command within a feature's
    command workflow.

    This command delegates to the ``Feature.reorder_command`` model helper,
    which clamps the target position and behaves idempotently for invalid
    start positions.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * init
    def __init__(self, feature_service: FeatureService) -> None:
        '''
        Initialize the ReorderFeatureCommand command.

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
            start_position: int,
            end_position: int,
            **kwargs,
        ) -> str:
        '''
        Reorder a feature command by moving it from ``start_position`` to
        ``end_position`` within the feature's command list.

        :param id: The identifier of the feature whose command will be
            reordered.
        :type id: str
        :param start_position: The current index of the command to move.
        :type start_position: int
        :param end_position: The desired new index for the command.
        :type end_position: int
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The feature identifier.
        :rtype: str
        '''

        # Validate required parameters.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )
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

        # Retrieve the feature from the feature service.
        feature = self.feature_service.get(id)

        # Verify that the feature exists.
        self.verify(
            expression=feature is not None,
            error_code=FEATURE_NOT_FOUND_ID,
            message=f'Feature not found: {id}',
            feature_id=id,
        )

        # Delegate the reordering logic to the Feature model helper. This
        # method clamps ``end_position`` and is idempotent for invalid
        # ``start_position`` values.
        feature.reorder_command(start_position, end_position)

        # Persist the updated feature configuration.
        self.feature_service.save(feature)

        # Return the feature identifier.
        return id
