# *** imports

# ** infra
import pytest

# ** app
from . import *

# *** fixtures



# *** tests

# ** test: test_feature_command_new
def test_feature_command_new(test_feature_command):

    # Test that the FeatureCommand object is created with the correct values
    assert test_feature_command.name == 'Test Feature Command'
    assert test_feature_command.attribute_id == 'test_feature'
    assert test_feature_command.params == {'param1': 'value1', 'param2': 'value2'}
    assert test_feature_command.return_to_data == False
    assert test_feature_command.data_key == 'test_key'
    assert test_feature_command.pass_on_error == False


# ** test: test_feature_new
def test_feature_new(test_feature):

    # Test that the Feature object is created with the correct values
    assert test_feature.name == 'Test Feature'
    assert test_feature.group_id == 'test_group'
    assert test_feature.id == 'test_group.test_feature'
    assert test_feature.description == 'A test feature.'
    assert len(test_feature.commands) == 1


# ** test: test_feature_new_default_no_description
def test_feature_new_no_description(test_feature_no_desc):
   
    # Test that the default description is set correctly
    assert test_feature_no_desc.name == 'Feature with no description'
    assert test_feature_no_desc.description == 'Feature with no description'


# ** test: test_feature_new_name_and_group_only
def test_feature_new_name_and_group_only(test_feature_name_and_group_only):

    # Test that the feature with only a name and group ID is created correctly
    assert test_feature_name_and_group_only.name == 'Plain Feature'
    assert test_feature_name_and_group_only.group_id == 'group'
    assert test_feature_name_and_group_only.id == 'group.plain_feature'
    assert test_feature_name_and_group_only.description == 'Plain Feature'
    assert len(test_feature_name_and_group_only.commands) == 0


# ** test: test_feature_new_with_id
def test_feature_new_with_id(test_feature_with_id):

    # Test that the feature with an ID is created correctly
    assert test_feature_with_id.name == 'Feature with ID'
    assert test_feature_with_id.group_id == 'test'
    assert test_feature_with_id.id == 'test.feature_with_id'
    assert test_feature_with_id.description == 'Feature with ID'
    assert len(test_feature_with_id.commands) == 0


# ** test: test_feature_add_handler
def test_feature_add_handler(test_feature, test_feature_command_to_add):

    # Add another command
    test_feature.add_handler(test_feature_command_to_add)
    assert len(test_feature.commands) == 2
    
    # Test that the new command is added to the list
    assert test_feature.commands[1] == test_feature_command_to_add


# ** test: test_feature_add_handler_position
def test_feature_add_handler_position(test_feature, test_feature_command_to_add):

    # Add another command at the beginning
    test_feature.add_handler(test_feature_command_to_add, position=0)
    assert len(test_feature.commands) == 2
    
    # Test that the new command is added to the list
    assert test_feature.commands[0] == test_feature_command_to_add
