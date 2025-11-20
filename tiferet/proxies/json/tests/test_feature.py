"""Tiferet Feature JSON Proxy Tests Exports"""

# *** imports

# ** infra
import pytest
import json

# ** app
from ....commands import TiferetError
from ....data import DataObject, FeatureConfigData
from ..feature import FeatureJsonProxy

# *** fixtures

# ** fixture: feature_config_file_path
@pytest.fixture
def feature_config_file(tmp_path) -> str:
    '''
    A fixture for the feature configuration file path.

    :param tmp_path: The temporary path provided by pytest.
    :type tmp_path: pathlib.Path
    :return: The feature configuration file path.
    :rtype: str
    '''
    
    # Create a temporary JSON file with sample feature configuration content.
    file_path = tmp_path / 'test.json'

    # Write the sample feature configuration to the JSON file.
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'features': {
                'test_group': {
                    'test_feature': {
                        'name': 'Test Feature',
                        'description': 'A test feature.',
                        'commands': [
                            {
                                'attribute_id': 'test_feature_command',
                                'name': 'Test Feature Command',
                                'parameters': {
                                    'param1': 'value1'
                                }
                            }
                        ]
                    }
                }
            }
        }, f)

    # Return the file path as a string.
    return str(file_path)

# ** fixture: test_feature_json_proxy
@pytest.fixture
def feature_json_proxy(feature_config_file: str) -> FeatureJsonProxy:
    '''
    A fixture for the feature JSON proxy.

    :param feature_config_file_path: The feature configuration file path.
    :type feature_config_file_path: str
    :return: The feature JSON proxy.
    :rtype: FeatureJsonProxy
    '''

    # Create and return the feature JSON proxy.
    return FeatureJsonProxy(feature_config_file)

# *** tests

# ** test: feature_json_proxy_load_json
def test_feature_json_proxy_load_json(feature_json_proxy: FeatureJsonProxy):
    '''
    Test the feature JSON proxy load JSON method.

    :param feature_json_proxy: The feature JSON proxy.
    :type feature_json_proxy: FeatureJsonProxy
    '''

    # Load the JSON file.
    data = feature_json_proxy.load_json()

    # Check the loaded features.
    assert data
    assert data.get('features')
    assert len(data['features']) > 0

# ** test: feature_json_proxy_load_json_file_not_found
def test_feature_json_proxy_load_json_file_not_found(feature_json_proxy: FeatureJsonProxy):
    '''
    Test the feature JSON proxy load JSON method with a file not found error.

    :param feature_json_proxy: The feature JSON proxy.
    :type feature_json_proxy: FeatureJsonProxy
    '''

    # Set a non-existent configuration file.
    feature_json_proxy.json_file = 'non_existent_file.yml'

    # Attempt to load the JSON file.
    with pytest.raises(TiferetError) as exc_info:
        feature_json_proxy.load_json()

    # Verify the error message.
    assert exc_info.value.error_code == 'FEATURE_CONFIG_LOADING_FAILED'
    assert 'Unable to load feature configuration file' in str(exc_info.value)


# ** test: feature_json_proxy_get
def test_feature_json_proxy_get(
        feature_json_proxy: FeatureJsonProxy,
    ):
    '''
    Test the get method of the FeatureJsonProxy.

    :param feature_json_proxy: The feature JSON proxy.
    :type feature_json_proxy: FeatureJsonProxy
    :param feature: The Feature instance.
    :type feature: Feature
    '''
    
    # Get the feature.
    test_feature = feature_json_proxy.get('test_group.test_feature')

    # Check the feature.
    assert test_feature
    assert test_feature.id == 'test_group.test_feature'
    assert test_feature.name == 'Test Feature'
    assert test_feature.group_id == 'test_group'
    assert test_feature.feature_key == 'test_feature'
    assert test_feature.description == 'A test feature.'
    assert test_feature.commands
    assert len(test_feature.commands) == 1
    assert test_feature.commands[0].attribute_id == 'test_feature_command'
    assert test_feature.commands[0].name == 'Test Feature Command'
    assert test_feature.commands[0].parameters == {'param1': 'value1'}


# ** test: feature_json_proxy_exists
def test_feature_json_proxy_exists(
        feature_json_proxy: FeatureJsonProxy,
    ):
    '''
    Test the exists method of the FeatureJsonProxy.

    :param feature_json_proxy: The feature JSON proxy.
    :type feature_json_proxy: FeatureJsonProxy
    :param feature: The Feature instance.
    :type feature: Feature
    '''
    
    # Check the feature exists.
    assert feature_json_proxy.exists('test_group.test_feature')


# ** test: feature_json_proxy_exists_not_found
def test_feature_json_proxy_exists_not_found(feature_json_proxy: FeatureJsonProxy):
    '''
    Test the exists method of the FeatureJsonProxy for a non-existent feature.

    :param feature_json_proxy: The feature JSON proxy.
    :type feature_json_proxy: FeatureJsonProxy
    '''
    
    # Check the feature does not exist.
    assert not feature_json_proxy.exists('test_group.not_found')


