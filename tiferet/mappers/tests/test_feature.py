"""Tiferet Feature Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import (
    TransferObject,
)
from ..feature import (
    FeatureYamlObject,
    FeatureCommandYamlObject,
    FeatureAggregate,
    FeatureCommandAggregate,
)
from ...domain import (
    Feature,
    FeatureCommand,
)

# *** fixtures

# ** fixture: feature_command_yaml_object
@pytest.fixture
def feature_command_yaml_object() -> FeatureCommandYamlObject:
    '''
    A fixture for a feature command YAML object.

    :return: The feature command YAML object.
    :rtype: FeatureCommandYamlObject
    '''

    # Return the feature command YAML object.
    return TransferObject.from_data(
        FeatureCommandYamlObject,
        name='Test Feature Command',
        attribute_id='test_feature_command',
        params={},
        return_to_data=True,
        data_key='test_data',
        pass_on_error=True
    )

# ** fixture: feature_yaml_object
@pytest.fixture
def feature_yaml_object() -> FeatureYamlObject:
    '''
    A fixture for a feature YAML object.

    :return: The feature YAML object.
    :rtype: FeatureYamlObject
    '''

    # Return the feature YAML object.
    return TransferObject.from_data(
        FeatureYamlObject,
        id='test_group.test_feature',
        name='Test Feature',
        description='This is a test feature.',
        feature_key='test_feature',
        group_id='test_group',
        commands=[
            dict(
                name='Test Feature Command',
                attribute_id='test_feature_command',
                params={'test_param': 'test_value'},
                return_to_data=True,
                data_key='test_data',
                pass_on_error=True
            )
        ]
    )

# *** tests

# ** test: feature_command_data_init
def test_feature_command_data_init(feature_command_yaml_object: FeatureCommandYamlObject):
    '''
    Test the feature command data initialization.

    :param feature_command_data: The feature command data object.
    :type feature_command_data: FeatureCommandData
    '''

    # Assert the feature command data attributes.
    assert feature_command_yaml_object.name == 'Test Feature Command'
    assert feature_command_yaml_object.attribute_id == 'test_feature_command'
    assert feature_command_yaml_object.parameters == {}
    assert feature_command_yaml_object.return_to_data == True
    assert feature_command_yaml_object.data_key == 'test_data'
    assert feature_command_yaml_object.pass_on_error == True

# ** test: feature_command_data_map
def test_feature_command_data_map(feature_command_yaml_object: FeatureCommandYamlObject):
    '''
    Test the feature command data mapping.

    :param feature_command_data: The feature command data object.
    :type feature_command_data: FeatureCommandData
    '''

    # Map the feature command data to a feature command object.
    feature_command = feature_command_yaml_object.map()

    # Assert the feature command type.
    assert isinstance(feature_command, FeatureCommand)

    # Assert the feature command attributes.
    assert feature_command.name == 'Test Feature Command'
    assert feature_command.attribute_id == 'test_feature_command'
    assert feature_command.parameters == {}
    assert feature_command.return_to_data == True
    assert feature_command.data_key == 'test_data'
    assert feature_command.pass_on_error == True

# ** test: feature_data_from_data
def test_feature_data_from_data(feature_yaml_object: FeatureYamlObject):
    '''
    Test the feature data from data method.

    :param feature_data: The feature data object.
    :type feature_data: FeatureData
    '''

    # Assert the feature data attributes.
    assert feature_yaml_object.name == 'Test Feature'
    assert feature_yaml_object.feature_key == 'test_feature'
    assert feature_yaml_object.description == 'This is a test feature.'
    assert feature_yaml_object.group_id == 'test_group'
    assert len(feature_yaml_object.commands) == 1

    # Assert the feature command data attributes.
    feature_command_data = feature_yaml_object.commands[0]
    assert feature_command_data.name == 'Test Feature Command'
    assert feature_command_data.attribute_id == 'test_feature_command'
    assert feature_command_data.parameters == {'test_param': 'test_value'}
    assert feature_command_data.return_to_data == True
    assert feature_command_data.data_key == 'test_data'
    assert feature_command_data.pass_on_error == True

# ** test: feature_data_map
def test_feature_data_map(feature_yaml_object: FeatureYamlObject):
    '''
    Test the feature YAML object mapping.

    :param feature_yaml_object: The feature YAML object.
    :type feature_yaml_object: FeatureYamlObject
    '''

    # Map the feature data to a feature aggregate.
    feature = feature_yaml_object.map()

    # Assert the feature type.
    assert isinstance(feature, FeatureAggregate)

    # Assert the feature attributes.
    assert feature.name == 'Test Feature'
    assert feature.feature_key == 'test_feature'
    assert feature.description == 'This is a test feature.'
    assert feature.group_id == 'test_group'
    assert len(feature.commands) == 1

    # Assert the feature command attributes.
    feature_command = feature.commands[0]
    assert feature_command.name == 'Test Feature Command'
    assert feature_command.attribute_id == 'test_feature_command'
    assert feature_command.parameters == {'test_param': 'test_value'}
    assert feature_command.return_to_data == True
    assert feature_command.data_key == 'test_data'
    assert feature_command.pass_on_error == True

# ** test: feature_aggregate_new
def test_feature_aggregate_new():
    '''
    Test creating a new FeatureAggregate.
    '''

    # Create a feature aggregate.
    aggregate = FeatureAggregate.new(
        name='Test Feature',
        group_id='test_group',
    )

    # Assert the aggregate is valid.
    assert isinstance(aggregate, FeatureAggregate)
    assert aggregate.id == 'test_group.test_feature'
    assert aggregate.feature_key == 'test_feature'
    assert aggregate.name == 'Test Feature'

# ** test: feature_aggregate_add_command
def test_feature_aggregate_add_command():
    '''
    Test adding a command to a FeatureAggregate.
    '''

    # Create a feature aggregate.
    aggregate = FeatureAggregate.new(
        name='Test Feature',
        group_id='test_group',
        commands=[],
    )

    # Add a command using raw attributes.
    command = aggregate.add_command(
        name='Test Command',
        attribute_id='test_attr',
        parameters={'p1': 'v1'},
    )

    # Assert the command was added.
    assert len(aggregate.commands) == 1
    assert aggregate.commands[0] is command
    assert command.pass_on_error is False

# ** test: feature_aggregate_add_command_position
def test_feature_aggregate_add_command_position():
    '''
    Test inserting a command at a specific position in a FeatureAggregate.
    '''

    # Create a feature aggregate.
    aggregate = FeatureAggregate.new(
        name='Test Feature',
        group_id='test_group',
        commands=[],
    )

    # Add two commands.
    first = aggregate.add_command(
        name='First Command',
        attribute_id='first_attr',
    )
    inserted = aggregate.add_command(
        name='Inserted Command',
        attribute_id='inserted_attr',
        position=0,
    )

    # Assert the inserted command is at position 0.
    assert aggregate.commands[0] is inserted
    assert aggregate.commands[1] is first

# ** test: feature_aggregate_remove_command
def test_feature_aggregate_remove_command():
    '''
    Test removing a command from a FeatureAggregate.
    '''

    # Create a feature aggregate with commands.
    aggregate = FeatureAggregate.new(
        name='Test Feature',
        group_id='test_group',
        commands=[],
    )
    first = aggregate.add_command(name='First', attribute_id='a')
    second = aggregate.add_command(name='Second', attribute_id='b')

    # Remove the first command.
    removed = aggregate.remove_command(0)
    assert removed is first
    assert aggregate.commands == [second]

    # Invalid positions return None.
    assert aggregate.remove_command(5) is None
    assert aggregate.remove_command(-1) is None

# ** test: feature_aggregate_reorder_command
def test_feature_aggregate_reorder_command():
    '''
    Test reordering commands in a FeatureAggregate.
    '''

    # Create a feature aggregate with commands.
    aggregate = FeatureAggregate.new(
        name='Test Feature',
        group_id='test_group',
        commands=[],
    )
    first = aggregate.add_command(name='First', attribute_id='a')
    second = aggregate.add_command(name='Second', attribute_id='b')
    third = aggregate.add_command(name='Third', attribute_id='c')

    # Move first command to the end.
    moved = aggregate.reorder_command(0, 2)
    assert moved is first
    assert aggregate.commands == [second, third, first]

    # Invalid current position returns None.
    assert aggregate.reorder_command(5, 0) is None

# ** test: feature_aggregate_rename
def test_feature_aggregate_rename():
    '''
    Test renaming a FeatureAggregate.
    '''

    # Create a feature aggregate.
    aggregate = FeatureAggregate.new(
        name='Original Name',
        group_id='test_group',
    )

    # Rename the feature.
    aggregate.rename('Renamed Feature')

    # Assert only the name changed.
    assert aggregate.name == 'Renamed Feature'
    assert aggregate.id == 'test_group.original_name'

# ** test: feature_aggregate_set_description
def test_feature_aggregate_set_description():
    '''
    Test setting description on a FeatureAggregate.
    '''

    # Create a feature aggregate.
    aggregate = FeatureAggregate.new(
        name='Test Feature',
        group_id='test_group',
    )

    # Set a new description.
    aggregate.set_description('New description.')
    assert aggregate.description == 'New description.'

    # Clear the description.
    aggregate.set_description(None)
    assert aggregate.description is None

# ** test: feature_command_aggregate_set_pass_on_error
def test_feature_command_aggregate_set_pass_on_error():
    '''
    Test ``set_pass_on_error`` on FeatureCommandAggregate.
    '''

    # Create a feature command aggregate.
    aggregate = FeatureCommandAggregate.new(
        name='Test Command',
        attribute_id='attr',
    )

    # Explicit "false" string should result in False.
    aggregate.set_pass_on_error('false')
    assert aggregate.pass_on_error is False

    # Mixed-case should also be False.
    aggregate.set_pass_on_error('False')
    assert aggregate.pass_on_error is False

    # Truthy value should result in True.
    aggregate.set_pass_on_error(1)
    assert aggregate.pass_on_error is True

# ** test: feature_command_aggregate_set_parameters
def test_feature_command_aggregate_set_parameters():
    '''
    Test ``set_parameters`` merge and cleanup on FeatureCommandAggregate.
    '''

    # Create a feature command aggregate with initial parameters.
    aggregate = FeatureCommandAggregate.new(
        name='Test Command',
        attribute_id='attr',
        parameters={'a': '1', 'b': '2'},
    )

    # Merge new parameters.
    aggregate.set_parameters({'b': '3', 'c': None})
    assert aggregate.parameters == {'a': '1', 'b': '3'}

    # None should be a no-op.
    aggregate.set_parameters(None)
    assert aggregate.parameters == {'a': '1', 'b': '3'}

# ** test: feature_command_aggregate_set_attribute
def test_feature_command_aggregate_set_attribute():
    '''
    Test ``set_attribute`` delegation on FeatureCommandAggregate.
    '''

    # Create a feature command aggregate.
    aggregate = FeatureCommandAggregate.new(
        name='Test Command',
        attribute_id='attr',
        parameters={'a': '1'},
    )

    # Update parameters via set_attribute.
    aggregate.set_attribute('parameters', {'a': None, 'b': '2'})
    assert aggregate.parameters == {'b': '2'}

    # Update pass_on_error via set_attribute.
    aggregate.set_attribute('pass_on_error', 'false')
    assert aggregate.pass_on_error is False

    # Fallback to setattr for other attributes.
    aggregate.set_attribute('data_key', 'result')
    assert aggregate.data_key == 'result'
