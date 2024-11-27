# *** imports

# app
from . import *


# *** tests

# ** test: test_container_context_init
def test_container_context_init(container_context):

    # Ensure the container context was initialized correctly
    assert container_context.interface_id == "test_interface"
    assert len(container_context.attributes) == 2
    assert container_context.feature_flag == "test"
    assert container_context.data_flag == "test"


# ** test: test_get_dependency
def test_get_dependency(container_context):
    
    # Call get_dependency with a test attribute
    result = container_context.get_dependency("test_repo")

    # Ensure the dependency was retrieved
    assert result is not None
    assert result.config_file == 'test.yml'


# ** test: test_create_injector
def test_create_injector(container_context):

    # Call create_injector.
    injector = container_context.create_injector()

    # Ensure the injector was created.
    assert injector is not None


# ** test: test_import_dependency
def test_import_dependency(container_context, test_repo_container_attribute):

    # Call import_dependency with a test attribute
    result = container_context.import_dependency(test_repo_container_attribute, "test")

    # Ensure the dependency was imported
    assert result is not None
    assert result == TestProxy