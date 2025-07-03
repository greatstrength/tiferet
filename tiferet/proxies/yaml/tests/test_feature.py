# *** imports

# ** infra
import pytest

# ** app
from ....configs import TiferetError
from ....models.feature import *
from ...yaml.feature import FeatureYamlProxy


# *** fixtures

# ** fixture: feature_config_file_path
@pytest.fixture
def feature_config_file_path():
    return 'tiferet/configs/tests/test.yml'


# ** fixture: test_feature_yaml_proxy
@pytest.fixture
def feature_yaml_proxy(feature_config_file_path):
    return FeatureYamlProxy(feature_config_file_path)


# ** fixture: feature
@pytest.fixture
def feature() -> Feature:
    return Feature.new(
        **dict(
            id='test_group.test_feature',
            name='Test Feature',
            group_id='test_group',
            feature_key='test_feature',
            description='A test feature.',
            commands=[
                dict(
                    attribute_id='test_feature_command',
                    name='Test Feature Command',
                    parameters={'param1': 'value1'},
                )
            ]
        )
    )


# *** tests

# ** test: int_feature_yaml_proxy_load_yaml
def test_int_feature_yaml_proxy_load_yaml(feature_yaml_proxy, feature):
    '''
    Test the feature YAML proxy load YAML method.
    '''

    # Load the YAML file.
    data = feature_yaml_proxy.load_yaml()

    # Check the loaded features.
    assert data
    assert data.get('features')
    assert len(data['features']) > 0

# ** test: int_feature_yaml_proxy_load_yaml_file_not_found
def test_int_feature_yaml_proxy_load_yaml_file_not_found(feature_yaml_proxy):
    '''
    Test the feature YAML proxy load YAML method with a file not found error.
    '''

    # Set a non-existent configuration file.
    feature_yaml_proxy.config_file = 'non_existent_file.yml'

    # Attempt to load the YAML file.
    with pytest.raises(TiferetError) as exc_info:
        feature_yaml_proxy.load_yaml()

    # Verify the error message.
    assert exc_info.value.error_code == 'FEATURE_CONFIG_LOADING_FAILED'
    assert 'Unable to load feature configuration file' in str(exc_info.value)


# ** test: int_feature_yaml_proxy_get
def test_int_feature_yaml_proxy_get(feature_yaml_proxy, feature):
    
    # Get the feature.
    test_feature = feature_yaml_proxy.get(feature.id)
    
    # Check the feature.
    assert test_feature
    assert test_feature == feature


# ** test: int_feature_yaml_proxy_exists
def test_int_feature_yaml_proxy_exists(feature_yaml_proxy, feature):
    
    # Check the feature exists.
    assert feature_yaml_proxy.exists(feature.id)


# ** test: int_feature_yaml_proxy_exists_not_found
def test_int_feature_yaml_proxy_exists_not_found(feature_yaml_proxy):
    
    # Check the feature does not exist.
    assert not feature_yaml_proxy.exists('not_found')


# ** test: int_feature_yaml_proxy_list
def test_int_feature_yaml_proxy_list(feature_yaml_proxy, feature):
    
    # List the features.
    features = feature_yaml_proxy.list()
    
    # Check the features.
    assert features
    assert len(features) == 1
    assert features[0] == feature