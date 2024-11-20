from ...domain import AppInterface, AppDependency
from ...data import AppDependencyYamlData, AppInterfaceYamlData

# ** domain: test_app_dependency
test_app_dependency = AppDependency.new(
    attribute_id='app_context',
    module_path='tests.contexts.app',
    class_name='TestAppInterfaceContext',
)

# ** domain: test_app_interface
test_app_interface = AppInterface.new(
    id='test',
    name='test interface',
    description='test description',
    feature_flag='test feature flag',
    data_flag='test data flag',
    dependencies=[
        test_app_dependency,
    ],
)

# ** data: test_app_dependency_yaml_data
test_app_dependency_yaml_data = AppDependencyYamlData.new(
    attribute_id='app_context',
    module_path='tests.contexts.app',
    class_name='TestAppContext',
)

# ** data: test_app_interface_yaml_data
test_app_interface_yaml_data = AppInterfaceYamlData.new(
    id='test',
    name='test interface',
    description='test description',
    feature_flag='test feature flag',
    data_flag='test data flag',
    app_context=dict(
        module_path='tests.contexts.app',
        class_name='TestAppInterfaceContext',
    ),
)
