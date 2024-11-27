# *** imports

# ** app
from . import *


# *** tests

# ** test: container_dependency_new
def test_container_dependency_new(test_proxy_container_dependency):

    # Assert the container dependency is valid.
    assert test_proxy_container_dependency.module_path == 'tiferet.repos.tests'
    assert test_proxy_container_dependency.class_name == 'TestProxy'
    assert test_proxy_container_dependency.flag == 'test'
    assert test_proxy_container_dependency.parameters == {
        'config_file': 'test.yml'}


# ** test: container_attribute_new
def test_container_attribute_new(test_repo_container_attribute, test_proxy_container_dependency):

    # Assert the container attribute is valid.
    assert test_repo_container_attribute.id == 'test_repo'
    assert test_repo_container_attribute.type == 'data'
    assert len(test_repo_container_attribute.dependencies) == 1
    assert test_repo_container_attribute.dependencies[0] == test_proxy_container_dependency


# ** test: test_container_attribute_get_dependency
def test_container_attribute_get_dependency(
    test_repo_container_attribute,
    test_proxy_container_dependency
):

    # Get the container dependency.
    container_dependency = test_repo_container_attribute.get_dependency('test')

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
    container_dependency = test_repo_container_attribute.get_dependency('test')

    # Assert the container dependency is valid.
    assert container_dependency == test_proxy_container_dependency
