"""Tests for Tiferet Feature Commands"""

# *** imports

# ** core
from typing import Dict, Any, List

# ** infra
import pytest
from unittest import mock

# ** app
from ..feature import GetFeature, AddFeature
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

    # Test with empty id.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            GetFeature,
            dependencies={'feature_service': mock_feature_service},
            id=' ',
        )

    # Check the error.
    error: TiferetError = excinfo.value
    assert error.error_code == COMMAND_PARAMETER_REQUIRED_ID
    # Service should not be called when validation fails.
    mock_feature_service.get_feature.assert_not_called()

# ** test: add_feature_success
def test_add_feature_success(mock_feature_service: FeatureService):
    '''
    Test that AddFeature creates and saves a new feature when the id does not
    already exist.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    # The feature service should report that the feature does not exist.
    mock_feature_service.exists.return_value = False

    result = Command.handle(
        AddFeature,
        dependencies={'feature_service': mock_feature_service},
        name='Test Feature',
        group_id='test_group',
        # rely on Feature.new to derive feature_key and id
        description='A test feature.',
        commands=[],
        log_params={'foo': 'bar'},
    )

    assert isinstance(result, Feature)
    assert result.id == 'test_group.test_feature'
    assert result.name == 'Test Feature'
    assert result.group_id == 'test_group'
    assert result.feature_key == 'test_feature'
    assert result.description == 'A test feature.'
    assert result.log_params == {'foo': 'bar'}

    mock_feature_service.exists.assert_called_once_with('test_group.test_feature')
    mock_feature_service.save.assert_called_once_with(result)

# ** test: add_feature_missing_name
def test_add_feature_missing_name(mock_feature_service: FeatureService):
    '''
    Test that AddFeature validates the required name parameter.
    '''

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            AddFeature,
            dependencies={'feature_service': mock_feature_service},
            name=' ',
            group_id='test_group',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == COMMAND_PARAMETER_REQUIRED_ID
    mock_feature_service.exists.assert_not_called()
    mock_feature_service.save.assert_not_called()

# ** test: add_feature_missing_group_id
def test_add_feature_missing_group_id(mock_feature_service: FeatureService):
    '''
    Test that AddFeature validates the required group_id parameter.
    '''

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            AddFeature,
            dependencies={'feature_service': mock_feature_service},
            name='Test Feature',
            group_id=' ',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == COMMAND_PARAMETER_REQUIRED_ID
    mock_feature_service.exists.assert_not_called()
    mock_feature_service.save.assert_not_called()

# ** test: add_feature_already_exists
def test_add_feature_already_exists(mock_feature_service: FeatureService):
    '''
    Test that AddFeature raises when attempting to create a feature that
    already exists.
    '''

    # Service reports that the computed id already exists.
    mock_feature_service.exists.return_value = True

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            AddFeature,
            dependencies={'feature_service': mock_feature_service},
            name='Test Feature',
            group_id='test_group',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == 'FEATURE_ALREADY_EXISTS'
    assert error.kwargs.get('id') == 'test_group.test_feature'
    mock_feature_service.exists.assert_called_once()
    mock_feature_service.save.assert_not_called()
