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
    AddFeatureCommand,
    UpdateFeatureCommand,
    RemoveFeatureCommand,
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


# ** test: add_feature_command_append_success
def test_add_feature_command_append_success(
        mock_feature_service: FeatureService,
        sample_feature: Feature,
    ) -> None:
    '''
    Test successfully appending a new command to a feature workflow.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param sample_feature: The sample feature instance.
    :type sample_feature: Feature
    '''

    # Arrange the feature service to return the sample feature.
    mock_feature_service.get.return_value = sample_feature

    # Execute the command via the static Command.handle interface.
    result = Command.handle(
        AddFeatureCommand,
        dependencies={'feature_service': mock_feature_service},
        id=sample_feature.id,
        name='do_something',
        attribute_id='container.attribute',
        parameters={'foo': 'bar'},
        data_key='result_key',
        pass_on_error=True,
    )

    # Assert that the feature ID is returned.
    assert result == sample_feature.id

    # Assert that a command was appended to the feature.
    assert len(sample_feature.commands) == 1
    command = sample_feature.commands[0]
    assert command.name == 'do_something'
    assert command.attribute_id == 'container.attribute'
    assert command.parameters == {'foo': 'bar'}
    assert command.data_key == 'result_key'
    assert command.pass_on_error is True

    # Verify that the feature was retrieved and saved.
    mock_feature_service.get.assert_called_once_with(sample_feature.id)
    mock_feature_service.save.assert_called_once_with(sample_feature)


# ** test: add_feature_command_insert_success
def test_add_feature_command_insert_success(
        mock_feature_service: FeatureService,
        sample_feature: Feature,
    ) -> None:
    '''
    Test inserting a new command at a specific position in the feature workflow.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param sample_feature: The sample feature instance.
    :type sample_feature: Feature
    '''

    # Pre-populate the feature with two commands.
    sample_feature.add_command(
        name='first',
        attribute_id='container.first',
        parameters={'index': 0},
        data_key='first_key',
        pass_on_error=False,
    )
    sample_feature.add_command(
        name='second',
        attribute_id='container.second',
        parameters={'index': 1},
        data_key='second_key',
    )

    # Arrange the feature service to return the sample feature.
    mock_feature_service.get.return_value = sample_feature

    # Execute the command inserting at position 1.
    result = Command.handle(
        AddFeatureCommand,
        dependencies={'feature_service': mock_feature_service},
        id=sample_feature.id,
        name='inserted',
        attribute_id='container.inserted',
        parameters={'index': 1},
        data_key='inserted_key',
        position=1,
    )

    # Assert that the feature ID is returned.
    assert result == sample_feature.id

    # Assert that the command list has three entries with correct ordering.
    assert len(sample_feature.commands) == 3
    assert sample_feature.commands[0].name == 'first'
    assert sample_feature.commands[1].name == 'inserted'
    assert sample_feature.commands[2].name == 'second'

    inserted_command = sample_feature.commands[1]
    assert inserted_command.attribute_id == 'container.inserted'
    assert inserted_command.parameters.get('index') == '1'
    assert inserted_command.data_key == 'inserted_key'

    # Verify that the feature was retrieved and saved.
    mock_feature_service.get.assert_called_once_with(sample_feature.id)
    mock_feature_service.save.assert_called_once_with(sample_feature)


# ** test: add_feature_command_missing_required_parameters
@pytest.mark.parametrize(
    'id, name, attribute_id',
    [
        (' ', 'do_something', 'container.attribute'),
        ('group.sample_feature', ' ', 'container.attribute'),
        ('group.sample_feature', 'do_something', ' '),
    ],
)
def test_add_feature_command_missing_required_parameters(
        mock_feature_service: FeatureService,
        id: str,
        name: str,
        attribute_id: str,
    ) -> None:
    '''
    Test that AddFeatureCommand fails with COMMAND_PARAMETER_REQUIRED when
    required parameters are missing or empty.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param id: The feature identifier to test.
    :type id: str
    :param name: The command name to test.
    :type name: str
    :param attribute_id: The container attribute identifier to test.
    :type attribute_id: str
    '''

    # Execute the command with invalid parameters and expect a validation error.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            AddFeatureCommand,
            dependencies={'feature_service': mock_feature_service},
            id=id,
            name=name,
            attribute_id=attribute_id,
        )

    error: TiferetError = excinfo.value
    assert error.error_code == COMMAND_PARAMETER_REQUIRED_ID

    # The feature service should not be called when validation fails.
    mock_feature_service.get.assert_not_called()
    mock_feature_service.save.assert_not_called()


