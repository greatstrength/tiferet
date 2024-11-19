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

    # Create a new mock app interface repository.
    from ..repos import MockAppRepository
    app_repo = MockAppRepository(
        interfaces=[
            AppInterface.new(
                id='test',
                name='test interface',
                description='test description',
                feature_flag='test feature flag',
                data_flag='test data flag',
                dependencies=[
                     AppDependency.new(
                            attribute_id='app_context',
                            module_path='tests.contexts.app',
                            class_name='TestAppInterfaceContext',
                     ),
                ],
            ),
        ],
    )
