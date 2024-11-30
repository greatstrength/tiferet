# *** imports

# ** app
from . import *
from ..error import YamlProxy as ErrorYamlProxy


# *** fixtures

# ** fixture: test_error_yaml_proxy
@pytest.fixture
def test_error_yaml_proxy():
    return ErrorYamlProxy(TEST_CONFIG_FILE_PATH)


# ** fixture: test_error_with_custom_code
@pytest.fixture
def test_error_with_custom_code(test_error_message):

    # Create random number as a string to use as the error code.
    import random
    error_code = str(random.randint(1000, 9999))
    return Error.new(
        'Test save error',
        'TEST_SAVE_ERROR',
        error_code,
        message=[
            test_error_message
        ]

    )


# *** tests

# ** test: error_yaml_proxy_list_errors
def test_error_yaml_proxy_list(
    test_error_yaml_proxy
):

    # List the errors.
    errors = test_error_yaml_proxy.list()

    # Check the errors.
    assert errors
    assert len(errors) == 3
    for error_id in ['MY_ERROR', 'FORMATTED_ERROR', 'TEST_SAVE_ERROR']:
        assert error_id in [error.id for error in errors]


# ** test: error_yaml_proxy_exists
def test_error_yaml_proxy_exists(test_error_yaml_proxy, test_error):

    # Check if the error exists.
    assert test_error_yaml_proxy.exists(test_error.id)


# ** test: error_yaml_proxy_exists_not_found
def test_error_yaml_proxy_exists_not_found(test_error_yaml_proxy):

    # Check if the error exists.
    assert not test_error_yaml_proxy.exists('not_found')


# ** test: error_yaml_proxy_get
def test_error_yaml_proxy_get(test_error_yaml_proxy, test_error):

    # Get the error.
    error = test_error_yaml_proxy.get(test_error.id)

    # Check the error.
    assert error
    assert error == test_error


# ** test: error_yaml_proxy_save
def test_error_yaml_proxy_save(test_error_yaml_proxy, test_error_with_custom_code):

    # Save the error.
    test_error_yaml_proxy.save(test_error_with_custom_code)

    # Get the error.
    error = test_error_yaml_proxy.get(test_error_with_custom_code.id)

    # Check the error.
    assert error
    assert error.id == test_error_with_custom_code.id
    assert error.error_code == test_error_with_custom_code.error_code