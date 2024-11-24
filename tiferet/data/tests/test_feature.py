# *** imports

# ** infra
import pytest

# ** app
from . import *


# *** fixtures

# ** fixture: feature_command_data
@pytest.fixture
def feature_command_data():
    
    # Return the feature command data.
    return FeatureCommandData(dict(
        name='Test Feature Command',
        attribute_id='test_feature_command',
        params={},
        return_to_data=True,
        data_key='test_data',
        pass_on_error=True
    ))


# ** fixture: feature_data
@pytest.fixture
def feature_data():

    # Return the feature data.
    return FeatureData.from_data(**dict(
        id='test.test_feature',
        name='Test Feature',
        description='This is a test feature.',
        group_id='test',
        commands=[
            dict(
                name='Test Feature Command',
                attribute_id='test_feature_command',
                params={},
                return_to_data=True,
                data_key='test_data',
                pass_on_error=True
            )
        ]
    ))


# *** tests

# ** test: test_feature_command_data_init
def test_feature_command_data_init(feature_command_data):
    '''
    Test the feature command data initialization.
    '''
    
    # Assert the feature command data attributes.
    assert feature_command_data.name == 'Test Feature Command'
    assert feature_command_data.attribute_id == 'test_feature_command'
    assert feature_command_data.params == {}
    assert feature_command_data.return_to_data == True
    assert feature_command_data.data_key == 'test_data'
    assert feature_command_data.pass_on_error == True


# ** test: test_feature_command_data_map
def test_feature_command_data_map(feature_command_data):
    '''
    Test the feature command data mapping.
    '''
    
    # Map the feature command data to a feature command object.
    feature_command = feature_command_data.map()

    # Assert the feature command type.
    assert isinstance(feature_command, FeatureCommand)
    
    # Assert the feature command attributes.
    assert feature_command.name == 'Test Feature Command'
    assert feature_command.attribute_id == 'test_feature_command'
    assert feature_command.params == {}
    assert feature_command.return_to_data == True
    assert feature_command.data_key == 'test_data'
    assert feature_command.pass_on_error == True


# ** test: test_feature_data_from_data
def test_feature_data_from_data(feature_data):
    '''
    Test the feature data from data method.
    '''
    
    # Assert the feature data attributes.
    assert feature_data.name == 'Test Feature'
    assert feature_data.feature_key == 'test_feature'
    assert feature_data.description == 'This is a test feature.'
    assert feature_data.group_id == 'test'
    assert len(feature_data.commands) == 1
    
    # Assert the feature command data attributes.
    feature_command_data = feature_data.commands[0]
    assert feature_command_data.name == 'Test Feature Command'
    assert feature_command_data.attribute_id == 'test_feature_command'
    assert feature_command_data.params == {}
    assert feature_command_data.return_to_data == True
    assert feature_command_data.data_key == 'test_data'
    assert feature_command_data.pass_on_error == True


# ** test: test_feature_data_map
def test_feature_data_map(feature_data):
    '''
    Test the feature data mapping.
    '''
    
    # Map the feature data to a feature object.
    feature = feature_data.map()

    # Assert the feature type.
    assert isinstance(feature, Feature)
    
    # Assert the feature attributes.
    assert feature.name == 'Test Feature'
    assert feature.description == 'This is a test feature.'
    assert feature.group_id == 'test'
    assert len(feature.commands) == 1
    
    # Assert the feature command attributes.
    feature_command = feature.commands[0]
    assert feature_command.name == 'Test Feature Command'
    assert feature_command.attribute_id == 'test_feature_command'
    assert feature_command.params == {}
    assert feature_command.return_to_data == True
    assert feature_command.data_key == 'test_data'
    assert feature_command.pass_on_error == True