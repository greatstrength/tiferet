# *** imports

# ** core
import os

# ** app
from . import *


# *** tests

# ** test: test_container_context_init
def test_container_context_init(container_context):

    # Ensure the container context was initialized correctly
    assert container_context.interface_id == "test_interface"
    assert container_context.feature_flag == "test"
    assert container_context.data_flag == "test"


# ** test: test_parse_parameter
def test_parse_parameter(container_context, test_env_var):

    # Test parsing an environment variable
    result = container_context.parse_parameter("$env.TEST_ENV_VAR")
    assert result == test_env_var

    # Test parsing a regular parameter
    result = container_context.parse_parameter("test")
    assert result == "test"


# ** test: test_get_dependency
def test_get_dependency(container_context):
    
    # Call get_dependency with a test attribute
    result = container_context.get_dependency(TEST_PROXY_ATTRIBUTE_ID)

    # Ensure the dependency was retrieved
    assert result is not None
    assert result.config_file == TEST_PROXY_CONFIG_FILE_VALUE


# ** test: test_create_injector
def test_create_injector(container_context):

    # Call create_injector.
    injector = container_context.create_injector()

    # Ensure the injector was created.
    assert injector is not None


# ** test: test_import_dependency
def test_import_dependency(container_context, container_attribute):

    # Call import_dependency with a test attribute
    result = container_context.import_dependency(container_attribute, "test")

    # Ensure the dependency was imported
    assert result is not None
    assert result == TestProxy