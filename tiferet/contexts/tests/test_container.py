# *** imports

# app
from . import *


# *** fixtures


# ** fixture: container_dependency
@pytest.fixture(scope='session')
def container_dependency():
    return ContainerDependency.new(
        module_path='tiferet.contexts.tests',
        class_name='TestProxy',
        flag='test',
        parameters={'config_file': 'test.yml'}
    )


# ** fixture: container_attribute
@pytest.fixture(scope='session')
def container_attribute(container_dependency):
    return ContainerAttribute.new(
        id='test_repo',
        type='data',
        dependencies=[container_dependency],
    )


# ** fixture: feature_container_attribute
@pytest.fixture(scope='session')
def feature_container_attribute(container_dependency):
    return ContainerAttribute.new(
        id='test_repo',
        type='feature',
        dependencies=[container_dependency],
    )

# ** fixture: container_repo
@pytest.fixture(scope='session')
def container_repo(mock_container_repo, container_attribute):

    # Create a container repo with a test attribute
    return mock_container_repo(
        attributes=[container_attribute],
        constants={'config_file': 'test.yml'}
    )


# ** fixture: container_context
@pytest.fixture(scope='session')
def container_context(container_repo):
    return ContainerContext(
        interface_id="test_interface",
        container_repo=container_repo,
        feature_flag="test",
        data_flag="test"
    )


# *** tests

# ** test: test_container_context_init
def test_container_context_init(container_context):

    # Ensure the container context was initialized correctly
    assert container_context.interface_id == "test_interface"
    assert len(container_context.attributes) == 1
    assert container_context.feature_flag == "test"
    assert container_context.data_flag == "test"


# ** test: test_get_dependency
def test_get_dependency(container_context):
    
    
    # Call get_dependency with a test attribute
    result = container_context.get_dependency("test_repo")

    # Ensure the dependency was retrieved
    assert result is not None
    assert result.config_file == 'test.yml'


# ** test: test_create_injector
def test_create_injector(container_context):

    # Call create_injector.
    injector = container_context.create_injector()

    # Ensure the injector was created.
    assert injector is not None


# ** test: test_import_dependency
def test_import_dependency(container_context, container_attribute):

    # Call import_dependency with a test attribute
    result = container_context.import_dependency(container_attribute, "test")

    # Ensure the dependency was imported
    assert result is not None
    assert result == TestProxy