"""Tiferet CLI YAML Proxy"""

# *** imports

# ** core
from typing import (
    Any,
    List,
    Dict,
    Callable
)

# ** app
from ...commands import raise_error
from ...data import (
    DataObject,
    CliCommandConfigData,
    CliArgumentConfigData,
)
from ...contracts import (
    CliRepository,
    CliCommandContract,
    CliArgumentContract,
)
from .settings import YamlFileProxy

# *** proxies

# ** proxy: cli_yaml_proxy
class CliYamlProxy(CliRepository, YamlFileProxy):
    '''
    The YAML proxy for the CLI configuration.
    This proxy is used to manage the command line interface configuration in YAML format.
    '''

    # * method: init
    def __init__(self, cli_config_file: str):
        '''
        Initialize the CLI YAML proxy.

        :param cli_config_file: The path to the CLI configuration file.
        :type cli_config_file: str
        '''

        # Initialize the base class with the provided configuration file.
        super().__init__(cli_config_file)

    # * method: load_yaml
    def load_yaml(self, start_node: Callable = lambda data: data, data_factory: Callable = lambda data: data) -> List[Any] | Dict[str, Any]:
        '''
        Load data from the YAML configuration file.

        :param start_node: A callable to specify the starting node in the YAML file.
        :type start_node: Callable
        :param data_factory: A callable to create data objects from the loaded data.
        :type data_factory: Callable
        :return: The loaded data.
        :rtype: Any
        '''

        # Load the YAML file contents using the yaml config proxy.
        try:
            return super().load_yaml(
                start_node=start_node,
                data_factory=data_factory
            )

        # Raise an error if the loading fails.
        except Exception as e:
            raise_error.execute(
                'CLI_CONFIG_LOADING_FAILED',
                f'Unable to load CLI configuration file {self.yaml_file}: {e}.',
                self.yaml_file,
                e
            )

    # * method: get_command
    def get_command(self, command_id: str) -> CliCommandContract:
        '''
        Get a command by its group and name.

        :param command_id: The unique identifier for the command.
        :type command_id: str
        :return: The command object.
        :rtype: CliCommandContract
        '''

        # Load the raw YAML data for the command.
        yaml_data: CliCommandConfigData = self.load_yaml(
            start_node=lambda data: data.get('cli', {}).get('cmds', {}).get(command_id, None),
        )

        # If no data is found, return None.
        if not yaml_data:
            return None

        # Return the command object created from the YAML data.
        return DataObject.from_data(
            CliCommandConfigData,
            id=command_id,
            **yaml_data
        ).map()

    # * method: get_commands
    def get_commands(self) -> List[CliCommandContract]:
        '''
        Get all commands available in the CLI service.

        :return: A list of CLI commands.
        :rtype: List[CliCommandContract]
        '''

        # Load the YAML data for the commands.
        result: List[CliCommandContract] = self.load_yaml(
            start_node=lambda data: data.get('cli', {}).get('cmds', []),
            data_factory=lambda data: [DataObject.from_data(
                CliCommandConfigData,
                id=id,
                **cmd_data
            ) for id, cmd_data in data.items()]
        )

        # Return the result if it exists, otherwise return an empty list.
        return [cmd.map() for cmd in result] if result else []
    
    # * method: get_parent_arguments
    def get_parent_arguments(self) -> List[CliArgumentContract]:
        '''
        Get the parent arguments for the CLI commands.
        :return: A list of parent arguments.
        :rtype: List[CliArgumentContract]
        '''

        # Load the YAML data for the parent arguments.
        result: List[CliArgumentContract] = self.load_yaml(
            start_node=lambda data: data.get('cli', {}).get('parent_args', []),
            data_factory=lambda data: [DataObject.from_data(
                CliArgumentConfigData,
                **arg_data
            ) for arg_data in data]
        )

        # Return the result if it exists, otherwise return an empty list.
        return result if result else []
    
    # * method: save_command
    def save_command(self, cli_command: CliCommandContract):
        '''
        Save a CLI command to the YAML configuration file.

        :param cli_command: The CLI command to save.
        :type cli_command: CliCommandContract
        '''

        # Convert the command to a data object for serialization.
        yaml_data = DataObject.from_model(
            CliCommandConfigData,
            cli_command,
            id=cli_command.id
        )

        # Save the command data to the YAML file.
        self.save_yaml(
            yaml_data.to_primitive(self.default_role),
            data_yaml_path=f'cli/cmds/{cli_command.id}'
        )

    # * method: delete_command
    def delete_command(self, command_id: str):
        '''
        Delete a CLI command from the YAML configuration file.

        :param command_id: The unique identifier for the command to delete.
        :type command_id: str
        '''

        # Delete the command data from the YAML file.
        commands_data = self.load_yaml(
            start_node=lambda data: data.get('cli', {}).get('cmds', {})
        )

        # Pop the command regardless of its existence.
        commands_data.pop(command_id, None)

        # Save the updated commands data back to the YAML file.
        self.save_yaml(
            commands_data,
            data_yaml_path='cli/cmds'
        )

    # * method: save_parent_arguments
    def save_parent_arguments(self, parent_arguments: List[CliArgumentContract]):
        '''
        Save the parent arguments to the YAML configuration file.

        :param parent_arguments: The list of parent arguments to save.
        :type parent_arguments: List[CliArgumentContract]
        '''

        # Convert the parent arguments to data objects for serialization.
        yaml_data = [
            DataObject.from_model(
                CliArgumentConfigData,
                arg
            ) for arg in parent_arguments
        ]

        # Save the parent arguments data to the YAML file.
        # The cli argument is actually a model, so we do not use 'to_data' here.
        self.save_yaml(
            [arg.to_primitive() for arg in yaml_data], 
            data_yaml_path='cli/parent_args'
        )