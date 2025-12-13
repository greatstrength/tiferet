""""Tiferet Feature Handler Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ...configs import TiferetError
from ...contexts import RequestContext
from ...models import (
    ModelObject,
    Feature,
    FeatureCommand,
)
from ...contracts import FeatureRepository
from ..feature import FeatureHandler

# *** fixtures

# ** fixture: feature_repo
@pytest.fixture()
def feature_repo():
    """Fixture to provide a mock FeatureRepository."""
    return mock.Mock(spec=FeatureRepository)

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
            ModelObject.new(
                FeatureCommand,
                name='Test Command',
                attribute_id='test_command',
                parameters={'param1': 'value1'}
            )
        ],
    )

# ** fixture: feature_handler
@pytest.fixture
def feature_handler(feature_repo):
    """Fixture to provide a FeatureHandler instance."""

    return FeatureHandler(
        feature_repo=feature_repo,
    )

# ** fixture: request_with_data
@pytest.fixture
def request_with_data():
    """Fixture to provide a request object with data."""

    return RequestContext(
        data=dict(
            const_value='test_value',
        )
    )

# *** tests

# ** test: test_feature_handler_parse_parameter
def test_feature_handler_parse_parameter(feature_handler, request_with_data):
    """Test that the feature handler can parse a parameter from the request data."""

    # Run the test.
    parsed_value = feature_handler.parse_parameter('$r.const_value', request_with_data)

    # Assert that the parsed value is correct.
    assert parsed_value == 'test_value'

# ** test: test_feature_handler_parse_parameter_invalid_request
def test_feature_handler_parse_parameter_invalid_request(feature_handler):
    """Test that the feature handler raises an error when the request is None."""

    # Assert that an error is raised when trying to parse a parameter with a None request.
    with pytest.raises(TiferetError) as exc_info:
        feature_handler.parse_parameter('$r.const_value')

    # Assert that the error message is correct.
    assert exc_info.value.error_code == 'REQUEST_NOT_FOUND'
    assert 'Request data is not available for parameter parsing.' in str(exc_info.value)

# ** test: test_feature_handler_parse_parameter_not_found
def test_feature_handler_parse_parameter_not_found(feature_handler, request_with_data):
    """Test that the feature handler raises an error when a parameter is not found in the request data."""

    # Assert that an error is raised when trying to parse a non-existent parameter.
    with pytest.raises(TiferetError) as exc_info:
        feature_handler.parse_parameter('$r.non_existent_param', request_with_data)

    # Assert that the error message is correct.
    assert exc_info.value.error_code == 'PARAMETER_NOT_FOUND'
    assert 'Parameter $r.non_existent_param not found in request data.' in str(exc_info.value)

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
def test_feature_handler_get_feature_from_repo(feature_handler, feature_repo, feature):
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
