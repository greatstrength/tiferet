from ...domain.app import AppDependency, AppInterface, ModuleDependency


def test_app_dependency_new():
    
        # Create a new app dependency.
        app_dependency = AppDependency.new(
            attribute_id='feature_context',
            module_path='tests.contexts.feature',
            class_name='TestFeatureContext',
        )
    
        # Assert the app dependency is valid.
        assert app_dependency.attribute_id == 'feature_context'
        assert app_dependency.module_path == 'tests.contexts.feature'
        assert app_dependency.class_name == 'TestFeatureContext'


def test_app_interface_new():

    # Create a new app interface.
    app_interface = AppInterface.new(
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
    )

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
    