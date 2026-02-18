"""Tiferet CLI YAML Proxy Tests Exports"""

# *** imports

# ** infra
import pytest
import json

# ** app
from ....assets import TiferetError
from ....entities import ModelObject, CliArgument
from ....mappers import DataObject, CliCommandConfigData
from ..cli import CliJsonProxy

# *** fixtures

# ** fixture: cli_config_file
@pytest.fixture
def cli_config_file(tmp_path) -> str:
    '''
    Fixture to provide the path to the CLI configuration file.
    
    :return: The CLI configuration file path.
    :rtype: str
    '''

    # Create a temporary YAML file with sample CLI configuration content.
    file_path = tmp_path / 'test.json'

    # Write the sample CLI configuration to the YAML file.
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'cli': {
                'parent_args': [
                    {
                        'name_or_flags': ['--parent-arg', '-p'],
                        'description': 'Parent argument',
                        'required': True
                    }
                ],
                'cmds': {
                    'test_group': {
                        'test_feature': {
                            'name': 'Test Feature Command',
                            'description': 'A test feature command.',
                            'args': [
                                {
                                    'name_or_flags': ['--arg1', '-a'],
                                    'description': 'Argument 1'
                                },
                                {
                                    'name_or_flags': ['--arg2', '-b'],
                                    'description': 'Argument 2'
                                }
                            ]
                        }
                    }   
                }
            }
        }, f)

    # Return the file path as a string.
    return str(file_path)

# ** fixture: cli_json_proxy
@pytest.fixture
def cli_json_proxy(cli_config_file: str):
    '''
    Fixture to create an instance of the CliJsonProxy.

    :param cli_config_file: The CLI configuration file path.
    :type cli_config_file: str
    '''

    # Create and return the CliJsonProxy instance.
    return CliJsonProxy(cli_config_file)

# *** tests

# ** test: cli_json_proxy_load_json
def test_cli_json_proxy_load_json(cli_json_proxy: CliJsonProxy):
    '''
    Test the load_json method of the CliJsonProxy.

    :param cli_json_proxy: The CLI YAML proxy.
    :type cli_json_proxy: CliJsonProxy
    '''

    # Load the YAML file.
    data = cli_json_proxy.load_json()
    
    # Check the loaded data.
    assert data
    assert isinstance(data, dict)
    assert data.get('cli')
    assert len(data.get('cli', {}).get('cmds', {})) > 0

# ** test: cli_json_proxy_load_json_file_not_found
def test_cli_json_proxy_load_json_file_not_found(cli_json_proxy: CliJsonProxy):
    '''
    Test the load_json method with a file not found error.

    :param cli_json_proxy: The CLI YAML proxy.
    :type cli_json_proxy: CliJsonProxy
    '''

    # Set a non-existent configuration file.
    cli_json_proxy.json_file = 'non_existent_file.yml'
    
    # Attempt to load the YAML file.
    with pytest.raises(TiferetError) as exc_info:
        cli_json_proxy.load_json()
    
    # Verify the error message.
    assert exc_info.value.error_code == 'CLI_CONFIG_LOADING_FAILED'
    assert 'Unable to load CLI configuration file' in str(exc_info.value)
    assert exc_info.value.kwargs.get('json_file') == cli_json_proxy.json_file

# ** test: cli_json_proxy_get_command
def test_cli_json_proxy_get_command(cli_json_proxy: CliJsonProxy):
    '''
    Test the get_command method of the CliJsonProxy.

    :param cli_json_proxy: The CLI YAML proxy.
    :type cli_json_proxy: CliJsonProxy
    '''

    # Get a command by its ID.
    command = cli_json_proxy.get_command('test_group.test_feature')
    
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

# ** test: cli_json_proxy_get_command_not_found
def test_cli_json_proxy_get_command_not_found(cli_json_proxy: CliJsonProxy):
    '''
    Test the get_command method when the command is not found.

    :param cli_json_proxy: The CLI YAML proxy.
    :type cli_json_proxy: CliJsonProxy
    '''

    # Attempt to get a non-existent command.
    command = cli_json_proxy.get_command('non_existent.command')
    
    # Check that the command is None.
    assert command is None

