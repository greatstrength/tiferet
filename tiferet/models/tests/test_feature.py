"""Tiferet Feature Model Tests."""

# *** imports

# ** infra
import pytest

# ** app
from ..feature import (
    ModelObject,
    Feature,
    FeatureCommand,
)

# *** fixtures

# ** fixture: feature_command
@pytest.fixture
def feature_command() -> FeatureCommand:
    '''
    Fixture to create a FeatureCommand instance for testing.

    :return: The FeatureCommand instance.
    :rtype: FeatureCommand
    '''

    return ModelObject.new(
        FeatureCommand,
        name='Test Service Command',
        attribute_id=' test_feature_command',
        parameters={'param1': 'value1'},
    )

# ** fixture: feature
@pytest.fixture
def feature() -> Feature:
    '''
    Fixture to create a Feature instance for testing.

    :return: The Feature instance.
    :rtype: Feature
    '''

    return Feature.new(
        name='Test Feature',
        group_id='test_group',
        commands=[],
    )

# *** tests

# ** test: feature_new
def test_feature_new(feature_command: FeatureCommand):
    '''
    Fixture to create a Feature instance for testing.

    :param feature_command: The feature command to add to the feature.
    :type feature_command: FeatureCommand
    '''

    # Create new feature with all attributes.
    feature = Feature.new(
        name='Test Feature',
        group_id='test_group',
        feature_key='test_feature',
        id='test_group.test_feature',
        description='A test feature.',
        commands=[feature_command],
    )

    # Test that the feature is created correctly.
    assert feature.name == 'Test Feature'
    assert feature.group_id == 'test_group'
    assert feature.feature_key == 'test_feature'
    assert feature.id == 'test_group.test_feature'
    assert feature.description == 'A test feature.'
    assert len(feature.commands) == 1
    assert feature.commands[0] == feature_command

# ** test: feature_new_no_description
def test_feature_new_no_description():
    '''
    Test creating a Feature instance without a description.
    '''

    # Create new feature with no description.
    feature = Feature.new(
        name='Test Feature',
        group_id='test_group',
        feature_key='test_feature',
        id='test_group.test_feature',
        commands=[],
    )

    # Test that the default description is set correctly.
    assert feature.name == 'Test Feature'
    assert feature.group_id == 'test_group'
    assert feature.feature_key == 'test_feature'
    assert feature.id == 'test_group.test_feature'
    assert feature.description == feature.name
    assert len(feature.commands) == 0

# ** test: feature_new_name_and_group_only
def test_feature_new_name_and_group_only():

    # Create the feature with only the name and group ID.
    feature = Feature.new(
        name='Test Feature',
        group_id='test_group',
        description='A test feature.',
    )    

    # Test that the feature is created correctly.
    assert feature.name == 'Test Feature'
    assert feature.group_id == 'test_group'
    assert feature.feature_key == 'test_feature'
    assert feature.id == 'test_group.test_feature'
    assert feature.description == 'A test feature.'
    assert len(feature.commands) == 0

# ** test: feature_add_service_command
def test_feature_add_service_command(feature: Feature):
    '''
    Test adding a FeatureCommand to a Feature via raw attributes.

    :param feature: The feature to add the command to.
    :type feature: Feature
    '''

    command = feature.add_command(
        name='Test Service Command',
        attribute_id='test_feature_command',
        parameters={'param1': 'value1'},
    )
    assert len(feature.commands) == 1

    # Test that the new command is added to the list
    assert feature.commands[0] == command
    assert command.name == 'Test Service Command'
    assert command.attribute_id == 'test_feature_command'
    assert command.parameters == {'param1': 'value1'}

# ** test: feature_add_command_position
def test_feature_add_command_position(feature: Feature):

    # Add a command at the end.
    feature.add_command(
        name='Existing Command',
        attribute_id='existing_feature_command',
        parameters={'param1': 'value1'},
    )

    # Add a new command at the beginning.
    new_command = feature.add_command(
        name='New Service Command',
        attribute_id='new_feature_command',
        parameters={'param1': 'value1'},
        position=0,
    )

    # Test that the new command is added to the beginning of the list.
    assert len(feature.commands) == 2
    assert feature.commands[0] == new_command
    assert feature.commands[0].attribute_id == 'new_feature_command'

# ** test: feature_rename
def test_feature_rename(feature: Feature):
    '''
    Test the rename helper on Feature.
    '''

    feature.rename('Renamed Feature')
    assert feature.name == 'Renamed Feature'

# ** test: feature_set_description
def test_feature_set_description(feature: Feature):
    '''
    Test the set_description helper on Feature.
    '''

    feature.set_description('Updated description')
    assert feature.description == 'Updated description'


# ** test: feature_get_command_valid
def test_feature_get_command_valid(feature: Feature):
    '''
    Test that get_command returns the command at the given index.
    '''

    feature.add_command(
        name='First Command',
        attribute_id='first',
    )
    feature.add_command(
        name='Second Command',
        attribute_id='second',
    )

    cmd = feature.get_command(1)
    assert isinstance(cmd, FeatureCommand)
    assert cmd.name == 'Second Command'
    assert cmd.attribute_id == 'second'


# ** test: feature_get_command_out_of_range
def test_feature_get_command_out_of_range(feature: Feature):
    '''
    Test that get_command returns None when the index is out of range.
    '''

    feature.add_command(
        name='Only Command',
        attribute_id='only',
    )

    assert feature.get_command(5) is None
    assert feature.get_command(-5) is None


# ** test: feature_command_set_pass_on_error
def test_feature_command_set_pass_on_error(feature_command: FeatureCommand):
    '''
    Test the set_pass_on_error helper on FeatureCommand.
    '''

    feature_command.set_pass_on_error('false')
    assert feature_command.pass_on_error is False

    feature_command.set_pass_on_error('TRUE')
    assert feature_command.pass_on_error is True

    feature_command.set_pass_on_error(0)
    assert feature_command.pass_on_error is False

    feature_command.set_pass_on_error(1)
    assert feature_command.pass_on_error is True


# ** test: feature_command_set_parameters_merge
def test_feature_command_set_parameters_merge(feature_command: FeatureCommand):
    '''
    Test that set_parameters merges dictionaries and removes None values.
    '''

    assert feature_command.parameters == {'param1': 'value1'}

    feature_command.set_parameters({
        'param1': 'new',
        'param2': 'value2',
        'to_remove': None,
    })

    assert feature_command.parameters == {
        'param1': 'new',
        'param2': 'value2',
    }


# ** test: feature_command_set_attribute_parameters
def test_feature_command_set_attribute_parameters(feature_command: FeatureCommand):
    '''
    Test that set_attribute delegates parameter updates to set_parameters.
    '''

    feature_command.set_attribute('parameters', {'param1': 'updated'})
    assert feature_command.parameters == {'param1': 'updated'}


# ** test: feature_command_set_attribute_pass_on_error
def test_feature_command_set_attribute_pass_on_error(feature_command: FeatureCommand):
    '''
    Test that set_attribute delegates pass_on_error updates to set_pass_on_error.
    '''

    feature_command.set_attribute('pass_on_error', 'false')
    assert feature_command.pass_on_error is False


# ** test: feature_command_set_attribute_other
def test_feature_command_set_attribute_other(feature_command: FeatureCommand):
    '''
    Test that set_attribute falls back to setattr for other attributes.
    '''

    feature_command.set_attribute('data_key', 'foo')
    assert feature_command.data_key == 'foo'