# ** test: add_feature_command_feature_not_found
def test_add_feature_command_feature_not_found(
        mock_feature_service: FeatureService,
    ) -> None:
    '''
    Test that AddFeatureCommand raises FEATURE_NOT_FOUND when the feature
    does not exist.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    # Arrange the feature service to return None for the requested feature.
    mock_feature_service.get.return_value = None

    # Execute the command and expect a TiferetError with FEATURE_NOT_FOUND_ID.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            AddFeatureCommand,
            dependencies={'feature_service': mock_feature_service},
            id='missing.feature',
            name='do_something',
            attribute_id='container.attribute',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == FEATURE_NOT_FOUND_ID
    mock_feature_service.get.assert_called_once_with('missing.feature')
    mock_feature_service.save.assert_not_called()

# ** test: update_feature_command_update_string_attributes_success
@pytest.mark.parametrize(
    'attribute, new_value, getter',
    [
        ('name', 'updated_name', lambda cmd: cmd.name),
        ('attribute_id', 'container.updated', lambda cmd: cmd.attribute_id),
        ('data_key', 'updated_key', lambda cmd: cmd.data_key),
    ],
)
def test_update_feature_command_update_string_attributes_success(
        mock_feature_service: FeatureService,
        sample_feature: Feature,
        attribute: str,
        new_value: str,
        getter,
    ) -> None:
    '''
    Test successfully updating simple string attributes on a feature command.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param sample_feature: The sample feature instance.
    :type sample_feature: Feature
    :param attribute: The attribute being updated.
    :type attribute: str
    :param new_value: The new value to assign.
    :type new_value: str
    :param getter: A callable to retrieve the updated attribute from the
        command.
    :type getter: Callable
    '''

    # Pre-populate the feature with a single command.
    command = sample_feature.add_command(
        name='original',
        attribute_id='container.original',
        parameters={'foo': 'bar'},
        data_key='original_key',
        pass_on_error=False,
    )

    # Arrange the feature service to return the sample feature.
    mock_feature_service.get.return_value = sample_feature

    # Execute the command via the static Command.handle interface.
    result = Command.handle(
        UpdateFeatureCommand,
        dependencies={'feature_service': mock_feature_service},
        id=sample_feature.id,
        position=0,
        attribute=attribute,
        value=new_value,
    )

    # Assert that the feature ID is returned and the command was updated.
    assert result == sample_feature.id
    assert getter(command) == new_value
    mock_feature_service.get.assert_called_once_with(sample_feature.id)
    mock_feature_service.save.assert_called_once_with(sample_feature)

# ** test: update_feature_command_update_parameters_success
def test_update_feature_command_update_parameters_success(
        mock_feature_service: FeatureService,
        sample_feature: Feature,
    ) -> None:
    '''
    Test updating the parameters attribute on a feature command.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param sample_feature: The sample feature instance.
    :type sample_feature: Feature
    '''

    # Pre-populate the feature with a command that has existing parameters.
    command = sample_feature.add_command(
        name='with_params',
        attribute_id='container.with_params',
        parameters={'foo': 'bar', 'remove_me': 'x'},
        data_key='key',
    )

    # Arrange the feature service to return the sample feature.
    mock_feature_service.get.return_value = sample_feature

    # Update parameters, adding a new key and clearing an existing one.
    result = Command.handle(
        UpdateFeatureCommand,
        dependencies={'feature_service': mock_feature_service},
        id=sample_feature.id,
        position=0,
        attribute='parameters',
        value={'baz': 'qux', 'remove_me': None},
    )

    # Assert that the feature ID is returned and parameters were merged.
    assert result == sample_feature.id
    assert command.parameters == {'foo': 'bar', 'baz': 'qux'}
    mock_feature_service.get.assert_called_once_with(sample_feature.id)
    mock_feature_service.save.assert_called_once_with(sample_feature)

# ** test: update_feature_command_update_pass_on_error_success
def test_update_feature_command_update_pass_on_error_success(
        mock_feature_service: FeatureService,
        sample_feature: Feature,
    ) -> None:
    '''
    Test updating the pass_on_error attribute on a feature command.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param sample_feature: The sample feature instance.
    :type sample_feature: Feature
    '''

    # Pre-populate the feature with a command where pass_on_error is False.
    command = sample_feature.add_command(
        name='handler',
        attribute_id='container.handler',
        parameters={},
        data_key=None,
        pass_on_error=False,
    )

    # Arrange the feature service to return the sample feature.
    mock_feature_service.get.return_value = sample_feature

    # Update the pass_on_error flag.
    result = Command.handle(
        UpdateFeatureCommand,
        dependencies={'feature_service': mock_feature_service},
        id=sample_feature.id,
        position=0,
        attribute='pass_on_error',
        value=True,
    )

    # Assert that the feature ID is returned and the flag was updated.
    assert result == sample_feature.id
    assert command.pass_on_error is True
    mock_feature_service.get.assert_called_once_with(sample_feature.id)
    mock_feature_service.save.assert_called_once_with(sample_feature)

# ** test: update_feature_command_missing_required_parameters
@pytest.mark.parametrize(
    'id, position, attribute',
    [
        (' ', 0, 'name'),
        ('group.sample_feature', None, 'name'),
        ('group.sample_feature', 0, ' '),
    ],
)
def test_update_feature_command_missing_required_parameters(
        mock_feature_service: FeatureService,
        id: str,
        position: int | None,
        attribute: str,
    ) -> None:
    '''
    Test that UpdateFeatureCommand fails with COMMAND_PARAMETER_REQUIRED when
    required parameters are missing or empty.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param id: The feature identifier to test.
    :type id: str
    :param position: The command position to test.
    :type position: int | None
    :param attribute: The attribute name to test.
    :type attribute: str
    '''

    # Execute the command with invalid parameters and expect a validation error.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeatureCommand,
            dependencies={'feature_service': mock_feature_service},
            id=id,
            position=position,
            attribute=attribute,
        )

    error: TiferetError = excinfo.value
    assert error.error_code == COMMAND_PARAMETER_REQUIRED_ID

    # The feature service should not be called when validation fails.
    mock_feature_service.get.assert_not_called()
    mock_feature_service.save.assert_not_called()

# ** test: update_feature_command_invalid_attribute
def test_update_feature_command_invalid_attribute(
        mock_feature_service: FeatureService,
    ) -> None:
    '''
    Test that UpdateFeatureCommand fails when an unsupported attribute is
    provided.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    # Execute the command with an invalid attribute and expect an error.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeatureCommand,
            dependencies={'feature_service': mock_feature_service},
            id='group.sample_feature',
            position=0,
            attribute='invalid',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == INVALID_FEATURE_COMMAND_ATTRIBUTE_ID

    # The feature service should not be called when attribute validation fails.
    mock_feature_service.get.assert_not_called()
    mock_feature_service.save.assert_not_called()

