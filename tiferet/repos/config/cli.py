"""Tiferet CLI Configuration Repository"""

# *** imports

# ** core
from typing import (
    List,
    Dict,
    Any
)

# ** app
from ...models import ModelObject, CliCommand, CliArgument
from ...contracts import CliRepository, CliCommandContract, CliArgumentContract
from ...data import (
    CliCommandConfigData,
    DataObject
)
from .settings import ConfigurationFileRepository
from ...commands import RaiseError, const

# *** repositories

# ** repo: cli_configuration_repository
class CliConfigurationRepository(CliRepository, ConfigurationFileRepository):
    '''
    YAML-backed repository for CLI configurations (commands, parent arguments).
    '''

    # * attribute: cli_config_file
    cli_config_file: str

    # * attribute: encoding
    encoding: str

    # * init
    def __init__(self, cli_config_file: str, encoding: str = 'utf-8'):
        '''
        Initialize the CLI configuration repository.

        :param cli_config_file: Path to YAML CLI config file
        :type cli_config_file: str
        :param encoding: File encoding (default 'utf-8')
        :type encoding: str
        '''

        # Set the repository attributes.
        self.cli_config_file = cli_config_file
        self.encoding = encoding

    # * method: get_commands
    def get_commands(self) -> List[CliCommandContract]:
        '''
        List all CLI command configurations.

        :return: List of CLI commands
        :rtype: List[CliCommandContract]
        '''

        # Load the CLI commands from the yaml configuration file.
        with self.open_config(self.cli_config_file, mode='r') as config_file:

            # Load all command data from nested cli.cmds structure.
            cmds_data = config_file.load(
                start_node=lambda d: d.get('cli', {}).get('cmds', {}),
                data_factory=lambda d: {
                    f"{group}.{cmd}": DataObject.from_data(
                        CliCommandConfigData,
                        id=f"{group}.{cmd}",
                        **cmd_data
                    ) for group, group_data in d.items() for cmd, cmd_data in group_data.items()
                }
            )

        # Return the mapped command objects.
        return [cmd.map() for cmd in cmds_data.values()]

    # * method: get_command
    def get_command(self, command_id: str) -> CliCommandContract | None:
        '''
        Get a CLI command by its full ID (group.key).

        :param command_id: Command identifier (e.g., 'calc.add')
        :type command_id: str
        :return: CLI command or None if not found
        :rtype: CliCommandContract | None
        '''

        # Split the command ID into group and command keys.
        group_key, command_key = command_id.split('.', 1)

        # Load the command data from the yaml configuration file.
        with self.open_config(self.cli_config_file, mode='r') as config_file:

            # Load the specific command data.
            cmd_data = config_file.load(
                start_node=lambda d: d.get('cli', {}).get('cmds', {}).get(group_key, {}).get(command_key)
            )

        # If no data is found, return None.
        if not cmd_data:
            return None

        # Map the command data to the command object and return it.
        return DataObject.from_data(
            CliCommandConfigData,
            id=command_id,
            **cmd_data
        ).map()

    # * method: get_parent_arguments
    def get_parent_arguments(self) -> List[CliArgumentContract]:
        '''
        Get all parent-level CLI arguments.

        :return: List of parent arguments
        :rtype: List[CliArgumentContract]
        '''

        # Load the parent arguments from the yaml configuration file.
        with self.open_config(self.cli_config_file, mode='r') as config_file:

            # Load and return the parent arguments data.
            return config_file.load(
                start_node=lambda d: d.get('cli', {}).get('parent_args', []),
                data_factory=lambda d: [ModelObject.new(
                    CliArgument,
                    **arg
                ) for arg in d]
            )

    # * method: save_command
    def save_command(self, cli_command: CliCommandContract):
        '''
        Save/update a CLI command configuration.

        :param cli_command: The CLI command to save.
        :type cli_command: CliCommandContract
        '''

        # Create updated command data.
        cmd_data = DataObject.from_model(
            CliCommandConfigData,
            cli_command
        )

        # Split the command ID into group and command keys.
        group_key, command_key = cli_command.id.split('.', 1)

        # Update the command data.
        with self.open_config(self.cli_config_file, mode='w') as config_file:

            # Save the updated command data back to the yaml file.
            config_file.save(
                cmd_data.to_primitive(self.default_role),
                data_path=f'cli.cmds.{group_key}.{command_key}'
            )

    # * method: delete_command
    def delete_command(self, command_id: str):
        '''
        Delete a CLI command by ID (idempotent).

        :param command_id: The command id.
        :type command_id: str
        '''

        # Split the command ID into group and command keys.
        group_key, command_key = command_id.split('.', 1)

        # Retrieve the group data from the yaml file.
        with self.open_config(self.cli_config_file, mode='r') as config_file:

            # Load the group data.
            group_data = config_file.load(
                start_node=lambda d: d.get('cli', {}).get('cmds', {}).get(group_key, {})
            )

        # Pop the command data whether it exists or not.
        group_data.pop(command_key, None)

        # Save the updated group data back to the yaml file.
        with self.open_config(self.cli_config_file, mode='w') as config_file:

            # Save the updated group data.
            config_file.save(
                group_data,
                data_path=f'cli.cmds.{group_key}'
            )

    # * method: save_parent_arguments
    def save_parent_arguments(self, parent_arguments: List[CliArgumentContract]):
        '''
        Save/update parent-level CLI arguments.

        :param parent_arguments: The list of parent arguments to save.
        :type parent_arguments: List[CliArgumentContract]
        '''

        # Save the parent arguments data to the yaml file.
        with self.open_config(self.cli_config_file, mode='w') as config_file:

            # Save the parent arguments data.
            config_file.save(
                [arg.to_primitive() for arg in parent_arguments],
                data_path='cli.parent_args'
            )