# ** test: cli_json_proxy_get_commands
def test_cli_json_proxy_get_commands(cli_json_proxy: CliJsonProxy):
    '''
    Test the get_commands method of the CliJsonProxy.

    :param cli_json_proxy: The CLI YAML proxy.
    :type cli_json_proxy: CliJsonProxy
    '''

    # Get all commands.
    commands = cli_json_proxy.get_commands()
    
    # Check the commands.
    assert commands
    assert len(commands) > 0
    
    # Check that the command we expect is in the list.
    command_ids = [cmd.id for cmd in commands]
    assert 'test_group.test_feature' in command_ids

# ** test: cli_json_proxy_get_parent_arguments
def test_cli_json_proxy_get_parent_arguments(cli_json_proxy: CliJsonProxy):
    '''
    Test the get_parent_arguments method of the CliJsonProxy.

    :param cli_json_proxy: The CLI YAML proxy.
    :type cli_json_proxy: CliJsonProxy
    '''

    # Get parent arguments.
    parent_args = cli_json_proxy.get_parent_arguments()
    
    # Check the parent arguments.
    assert parent_args
    assert len(parent_args) > 0
    
    # Check that the first argument has the expected properties.
    first_arg = parent_args[0]
    assert first_arg.name_or_flags == ['--parent-arg', '-p']
    assert first_arg.description == 'Parent argument'
    assert first_arg.required is True

# ** test: cli_json_proxy_save_command
def test_cli_json_proxy_save_command(
        cli_json_proxy: CliJsonProxy,
    ):
    '''
    Test the save_command method of the CliJsonProxy.

    :param cli_json_proxy: The CLI YAML proxy.
    :type cli_json_proxy: CliJsonProxy
    :param tmp_path: The temporary path fixture.
    :type tmp_path: pathlib.Path
    '''

    # Create a new command to save.
    new_command = DataObject.from_data(
        CliCommandConfigData,
        id='new_group.new_command',
        name='New Command',
        key='new-command',
        group_key='new-group',
        description='A new command for testing.',
        arguments=[{
            'name_or_flags': ['--new-arg', '-n'],
            'description': 'New argument',
            'required': False
        }]
    ).map()

    # Save the new command.
    cli_json_proxy.save_command(new_command)

    # Reload the command to verify it was saved correctly.
    saved_command = cli_json_proxy.get_command('new_group.new_command')

    # Check the saved command.
    assert saved_command
    assert saved_command.id == 'new_group.new_command'
    assert saved_command.name == 'New Command'
    assert saved_command.group_key == 'new-group'
    assert saved_command.key == 'new-command'
    assert saved_command.description == 'A new command for testing.'
    assert len(saved_command.arguments) == 1
    assert saved_command.arguments[0].name_or_flags == ['--new-arg', '-n']
    assert saved_command.arguments[0].description == 'New argument'
    assert saved_command.arguments[0].required is False

# ** test: cli_json_proxy_delete_command
def test_cli_json_proxy_delete_command(
        cli_json_proxy: CliJsonProxy
    ):
    '''
    Test the delete_command method of the CliJsonProxy.

    :param cli_json_proxy: The CLI YAML proxy.
    :type cli_json_proxy: CliJsonProxy
    '''

    # Delete an existing command.
    cli_json_proxy.delete_command('test_group.test_feature')

    # Attempt to get the deleted command.
    deleted_command = cli_json_proxy.get_command('test_group.test_feature')

    # Check that the command is None.
    assert deleted_command is None

# ** test: cli_json_proxy_save_parent_arguments
def test_cli_json_proxy_save_parent_arguments(
        cli_json_proxy: CliJsonProxy
    ):
    '''
    Test the save_parent_arguments method of the CliJsonProxy.

    :param cli_json_proxy: The CLI YAML proxy.
    :type cli_json_proxy: CliJsonProxy
    '''

    # Create new parent arguments to save.
    new_parent_args = [
        ModelObject.new(
            CliArgument,
            name_or_flags=['--new-parent-arg', '-P'],
            description='New parent argument',
            required=True
        )
    ]

    # Save the new parent arguments.
    cli_json_proxy.save_parent_arguments(new_parent_args)

    # Reload the parent arguments to verify they were saved correctly.
    saved_parent_args = cli_json_proxy.get_parent_arguments()

    # Check the saved parent arguments.
    assert saved_parent_args
    assert len(saved_parent_args) == 1
    assert saved_parent_args[0].name_or_flags == ['--new-parent-arg', '-P']
    assert saved_parent_args[0].description == 'New parent argument'
    assert saved_parent_args[0].required is True