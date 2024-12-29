# *** imports

# ** app
from . import *


# *** fixtures

# ** fixture: container_dependency (container)
@pytest.fixture
def container_dependency() -> ContainerDependency:
    return ValueObject.new(
        ContainerDependency,
        module_path='tiferet.repos.tests',
        class_name='TestProxy',
        flag='test',
        parameters={'config_file': 'tiferet/configs/tests/test.yml'}
    )


# ** fixture: test_repo_container_attribute (container)
@pytest.fixture
def container_attribute(container_dependency: ContainerDependency) -> ContainerAttribute:
    return Entity.new(
        ContainerAttribute,
        id='test_repo',
        type='data',
        dependencies=[container_dependency],
    )

# ** fixture: empty_container_attribute
@pytest.fixture
def empty_container_attribute() -> ContainerAttribute:
    return Entity.new(
        ContainerAttribute,
        id='test_repo',
        type='data',
        dependencies=[],
    )


# *** tests

# ** test: container_attribute_new
def test_container_attribute(container_attribute, container_dependency):

    # Assert the container attribute is valid.
    assert container_attribute.id == 'test_repo'
    assert container_attribute.type == 'data'
    assert len(container_attribute.dependencies) == 1
    assert container_attribute.dependencies[0] == container_dependency


# ** test: test_container_attribute_get_dependency
def test_container_attribute_get_dependency(
    container_attribute,
    container_dependency
):

    # Get the container dependency.
    container_dependency = container_attribute.get_dependency('test')

    # Assert the container dependency is valid.
    assert container_dependency.module_path == 'tiferet.repos.tests'
    assert container_dependency.class_name == 'TestProxy'
    assert container_dependency.flag == 'test'


# ** test: test_container_attribute_get_dependency_invalid
def test_container_attribute_get_dependency_invalid(container_attribute):

    # Assert the container dependency is invalid.
    assert container_attribute.get_dependency('invalid') is None


# ** test: test_container_attribute_se  t_dependency
def test_container_attribute_set_dependency(
    empty_container_attribute,
    container_dependency,
    container_attribute
):

    # Assert that the container attribute has no dependencies.
    assert len(empty_container_attribute.dependencies) == 0

    # Set the container dependency.
    empty_container_attribute.set_dependency(container_dependency)

    # Assert the container dependency is valid.
    assert empty_container_attribute == container_attribute


# ** test: test_container_attribute_set_dependency_exists
def test_container_attribute_set_dependency_exists(
        container_attribute, 
        container_dependency
    ):

    # Modify the container dependency.
    container_dependency.module_path = 'tests.repos.super_test'
    container_dependency.class_name = 'SuperYamlProxy'

    # Set the container dependency.
    container_attribute.set_dependency(container_dependency)

    # Get the container dependency.
    test_container_dependency = container_attribute.get_dependency('test')

    # Assert the container dependency is valid.
    assert test_container_dependency == container_dependency
