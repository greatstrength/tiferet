"""Tests for Tiferet Container Commands"""

# *** imports

# ** core
from typing import Tuple, Dict, Any, List

# ** infra
import pytest
from unittest import mock

# ** app
from ..container import (
    ListAllSettings,
    AddServiceConfiguration,
    RemoveServiceConfiguration,
    SetServiceConstants,
    a,
)
from ...entities import ContainerAttribute, FlaggedDependency
from ...mappers import (
    ContainerAttributeAggregate,
    FlaggedDependencyAggregate,
)
from ...mappers.settings import Aggregate
from ...interfaces import ContainerService
from ...assets import TiferetError
from ...events import Command

# *** fixtures

# ** fixture: flagged_dependency_for_commands
@pytest.fixture
def flagged_dependency_for_commands() -> FlaggedDependency:
    '''
    A flagged dependency instance for command tests.
    '''

    return Aggregate.new(
        FlaggedDependencyAggregate,
        module_path='tiferet.models.tests.test_container',
        class_name='TestDependencyAlpha',
        flag='test_alpha',
        parameters={
            'test_param': 'test_value',
            'param': 'value1',
        },
    )

# ** fixture: container_attribute_and_constants
@pytest.fixture
def container_attribute_and_constants() -> Tuple[ContainerAttribute, Dict[str, Any]]:
    '''
    A fixture for a container attribute and constants.
    '''

    # Create a container attribute aggregate.
    container_attribute = Aggregate.new(
        ContainerAttributeAggregate,
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

# ** test: set_service_constants_clear_all_with_none
def test_set_service_constants_clear_all_with_none(
    mock_container_service: ContainerService,
):
    '''
    Test that SetServiceConstants clears all constants when None is passed.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    # Arrange existing constants.
    existing_constants = {
        'constant_1': 'value1',
        'constant_2': 'value2',
    }
    mock_container_service.list_all.return_value = ([], existing_constants)

    command = SetServiceConstants(container_service=mock_container_service)

    result = command.execute(constants=None)

    assert result == {}
    mock_container_service.list_all.assert_called_once()
    mock_container_service.save_constants.assert_called_once_with({})

# ** test: set_service_constants_partial_removal
def test_set_service_constants_partial_removal(
    mock_container_service: ContainerService,
):
    '''
    Test that SetServiceConstants removes keys with None values while
    preserving others.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    existing_constants = {
        'keep': 'value',
        'remove': 'to_delete',
    }
    mock_container_service.list_all.return_value = ([], existing_constants)

    command = SetServiceConstants(container_service=mock_container_service)

    result = command.execute(constants={'remove': None})

    assert result == {'keep': 'value'}
    mock_container_service.list_all.assert_called_once()
    mock_container_service.save_constants.assert_called_once_with({'keep': 'value'})

# ** test: set_service_constants_add_new
def test_set_service_constants_add_new(
    mock_container_service: ContainerService,
):
    '''
    Test that SetServiceConstants adds new constants on top of existing
    ones.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    existing_constants = {
        'existing': 'old',
    }
    mock_container_service.list_all.return_value = ([], existing_constants)

    command = SetServiceConstants(container_service=mock_container_service)

    result = command.execute(constants={'new': 'value'})

    assert result == {
        'existing': 'old',
        'new': 'value',
    }
    mock_container_service.list_all.assert_called_once()
    mock_container_service.save_constants.assert_called_once_with({
        'existing': 'old',
        'new': 'value',
    })

# ** test: set_service_constants_update_existing
def test_set_service_constants_update_existing(
    mock_container_service: ContainerService,
):
    '''
    Test that SetServiceConstants updates existing constant values.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    existing_constants = {
        'to_update': 'old',
    }
    mock_container_service.list_all.return_value = ([], existing_constants)

    command = SetServiceConstants(container_service=mock_container_service)

    result = command.execute(constants={'to_update': 'new'})

    assert result == {'to_update': 'new'}
    mock_container_service.list_all.assert_called_once()
    mock_container_service.save_constants.assert_called_once_with({'to_update': 'new'})

# ** test: set_service_constants_mixed_operations
def test_set_service_constants_mixed_operations(
    mock_container_service: ContainerService,
):
    '''
    Test that SetServiceConstants can add, update, and remove constants in
    a single call.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    existing_constants = {
        'keep': 'value',
        'remove': 'to_delete',
        'update': 'old',
    }
    mock_container_service.list_all.return_value = ([], existing_constants)

    command = SetServiceConstants(container_service=mock_container_service)

    result = command.execute(
        constants={
            'remove': None,
            'update': 'new',
            'add': 'added',
        },
    )

    expected = {
        'keep': 'value',
        'update': 'new',
        'add': 'added',
    }

    assert result == expected
    mock_container_service.list_all.assert_called_once()
    mock_container_service.save_constants.assert_called_once_with(expected)

# ** test: set_service_constants_empty_dict
def test_set_service_constants_empty_dict(
    mock_container_service: ContainerService,
):
    '''
    Test that SetServiceConstants is idempotent when an empty dict is
    provided (no changes to existing constants).

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    existing_constants = {
        'keep': 'value',
    }
    mock_container_service.list_all.return_value = ([], existing_constants)

    command = SetServiceConstants(container_service=mock_container_service)

    result = command.execute(constants={})

    assert result == existing_constants
    mock_container_service.list_all.assert_called_once()
    mock_container_service.save_constants.assert_called_once_with(existing_constants)

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
    assert error.error_code == a.const.ATTRIBUTE_ALREADY_EXISTS_ID

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
    assert error.error_code == a.const.INVALID_SERVICE_CONFIGURATION_ID

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

    # Create an existing attribute aggregate.
    attribute = Aggregate.new(
        ContainerAttributeAggregate,
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

    attribute = Aggregate.new(
        ContainerAttributeAggregate,
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

    attribute = Aggregate.new(
        ContainerAttributeAggregate,
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
    assert error.error_code == a.const.SERVICE_CONFIGURATION_NOT_FOUND_ID

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

    attribute = Aggregate.new(
        ContainerAttributeAggregate,
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
    assert error.error_code == a.const.INVALID_SERVICE_CONFIGURATION_ID


# ** test: set_service_dependency_add_new
def test_set_service_dependency_add_new(
    mock_container_service: ContainerService,
):
    '''
    Test that SetServiceDependency adds a new flagged dependency when the
    flag does not yet exist.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    # Existing attribute aggregate with no dependencies.
    attribute = Aggregate.new(
        ContainerAttributeAggregate,
        id='svc_flags',
        module_path='tiferet.models.tests.test_container',
        class_name='TestDependency',
        parameters={},
        dependencies=[],
    )

    mock_container_service.get_attribute.return_value = attribute

    from ..container import SetServiceDependency

    command = SetServiceDependency(container_service=mock_container_service)

    result_id = command.execute(
        id='svc_flags',
        flag='alpha',
        module_path='tiferet.models.tests.test_container',
        class_name='TestDependencyAlpha',
        parameters={'param': 'value'},
    )

    assert result_id == 'svc_flags'
    assert len(attribute.dependencies) == 1
    dep = attribute.get_dependency('alpha')
    assert dep is not None
    assert dep.flag == 'alpha'
    assert dep.module_path == 'tiferet.models.tests.test_container'
    assert dep.class_name == 'TestDependencyAlpha'
    assert dep.parameters == {'param': 'value'}
    mock_container_service.get_attribute.assert_called_once_with('svc_flags')
    mock_container_service.save_attribute.assert_called_once_with(attribute)


# ** test: set_service_dependency_update_existing
def test_set_service_dependency_update_existing(
    mock_container_service: ContainerService,
    flagged_dependency_for_commands: FlaggedDependency,
):
    '''
    Test that SetServiceDependency updates an existing flagged
    dependency when the flag already exists.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    :param flagged_dependency_for_commands: The existing flagged dependency.
    :type flagged_dependency_for_commands: FlaggedDependency
    '''

    # Attribute aggregate with one existing flagged dependency.
    attribute = Aggregate.new(
        ContainerAttributeAggregate,
        id='svc_flags_update',
        module_path='tiferet.models.tests.test_container',
        class_name='TestDependency',
        parameters={},
        dependencies=[flagged_dependency_for_commands],
    )

    mock_container_service.get_attribute.return_value = attribute

    from ..container import SetServiceDependency

    command = SetServiceDependency(container_service=mock_container_service)

    # Update dependency parameters and type via command.
    result_id = command.execute(
        id='svc_flags_update',
        flag='test_alpha',
        module_path='tiferet.models.tests.test_container',
        class_name='TestDependencyAlpha',
        parameters={'test_param': 'updated', 'extra': None},
    )

    assert result_id == 'svc_flags_update'
    dep = attribute.get_dependency('test_alpha')
    assert dep is not None
    # Type should be updated.
    assert dep.module_path == 'tiferet.models.tests.test_container'
    assert dep.class_name == 'TestDependencyAlpha'
    # Parameters should be cleaned (None removed) via set_parameters and
    # merged with existing parameters (new values win).
    assert dep.parameters == {
        'test_param': 'updated',
        'param': 'value1',
    }
    mock_container_service.get_attribute.assert_called_once_with('svc_flags_update')
    mock_container_service.save_attribute.assert_called_once_with(attribute)


# ** test: set_service_dependency_missing_flag
def test_set_service_dependency_missing_flag(
    mock_container_service: ContainerService,
):
    '''
    Test that SetServiceDependency fails when flag is missing or empty.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    attribute = Aggregate.new(
        ContainerAttributeAggregate,
        id='svc_missing_flag',
        module_path='tiferet.models.tests.test_container',
        class_name='TestDependency',
        parameters={},
        dependencies=[],
    )

    mock_container_service.get_attribute.return_value = attribute

    from ..container import SetServiceDependency

    command = SetServiceDependency(container_service=mock_container_service)

    with pytest.raises(TiferetError) as excinfo:
        command.execute(
            id='svc_missing_flag',
            flag=' ',
            module_path='tiferet.models.tests.test_container',
            class_name='TestDependency',
            parameters={'param': 'value'},
        )

    error: TiferetError = excinfo.value
    assert error.error_code == 'COMMAND_PARAMETER_REQUIRED'


# ** test: set_service_dependency_incomplete_type
def test_set_service_dependency_incomplete_type(
    mock_container_service: ContainerService,
):
    '''
    Test that SetServiceDependency rejects an incomplete flagged
    dependency when either module_path or class_name is missing.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    attribute = Aggregate.new(
        ContainerAttributeAggregate,
        id='svc_bad_dep',
        module_path='tiferet.models.tests.test_container',
        class_name='TestDependency',
        parameters={},
        dependencies=[],
    )

    mock_container_service.get_attribute.return_value = attribute

    from ..container import SetServiceDependency

    command = SetServiceDependency(container_service=mock_container_service)

    with pytest.raises(TiferetError) as excinfo:
        command.execute(
            id='svc_bad_dep',
            flag='alpha',
            module_path='tiferet.models.tests.test_container',
            class_name='',
            parameters={'param': 'value'},
        )

    error: TiferetError = excinfo.value
    assert error.error_code == a.const.INVALID_FLAGGED_DEPENDENCY_ID


# ** test: set_service_dependency_not_found
def test_set_service_dependency_not_found(
    mock_container_service: ContainerService,
):
    '''
    Test that SetServiceDependency raises SERVICE_CONFIGURATION_NOT_FOUND
    when the container attribute does not exist.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    mock_container_service.get_attribute.return_value = None

    from ..container import SetServiceDependency

    command = SetServiceDependency(container_service=mock_container_service)

    with pytest.raises(TiferetError) as excinfo:
        command.execute(
            id='missing',
            flag='alpha',
            module_path='tiferet.models.tests.test_container',
            class_name='TestDependency',
            parameters={'param': 'value'},
        )

    error: TiferetError = excinfo.value
    assert error.error_code == a.const.SERVICE_CONFIGURATION_NOT_FOUND_ID

# ** test: remove_service_configuration_existing
def test_remove_service_configuration_existing(
    mock_container_service: ContainerService,
):
    '''
    Test that RemoveServiceConfiguration deletes an existing container
    attribute and returns its id.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    result = Command.handle(
        RemoveServiceConfiguration,
        dependencies={'container_service': mock_container_service},
        id='svc_to_delete',
    )

    assert result == 'svc_to_delete'
    mock_container_service.delete_attribute.assert_called_once_with('svc_to_delete')

# ** test: remove_service_configuration_nonexistent_id
def test_remove_service_configuration_nonexistent_id(
    mock_container_service: ContainerService,
):
    '''
    Test that RemoveServiceConfiguration is idempotent when the attribute
    does not exist (delete_attribute is still called, no error).

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    result = Command.handle(
        RemoveServiceConfiguration,
        dependencies={'container_service': mock_container_service},
        id='missing_id',
    )

    assert result == 'missing_id'
    mock_container_service.delete_attribute.assert_called_once_with('missing_id')

# ** test: remove_service_configuration_missing_id
def test_remove_service_configuration_missing_id(
    mock_container_service: ContainerService,
):
    '''
    Test that RemoveServiceConfiguration fails with COMMAND_PARAMETER_REQUIRED
    when id is missing or empty.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            RemoveServiceConfiguration,
            dependencies={'container_service': mock_container_service},
            id=' ',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == 'COMMAND_PARAMETER_REQUIRED'

# ** test: remove_service_dependency_success_with_remaining_default
def test_remove_service_dependency_success_with_remaining_default(
    mock_container_service: ContainerService,
    flagged_dependency_for_commands: FlaggedDependency,
):
    '''
    Test that RemoveServiceDependency removes a dependency while a
    default type remains configured.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    :param flagged_dependency_for_commands: The flagged dependency to remove.
    :type flagged_dependency_for_commands: FlaggedDependency
    '''

    attribute = Aggregate.new(
        ContainerAttributeAggregate,
        id='svc_remove_default',
        module_path='tiferet.models.tests.test_container',
        class_name='TestDependency',
        parameters={},
        dependencies=[flagged_dependency_for_commands],
    )

    mock_container_service.get_attribute.return_value = attribute

    from ..container import RemoveServiceDependency

    command = RemoveServiceDependency(container_service=mock_container_service)

    result_id = command.execute(
        id='svc_remove_default',
        flag='test_alpha',
    )

    assert result_id == 'svc_remove_default'
    # Dependency should be removed, but default type remains.
    assert attribute.get_dependency('test_alpha') is None
    assert attribute.module_path == 'tiferet.models.tests.test_container'
    assert attribute.class_name == 'TestDependency'
    mock_container_service.get_attribute.assert_called_once_with('svc_remove_default')
    mock_container_service.save_attribute.assert_called_once_with(attribute)

# ** test: remove_service_dependency_success_nonexistent_flag
def test_remove_service_dependency_success_nonexistent_flag(
    mock_container_service: ContainerService,
    flagged_dependency_for_commands: FlaggedDependency,
):
    '''
    Test that RemoveServiceDependency is idempotent when the flag does
    not exist, as long as a type source remains.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    :param flagged_dependency_for_commands: An existing flagged dependency.
    :type flagged_dependency_for_commands: FlaggedDependency
    '''

    attribute = Aggregate.new(
        ContainerAttributeAggregate,
        id='svc_remove_missing',
        module_path='tiferet.models.tests.test_container',
        class_name='TestDependency',
        parameters={},
        dependencies=[flagged_dependency_for_commands],
    )

    mock_container_service.get_attribute.return_value = attribute

    from ..container import RemoveServiceDependency

    command = RemoveServiceDependency(container_service=mock_container_service)

    result_id = command.execute(
        id='svc_remove_missing',
        flag='non_existent_flag',
    )

    assert result_id == 'svc_remove_missing'
    # Dependencies and default type remain unchanged.
    assert attribute.get_dependency('test_alpha') is not None
    assert attribute.module_path == 'tiferet.models.tests.test_container'
    assert attribute.class_name == 'TestDependency'
    mock_container_service.get_attribute.assert_called_once_with('svc_remove_missing')
    mock_container_service.save_attribute.assert_called_once_with(attribute)

# ** test: remove_service_dependency_invalid_after_removal
def test_remove_service_dependency_invalid_after_removal(
    mock_container_service: ContainerService,
    flagged_dependency_for_commands: FlaggedDependency,
):
    '''
    Test that RemoveServiceDependency raises INVALID_SERVICE_CONFIGURATION
    when removing the last type source (no default type and no remaining
    dependencies).

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    :param flagged_dependency_for_commands: The flagged dependency to remove.
    :type flagged_dependency_for_commands: FlaggedDependency
    '''

    # Attribute aggregate with only a flagged dependency and no default type.
    attribute = Aggregate.new(
        ContainerAttributeAggregate,
        id='svc_invalid_after_remove',
        dependencies=[flagged_dependency_for_commands],
        parameters={},
    )

    mock_container_service.get_attribute.return_value = attribute

    from ..container import RemoveServiceDependency

    command = RemoveServiceDependency(container_service=mock_container_service)

    with pytest.raises(TiferetError) as excinfo:
        command.execute(
            id='svc_invalid_after_remove',
            flag='test_alpha',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == a.const.INVALID_SERVICE_CONFIGURATION_ID

# ** test: remove_service_dependency_not_found_attribute
def test_remove_service_dependency_not_found_attribute(
    mock_container_service: ContainerService,
):
    '''
    Test that RemoveServiceDependency raises SERVICE_CONFIGURATION_NOT_FOUND
    when the container attribute does not exist.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    mock_container_service.get_attribute.return_value = None

    from ..container import RemoveServiceDependency

    command = RemoveServiceDependency(container_service=mock_container_service)

    with pytest.raises(TiferetError) as excinfo:
        command.execute(
            id='missing_attr',
            flag='alpha',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == a.const.SERVICE_CONFIGURATION_NOT_FOUND_ID

# ** test: remove_service_dependency_missing_flag
def test_remove_service_dependency_missing_flag(
    mock_container_service: ContainerService
):
    '''
    Test that RemoveServiceDependency fails with COMMAND_PARAMETER_REQUIRED
    when flag is missing or empty.

    :param mock_container_service: The mock container service.
    :type mock_container_service: ContainerService
    '''

    # Import and create the command.
    from ..container import RemoveServiceDependency
    command = RemoveServiceDependency(container_service=mock_container_service)

    # Run the command with the expectation of an error.
    with pytest.raises(TiferetError) as excinfo:
        command.execute(
            id='svc_missing_flag_remove',
            flag=' ',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
