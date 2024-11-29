# *** imports

# ** app
from . import *
from ...repos.feature import YamlProxy as FeatureYamlProxy


# *** fixtures

# ** fixture: test_feature_yaml_proxy
@pytest.fixture
def test_feature_yaml_proxy():
    return FeatureYamlProxy(TEST_CONFIG_FILE_PATH)


# *** tests

# ** test: int_feature_yaml_proxy_get
def test_int_feature_yaml_proxy_get(test_feature_yaml_proxy, test_feature):
    
    # Get the feature.
    feature = test_feature_yaml_proxy.get(test_feature.id)
    
    # Check the feature.
    assert feature
    assert feature == test_feature


# ** test: int_feature_yaml_proxy_exists
def test_int_feature_yaml_proxy_exists(test_feature_yaml_proxy, test_feature):
    
    # Check the feature exists.
    assert test_feature_yaml_proxy.exists(test_feature.id)


# ** test: int_feature_yaml_proxy_exists_not_found
def test_int_feature_yaml_proxy_exists_not_found(test_feature_yaml_proxy):
    
    # Check the feature does not exist.
    assert not test_feature_yaml_proxy.exists('not_found')


# ** test: int_feature_yaml_proxy_list
def test_int_feature_yaml_proxy_list(test_feature_yaml_proxy, test_feature):
    
    # List the features.
    features = test_feature_yaml_proxy.list()
    
    # Check the features.
    assert features
    assert len(features) == 1
    assert features[0] == test_feature