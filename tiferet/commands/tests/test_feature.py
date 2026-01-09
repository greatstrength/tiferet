"""Tests for Tiferet Feature Commands"""

# *** imports

# ** core
from typing import Dict, Any

# ** infra
import pytest
from unittest import mock

# ** app
from ..feature import GetFeature
from ...models import ModelObject, Feature
from ...contracts import FeatureService
from ...assets import TiferetError
from ...assets.constants import (
    FEATURE_NOT_FOUND_ID,
    COMMAND_PARAMETER_REQUIRED_ID,
)
from ...commands import Command


# *** fixtures

# ** fixture: mock_feature_service
@pytest.fixture
def mock_feature_service() -> FeatureService:
    '''
    A fixture for a mock feature service.
    '''

    return mock.Mock(spec=FeatureService)


# ** fixture: sample_feature
@pytest.fixture
def sample_feature() -> Feature:
    '''
    A sample Feature instance for testing.
    '''

    return ModelObject.new(
        Feature,
        id='group.sample_feature',
        name='Sample Feature',
        group_id='group',
        feature_key='sample_feature',
        description='A sample feature for testing.',
    )

# *** tests

# ** test: get_feature_success
def test_get_feature_success(mock_feature_service: FeatureService, sample_feature: Feature) -> None:
    '''
    Test successful retrieval of a feature via GetFeature.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param sample_feature: The sample feature instance.
    :type sample_feature: Feature
    '''

    # Arrange the feature service to return the sample feature.
    mock_feature_service.get_feature.return_value = sample_feature

    # Execute the command via the static Command.handle interface.
    result = Command.handle(
        GetFeature,
        dependencies={'feature_service': mock_feature_service},
        id='group.sample_feature',
    )

    # Assert that the feature is returned and the service was called as expected.
    assert result is sample_feature
    mock_feature_service.get_feature.assert_called_once_with('group.sample_feature')

# ** test: get_feature_not_found
def test_get_feature_not_found(mock_feature_service: FeatureService) -> None:
    '''
    Test that GetFeature raises FEATURE_NOT_FOUND when the feature does not exist.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    # Arrange the feature service to return None for the requested feature.
    mock_feature_service.get_feature.return_value = None

    # Execute the command and expect a TiferetError with FEATURE_NOT_FOUND_ID.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            GetFeature,
            dependencies={'feature_service': mock_feature_service},
            id='missing.feature',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == FEATURE_NOT_FOUND_ID
    mock_feature_service.get_feature.assert_called_once_with('missing.feature')

# ** test: get_feature_missing_id
def test_get_feature_missing_id(mock_feature_service: FeatureService) -> None:
    '''
    Test that GetFeature fails with COMMAND_PARAMETER_REQUIRED when id is missing or empty.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    # Execute the command with an invalid id and expect a validation error.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            GetFeature,
            dependencies={'feature_service': mock_feature_service},
            id=' ',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == COMMAND_PARAMETER_REQUIRED_ID
    # The feature service should not be called when validation fails.
    mock_feature_service.get_feature.assert_not_called()
