# *** imports

# ** app
from . import *
from ...repos.app import AppYamlProxy


# *** fixtures

# ** fixture: test_app_yaml_proxy
@pytest.fixture
def test_app_yaml_proxy():
    return AppYamlProxy(TEST_CONFIG_FILE_PATH)


# *** tests

# ** test: app_yaml_proxy_list_interfaces
def test_app_yaml_proxy_list_interfaces(test_app_yaml_proxy, test_app_interface):
    '''
    Test the app YAML proxy list interfaces method.
    '''
    
    # List the interfaces.
    interfaces = test_app_yaml_proxy.list_interfaces()
    
    # Check the interfaces.
    assert interfaces
    assert len(interfaces) == 1
    assert interfaces[0].id == test_app_interface.id
    assert interfaces[0].name == test_app_interface.name


# ** test: app_yaml_proxy_get_interface
def test_app_yaml_proxy_get_interface(test_app_yaml_proxy, test_app_interface):

    # Get the interface.
    interface = test_app_yaml_proxy.get_interface(test_app_interface.id)

    # Check the interface.
    assert interface
    assert interface.id == test_app_interface.id
    assert interface.name == test_app_interface.name
    assert interface.description == test_app_interface.description
    assert interface.feature_flag == test_app_interface.feature_flag
    assert interface.data_flag == test_app_interface.data_flag
    assert len(interface.dependencies) == len(test_app_interface.dependencies)


# ** test: app_yaml_proxy_get_interface_not_found
def test_app_yaml_proxy_get_interface_not_found(test_app_yaml_proxy):

    # Get the interface.
    interface = test_app_yaml_proxy.get_interface('not_found')

    # Check the interface.
    assert not interface