""""Tiferet Feature Handler Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ...assets import TiferetError
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
# *** tests

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
    assert exc_info.value.kwargs.get('feature_id') == 'non_existent_feature'
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