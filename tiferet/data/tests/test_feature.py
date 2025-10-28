"""Tiferet Feature Data Object Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ...models import (
    Feature,
    FeatureCommand,
)
from ..feature import (
    FeatureConfigData,
    FeatureCommandConfigData,
)

# *** fixtures

# ** fixture: feature_command_config_data
@pytest.fixture
def feature_command_config_data() -> FeatureCommandConfigData:
    '''
    A fixture for a feature command data object.

    :return: The feature command data object.
    :rtype: FeatureCommandData
    '''
    
    # Return the feature command data.
    return FeatureCommandConfigData(dict(
        name='Test Feature Command',
        attribute_id='test_feature_command',
        params={},
        return_to_data=True,
        data_key='test_data',
        pass_on_error=True
    ))

# ** fixture: feature_config_data
@pytest.fixture
def feature_config_data() -> FeatureConfigData:
    '''
    A fixture for a feature data object.

    :return: The feature data object.
    :rtype: FeatureData
    '''

    # Return the feature data.
    return FeatureConfigData.from_data(
        id='test_group.test_feature',
        name='Test Feature',
        description='This is a test feature.',
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
    )

# *** tests

# ** test: feature_command_data_init
def test_feature_command_data_init(feature_command_config_data: FeatureCommandConfigData):
    '''
    Test the feature command data initialization.

    :param feature_command_data: The feature command data object.
    :type feature_command_data: FeatureCommandData
    '''

    # Assert the feature command data attributes.
    assert feature_command_config_data.name == 'Test Feature Command'
    assert feature_command_config_data.attribute_id == 'test_feature_command'
    assert feature_command_config_data.parameters == {}
    assert feature_command_config_data.return_to_data == True
    assert feature_command_config_data.data_key == 'test_data'
    assert feature_command_config_data.pass_on_error == True

# ** test: feature_command_data_map
def test_feature_command_data_map(feature_command_config_data: FeatureCommandConfigData):
    '''
    Test the feature command data mapping.

    :param feature_command_data: The feature command data object.
    :type feature_command_data: FeatureCommandData
    '''

    # Map the feature command data to a feature command object.
    feature_command = feature_command_config_data.map()

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
def test_feature_data_from_data(feature_config_data: FeatureConfigData):
    '''
    Test the feature data from data method.

    :param feature_data: The feature data object.
    :type feature_data: FeatureData
    '''

    # Assert the feature data attributes.
    assert feature_config_data.name == 'Test Feature'
    assert feature_config_data.feature_key == 'test_feature'
    assert feature_config_data.description == 'This is a test feature.'
    assert feature_config_data.group_id == 'test_group'
    assert len(feature_config_data.commands) == 1

    # Assert the feature command data attributes.
    feature_command_data = feature_config_data.commands[0]
    assert feature_command_data.name == 'Test Feature Command'
    assert feature_command_data.attribute_id == 'test_feature_command'
    assert feature_command_data.parameters == {}
    assert feature_command_data.return_to_data == True
    assert feature_command_data.data_key == 'test_data'
    assert feature_command_data.pass_on_error == True

# ** test: feature_data_map
def test_feature_data_map(feature_config_data: FeatureConfigData):
    '''
    Test the feature data mapping.

    :param feature_data: The feature data object.
    :type feature_data: FeatureData
    '''

    # Map the feature data to a feature object.
    feature = feature_config_data.map()

    # Assert the feature type.
    assert isinstance(feature, Feature)

    # Assert the feature attributes.
    assert feature.name == 'Test Feature'
    assert feature.description == 'This is a test feature.'
    assert feature.group_id == 'test_group'
    assert len(feature.commands) == 1

    # Assert the feature command attributes.
    feature_command = feature.commands[0]
    assert feature_command.name == 'Test Feature Command'
    assert feature_command.attribute_id == 'test_feature_command'
    assert feature_command.parameters == {}
    assert feature_command.return_to_data == True
    assert feature_command.data_key == 'test_data'
    assert feature_command.pass_on_error == True