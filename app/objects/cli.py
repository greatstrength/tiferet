from typing import List

from schematics import types as t

from . import object as obj


CLI_ARGUMENT_TYPE_COMMAND = 'command'
CLI_ARGUMENT_TYPE_PARENT_ARGUMENT = 'parent_argument'
CLI_ARGUMENT_TYPES = [
    CLI_ARGUMENT_TYPE_COMMAND,
    CLI_ARGUMENT_TYPE_PARENT_ARGUMENT
]
CLI_ARGUMENT_TYPE_DEFAULT = CLI_ARGUMENT_TYPE_COMMAND
CLI_ARGUMENT_DATA_TYPES = [
    'str',
    'int',
    'float'
]
CLI_ARGUMENT_DATA_TYPE_DEFAULT = 'str'


class CliArgument(obj.ValueObject):
    '''
    A Command Line Interface (CLI) argument for use in a CLI command or as a parent argument for a CLI interface.
    '''

    name_or_flags = t.ListType(
        t.StringType,
        required=True,
        default=[],
        metadata=dict(
            description='The name and any optional flags for the CLI argument.'
        )
    )

    help = t.StringType(
        required=True,
        metadata=dict(
            description='The help text for the CLI argument.'
        )
    )

    type = t.StringType(
        choices=CLI_ARGUMENT_DATA_TYPES,
        default=CLI_ARGUMENT_DATA_TYPE_DEFAULT,
        metadata=dict(
            description='The data type of the CLI argument.'
        )
    )

    default = t.StringType(
        metadata=dict(
            description='The default value for the CLI argument.'
        )
    )

    required = t.BooleanType(
        metadata=dict(
            description='True if a value is required for the CLI argument.'
        )
    )

    nargs = t.StringType(
        metadata=dict(
            description='The number of allowed values for the CLI argument.'
        )
    )

    choices = t.ListType(
        t.StringType,
        metadata=dict(
            description='The pre-defined set of values for the CLI argument.'
        )
    )

    action = t.StringType(
        metadata=dict(
            description='The unique action for the CLI argument.'
        )
    )

    to_data = t.BooleanType(
        metadata=dict(
            description='True if the CLI argument should be converted to an object or object list.'
        )
    )

    @staticmethod
    def new(name: str,
            flags: List[str] = [],
            required: bool = False,
            positional: bool = False,
            **kwargs
            ):
        '''
        Initializes a new CliArgument object.

        :param name: The name of the CLI argument.
        :type name: str
        :param flags: The optional flags for the CLI argument.
        :type flags: list
        :param required: True if the CLI argument is required.
        :type required: bool
        :param positional: True if the CLI argument is positional.
        :type positional: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new CliArgument object.
        '''

        # Create a new CliArgument object.
        argument = CliArgument(dict(
            **kwargs
        ), strict=False)

        # Format name.
        name = name.lower().replace('_', '-').replace(' ', '-')

        # If the argument is positional, add the name to the name_or_flags list.
        if positional:
            argument.name_or_flags.append(name)

        # If the argument is not positional, add the name and any optional flags to the name_or_flags list.
        else:

            # Add the name to the name_or_flags list.
            argument.name_or_flags.append('--{}'.format(name))

            # Set the flags to an empty list if it is None.
            flags = flags if flags is not None else []

            # Loop through the flags and add them to the name_or_flags list.
            for flag in flags:
                argument.name_or_flags.append(
                    '-{}'.format(flag.lower().replace('_', '-')))

        # Format required parameter.
        if positional or required == False:
            required = None

        # Set the required parameter.
        argument.required = required

        # Return argument
        return argument

    def get_name(self):
        for name in self.name_or_flags:
            if name.startswith('--'):
                return name.replace('--', '').replace('-', '_')
            elif name.startswith('-') and len(name) == 2:
                continue
            else:
                return name
        return None


