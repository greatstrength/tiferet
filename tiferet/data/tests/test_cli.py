"""Tiferet CLI Data Object Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import (
    DataObject,
)
from ..cli import (
    CliCommandConfigData,
    CliCommand,
)

# *** fixtures

# ** fixture: cli_command_yaml_data
@pytest.fixture
def cli_command_config_data() -> CliCommandConfigData:
    '''
    Provides a fixture for CLI command configuration data.

    :return: The CLI command configuration data object.
    :rtype: CliCommandConfigData
    '''

    # Create and return a CLI command configuration data object.
    return DataObject.from_data(
        CliCommandConfigData,
        id='test_group.test_feature',
        name='Test Feature',
        description='This is a test feature command.',
        group_key='test-group',
        key='test-feature',
        args=[
            dict(
                name_or_flags=['--arg1', '-a'],
                description='Argument 1',
                required=True
            ),
            dict(
                name_or_flags=['--arg2', '-b'],
                description='Argument 2',
                required=False
            )
        ]
    )

# *** tests

# ** test: cli_command_yaml_data_from_data
def test_cli_command_yaml_data_from_data(cli_command_config_data: CliCommandConfigData):
    '''
    Test the creation of CLI command configuration data from a dictionary.

    :param cli_command_yaml_data: The CLI command configuration data object.
    :type cli_command_yaml_data: CliCommandConfigData
    '''

    # Assert the CLI command configuration data is an instance of CliCommandYamlData.
    assert isinstance(cli_command_config_data, CliCommandConfigData)

    # Assert the attributes are correctly set.
    assert cli_command_config_data.id == 'test_group.test_feature'
    assert cli_command_config_data.name == 'Test Feature'
    assert cli_command_config_data.description == 'This is a test feature command.'
    assert cli_command_config_data.group_key == 'test-group'
    assert cli_command_config_data.key == 'test-feature'

    # Assert the arguments are correctly set.
    assert len(cli_command_config_data.arguments) == 2
    assert cli_command_config_data.arguments[0].name_or_flags == ['--arg1', '-a']
    assert cli_command_config_data.arguments[0].description == 'Argument 1'
    assert cli_command_config_data.arguments[0].required is True
    assert cli_command_config_data.arguments[1].name_or_flags == ['--arg2', '-b']
    assert cli_command_config_data.arguments[1].description == 'Argument 2'
    assert cli_command_config_data.arguments[1].required is False

# ** test: cli_command_yaml_data_map
def test_cli_command_yaml_data_map(cli_command_config_data: CliCommandConfigData):
    '''
    Test the mapping of CLI command configuration data to a CLI command object.

    :param cli_command_yaml_data: The CLI command configuration data object.
    :type cli_command_yaml_data: CliCommandConfigData
    '''

    # Map the configuration data to a CLI command object.
    cli_command = cli_command_config_data.map()

    # Assert the mapped CLI command is valid.
    assert isinstance(cli_command, CliCommand)
    assert cli_command.id == 'test_group.test_feature'
    assert cli_command.name == 'Test Feature'
    assert cli_command.description == 'This is a test feature command.'
    assert cli_command.group_key == 'test-group'
    assert cli_command.key == 'test-feature'

    # Assert the arguments are correctly mapped.
    assert len(cli_command.arguments) == 2
    assert cli_command.arguments[0].name_or_flags == ['--arg1', '-a']
    assert cli_command.arguments[0].description == 'Argument 1'
    assert cli_command_config_data.arguments[0].required is True
    assert cli_command.arguments[1].name_or_flags == ['--arg2', '-b']
    assert cli_command.arguments[1].description == 'Argument 2'
    assert cli_command_config_data.arguments[1].required is False

# ** test: cli_command_yaml_data_to_primitive
def test_cli_command_yaml_data_to_primitive(cli_command_config_data: CliCommandConfigData):
    '''
    Test the conversion of CLI command configuration data to a primitive dictionary.

    :param cli_command_yaml_data: The CLI command configuration data object.
    :type cli_command_yaml_data: CliCommandConfigData
    '''

    # Convert the configuration data to a primitive dictionary.
    primitive = cli_command_config_data.to_primitive('to_data.yaml')

    # Assert the primitive is a dictionary.
    assert isinstance(primitive, dict)

    # Assert the primitive values are correct.
    assert primitive.get('name') == 'Test Feature'
    assert primitive.get('description') == 'This is a test feature command.'
    assert primitive.get('group_key') == 'test-group'
    assert primitive.get('key') == 'test-feature'
    assert len(primitive.get('args')) == 2
    assert primitive.get('args')[0].get('name_or_flags') == ['--arg1', '-a']
    assert primitive.get('args')[0].get('description') == 'Argument 1'
    assert primitive.get('args')[0].get('required') is True
    assert primitive.get('args')[1].get('name_or_flags') == ['--arg2', '-b']
    assert primitive.get('args')[1].get('description') == 'Argument 2'
    assert primitive.get('args')[1].get('required') is False