# *** imports

# ** infra
import pytest

# ** app
from ..dependencies import *


# *** fixtures

# ** fixture: dependency_with_constant
@pytest.fixture
def dependency_with_constant():
    """Fixture to create a dependency with a constant value for testing."""

    # Define a simple dependency class with a constant value.
    class TestDependency(object):
        """TestDependency class that holds a constant value."""

        # * attribute: const_value
        const_value: str

        def __init__(self, const_value: str):
            self.const_value = const_value

    return TestDependency

# ** fixture: dependency_with_nested_dependency
@pytest.fixture
def dependency_with_nested_dependency():
    class NestedDependency(object):
        def __init__(self, const_value: str):
            """NestedDependency class that holds a constant value."""

            # * attribute: const_value
            self.const_value = const_value

    class TestDependency(object):
        """TestDependency class that holds a nested dependency."""

        # * attribute: nested
        nested: NestedDependency

        def __init__(self, nested: NestedDependency):
            self.nested = nested

    return TestDependency, NestedDependency


# ** fixture: invalid_dependency_with_kwargs_initialization
@pytest.fixture
def invalid_dependency_with_kwargs_initialization():
    """
    Fixture to create a dependency that requires keyword arguments for initialization.
    This is used to test error handling when dependencies cannot be resolved.
    """

    class InvalidDependency(object):
        """InvalidDependency class that requires keyword arguments."""

        def __init__(self, **kwargs):
            if not kwargs:
                raise ValueError("Invalid initialization: kwargs are required")

    return InvalidDependency


# ***. tests

# ** test: create_injector_with_dependency
def test_create_injector_with_dependency(dependency_with_constant):
    """
    Test creating an injector with a dependency that has a constant value.
    """
    injector = create_injector.execute(
        'TestInjector',
        dependencies=dict(
            test_dependency=dependency_with_constant
        ),
        const_value='test_value'
    )

    # Create an instance of the dependency.
    instance = get_dependency.execute(
        injector,
        'test_dependency'
    )

    # Assert the instance has the correct constant value.
    assert instance
    assert instance.const_value == 'test_value'


# ** test: create_injector_with_nested_dependency
def test_create_injector_with_nested_dependency(dependency_with_nested_dependency):
    """
    Test creating an injector with a dependency that has a nested dependency.
    """

    # Get the nested dependency and the test dependency from the fixture.
    test_dependency, nested_dependency = dependency_with_nested_dependency


    # Create an injector with the nested dependency.
    injector = create_injector.execute(
        'TestInjector',
        dependencies={
            'test_dependency': test_dependency,
            'nested': nested_dependency
        },
        const_value='nested_value'
    )

    # Create an instance of the test dependency.
    instance = get_dependency.execute(
        injector,
        'test_dependency'
    )

    # Assert the instance has the correct nested constant value.
    assert instance
    assert instance.nested
    assert instance.nested.const_value == 'nested_value'


# ** test: test_create_injector_with_unresolved_dependency
def test_create_injector_with_unresolved_dependency(dependency_with_nested_dependency):
    """
    Test creating an injector with a dependency that has a nested dependency.
    """

    # Get the nested dependency and the test dependency from the fixture.
    test_dependency, nested_dependency = dependency_with_nested_dependency

    # Create an injector with the nested dependency.
    injector = create_injector.execute(
        'TestInjector',
        dependencies={
            'test_dependency': test_dependency,
            'incorrect_name': nested_dependency
        },
        const_value='nested_value'
    )

    # Attempt to create an instance of the test dependency.
    with pytest.raises(TiferetError) as exc_info:
        get_dependency.execute(
            injector,
            'test_dependency'
        )

    # Assert that the error is raised due to unresolved dependency.
    assert exc_info.value.error_code == 'INVALID_DEPENDENCY_ERROR', "Should raise INVALID_DEPENDENCY_ERROR error"
    assert 'Dependency test_dependency could not be resolved:' in str(exc_info.value), "Should include unresolved dependency message"
    

# ** test: create_injector_with_invalid_dependency
def test_create_injector_with_invalid_dependency(invalid_dependency_with_kwargs_initialization):
    """
    Test creating an injector with a dependency that requires keyword arguments for initialization.
    This should raise an error when trying to resolve the dependency.
    """


    injector = create_injector.execute(
        'TestInjector',
        dependencies=dict(
            test_dependency=invalid_dependency_with_kwargs_initialization
        )
    )

    # Attempt to create an instance of the dependency.
    with pytest.raises(TiferetError) as exc_info:
        get_dependency.execute(
            injector,
            'test_dependency'
        )
    
    # Assert that the error is raised due to invalid dependency initialization.
    assert exc_info.value.error_code == 'INVALID_DEPENDENCY_ERROR', "Should raise INVALID_DEPENDENCY_ERROR error"
    assert 'Dependency test_dependency could not be resolved:' in str(exc_info.value), "Should include unresolved dependency message"


