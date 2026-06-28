"""Tiferet CLI Configuration Repository"""

# *** imports

# ** core
from typing import List

# ** app
from ..interfaces import CliService
from ..mappers import (
    CliArgumentAggregate,
    CliCommandAggregate,
    CliCommandConfigObject,
)
from .settings import ConfigurationRepository

# *** repos

# ** repo: cli_config_repository
class CliConfigRepository(CliService, ConfigurationRepository):
    '''
    The CLI configuration repository.
    '''

    # * init
    def __init__(self, cli_config: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the CLI configuration repository.

        :param cli_config: The configuration file path.
        :type cli_config: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Initialize the configuration repository base.
        ConfigurationRepository.__init__(self, config_file=cli_config, encoding=encoding)

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
        cmd_data = self._load(
            start_node=lambda data: data.get('cli', {}).get('cmds', {}).get(group_key, {}).get(command_key)
        )

        # If no data is found, return None.
        if not cmd_data:
            return None

        # Map the data to a CliCommandAggregate and return it.
        return CliCommandConfigObject.model_validate(
            {**cmd_data, 'id': id}
        ).map()

    # * method: list
    def list(self) -> List[CliCommandAggregate]:
        '''
        List all CLI commands.

        :return: A list of CLI command aggregates.
        :rtype: List[CliCommandAggregate]
        '''

        # Load all command groups from the configuration file.
        cmds_data = self._load(
            start_node=lambda data: data.get('cli', {}).get('cmds', {})
        )

        # Flatten nested group → command structure into a list of aggregates.
        result = []
        for group_key, commands in cmds_data.items():
            for command_key, command_data in commands.items():
                cmd = CliCommandConfigObject.model_validate(
                    {**command_data, 'id': f'{group_key}.{command_key}'}
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
        cmd_data = CliCommandConfigObject.from_model(command)

        # Split the composite ID into group_key and command_key.
        group_key, command_key = command.id.split('.', 1)

        # Load the full configuration file.
        full_data = self._load()

        # Update or insert the command entry under the appropriate group.
        full_data.setdefault('cli', {}).setdefault('cmds', {}).setdefault(group_key, {})[command_key] = cmd_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        self._save(full_data)

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
        full_data = self._load()

        # Remove the command entry if it exists (idempotent).
        full_data.get('cli', {}).get('cmds', {}).get(group_key, {}).pop(command_key, None)

        # Persist the updated configuration file.
        self._save(full_data)

    # * method: get_parent_arguments
    def get_parent_arguments(self) -> List[CliArgumentAggregate]:
        '''
        Get all parent-level CLI arguments.

        :return: A list of parent CLI argument aggregates.
        :rtype: List[CliArgumentAggregate]
        '''

        # Load parent arguments from the configuration file.
        parent_args_data = self._load(
            start_node=lambda data: data.get('cli', {}).get('parent_args', []),
            data_factory=lambda args: [
                CliArgumentAggregate(**arg)
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
        full_data = self._load()

        # Set the parent_args section to the serialized argument list.
        full_data.setdefault('cli', {})['parent_args'] = [
            {k: v for k, v in arg.model_dump().items() if v is not None}
            for arg in parent_arguments
        ]

        # Persist the updated configuration file.
        self._save(full_data)
