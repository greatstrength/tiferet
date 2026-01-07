"""Tests for Tiferet Feature Commands"""

# *** imports

# ** core
from typing import Dict, Any, List

# ** infra
import pytest
from unittest import mock

# ** app
from ..feature import (
    GetFeature,
    AddFeature,
    ListFeatures,
    UpdateFeature,
    AddFeatureCommand,
    UpdateFeatureCommand,
)
from ...models import (
    Feature,
    FeatureCommand,
    ModelObject,
)
from ...contracts import FeatureService
from ...assets import TiferetError
from ...assets.constants import (
    COMMAND_PARAMETER_REQUIRED_ID,
    FEATURE_NOT_FOUND_ID,
    FEATURE_NAME_REQUIRED_ID,
    INVALID_FEATURE_ATTRIBUTE_ID,
    FEATURE_COMMAND_NOT_FOUND_ID,
    INVALID_FEATURE_COMMAND_ATTRIBUTE_ID,
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

# ** test: list_features_success_all
def test_list_features_success_all(mock_feature_service: FeatureService):
    '''
    Test that ListFeatures returns all features when no group_id is
    specified.
    '''

    feature1 = ModelObject.new(
        Feature,
        id='group1.feature1',
        name='Feature One',
        group_id='group1',
        feature_key='feature1',
        description='First feature',
        commands=[],
    )
    feature2 = ModelObject.new(
        Feature,
        id='group2.feature2',
        name='Feature Two',
        group_id='group2',
        feature_key='feature2',
        description='Second feature',
        commands=[],
    )

    mock_feature_service.list.return_value = [feature1, feature2]

    result = Command.handle(
        ListFeatures,
        dependencies={'feature_service': mock_feature_service},
    )

    assert result == [feature1, feature2]
    mock_feature_service.list.assert_called_once_with(None)

# ** test: list_features_by_group
def test_list_features_by_group(mock_feature_service: FeatureService):
    '''
    Test that ListFeatures filters features by the provided group id.
    '''

    feature = ModelObject.new(
        Feature,
        id='group1.feature1',
        name='Feature One',
        group_id='group1',
        feature_key='feature1',
        description='First feature',
        commands=[],
    )

    mock_feature_service.list.return_value = [feature]

    result = Command.handle(
        ListFeatures,
        dependencies={'feature_service': mock_feature_service},
        group_id='group1',
    )

    assert result == [feature]
    mock_feature_service.list.assert_called_once_with('group1')


# ** test: list_features_empty
def test_list_features_empty(mock_feature_service: FeatureService):
    '''
    Test that ListFeatures returns an empty list when no features exist.
    '''

    mock_feature_service.list.return_value = []

    result = Command.handle(
        ListFeatures,
        dependencies={'feature_service': mock_feature_service},
    )

    assert result == []
    mock_feature_service.list.assert_called_once_with(None)

# ** test: list_features_group_not_found
def test_list_features_group_not_found(mock_feature_service: FeatureService):
    '''
    Test that ListFeatures returns an empty list when the group id does not
    exist.
    '''

    mock_feature_service.list.return_value = []

    result = Command.handle(
        ListFeatures,
        dependencies={'feature_service': mock_feature_service},
        group_id='missing_group',
    )

    assert result == []
    mock_feature_service.list.assert_called_once_with('missing_group')

# ** test: update_feature_name_success
def test_update_feature_name_success(mock_feature_service: FeatureService, sample_feature: Feature):
    '''
    Test that UpdateFeature successfully updates the feature name.
    '''

    mock_feature_service.get_feature.return_value = sample_feature

    result = Command.handle(
        UpdateFeature,
        dependencies={'feature_service': mock_feature_service},
        id='test_group.test_feature',
        attribute='name',
        value='Updated Name',
    )

    assert result is sample_feature
    assert sample_feature.name == 'Updated Name'
    mock_feature_service.get_feature.assert_called_once_with('test_group.test_feature')
    mock_feature_service.save.assert_called_once_with(sample_feature)

# ** test: update_feature_description_success
def test_update_feature_description_success(mock_feature_service: FeatureService, sample_feature: Feature):
    '''
    Test that UpdateFeature successfully updates the feature description.
    '''

    mock_feature_service.get_feature.return_value = sample_feature

    result = Command.handle(
        UpdateFeature,
        dependencies={'feature_service': mock_feature_service},
        id='test_group.test_feature',
        attribute='description',
        value='Updated description',
    )

    assert result is sample_feature
    assert sample_feature.description == 'Updated description'
    mock_feature_service.get_feature.assert_called_once_with('test_group.test_feature')
    mock_feature_service.save.assert_called_once_with(sample_feature)

# ** test: update_feature_invalid_attribute
def test_update_feature_invalid_attribute(mock_feature_service: FeatureService, sample_feature: Feature):
    '''
    Test that UpdateFeature raises INVALID_FEATURE_ATTRIBUTE for unsupported attributes.
    '''

    mock_feature_service.get_feature.return_value = sample_feature

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeature,
            dependencies={'feature_service': mock_feature_service},
            id='test_group.test_feature',
            attribute='invalid',
            value='value',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == INVALID_FEATURE_ATTRIBUTE_ID
    assert error.kwargs.get('attribute') == 'invalid'
    mock_feature_service.get_feature.assert_called_once_with('test_group.test_feature')
    mock_feature_service.save.assert_not_called()


# ** test: update_feature_name_required
def test_update_feature_name_required(mock_feature_service: FeatureService, sample_feature: Feature):
    '''
    Test that UpdateFeature enforces FEATURE_NAME_REQUIRED when attribute is name and value is None.
    '''

    mock_feature_service.get_feature.return_value = sample_feature

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeature,
            dependencies={'feature_service': mock_feature_service},
            id='test_group.test_feature',
            attribute='name',
            value=None,
        )

    error: TiferetError = excinfo.value
    assert error.error_code == FEATURE_NAME_REQUIRED_ID
    mock_feature_service.get_feature.assert_called_once_with('test_group.test_feature')
    mock_feature_service.save.assert_not_called()


