"""Tests for Tiferet Feature Commands"""

# *** imports

# ** core
from typing import Dict, Any, List

# ** infra
import pytest
from unittest import mock

# ** app
from ..feature import GetFeature
from ...models import Feature, FeatureCommand, ModelObject
from ...contracts import FeatureService
from ...assets import TiferetError
from ...assets.constants import (
    COMMAND_PARAMETER_REQUIRED_ID,
    FEATURE_NOT_FOUND_ID,
)
from ...commands import Command


# *** fixtures

# ** fixture: mock_feature_service
@pytest.fixture
def mock_feature_service() -> FeatureService:
    '''
    A fixture for a mock feature service.

    :return: A mock FeatureService instance.
    :rtype: FeatureService
    '''

    return mock.Mock(spec=FeatureService)


# ** fixture: sample_feature
@pytest.fixture
def sample_feature() -> Feature:
    '''
    A sample Feature model for testing.

    :return: A Feature instance.
    :rtype: Feature
    '''

    command = ModelObject.new(
        FeatureCommand,
        name='Test Command',
        attribute_id='test_command',
        parameters={'param': 'value'},
    )

    return ModelObject.new(
        Feature,
        id='test_group.test_feature',
        name='Test Feature',
        description='A test feature.',
        group_id='test_group',
        feature_key='test_feature',
        commands=[command],
    )


# *** tests

# ** test: get_feature_success
def test_get_feature_success(mock_feature_service: FeatureService, sample_feature: Feature):
    '''
    Test that GetFeature returns the feature when it exists.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param sample_feature: The sample feature.
    :type sample_feature: Feature
    '''

    mock_feature_service.get_feature.return_value = sample_feature

    result = Command.handle(
        GetFeature,
        dependencies={'feature_service': mock_feature_service},
        id='test_group.test_feature',
    )

    assert result is sample_feature
    mock_feature_service.get_feature.assert_called_once_with('test_group.test_feature')


# ** test: get_feature_not_found
def test_get_feature_not_found(mock_feature_service: FeatureService):
    '''
    Test that GetFeature raises FEATURE_NOT_FOUND when the feature does not exist.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    mock_feature_service.get_feature.return_value = None

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            GetFeature,
            dependencies={'feature_service': mock_feature_service},
            id='missing.feature',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == FEATURE_NOT_FOUND_ID
    assert error.kwargs.get('feature_id') == 'missing.feature'
    mock_feature_service.get_feature.assert_called_once_with('missing.feature')


# ** test: get_feature_missing_id
def test_get_feature_missing_id(mock_feature_service: FeatureService):
    '''
    Test that GetFeature fails with COMMAND_PARAMETER_REQUIRED when id is missing or empty.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            GetFeature,
            dependencies={'feature_service': mock_feature_service},
            id=' ',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == COMMAND_PARAMETER_REQUIRED_ID
    # Service should not be called when validation fails.
    mock_feature_service.get_feature.assert_not_called()
