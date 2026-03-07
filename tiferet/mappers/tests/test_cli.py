"""Tiferet CLI Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ...domain import CliArgument, CliCommand, DomainObject
from ...assets import TiferetError
from ..settings import TransferObject
from ..cli import CliArgumentAggregate, CliCommandAggregate, CliCommandYamlObject

# *** fixtures

# ** fixture: cli_command_yaml_object
@pytest.fixture
def cli_command_yaml_object() -> CliCommandYamlObject:
    '''
    A fixture for a CLI command YAML data object with two arguments using the args alias.

    :return: The CLI command YAML data object.
    :rtype: CliCommandYamlObject
    '''

    # Create and return the CLI command YAML data object.
    return TransferObject.from_data(
        CliCommandYamlObject,
        id='calc.add',
        name='Add Number Command',
        description='Adds two numbers.',
        key='add',
        group_key='calc',
        args=[
            dict(
                name_or_flags=['a'],
                description='The first number to add.',
                type='str',
            ),
            dict(
                name_or_flags=['b'],
                description='The second number to add.',
                type='str',
            ),
        ],
    )

# *** tests

# ** test: cli_command_yaml_object_from_data
def test_cli_command_yaml_object_from_data(cli_command_yaml_object: CliCommandYamlObject):
    '''
    Test that the CliCommandYamlObject can be initialized from data with correct
    attributes and two arguments using the args alias.

    :param cli_command_yaml_object: The CLI command YAML data object.
    :type cli_command_yaml_object: CliCommandYamlObject
    '''

    # Assert the data is correctly initialized.
    assert isinstance(cli_command_yaml_object, CliCommandYamlObject)
    assert cli_command_yaml_object.id == 'calc.add'
    assert cli_command_yaml_object.name == 'Add Number Command'
    assert cli_command_yaml_object.description == 'Adds two numbers.'
    assert cli_command_yaml_object.key == 'add'
    assert cli_command_yaml_object.group_key == 'calc'

    # Assert the arguments are correctly initialized.
    assert len(cli_command_yaml_object.arguments) == 2
    assert cli_command_yaml_object.arguments[0].name_or_flags == ['a']
    assert cli_command_yaml_object.arguments[0].description == 'The first number to add.'
    assert cli_command_yaml_object.arguments[1].name_or_flags == ['b']
    assert cli_command_yaml_object.arguments[1].description == 'The second number to add.'


# ** test: cli_command_yaml_object_map
def test_cli_command_yaml_object_map(cli_command_yaml_object: CliCommandYamlObject):
    '''
    Test that map() produces a CliCommandAggregate with correct arguments.

    :param cli_command_yaml_object: The CLI command YAML data object.
    :type cli_command_yaml_object: CliCommandYamlObject
    '''

    # Map the CLI command YAML data to a CLI command aggregate.
    aggregate = cli_command_yaml_object.map()

    # Assert the mapped aggregate is valid.
    assert isinstance(aggregate, CliCommandAggregate)
    assert aggregate.id == 'calc.add'
    assert aggregate.name == 'Add Number Command'
    assert aggregate.key == 'add'
    assert aggregate.group_key == 'calc'

    # Assert the arguments are correctly mapped.
    assert len(aggregate.arguments) == 2
    assert aggregate.arguments[0].name_or_flags == ['a']
    assert aggregate.arguments[1].name_or_flags == ['b']


# ** test: cli_command_yaml_object_to_primitive
def test_cli_command_yaml_object_to_primitive(cli_command_yaml_object: CliCommandYamlObject):
    '''
    Test that custom to_primitive('to_data.yaml') serializes args correctly.

    :param cli_command_yaml_object: The CLI command YAML data object.
    :type cli_command_yaml_object: CliCommandYamlObject
    '''

    # Serialize the data to primitive format for YAML.
    primitive = cli_command_yaml_object.to_primitive('to_data.yaml')

    # Assert the primitive data is a dict with the expected keys.
    assert isinstance(primitive, dict)
    assert 'id' not in primitive
    assert 'args' in primitive
    assert len(primitive['args']) == 2
    assert primitive['args'][0]['name_or_flags'] == ['a']
    assert primitive['args'][1]['name_or_flags'] == ['b']
    assert primitive['name'] == 'Add Number Command'
    assert primitive['key'] == 'add'
    assert primitive['group_key'] == 'calc'


# ** test: cli_command_yaml_object_from_model
def test_cli_command_yaml_object_from_model():
    '''
    Test that from_model() from CliCommand.new() produces a valid YAML object.
    '''

    # Create a CliCommand domain object using the factory method.
    cli_command = CliCommand.new(
        group_key='calc',
        key='subtract',
        name='Subtract Number Command',
        description='Subtracts one number from another.',
        arguments=[
            DomainObject.new(
                CliArgument,
                name_or_flags=['a'],
                description='The number to subtract from.',
            ),
        ],
    )

    # Create a CliCommandYamlObject from the model.
    yaml_obj = CliCommandYamlObject.from_model(cli_command)

    # Assert the YAML object is valid.
    assert isinstance(yaml_obj, CliCommandYamlObject)
    assert yaml_obj.id == 'calc.subtract'
    assert yaml_obj.name == 'Subtract Number Command'
    assert yaml_obj.key == 'subtract'
    assert yaml_obj.group_key == 'calc'
    assert len(yaml_obj.arguments) == 1
    assert yaml_obj.arguments[0].name_or_flags == ['a']


# ** test: cli_command_aggregate_new
def test_cli_command_aggregate_new():
    '''
    Test that CliCommandAggregate.new() creates an aggregate with correct fields.
    '''

    # Create a new CLI command aggregate.
    aggregate = CliCommandAggregate.new(
        id='calc.multiply',
        name='Multiply Number Command',
        description='Multiplies two numbers.',
        key='multiply',
        group_key='calc',
        arguments=[],
    )

    # Assert the aggregate is correctly instantiated.
    assert isinstance(aggregate, CliCommandAggregate)
    assert aggregate.id == 'calc.multiply'
    assert aggregate.name == 'Multiply Number Command'
    assert aggregate.description == 'Multiplies two numbers.'
    assert aggregate.key == 'multiply'
    assert aggregate.group_key == 'calc'
    assert aggregate.arguments == []


# ** test: cli_command_aggregate_add_argument
def test_cli_command_aggregate_add_argument():
    '''
    Test that add_argument() correctly adds a CliArgument to the aggregate.
    '''

    # Create a CLI command aggregate with no arguments.
    aggregate = CliCommandAggregate.new(
        id='calc.divide',
        name='Divide Number Command',
        key='divide',
        group_key='calc',
    )

    # Add an argument to the command.
    aggregate.add_argument(
        name_or_flags=['a'],
        description='The numerator.',
        type='int',
    )

    # Assert the argument was added.
    assert len(aggregate.arguments) == 1
    assert isinstance(aggregate.arguments[0], CliArgument)
    assert aggregate.arguments[0].name_or_flags == ['a']
    assert aggregate.arguments[0].description == 'The numerator.'
    assert aggregate.arguments[0].type == 'int'


# ** test: cli_command_aggregate_set_attribute
def test_cli_command_aggregate_set_attribute():
    '''
    Test that set_attribute() updates supported attributes on the CLI command aggregate.
    '''

    # Create a CLI command aggregate.
    aggregate = CliCommandAggregate.new(
        id='calc.exp',
        name='Exponentiate Number Command',
        key='exp',
        group_key='calc',
    )

    # Update supported attributes.
    aggregate.set_attribute('name', 'Updated Exp Command')
    aggregate.set_attribute('description', 'Raises a number to a power.')

    # Assert the attributes were updated.
    assert aggregate.name == 'Updated Exp Command'
    assert aggregate.description == 'Raises a number to a power.'


# ** test: cli_argument_aggregate_new
def test_cli_argument_aggregate_new():
    '''
    Test that CliArgumentAggregate.new() creates an aggregate with all supported fields.
    '''

    # Create a new CLI argument aggregate with all supported fields.
    aggregate = CliArgumentAggregate.new(
        name_or_flags=['-v', '--verbose'],
        description='Enable verbose output.',
        type='str',
        required=False,
        default='false',
        action='store_true',
    )

    # Assert the aggregate is correctly instantiated.
    assert isinstance(aggregate, CliArgumentAggregate)
    assert aggregate.name_or_flags == ['-v', '--verbose']
    assert aggregate.description == 'Enable verbose output.'
    assert aggregate.type == 'str'
    assert aggregate.required is False
    assert aggregate.default == 'false'
    assert aggregate.action == 'store_true'


# ** test: cli_argument_aggregate_set_attribute
def test_cli_argument_aggregate_set_attribute():
    '''
    Test that set_attribute() updates supported attributes on the CLI argument aggregate.
    '''

    # Create a CLI argument aggregate.
    aggregate = CliArgumentAggregate.new(
        name_or_flags=['a'],
        description='Original description.',
    )

    # Update supported attributes.
    aggregate.set_attribute('description', 'Updated description.')
    aggregate.set_attribute('required', True)

    # Assert the attributes were updated.
    assert aggregate.description == 'Updated description.'
    assert aggregate.required is True


# ** test: cli_argument_aggregate_set_attribute_invalid
def test_cli_argument_aggregate_set_attribute_invalid():
    '''
    Test that set_attribute() raises TiferetError for unsupported attributes (name_or_flags).
    '''

    # Create a CLI argument aggregate.
    aggregate = CliArgumentAggregate.new(
        name_or_flags=['a'],
        description='Test argument.',
    )

    # Attempt to set an unsupported attribute and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        aggregate.set_attribute('name_or_flags', ['b'])

    # Verify that the correct error code is raised.
    assert exc_info.value.error_code == 'INVALID_MODEL_ATTRIBUTE'
    assert exc_info.value.kwargs.get('attribute') == 'name_or_flags'
