# *** imports

# ** app
from .settings import *
from ..models.cli import *

# *** data

# ** data: cli_command_yaml_data
class CliCommandYamlData(CliCommand, DataObject):
    '''
    Represents the YAML data for a CLI command.
    '''
    
    class Options():
        '''
        Options for the data object.
        '''

        serialize_when_none = False
        roles = {
            'to_data': DataObject.deny('id', 'arguments'),
            'to_model': DataObject.deny('arguments')
        }
    
    # * attribute: id
    id = StringType(
        metadata=dict(
            description='The unique identifier for the command.'
        )
    )
    
    # * attribute: arguments
    arguments = ListType(
        ModelType(CliArgument),
        serialized_name='args',
        deserialize_from=['args', 'arguments'],
        default=[],
        metadata=dict(
            description='A list of arguments for the command.'
        )
    )
    
    # * method: to_primitive
    def to_primitive(self, role: str = 'to_data', **kwargs) -> dict:
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
        if role == 'to_data':
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
    def map(self, **kwargs) -> CliCommand:
        '''
        Maps the YAML data to a CLI command object.
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new CLI command object.
        :rtype: CliCommand
        '''
        # Map the data to a CLI command object.
        return ModelObject.new(
            CliCommand,
            **self.to_primitive('to_model')
        )