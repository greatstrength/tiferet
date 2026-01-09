"""Tiferet Feature Model Tests."""

# *** imports

# ** infra
import pytest

# ** app
from ..feature import Feature

# *** fixtures


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
def test_feature_new():
    '''
    Test creating a Feature instance with all attributes.
    '''

    # Create new feature with all attributes.
    feature = Feature.new(
        name='Test Feature',
        group_id='test_group',
        feature_key='test_feature',
        id='test_group.test_feature',
        description='A test feature.',
        commands=[],
    )

    # Test that the feature is created correctly.
    assert feature.name == 'Test Feature'
    assert feature.group_id == 'test_group'
    assert feature.feature_key == 'test_feature'
    assert feature.id == 'test_group.test_feature'
    assert feature.description == 'A test feature.'
    assert len(feature.commands) == 0

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
    Test adding a FeatureCommand to a Feature using raw attributes.

    :param feature: The feature to add the command to.
    :type feature: Feature
    '''

    # Add a command using raw attributes.
    command = feature.add_command(
        name='Test Service Command',
        attribute_id='test_feature_command',
        parameters={'param1': 'value1'},
    )

    # Test that the new command is added to the list.
    assert len(feature.commands) == 1
    assert feature.commands[0] == command

# ** test: feature_add_command_position
def test_feature_add_command_position(feature: Feature):
    '''
    Test inserting a feature command at a specific position.

    :param feature: The feature to add the commands to.
    :type feature: Feature
    '''

    # Add an initial command.
    first_command = feature.add_command(
        name='Initial Service Command',
        attribute_id='initial_feature_command',
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
    assert feature.commands[1] == first_command
