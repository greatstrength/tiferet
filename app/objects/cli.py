from typing import List

from schematics import types as t

from . import object as obj


CLI_ARUGUMENT_TYPES = [
    'command',
    'parent_argument'
]
CLI_ARUGUMENT_TYPE_DEFAULT = 'command'
CLI_ARUGUMENT_DATA_TYPES = [
    'str',
    'int',
    'float'
]
CLI_ARUGUMENT_DATA_TYPE_DEFAULT = 'str'


class CliArgument(obj.ValueObject):
    '''A Command Line Interface (CLI) argument for use in a CLI command or as a parent argument in a CLI interface.

    :param name_or_flags: The name and any optional flags for the CLI argument.
    :type name_or_flags: list
    :param help: The help text for the CLI argument.
    :type help: str
    :param type: The type of the CLI argument (command, parent_argument).
    :type type: str
    :param data_type: The data type of the CLI argument.
    :type data_type: str
    :param default: The default value for the CLI argument.
    :type default: str
    :param required: True if the CLI argument is required.
    :type required: bool
    :param nargs: The number of allowed values for the CLI argument.
    :type nargs: str
    :param choices: The choices for the CLI argument value.
    :type choices: list
    :param action: The unique action for the CLI argument.
    :type action: str 
    '''

    name_or_flags = t.ListType(t.StringType, required=True, default=[])
    help = t.StringType(required=True)
    type = t.StringType(choices=CLI_ARUGUMENT_TYPES,
                        default=CLI_ARUGUMENT_TYPE_DEFAULT)
    data_type = t.StringType(
        choices=CLI_ARUGUMENT_DATA_TYPES, default=CLI_ARUGUMENT_DATA_TYPE_DEFAULT)
    default = t.StringType()
    required = t.BooleanType()
    nargs = t.StringType()
    choices = t.ListType(t.StringType)
    action = t.StringType()

    @staticmethod
    def new(name: str,
            help: str,
            type: str = CLI_ARUGUMENT_TYPE_DEFAULT,
            data_type: str = CLI_ARUGUMENT_DATA_TYPE_DEFAULT,
            flags: List[str] = [],
            required: bool = False,
            default: str = None,
            positional: bool = False,
            choices: List[str] = None,
            nargs: str = None,
            action: str = None,
            **kwargs
            ):
        
        '''
        Initializes a new CliArgument object.

        :param name: The name of the CLI argument.
        :type name: str
        :param help: The help text for the CLI argument.
        :type help: str
        :param type: The type of the CLI argument (command, parent_argument).
        :type type: str
        :param data_type: The data type of the CLI argument.
        :type data_type: str
        :param flags: The optional flags for the CLI argument.
        :type flags: list
        :param required: True if the CLI argument is required.
        :type required: bool
        :param default: The default value for the CLI argument.
        :type default: str
        :param positional: True if the CLI argument is positional.
        :type positional: bool
        :param choices: The choices for the CLI argument value.
        :type choices: list
        :param nargs: The number of allowed values for the CLI argument.
        :type nargs: str
        :param action: The unique action for the CLI argument.
        :type action: str
        :return: A new CliArgument object.
        '''

        # Create a new CliArgument object.
        argument = CliArgument()

        # Format name or flags parameter.
        name = name.lower().replace('_', '-')

        # If the argument is positional, add the name to the name_or_flags list.
        if positional:
            argument.name_or_flags.append(name)

        # If the argument is not positional, add the name and any optional flags to the name_or_flags list.
        else:
            argument.name_or_flags.append('--{}'.format(name))
            for flag in flags:
                argument.name_or_flags.append('-{}'.format(flag.lower().replace('_', '-')))

        # Format required parameter.
        if positional or required == False:
            required = None

        # Set argument properties
        argument.help = help
        argument.type = type
        argument.data_type = data_type
        argument.default = default
        argument.required = required
        argument.nargs = nargs
        argument.choices = choices
        argument.action = action

        # Return argument
        return argument

    def exclude(self, *args):
        return {k: v for k, v in self.to_primitive().items() if k not in args}


class CliCommand(obj.Entity):
    feature_id = t.StringType(required=True)
    name = t.StringType(required=True)
    group_id = t.StringType(required=True)
    help = t.StringType(required=True)
    arguments = t.ListType(t.ModelType(CliArgument), default=[])

    @staticmethod
    def new(name: str, command_key: str, group_id: str, help: str, arguments: List[CliArgument] = []):
        feature_id = f'{group_id}.{command_key}'
        command = CliCommand(dict(
            id=feature_id,
            feature_id=feature_id,
            name=name,
            group_id=group_id,
            help=help
        ))
        command.arguments = arguments

        return command

    def argument_exists(self, flags: List[str]):
        # Loop through the flags and check if any of them match the flags of an existing argument
        for flag in flags:
            if any([argument for argument in self.arguments if flag in argument.name_or_flags]):
                return True
        # Return False if no argument was found
        return False

    def add_argument(self, argument: CliArgument) -> None:
        self.arguments.append(argument)


class CliInterface(obj.Entity):
    commands = t.ListType(t.ModelType(CliCommand), default=[])
    parent_arguments = t.ListType(t.ModelType(CliArgument), default=[])

    @staticmethod
    def new(id: str, commands: List[CliCommand] = [], parent_arguments: List[CliArgument] = []):
        interface = CliInterface()
        interface.commands = commands
        interface.parent_arguments = parent_arguments

        return interface

    def add_command(self, command: CliCommand) -> None:

        # Add the command to the list of commands.
        self.commands.append(command)

    def add_parent_argument(self, argument: CliArgument) -> None:
        self.parent_arguments.append(argument)

    def get_command(self, feature_id: str) -> CliCommand:
        return next((command for command in self.commands if command.feature_id == feature_id), None)

    def command_exists(self, feature_id: str) -> bool:

        # Return True if the command exists.
        return any((command for command in self.commands if command.feature_id == feature_id))
