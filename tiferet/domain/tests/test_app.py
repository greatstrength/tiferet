# *** imports

# ** infra

import pytest

# ** app
from . import *


# *** fixtures

# ** fixture: app_repository_configuration
@pytest.fixture
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

# ** test: test_app_context_dependency_new
def test_app_context_dependency_new(app_context_dependency):

    # Assert the app dependency is valid.
    assert app_context_dependency.attribute_id == 'app_context'
    assert app_context_dependency.module_path == 'tiferet.contexts.app'
    assert app_context_dependency.class_name == 'AppInterfaceContext'


# ** test: test_app_interface_new
def test_app_interface_new(test_app_interface):  

    # Assert the app interface is valid.
    assert test_app_interface.id == 'test'
    assert test_app_interface.name == 'Test Interface'
    assert test_app_interface.description == 'The test interface.'
    assert test_app_interface.feature_flag == 'test'
    assert test_app_interface.data_flag == 'test'
    assert len(test_app_interface.dependencies) == 7


# ** test: test_app_interface_get_dependency
def test_app_interface_get_dependency(test_app_interface):

    # Get the app dependency.
    app_dependency = test_app_interface.get_dependency('app_context')

    # Assert the app dependency is valid.
    assert app_dependency.attribute_id == 'app_context'
    assert app_dependency.module_path == 'tiferet.contexts.app'
    assert app_dependency.class_name == 'AppInterfaceContext'


# ** test: test_app_interface_get_dependency_invalid
def test_app_interface_get_dependency_invalid(test_app_interface):

    # Assert the app dependency is invalid.
    assert test_app_interface.get_dependency('invalid') is None


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