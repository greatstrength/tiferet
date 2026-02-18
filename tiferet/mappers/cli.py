"""Tiferet CLI Mappers"""

# *** imports

# ** core
from typing import Dict, Any, List

# ** app
from ..entities import (
    CliCommand,
    CliArgument,
    StringType,
    ListType,
    ModelType,
)
from ..events import RaiseError, a
from .settings import (
    Aggregate,
    TransferObject,
)

# *** mappers

# ** mapper: cli_command_aggregate
class CliCommandAggregate(CliCommand, Aggregate):
    '''
    An aggregate representation of a CLI command.
    '''

    # * method: new
    @staticmethod
    def new(
        cli_command_data: Dict[str, Any],
        validate: bool = True,
        strict: bool = True,
        **kwargs
    ) -> 'CliCommandAggregate':
        '''
        Initializes a new CLI command aggregate.

        :param cli_command_data: The data to create the CLI command aggregate from.
        :type cli_command_data: dict
        :param validate: True to validate the aggregate object.
        :type validate: bool
        :param strict: True to enforce strict mode for the aggregate object.
        :type strict: bool
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new CLI command aggregate.
        :rtype: CliCommandAggregate
        '''

        # Create a new CLI command aggregate from the provided CLI command data.
        return Aggregate.new(
            CliCommandAggregate,
            validate=validate,
            strict=strict,
            **cli_command_data,
            **kwargs
        )

    # * method: add_argument
    def add_argument(self, argument: CliArgument) -> None:
        '''
        Add an argument to the command.

        :param argument: The argument to add.
        :type argument: CliArgument
        :return: None
        :rtype: None
        '''

        # Append the argument to the command's arguments list.
        self.arguments.append(argument)

    # * method: set_attribute
    def set_attribute(self, attribute: str, value: Any) -> None:
        '''
        Update a supported scalar attribute on the CLI command aggregate.

        Supported attributes: name, description, key, group_key.

        :param attribute: The attribute name to update.
        :type attribute: str
        :param value: The new value.
        :type value: Any
        :return: None
        :rtype: None
        '''

        # Define the set of supported attributes.
        supported = {
            'name',
            'description',
            'key',
            'group_key',
        }

        # Validate the attribute name.
        if attribute not in supported:
            RaiseError.execute(
                error_code=a.const.INVALID_MODEL_ATTRIBUTE_ID,
                message='Invalid attribute: {attribute}. Supported attributes are {supported}.',
                attribute=attribute,
                supported=', '.join(sorted(supported)),
            )

        # Apply the update to the attribute.
        setattr(self, attribute, value)

        # Perform final aggregate validation.
        self.validate()


# ** mapper: cli_argument_yaml_object
class CliArgumentYamlObject(CliArgument, TransferObject):
    '''
    A YAML data representation of a CLI argument object.
    '''

    class Options():
        '''
        The options for the CLI argument data.
        '''

        serialize_when_none = False
        roles = {
            'to_model': TransferObject.deny(),
            'to_data.yaml': TransferObject.deny(),
            'to_data.json': TransferObject.deny(),
        }

    # * method: map
    def map(self, **kwargs) -> CliArgument:
        '''
        Maps the CLI argument data to a CLI argument object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new CLI argument object.
        :rtype: CliArgument
        '''

        # Map to the CLI argument object.
        return super().map(
            CliArgument,
            **self.to_primitive('to_model'),
            **kwargs
        )

# ** mapper: cli_command_yaml_object
class CliCommandYamlObject(CliCommand, TransferObject):
    '''
    A YAML data representation of a CLI command object.
    '''

    class Options():
        '''
        The options for the CLI command data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': TransferObject.deny('arguments'),
            'to_data.yaml': TransferObject.deny('id'),
            'to_data.json': TransferObject.deny('id', 'key', 'group_key'),
        }

    # * attribute: arguments
    arguments = ListType(
        ModelType(CliArgumentYamlObject),
        serialized_name='args',
        deserialize_from=['args', 'arguments'],
        default=[],
        metadata=dict(
            description='A list of arguments for the command.'
        )
    )

    # * method: map
    def map(self, **kwargs) -> CliCommandAggregate:
        '''
        Maps the CLI command data to a CLI command aggregate.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new CLI command aggregate.
        :rtype: CliCommandAggregate
        '''

        # Map the CLI command data.
        return super().map(
            CliCommandAggregate,
            arguments=[arg.map() for arg in self.arguments],
            **self.to_primitive('to_model'),
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(cli_command: CliCommand, **kwargs) -> 'CliCommandYamlObject':
        '''
        Creates a CliCommandYamlObject from a CliCommand model.

        :param cli_command: The CLI command model.
        :type cli_command: CliCommand
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new CliCommandYamlObject.
        :rtype: CliCommandYamlObject
        '''

        # Create a new CliCommandYamlObject from the model, converting
        # the arguments list into CliArgumentYamlObject instances.
        return TransferObject.from_model(
            CliCommandYamlObject,
            cli_command,
            arguments=[
                TransferObject.from_model(CliArgumentYamlObject, arg)
                for arg in cli_command.arguments
            ],
            **kwargs,
        )
