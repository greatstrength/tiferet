# *** imports

# ** core
from typing import Any, List

# ** app
from . import *
from ...data.cli import *
from ...contracts.cli import (
    CliRepository,
    CliCommand as CliCommandContract,
    CliArgument as CliArgumentContract
)

# *** proxies

# ** proxy: cli_yaml_proxy
class CliYamlProxy(CliRepository, YamlConfigurationProxy):
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
    def load_yaml(self, start_node: callable = lambda data: data, create_data: callable = lambda data: data) -> Any:
        '''
        Load data from the YAML configuration file.
        :param start_node: The starting node in the YAML file.
        :type start_node: callable
        :param create_data: A callable to create data objects from the loaded data.
        :type create_data: callable
        :return: The loaded data.
        :rtype: Any
        '''
        # Load the YAML file contents using the yaml config proxy.
        try:
            return super().load_yaml(
                start_node=start_node,
                create_data=create_data
            )
        # Raise an error if the loading fails.
        except (Exception, TiferetError) as e:
            raise_error.execute(
                'CLI_CONFIG_LOADING_FAILED',
                f'Unable to load CLI configuration file {self.config_file}: {e}.',
                self.config_file,
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
        # Load the YAML data for the command.
        yaml_data: CliCommandYamlData = self.load_yaml(
            start_node=lambda data: data.get('cli', {}).get('cmds', {}).get(command_id, {}),
            create_data=lambda data: DataObject.from_data(
                CliCommandYamlData,
                id=command_id,
                **data
            )
        )
        # Return the command object created from the YAML data.
        return yaml_data.map()
    
    # * method: get_commands
    def get_commands(self) -> List[CliCommandContract]:
        '''
        Get all commands available in the CLI service.
        :return: A list of CLI commands.
        :rtype: List[CliCommandContract]
        '''
        # Load the YAML data for the commands.
        result: List[CliCommand] = self.load_yaml(
            start_node=lambda data: data.get('cli', {}).get('cmds', []),
            create_data=lambda data: [DataObject.from_data(
                CliCommandYamlData,
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
        result: List[CliArgument] = self.load_yaml(
            start_node=lambda data: data.get('cli', {}).get('parent_args', []),
            create_data=lambda data: [ModelObject.new(
                CliArgument,
                **arg_data
            ) for arg_data in data]
        )
        # Return the result if it exists, otherwise return an empty list.
        return result if result else []