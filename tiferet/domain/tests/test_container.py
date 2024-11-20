# *** imports

# ** infra
import pytest

# ** app
from . import *

# *** fixtures

# ** fixture: container_dependency
@pytest.fixture
def container_dependency():
    return ContainerDependency.new(
        module_path='tests.repos.test',
        class_name='YamlProxy',
        flag='test',
        parameters={'config_file': 'test.yml'}
    )


# ** fixture: container_attribute
@pytest.fixture
def container_attribute(container_dependency):
    return ContainerAttribute.new(
        id='test_repo',
        type='data',
        dependencies=[container_dependency],
    )


# ** fixture: container_attribute_empty
@pytest.fixture
def container_attribute_empty():
    return ContainerAttribute.new(
        id='test_repo',
        type='data',
        dependencies=[],
    )


# *** tests

# ** test: container_dependency_new
def test_container_dependency_new(container_dependency):

    # Assert the container dependency is valid.
    assert container_dependency.module_path == 'tests.repos.test'
    assert container_dependency.class_name == 'YamlProxy'
    assert container_dependency.flag == 'test'
    assert container_dependency.parameters == {'config_file': 'test.yml'}


# ** test: container_attribute_new
def test_container_attribute_new(container_attribute):

    # Assert the container attribute is valid.
    assert container_attribute.id == 'test_repo'
    assert container_attribute.type == 'data'
    assert len(container_attribute.dependencies) == 1
    assert container_attribute.dependencies[0].module_path == 'tests.repos.test'
    assert container_attribute.dependencies[0].class_name == 'YamlProxy'
    assert container_attribute.dependencies[0].flag == 'test'
    assert container_attribute.dependencies[0].parameters == {'config_file': 'test.yml'}


# ** test: test_container_attribute_get_dependency
def test_container_attribute_get_dependency(container_attribute):

    # Get the container dependency.
    container_dependency = container_attribute.get_dependency('test')

    # Assert the container dependency is valid.
    assert container_dependency.module_path == 'tests.repos.test'
    assert container_dependency.class_name == 'YamlProxy'
    assert container_dependency.flag == 'test'
    assert container_dependency.parameters == {'config_file': 'test.yml'}


# ** test: test_container_attribute_get_dependency_invalid
def test_container_attribute_get_dependency_invalid(container_attribute):

    # Assert the container dependency is invalid.
    assert container_attribute.get_dependency('invalid') is None


# ** test: test_container_attribute_set_dependency
def test_container_attribute_set_dependency(container_attribute_empty, container_dependency):

    # Assert that the container attribute has no dependencies.
    assert len(container_attribute_empty.dependencies) == 0

    # Set the container dependency.
    container_attribute_empty.set_dependency(container_dependency)

    # Assert the container dependency is valid.
    assert len(container_attribute_empty.dependencies) == 1
    assert container_attribute_empty.dependencies[0].module_path == 'tests.repos.test'
    assert container_attribute_empty.dependencies[0].class_name == 'YamlProxy'
    assert container_attribute_empty.dependencies[0].flag == 'test'


# ** test: test_container_attribute_set_dependency_exists
def test_container_attribute_set_dependency_exists(container_attribute, container_dependency):

    # Modify the container dependency.
    container_dependency.module_path = 'tests.repos.super_test'
    container_dependency.class_name = 'SuperYamlProxy'

    # Set the container dependency.
    container_attribute.set_dependency(container_dependency)

    # Get the container dependency.
    container_dependency = container_attribute.get_dependency('test')

    # Assert the container dependency is valid.
    assert container_dependency.module_path == 'tests.repos.super_test'
    assert container_dependency.class_name == 'SuperYamlProxy'
    assert container_dependency.flag == 'test'
    assert container_dependency.parameters == {'config_file': 'test.yml'}