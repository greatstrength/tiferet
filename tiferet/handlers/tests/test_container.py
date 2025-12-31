# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ..container import ContainerRepository, ContainerHandler
from ...models.container import *
from ...assets import TiferetError
from ...assets.constants import CONTAINER_ATTRIBUTES_NOT_FOUND_ID, DEPENDENCY_TYPE_NOT_FOUND_ID
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

# ** fixture: container_attribute_with_flagged_dependencies_and_parameters
@pytest.fixture
def container_attribute_with_flagged_dependencies_and_parameters():
    """Fixture to provide a mock ContainerAttribute object with flags and parameters."""
    return ModelObject.new(
        ContainerAttribute,
        id='container_repo',
        name='Container Repository',
        dependencies=[
            ModelObject.new(
                FlaggedDependency,
                flag='flagged_dependency',
                module_path='tiferet.proxies.yaml.container',
                class_name='ContainerYamlProxy',
                parameters={'param1': 'value1'}
            )
        ],
        parameters={'param0': 'value0'}
    )


# ** fixture: constants
@pytest.fixture
def constants():
    """Fixture to provide a mock constants dictionary."""
    return dict(
        container_config_file='tiferet/configs/tests/test.yml',
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

# ** test: test_container_handler_load_constants_no_attributes
def test_container_handler_load_constants_no_attributes(container_handler):
    """Test the load_constants method with no attributes provided."""
    
    # Call the load_constants method with an empty attributes list.
    with pytest.raises(TiferetError) as exc_info:
        container_handler.load_constants([])

    # Assert that the error is raised with the correct error code and message.
    assert exc_info.value.error_code == CONTAINER_ATTRIBUTES_NOT_FOUND_ID
    assert 'No container attributes provided' in str(exc_info.value)


# ** test: test_container_handler_load_constants_with_flagged_dependencies
def test_container_handler_load_constants_with_flagged_dependencies(container_handler,
    container_attribute_with_flagged_dependencies_and_parameters,
    constants
):
    
    # Call the load_constants method without flags.
    result = container_handler.load_constants(
        [container_attribute_with_flagged_dependencies_and_parameters],
        constants
    )

    # Assert that the result contains parsed constants and parameters.
    expected_result = {
        'container_config_file': 'tiferet/configs/tests/test.yml',
        'param0': 'value0',
    }
    assert result == expected_result

    # Call the load_constants method with flags.
    result_with_flags = container_handler.load_constants(
        [container_attribute_with_flagged_dependencies_and_parameters],
        constants,
        flags=['flagged_dependency']
    )

    # Assert that the result with flags contains parsed constants and parameters.
    expected_result_with_flags = {
        'container_config_file': 'tiferet/configs/tests/test.yml',
        'param1': 'value1'
    }
    assert result_with_flags == expected_result_with_flags
