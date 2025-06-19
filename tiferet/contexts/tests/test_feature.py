# *** imports

# ** core
import json

# ** infra
import pytest
from unittest import mock

# ** app 
from ..feature import *
from ...configs import TiferetError


# *** fixtures

# ** fixture: request_context
@pytest.fixture
def request_context():
    """
    Fixture to provide a request context for testing.
    """
    return RequestContext(
        feature_id="test_group.test_feature",
        headers={"Content-Type": "application/json"},
        data=dict(
            test_key="test_value"
        )
    )

# ** fixture: feature
@pytest.fixture
def feature():
    """
    Test feature object.
    """
    return Feature.new(
        id="test_group.test_feature",
        name="Test Feature",
        group_id="test_group",
        feature_key="test_feature",
        description="A test feature for unit testing.",
        commands=[
            ValueObject.new(
                FeatureCommand,
                attribute_id="test_feature_command",
                name="Test Feature Command",
                parameters=dict(
                    param1="value1",
                    param2="value2"
                ),
            )
        ]
    )


# ** fixture: feature_handler
@pytest.fixture
def feature_handler(feature, request_context):
    """
    Fixture to provide a mock feature handler.
    """

    # Set the result for the request context.
    request_context.result = json.dumps(['value1', 'value2'])

    # Mock the feature handler to return the test feature.
    handler = mock.Mock(spec=FeatureHandler)
    handler.get_feature.return_value = feature
    handler.handle_command.return_value = request_context
    return handler


# ** fixture: feature_context
@pytest.fixture
def feature_context(feature_handler):
    """
    Fixture to provide a FeatureContext instance for testing.
    """
    return FeatureContext(
        feature_handler=feature_handler
    )

# ** fixture: feature_handler
@pytest.fixture
def feature_repo(feature):
    """
    Fixture to provide a mock feature repository.
    """
    
    # Mock the repository to return the test feature.
    repo = mock.Mock(spec=FeatureRepository)
    repo.get.return_value = feature
    return repo


# ** fixture: container_context
@pytest.fixture
def container_context():
    """
    Fixture to provide a mock container context.
    """
    return mock.Mock(spec=ContainerContext)


# *** tests 

# ** test: test_init_feature_context
def test_init_feature_context(feature_repo, container_context):
    """
    Test initializing the FeatureContext with a feature repository and container context.
    """
    feature_context = FeatureContext(
        feature_repo=feature_repo,
        container_context=container_context
    )
    
    # Assert the feature handler is initialized correctly.
    assert isinstance(feature_context.feature_handler, FeatureHandler)
    assert feature_context.feature_handler.feature_repo == feature_repo
    assert feature_context.feature_handler.container_service == container_context


# ** test: test_init_feature_context_without_repo_or_container
def test_init_feature_context_without_repo_or_container():
    """
    Test initializing the FeatureContext without a feature repository or container context.
    """
    with pytest.raises(TiferetError) as exc_info:
        FeatureContext()
    
    # Assert the exception is raised.
    assert exc_info.value.error_code == 'FEATURE_CONTEXT_LOADING_FAILED'
    assert 'A feature repository and container context are required to initialize the feature context.' in str(exc_info.value)

# ** test: test_execute_feature_success
def test_execute_feature_success(feature_context, request_context):

    # Test executing a feature that sets result
    feature_context.execute(request_context)

    # Assert the result.
    assert request_context.result == json.dumps(['value1', 'value2'])