# *** imports

# ** infra

import pytest

# ** app
from . import *


# *** fixtures

# ** fixture: app_dependency
@pytest.fixture(scope="module")
def app_dependency():
    return AppDependency.new(
        attribute_id='app_context',
        module_path='tests.contexts.app',
        class_name='TestAppInterfaceContext',
    )


# ** fixture: app_interface
@pytest.fixture(scope="module")
def app_interface(app_dependency):
    return AppInterface.new(
        id='test',
        name='test interface',
        description='test description',
        feature_flag='test feature flag',
        data_flag='test data flag',
        dependencies=[
            app_dependency,
        ],
    )


# ** fixture: app_repository_configuration
@pytest.fixture(scope="module")
def app_repository_configuration():
    return AppRepositoryConfiguration.new()


# ** fixture: app_repository_configuration_custom
@pytest.fixture(scope="module")
def app_repository_configuration_custom():
    return AppRepositoryConfiguration.new(
        module_path='test.module.path',
        class_name='TestClassName',
        params=dict(
            test_param='test value',
        ),
    )


# *** tests

# ** test: test_app_dependency_new
def test_app_dependency_new(app_dependency):

    # Assert the app dependency is valid.
    assert app_dependency.attribute_id == 'app_context'
    assert app_dependency.module_path == 'tests.contexts.app'
    assert app_dependency.class_name == 'TestAppInterfaceContext'


# ** test: test_app_interface_new
def test_app_interface_new(app_interface):  

    # Assert the app interface is valid.
    assert app_interface.id == 'test'
    assert app_interface.name == 'test interface'
    assert app_interface.description == 'test description'
    assert app_interface.feature_flag == 'test feature flag'
    assert app_interface.data_flag == 'test data flag'
    assert len(app_interface.dependencies) == 1
    assert app_interface.dependencies[0].attribute_id == 'app_context'
    assert app_interface.dependencies[0].module_path == 'tests.contexts.app'
    assert app_interface.dependencies[0].class_name == 'TestAppInterfaceContext'


# ** test: test_app_interface_get_dependency
def test_app_interface_get_dependency(app_interface):

    # Get the app dependency.
    app_dependency = app_interface.get_dependency('app_context')

    # Assert the app dependency is valid.
    assert app_dependency.attribute_id == 'app_context'
    assert app_dependency.module_path == 'tests.contexts.app'
    assert app_dependency.class_name == 'TestAppInterfaceContext'


# ** test: test_app_interface_get_dependency_invalid
def test_app_interface_get_dependency_invalid(app_interface):

    # Assert the app dependency is invalid.
    assert app_interface.get_dependency('invalid') is None


# ** test: test_app_repository_configuration_new
def test_app_repository_configuration_new(app_repository_configuration):

    # Assert the app repository configuration is valid.
    assert app_repository_configuration.module_path == 'tiferet.repos.app'
    assert app_repository_configuration.class_name == 'YamlProxy'
    assert app_repository_configuration.params == dict(
        app_config_file='app/configs/app.yml')


# ** test: test_app_repository_configuration_new_custom
def test_app_repository_configuration_new_custom(app_repository_configuration_custom):

    # Assert the app repository configuration is valid.
    assert app_repository_configuration_custom.module_path == 'test.module.path'
    assert app_repository_configuration_custom.class_name == 'TestClassName'
    assert app_repository_configuration_custom.params == dict(test_param='test value')