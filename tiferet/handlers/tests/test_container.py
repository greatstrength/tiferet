# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ..container import ContainerRepository, ContainerHandler
from ...models.container import *
from ...commands import TiferetError
from ...proxies.yaml.container import ContainerYamlProxy


# *** fixtures

# ** fixture: container_attribute
@pytest.fixture
def container_attribute():
    """Fixture to provide a mock ContainerAttribute object."""
    return ModelObject.new(
        ContainerAttribute,
        id='container_repo',
        name='Container Repository',
        module_path='tiferet.proxies.yaml.container',
        class_name='ContainerYamlProxy',
    )


# ** fixture: container_attribute_with_flagged_dependencies
@pytest.fixture
def container_attribute_with_flagged_dependencies():
    """Fixture to provide a mock ContainerAttribute object with flags."""
    return ModelObject.new(
        ContainerAttribute,
        id='container_repo',
        name='Container Repository',
        dependencies=[
            ModelObject.new(
                FlaggedDependency,
                flag='flagged_dependency',
                module_path='tiferet.proxies.yaml.container',
                class_name='ContainerYamlProxy'
            )
        ]
    )

# ** fixture: constants
@pytest.fixture
def constants():
    """Fixture to provide a mock constants dictionary."""
    return dict(
        container_config_file='tiferet/config/tests/test.yml',
    )


# ** fixture: container_handler
@pytest.fixture
def container_handler(container_repo):
    """Fixture to provide a ContainerHandler instance."""
    return ContainerHandler(
        container_repo=container_repo
    )


# ** fixture: container_repo
@pytest.fixture()
def container_repo():
    """Fixture to provide a mock ContainerRepository."""
    return mock.Mock(spec=ContainerRepository)


# ** fixture: container_repo
@pytest.fixture()
def container_repo(container_attribute, constants):
    """Fixture to provide a mock ContainerRepository."""

    repo = mock.Mock(spec=ContainerRepository)
    repo.list_all.return_value = (
        [container_attribute],
        constants
    )
    return repo


# *** tests

# ** test: test_container_handler_list_all

def test_container_handler_list_all(container_handler, container_repo, container_attribute, constants):
    """Test the list_all method of ContainerHandler."""
    
    # Call the list_all method.
    attributes, consts = container_handler.list_all()

    # Assert that the repository's list_all method was called.
    container_repo.list_all.assert_called_once()

    # Assert that the returned attributes and constants match the expected values.
    assert attributes == [container_attribute]
    assert consts == constants


# ** test: test_container_handler_get_dependency_type
def test_container_handler_get_dependency_type(container_handler, container_attribute):
    """Test the get_dependency_type method of ContainerHandler."""
    
    # Call the get_dependency_type method.
    dependency_type = container_handler.get_dependency_type(container_attribute)

    # Assert that the type is correct.
    assert dependency_type == ContainerYamlProxy


# ** test: test_container_handler_get_dependency_type_with_flagged_dependencies
def test_container_handler_get_dependency_type_with_flagged_dependencies(container_handler, container_attribute_with_flagged_dependencies):
    """Test the get_dependency_type method with flagged dependencies."""
    
    # Call the get_dependency_type method with flags.
    dependency_type = container_handler.get_dependency_type(
        container_attribute_with_flagged_dependencies,
        flags=['flagged_dependency']
    )

    # Assert that the type is correct.
    assert dependency_type == ContainerYamlProxy


# ** test: test_container_handler_get_dependency_type_not_found
def test_container_handler_get_dependency_type_not_found(container_handler, container_attribute):
    """Test the get_dependency_type method when the type is not found."""
    
    # Remove module path and class name from the container attribute.
    container_attribute.module_path = None
    container_attribute.class_name = None

    # Call the get_dependency_type method with a non-existent flag.
    with pytest.raises(TiferetError) as exc_info:
         container_handler.get_dependency_type(
            container_attribute,
            flags=['non_existent_flag']
        )

    # Assert that the error is raised with the correct error code and message.
    assert exc_info.value.error_code == 'DEPENDENCY_TYPE_NOT_FOUND'
    assert 'No dependency type found for attribute container_repo with flags [\'non_existent_flag\'].' in str(exc_info.value)