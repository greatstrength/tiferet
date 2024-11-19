from ...domain.app import AppDependency, AppInterface, ModuleDependency


def test_app_dependency_new():

    # Create a new app dependency.
    from ..configs.app import test_app_dependency as app_dependency

    # Assert the app dependency is valid.
    assert app_dependency.attribute_id == 'app_context'
    assert app_dependency.module_path == 'tests.contexts.app'
    assert app_dependency.class_name == 'TestAppInterfaceContext'


def test_app_interface_new():

    # Create a new app interface.
    from ..configs.app import test_app_interface as app_interface

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


def test_app_interface_get_dependency():

    # Create a new app interface.
    from ..configs.app import test_app_interface as app_interface

    # Get the app dependency.
    app_dependency = app_interface.get_dependency('app_context')

    # Assert the app dependency is valid.
    assert app_dependency.attribute_id == 'app_context'
    assert app_dependency.module_path == 'tests.contexts.app'
    assert app_dependency.class_name == 'TestAppInterfaceContext'


def test_app_interface_get_dependency_invalid():

    # Create a new app interface.
    from ..configs.app import test_app_interface as app_interface

    # Assert the app dependency is invalid.
    assert app_interface.get_dependency('invalid') is None


def test_app_repository_configuration_new_default():

    # Create a new app repository configuration.
    from ...domain.app import AppRepositoryConfiguration

    # Create a new app repository configuration object.
    app_repository_configuration = AppRepositoryConfiguration.new()

    # Assert the app repository configuration is valid.
    assert app_repository_configuration.module_path == 'tiferet.repos.app'
    assert app_repository_configuration.class_name == 'YamlProxy'
    assert app_repository_configuration.params == dict(
        app_config_file='app/configs/app.yml')


def test_app_repository_configuration_new_custom():

    # Create a new app repository configuration.
    from ...domain.app import AppRepositoryConfiguration

    # Create a new app repository configuration object.
    app_repository_configuration = AppRepositoryConfiguration.new(
        module_path='test.module.path',
        class_name='TestClassName',
        params=dict(
            test_param='test value',
        ),
    )

    # Assert the app repository configuration is valid.
    assert app_repository_configuration.module_path == 'test.module.path'
    assert app_repository_configuration.class_name == 'TestClassName'
    assert app_repository_configuration.params == dict(test_param='test value')
