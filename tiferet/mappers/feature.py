"""Tiferet Feature Mappers"""

# *** imports

# ** core
from typing import Dict, Any, List

# ** app
from ..domain import (
    Feature,
    FeatureCommand,
    ListType,
    ModelType,
    DictType,
    StringType,
)
from ..events import RaiseError, a
from .settings import (
    Aggregate,
    TransferObject,
)

# *** mappers

# ** mapper: feature_command_aggregate
class FeatureCommandAggregate(FeatureCommand, Aggregate):
    '''
    An aggregate representation of a feature command.
    '''

    # * method: new
    @staticmethod
    def new(
        validate: bool = True,
        strict: bool = True,
        **kwargs
    ) -> 'FeatureCommandAggregate':
        '''
        Initializes a new feature command aggregate.

        :param validate: True to validate the aggregate object.
        :type validate: bool
        :param strict: True to enforce strict mode for the aggregate object.
        :type strict: bool
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new feature command aggregate.
        :rtype: FeatureCommandAggregate
        '''

        # Create a new feature command aggregate from the provided data.
        return Aggregate.new(
            FeatureCommandAggregate,
            validate=validate,
            strict=strict,
            **kwargs
        )

    # * method: set_pass_on_error
    def set_pass_on_error(self, value: Any) -> None:
        '''
        Set the ``pass_on_error`` flag based on a provided value.

        :param value: The value to interpret as a boolean.
        :type value: Any
        :return: None
        :rtype: None
        '''

        # Normalize the value, treating the string "false" (case-insensitive)
        # as an explicit False value and using standard bool conversion otherwise.
        if isinstance(value, str) and value.lower() == 'false':
            self.pass_on_error = False
        else:
            self.pass_on_error = bool(value)

    # * method: set_parameters
    def set_parameters(self, parameters: Dict[str, Any] | None = None) -> None:
        '''
        Merge new parameters into the existing parameters, preferring new
        values and removing keys with ``None`` values.

        :param parameters: The new parameters to merge.
        :type parameters: dict | None
        :return: None
        :rtype: None
        '''

        # Do nothing if no parameters were provided.
        if parameters is None:
            return

        # Start from the existing parameters and update with new values.
        merged = dict(self.parameters or {})
        merged.update(parameters)

        # Remove any keys whose value is None.
        self.parameters = {k: v for k, v in merged.items() if v is not None}

    # * method: set_attribute
    def set_attribute(self, attribute: str, value: Any) -> None:
        '''
        Set an attribute on the feature command, with special handling for
        ``parameters`` and ``pass_on_error``.

        :param attribute: The attribute name to set.
        :type attribute: str
        :param value: The value to apply to the attribute.
        :type value: Any
        :return: None
        :rtype: None
        '''

        # Delegate to specialized helpers for parameters and pass_on_error.
        if attribute == 'parameters':
            self.set_parameters(value)
        elif attribute == 'pass_on_error':
            self.set_pass_on_error(value)
        else:
            setattr(self, attribute, value)


