# *** imports

# ** infra
import pytest

# ** app
from ..container import *


# *** fixtures

# ** fixture: flagged_dependency
@pytest.fixture
def flagged_dependency() -> FlaggedDependency:
    return ValueObject.new(
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
    return ValueObject.new(
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
def container_attribute(flagged_dependency) -> ContainerAttribute:
    return Entity.new(
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
    container_attribute,
    flagged_dependency
):
    """Test that the container attribute can retrieve a flagged dependency."""

    # Get the flagged dependency.
    dependency = container_attribute.get_dependency('test_alpha')

    # Assert the dependency is valid.
    assert dependency.module_path == flagged_dependency.module_path
    assert dependency.class_name == flagged_dependency.class_name
    assert dependency.flag == flagged_dependency.flag
    assert dependency.parameters == flagged_dependency.parameters


# ** test: test_container_attribute_get_dependency_invalid
def test_container_attribute_get_dependency_invalid(container_attribute):
    """Test that the container attribute returns None for an invalid dependency."""

    # Assert the container dependency is invalid.
    assert container_attribute.get_dependency('invalid') is None


# ** test: test_container_attribute_set_dependency_exists(
def test_container_attribute_set_dependency_exists(
    container_attribute,
    flagged_dependency
):
    """Test that the container attribute can set an existing flagged dependency."""

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
    )


# ** test: test_container_attribute_set_dependency_new
def test_container_attribute_set_dependency_new(
    container_attribute,
    flagged_dependency_to_add
):
    """Test that the container attribute can set a new flagged dependency."""

    # Set the beta dependency.
    container_attribute.set_dependency(flagged_dependency_to_add)

    # Verify that the beta dependency is set.
    assert len(container_attribute.dependencies) == 2
    assert container_attribute.get_dependency('test_beta') == flagged_dependency_to_add


# ** test: container_attirbute_get_dependency_muliple_flags
def test_container_attribute_get_dependency_multiple_flags(
    container_attribute,
    flagged_dependency,
    flagged_dependency_to_add
):
    """Test that the container attribute can retrieve a flagged dependency with multiple flags."""

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

