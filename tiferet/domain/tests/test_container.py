# *** imports

# ** app
from . import *


# *** tests

# ** test: container_dependency_new
def test_container_dependency_new(test_proxy_container_dependency):

    # Assert the container dependency is valid.
    assert test_proxy_container_dependency.module_path == TEST_PROXY_MODULE_PATH
    assert test_proxy_container_dependency.class_name == TEST_PROXY_CLASS_NAME
    assert test_proxy_container_dependency.flag == TEST_PROXY_DATA_FLAG
    assert test_proxy_container_dependency.parameters == {
        TEST_PROXY_CONFIG_FILE_KEY: TEST_PROXY_CONFIG_FILE_VALUE}


# ** test: container_attribute_new
def test_container_attribute_new(test_repo_container_attribute, test_proxy_container_dependency):

    # Assert the container attribute is valid.
    assert test_repo_container_attribute.id == TEST_PROXY_ATTRIBUTE_ID
    assert test_repo_container_attribute.type == TEST_PROXY_DEPENDENCY_TYPE
    assert len(test_repo_container_attribute.dependencies) == 1
    assert test_repo_container_attribute.dependencies[0] == test_proxy_container_dependency


# ** test: test_container_attribute_get_dependency
def test_container_attribute_get_dependency(
    test_repo_container_attribute,
    test_proxy_container_dependency
):

    # Get the container dependency.
    container_dependency = test_repo_container_attribute.get_dependency(TEST_PROXY_DATA_FLAG)

    # Assert the container dependency is valid.
    assert container_dependency == test_proxy_container_dependency


# ** test: test_container_attribute_get_dependency_invalid
def test_container_attribute_get_dependency_invalid(test_repo_container_attribute):

    # Assert the container dependency is invalid.
    assert test_repo_container_attribute.get_dependency('invalid') is None


# ** test: test_container_attribute_se  t_dependency
def test_container_attribute_set_dependency(
    container_attribute_empty,
    test_proxy_container_dependency
):

    # Assert that the container attribute has no dependencies.
    assert len(container_attribute_empty.dependencies) == 0

    # Set the container dependency.
    container_attribute_empty.set_dependency(test_proxy_container_dependency)

    # Assert the container dependency is valid.
    assert len(container_attribute_empty.dependencies) == 1
    assert container_attribute_empty.dependencies[0] == test_proxy_container_dependency


# ** test: test_container_attribute_set_dependency_exists
def test_container_attribute_set_dependency_exists(test_repo_container_attribute, test_proxy_container_dependency):

    # Modify the container dependency.
    test_proxy_container_dependency.module_path = 'tests.repos.super_test'
    test_proxy_container_dependency.class_name = 'SuperYamlProxy'

    # Set the container dependency.
    test_repo_container_attribute.set_dependency(test_proxy_container_dependency)

    # Get the container dependency.
    container_dependency = test_repo_container_attribute.get_dependency(TEST_PROXY_DATA_FLAG)

    # Assert the container dependency is valid.
    assert container_dependency == test_proxy_container_dependency