# ** mapper: feature_command_yaml_object
class FeatureCommandYamlObject(FeatureCommand, TransferObject):
    '''
    A YAML data representation of a feature command object.
    '''

    class Options():
        '''
        The options for the feature command data.
        '''

        serialize_when_none = False
        roles = {
            'to_model': TransferObject.deny(),
            'to_data.yaml': TransferObject.deny(),
            'to_data.json': TransferObject.deny()
        }

    # * attribute: parameters
    parameters = DictType(
        StringType(),
        default={},
        serialized_name='params',
        deserialize_from=['params', 'parameters'],
        metadata=dict(
            description='The parameters for the feature.'
        )
    )

    # * method: map
    def map(self, **kwargs) -> FeatureCommand:
        '''
        Maps the feature command data to a feature command object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new feature command object.
        :rtype: FeatureCommand
        '''

        # Map to the feature command object.
        return super().map(
            FeatureCommand,
            parameters=self.parameters,
            **self.to_primitive('to_model'),
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(feature_command: FeatureCommand, **kwargs) -> 'FeatureCommandYamlObject':
        '''
        Creates a FeatureCommandYamlObject from a FeatureCommand model.

        :param feature_command: The feature command model.
        :type feature_command: FeatureCommand
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FeatureCommandYamlObject.
        :rtype: FeatureCommandYamlObject
        '''

        # Create a new FeatureCommandYamlObject from the model.
        return TransferObject.from_model(
            FeatureCommandYamlObject,
            feature_command,
            **kwargs,
        )

# ** mapper: feature_aggregate
class FeatureAggregate(Feature, Aggregate):
    '''
    An aggregate representation of a feature.
    '''

    # * method: new
    @staticmethod
    def new(
        name: str = None,
        group_id: str = None,
        feature_key: str = None,
        id: str = None,
        description: str = None,
        validate: bool = True,
        strict: bool = True,
        **kwargs
    ) -> 'FeatureAggregate':
        '''
        Initializes a new feature aggregate.

        :param name: The name of the feature.
        :type name: str
        :param group_id: The context group identifier of the feature.
        :type group_id: str
        :param feature_key: The key of the feature.
        :type feature_key: str
        :param id: The identifier of the feature.
        :type id: str
        :param description: The description of the feature.
        :type description: str
        :param validate: True to validate the aggregate object.
        :type validate: bool
        :param strict: True to enforce strict mode for the aggregate object.
        :type strict: bool
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new feature aggregate.
        :rtype: FeatureAggregate
        '''

        # Derive group_id and feature_key from id if provided.
        if id and '.' in id and (not group_id or not feature_key):
            group_id, feature_key = id.split('.', 1)

        # Set the feature key as the snake case of the name if not provided.
        if name and not feature_key:
            feature_key = name.lower().replace(' ', '_')

        # Feature ID is the group ID and feature key separated by a period.
        if not id and group_id and feature_key:
            id = f'{group_id}.{feature_key}'

        # Set the description as the name if not provided.
        if name and not description:
            description = name

        # Create a new feature aggregate from the provided data.
        return Aggregate.new(
            FeatureAggregate,
            validate=validate,
            strict=strict,
            id=id,
            name=name,
            group_id=group_id,
            feature_key=feature_key,
            description=description,
            **kwargs
        )

    # * method: add_command
    def add_command(
        self,
        name: str,
        attribute_id: str,
        parameters: Dict[str, Any] | None = None,
        data_key: str | None = None,
        pass_on_error: bool = False,
        position: int | None = None,
    ) -> FeatureCommand:
        '''
        Add a feature command using raw attributes.

        :param name: Command name.
        :type name: str
        :param attribute_id: Container attribute ID.
        :type attribute_id: str
        :param parameters: Optional parameters dictionary.
        :type parameters: dict | None
        :param data_key: Optional result data key.
        :type data_key: str | None
        :param pass_on_error: Whether to pass on errors from this command.
        :type pass_on_error: bool
        :param position: Insertion position (None to append).
        :type position: int | None
        :return: Created FeatureCommand instance.
        :rtype: FeatureCommand
        '''

        # Create the feature command from raw attributes.
        from ..domain import DomainObject
        command = DomainObject.new(
            FeatureCommand,
            name=name,
            attribute_id=attribute_id,
            parameters=parameters or {},
            data_key=data_key,
            pass_on_error=pass_on_error,
        )

        # Add the feature command to the feature.
        if position is not None:
            self.commands.insert(position, command)
        else:
            self.commands.append(command)

        return command

    # * method: get_command
    def get_command(self, position: int) -> FeatureCommand | None:
        '''
        Get the feature command at the given position, or ``None`` if the
        index is out of range or invalid.

        :param position: The index of the command to retrieve.
        :type position: int
        :return: The FeatureCommand at the position, or None.
        :rtype: FeatureCommand | None
        '''

        # Attempt to retrieve the command at the specified index.
        try:
            return self.commands[position]
        except (IndexError, TypeError):
            return None

    # * method: remove_command
    def remove_command(self, position: int) -> FeatureCommand | None:
        '''
        Remove and return the feature command at the given position, or
        return ``None`` if the index is out of range or invalid.

        :param position: The index of the feature command to remove.
        :type position: int
        :return: The removed feature command or ``None``.
        :rtype: FeatureCommand | None
        '''

        # Validate the position argument.
        if not isinstance(position, int) or position < 0:
            return None

        # Attempt to remove and return the command at the specified index.
        try:
            return self.commands.pop(position)
        except IndexError:
            return None

    # * method: reorder_command
    def reorder_command(self, current_position: int, new_position: int) -> FeatureCommand | None:
        '''
        Move a feature command from its current position to a new position
        within the ``commands`` list.

        :param current_position: Current index of the command.
        :type current_position: int
        :param new_position: Desired new index.
        :type new_position: int
        :return: Moved command or ``None`` if ``current_position`` is invalid.
        :rtype: FeatureCommand | None
        '''

        # Attempt to remove the command at the current position.
        try:
            command = self.commands.pop(current_position)
        except (IndexError, TypeError):
            return None

        # Clamp the new position index to the valid range.
        if new_position < 0:
            new_position = 0
        if new_position > len(self.commands):
            new_position = len(self.commands)

        # Insert the command at the clamped position and return it.
        self.commands.insert(new_position, command)

        return command

    # * method: rename
    def rename(self, name: str) -> None:
        '''
        Update the display name of the feature.

        :param name: The new name.
        :type name: str
        :return: None
        :rtype: None
        '''

        self.name = name

        # Perform final aggregate validation.
        self.validate()

    # * method: set_description
    def set_description(self, description: str | None) -> None:
        '''
        Update the feature description.

        :param description: The new description.
        :type description: str | None
        :return: None
        :rtype: None
        '''

        self.description = description


# ** mapper: feature_yaml_object
class FeatureYamlObject(Feature, TransferObject):
    '''
    A YAML data representation of a feature object.
    '''

    class Options():
        '''
        The options for the feature data.
        '''

        serialize_when_none = False
        roles = {
            'to_model': TransferObject.deny('commands'),
            'to_data.yaml': TransferObject.deny('feature_key', 'group_id', 'id'),
            'to_data.json': TransferObject.deny('feature_key', 'group_id', 'id')
        }

    # * attribute: commands
    commands = ListType(
        ModelType(FeatureCommandYamlObject),
        deserialize_from=['handlers', 'functions', 'commands'],
        default=[],
    )

    # * method: map
    def map(self, **kwargs) -> FeatureAggregate:
        '''
        Maps the feature data to a feature aggregate.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new feature aggregate.
        :rtype: FeatureAggregate
        '''

        # Map the feature data.
        return super().map(
            FeatureAggregate,
            commands=[command.map() for command in (self.commands or [])],
            **self.to_primitive('to_model'),
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(feature: Feature, **kwargs) -> 'FeatureYamlObject':
        '''
        Creates a FeatureYamlObject from a Feature model.

        :param feature: The feature model.
        :type feature: Feature
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FeatureYamlObject.
        :rtype: FeatureYamlObject
        '''

        # Create a new FeatureYamlObject from the model, converting
        # the commands list into FeatureCommandYamlObject instances.
        return TransferObject.from_model(
            FeatureYamlObject,
            feature,
            commands=[
                TransferObject.from_model(FeatureCommandYamlObject, cmd)
                for cmd in feature.commands
            ],
            **kwargs,
        )