# ** test: update_feature_command_missing_name_or_attribute_id_value
@pytest.mark.parametrize('attribute', ['name', 'attribute_id'])
def test_update_feature_command_missing_name_or_attribute_id_value(
        mock_feature_service: FeatureService,
        attribute: str,
    ) -> None:
    '''
    Test that UpdateFeatureCommand fails with COMMAND_PARAMETER_REQUIRED when
    updating name or attribute_id with an empty value.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param attribute: The attribute being updated.
    :type attribute: str
    '''

    # Execute the command with an empty value and expect an error.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeatureCommand,
            dependencies={'feature_service': mock_feature_service},
            id='group.sample_feature',
            position=0,
            attribute=attribute,
            value=' ',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == COMMAND_PARAMETER_REQUIRED_ID

    # The feature service should not be called when name/attribute_id
    # validation fails.
    mock_feature_service.get.assert_not_called()
    mock_feature_service.save.assert_not_called()

# ** test: update_feature_command_feature_not_found
def test_update_feature_command_feature_not_found(
        mock_feature_service: FeatureService,
    ) -> None:
    '''
    Test that UpdateFeatureCommand raises FEATURE_NOT_FOUND when the feature
    does not exist.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    # Arrange the feature service to return None for the requested feature.
    mock_feature_service.get.return_value = None

    # Execute the command and expect a TiferetError with FEATURE_NOT_FOUND_ID.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeatureCommand,
            dependencies={'feature_service': mock_feature_service},
            id='missing.feature',
            position=0,
            attribute='name',
            value='Updated Name',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == FEATURE_NOT_FOUND_ID
    mock_feature_service.get.assert_called_once_with('missing.feature')
    mock_feature_service.save.assert_not_called()

# ** test: update_feature_command_command_not_found
def test_update_feature_command_command_not_found(
        mock_feature_service: FeatureService,
        sample_feature: Feature,
    ) -> None:
    '''
    Test that UpdateFeatureCommand raises FEATURE_COMMAND_NOT_FOUND when the
    command at the specified position does not exist.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param sample_feature: The sample feature instance.
    :type sample_feature: Feature
    '''

    # Ensure the feature has no commands so that get_command returns None.
    assert sample_feature.commands == []

    # Arrange the feature service to return the sample feature.
    mock_feature_service.get.return_value = sample_feature

    # Execute the command and expect a TiferetError with
    # FEATURE_COMMAND_NOT_FOUND_ID.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            UpdateFeatureCommand,
            dependencies={'feature_service': mock_feature_service},
            id=sample_feature.id,
            position=0,
            attribute='name',
            value='Updated Name',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == FEATURE_COMMAND_NOT_FOUND_ID
    mock_feature_service.get.assert_called_once_with(sample_feature.id)
    mock_feature_service.save.assert_not_called()

# ** test: remove_feature_command_success
def test_remove_feature_command_success(
        mock_feature_service: FeatureService,
        sample_feature: Feature,
    ) -> None:
    '''
    Test successfully removing a command at a valid position via
    RemoveFeatureCommand.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param sample_feature: The sample feature instance.
    :type sample_feature: Feature
    '''

    # Pre-populate the feature with two commands.
    first_command = sample_feature.add_command(
        name='first',
        attribute_id='container.first',
        parameters={'index': 0},
        data_key='first_key',
    )
    second_command = sample_feature.add_command(
        name='second',
        attribute_id='container.second',
        parameters={'index': 1},
        data_key='second_key',
    )

    assert sample_feature.commands == [first_command, second_command]

    # Arrange the feature service to return the sample feature.
    mock_feature_service.get.return_value = sample_feature

    # Execute the command via the static Command.handle interface.
    result = Command.handle(
        RemoveFeatureCommand,
        dependencies={'feature_service': mock_feature_service},
        id=sample_feature.id,
        position=0,
    )

    # Assert that the feature ID is returned and the first command was
    # removed.
    assert result == sample_feature.id
    assert sample_feature.commands == [second_command]

    # Verify that the feature was retrieved and saved.
    mock_feature_service.get.assert_called_once_with(sample_feature.id)
    mock_feature_service.save.assert_called_once_with(sample_feature)

# ** test: remove_feature_command_invalid_position_idempotent
def test_remove_feature_command_invalid_position_idempotent(
        mock_feature_service: FeatureService,
        sample_feature: Feature,
    ) -> None:
    '''
    Test that RemoveFeatureCommand behaves idempotently when an invalid
    position is provided.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param sample_feature: The sample feature instance.
    :type sample_feature: Feature
    '''

    # Pre-populate the feature with a single command.
    original_command = sample_feature.add_command(
        name='only',
        attribute_id='container.only',
        parameters={'index': 0},
        data_key='only_key',
    )

    # Arrange the feature service to return the sample feature.
    mock_feature_service.get.return_value = sample_feature

    # Execute the command with an out-of-range position; this should be a
    # silent, idempotent no-op.
    result = Command.handle(
        RemoveFeatureCommand,
        dependencies={'feature_service': mock_feature_service},
        id=sample_feature.id,
        position=5,
    )

    # Assert that the feature ID is returned and the commands list is
    # unchanged.
    assert result == sample_feature.id
    assert sample_feature.commands == [original_command]

    # Verify that the feature was retrieved and saved.
    mock_feature_service.get.assert_called_once_with(sample_feature.id)
    mock_feature_service.save.assert_called_once_with(sample_feature)

# ** test: remove_feature_command_feature_not_found
def test_remove_feature_command_feature_not_found(
        mock_feature_service: FeatureService,
    ) -> None:
    '''
    Test that RemoveFeatureCommand raises FEATURE_NOT_FOUND when the feature
    does not exist.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    '''

    # Arrange the feature service to return None for the requested feature.
    mock_feature_service.get.return_value = None

    # Execute the command and expect a TiferetError with FEATURE_NOT_FOUND_ID.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            RemoveFeatureCommand,
            dependencies={'feature_service': mock_feature_service},
            id='missing.feature',
            position=0,
        )

    error: TiferetError = excinfo.value
    assert error.error_code == FEATURE_NOT_FOUND_ID
    mock_feature_service.get.assert_called_once_with('missing.feature')
    mock_feature_service.save.assert_not_called()

# ** test: remove_feature_command_missing_required_parameters
@pytest.mark.parametrize(
    'id, position',
    [
        (' ', 0),
        ('group.sample_feature', None),
    ],
)
def test_remove_feature_command_missing_required_parameters(
        mock_feature_service: FeatureService,
        id: str,
        position: int | None,
    ) -> None:
    '''
    Test that RemoveFeatureCommand fails with COMMAND_PARAMETER_REQUIRED when
    required parameters are missing or empty.

    :param mock_feature_service: The mock feature service.
    :type mock_feature_service: FeatureService
    :param id: The feature identifier to test.
    :type id: str
    :param position: The command position to test.
    :type position: int | None
    '''

    # Execute the command with invalid parameters and expect a validation
    # error.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            RemoveFeatureCommand,
            dependencies={'feature_service': mock_feature_service},
            id=id,
            position=position,
        )

    error: TiferetError = excinfo.value
    assert error.error_code == COMMAND_PARAMETER_REQUIRED_ID

    # The feature service should not be called when validation fails.
    mock_feature_service.get.assert_not_called()
    mock_feature_service.save.assert_not_called()
