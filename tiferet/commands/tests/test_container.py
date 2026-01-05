"""Tests for Tiferet Container Commands"""

# *** imports

# ** core
from typing import Tuple, Dict, Any, List

# ** infra
import pytest
from unittest import mock

# ** app
from ..container import ListAllSettings, AddServiceConfiguration
from ...models import ModelObject, ContainerAttribute
from ...contracts import ContainerService
from ...assets import TiferetError
from ...assets.constants import (
    INVALID_SERVICE_CONFIGURATION_ID,
    ATTRIBUTE_ALREADY_EXISTS_ID,
    SERVICE_CONFIGURATION_NOT_FOUND_ID,
)

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
def mock_container_service() -> ContainerService:
    '''
    A fixture for a mock container service.
    '''

    # Create the mock container service.
    return mock.Mock(spec=ContainerService)

# ** fixture: list_all_settings_command
@pytest.fixture
def list_all_settings_command(mock_container_service: ContainerService) -> ListAllSettings:
    '''
    A fixture for the list all settings command.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    :return: The list all settings command.
    :rtype: ListAllSettings
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

    :param container_attribute_and_constants: The container attribute and constants.
    :type container_attribute_and_constants: Tuple[ContainerAttribute, Dict[str, Any]]
    :param list_all_settings_command: The list all settings command.
    :type list_all_settings_command: ListAllSettings
    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    # Arrange the mock container service to return an empty list and empty dict.
    mock_container_service.list_all.return_value = container_attribute_and_constants

    # Execute the command.
    content = list_all_settings_command.execute()

    # Assert that the content is as expected.
    assert content == container_attribute_and_constants

    # Assert that the container service's list_all method was called once.
    mock_container_service.list_all.assert_called_once()

# ** test: add_service_configuration_with_default_type_only
def test_add_service_configuration_with_default_type_only(
    mock_container_service: ContainerService,
):
    '''
    Test that AddServiceConfiguration can add an attribute using only a
    default type (module_path and class_name).

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    # Arrange the container service mock.
    mock_container_service.attribute_exists.return_value = False

    command = AddServiceConfiguration(container_service=mock_container_service)

    attribute = command.execute(
        id='svc_default_only',
        module_path='tiferet.models.tests.test_container',
        class_name='TestDependency',
        parameters={'param': 'value'},
        dependencies=[],
    )

    # Assert the attribute is created correctly.
    assert isinstance(attribute, ContainerAttribute)
    assert attribute.id == 'svc_default_only'
    assert attribute.module_path == 'tiferet.models.tests.test_container'
    assert attribute.class_name == 'TestDependency'
    assert attribute.parameters == {'param': 'value'}
    assert isinstance(attribute.dependencies, list)
    assert attribute.dependencies == []

    # Assert the service was called to check existence and to save.
    mock_container_service.attribute_exists.assert_called_once_with('svc_default_only')
    mock_container_service.save_attribute.assert_called_once_with(attribute)

