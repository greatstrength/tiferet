# *** imports

# ** core
from typing import List

# ** app
from .settings import *
from .feature import Request

# *** models

# ** model: cli_request
class CliRequest(Request):
    '''
    Represents a request for a command line command.
    This request is used to identify a specific command in the CLI context.
    '''
    
    # * attribute: command_group
    command_group = StringType(
        required=True,
        metadata=dict(
            description='The group of the command being requested. This is typically used to modularly group commands by functional context in a configuration file.'
        )
    )
    
    # * attribute: command_key
    command_key = StringType(
        required=True,
        metadata=dict(
            description='The unique key of the command being requested. This is typically used to identify the command in a configuration file.'
        )
    )
    
    # * method: to_feature_id
    def to_feature_id(self) -> str:
        '''
        Convert the request to a feature ID.
        :return: The feature ID.
        :rtype: str
        '''
        # Format the feature ID as 'command_group.command_key'.
        return '{}.{}'.format(
            self.command_group.replace('-', '_'),
            self.command_key.replace('-', '_')
        )

# ** model: cli_argument
class CliArgument(ValueObject):
    '''
    Represents a command line argument.
    '''
    
    # * attribute: name_or_flags
    name_or_flags = ListType(
        StringType,
        required=True,
        metadata=dict(
            description='The name or flags of the argument. Can be a single name or multiple flags (e.g., ["-f", "--flag"])'
        )
    )
    
    # * attribute: description
    description = StringType(
        metadata=dict(
            description='A brief description of the argument.'
        )
    )
    
    # * attribute: type
    type = StringType(
        choices=['str', 'int', 'float'],
        default='str',
        metadata=dict(
            description='The type of the argument. Can be "str", "int", or "float". Defaults to "str".'
        )
    )
    
    # * attribute: required
    required = BooleanType(
        metadata=dict(
            description='Whether the argument is required. Defaults to False.'
        )
    )
    
    # * attribute: default
    default = StringType(
        metadata=dict(
            description='The default value of the argument if it is not provided. Only applicable if the argument is not required.'
        )
    )
    
    # * attribute: choices
    choices = ListType(
        StringType,
        metadata=dict(
            description='A list of valid choices for the argument. If provided, the argument must be one of these choices.'
        )
    )
    
    # * attribute: nargs
    nargs = StringType(
        metadata=dict(
            description='The number of arguments that should be consumed. Can be an integer or "?" for optional, "*" for zero or more, or "+" for one or more.'
        )
    )
    
    # * attribute: action
    action = StringType(
        choices=['store', 'store_const', 'store_true', 'store_false', 'append', 'append_const', 'count', 'help', 'version'],
        metadata=dict(
            description='The action to be taken when the argument is encountered.'
        )
    )
    
    # * method: get_type
    def get_type(self) -> str | int | float:
        '''
        Get the type of the argument.
        :return: The type of the argument.
        :rtype: str | int | float
        '''

        # Map the type string to a Python type.
        if self.type == 'str':
            return str
        elif self.type == 'int':
            return int
        elif self.type == 'float':
            return float
        
        # If the type is not recognized, return str as a default.
        else:
            return str

# ** model: cli_command
class CliCommand(Entity):
    '''
    Represents a command line command.
    '''
    
    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the command.'
        )
    )
    
    # * attribute: description
    description = StringType(
        metadata=dict(
            description='A brief description of the command.'
        )
    )
    
    # * attribute: key
    key = StringType(
        required=True,
        metadata=dict(
            description='A unique key for the command, typically used for identification in a configuration file.'
        )
    )
    
    # * attribute: group_key
    group_key = StringType(
        required=True,
        metadata=dict(
            description='A unique key for the group this command belongs to, typically used for modularly grouping commands by functional context in a configuration file.'
        )
    )
    
    # * attribute: arguments
    arguments = ListType(
        ModelType(CliArgument),
        default=[],
        metadata=dict(
            description='A list of arguments for the command.'
        )
    )
    
    # * method: new
    @staticmethod
    def new(group_key: str, key: str, name: str, description: str = None, arguments: List[CliArgument] = []) -> 'CliCommand':
        '''
        Create a new command.
        :param group_key: The group key for the command.
        :type group_key: str
        :param key: The unique key for the command.
        :type key: str
        :param name: The name of the command.
        :type name: str
        :param description: A brief description of the command.
        :type description: str
        :param arguments: A list of arguments for the command.
        :type arguments: List[CliArgument]
        :return: The created command.
        :rtype: CliCommand
        '''

        # Create the command id from the formatted group key and key.
        id = '{}.{}'.format(group_key.replace('-', '_'), key.replace('-', '_'))
        
        # Create and return the command object.
        return ModelObject.new(
            CliCommand,
            id=id,
            group_key=group_key,
            key=key,
            name=name,
            description=description,
            arguments=arguments
        )
    
    # * method: has_argument
    def has_argument(self, flags: List[str]) -> bool:
        '''
        Check if the command has an argument with the given flags.
        :param flags: The flags to check for.
        :type flags: List[str]
        :return: True if the command has the argument, False otherwise.
        :rtype: bool
        '''

        # Loop through the flags and check if any of them match the flags of an existing argument
        for flag in flags:
            if any([argument for argument in self.arguments if flag in argument.name_or_flags]):
                return True
            
        # Return False if no argument was found
        return False
    
    # * method: add_argument
    def add_argument(self, argument: CliArgument):
        '''
        Add an argument to the command.
        :param argument: The argument to add.
        :type argument: CliArgument
        '''

        # Append the argument to the command's arguments list.
        self.arguments.append(argument)