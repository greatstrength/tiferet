# *** imports

# ** app
from ..error_yaml import *
from ...models.tests.test_error import *


# *** fixtures

# ** fixture: config_file_path
@pytest.fixture
def config_file_path():
    return 'tiferet/configs/tests/test.yml'

# ** fixture: test_error_yaml_proxy
@pytest.fixture
def error_yaml_proxy(config_file_path):
    return ErrorYamlProxy(config_file_path)


# *** tests

# ** test: error_yaml_proxy_list_errors
def test_error_yaml_proxy_list(
    error_yaml_proxy
):

    # List the errors.
    errors = error_yaml_proxy.list()

    # Check the errors.
    assert errors
    for error_id in ['MY_ERROR', 'MY_FORMATTED_ERROR']:
        assert error_id in [error.id for error in errors]


# ** test: error_yaml_proxy_exists
def test_error_yaml_proxy_exists(error_yaml_proxy, error):

    # Check if the error exists.
    assert error_yaml_proxy.exists(error.id)


# ** test: error_yaml_proxy_exists_not_found
def test_error_yaml_proxy_exists_not_found(error_yaml_proxy):

    # Check if the error exists.
    assert not error_yaml_proxy.exists('not_found')


# ** test: error_yaml_proxy_get
def test_error_yaml_proxy_get(error_yaml_proxy, error):

    # Get the error.
    error = error_yaml_proxy.get(error.id)

    # Check the error.
    assert error
    assert error == error
