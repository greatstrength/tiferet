"""Tiferet Container Models Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..container import (
    ModelObject,
    FlaggedDependency,
    ContainerAttribute,
)

# *** fixtures

# ** fixture: flagged_dependency
@pytest.fixture
def flagged_dependency() -> FlaggedDependency:
    '''
    Fixture to create a FlaggedDependency instance for testing.
    '''

    # Create a flagged dependency.
    return ModelObject.new(
        FlaggedDependency,
        module_path='tiferet.proxies.tests',
        class_name='AlphaTestProxy',
        flag='test_alpha',
        parameters=dict(
            test_param='test_value',
            param1='value1',
        )
    )

# ** fixture: flagged_dependency_to_add
@pytest.fixture
def flagged_dependency_to_add() -> FlaggedDependency:
    '''
    Fixture to create a FlaggedDependency instance for testing addition.
    '''

    # Create a new flagged dependency.
    return ModelObject.new(
        FlaggedDependency,
        module_path='tiferet.proxies.tests',
        class_name='BetaTestProxy',
        flag='test_beta',
        parameters=dict(
            test_param='test_value',
            param2='value2'
        )
    )

# ** fixture: container_attribute
@pytest.fixture
def container_attribute(flagged_dependency: FlaggedDependency) -> ContainerAttribute:
    '''
    Fixture to create a ContainerAttribute instance for testing.

    :param flagged_dependency: The flagged dependency to add to the container attribute.
    :type flagged_dependency: FlaggedDependency
    :return: The created container attribute.
    :rtype: ContainerAttribute
    '''

    # Create a container attribute with a flagged dependency.
    return ModelObject.new(
        ContainerAttribute,
        id='test_repo',
        module_path='tiferet.proxies.tests',
        class_name='TestProxy',
        dependencies=[
            flagged_dependency
        ],
        parameters=dict(
            test_param='test_value',
            param0='value0'
        )
    )

# *** tests

# ** test: container_attribute_get_dependency
def test_container_attribute_get_dependency(
    container_attribute: ContainerAttribute,
    flagged_dependency: FlaggedDependency
):
    '''
    Test that the container attribute can retrieve a flagged dependency.

    :param container_attribute: The container attribute to test.
    :type container_attribute: ContainerAttribute
    :param flagged_dependency: The flagged dependency to test.
    :type flagged_dependency: FlaggedDependency
    '''

    # Get the flagged dependency.
    dependency = container_attribute.get_dependency('test_alpha')

    # Assert the dependency is valid.
    assert dependency.module_path == flagged_dependency.module_path
    assert dependency.class_name == flagged_dependency.class_name
    assert dependency.flag == flagged_dependency.flag
    assert dependency.parameters == flagged_dependency.parameters

# ** test: container_attribute_get_dependency_invalid
def test_container_attribute_get_dependency_invalid(container_attribute: ContainerAttribute):
    ''''
    Test that the container attribute returns None for an invalid dependency.

    :param container_attribute: The container attribute to test.
    :type container_attribute: ContainerAttribute
    '''

    # Assert the container dependency is invalid.
    assert container_attribute.get_dependency('invalid') is None

# ** test: container_attribute_set_dependency_exists(
def test_container_attribute_set_dependency_exists(
    container_attribute : ContainerAttribute,
    flagged_dependency : FlaggedDependency
):
    '''
    Test that the container attribute can set an existing flagged dependency.

    :param container_attribute: The container attribute to test.
    :type container_attribute: ContainerAttribute
    :param flagged_dependency: The flagged dependency to test.
    :type flagged_dependency: FlaggedDependency
    '''

    # Update the flagged dependency.
    flagged_dependency.parameters['test_param_2'] = 'test_value_2'

    # Set the flagged dependency.
    container_attribute.set_dependency(flagged_dependency)

    # Get the flagged dependency.
    dependency = container_attribute.get_dependency('test_alpha')

    # Assert the dependency is valid.
    assert dependency.module_path == flagged_dependency.module_path
    assert dependency.class_name == flagged_dependency.class_name
    assert dependency.flag == flagged_dependency.flag
    assert dependency.parameters == dict(
        test_param='test_value',
        param1='value1',
        test_param_2='test_value_2'
    )

# ** test: container_attribute_set_dependency_new
def test_container_attribute_set_dependency_new(
    container_attribute : ContainerAttribute,
    flagged_dependency_to_add: FlaggedDependency
):
    '''
    Test that the container attribute can set a new flagged dependency.

    :param container_attribute: The container attribute to test.
    :type container_attribute: ContainerAttribute
    :param flagged_dependency_to_add: The flagged dependency to add.
    :type flagged_dependency_to_add: FlaggedDependency
    '''

    # Set the beta dependency.
    container_attribute.set_dependency(flagged_dependency_to_add)

    # Verify that the beta dependency is set.
    assert len(container_attribute.dependencies) == 2
    assert container_attribute.get_dependency('test_beta') == flagged_dependency_to_add

# ** test: container_attribute_get_dependency_muliple_flags
def test_container_attribute_get_dependency_multiple_flags(
    container_attribute : ContainerAttribute,
    flagged_dependency: FlaggedDependency,
    flagged_dependency_to_add: FlaggedDependency
):
    '''
    Test that the container attribute can retrieve a flagged dependency with multiple flags.

    :param container_attribute: The container attribute to test.
    :type container_attribute: ContainerAttribute
    :param flagged_dependency: The flagged dependency to test.
    :type flagged_dependency: FlaggedDependency
    :param flagged_dependency_to_add: The flagged dependency to add.
    :type flagged_dependency_to_add: FlaggedDependency
    '''

    # Set the beta dependency.
    container_attribute.set_dependency(flagged_dependency_to_add)

    # Assert that the test_alpha dependency is returned.
    dependency = container_attribute.get_dependency('test_alpha', 'test_beta')
    assert dependency.module_path == flagged_dependency.module_path
    assert dependency.class_name == flagged_dependency.class_name
    assert dependency.flag == flagged_dependency.flag
    assert dependency.parameters == flagged_dependency.parameters

    # Assert that the test_beta dependency is returned when flipping the order.
    dependency = container_attribute.get_dependency('test_beta', 'test_alpha')
    assert dependency.module_path == flagged_dependency_to_add.module_path
    assert dependency.class_name == flagged_dependency_to_add.class_name
    assert dependency.flag == flagged_dependency_to_add.flag
    assert dependency.parameters == flagged_dependency_to_add.parameters