# ** test: feature_json_proxy_list
def test_feature_json_proxy_list(
        feature_json_proxy: FeatureJsonProxy,
    ):
    '''
    Test the list method of the FeatureJsonProxy.

    :param feature_json_proxy: The feature JSON proxy.
    :type feature_json_proxy: FeatureJsonProxy
    :param feature: The Feature instance.
    :type feature: Feature
    '''
    
    # List the features.
    features = feature_json_proxy.list()
    
    # Check the features.
    assert features
    assert len(features) == 1
    assert features[0].id == 'test_group.test_feature'
    assert features[0].name == 'Test Feature'
    assert features[0].group_id == 'test_group'
    assert features[0].feature_key == 'test_feature'
    assert features[0].description == 'A test feature.'
    assert features[0].commands
    assert len(features[0].commands) == 1
    assert features[0].commands[0].attribute_id == 'test_feature_command'
    assert features[0].commands[0].name == 'Test Feature Command'
    assert features[0].commands[0].parameters == {'param1': 'value1'}

# ** test: feature_json_proxy_list_by_group_id
def test_feature_json_proxy_list_by_group_id(
        feature_json_proxy: FeatureJsonProxy,
    ):
    '''
    Test the list method of the FeatureJsonProxy with a group id.

    :param feature_json_proxy: The feature JSON proxy.
    :type feature_json_proxy: FeatureJsonProxy
    :param feature: The Feature instance.
    :type feature: Feature
    '''
    
    # List the features by group id.
    features = feature_json_proxy.list(group_id='test_group')
    
    # Check the features.
    assert features
    assert len(features) == 1
    assert features[0].id == 'test_group.test_feature'
    assert features[0].name == 'Test Feature'
    assert features[0].group_id == 'test_group'
    assert features[0].feature_key == 'test_feature'
    assert features[0].description == 'A test feature.'
    assert features[0].commands
    assert len(features[0].commands) == 1
    assert features[0].commands[0].attribute_id == 'test_feature_command'
    assert features[0].commands[0].name == 'Test Feature Command'
    assert features[0].commands[0].parameters == {'param1': 'value1'}

# ** test: feature_json_proxy_list_by_group_id_not_found
def test_feature_json_proxy_list_by_group_id_not_found(
        feature_json_proxy: FeatureJsonProxy,
    ):
    '''
    Test the list method of the FeatureJsonProxy with a non-existent group id.

    :param feature_json_proxy: The feature JSON proxy.
    :type feature_json_proxy: FeatureJsonProxy
    :param feature: The Feature instance.
    :type feature: Feature
    '''
    
    # List the features by a non-existent group id.
    features = feature_json_proxy.list(group_id='not_found')
    
    # Check the features.
    assert features == []

# ** test: feature_json_proxy_save
def test_feature_json_proxy_save(
        feature_json_proxy: FeatureJsonProxy,
    ):
    '''
    Test the save method of the FeatureJsonProxy.

    :param feature_json_proxy: The feature JSON proxy.
    :type feature_json_proxy: FeatureJsonProxy
    :param feature: The Feature instance.
    :type feature: Feature
    '''
    
    # Create a new feature to save.
    new_feature = DataObject.from_data(
        FeatureConfigData,
        id='new_group.new_feature',
        name='New Feature',
        group_id='new_group',
        feature_key='new_feature',
        description='A new feature.',
        commands=[
            {
                'attribute_id': 'new_feature_command',
                'name': 'New Feature Command',
                'parameters': {
                    'param1': 'value1'
                }
            }
        ]
    ).map()
    
    # Save the new feature.
    feature_json_proxy.save(new_feature)
    
    # Get the saved feature.
    saved_feature = feature_json_proxy.get('new_group.new_feature')
    
    # Check the saved feature.
    assert saved_feature
    assert saved_feature.id == 'new_group.new_feature'
    assert saved_feature.name == 'New Feature'
    assert saved_feature.group_id == 'new_group'
    assert saved_feature.feature_key == 'new_feature'
    assert saved_feature.description == 'A new feature.'
    assert saved_feature.commands
    assert len(saved_feature.commands) == 1
    assert saved_feature.commands[0].attribute_id == 'new_feature_command'
    assert saved_feature.commands[0].name == 'New Feature Command'
    assert saved_feature.commands[0].parameters == {'param1': 'value1'}

# ** test: feature_json_proxy_delete
def test_feature_json_proxy_delete(
        feature_json_proxy: FeatureJsonProxy,
    ):
    '''
    Test the save method of the FeatureJsonProxy for updating an existing feature.

    :param feature_json_proxy: The feature JSON proxy.
    :type feature_json_proxy: FeatureJsonProxy
    :param feature: The Feature instance.
    :type feature: Feature
    '''
    
    # Delete the existing feature.
    feature_json_proxy.delete('test_group.test_feature')

    # Attempt to retireve the deleted feature.
    deleted_feature = feature_json_proxy.get('test_group.test_feature')

    # Check that the feature is None.
    assert deleted_feature is None