# ** test: update_feature_attribute_required
def test_update_feature_attribute_required(mock_feature_service: FeatureService, sample_feature: Feature):
    '''
    Test that UpdateFeature requires the attribute parameter.
    '''

    mock_feature_service.get_feature.return_value = sample_feature

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeature,
            dependencies={'feature_service': mock_feature_service},
            id='test_group.test_feature',
            attribute=' ',
            value='Updated Name',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == COMMAND_PARAMETER_REQUIRED_ID
    mock_feature_service.get_feature.assert_not_called()
    mock_feature_service.save.assert_not_called()


# ** test: update_feature_not_found
def test_update_feature_not_found(mock_feature_service: FeatureService):
    '''
    Test that UpdateFeature raises FEATURE_NOT_FOUND when the feature does not exist.
    '''

    mock_feature_service.get_feature.return_value = None

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeature,
            dependencies={'feature_service': mock_feature_service},
            id='missing.feature',
            attribute='name',
            value='Updated Name',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == FEATURE_NOT_FOUND_ID
    assert error.kwargs.get('feature_id') == 'missing.feature'
    mock_feature_service.get_feature.assert_called_once_with('missing.feature')
    mock_feature_service.save.assert_not_called()

# ** test: add_feature_command_success
def test_add_feature_command_success(mock_feature_service: FeatureService):
    '''
    Test that AddFeatureCommand successfully adds a command to an existing feature.
    '''

    feature = ModelObject.new(
        Feature,
        id='test_group.test_feature',
        name='Test Feature',
        group_id='test_group',
        feature_key='test_feature',
        commands=[],
    )
    mock_feature_service.get.return_value = feature

    result = Command.handle(
        AddFeatureCommand,
        dependencies={'feature_service': mock_feature_service},
        id='test_group.test_feature',
        name='Test Command',
        attribute_id='test_command',
        parameters={'param': 'value'},
        data_key='response_data',
        position=0,
    )

    assert result == 'test_group.test_feature'
    mock_feature_service.get.assert_called_once_with('test_group.test_feature')
    mock_feature_service.save.assert_called_once_with(feature)
    assert len(feature.commands) == 1
    cmd = feature.commands[0]
    assert cmd.name == 'Test Command'
    assert cmd.attribute_id == 'test_command'
    assert cmd.parameters == {'param': 'value'}
    assert cmd.data_key == 'response_data'

# ** test: add_feature_command_missing_name
def test_add_feature_command_missing_name(mock_feature_service: FeatureService):
    '''
    Test that AddFeatureCommand validates the required name parameter.
    '''

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            AddFeatureCommand,
            dependencies={'feature_service': mock_feature_service},
            id='test_group.test_feature',
            name=' ',
            attribute_id='test_command',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == COMMAND_PARAMETER_REQUIRED_ID
    mock_feature_service.get.assert_not_called()
    mock_feature_service.save.assert_not_called()

# ** test: add_feature_command_missing_attribute_id
def test_add_feature_command_missing_attribute_id(mock_feature_service: FeatureService):
    '''
    Test that AddFeatureCommand validates the required attribute_id parameter.
    '''

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            AddFeatureCommand,
            dependencies={'feature_service': mock_feature_service},
            id='test_group.test_feature',
            name='Test Command',
            attribute_id=' ',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == COMMAND_PARAMETER_REQUIRED_ID
    mock_feature_service.get.assert_not_called()
    mock_feature_service.save.assert_not_called()

