# *** imports

# ** infra
import pytest

# ** app 
from ..feature import *
from ...models import *
from ...configs.tests import *
from ...commands.tests.test_settings import TestServiceCommand


# *** fixtures

# ** fixture: container_repo
@pytest.fixture
def container_repo():

    from ...proxies.tests.container_mock import MockContainerProxy

    return MockContainerProxy

# ** fixture: feature_repo
@pytest.fixture
def feature_repo():

    from ...proxies.tests.feature_mock import MockFeatureProxy

    return MockFeatureProxy


# ** fixture: feature_repo_with_errors
@pytest.fixture
def feature_repo_with_errors():
    
    # Mock error feature proxy.
    class MockErrorFeatureProxy(FeatureRepository):

        def list(self) -> List[Feature]:
            raise Exception("Failed to list features")

        def get(self, feature_id: str) -> Feature:
            raise Exception("Failed to get feature")

        def exists(self, feature_id: str) -> bool:
            raise Exception("Checking feature existence failed")
        
    # Return the mock error feature proxy.
    return MockErrorFeatureProxy()


# ** fixture: features
@pytest.fixture
def features():
    return [
        ModelObject.new(
            Feature,
            **TEST_FEATURE
        ),
        ModelObject.new(
            Feature,
            **TEST_FEATURE_WITH_RETURN_TO_DATA,
        ),
        Entity.new(
            Feature,
            **TEST_FEATURE_WITH_THROW_ERROR,
        ),
        Entity.new(
            Feature,
            **TEST_FEATURE_WITH_PASS_ON_ERROR,
        ),
    ]


# ** fixture: attributes
@pytest.fixture
def attributes():
    return [
        ModelObject.new(
            ContainerAttribute,
            **TEST_SERVICE_COMMAND_ATTRIBUTE
        )
    ]


# ** fixture: request_context
@pytest.fixture
def request_context():
    return RequestContext(
        **TEST_REQUEST_CONTEXT,
    )


# ** fixture: request_context_feature_not_found
@pytest.fixture
def request_context_feature_not_found():
    return RequestContext(
        **TEST_REQUEST_FEATURE_NOT_FOUND,
    )


# ** fixture: request_context_with_return_to_data
@pytest.fixture
def request_context_with_return_to_data():
    return RequestContext(
        **TEST_REQUEST_WITH_RETURN_TO_DATA,
    )


# ** fixture: request_context_throw_error
@pytest.fixture
def request_context_throw_error():
    return RequestContext(
        **TEST_REQUEST_WITH_THROW_ERROR
    )


# ** fixture: request_context_with_pass_on_error
@pytest.fixture
def request_context_with_pass_on_error():
    return RequestContext(
        **TEST_REQUEST_WITH_PASS_ON_ERROR
    )


# ** fixture: request_context_throw_and_pass_on_error
@pytest.fixture
def request_context_throw_and_pass_on_error():
    return RequestContext(
        **TEST_REQUEST_THROW_AND_PASS_ON_ERROR
    )


# ** fixture: container_context
@pytest.fixture
def container_context(container_repo, attributes):

    return ContainerContext(
        interface_id="test_interface",
        container_repo=container_repo(
            attributes=attributes,
        ),
        feature_flag="test",
        data_flag="test",
    )


# ** fixture: feature_context
@pytest.fixture
def feature_context(container_context, feature_repo, features):

    return FeatureContext(
        feature_repo=feature_repo(features=features),
        container_context=container_context
    )


# ** fixture: command
@pytest.fixture
def command():
    
    return TestServiceCommand()


# *** tests

# ** test: test_feature_context_init_error
def test_feature_context_init_error(feature_repo_with_errors):

    # Create new container context.
    with pytest.raises(TiferetError) as excinfo:
        FeatureContext(
            feature_repo=feature_repo_with_errors,
            container_context=None
        )

    # Assert the error code and content.
    assert excinfo.value.error_code == 'FEATURE_LOADING_FAILED'
    assert 'Failed loading features:' in str(excinfo.value)
    

# ** test: test_execute_feature_feature_not_found
def test_execute_feature_feature_not_found(feature_context, request_context_feature_not_found):

    # Test executing a feature that does not exist
    with pytest.raises(TiferetError) as excinfo:
        feature_context.execute(request_context_feature_not_found)

    # Assert the error code and content.
    assert excinfo.value.error_code == 'FEATURE_NOT_FOUND'
    assert 'Feature not found:' in str(excinfo.value)
        

# ** test: test_execute_feature_success
def test_execute_feature_success(feature_context, request_context):

    # Test executing a feature that sets result
    feature_context.execute(request_context)

    # Assert the result.
    import json
    assert request_context.result == json.dumps(('value1', 'value2'))


# ** test: test_execute_feature_with_return_to_data
def test_execute_feature_with_return_to_data(feature_context, command, request_context_with_return_to_data):
    

    # Test executing a feature that returns data.
    feature_context.handle_command(
        command, 
        request_context_with_return_to_data, 
        params=dict(param1='value1'),
        return_to_data=True,
        data_key='test_key'
    )

    # Assert the result.
    assert request_context_with_return_to_data.data.get('test_key') == ('value1', 'value2')


# ** test: test_execute_feature_with_throw_error
def test_execute_feature_with_throw_error(feature_context, command, request_context_throw_error):

    # Test where pass_on_error is False.
    with pytest.raises(TiferetError):
        feature_context.handle_command(
            command,
            request_context_throw_error,
            params=dict(param1='value1')
        )


# ** test: test_execute_feature_with_pass_on_error
def test_execute_feature_with_pass_on_error(feature_context, command, request_context_with_pass_on_error):

    # Test where pass_on_error is True.
    feature_context.handle_command(
        command,
        request_context_with_pass_on_error,
        params=dict(param1='value1'),
        pass_on_error=True
    )

    # Assert the result.
    assert request_context_with_pass_on_error.result == None
