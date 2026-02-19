"""Tiferet CLI Mappers"""

# *** imports

# ** core
from typing import Dict, Any, List

# ** app
from ..entities import (
    CliCommand,
    CliArgument,
    ModelObject,
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
        validate: bool = True,
        strict: bool = True,
        **kwargs
    ) -> 'CliCommandAggregate':
        '''
        Initializes a new CLI command aggregate.

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
            **kwargs
        )

    # * method: add_argument
    def add_argument(self,
            name_or_flags: list,
            description: str = None,
            type: str = None,
            required: bool = None,
            default: str = None,
            choices: list = None,
            nargs: str = None,
            action: str = None
        ) -> None:
        '''
        Add an argument to the command.

        :param name_or_flags: The name or flags of the argument.
        :type name_or_flags: list
        :param description: A brief description of the argument.
        :type description: str
        :param type: The type of the argument (str, int, float).
        :type type: str
        :param required: Whether the argument is required.
        :type required: bool
        :param default: The default value of the argument.
        :type default: str
        :param choices: A list of valid choices for the argument.
        :type choices: list
        :param nargs: The number of arguments to consume.
        :type nargs: str
        :param action: The action to take when the argument is encountered.
        :type action: str
        :return: None
        :rtype: None
        '''

        # Create a new CliArgument instance using ModelObject.new.
        argument = ModelObject.new(
            CliArgument,
            name_or_flags=name_or_flags,
            description=description,
            type=type,
            required=required,
            default=default,
            choices=choices,
            nargs=nargs,
            action=action
        )

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
            'to_data.yaml': TransferObject.deny('id', 'arguments'),
        }

    # * attribute: arguments
    arguments = ListType(
        ModelType(CliArgument),
        default=[],
        deserialize_from=['args', 'arguments'],
        serialized_name='args',
        metadata={
            'description': 'The list of arguments for the CLI command.'
        })

    # * method: to_primitive
    def to_primitive(self, role='to_data.yaml', **kwargs) -> Dict[str, Any]:
        '''
        Converts the CLI command data to a primitive dictionary representation.

        :param role: The role to use for the conversion.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A primitive dictionary representation of the CLI command data.
        :rtype: dict
        '''

        # Convert the CLI command data to a primitive dictionary, converting
        # the arguments list into dictionaries as well.
        return dict(
            **super().to_primitive(role=role, **kwargs),
            args=[
                arg.to_primitive()
                for arg in self.arguments
            ]
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
            arguments=[
                arg.to_primitive()
                for arg in self.arguments
            ],
            **self.to_primitive('to_model'),
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(cli_command: CliCommandAggregate, **kwargs) -> 'CliCommandYamlObject':
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
                arg.to_primitive()
                for arg in cli_command.arguments
            ],
            **kwargs,
        )
