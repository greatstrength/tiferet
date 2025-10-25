"""Tiferet Feature YAML Proxy Tests Exports"""

# *** imports

# ** infra
import pytest

# ** app
from ....commands import TiferetError
from ....models import Feature
from ..feature import FeatureYamlProxy

# *** fixtures

# ** fixture: feature_config_file_path
@pytest.fixture
def feature_config_file_path() -> str:
    '''
    A fixture for the feature configuration file path.

    :return: The feature configuration file path.
    :rtype: str
    '''
    
    # Return the feature configuration file path.
    return 'tiferet/configs/tests/test.yml'

# ** fixture: test_feature_yaml_proxy
@pytest.fixture
def feature_yaml_proxy(feature_config_file_path: str) -> FeatureYamlProxy:
    '''
    A fixture for the feature YAML proxy.

    :param feature_config_file_path: The feature configuration file path.
    :type feature_config_file_path: str
    :return: The feature YAML proxy.
    :rtype: FeatureYamlProxy
    '''

    # Create and return the feature YAML proxy.
    return FeatureYamlProxy(feature_config_file_path)

# ** fixture: feature
@pytest.fixture
def feature() -> Feature:
    '''
    A fixture for a basic Feature instance.

    :return: The Feature instance.
    :rtype: Feature
    '''

    # Create and return the Feature instance.
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
def test_int_feature_yaml_proxy_load_yaml(feature_yaml_proxy: FeatureYamlProxy):
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

# ** test: int_feature_yaml_proxy_load_yaml_file_not_found
def test_int_feature_yaml_proxy_load_yaml_file_not_found(feature_yaml_proxy: FeatureYamlProxy):
    '''
    Test the feature YAML proxy load YAML method with a file not found error.

    :param feature_yaml_proxy: The feature YAML proxy.
    :type feature_yaml_proxy: FeatureYamlProxy
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
def test_int_feature_yaml_proxy_get(
        feature_yaml_proxy: FeatureYamlProxy,
        feature: Feature
    ):
    '''
    Test the get method of the FeatureYamlProxy.

    :param feature_yaml_proxy: The feature YAML proxy.
    :type feature_yaml_proxy: FeatureYamlProxy
    :param feature: The Feature instance.
    :type feature: Feature
    '''
    
    # Get the feature.
    test_feature = feature_yaml_proxy.get(feature.id)
    
    # Check the feature.
    assert test_feature
    assert test_feature == feature


# ** test: int_feature_yaml_proxy_exists
def test_int_feature_yaml_proxy_exists(
        feature_yaml_proxy: FeatureYamlProxy,
        feature: Feature
    ):
    '''
    Test the exists method of the FeatureYamlProxy.

    :param feature_yaml_proxy: The feature YAML proxy.
    :type feature_yaml_proxy: FeatureYamlProxy
    :param feature: The Feature instance.
    :type feature: Feature
    '''
    
    # Check the feature exists.
    assert feature_yaml_proxy.exists(feature.id)


# ** test: int_feature_yaml_proxy_exists_not_found
def test_int_feature_yaml_proxy_exists_not_found(feature_yaml_proxy: FeatureYamlProxy):
    '''
    Test the exists method of the FeatureYamlProxy for a non-existent feature.

    :param feature_yaml_proxy: The feature YAML proxy.
    :type feature_yaml_proxy: FeatureYamlProxy
    '''
    
    # Check the feature does not exist.
    assert not feature_yaml_proxy.exists('not_found')


# ** test: int_feature_yaml_proxy_list
def test_int_feature_yaml_proxy_list(
        feature_yaml_proxy: FeatureYamlProxy,
        feature: Feature
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
    assert features[0] == feature