from typing import List

from schematics import types as t

from . import object as obj


CLI_ARUGUMENT_TYPES = [
    'str',
    'int',
    'float'
]

class CliArgument(obj.ValueObject):
    name_or_flags = t.ListType(t.StringType, required=True)
    help = t.StringType(required=True)
    type = t.StringType(choices=CLI_ARUGUMENT_TYPES)
    default = t.StringType()
    required = t.BooleanType()
    nargs = t.StringType()
    choices = t.ListType(t.StringType)
    action = t.StringType()

    @staticmethod
    def new(name: str, help: str, type: str = None, flags: List[str] = [], positional: bool = False, default: str = None, required: bool = False, nargs: str = None, choices: List[str] = None, action: str = None):
        argument = CliArgument()

        # Format name or flags parameter
        name = name.lower().replace('_', '-').replace(' ', '-')
        if not positional:
            name = '--{}'.format(name)
            if flags:
                flags = ['-{}'.format(flag.replace('_', '-')) for flag in flags]
        name_or_flags = []
        name_or_flags.append(name)
        if flags:
            name_or_flags.extend(flags)

        # Format required parameter.
        if positional or required == False:
            required = None

        # Set argument properties
        argument.name_or_flags = name_or_flags
        argument.help = help
        argument.type = type
        argument.default = default
        argument.required = required
        argument.nargs = nargs
        argument.choices = choices
        argument.action = action

        # Return argument
        return argument


class CliCommand(obj.ValueObject):
    feature_id = t.StringType()
    help = t.StringType(required=True)
    arguments = t.ListType(t.ModelType(CliArgument), default=[])

    @staticmethod
    def new(command_key: str, help: str, subcommand_key: str = None, arguments: List[CliArgument] = []):
        command = CliCommand()
        command.help = help
        command.arguments = arguments

        command.id = command_key
        if subcommand_key:
            command.id = '{}.{}'.format(command_key, subcommand_key)

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
    commands = t.ListType(t.ModelType(CliCommand), default={})
    parent_arguments = t.ListType(t.ModelType(CliArgument), default=[])

    def add_command(self, command: CliCommand) -> None:
        self.commands[command.id] = command

    def add_parent_argument(self, argument: CliArgument) -> None:
        self.parent_arguments.append(argument)

    def get_command(self, feature_id: str) -> CliCommand:
        return next((command for command in self.commands.values() if command.feature_id == feature_id), None)

    def command_exists(self, feature_id: str) -> bool:
        return any((command for command in self.commands.values() if command.feature_id == feature_id))
