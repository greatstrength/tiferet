"""Tiferet CLI YAML Repository"""

# *** imports

# ** core
from typing import (
    List,
    Dict,
    Any
)

# ** app
from ..interfaces import CliService
from ..mappers import (
    CliArgumentAggregate,
    CliCommandAggregate,
    CliCommandYamlObject,
    TransferObject,
)
from ..utils import Yaml
from ..events import RaiseError

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
    def __init__(self, cli_yaml_file: str, encoding: str = 'utf-8'):
        '''
        Initialize the CLI YAML repository.

        :param cli_yaml_file: Path to YAML CLI config file
        :type cli_yaml_file: str
        :param encoding: File encoding (default 'utf-8')
        :type encoding: str
        '''

        # Set the repository attributes.
        self.yaml_file = cli_yaml_file
        self.default_role = 'to_data.yaml'
        self.encoding = encoding

    # * method: list
    def list(self) -> List[CliCommandAggregate]:
        '''
        List all CLI command configurations.

        :return: List of CLI commands
        :rtype: List[CliCommandAggregate]
        '''

        # Load the CLI commands from the yaml configuration file.
        # Load all command data from nested cli.cmds structure.
        cmds_data = Yaml(self.yaml_file, encoding=self.encoding).load(
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

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if a CLI command exists by ID.

        :param id: The CLI command identifier.
        :type id: str
        :return: True if the CLI command exists, otherwise False.
        :rtype: bool
        '''

        # Check if the command exists by attempting to retrieve it.
        return self.get(id) is not None

    # * method: get
    def get(self, id: str) -> CliCommandAggregate | None:
        '''
        Get a CLI command by its full ID (group.key).

        :param id: Command identifier (e.g., 'calc.add')
        :type id: str
        :return: CLI command or None if not found
        :rtype: CliCommandAggregate | None
        '''

        # Split the command ID into group and command keys.
        group_key, command_key = id.split('.', 1)

        # Load the command data from the yaml configuration file.
        # Load the specific command data.
        cmd_data = Yaml(self.yaml_file, encoding=self.encoding).load(
            start_node=lambda d: d.get('cli', {}).get('cmds', {}).get(group_key, {}).get(command_key)
        )

        # If no data is found, return None.
        if not cmd_data:
            return None

        # Map the command data to the command object and return it.
        return TransferObject.from_data(
            CliCommandYamlObject,
            id=id,
            **cmd_data
        ).map()

    # * method: get_parent_arguments
    def get_parent_arguments(self) -> List[CliArgumentAggregate]:
        '''
        Get all parent-level CLI arguments.

        :return: List of parent arguments
        :rtype: List[CliArgumentAggregate]
        '''

        # Load the parent arguments from the yaml configuration file.
        # Load and return the parent arguments data.
        return Yaml(self.yaml_file, encoding=self.encoding).load(
            start_node=lambda d: d.get('cli', {}).get('parent_args', []),
            data_factory=lambda d: [CliArgumentAggregate.new(
                **arg
            ) for arg in d]
        )

    # * method: save
    def save(self, command: CliCommandAggregate):
        '''
        Save/update a CLI command configuration.

        :param command: The CLI command to save.
        :type command: CliCommandAggregate
        '''

        # Create updated command data.
        cmd_data = TransferObject.from_model(
            CliCommandYamlObject,
            command
        )

        # Split the command ID into group and command keys.
        group_key, command_key = command.id.split('.', 1)

        # Update the command data.
        # Load the full configuration file.
        full_data = Yaml(self.yaml_file, encoding=self.encoding).load()

        # Update the entry.
        full_data.setdefault('cli', {}).setdefault('cmds', {}).setdefault(f'{group_key}', {})[f'{command_key}'] = cmd_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)

    # * method: delete
    def delete(self, id: str):
        '''
        Delete a CLI command by ID (idempotent).

        :param id: The command id.
        :type id: str
        '''

        # Split the command ID into group and command keys.
        group_key, command_key = id.split('.', 1)

        # Retrieve the group data from the yaml file.
        # Load the group data.
        group_data = Yaml(self.yaml_file, encoding=self.encoding).load(
            start_node=lambda d: d.get('cli', {}).get('cmds', {}).get(group_key, {})
        )

        # Pop the command data whether it exists or not.
        group_data.pop(command_key, None)

        # Save the updated group data back to the yaml file.
        # Load the full configuration file.
        full_data = Yaml(self.yaml_file, encoding=self.encoding).load()

        # Update the entry.
        full_data.setdefault('cli', {}).setdefault('cmds', {})[f'{group_key}'] = group_data

        # Persist the updated configuration file.
        Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)

    # * method: save_parent_arguments
    def save_parent_arguments(self, parent_arguments: List[CliArgumentAggregate]):
        '''
        Save/update parent-level CLI arguments.

        :param parent_arguments: The list of parent arguments to save.
        :type parent_arguments: List[CliArgumentAggregate]
        '''

        # Save the parent arguments data to the yaml file.
        # Load the full configuration file.
        full_data = Yaml(self.yaml_file, encoding=self.encoding).load()

        # Update the cli.parent_args entry.
        full_data.setdefault('cli', {})['parent_args'] = [arg.to_primitive() for arg in parent_arguments]

        # Persist the updated configuration file.
        Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)