# ** test: add_service_configuration_with_dependencies_only
def test_add_service_configuration_with_dependencies_only(
    mock_container_service: ContainerService,
):
    '''
    Test that AddServiceConfiguration can add an attribute using only
    flagged dependencies.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    mock_container_service.attribute_exists.return_value = False

    command = AddServiceConfiguration(container_service=mock_container_service)

    dependencies: List[Dict[str, Any]] = [
        dict(
            module_path='tiferet.models.tests.test_container',
            class_name='TestDependency',
            flag='alpha',
            parameters={'flag_param': 'x'},
        )
    ]

    attribute = command.execute(
        id='svc_deps_only',
        dependencies=dependencies,
    )

    assert isinstance(attribute, ContainerAttribute)
    assert attribute.id == 'svc_deps_only'
    assert attribute.module_path is None
    assert attribute.class_name is None
    assert len(attribute.dependencies) == 1

    dep = attribute.dependencies[0]
    # Dependency should round-trip from the dicts provided.
    assert dep.flag == 'alpha'
    assert dep.module_path == 'tiferet.models.tests.test_container'
    assert dep.class_name == 'TestDependency'
    assert dep.parameters == {'flag_param': 'x'}

    mock_container_service.attribute_exists.assert_called_once_with('svc_deps_only')
    mock_container_service.save_attribute.assert_called_once_with(attribute)

# ** test: add_service_configuration_with_default_and_dependencies
def test_add_service_configuration_with_default_and_dependencies(
    mock_container_service: ContainerService,
):
    '''
    Test that AddServiceConfiguration can add an attribute when both a
    default type and flagged dependencies are provided.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    mock_container_service.attribute_exists.return_value = False

    command = AddServiceConfiguration(container_service=mock_container_service)

    dependencies: List[Dict[str, Any]] = [
        dict(
            module_path='tiferet.models.tests.test_container',
            class_name='TestDependency',
            flag='alpha',
            parameters={'flag_param': 'x'},
        )
    ]

    attribute = command.execute(
        id='svc_both',
        module_path='tiferet.models.tests.test_container',
        class_name='TestDependency',
        parameters={'param': 'value'},
        dependencies=dependencies,
    )

    assert isinstance(attribute, ContainerAttribute)
    assert attribute.id == 'svc_both'
    assert attribute.module_path == 'tiferet.models.tests.test_container'
    assert attribute.class_name == 'TestDependency'
    assert attribute.parameters == {'param': 'value'}
    assert len(attribute.dependencies) == 1

    dep = attribute.dependencies[0]
    assert dep.flag == 'alpha'
    assert dep.module_path == 'tiferet.models.tests.test_container'
    assert dep.class_name == 'TestDependency'
    assert dep.parameters == {'flag_param': 'x'}

    mock_container_service.attribute_exists.assert_called_once_with('svc_both')
    mock_container_service.save_attribute.assert_called_once_with(attribute)

