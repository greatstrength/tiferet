# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ..feature import *
from ...contexts.cache import *
from ...models.feature import *
from ...commands import Command


# *** fixtures

# ** fixture: feature_repo
@pytest.fixture()
def feature_repo():
    """Fixture to provide a mock FeatureRepository."""
    return mock.Mock(spec=FeatureRepository)

# ** fixture: container_service
@pytest.fixture
def container_service():
    """Fixture to provide a mock ContainerService."""
    return mock.Mock(spec=ContainerService)


# ** fixture: feature
@pytest.fixture
def feature():
    """Fixture to provide a mock Feature object."""
    return Feature.new(
        name='Test Feature',
        group_id='test_group',
        feature_key='test_feature',
        id='test_group.test_feature',
        description='A test feature.',
        commands=[
            ValueObject.new(
                FeatureCommand,
                name='Test Command',
                attribute_id='test_command',
                parameters={'param1': 'value1'}
            )
        ],
    )

# ** fixture: initial_cache
@pytest.fixture
def initial_cache(feature):
    """Fixture to provide an initial cache dictionary."""
    return dict(
        cached_feature=feature
    )

# ** fixture: cache_service
@pytest.fixture
def cache_service(initial_cache):
    """Fixture to provide an in-memory CacheService."""
    return CacheContext(initial_cache)


# ** fixture: feature_handler
@pytest.fixture
def feature_handler(container_service, feature_repo, cache_service):
    """Fixture to provide a FeatureHandler instance."""
    return FeatureHandler(
        container_service=container_service,
        feature_repo=feature_repo,
        cache=cache_service
    )

# ** fixture: request_model
@pytest.fixture
def request_model() -> Request:
    return ValueObject.new(
        Request,
        headers={'Content-Type': 'application/json'},
        data={'key': 'value'},
    )

# ** fixture: command
@pytest.fixture
def command():
    """Fixture to provide a mock Command object."""
    return mock.Mock(spec=Command)


# *** tests

# ** test: test_feature_handler_get_feature
def test_feature_handler_get_feature(feature_handler):
    """Test that the feature handler can retrieve a feature from the cache."""

    # Run the test.
    feature = feature_handler.get_feature('cached_feature')

    # Assert that the feature is retrieved correctly.
    assert feature is not None
    assert feature.id == 'test_group.test_feature'
    assert feature.name == 'Test Feature'
    assert feature.group_id == 'test_group'
    assert feature.feature_key == 'test_feature'
    assert len(feature.commands) == 1
    assert feature.commands[0].name == 'Test Command'
    assert feature.commands[0].attribute_id == 'test_command'
    assert feature.commands[0].parameters == {'param1': 'value1'}


# ** test: test_feature_handler_get_feature_not_found
def test_feature_handler_get_feature_not_found(feature_handler, feature_repo):
    """Test that the feature handler raises an error when a feature is not found."""

    # Mock the feature repository to return None.
    feature_repo.get.return_value = None

    # Assert that an error is raised when trying to get a non-existent feature.
    with pytest.raises(TiferetError) as exc_info:
        feature_handler.get_feature('non_existent_feature')

    # Assert that the error message is correct.
    assert exc_info.value.error_code == 'FEATURE_NOT_FOUND'
    assert 'Feature not found: non_existent_feature' in str(exc_info.value)


# ** test: test_feature_handler_get_feature_from_repo
def test_feature_handler_get_feature_from_repo(feature_handler, feature_repo, feature, cache_service):
    """Test that the feature handler retrieves a feature from the repository when not in cache."""

    # Mock the feature repository to return a feature.
    feature_repo.get.return_value = feature

    # Run the test.
    retrieved_feature = feature_handler.get_feature('test_group.test_feature')

    # Assert that the feature is retrieved correctly.
    assert retrieved_feature is not None
    assert retrieved_feature.id == feature.id
    assert retrieved_feature.name == feature.name
    assert retrieved_feature.group_id == feature.group_id
    assert retrieved_feature.feature_key == feature.feature_key 
    assert len(retrieved_feature.commands) == len(feature.commands)
    assert retrieved_feature.commands[0].name == feature.commands[0].name
    assert retrieved_feature.commands[0].attribute_id == feature.commands[0].attribute_id
    assert retrieved_feature.commands[0].parameters == feature.commands[0].parameters

    # Assert that the feature is cached after retrieval.
    assert cache_service.get(feature.id) is not None


# ** test: test_feature_handler_handle_command_request_not_provided
def test_feature_handler_handle_command_request_not_provided(feature_handler, feature):
    """Test that the feature handler raises an error when no request is provided."""

    # Assert that an error is raised when no request is provided.
    with pytest.raises(TiferetError) as exc_info:
        feature_handler.handle_command(feature.commands[0], None)

    # Assert that the error message is correct.
    assert exc_info.value.error_code == 'REQUEST_NOT_PROVIDED'
    assert 'Request is required to execute the feature command.' in str(exc_info.value)


# ** test: test_feature_handler_handle_command_dependency_not_found
def test_feature_handler_handle_command_dependency_not_found(feature_handler, feature, request_model):
    """Test that the feature handler raises an error when a command dependency is not found."""

    # Mock the container service to raise an error when trying to get a dependency.
    feature_handler.container_service.get_dependency.side_effect = Exception(
        f'Dependency not found: {feature.commands[0].attribute_id}'
    )

    # Assert that an error is raised when trying to handle a command with a missing dependency.
    with pytest.raises(TiferetError) as exc_info:
        feature_handler.handle_command(feature.commands[0], request_model)

    # Assert that the error message is correct.
    assert exc_info.value.error_code == 'FEATURE_COMMAND_NOT_FOUND'
    assert 'Feature command not found: test_command' in str(exc_info.value)


# ** test: test_feature_handler_handle_command_success
def test_feature_handler_handle_command_success(feature_handler, feature, request_model, command):
    """Test that the feature handler successfully handles a command."""

    # Mock the container service to return a command.
    feature_handler.container_service.get_dependency.return_value = command

    # Mock the command execution to return a result.
    command.execute.return_value = 'Command executed successfully.'

    # Run the test.
    result = feature_handler.handle_command(
        feature.commands[0],
        request_model
    )

    # Assert that the result is as expected.
    assert request_model.handle_response() == 'Command executed successfully.'