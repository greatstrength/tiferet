# *** imports

# ** infra
import pytest

# ** app
from ..feature import *


# *** fixtures

# ** fixture: feature_data_raw
@pytest.fixture
def feature_data():

    # Return the feature data.
    return DataObject.from_data(
        FeatureData,
        **dict(
        id='test.test_feature',
        name='Test Feature',
        description='This is a test feature.',
        group_id='test',
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
    ))


# *** tests

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
    assert feature_command.params == {'test_param': 'test_value'}
    assert feature_command.return_to_data == True
    assert feature_command.data_key == 'test_data'
    assert feature_command.pass_on_error == True