# ** test: add_service_configuration_missing_id
def test_add_service_configuration_missing_id(
    mock_container_service: ContainerService,
):
    '''
    Test that AddServiceConfiguration fails when id is missing or empty.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    mock_container_service.attribute_exists.return_value = False

    command = AddServiceConfiguration(container_service=mock_container_service)

    with pytest.raises(TiferetError) as excinfo:
        command.execute(
            id=' ',  # empty after strip
            module_path='tiferet.models.tests.test_container',
            class_name='TestDependency',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == 'COMMAND_PARAMETER_REQUIRED'

# ** test: add_service_configuration_duplicate_id
def test_add_service_configuration_duplicate_id(
    mock_container_service: ContainerService,
):
    '''
    Test that AddServiceConfiguration fails when the attribute id already exists.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    mock_container_service.attribute_exists.return_value = True

    command = AddServiceConfiguration(container_service=mock_container_service)

    with pytest.raises(TiferetError) as excinfo:
        command.execute(
            id='svc_existing',
            module_path='tiferet.models.tests.test_container',
            class_name='TestDependency',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == ATTRIBUTE_ALREADY_EXISTS_ID

# ** test: add_service_configuration_no_type_source
def test_add_service_configuration_no_type_source(
    mock_container_service: ContainerService,
):
    '''
    Test that AddServiceConfiguration fails when no default type or
    dependencies are provided.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    mock_container_service.attribute_exists.return_value = False

    command = AddServiceConfiguration(container_service=mock_container_service)

    with pytest.raises(TiferetError) as excinfo:
        command.execute(
            id='svc_invalid',
            module_path=None,
            class_name=None,
            dependencies=[],
        )

    error: TiferetError = excinfo.value
    assert error.error_code == INVALID_SERVICE_CONFIGURATION_ID

# ** test: set_default_service_configuration_full_update
def test_set_default_service_configuration_full_update(
    mock_container_service: ContainerService,
):
    '''
    Test that SetDefaultServiceConfiguration updates both default type and
    parameters when provided.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    # Create an existing attribute.
    attribute = ModelObject.new(
        ContainerAttribute,
        id='svc_full',
        module_path='old.module',
        class_name='OldClass',
        parameters={'old': 'value'},
        dependencies=[],
    )

    mock_container_service.get_attribute.return_value = attribute

    from ..container import SetDefaultServiceConfiguration

    command = SetDefaultServiceConfiguration(container_service=mock_container_service)

    result = command.execute(
        id='svc_full',
        module_path='new.module',
        class_name='NewClass',
        parameters={'param': 'value'},
    )

    assert result is attribute
    assert attribute.module_path == 'new.module'
    assert attribute.class_name == 'NewClass'
    assert attribute.parameters == {'param': 'value'}
    mock_container_service.get_attribute.assert_called_once_with('svc_full')
    mock_container_service.save_attribute.assert_called_once_with(attribute)

# ** test: set_default_service_configuration_parameters_only
def test_set_default_service_configuration_parameters_only(
    mock_container_service: ContainerService,
):
    '''
    Test that SetDefaultServiceConfiguration updates only parameters when
    module_path and class_name are not provided.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    attribute = ModelObject.new(
        ContainerAttribute,
        id='svc_params',
        module_path='tiferet.models.tests.test_container',
        class_name='TestDependency',
        parameters={'keep': 'value', 'drop': 'x'},
        dependencies=[],
    )

    mock_container_service.get_attribute.return_value = attribute

    from ..container import SetDefaultServiceConfiguration

    command = SetDefaultServiceConfiguration(container_service=mock_container_service)

    result = command.execute(
        id='svc_params',
        parameters={'keep': 'updated', 'drop': None},
    )

    assert result is attribute
    # Default type should remain unchanged.
    assert attribute.module_path == 'tiferet.models.tests.test_container'
    assert attribute.class_name == 'TestDependency'
    # Parameters should be cleaned via set_default_type (drop=None removed).
    assert attribute.parameters == {'keep': 'updated'}
    mock_container_service.get_attribute.assert_called_once_with('svc_params')
    mock_container_service.save_attribute.assert_called_once_with(attribute)

# ** test: set_default_service_configuration_clear_parameters
def test_set_default_service_configuration_clear_parameters(
    mock_container_service: ContainerService,
):
    '''
    Test that SetDefaultServiceConfiguration clears parameters when
    parameters is None.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    attribute = ModelObject.new(
        ContainerAttribute,
        id='svc_clear',
        module_path='tiferet.models.tests.test_container',
        class_name='TestDependency',
        parameters={'keep': 'value'},
        dependencies=[],
    )

    mock_container_service.get_attribute.return_value = attribute

    from ..container import SetDefaultServiceConfiguration

    command = SetDefaultServiceConfiguration(container_service=mock_container_service)

    result = command.execute(
        id='svc_clear',
        parameters=None,
    )

    assert result is attribute
    assert attribute.module_path == 'tiferet.models.tests.test_container'
    assert attribute.class_name == 'TestDependency'
    assert attribute.parameters == {}
    mock_container_service.get_attribute.assert_called_once_with('svc_clear')
    mock_container_service.save_attribute.assert_called_once_with(attribute)

# ** test: set_default_service_configuration_not_found
def test_set_default_service_configuration_not_found(
    mock_container_service: ContainerService,
):
    '''
    Test that SetDefaultServiceConfiguration raises when the attribute
    does not exist.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    mock_container_service.get_attribute.return_value = None

    from ..container import SetDefaultServiceConfiguration

    command = SetDefaultServiceConfiguration(container_service=mock_container_service)

    with pytest.raises(TiferetError) as excinfo:
        command.execute(
            id='missing',
            module_path='mod',
            class_name='Cls',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == SERVICE_CONFIGURATION_NOT_FOUND_ID

# ** test: set_default_service_configuration_incomplete_type
def test_set_default_service_configuration_incomplete_type(
    mock_container_service: ContainerService,
):
    '''
    Test that SetDefaultServiceConfiguration rejects partial default type
    updates when only one of module_path or class_name is provided.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    attribute = ModelObject.new(
        ContainerAttribute,
        id='svc_partial',
        module_path='tiferet.models.tests.test_container',
        class_name='TestDependency',
        parameters={'keep': 'value'},
        dependencies=[],
    )

    mock_container_service.get_attribute.return_value = attribute

    from ..container import SetDefaultServiceConfiguration

    command = SetDefaultServiceConfiguration(container_service=mock_container_service)

    with pytest.raises(TiferetError) as excinfo:
        command.execute(
            id='svc_partial',
            module_path='new.module',
            class_name=None,
            parameters={'param': 'value'},
        )

    error: TiferetError = excinfo.value
    assert error.error_code == INVALID_SERVICE_CONFIGURATION_ID
