"""Tiferet CLI Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import (
    TransferObject,
)
from ..cli import (
    CliCommandYamlObject,
    CliCommandAggregate,
)
from ...domain import CliCommand

# *** fixtures

# ** fixture: cli_command_yaml_object
@pytest.fixture
def cli_command_yaml_object() -> CliCommandYamlObject:
    '''
    Provides a fixture for CLI command YAML object.

    :return: The CLI command YAML object.
    :rtype: CliCommandYamlObject
    '''

    # Create and return a CLI command YAML object.
    return TransferObject.from_data(
        CliCommandYamlObject,
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

# ** test: cli_command_yaml_object_from_data
def test_cli_command_yaml_object_from_data(cli_command_yaml_object: CliCommandYamlObject):
    '''
    Test the creation of CLI command YAML object from a dictionary.

    :param cli_command_yaml_object: The CLI command YAML object.
    :type cli_command_yaml_object: CliCommandYamlObject
    '''

    # Assert the CLI command YAML object is an instance of CliCommandYamlObject.
    assert isinstance(cli_command_yaml_object, CliCommandYamlObject)

    # Assert the attributes are correctly set.
    assert cli_command_yaml_object.id == 'test_group.test_feature'
    assert cli_command_yaml_object.name == 'Test Feature'
    assert cli_command_yaml_object.description == 'This is a test feature command.'
    assert cli_command_yaml_object.group_key == 'test-group'
    assert cli_command_yaml_object.key == 'test-feature'

    # Assert the arguments are correctly set.
    assert len(cli_command_yaml_object.arguments) == 2
    assert cli_command_yaml_object.arguments[0].name_or_flags == ['--arg1', '-a']
    assert cli_command_yaml_object.arguments[0].description == 'Argument 1'
    assert cli_command_yaml_object.arguments[0].required is True
    assert cli_command_yaml_object.arguments[1].name_or_flags == ['--arg2', '-b']
    assert cli_command_yaml_object.arguments[1].description == 'Argument 2'
    assert cli_command_yaml_object.arguments[1].required is False

# ** test: cli_command_yaml_object_map
def test_cli_command_yaml_object_map(cli_command_yaml_object: CliCommandYamlObject):
    '''
    Test the mapping of CLI command YAML object to a CLI command aggregate.

    :param cli_command_yaml_object: The CLI command YAML object.
    :type cli_command_yaml_object: CliCommandYamlObject
    '''

    # Map the YAML object to a CLI command aggregate.
    cli_command_aggregate = cli_command_yaml_object.map()

    # Assert the mapped CLI command aggregate is valid.
    assert isinstance(cli_command_aggregate, CliCommandAggregate)
    assert cli_command_aggregate.id == 'test_group.test_feature'
    assert cli_command_aggregate.name == 'Test Feature'
    assert cli_command_aggregate.description == 'This is a test feature command.'
    assert cli_command_aggregate.group_key == 'test-group'
    assert cli_command_aggregate.key == 'test-feature'

    # Assert the arguments are correctly mapped.
    assert len(cli_command_aggregate.arguments) == 2
    assert cli_command_aggregate.arguments[0].name_or_flags == ['--arg1', '-a']
    assert cli_command_aggregate.arguments[0].description == 'Argument 1'
    assert cli_command_aggregate.arguments[0].required is True
    assert cli_command_aggregate.arguments[1].name_or_flags == ['--arg2', '-b']
    assert cli_command_aggregate.arguments[1].description == 'Argument 2'
    assert cli_command_aggregate.arguments[1].required is False

# ** test: cli_command_yaml_object_to_primitive
def test_cli_command_yaml_object_to_primitive(cli_command_yaml_object: CliCommandYamlObject):
    '''
    Test the conversion of CLI command YAML object to a primitive dictionary.

    :param cli_command_yaml_object: The CLI command YAML object.
    :type cli_command_yaml_object: CliCommandYamlObject
    '''

    # Convert the YAML object to a primitive dictionary.
    primitive = cli_command_yaml_object.to_primitive('to_data.yaml')

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

# ** test: cli_command_yaml_object_from_model
def test_cli_command_yaml_object_from_model():
    '''
    Test the creation of CLI command YAML object from a CLI command model.
    '''

    # Create a CLI command model.
    cli_command = CliCommand.new(
        group_key='test-group',
        key='test-feature',
        name='Test Feature',
        description='This is a test feature command.',
        arguments=[
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

    # Create a YAML object from the model.
    yaml_object = CliCommandYamlObject.from_model(cli_command)

    # Assert the YAML object is valid.
    assert isinstance(yaml_object, CliCommandYamlObject)
    assert yaml_object.id == 'test_group.test_feature'
    assert yaml_object.name == 'Test Feature'
    assert yaml_object.description == 'This is a test feature command.'
    assert yaml_object.group_key == 'test-group'
    assert yaml_object.key == 'test-feature'
    assert len(yaml_object.arguments) == 2

# ** test: cli_command_aggregate_new
def test_cli_command_aggregate_new():
    '''
    Test the creation of a CLI command aggregate.
    '''

    # Create a CLI command aggregate.
    cli_command_data = dict(
        id='test_group.test_feature',
        group_key='test-group',
        key='test-feature',
        name='Test Feature',
        description='This is a test feature command.',
        arguments=[]
    )

    aggregate = CliCommandAggregate.new(**cli_command_data)

    # Assert the aggregate is valid.
    assert isinstance(aggregate, CliCommandAggregate)
    assert aggregate.id == 'test_group.test_feature'
    assert aggregate.name == 'Test Feature'
    assert aggregate.description == 'This is a test feature command.'
    assert aggregate.group_key == 'test-group'
    assert aggregate.key == 'test-feature'

# ** test: cli_command_aggregate_add_argument
def test_cli_command_aggregate_add_argument():
    '''
    Test adding an argument to a CLI command aggregate.
    '''

    # Create a CLI command aggregate.
    cli_command_data = dict(
        id='test_group.test_feature',
        group_key='test-group',
        key='test-feature',
        name='Test Feature',
        description='This is a test feature command.',
        arguments=[]
    )

    aggregate = CliCommandAggregate.new(**cli_command_data)

    # Add an argument using individual attributes.
    aggregate.add_argument(
        name_or_flags=['--new-arg', '-n'],
        description='New argument',
        required=False
    )

    # Assert the argument was added.
    assert len(aggregate.arguments) == 1
    assert aggregate.arguments[0].name_or_flags == ['--new-arg', '-n']
    assert aggregate.arguments[0].description == 'New argument'
    assert aggregate.arguments[0].required is False

# ** test: cli_command_aggregate_set_attribute
def test_cli_command_aggregate_set_attribute():
    '''
    Test updating attributes on a CLI command aggregate.
    '''

    # Create a CLI command aggregate.
    cli_command_data = dict(
        id='test_group.test_feature',
        group_key='test-group',
        key='test-feature',
        name='Test Feature',
        description='This is a test feature command.',
        arguments=[]
    )

    aggregate = CliCommandAggregate.new(**cli_command_data)

    # Update the name attribute.
    aggregate.set_attribute('name', 'Updated Feature Name')

    # Assert the attribute was updated.
    assert aggregate.name == 'Updated Feature Name'
