"""Tests for Tiferet Feature Commands"""

# *** imports

# ** core
from typing import Dict, Any

# ** infra
import pytest
from unittest import mock

# ** app
from ..feature import (
    GetFeature,
    AddFeature,
    ListFeatures,
    UpdateFeature,
)
from ...models import ModelObject, Feature
from ...contracts import FeatureService
from ...assets import TiferetError
from ...assets.constants import (
    FEATURE_NOT_FOUND_ID,
    COMMAND_PARAMETER_REQUIRED_ID,
    FEATURE_ALREADY_EXISTS_ID,
    FEATURE_NAME_REQUIRED_ID,
    INVALID_FEATURE_ATTRIBUTE_ID,
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
    mock_feature_service.get.return_value = sample_feature

    # Execute the command via the static Command.handle interface.
    result = Command.handle(
        GetFeature,
        dependencies={'feature_service': mock_feature_service},
        id='group.sample_feature',
    )

    # Assert that the feature is returned and the service was called as expected.
    assert result is sample_feature
    mock_feature_service.get.assert_called_once_with('group.sample_feature')

# ** test: get_feature_not_found
def test_get_feature_not_found(mock_feature_service: FeatureService) -> None:
    '''
    Test that GetFeature raises FEATURE_NOT_FOUND when the feature does not exist.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    # Arrange the feature service to return None for the requested feature.
    mock_feature_service.get.return_value = None

    # Execute the command and expect a TiferetError with FEATURE_NOT_FOUND_ID.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            GetFeature,
            dependencies={'feature_service': mock_feature_service},
            id='missing.feature',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == FEATURE_NOT_FOUND_ID
    mock_feature_service.get.assert_called_once_with('missing.feature')

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
    mock_feature_service.get.assert_not_called()


# ** test: add_feature_minimal_success
def test_add_feature_minimal_success(mock_feature_service: FeatureService) -> None:
    '''
    Test successful creation of a feature with minimal required parameters.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    # Arrange the feature service to indicate the feature does not already exist.
    mock_feature_service.exists.return_value = False

    # Execute the command via the static Command.handle interface with minimal parameters.
    result: Feature = Command.handle(
        AddFeature,
        dependencies={'feature_service': mock_feature_service},
        name='New Feature',
        group_id='group',
    )

    # Assert that the result is a Feature with derived key, id, and description.
    assert isinstance(result, Feature)
    assert result.name == 'New Feature'
    assert result.group_id == 'group'
    assert result.feature_key == 'new_feature'
    assert result.id == 'group.new_feature'
    assert result.description == 'New Feature'

    # Verify that existence was checked and the feature was saved.
    mock_feature_service.exists.assert_called_once_with(result.id)
    mock_feature_service.save.assert_called_once_with(result)


# ** test: add_feature_full_parameters
def test_add_feature_full_parameters(mock_feature_service: FeatureService) -> None:
    '''
    Test creation of a feature when all optional parameters are explicitly provided.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    # Arrange the feature service to indicate the feature does not already exist.
    mock_feature_service.exists.return_value = False

    # Explicit parameters.
    feature_name = 'Explicit Feature'
    group_id = 'group'
    feature_key = 'explicit_key'
    feature_id = 'group.explicit_key'
    description = 'Explicit description.'
    commands = []
    log_params = {'foo': 'bar'}

    # Execute the command with all parameters provided.
    result: Feature = Command.handle(
        AddFeature,
        dependencies={'feature_service': mock_feature_service},
        name=feature_name,
        group_id=group_id,
        feature_key=feature_key,
        id=feature_id,
        description=description,
        commands=commands,
        log_params=log_params,
    )

    # Assert that the result reflects the explicitly provided values.
    assert result.name == feature_name
    assert result.group_id == group_id
    assert result.feature_key == feature_key
    assert result.id == feature_id
    assert result.description == description
    assert result.commands == commands
    assert result.log_params == log_params

    # Verify that existence was checked and the feature was saved.
    mock_feature_service.exists.assert_called_once_with(result.id)
    mock_feature_service.save.assert_called_once_with(result)


# ** test: add_feature_missing_required_parameters
@pytest.mark.parametrize(
    'name, group_id',
    [
        (' ', 'group'),
        ('Feature Name', ' '),
    ],
)
def test_add_feature_missing_required_parameters(
        mock_feature_service: FeatureService,
        name: str,
        group_id: str,
    ) -> None:
    '''
    Test that AddFeature fails with COMMAND_PARAMETER_REQUIRED when required parameters are missing or empty.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param name: The feature name to test.
    :type name: str
    :param group_id: The group identifier to test.
    :type group_id: str
    '''

    # Execute the command with invalid parameters and expect a validation error.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            AddFeature,
            dependencies={'feature_service': mock_feature_service},
            name=name,
            group_id=group_id,
        )

    error: TiferetError = excinfo.value
    assert error.error_code == COMMAND_PARAMETER_REQUIRED_ID

    # The feature service should not be called when validation fails.
    mock_feature_service.exists.assert_not_called()
    mock_feature_service.save.assert_not_called()


# ** test: add_feature_duplicate_id
def test_add_feature_duplicate_id(mock_feature_service: FeatureService) -> None:
    '''
    Test that AddFeature raises ERROR_ALREADY_EXISTS_ID when the feature id already exists.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    # Arrange the feature service to indicate the feature already exists.
    mock_feature_service.exists.return_value = True

    # Execute the command and expect a TiferetError with ERROR_ALREADY_EXISTS_ID.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            AddFeature,
            dependencies={'feature_service': mock_feature_service},
            name='Duplicate Feature',
            group_id='group',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == FEATURE_ALREADY_EXISTS_ID

    # Verify that existence was checked and the feature was not saved.
    mock_feature_service.exists.assert_called_once()
    mock_feature_service.save.assert_not_called()

# ** test: list_features_all
def test_list_features_all(mock_feature_service: FeatureService, sample_feature: Feature) -> None:
    '''ß
    Test listing all features when no group_id filter is provided.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param sample_feature: The sample feature instance.
    :type sample_feature: Feature
    '''

    # Arrange the feature service to return all features.
    mock_feature_service.list.return_value = [sample_feature]

    # Execute the command via the static Command.handle interface.
    result = Command.handle(
        ListFeatures,
        dependencies={'feature_service': mock_feature_service},
        group_id=None,
    )

    # Assert that all features are returned and the service was called as expected.
    assert result == [sample_feature]
    mock_feature_service.list.assert_called_once_with(group_id=None)

# ** test: list_features_by_group_id
def test_list_features_by_group_id(mock_feature_service: FeatureService, sample_feature: Feature) -> None:
    '''
    Test listing features filtered by group_id.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param sample_feature: The sample feature instance.
    :type sample_feature: Feature
    '''

    # Arrange the feature service to return features for the specified group.
    group_id = 'group'
    mock_feature_service.list.return_value = [sample_feature]

    # Execute the command via the static Command.handle interface.
    result = Command.handle(
        ListFeatures,
        dependencies={'feature_service': mock_feature_service},
        group_id=group_id,
    )

    # Assert that the filtered features are returned and the service was called as expected.
    assert result == [sample_feature]
    mock_feature_service.list.assert_called_once_with(group_id=group_id)

# ** test: list_features_empty_result
def test_list_features_empty_result(mock_feature_service: FeatureService) -> None:
    '''
    Test listing features when the service returns an empty list.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    # Arrange the feature service to return an empty list.
    mock_feature_service.list.return_value = []

    # Execute the command via the static Command.handle interface.
    result = Command.handle(
        ListFeatures,
        dependencies={'feature_service': mock_feature_service},
        group_id=None,
    )

    # Assert that an empty list is returned and the service was called as expected.
    assert result == []
    mock_feature_service.list.assert_called_once_with(group_id=None)

# ** test: update_feature_name_success
def test_update_feature_name_success(
        mock_feature_service: FeatureService,
        sample_feature: Feature,
    ) -> None:
    '''
    Test successful update of a feature name via UpdateFeature.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param sample_feature: The sample feature instance.
    :type sample_feature: Feature
    '''

    # Arrange the feature service to return the sample feature.
    mock_feature_service.get.return_value = sample_feature

    # Execute the command via the static Command.handle interface.
    result: Feature = Command.handle(
        UpdateFeature,
        dependencies={'feature_service': mock_feature_service},
        id=sample_feature.id,
        attribute='name',
        value='Updated Feature Name',
    )

    # Assert that the feature name is updated and persisted.
    assert result is sample_feature
    assert result.name == 'Updated Feature Name'
    mock_feature_service.get.assert_called_once_with(sample_feature.id)
    mock_feature_service.save.assert_called_once_with(sample_feature)

# ** test: update_feature_description_success
def test_update_feature_description_success(
        mock_feature_service: FeatureService,
        sample_feature: Feature,
    ) -> None:
    '''
    Test successful update of a feature description via UpdateFeature.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param sample_feature: The sample feature instance.
    :type sample_feature: Feature
    '''

    # Arrange the feature service to return the sample feature.
    mock_feature_service.get.return_value = sample_feature

    # Execute the command to update the description.
    result: Feature = Command.handle(
        UpdateFeature,
        dependencies={'feature_service': mock_feature_service},
        id=sample_feature.id,
        attribute='description',
        value='Updated description.',
    )

    # Assert that the feature description is updated and persisted.
    assert result is sample_feature
    assert result.description == 'Updated description.'
    mock_feature_service.get.assert_called_once_with(sample_feature.id)
    mock_feature_service.save.assert_called_once_with(sample_feature)

# ** test: update_feature_clear_description
def test_update_feature_clear_description(
        mock_feature_service: FeatureService,
        sample_feature: Feature,
    ) -> None:
    '''
    Test clearing a feature description via UpdateFeature.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param sample_feature: The sample feature instance.
    :type sample_feature: Feature
    '''

    # Arrange the feature service to return the sample feature.
    mock_feature_service.get.return_value = sample_feature

    # Execute the command to clear the description.
    result: Feature = Command.handle(
        UpdateFeature,
        dependencies={'feature_service': mock_feature_service},
        id=sample_feature.id,
        attribute='description',
        value=None,
    )

    # Assert that the feature description is cleared and persisted.
    assert result is sample_feature
    assert result.description is None
    mock_feature_service.get.assert_called_once_with(sample_feature.id)
    mock_feature_service.save.assert_called_once_with(sample_feature)

# ** test: update_feature_missing_required_parameters
@pytest.mark.parametrize(
    'id, attribute',
    [
        (' ', 'name'),
        ('group.sample_feature', ' '),
    ],
)
def test_update_feature_missing_required_parameters(
        mock_feature_service: FeatureService,
        id: str,
        attribute: str,
    ) -> None:
    '''
    Test that UpdateFeature fails with COMMAND_PARAMETER_REQUIRED when
    required parameters are missing or empty.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param id: The feature identifier to test.
    :type id: str
    :param attribute: The attribute name to test.
    :type attribute: str
    '''

    # Execute the command with invalid parameters and expect a validation error.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeature,
            dependencies={'feature_service': mock_feature_service},
            id=id,
            attribute=attribute,
            value='ignored',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == COMMAND_PARAMETER_REQUIRED_ID

    # The feature service should not be called when validation fails.
    mock_feature_service.get.assert_not_called()
    mock_feature_service.save.assert_not_called()

# ** test: update_feature_invalid_attribute
def test_update_feature_invalid_attribute(
        mock_feature_service: FeatureService,
    ) -> None:
    '''
    Test that UpdateFeature fails when an unsupported attribute is provided.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    # Execute the command with an invalid attribute and expect an error.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeature,
            dependencies={'feature_service': mock_feature_service},
            id='group.sample_feature',
            attribute='invalid',
            value='ignored',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == INVALID_FEATURE_ATTRIBUTE_ID

    # The feature service should not be called when attribute validation fails.
    mock_feature_service.get.assert_not_called()
    mock_feature_service.save.assert_not_called()

# ** test: update_feature_missing_name_value
def test_update_feature_missing_name_value(
        mock_feature_service: FeatureService,
    ) -> None:
    '''
    Test that UpdateFeature fails with FEATURE_NAME_REQUIRED when updating
    the name with an empty value.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    # Execute the command with an empty name value and expect an error.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeature,
            dependencies={'feature_service': mock_feature_service},
            id='group.sample_feature',
            attribute='name',
            value=' ',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == FEATURE_NAME_REQUIRED_ID

    # The feature service should not be called when name validation fails.
    mock_feature_service.get.assert_not_called()
    mock_feature_service.save.assert_not_called()

# ** test: update_feature_not_found
def test_update_feature_not_found(mock_feature_service: FeatureService) -> None:
    '''
    Test that UpdateFeature raises FEATURE_NOT_FOUND when the feature does
    not exist.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    # Arrange the feature service to return None for the requested feature.
    mock_feature_service.get.return_value = None

    # Execute the command and expect a TiferetError with FEATURE_NOT_FOUND_ID.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeature,
            dependencies={'feature_service': mock_feature_service},
            id='missing.feature',
            attribute='name',
            value='Updated Feature Name',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == FEATURE_NOT_FOUND_ID
    mock_feature_service.get.assert_called_once_with('missing.feature')
    mock_feature_service.save.assert_not_called()
