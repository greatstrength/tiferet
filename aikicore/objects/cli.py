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
                flags = ['-{}'.format(flag.replace('_', '-'))
                         for flag in flags]
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


class CliCommand(obj.Entity):
    feature_id = t.StringType(required=True)
    group_id = t.StringType(required=True)
    help = t.StringType(required=True)
    arguments = t.ListType(t.ModelType(CliArgument), default=[])

    @staticmethod
    def new(id: str, feature_id: str, group_id: str, help: str, arguments: List[CliArgument] = []):
        command = CliCommand(
            dict(id=id, feature_id=feature_id, group_id=group_id, help=help))
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
    def new(commands: List[CliCommand] = [], parent_arguments: List[CliArgument] = []):
        interface = CliInterface()
        interface.commands = commands
        interface.parent_arguments = parent_arguments

        return interface

    def add_command(self, command: CliCommand) -> None:
        self.commands[command.id] = command

    def add_parent_argument(self, argument: CliArgument) -> None:
        self.parent_arguments.append(argument)

    def get_command(self, feature_id: str) -> CliCommand:
        return next((command for command in self.commands if command.feature_id == feature_id), None)

    def command_exists(self, feature_id: str) -> bool:
        return any((command for command in self.commands if command.feature_id == feature_id))
