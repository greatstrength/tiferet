# *** imports

# ** core
import json

# ** infra
import pytest

# ** app 
from ...models import Entity, ValueObject
from ..feature import *


# *** classes

# ** class: mock_feature_repository
class MockFeatureRepository(FeatureRepository):

    # * method: init
    def __init__(self, features: List[Feature] = []):
        self.features = features

    # * method: list
    def list(self) -> List[Feature]:
        return self.features
    
    # * method: get
    def get(self, feature_id: str) -> Feature:
        return next((feature for feature in self.features if feature.id == feature_id), None)
    
    # * method: exists
    def exists(self, feature_id: str) -> bool:
        return self.get(feature_id) is not None
    

# ** class: test_service_command
class TestServiceCommand(ServiceCommand):
    '''
    A test service command class.
    '''
    
    def execute(self, param1: str, param2: str, throw_error: bool = False, error_args: List[str] = [], **kwargs) -> Tuple[str, str]:

        # Throw an error if requested.
        if error_args:
            self.verify(throw_error == False, 'MY_FORMATTED_ERROR', 'An error occurred: {}', *error_args)
        else:
            self.verify(throw_error == False, 'MY_ERROR', 'An error occurred.')

        # Return the result.
        return (param1, param2)


# *** fixtures

# ** fixture: test_env_var
@pytest.fixture
def test_env_var():
    '''
    Test environment variable.
    '''

    # Return the test environment variable.
    return os.getenv("TEST_ENV_VAR")


# ** fixture: mock_fixture_repo_raise_error
@pytest.fixture
def mock_feature_repo_raise_error():
    
    class MockFeatureRepository(FeatureRepository):
        
        def list(self) -> List[Feature]:
            raise Exception("Error")
        
        def get(self, feature_id: str) -> Feature:
            raise Exception("Error")
        
        def exists(self, feature_id: str) -> bool:
            raise Exception("Error")
    
    return MockFeatureRepository


# ** fixture: request_context_pass_on_error
@pytest.fixture
def request_context_pass_on_error():
    return 


# ** fixture: request_context_throw_and_pass_on_error
@pytest.fixture
def request_context_throw_and_pass_on_error():
    return RequestContext(
        feature_id="test_group.test_feature_with_throw_and_pass_on_error",
        headers={"Content-Type": "application/json"},
        data={"param2": "value2a"}
    )



# ** fixture: container_context
@pytest.fixture
def container_context():

    from ..container import ContainerRepository, ContainerContext, ContainerAttribute, ContainerDependency

    class MockContainerRepository(ContainerRepository):

        def get_attribute(self, attribute_id, type):
            return ValueObject.new(
                ContainerAttribute,
                id='test_service_command',
                type='feature',
                dependencies=
                [
                    ValueObject.new(
                        ContainerDependency,
                        module_path='tiferet.contexts.tests.test_feature',
                        class_name='TestServiceCommand',
                        flag='test',
                        parameters={},
                    )
                ],
            )

        def list_all(self):
            return [self.get_attribute('test_service_command', 'feature')], {}

    return ContainerContext(
        interface_id="test_interface",
        container_repo=MockContainerRepository(),
        feature_flag="test",
    )


# ** fixture: feature_context
@pytest.fixture
def feature_context(container_context):

    from ...models.feature import ServiceCommand

    return FeatureContext(
        feature_repo=MockFeatureRepository([
            Entity.new(
                Feature,
                name='Test Feature',
                group_id='test_group',
                feature_key='test_feature',
                id='test_group.test_feature',
                description='A test feature.',
                commands=[ValueObject.new(
                    ServiceCommand,
                    name='Test Service Command',
                    attribute_id='test_service_command',
                    params={'param1': 'value1'},
                )]
            ),
            Entity.new(
                Feature,
                name='Test Feature with return to data',
                group_id='test_group',
                feature_key='test_feature_with_return_to_data',
                id='test_group.test_feature_with_return_to_data',
                description='A test feature with return to data.',
                commands=[ValueObject.new(
                    ServiceCommand,
                    name='Test Service Command',
                    attribute_id='test_service_command',
                    params={'param1': 'value1'},
                    return_to_data=True,
                    data_key='test_key'
                )]
            ),
            Entity.new(
                Feature,
                name='Test Feature with throw error',
                group_id='test_group',
                feature_key='test_feature_with_throw_error',
                id='test_group.test_feature_with_throw_error',
                description='A test feature with throw error.',
                commands=[ValueObject.new(
                    ServiceCommand,
                    name='Test Service Command',
                    attribute_id='test_service_command',
                    params={'param1': 'value1'},
                )]
            ),
            Entity.new(
                Feature,
                name='Test Feature with pass on error',
                group_id='test_group',
                feature_key='test_feature_with_pass_on_error',
                id='test_group.test_feature_with_pass_on_error',
                description='A test feature with pass on error.',
                commands=[ValueObject.new(
                    ServiceCommand,
                    name='Test Service Command',
                    attribute_id='test_service_command',
                    params={'param1': 'value1'},
                    pass_on_error=True
                )]
            ),
        ]),
        container_context=container_context
    )


# *** tests

# ** test: test_feature_context_init_error
def test_feature_context_init_error(mock_feature_repo_raise_error):

    # Create new container context.
    with pytest.raises(FeatureLoadingError):
        FeatureContext(
            feature_repo=mock_feature_repo_raise_error(),
            container_context=None
        )


# ** test: test_execute_feature_feature_not_found
def test_execute_feature_feature_not_found(feature_context):

    # Create new request context.
    request = RequestContext(
        feature_id="test_group.non_existent_feature",
        headers={"Content-Type": "application/json"},
        data={}
    )

    # Test executing a feature that does not exist
    with pytest.raises(FeatureNotFoundError):
        feature_context.execute(request)
        

# ** test: test_execute_feature_success
def test_execute_feature_success(feature_context):

    # Create a new request context.
    request_context = RequestContext(
        feature_id="test_group.test_feature",
        headers={"Content-Type": "application/json"},
        data={"param2": "value2"}
    )

    # Test executing a feature that sets result
    feature_context.execute(request_context)

    # Assert the result.
    import json
    assert request_context.result == json.dumps(('value1', 'value2'))


# ** test: test_execute_feature_with_return_to_data
def test_execute_feature_with_return_to_data(feature_context):
    
    # Create a new request context.
    request = RequestContext(
        feature_id="test_group.test_feature_with_return_to_data",
        headers={"Content-Type": "application/json"},
        data={"param2": "value2"}
    )

    # Test executing a feature that returns data.
    feature_context.execute(request)

    # Assert the result.
    assert request.data.get('test_key') == ('value1', 'value2')


# ** test: test_execute_feature_with_throw_error
def test_execute_feature_with_throw_error(feature_context):

    # Create a new request context.
    request = RequestContext(
        feature_id="test_group.test_feature_with_throw_error",
        headers={"Content-Type": "application/json"},
        data={"param2": "value2", "throw_error": "True"}
    )

    # Test where pass_on_error is False.
    with pytest.raises(TiferetError):
        feature_context.execute(request)


# ** test: test_execute_feature_with_pass_on_error
def test_execute_feature_with_pass_on_error(feature_context):

    # Create a new request context.
    request = RequestContext(
        feature_id="test_group.test_feature_with_pass_on_error",
        headers={"Content-Type": "application/json"},
        data={"param2": "value2", "throw_error": "True"}
    )

    # Test where pass_on_error is True.
    feature_context.execute(request)

    # Assert the result.
    assert request.result == None
