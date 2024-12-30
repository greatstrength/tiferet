# *** imports

# ** infra
import pytest

# ** app
from ..feature import *
from . import *


# *** fixtures

# ** fixture: feature_command
@pytest.fixture
def service_command() -> ServiceCommand:
    return ValueObject.new(
        ServiceCommand,
        name='Test Service Command',
        attribute_id='test_service_command',
        params={'param1': 'value1'},
    )


@pytest.fixture
def feature() -> Feature:
    return Feature.new(
        name='Test Feature',
        group_id='test_group',
        commands=[],
    )

# *** tests

# ** test: test_feature_new
def test_feature_new(service_command):

    # Create new feature with all attributes.
    feature = Feature.new(
        name='Test Feature',
        group_id='test_group',
        feature_key='test_feature',
        id='test_group.test_feature',
        description='A test feature.',
        commands=[service_command],
    )

    # Test that the feature is created correctly.
    assert feature.name == 'Test Feature'
    assert feature.group_id == 'test_group'
    assert feature.feature_key == 'test_feature'
    assert feature.id == 'test_group.test_feature'
    assert feature.description == 'A test feature.'
    assert len(feature.commands) == 1
    assert feature.commands[0] == service_command


# ** test: test_feature_new_no_description
def test_feature_new_no_description():
    
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


# ** test: test_feature_new_name_and_group_only
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


# ** test: test_feature_add_service_command
def test_feature_add_service_command(feature, service_command):

    # Add another command
    feature.add_command(service_command)
    assert len(feature.commands) == 1
    
    # Test that the new command is added to the list
    assert feature.commands[0] == service_command


# ** test: test_feature_add_command_position
def test_feature_add_command_position(feature, service_command):

    # Add a command at the beginning
    feature.add_command(service_command)
    
    # Create a new command and add it at the beginning.
    new_command = ValueObject.new(
        ServiceCommand,
        name='New Service Command',
        attribute_id='new_service_command',
        params={'param1': 'value1'},
    )
    feature.add_command(new_command, 0)

    # Test that the new command is added to the beginning of the list.
    assert len(feature.commands) == 2
    assert feature.commands[0] == new_command
