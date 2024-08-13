from ..repositories.cli import CliInterfaceRepository
from ..objects.cli import CliInterface
from ..objects.cli import CliCommand
from ..objects.cli import CliArgument


class AddCliCommand(object):

    def __init__(self, cli_interface_repo: CliInterfaceRepository):
        self.cli_interface_repo = cli_interface_repo

    def execute(self, interface_id: str, **kwargs):

        # Get CLI interface using the interface ID.
        cli_interface: CliInterface = self.cli_interface_repo.get(interface_id)

        # Assert that the CLI interface exists.
        assert cli_interface is not None, f'CLI_INTERFACE_NOT_FOUND: {interface_id}'

        # Create the new CLI command.
        command = CliCommand.new(
            **kwargs
        )

        # Assert that the feature does not already exist.
        assert not cli_interface.get_command(
            command.feature_id), f'CLI_COMMAND_ALREADY_EXISTS: {command.feature_id}'

        # Add the command to the CLI interface.
        cli_interface.add_command(command)

        # Save the CLI interface.
        self.cli_interface_repo.save(cli_interface)

        # Return the new command.
        return command


class AddCliArgument(object):

    def __init__(self, cli_interface_repo: CliInterfaceRepository):
        self.cli_interface_repo = cli_interface_repo

    def execute(self, interface_id: str, name: str, help: str, arg_type: str, feature_id: str = None, **kwargs):
        '''
        Execute the command to add a new CLI argument to a CLI interface.

        :param interface_id: The ID of the CLI interface.
        :type interface_id: str
        :param name: The name of the CLI argument.
        :type name: str
        :param help: The help text for the CLI argument.
        :type help: str
        :param arg_type: The type of CLI argument.
        :type arg_type: str
        :param feature_id: The feature ID if the CLI argument is to be added to a CLI command.
        :type feature_id: str
        '''

        # Get CLI interface using the interface ID.
        cli_interface: CliInterface = self.cli_interface_repo.get(interface_id)

        # Assert that the CLI interface exists.
        assert cli_interface is not None, f'CLI_INTERFACE_NOT_FOUND: {interface_id}'

        # Create the new CLI argument.
        argument = CliArgument.new(
            name=name,
            help=help,
            **kwargs
        )

        # Set the argument to the CLI interface.
        cli_interface.set_argument(
            argument=argument,
            arg_type=arg_type,
            feature_id=feature_id)

        # Save the CLI interface.
        self.cli_interface_repo.save(cli_interface)

        # Return the new argument.
        return argument
