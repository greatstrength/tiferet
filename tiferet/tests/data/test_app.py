from ...data.app import AppDependencyYamlData, AppInterfaceYamlData

def test_app_dependency_yaml_data_new():

    # Create yaml data representation.
    yaml_data = dict(
        app_context=dict(
            module_path='tests.contexts.app',
            class_name='TestAppContext',
        )
    )

    # Create a new app dependency yaml data object.
    for context, data in yaml_data.items():
        app_dependency_yaml_data = AppDependencyYamlData.new(attribute_id=context, **data)

    # Assert the app dependency yaml data object is valid.
    assert app_dependency_yaml_data.attribute_id == 'app_context'
    assert app_dependency_yaml_data.module_path == 'tests.contexts.app'
    assert app_dependency_yaml_data.class_name == 'TestAppContext'


def test_app_dependency_yaml_data_to_primitive():

    # Import test data.
    from ..configs.app import test_app_dependency_yaml_data as app_dependency_yaml_data

    # Convert the app dependency yaml data object to a primitive.
    primitive = app_dependency_yaml_data.to_primitive('to_data.yaml')

    # Assert the primitive is valid.
    assert primitive.get('attribute_id', None) == None
    assert primitive.get('module_path') == 'tests.contexts.app'
    assert primitive.get('class_name') == 'TestAppContext'


def test_app_dependency_yaml_data_map():

    # Import test data.
    from ..configs.app import test_app_dependency_yaml_data as app_dependency_yaml_data

    # Map the app dependency yaml data object to a model object.
    app_dependency = app_dependency_yaml_data.map()

    # Assert the app dependency is valid.
    assert app_dependency.attribute_id == 'app_context'
    assert app_dependency.module_path == 'tests.contexts.app'
    assert app_dependency.class_name == 'TestAppContext'


def test_app_interface_yaml_data_new():

    # Import test data.
    from ..configs.app import test_app_interface_yaml_data as app_interface_yaml_data

    # Assert the app interface yaml data object is valid.
    assert app_interface_yaml_data.id == 'test'
    assert app_interface_yaml_data.name == 'test interface'
    assert app_interface_yaml_data.description == 'test description'
    assert app_interface_yaml_data.feature_flag == 'test feature flag'
    assert app_interface_yaml_data.data_flag == 'test data flag'
    assert app_interface_yaml_data.app_context.module_path == 'tests.contexts.app'
    assert app_interface_yaml_data.app_context.class_name == 'TestAppInterfaceContext'

    # Assert that the default values are set.
    assert app_interface_yaml_data.feature_context.module_path == 'tiferet.contexts.feature'
    assert app_interface_yaml_data.feature_context.class_name == 'FeatureContext'
    assert app_interface_yaml_data.container_context.module_path == 'tiferet.contexts.container'
    assert app_interface_yaml_data.container_context.class_name == 'ContainerContext'
    assert app_interface_yaml_data.error_context.module_path == 'tiferet.contexts.error'
    assert app_interface_yaml_data.error_context.class_name == 'ErrorContext'
    assert app_interface_yaml_data.feature_repo.module_path == 'tiferet.repos.feature'
    assert app_interface_yaml_data.feature_repo.class_name == 'YamlProxy'
    assert app_interface_yaml_data.container_repo.module_path == 'tiferet.repos.container'
    assert app_interface_yaml_data.container_repo.class_name == 'YamlProxy'
    assert app_interface_yaml_data.error_repo.module_path == 'tiferet.repos.error'
    assert app_interface_yaml_data.error_repo.class_name == 'YamlProxy'


def test_app_interface_yaml_data_to_primitive():

    # Create a new app interface yaml data object.
    from ..configs.app import test_app_interface_yaml_data as app_interface_yaml_data

    # Convert the app interface yaml data object to a primitive.
    primitive = app_interface_yaml_data.to_primitive('to_data.yaml')

    # Assert the primitive is valid.
    assert primitive.get('id', None) == None
    assert primitive.get('name') == 'test interface'
    assert primitive.get('description') == 'test description'
    assert primitive.get('feature_flag') == 'test feature flag'
    assert primitive.get('data_flag') == 'test data flag'
    assert primitive.get('app_context', {}).get('module_path') == 'tests.contexts.app'
    assert primitive.get('app_context', {}).get('class_name') == 'TestAppInterfaceContext'

    # Assert that the default values are set.
    assert primitive.get('feature_context', {}).get('module_path') == 'tiferet.contexts.feature'
    assert primitive.get('feature_context', {}).get('class_name') == 'FeatureContext'
    assert primitive.get('container_context', {}).get('module_path') == 'tiferet.contexts.container'
    assert primitive.get('container_context', {}).get('class_name') == 'ContainerContext'
    assert primitive.get('error_context', {}).get('module_path') == 'tiferet.contexts.error'
    assert primitive.get('error_context', {}).get('class_name') == 'ErrorContext'
    assert primitive.get('feature_repo', {}).get('module_path') == 'tiferet.repos.feature'
    assert primitive.get('feature_repo', {}).get('class_name') == 'YamlProxy'
    assert primitive.get('container_repo', {}).get('module_path') == 'tiferet.repos.container'
    assert primitive.get('container_repo', {}).get('class_name') == 'YamlProxy'
    assert primitive.get('error_repo', {}).get('module_path') == 'tiferet.repos.error'
    assert primitive.get('error_repo', {}).get('class_name') == 'YamlProxy'


def test_app_interface_yaml_data_map():

    # Import test data.
    from ..configs.app import test_app_interface_yaml_data as app_interface_yaml_data

    # Map the app interface yaml data object to a model object.
    app_interface = app_interface_yaml_data.map()

    # Assert the app interface is valid.
    assert app_interface.id == 'test'
    assert app_interface.name == 'test interface'
    assert app_interface.description == 'test description'
    assert app_interface.feature_flag == 'test feature flag'
    assert app_interface.data_flag == 'test data flag'
    assert app_interface.dependencies[0].module_path == 'tests.contexts.app'
    assert app_interface.dependencies[0].class_name == 'TestAppInterfaceContext'