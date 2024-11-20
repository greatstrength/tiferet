import pytest
from ...domain import AppInterface, AppDependency
from ...data import AppDependencyYamlData, AppInterfaceYamlData


@pytest.fixture(scope="module")
def test_app_dependency():
    return AppDependency.new(
        attribute_id='app_context',
        module_path='tests.contexts.app',
        class_name='TestAppInterfaceContext',
    )


@pytest.fixture(scope="module")
def test_app_interface(test_app_dependency):
    return AppInterface.new(
        id='test',
        name='test interface',
        description='test description',
        feature_flag='test feature flag',
        data_flag='test data flag',
        dependencies=[
            test_app_dependency,
        ],
    )


@pytest.fixture(scope="module")
def test_app_dependency_yaml_data():
    return AppDependencyYamlData.new(
        attribute_id='app_context',
        module_path='tests.contexts.app',
        class_name='TestAppContext',
    )


@pytest.fixture(scope="module")
def test_app_interface_yaml_data():
    return AppInterfaceYamlData.new(
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
