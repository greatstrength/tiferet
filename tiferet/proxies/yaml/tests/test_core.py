# *** imports

# ** infra
import pytest

# ** app
from ..core import *
from ....configs import TiferetError


# *** fixtures

# ** fixture: yaml_config_file
@pytest.fixture
def yaml_config_file():
    """Fixture to provide the path to the YAML configuration file."""
    
    return 'tiferet/configs/tests/test.yml'


# ** fixture: yaml_config_proxy
@pytest.fixture
def yaml_config_proxy(yaml_config_file):
    """Fixture to create an instance of the YamlConfigurationProxy."""
    
    return YamlConfigurationProxy(yaml_config_file)


# *** tests

# ** test: yaml_config_proxy_load_yaml
def test_yaml_config_proxy_load_yaml(yaml_config_proxy):
    """Test the load_yaml method of the YamlConfigurationProxy."""
    
    # Load the YAML file.
    data = yaml_config_proxy.load_yaml()
    
    # Check the loaded data.
    assert data
    assert isinstance(data, dict)
    assert 'interfaces' in data
    assert 'attrs' in data
    assert 'const' in data
    assert 'features' in data
    assert 'errors' in data


# ** test: yaml_config_proxy_load_yaml_file_not_found
def test_yaml_config_proxy_load_yaml_file_not_found(yaml_config_proxy):
    """Test the load_yaml method with a file not found error."""
    
    # Set a non-existent configuration file.
    yaml_config_proxy.config_file = 'non_existent_file.yml'
    
    # Attempt to load the YAML file.
    with pytest.raises(TiferetError) as exc_info:
        yaml_config_proxy.load_yaml()
    
    # Verify the error message.
    assert exc_info.value.error_code == 'CONFIG_FILE_NOT_FOUND'
    assert 'Configuration file non_existent_file.yml not found' in str(exc_info.value)