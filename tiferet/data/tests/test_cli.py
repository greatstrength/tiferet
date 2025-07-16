# *** imports

# ** infra
import pytest

# ** app
from ..cli import *

# *** fixtures

# ** fixture: cli_command_yaml_data
@pytest.fixture
def cli_command_yaml_data():
    '''
    Provides a fixture for CLI command YAML data.
    '''
    return DataObject.from_data(
        CliCommandYamlData,
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

# ** test: test_cli_command_yaml_data_from_data
def test_cli_command_yaml_data_from_data(cli_command_yaml_data):
    '''
    Test the creation of CLI command YAML data from a dictionary.
    '''
    # Assert the CLI command YAML data is an instance of CliCommandYamlData.
    assert isinstance(cli_command_yaml_data, CliCommandYamlData)
    
    # Assert the attributes are correctly set.
    assert cli_command_yaml_data.id == 'test_group.test_feature'
    assert cli_command_yaml_data.name == 'Test Feature'
    assert cli_command_yaml_data.description == 'This is a test feature command.'
    assert cli_command_yaml_data.group_key == 'test-group'
    assert cli_command_yaml_data.key == 'test-feature'
    
    # Assert the arguments are correctly set.
    assert len(cli_command_yaml_data.arguments) == 2
    assert cli_command_yaml_data.arguments[0].name_or_flags == ['--arg1', '-a']
    assert cli_command_yaml_data.arguments[0].description == 'Argument 1'
    assert cli_command_yaml_data.arguments[0].required is True
    assert cli_command_yaml_data.arguments[1].name_or_flags == ['--arg2', '-b']
    assert cli_command_yaml_data.arguments[1].description == 'Argument 2'
    assert cli_command_yaml_data.arguments[1].required is False

# ** test: test_cli_command_yaml_data_map
def test_cli_command_yaml_data_map(cli_command_yaml_data):
    '''
    Test the mapping of CLI command YAML data to a CLI command object.
    '''
    # Map the YAML data to a CLI command object.
    cli_command = cli_command_yaml_data.map()
    
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
    assert cli_command_yaml_data.arguments[0].required is True
    assert cli_command.arguments[1].name_or_flags == ['--arg2', '-b']
    assert cli_command.arguments[1].description == 'Argument 2'
    assert cli_command_yaml_data.arguments[1].required is False

# ** test: test_cli_command_yaml_data_to_primitive
def test_cli_command_yaml_data_to_primitive(cli_command_yaml_data):
    '''
    Test the conversion of CLI command YAML data to a primitive dictionary.
    '''
    # Convert the YAML data to a primitive dictionary.
    primitive = cli_command_yaml_data.to_primitive('to_data')
    
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