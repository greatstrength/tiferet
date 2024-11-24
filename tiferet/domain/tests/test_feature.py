# *** imports

# ** infra
import pytest

# ** app
from . import *

# *** fixtures

# ** fixture: feature_command
@pytest.fixture
def feature_command():
    return FeatureCommand.new(
        name='test_command',
        attribute_id='test_attr',
        params={'param1': 'value1'},
        return_to_data=True,
        data_key='test_key',
        pass_on_error=False
    )


# ** fixture: feature
@pytest.fixture
def feature(feature_command):
    return Feature.new(
        name='Test Feature',
        group_id='test_group',
        feature_key='test_feature',
        description='A test feature',
        commands=[feature_command]
    )


# ** fixture: additional_feature_command
@pytest.fixture
def additional_feature_command():
    return FeatureCommand.new(
        name='additional_command',
        attribute_id='additional_attr',
        params={'param1': 'value1'},
        return_to_data=True,
        data_key='additional_key',
        pass_on_error=False
    )


# ** fixture: feature_no_desc
@pytest.fixture
def feature_no_desc():
    return Feature.new(
        name='Feature with no description',
        group_id='group',
        feature_key='key'
    )


# ** fixture: feature_name_and_group_only
@pytest.fixture
def feature_name_and_group_only():
    return Feature.new(
        name='Plain Feature',
        group_id='group'
    )


# ** fixture: feature_with_id
@pytest.fixture
def feature_with_id():
    return Feature.new(
        name='Feature with ID',
        group_id='test',
        id='test.feature_with_id'
    )


# *** tests

# ** test: test_feature_command_new
def test_feature_command_new(feature_command):

    # Test that the FeatureCommand object is created with the correct values
    assert feature_command.name == 'test_command'
    assert feature_command.attribute_id == 'test_attr'
    assert feature_command.params == {'param1': 'value1'}
    assert feature_command.return_to_data == True
    assert feature_command.data_key == 'test_key'
    assert feature_command.pass_on_error == False


# ** test: test_feature_new
def test_feature_new(feature):

    # Test that the Feature object is created with the correct values
    assert feature.name == 'Test Feature'
    assert feature.group_id == 'test_group'
    assert feature.id == 'test_group.test_feature'
    assert feature.description == 'A test feature'
    assert len(feature.commands) == 1


# ** test: test_feature_default_id
def test_feature_no_description(feature_no_desc):
   
    # Test that the default description is set correctly
    assert feature_no_desc.name == 'Feature with no description'
    assert feature_no_desc.description == 'Feature with no description'


# ** test: test_feature_add_handler
def test_feature_add_handler(feature, additional_feature_command):

    # Add another command
    feature.add_handler(additional_feature_command)
    assert len(feature.commands) == 2
    
    # Test that the new command is added to the list
    assert feature.commands[1].name == 'additional_command'
    assert feature.commands[1].attribute_id == 'additional_attr'
    assert feature.commands[1].params == {'param1': 'value1'}
    assert feature.commands[1].return_to_data == True
    assert feature.commands[1].data_key == 'additional_key'
    assert feature.commands[1].pass_on_error == False


# ** test: test_feature_add_handler_position
def test_feature_add_handler_position(feature, additional_feature_command):

    # Add another command at the beginning
    feature.add_handler(additional_feature_command, position=0)
    assert len(feature.commands) == 2
    
    # Test that the new command is added to the list
    assert feature.commands[0].name == 'additional_command'
    assert feature.commands[0].attribute_id == 'additional_attr'
    assert feature.commands[0].params == {'param1': 'value1'}
    assert feature.commands[0].return_to_data == True
    assert feature.commands[0].data_key == 'additional_key'
    assert feature.commands[0].pass_on_error == False


# ** test: test_feature_name_and_group_only
def test_feature_name_and_group_only(feature_name_and_group_only):

    # Test that the feature with only a name and group ID is created correctly
    assert feature_name_and_group_only.name == 'Plain Feature'
    assert feature_name_and_group_only.group_id == 'group'
    assert feature_name_and_group_only.id == 'group.plain_feature'
    assert feature_name_and_group_only.description == 'Plain Feature'
    assert len(feature_name_and_group_only.commands) == 0


# ** test: test_feature_with_id
def test_feature_with_id(feature_with_id):

    # Test that the feature with an ID is created correctly
    assert feature_with_id.name == 'Feature with ID'
    assert feature_with_id.group_id == 'test'
    assert feature_with_id.id == 'test.feature_with_id'
    assert feature_with_id.description == 'Feature with ID'
    assert len(feature_with_id.commands) == 0
