# *** imports

# ** core
from typing import List

# ** app
from .settings import *

# *** models

# ** model: cli_argument
class CliArgument(ValueObject):
    '''
    Represents a command line argument.
    '''

    # * attribute: name
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
        ),
    )

    # * method: new
    @staticmethod
    def new(name: str, help: str, type: str = None, flags: List[str] = [], positional: bool = False, default: str = None, required: bool = False, nargs: str = None, choices: List[str] = None, action: str = None):

        # Format name or flags parameter
        name = name.lower().replace('_', '-').replace(' ', '-')

        # If the argument is not positional, it should be prefixed with '--' and flags should be prefixed with '-'.
        if not positional:
            name = '--{}'.format(name)
            if flags:
                flags = ['-{}'.format(flag.replace('_', '-')) for flag in flags]
        
        # Create the name or flags list.
        name_or_flags = [name]
        if flags:
            name_or_flags.extend(flags)

        # Format required parameter.
        if positional or required == False:
            required = None

        # Create the argument object
        argument = ModelObject.new(
            CliArgument,
            name_or_flags=name_or_flags,
            description=help,
            type=type,
            default=default,
            required=required,
            nargs=nargs,
            choices=choices,
            action=action,
        )

        # Return argument
        return argument
    
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
        id = '{}.{}'.format(group_key, key)

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