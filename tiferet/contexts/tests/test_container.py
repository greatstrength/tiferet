# *** imports

# infra
import pytest

# ** app
from ..container import *


# *** mocks
class MockContainerRepository(ContainerRepository):

    def __init__(self, attributes: List[ContainerAttribute] = [], constants: Dict[str, str] = {}):
        self.attributes = attributes
        self.constants = constants

    def get_attribute(self, attribute_id, type):
        return next((attribute for attribute in self.attributes if attribute.id == attribute_id), None)

    def list_all(self):
        return self.attributes, self.constants


# *** fixtures

# ** fixture: test_env_var
@pytest.fixture
def test_env_var():
    '''
    Test environment variable.
    '''

    # Return the test environment variable.
    return os.getenv("TEST_ENV_VAR")


# ** fixture: mock_container_repository_raise_error
@pytest.fixture
def mock_container_repository_raise_error():

    class MockContainerRepository(ContainerRepository):

        def get_attribute(self, attribute_id, type):
            raise Exception("Error")

        def list_all(self):
            raise Exception("Error")


    return MockContainerRepository

# ** fixture: container_dependency
@pytest.fixture
def container_dependency():
    return ValueObject.new(
        ContainerDependency,
        module_path='tiferet.contexts.tests.test_container',
        class_name='MockContainerRepository',
        flag='test',
        parameters={},
    )



# ** fixture: test_repo_container_attribute
@pytest.fixture
def container_attribute(container_dependency):
    return Entity.new(
        ContainerAttribute,
        id='test_dependency',
        type='data',
        dependencies=[container_dependency],
    )


# ** fixture: container_repo
@pytest.fixture
def container_repo(
    container_attribute
):
    return MockContainerRepository(
        attributes=[
            container_attribute
        ]
    )


# ** fixture: container_context
@pytest.fixture
def container_context(container_repo):
    return ContainerContext(
        interface_id="test_interface",
        container_repo=container_repo,
        feature_flag="test",
        data_flag="test"
    )


# *** tests

# ** test: test_create_injector_raises_failure_error
def test_create_injector_raises_failure_error(container_context):

    # Call create_injector with an invalid interface ID
    with pytest.raises(TiferetError) as excinfo:
        create_injector(None)

    # Ensure the error message is correct
    assert excinfo.value.error_code == 'CREATE_INJECTOR_FAILED'
    assert 'Error creating injector:' in str(excinfo.value)


# ** test: test_import_dependency_raises_failure_error
def test_import_dependency_raises_failure_error():

    # Call import_dependency with an invalid attribute ID
    with pytest.raises(TiferetError) as excinfo:
        import_dependency('app.import.does_not_exist', 'ClassDoesNotExist')

    # Ensure the error message is correct
    assert excinfo.value.error_code == 'IMPORT_DEPENDENCY_FAILURE'
    assert 'Error importing dependency:' in str(excinfo.value)


# ** test: test_container_context_init_raises_failure_error
def test_container_context_init_raises_failure_error(mock_container_repository_raise_error):

    # Create the repository.
    repository = mock_container_repository_raise_error()

    # Call ContainerContext.__init__ with an invalid interface ID
    with pytest.raises(TiferetError) as excinfo:
        ContainerContext(
            "test_interface", 
            repository,
            "test",
            "test",
        )

    # Ensure the error message is correct
    assert excinfo.value.error_code == 'CONTAINER_ATTRIBUTE_LOADING_FAILED'
    assert 'Error loading container attributes:' in str(excinfo.value)


# ** test: test_container_context_init
def test_container_context_init(container_context):

    # Ensure the container context was initialized correctly
    assert container_context.interface_id == "test_interface"
    assert container_context.feature_flag == "test"
    assert container_context.data_flag == "test"


# ** test: test_parse_parameter
def test_parse_parameter(container_context, test_env_var):

    # Test parsing an environment variable
    result = container_context.parse_parameter("$env.TEST_ENV_VAR")
    assert result == test_env_var

    # Test parsing a regular parameter
    result = container_context.parse_parameter("test")
    assert result == "test"


# ** test: test_parse_parameter_raises_failure_error
def test_parse_parameter_raises_failure_error(container_context):

    # Call parse_parameter with an invalid parameter
    with pytest.raises(TiferetError) as excinfo:
        container_context.parse_parameter("$env.does_not_exist")

    # Ensure the error message is correct
    assert excinfo.value.error_code == 'PARAMETER_PARSING_FAILED'
    assert 'Error parsing parameter:' in str(excinfo.value)


# ** test: test_get_dependency
def test_get_dependency(container_context, container_attribute):

    # Call get_dependency with a test attribute
    result = container_context.get_dependency('test_dependency', attributes=[container_attribute])

    # Ensure the dependency was retrieved
    assert result is not None
    assert isinstance(result, MockContainerRepository)


# ** test: test_create_injector
def test_create_injector(container_context, container_attribute):

    # Call create_injector.
    injector = container_context.create_injector(attributes=[container_attribute])

    # Ensure the injector was created.
    assert injector is not None


# ** test: test_import_dependency
def test_import_dependency(container_context, container_attribute):

    # Call import_dependency with a test attribute
    result = container_context.import_dependency(container_attribute, "test")

    # Ensure the dependency was imported
    assert result is not None
    assert result == MockContainerRepository


# ** test: test_import_dependency_raises_failure_error
def test_import_dependency_raises_failure_error(container_context, container_attribute):

    # Call import_dependency with an invalid attribute ID
    with pytest.raises(TiferetError) as excinfo:
        container_context.import_dependency(container_attribute, "does_not_exist")

    # Ensure the error message is correct
    assert excinfo.value.error_code == 'DEPENDENCY_NOT_FOUND'
    assert 'Dependency not found:' in str(excinfo.value)