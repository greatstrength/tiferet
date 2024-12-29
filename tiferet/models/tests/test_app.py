# *** imports

# ** infra
import pytest

# ** app
from ..app import *


# *** fixtures
# ** fixture: app_context_dependency
@pytest.fixture
def app_dependency():
    return ValueObject.new(
        AppDependency,
        attribute_id='app_context',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
    )

# ** fixture: app_interface
@pytest.fixture
def app_interface(
    app_dependency
):
    return Entity.new(
        AppInterface,
        id='test',
        name='Test Interface',
        description='The test interface.',
        feature_flag='test',
        data_flag='test',
        dependencies=[
            app_dependency,
        ],
    )


# *** tests

# ** test: test_app_interface
def test_app_interface(app_interface):

    # Assert the app interface is valid.
    assert app_interface.id == 'test'
    assert app_interface.name == 'Test Interface'
    assert app_interface.description == 'The test interface.'
    assert app_interface.feature_flag == 'test'
    assert app_interface.data_flag == 'test'
    assert len(app_interface.dependencies) == 1
    assert app_interface.dependencies[0].attribute_id == 'app_context'
    assert app_interface.dependencies[0].module_path == 'tiferet.contexts.app'
    assert app_interface.dependencies[0].class_name == 'AppInterfaceContext'
    

# ** test: test_app_interface_get_dependency
def test_app_interface_get_dependency(app_interface):

    # Get the app dependency.
    app_dependency = app_interface.get_dependency('app_context')

    # Assert the app dependency is valid.
    assert app_dependency.attribute_id == 'app_context'
    assert app_dependency.module_path == 'tiferet.contexts.app'
    assert app_dependency.class_name == 'AppInterfaceContext'


# ** test: test_app_interface_get_dependency_invalid
def test_app_interface_get_dependency_invalid(app_interface):

    # Assert the app dependency is invalid.
    assert app_interface.get_dependency('invalid') is None
