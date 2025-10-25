"""Tiferet CLI YAML Proxy Tests Exports"""

# *** imports

# ** infra
import pytest

# ** app
from ....commands import TiferetError
from ..cli import CliYamlProxy

# *** fixtures

# ** fixture: cli_config_file
@pytest.fixture
def cli_config_file() -> str:
    '''
    Fixture to provide the path to the CLI configuration file.
    
    :return: The CLI configuration file path.
    :rtype: str
    '''

    # Return the CLI configuration file path.
    return 'tiferet/configs/tests/test.yml'

# ** fixture: cli_yaml_proxy
@pytest.fixture
def cli_yaml_proxy(cli_config_file: str):
    '''
    Fixture to create an instance of the CliYamlProxy.

    :param cli_config_file: The CLI configuration file path.
    :type cli_config_file: str
    '''

    # Create and return the CliYamlProxy instance.
    return CliYamlProxy(cli_config_file)

# *** tests

# ** test: cli_yaml_proxy_load_yaml
def test_cli_yaml_proxy_load_yaml(cli_yaml_proxy: CliYamlProxy):
    '''
    Test the load_yaml method of the CliYamlProxy.

    :param cli_yaml_proxy: The CLI YAML proxy.
    :type cli_yaml_proxy: CliYamlProxy
    '''

    # Load the YAML file.
    data = cli_yaml_proxy.load_yaml()
    
    # Check the loaded data.
    assert data
    assert isinstance(data, dict)
    assert 'interfaces' in data
    assert 'attrs' in data
    assert 'const' in data
    assert 'features' in data
    assert 'errors' in data
    assert 'cli' in data

# ** test: cli_yaml_proxy_load_yaml_file_not_found
def test_cli_yaml_proxy_load_yaml_file_not_found(cli_yaml_proxy: CliYamlProxy):
    '''
    Test the load_yaml method with a file not found error.

    :param cli_yaml_proxy: The CLI YAML proxy.
    :type cli_yaml_proxy: CliYamlProxy
    '''

    # Set a non-existent configuration file.
    cli_yaml_proxy.config_file = 'non_existent_file.yml'
    
    # Attempt to load the YAML file.
    with pytest.raises(TiferetError) as exc_info:
        cli_yaml_proxy.load_yaml()
    
    # Verify the error message.
    assert exc_info.value.error_code == 'CLI_CONFIG_LOADING_FAILED'
    assert 'Unable to load CLI configuration file' in str(exc_info.value)

# ** test: cli_yaml_proxy_get_command
def test_cli_yaml_proxy_get_command(cli_yaml_proxy: CliYamlProxy):
    '''
    Test the get_command method of the CliYamlProxy.

    :param cli_yaml_proxy: The CLI YAML proxy.
    :type cli_yaml_proxy: CliYamlProxy
    '''

    # Get a command by its ID.
    command = cli_yaml_proxy.get_command('test_group.test_feature')
    
    # Check the command.
    assert command
    assert command.id == 'test_group.test_feature'
    assert command.name == 'Test Feature Command'
    assert command.group_key == 'test-group'
    assert command.key == 'test-feature'
    assert command.description == 'A test feature command.'
    
    # Check the arguments of the command.
    assert command.arguments
    assert len(command.arguments) == 2
    assert command.arguments[0].name_or_flags == ['--arg1', '-a']
    assert command.arguments[0].description == 'Argument 1'
    assert command.arguments[1].name_or_flags == ['--arg2', '-b']
    assert command.arguments[1].description == 'Argument 2'

# ** test: cli_yaml_proxy_get_commands
def test_cli_yaml_proxy_get_commands(cli_yaml_proxy: CliYamlProxy):
    '''
    Test the get_commands method of the CliYamlProxy.

    :param cli_yaml_proxy: The CLI YAML proxy.
    :type cli_yaml_proxy: CliYamlProxy
    '''

    # Get all commands.
    commands = cli_yaml_proxy.get_commands()
    
    # Check the commands.
    assert commands
    assert len(commands) > 0
    
    # Check that the command we expect is in the list.
    command_ids = [cmd.id for cmd in commands]
    assert 'test_group.test_feature' in command_ids

# ** test: cli_yaml_proxy_get_parent_arguments
def test_cli_yaml_proxy_get_parent_arguments(cli_yaml_proxy: CliYamlProxy):
    '''
    Test the get_parent_arguments method of the CliYamlProxy.

    :param cli_yaml_proxy: The CLI YAML proxy.
    :type cli_yaml_proxy: CliYamlProxy
    '''

    # Get parent arguments.
    parent_args = cli_yaml_proxy.get_parent_arguments()
    
    # Check the parent arguments.
    assert parent_args
    assert len(parent_args) > 0
    
    # Check that the first argument has the expected properties.
    first_arg = parent_args[0]
    assert first_arg.name_or_flags == ['--parent-arg', '-p']
    assert first_arg.description == 'Parent argument'
    assert first_arg.required is True