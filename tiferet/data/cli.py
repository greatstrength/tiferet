"""Tiferet CLI Data Objects"""

# *** imports

# ** app
from ..models import (
    CliCommand,
    CliArgument,
    ModelObject,
    StringType,
    ListType,
    ModelType,
)
from ..contracts import (
    CliCommandContract
)
from .settings import (
    DataObject,
)

# *** data

# ** data: cli_command_config_data
class CliCommandConfigData(CliCommand, DataObject):
    '''
    Represents the YAML data for a CLI command.
    '''

    class Options():
        '''
        Options for the data object.
        '''

        serialize_when_none = False
        roles = {
            'to_model': DataObject.deny('arguments'),
            'to_data.yaml': DataObject.deny('id', 'arguments'),
            'to_data.json': DataObject.deny('id', 'arguments', 'key', 'group_key'),
        }

    # * class: cli_argument_config_data
    class CliArgumentConfigData(CliArgument, DataObject):
        '''
        Represents the YAML data for a CLI argument.
        '''

        pass

    # * attribute: id
    id = StringType(
        metadata=dict(
            description='The unique identifier for the command.'
        )
    )

    # * attribute: arguments
    arguments = ListType(
        ModelType(CliArgumentConfigData),
        serialized_name='args',
        deserialize_from=['args', 'arguments'],
        default=[],
        metadata=dict(
            description='A list of arguments for the command.'
        )
    )

    # * method: to_primitive
    def to_primitive(self, role: str, **kwargs) -> dict:
        '''
        Converts the data object to a primitive dictionary.

        :param role: The role.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The primitive dictionary.
        :rtype: dict
        '''

        # Convert the data object to a primitive dictionary.
        if 'to_data' in role:
            return dict(
                **super().to_primitive(
                    role,
                    **kwargs
                ),
                args=[arg.to_primitive() for arg in self.arguments]
            )

        # Convert the data object to a model dictionary.
        elif role == 'to_model':
            return dict(
                **super().to_primitive(
                    role,
                    **kwargs
                ),
                arguments=[arg.to_primitive() for arg in self.arguments]
            )

    # * method: map
    def map(self, role: str = 'to_model', **kwargs) -> CliCommandContract:
        '''
        Maps the YAML data to a CLI command object.

        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new CLI command object.
        :rtype: CliCommand
        '''
        # Map the data to a CLI command object.
        return ModelObject.new(
            CliCommand,
            **self.to_primitive(role)
        )