from ..repositories.cli import CliInterfaceRepository
from ..objects.cli import CliInterface
from ..objects.cli import CliCommand


class AddCliCommand(object):

    def __init__(self, cli_interface_repo: CliInterfaceRepository):
        self.cli_interface_repo = cli_interface_repo

    def execute(self, interface_id: str, feature_id: str, name: str, group_id: str, help: str, **kwargs):

        # Get CLI interface using the interface ID.
        cli_interface: CliInterface = self.cli_interface_repo.get(interface_id)

        # Assert that the CLI interface exists.
        assert cli_interface is not None, f'CLI_INTERFACE_NOT_FOUND: {interface_id}'

        # Assert that the feature does not already exist.
        assert cli_interface.command_exists(
            feature_id), f'FEATURE_ALREADY_EXISTS: {feature_id}'

        # Create the new CLI command.
        command = CliCommand.new(
            id=feature_id, name=name, feature_id=feature_id, group_id=group_id, help=help)
        
        # Add the command to the CLI interface.
        cli_interface.add_command(command)

        # Save the CLI interface.
        self.cli_interface_repo.save(cli_interface)

        # Return the new command.
        return command