class CliCommand(obj.Entity):
    '''
    A Command Line Interface (CLI) command for use in a CLI interface.
    '''

    feature_id = t.StringType(
        required=True,
        metadata=dict(
            description='The feature identifier for the CLI command.'
        )
    )

    name = t.StringType(
        required=True,
        metadata=dict(
            description='The name of the CLI command.'
        )
    )

    group_id = t.StringType(
        required=True,
        metadata=dict(
            description='The context group identifier for the CLI command.'
        )
    )

    help = t.StringType(
        required=True,
        metadata=dict(
            description='The help text for the CLI command.'
        )
    )

    arguments = t.ListType(
        t.ModelType(CliArgument),
        default=[],
        metadata=dict(
            description='The list of CLI arguments for the CLI command.'
        )
    )

    @staticmethod
    def new(group_id: str, command_key: str, **kwargs):
        '''
        Initializes a new CliCommand object.

        :param group_id: The group identifier for the CLI command.
        :type group_id: str
        :param command_key: The key for the CLI command.
        :type command_key: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new CliCommand object
        :rtype: CliCommand
        '''

        # Create the feature ID by combining the group ID and the command key.
        feature_id = f'{group_id}.{command_key}'

        # Create a new CliCommand object.
        command = CliCommand(dict(
            id=feature_id,
            feature_id=feature_id,
            **kwargs
        ), strict=False)

        # Validate and return the new CliCommand object.
        command.validate()
        return command

    def argument_exists(self, flags: List[str]) -> bool:
        '''
        Returns True if an argument exists with the specified flags.

        :param flags: The flags of the argument.
        :type flags: list
        :return: True if an argument exists with the specified flags.
        :rtype: bool
        '''

        # Loop through the flags and check if any of them match the flags of an existing argument
        for flag in flags:
            if any([argument for argument in self.arguments if flag in argument.name_or_flags]):
                return True
        # Return False if no argument was found
        return False

    def add_argument(self, argument: CliArgument) -> None:
        self.arguments.append(argument)


class CliInterface(obj.Entity):
    '''
    A Command Line Interface (CLI) interface for use in a CLI application.
    '''

    commands = t.ListType(
        t.ModelType(CliCommand),
        default=[],
        metadata=dict(
            description='The list of commands for the CLI interface.'
        )
    )

    parent_arguments = t.ListType(
        t.ModelType(CliArgument),
        default=[],
        metadata=dict(
            description='The list of parent arguments used by all CLI commands for the CLI interface.'
        )
    )

    @staticmethod
    def new(**kwargs) -> 'CliInterface':
        '''
        Initializes a new CliInterface object.
        
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new CliInterface object.
        :rtype: CliInterface
        '''

        # Create a new CliInterface object.
        interface = CliInterface(dict(
            **kwargs
        ), strict=False)

        # Validate and return the new CliInterface object.
        interface.validate()
        return interface

    def add_command(self, command: CliCommand) -> None:
        '''
        Adds a command to the CLI interface.
        
        :param command: The command to add to the CLI interface.
        :type command: CliCommand
        '''

        # Add the command to the list of commands.
        self.commands.append(command)

    def get_command(self, feature_id: str, **kwargs) -> CliCommand:
        '''
        Returns the command with the specified feature ID.

        :param feature_id: The feature ID of the command.
        :type feature_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The command with the specified feature ID.
        :rtype: CliCommand
        '''

        # Return the command with the specified feature ID.
        return next((command for command in self.commands if command.feature_id == feature_id), None)

    def has_parent_argument(self, flags: List[str]) -> bool:
        '''
        Returns True if a parent argument exists with the specified flags.
        
        :param flags: The flags of the parent argument.
        :type flags: list
        :return: True if a parent argument exists with the specified flags.
        :rtype: bool
        '''

        # Loop through the flags and check if any of them match the flags of an existing parent argument.
        for flag in flags:
            if any([argument for argument in self.parent_arguments if flag in argument.name_or_flags]):
                return True

        # Return False if no parent argument was found.
        return False

    def add_parent_argument(self, argument: CliArgument) -> None:
        '''
        Adds a parent argument to the CLI interface.

        :param argument: The parent argument to add to the CLI interface.
        :type argument: CliArgument
        '''

        # Add the argument to the list of parent arguments.
        self.parent_arguments.append(argument)

    def set_argument(self, argument: CliArgument, arg_type: str, feature_id: str = None) -> None:
        '''
        Sets a CLI argument to the CLI interface.

        :param argument: The CLI argument to set.
        :type argument: CliArgument
        :param arg_type: The type of CLI argument.
        :type arg_type: str
        :param feature_id: The feature ID if the CLI argument is to be added to a CLI command.
        :type feature_id: str
        '''

        # If the argument is a command...
        if arg_type == CLI_ARGUMENT_TYPE_COMMAND:

            # Assert that the feature ID is not None.
            assert feature_id is not None, 'CLI_ARGUMENT_INVALID_FEATURE_ID'

            # Get the command.
            command = self.get_command(feature_id)

            # Assert that the command exists.
            assert command is not None, 'CLI_COMMAND_NOT_FOUND'

            # Assert that the argument does not already exist.
            assert not command.argument_exists(
                argument.name_or_flags), f'CLI_ARGUMENT_ALREADY_EXISTS: {argument.name_or_flags}'

            # Add the argument to the command.
            command.add_argument(argument)

        # If the argument is a parent argument...
        elif arg_type == CLI_ARGUMENT_TYPE_PARENT_ARGUMENT:

            # Assert that the argument does not already exist.
            assert not self.has_parent_argument(
                argument.name_or_flags), f'CLI_ARGUMENT_ALREADY_EXISTS: {argument.name_or_flags}'

            # Add the argument to the parent arguments.
            self.add_parent_argument(argument)
