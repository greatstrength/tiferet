"""Tests for Tiferet Container Commands"""

# *** imports

# ** core
from typing import Tuple, Dict, Any

# ** infra
import pytest
from unittest import mock

# ** app
from ..container import ListAllSettings
from ...models import ModelObject, ContainerAttribute
from ...contracts import ContainerService

# *** fixtures

# ** fixture: container_attribute_and_constants
@pytest.fixture
def container_attribute_and_constants() -> Tuple[ContainerAttribute, Dict[str, Any]]:
    '''
    A fixture for a container attribute and constants.
    '''

    # Create a container attribute.
    container_attribute = ModelObject.new(
        ContainerAttribute,
        id='attribute_1',
        module_path='tiferet.example.module',
        class_name='ExampleClass',
        parameters={
            'param_1': 'value_1',
            'param_2': '10'
        },
        dependencies=[]
    )

    # Create constants.
    constants = {
        'constant_1': 'Constant Value 1',
        'constant_2': '42'
    }

    # Return the container attribute and constants.
    return container_attribute, constants

# ** fixture: mock_container_service
@pytest.fixture
def mock_container_service():
    '''
    A fixture for a mock container service.
    '''

    # Create the mock container service.
    return mock.Mock(spec=ContainerService)

# ** fixture: list_all_settings_command
@pytest.fixture
def list_all_settings_command(mock_container_service: ContainerService):
    '''
    A fixture for the list all settings command.
    '''

    # Create the list all settings command.
    return ListAllSettings(container_service=mock_container_service)

# *** tests

# ** test: test_execute_calls_container_service_list_all
def test_execute_calls_container_service_list_all(
    container_attribute_and_constants:  Tuple[ContainerAttribute, Dict[str, Any]],
    list_all_settings_command: ListAllSettings,
    mock_container_service: ContainerService
):
    '''
    Test that the execute method calls the container service's list_all method.
    '''

    # Arrange the mock container service to return an empty list and empty dict.
    mock_container_service.list_all.return_value = container_attribute_and_constants

    # Execute the command.
    content = list_all_settings_command.execute()

    # Assert that the content is as expected.
    assert content == container_attribute_and_constants

    # Assert that the container service's list_all method was called once.
    mock_container_service.list_all.assert_called_once()