# ** test: add_feature_command_feature_not_found
def test_add_feature_command_feature_not_found(mock_feature_service: FeatureService):
    '''
    Test that AddFeatureCommand raises FEATURE_NOT_FOUND when the feature does not exist.
    '''

    mock_feature_service.get.return_value = None

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            AddFeatureCommand,
            dependencies={'feature_service': mock_feature_service},
            id='missing.feature',
            name='Test Command',
            attribute_id='test_command',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == FEATURE_NOT_FOUND_ID
    assert error.kwargs.get('feature_id') == 'missing.feature'
    mock_feature_service.get.assert_called_once_with('missing.feature')
    mock_feature_service.save.assert_not_called()


# ** test: update_feature_command_success
def test_update_feature_command_success(mock_feature_service: FeatureService):
    '''
    Test that UpdateFeatureCommand successfully updates a feature command attribute.
    '''

    command = ModelObject.new(
        FeatureCommand,
        name='Original',
        attribute_id='test_command',
        parameters={},
    )
    feature = ModelObject.new(
        Feature,
        id='test_group.test_feature',
        name='Test Feature',
        group_id='test_group',
        feature_key='test_feature',
        commands=[command],
    )
    mock_feature_service.get.return_value = feature

    result = Command.handle(
        UpdateFeatureCommand,
        dependencies={'feature_service': mock_feature_service},
        id='test_group.test_feature',
        position=0,
        attribute='name',
        value='Updated',
    )

    assert result == 'test_group.test_feature'
    mock_feature_service.get.assert_called_once_with('test_group.test_feature')
    mock_feature_service.save.assert_called_once_with(feature)
    assert feature.commands[0].name == 'Updated'


# ** test: update_feature_command_invalid_attribute
def test_update_feature_command_invalid_attribute(mock_feature_service: FeatureService):
    '''
    Test that UpdateFeatureCommand rejects unsupported attributes.
    '''

    command = ModelObject.new(
        FeatureCommand,
        name='Cmd',
        attribute_id='test_command',
        parameters={},
    )
    feature = ModelObject.new(
        Feature,
        id='test_group.test_feature',
        name='Test Feature',
        group_id='test_group',
        feature_key='test_feature',
        commands=[command],
    )
    mock_feature_service.get.return_value = feature

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeatureCommand,
            dependencies={'feature_service': mock_feature_service},
            id='test_group.test_feature',
            position=0,
            attribute='invalid',
            value='x',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == INVALID_FEATURE_COMMAND_ATTRIBUTE_ID
    mock_feature_service.save.assert_not_called()


# ** test: update_feature_command_missing_name_value
def test_update_feature_command_missing_name_value(mock_feature_service: FeatureService):
    '''
    Test that UpdateFeatureCommand enforces a value for name and attribute_id.
    '''

    command = ModelObject.new(
        FeatureCommand,
        name='Original',
        attribute_id='test_command',
        parameters={},
    )
    feature = ModelObject.new(
        Feature,
        id='test_group.test_feature',
        name='Test Feature',
        group_id='test_group',
        feature_key='test_feature',
        commands=[command],
    )
    mock_feature_service.get.return_value = feature

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeatureCommand,
            dependencies={'feature_service': mock_feature_service},
            id='test_group.test_feature',
            position=0,
            attribute='name',
            value=' ',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == COMMAND_PARAMETER_REQUIRED_ID
    mock_feature_service.save.assert_not_called()


# ** test: update_feature_command_feature_not_found
def test_update_feature_command_feature_not_found(mock_feature_service: FeatureService):
    '''
    Test that UpdateFeatureCommand raises FEATURE_NOT_FOUND when the feature does not exist.
    '''

    mock_feature_service.get.return_value = None

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeatureCommand,
            dependencies={'feature_service': mock_feature_service},
            id='missing.feature',
            position=0,
            attribute='name',
            value='Updated',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == FEATURE_NOT_FOUND_ID
    assert error.kwargs.get('feature_id') == 'missing.feature'
    mock_feature_service.save.assert_not_called()


# ** test: update_feature_command_command_not_found
def test_update_feature_command_command_not_found(mock_feature_service: FeatureService):
    '''
    Test that UpdateFeatureCommand raises FEATURE_COMMAND_NOT_FOUND when no command exists at the position.
    '''

    feature = ModelObject.new(
        Feature,
        id='test_group.test_feature',
        name='Test Feature',
        group_id='test_group',
        feature_key='test_feature',
        commands=[],
    )
    mock_feature_service.get.return_value = feature

    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeatureCommand,
            dependencies={'feature_service': mock_feature_service},
            id='test_group.test_feature',
            position=0,
            attribute='name',
            value='Updated',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == FEATURE_COMMAND_NOT_FOUND_ID
    assert error.kwargs.get('feature_id') == 'test_group.test_feature'
    assert error.kwargs.get('position') == 0
    mock_feature_service.save.assert_not_called()
