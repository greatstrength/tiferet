"""Tiferet CLI YAML Repository"""

# *** imports

# ** core
from typing import List

# ** app
from ..interfaces import CliService
from ..mappers import (
    TransferObject,
    CliArgumentAggregate,
    CliCommandAggregate,
    CliCommandYamlObject,
)
from ..utils import Yaml

# *** repos

# ** repo: cli_yaml_repository
class CliYamlRepository(CliService):
    '''
    The CLI YAML repository.
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: encoding
    encoding: str

    # * attribute: default_role
    default_role: str

    # * init
    def __init__(self, cli_yaml_file: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the CLI YAML repository.

        :param cli_yaml_file: The YAML configuration file path.
        :type cli_yaml_file: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Set the repository attributes.
        self.yaml_file = cli_yaml_file
        self.encoding = encoding
        self.default_role = 'to_data.yaml'

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if a CLI command exists by ID.

        :param id: The CLI command identifier (format: group_key.command_key).
        :type id: str
        :return: True if the CLI command exists, otherwise False.
        :rtype: bool
        '''

        # Delegate to get and check for None.
        return self.get(id) is not None

    # * method: get
    def get(self, id: str) -> CliCommandAggregate | None:
        '''
        Retrieve a CLI command by ID.

        :param id: The CLI command identifier (format: group_key.command_key).
        :type id: str
        :return: The CLI command aggregate or None if not found.
        :rtype: CliCommandAggregate | None
        '''

        # Split the composite ID into group_key and command_key.
        group_key, command_key = id.split('.', 1)

        # Load the specific command data from the configuration file.
        cmd_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('cli', {}).get('cmds', {}).get(group_key, {}).get(command_key)
        )

        # If no data is found, return None.
        if not cmd_data:
            return None

        # Map the data to a CliCommandAggregate and return it.
        return TransferObject.from_data(
            CliCommandYamlObject,
            id=id,
            **cmd_data,
        ).map()

    # * method: list
    def list(self) -> List[CliCommandAggregate]:
        '''
        List all CLI commands.

        :return: A list of CLI command aggregates.
        :rtype: List[CliCommandAggregate]
        '''

        # Load all command groups from the configuration file.
        cmds_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('cli', {}).get('cmds', {})
        )

        # Flatten nested group → command structure into a list of aggregates.
        result = []
        for group_key, commands in cmds_data.items():
            for command_key, command_data in commands.items():
                cmd = TransferObject.from_data(
                    CliCommandYamlObject,
                    id=f'{group_key}.{command_key}',
                    **command_data,
                ).map()
                result.append(cmd)

        # Return the list of CLI command aggregates.
        return result

    # * method: save
    def save(self, command: CliCommandAggregate) -> None:
        '''
        Save or update a CLI command.

        :param command: The CLI command aggregate to save.
        :type command: CliCommandAggregate
        :return: None
        :rtype: None
        '''

        # Convert the CLI command model to configuration data.
        cmd_data = CliCommandYamlObject.from_model(command)

        # Split the composite ID into group_key and command_key.
        group_key, command_key = command.id.split('.', 1)

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load()

        # Update or insert the command entry under the appropriate group.
        full_data.setdefault('cli', {}).setdefault('cmds', {}).setdefault(group_key, {})[command_key] = cmd_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding,
        ).save(data=full_data)

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete a CLI command by ID. This operation is idempotent.

        :param id: The CLI command identifier (format: group_key.command_key).
        :type id: str
        :return: None
        :rtype: None
        '''

        # Split the composite ID into group_key and command_key.
        group_key, command_key = id.split('.', 1)

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load()

        # Remove the command entry if it exists (idempotent).
        full_data.get('cli', {}).get('cmds', {}).get(group_key, {}).pop(command_key, None)

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding,
        ).save(data=full_data)

    # * method: get_parent_arguments
    def get_parent_arguments(self) -> List[CliArgumentAggregate]:
        '''
        Get all parent-level CLI arguments.

        :return: A list of parent CLI argument aggregates.
        :rtype: List[CliArgumentAggregate]
        '''

        # Load parent arguments from the configuration file.
        parent_args_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('cli', {}).get('parent_args', []),
            data_factory=lambda args: [
                CliArgumentAggregate.new(**arg)
                for arg in args
            ],
        )

        # Return the list of parent CLI argument aggregates.
        return parent_args_data

    # * method: save_parent_arguments
    def save_parent_arguments(self, parent_arguments: List[CliArgumentAggregate]) -> None:
        '''
        Save or update parent-level CLI arguments.

        :param parent_arguments: The list of parent CLI argument aggregates to save.
        :type parent_arguments: List[CliArgumentAggregate]
        :return: None
        :rtype: None
        '''

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load()

        # Set the parent_args section to the serialized argument list.
        full_data.setdefault('cli', {})['parent_args'] = [
            {k: v for k, v in arg.to_primitive().items() if v is not None}
            for arg in parent_arguments
        ]

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding,
        ).save(data=full_data)
