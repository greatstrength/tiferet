"""Tiferet Feature YAML Proxy Tests Exports"""

# *** imports

# ** infra
import pytest
import yaml

# ** app
from ....commands import TiferetError
from ....data import DataObject, FeatureConfigData
from ..feature import FeatureYamlProxy

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
    
    # Create a temporary YAML file with sample feature configuration content.
    file_path = tmp_path / 'test.yaml'

    # Write the sample feature configuration to the YAML file.
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump({
            'features': {
                'test_group.test_feature': {
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
        }, f)

    # Return the file path as a string.
    return str(file_path)

# ** fixture: test_feature_yaml_proxy
@pytest.fixture
def feature_yaml_proxy(feature_config_file: str) -> FeatureYamlProxy:
    '''
    A fixture for the feature YAML proxy.

    :param feature_config_file_path: The feature configuration file path.
    :type feature_config_file_path: str
    :return: The feature YAML proxy.
    :rtype: FeatureYamlProxy
    '''

    # Create and return the feature YAML proxy.
    return FeatureYamlProxy(feature_config_file)

# *** tests

# ** test: feature_yaml_proxy_load_yaml
def test_feature_yaml_proxy_load_yaml(feature_yaml_proxy: FeatureYamlProxy):
    '''
    Test the feature YAML proxy load YAML method.

    :param feature_yaml_proxy: The feature YAML proxy.
    :type feature_yaml_proxy: FeatureYamlProxy
    '''

    # Load the YAML file.
    data = feature_yaml_proxy.load_yaml()

    # Check the loaded features.
    assert data
    assert data.get('features')
    assert len(data['features']) > 0

# ** test: feature_yaml_proxy_load_yaml_file_not_found
def test_feature_yaml_proxy_load_yaml_file_not_found(feature_yaml_proxy: FeatureYamlProxy):
    '''
    Test the feature YAML proxy load YAML method with a file not found error.

    :param feature_yaml_proxy: The feature YAML proxy.
    :type feature_yaml_proxy: FeatureYamlProxy
    '''

    # Set a non-existent configuration file.
    feature_yaml_proxy.yaml_file = 'non_existent_file.yml'

    # Attempt to load the YAML file.
    with pytest.raises(TiferetError) as exc_info:
        feature_yaml_proxy.load_yaml()

    # Verify the error message.
    assert exc_info.value.error_code == 'FEATURE_CONFIG_LOADING_FAILED'
    assert 'Unable to load feature configuration file' in str(exc_info.value)


# ** test: feature_yaml_proxy_get
def test_feature_yaml_proxy_get(
        feature_yaml_proxy: FeatureYamlProxy,
    ):
    '''
    Test the get method of the FeatureYamlProxy.

    :param feature_yaml_proxy: The feature YAML proxy.
    :type feature_yaml_proxy: FeatureYamlProxy
    :param feature: The Feature instance.
    :type feature: Feature
    '''
    
    # Get the feature.
    test_feature = feature_yaml_proxy.get('test_group.test_feature')

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


# ** test: feature_yaml_proxy_exists
def test_feature_yaml_proxy_exists(
        feature_yaml_proxy: FeatureYamlProxy,
    ):
    '''
    Test the exists method of the FeatureYamlProxy.

    :param feature_yaml_proxy: The feature YAML proxy.
    :type feature_yaml_proxy: FeatureYamlProxy
    :param feature: The Feature instance.
    :type feature: Feature
    '''
    
    # Check the feature exists.
    assert feature_yaml_proxy.exists('test_group.test_feature')


# ** test: feature_yaml_proxy_exists_not_found
def test_feature_yaml_proxy_exists_not_found(feature_yaml_proxy: FeatureYamlProxy):
    '''
    Test the exists method of the FeatureYamlProxy for a non-existent feature.

    :param feature_yaml_proxy: The feature YAML proxy.
    :type feature_yaml_proxy: FeatureYamlProxy
    '''
    
    # Check the feature does not exist.
    assert not feature_yaml_proxy.exists('not_found')


# ** test: feature_yaml_proxy_list
def test_feature_yaml_proxy_list(
        feature_yaml_proxy: FeatureYamlProxy,
    ):
    '''
    Test the list method of the FeatureYamlProxy.

    :param feature_yaml_proxy: The feature YAML proxy.
    :type feature_yaml_proxy: FeatureYamlProxy
    :param feature: The Feature instance.
    :type feature: Feature
    '''
    
    # List the features.
    features = feature_yaml_proxy.list()
    
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

# ** test: feature_yaml_proxy_list_by_group_id
def test_feature_yaml_proxy_list_by_group_id(
        feature_yaml_proxy: FeatureYamlProxy,
    ):
    '''
    Test the list method of the FeatureYamlProxy with a group id.

    :param feature_yaml_proxy: The feature YAML proxy.
    :type feature_yaml_proxy: FeatureYamlProxy
    :param feature: The Feature instance.
    :type feature: Feature
    '''
    
    # List the features by group id.
    features = feature_yaml_proxy.list(group_id='test_group')
    
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

# ** test: feature_yaml_proxy_list_by_group_id_not_found
def test_feature_yaml_proxy_list_by_group_id_not_found(
        feature_yaml_proxy: FeatureYamlProxy,
    ):
    '''
    Test the list method of the FeatureYamlProxy with a non-existent group id.

    :param feature_yaml_proxy: The feature YAML proxy.
    :type feature_yaml_proxy: FeatureYamlProxy
    :param feature: The Feature instance.
    :type feature: Feature
    '''
    
    # List the features by a non-existent group id.
    features = feature_yaml_proxy.list(group_id='not_found')
    
    # Check the features.
    assert features == []

# ** test: feature_yaml_proxy_save
def test_feature_yaml_proxy_save(
        feature_yaml_proxy: FeatureYamlProxy,
    ):
    '''
    Test the save method of the FeatureYamlProxy.

    :param feature_yaml_proxy: The feature YAML proxy.
    :type feature_yaml_proxy: FeatureYamlProxy
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
    )
    
    # Save the new feature.
    feature_yaml_proxy.save(new_feature)
    
    # Get the saved feature.
    saved_feature = feature_yaml_proxy.get('new_group.new_feature')
    
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

# ** test: error_yaml_proxy_delete
def test_feature_yaml_proxy_save_update(
        feature_yaml_proxy: FeatureYamlProxy,
    ):
    '''
    Test the save method of the FeatureYamlProxy for updating an existing feature.

    :param feature_yaml_proxy: The feature YAML proxy.
    :type feature_yaml_proxy: FeatureYamlProxy
    :param feature: The Feature instance.
    :type feature: Feature
    '''
    
    # Delete the existing feature.
    feature_yaml_proxy.delete('test_group.test_feature')

    # Attempt to retireve the deleted feature.
    deleted_feature = feature_yaml_proxy.get('test_group.test_feature')

    # Check that the feature is None.
    assert deleted_feature is None