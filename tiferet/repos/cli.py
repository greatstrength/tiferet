"""Tiferet CLI YAML Repository"""

# *** imports

# ** core
from typing import (
    List,
    Dict,
    Any
)

# ** app
from ..entities import CliCommand, CliArgument
from ..interfaces import CliService
from ..mappers import (
    CliCommandYamlObject,
    TransferObject,
    Aggregate,
)
from ..utils import Yaml
from ..events import RaiseError, const

# *** repos

# ** repo: cli_yaml_repository
class CliYamlRepository(CliService):
    '''
    YAML-backed repository for CLI configurations (commands, parent arguments).
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: default_role
    default_role: str

    # * attribute: encoding
    encoding: str

    # * init
    def __init__(self, yaml_file: str, encoding: str = 'utf-8'):
        '''
        Initialize the CLI YAML repository.

        :param yaml_file: Path to YAML CLI config file
        :type yaml_file: str
        :param encoding: File encoding (default 'utf-8')
        :type encoding: str
        '''

        # Set the repository attributes.
        self.yaml_file = yaml_file
        self.default_role = 'to_data.yaml'
        self.encoding = encoding

    # * method: get_commands
    def get_commands(self) -> List[CliCommand]:
        '''
        List all CLI command configurations.

        :return: List of CLI commands
        :rtype: List[CliCommand]
        '''

        # Load the CLI commands from the yaml configuration file.
        with Yaml(self.yaml_file, mode='r', encoding=self.encoding) as yaml_file:

            # Load all command data from nested cli.cmds structure.
            cmds_data = yaml_file.load(
                start_node=lambda d: d.get('cli', {}).get('cmds', {}),
                data_factory=lambda d: {
                    f"{group}.{cmd}": TransferObject.from_data(
                        CliCommandYamlObject,
                        id=f"{group}.{cmd}",
                        **cmd_data
                    ) for group, group_data in d.items() for cmd, cmd_data in group_data.items()
                }
            )

        # Return the mapped command objects.
        return [cmd.map() for cmd in cmds_data.values()]

    # * method: get_command
    def get_command(self, command_id: str) -> CliCommand | None:
        '''
        Get a CLI command by its full ID (group.key).

        :param command_id: Command identifier (e.g., 'calc.add')
        :type command_id: str
        :return: CLI command or None if not found
        :rtype: CliCommand | None
        '''

        # Split the command ID into group and command keys.
        group_key, command_key = command_id.split('.', 1)

        # Load the command data from the yaml configuration file.
        with Yaml(self.yaml_file, mode='r', encoding=self.encoding) as yaml_file:

            # Load the specific command data.
            cmd_data = yaml_file.load(
                start_node=lambda d: d.get('cli', {}).get('cmds', {}).get(group_key, {}).get(command_key)
            )

        # If no data is found, return None.
        if not cmd_data:
            return None

        # Map the command data to the command object and return it.
        return TransferObject.from_data(
            CliCommandYamlObject,
            id=command_id,
            **cmd_data
        ).map()

    # * method: get_parent_arguments
    def get_parent_arguments(self) -> List[CliArgument]:
        '''
        Get all parent-level CLI arguments.

        :return: List of parent arguments
        :rtype: List[CliArgument]
        '''

        # Load the parent arguments from the yaml configuration file.
        with Yaml(self.yaml_file, mode='r', encoding=self.encoding) as yaml_file:

            # Load and return the parent arguments data.
            return yaml_file.load(
                start_node=lambda d: d.get('cli', {}).get('parent_args', []),
                data_factory=lambda d: [Aggregate.new(
                    CliArgument,
                    **arg
                ) for arg in d]
            )

    # * method: save_command
    def save_command(self, cli_command: CliCommand):
        '''
        Save/update a CLI command configuration.

        :param cli_command: The CLI command to save.
        :type cli_command: CliCommand
        '''

        # Create updated command data.
        cmd_data = TransferObject.from_model(
            CliCommandYamlObject,
            cli_command
        )

        # Split the command ID into group and command keys.
        group_key, command_key = cli_command.id.split('.', 1)

        # Update the command data.
        with Yaml(self.yaml_file, mode='w', encoding=self.encoding) as yaml_file:

            # Save the updated command data back to the yaml file.
            yaml_file.save(
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
        with Yaml(self.yaml_file, mode='r', encoding=self.encoding) as yaml_file:

            # Load the group data.
            group_data = yaml_file.load(
                start_node=lambda d: d.get('cli', {}).get('cmds', {}).get(group_key, {})
            )

        # Pop the command data whether it exists or not.
        group_data.pop(command_key, None)

        # Save the updated group data back to the yaml file.
        with Yaml(self.yaml_file, mode='w', encoding=self.encoding) as yaml_file:

            # Save the updated group data.
            yaml_file.save(
                group_data,
                data_path=f'cli.cmds.{group_key}'
            )

    # * method: save_parent_arguments
    def save_parent_arguments(self, parent_arguments: List[CliArgument]):
        '''
        Save/update parent-level CLI arguments.

        :param parent_arguments: The list of parent arguments to save.
        :type parent_arguments: List[CliArgument]
        '''

        # Save the parent arguments data to the yaml file.
        with Yaml(self.yaml_file, mode='w', encoding=self.encoding) as yaml_file:

            # Save the parent arguments data.
            yaml_file.save(
                [arg.to_primitive() for arg in parent_arguments],
                data_path='cli.parent_args'
            )
