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
