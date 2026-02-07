"""Tiferet Feature Model Tests."""

# *** imports

# ** infra
import pytest

# ** app
from ..feature import (
    Feature,
    FeatureCommand,
    ModelObject
)

# *** fixtures


# ** fixture: feature
@pytest.fixture
def feature() -> Feature:
    '''
    Fixture to create a Feature instance for testing.

    :return: The Feature instance.
    :rtype: Feature
    '''

    return Feature.new(
        name='Test Feature',
        group_id='test_group',
        commands=[],
    )

# *** tests

# ** test: feature_flags_creation_and_round_trip
def test_feature_flags_creation_and_round_trip() -> None:
    '''
    Test that ``Feature.flags`` can be set on creation and that the
    values are preserved through a serialization round-trip.
    '''

    feature = Feature.new(
        name='Test Feature with Flags',
        group_id='test_group',
        flags=['global_flag', 'feature_specific_flag'],
    )

    assert feature.flags == ['global_flag', 'feature_specific_flag']

    primitive = feature.to_primitive()
    reloaded: Feature = ModelObject.new(Feature, **primitive)

    assert reloaded.flags == ['global_flag', 'feature_specific_flag']

# ** test: feature_new
def test_feature_new():
    '''
    Test creating a Feature instance with all attributes.
    '''

    # Create new feature with all attributes.
    feature = Feature.new(
        name='Test Feature',
        group_id='test_group',
        feature_key='test_feature',
        id='test_group.test_feature',
        description='A test feature.',
        commands=[],
    )

    # Test that the feature is created correctly.
    assert feature.name == 'Test Feature'
    assert feature.group_id == 'test_group'
    assert feature.feature_key == 'test_feature'
    assert feature.id == 'test_group.test_feature'
    assert feature.description == 'A test feature.'
    assert len(feature.commands) == 0

# ** test: feature_new_no_description
def test_feature_new_no_description():
    '''
    Test creating a Feature instance without a description.
    '''

    # Create new feature with no description.
    feature = Feature.new(
        name='Test Feature',
        group_id='test_group',
        feature_key='test_feature',
        id='test_group.test_feature',
        commands=[],
    )

    # Test that the default description is set correctly.
    assert feature.name == 'Test Feature'
    assert feature.group_id == 'test_group'
    assert feature.feature_key == 'test_feature'
    assert feature.id == 'test_group.test_feature'
    assert feature.description == feature.name
    assert len(feature.commands) == 0

# ** test: feature_new_name_and_group_only
def test_feature_new_name_and_group_only():

    # Create the feature with only the name and group ID.
    feature = Feature.new(
        name='Test Feature',
        group_id='test_group',
        description='A test feature.',
    )    

    # Test that the feature is created correctly.
    assert feature.name == 'Test Feature'
    assert feature.group_id == 'test_group'
    assert feature.feature_key == 'test_feature'
    assert feature.id == 'test_group.test_feature'
    assert feature.description == 'A test feature.'
    assert len(feature.commands) == 0

# ** test: feature_add_service_command
def test_feature_add_service_command(feature: Feature):
    '''
    Test adding a FeatureCommand to a Feature using raw attributes.

    :param feature: The feature to add the command to.
    :type feature: Feature
    '''

    # Add a command using raw attributes.
    command = feature.add_command(
        name='Test Service Command',
        attribute_id='test_feature_command',
        parameters={'param1': 'value1'},
    )

    # Test that the new command is added to the list.
    assert len(feature.commands) == 1
    assert feature.commands[0] == command
    # Default pass_on_error should be False.
    assert command.pass_on_error is False

# ** test: feature_add_command_position
def test_feature_add_command_position(feature: Feature):
    '''
    Test inserting a feature command at a specific position.

    :param feature: The feature to add the commands to.
    :type feature: Feature
    '''

    # Add an initial command.
    first_command = feature.add_command(
        name='Initial Service Command',
        attribute_id='initial_feature_command',
        parameters={'param1': 'value1'},
        pass_on_error=True,
    )

    # Add a new command at the beginning.
    new_command = feature.add_command(
        name='New Service Command',
        attribute_id='new_feature_command',
        parameters={'param1': 'value1'},
        position=0,
    )

    # Test that the new command is added to the beginning of the list.
    assert len(feature.commands) == 2
    assert feature.commands[0] == new_command
    assert feature.commands[1] == first_command
    # Ensure pass_on_error is preserved on the first command.
    assert first_command.pass_on_error is True

# ** test: feature_rename
def test_feature_rename(feature: Feature) -> None:
    '''
    Test renaming a feature updates only the name attribute.

    :param feature: The feature to rename.
    :type feature: Feature
    '''

    # Capture original attributes.
    original_id = feature.id
    original_group_id = feature.group_id
    original_feature_key = feature.feature_key
    original_description = feature.description
    original_commands = list(feature.commands)

    # Rename the feature.
    feature.rename('Renamed Feature')

    # Verify that only the name has changed.
    assert feature.name == 'Renamed Feature'
    assert feature.id == original_id
    assert feature.group_id == original_group_id
    assert feature.feature_key == original_feature_key
    assert feature.description == original_description
    assert feature.commands == original_commands

# ** test: feature_set_description_value
def test_feature_set_description_value(feature: Feature) -> None:
    '''
    Test setting a new description on a feature.

    :param feature: The feature to update.
    :type feature: Feature
    '''

    # Capture original attributes.
    original_id = feature.id
    original_group_id = feature.group_id
    original_feature_key = feature.feature_key
    original_name = feature.name
    original_commands = list(feature.commands)

    # Set a new description.
    feature.set_description('Updated description.')

    # Verify that only the description has changed.
    assert feature.description == 'Updated description.'
    assert feature.id == original_id
    assert feature.group_id == original_group_id
    assert feature.feature_key == original_feature_key
    assert feature.name == original_name
    assert feature.commands == original_commands

# ** test: feature_set_description_none
def test_feature_set_description_none(feature: Feature) -> None:
    '''
    Test clearing the description by setting it to None.

    :param feature: The feature to update.
    :type feature: Feature
    '''

    # Capture original attributes.
    original_id = feature.id
    original_group_id = feature.group_id
    original_feature_key = feature.feature_key
    original_name = feature.name
    original_commands = list(feature.commands)

    # Clear the description.
    feature.set_description(None)

    # Verify that the description is cleared and other attributes are unchanged.
    assert feature.description is None
    assert feature.id == original_id
    assert feature.group_id == original_group_id
    assert feature.feature_key == original_feature_key
    assert feature.name == original_name
    assert feature.commands == original_commands

# ** test: feature_command_flags_creation_and_round_trip
def test_feature_command_flags_creation_and_round_trip() -> None:
    '''
    Test that ``FeatureCommand.flags`` can be set on creation and that the
    values are preserved through a serialization round-trip.
    '''

    command: FeatureCommand = ModelObject.new(
        FeatureCommand,
        name='Test Command',
        attribute_id='attr',
        flags=['flag1', 'flag2'],
    )

    assert command.flags == ['flag1', 'flag2']

    primitive = command.to_primitive()
    reloaded: FeatureCommand = ModelObject.new(FeatureCommand, **primitive)

    assert reloaded.flags == ['flag1', 'flag2']


# ** test: feature_command_set_pass_on_error_false_string
def test_feature_command_set_pass_on_error_false_string() -> None:
    '''
    Test that ``set_pass_on_error`` treats the string "false" (any case) as
    ``False`` and uses standard bool conversion otherwise.
    '''

    command: FeatureCommand = ModelObject.new(
        FeatureCommand,
        name='Test Command',
        attribute_id='attr',
    )

    # Explicit "false" string should result in False.
    command.set_pass_on_error('false')
    assert command.pass_on_error is False

    # Mixed-case "False" string should also result in False.
    command.set_pass_on_error('False')
    assert command.pass_on_error is False

    # Truthy value should result in True.
    command.set_pass_on_error(1)
    assert command.pass_on_error is True

# ** test: feature_command_set_parameters_merge_and_cleanup
def test_feature_command_set_parameters_merge_and_cleanup() -> None:
    '''
    Test that ``set_parameters`` merges parameters and removes keys with
    ``None`` values.
    '''

    command: FeatureCommand = ModelObject.new(
        FeatureCommand,
        name='Test Command',
        attribute_id='attr',
        parameters={'a': '1', 'b': '2'},
    )

    # Merge new parameters, overriding existing values and dropping None.
    command.set_parameters({'b': '3', 'c': None})

    assert command.parameters == {'a': '1', 'b': '3'}

# ** test: feature_command_set_parameters_none_noop
def test_feature_command_set_parameters_none_noop() -> None:
    '''
    Test that ``set_parameters`` is a no-op when ``None`` is provided.
    '''

    command: FeatureCommand = ModelObject.new(
        FeatureCommand,
        name='Test Command',
        attribute_id='attr',
        parameters={'a': '1'},
    )

    command.set_parameters(None)

    assert command.parameters == {'a': '1'}

# ** test: feature_command_set_attribute_delegates
def test_feature_command_set_attribute_delegates() -> None:
    '''
    Test that ``set_attribute`` delegates to specialized methods for
    ``parameters`` and ``pass_on_error``.
    '''

    command: FeatureCommand = ModelObject.new(
        FeatureCommand,
        name='Test Command',
        attribute_id='attr',
        parameters={'a': '1'},
    )

    # Update parameters via set_attribute.
    command.set_attribute('parameters', {'a': None, 'b': '2'})
    assert command.parameters == {'b': '2'}

    # Update pass_on_error via set_attribute.
    command.set_attribute('pass_on_error', 'false')
    assert command.pass_on_error is False

# ** test: feature_command_set_attribute_fallback
def test_feature_command_set_attribute_fallback() -> None:
    '''
    Test that ``set_attribute`` falls back to ``setattr`` for other
    attributes.
    '''

    command: FeatureCommand = ModelObject.new(
        FeatureCommand,
        name='Test Command',
        attribute_id='attr',
    )

    # Set the data_key attribute using the generic attribute setter.
    command.set_attribute('data_key', 'result')
    assert command.data_key == 'result'

# ** test: feature_get_command_valid_and_invalid_indices
def test_feature_get_command_valid_and_invalid_indices(feature: Feature) -> None:
    '''
    Test that ``get_command`` returns commands for valid indices and ``None``
    for invalid indices.
    '''

    # Add two commands to the feature.
    first_command = feature.add_command(
        name='First Command',
        attribute_id='first_attr',
    )
    second_command = feature.add_command(
        name='Second Command',
        attribute_id='second_attr',
    )

    # Valid indices should return the corresponding commands.
    assert feature.get_command(0) is first_command
    assert feature.get_command(1) is second_command

    # Out-of-range indices should return None.
    assert feature.get_command(2) is None

    # Non-integer index should also return None.
    assert feature.get_command('invalid') is None

# ** test: feature_remove_command_valid_positions
def test_feature_remove_command_valid_positions(feature: Feature) -> None:
    '''
    Test that ``remove_command`` removes and returns commands for valid
    positions.
    '''

    # Add three commands to the feature.
    first_command = feature.add_command(
        name='First Command',
        attribute_id='first_attr',
    )
    middle_command = feature.add_command(
        name='Middle Command',
        attribute_id='middle_attr',
    )
    last_command = feature.add_command(
        name='Last Command',
        attribute_id='last_attr',
    )

    # Remove the middle command.
    removed = feature.remove_command(1)
    assert removed is middle_command
    assert feature.commands == [first_command, last_command]

    # Remove the first command (start of the list).
    removed = feature.remove_command(0)
    assert removed is first_command
    assert feature.commands == [last_command]

    # Re-add commands to test removing the last position explicitly.
    feature.add_command(
        name='Another Command',
        attribute_id='another_attr',
    )
    # At this point, commands are [last_command, another_command].
    another_command = feature.commands[1]

    removed = feature.remove_command(1)
    assert removed is another_command
    assert feature.commands == [last_command]

# ** test: feature_remove_command_invalid_positions
def test_feature_remove_command_invalid_positions(feature: Feature) -> None:
    '''
    Test that ``remove_command`` returns ``None`` and leaves the commands
    list unchanged for invalid positions.
    '''

    # Add two commands to the feature.
    first_command = feature.add_command(
        name='First Command',
        attribute_id='first_attr',
    )
    second_command = feature.add_command(
        name='Second Command',
        attribute_id='second_attr',
    )

    original_commands = list(feature.commands)

    # Out-of-range positive index should return None and not modify the list.
    assert feature.remove_command(5) is None
    assert feature.commands == original_commands

    # Negative index should return None and not modify the list.
    assert feature.remove_command(-1) is None
    assert feature.commands == original_commands

    # Non-integer index should also return None and not modify the list.
    assert feature.remove_command('invalid') is None
    assert feature.commands == original_commands

    # Empty list should remain unchanged when attempting removal.
    empty_feature = Feature.new(
        name='Empty Feature',
        group_id='empty_group',
        commands=[],
    )

    assert empty_feature.remove_command(0) is None
    assert empty_feature.commands == []

# ** test: feature_reorder_command_move_forward
def test_feature_reorder_command_move_forward(feature: Feature) -> None:
    '''
    Test moving a feature command forward in the list.
    '''

    # Add three commands to the feature.
    first_command = feature.add_command(
        name='First Command',
        attribute_id='first_attr',
    )
    second_command = feature.add_command(
        name='Second Command',
        attribute_id='second_attr',
    )
    third_command = feature.add_command(
        name='Third Command',
        attribute_id='third_attr',
    )

    # Move the first command to the end.
    moved = feature.reorder_command(0, 2)

    assert moved is first_command
    assert feature.commands == [second_command, third_command, first_command]

# ** test: feature_reorder_command_move_backward
def test_feature_reorder_command_move_backward(feature: Feature) -> None:
    '''
    Test moving a feature command backward in the list.
    '''

    # Add three commands to the feature.
    first_command = feature.add_command(
        name='First Command',
        attribute_id='first_attr',
    )
    second_command = feature.add_command(
        name='Second Command',
        attribute_id='second_attr',
    )
    third_command = feature.add_command(
        name='Third Command',
        attribute_id='third_attr',
    )

    # Move the last command to the beginning.
    moved = feature.reorder_command(2, 0)

    assert moved is third_command
    assert feature.commands == [third_command, first_command, second_command]

# ** test: feature_reorder_command_clamp_positions
def test_feature_reorder_command_clamp_positions() -> None:
    '''
    Test that ``reorder_command`` clamps the new position to the valid range.
    '''

    # Create a feature with three commands.
    feature = Feature.new(
        name='Clamp Feature',
        group_id='clamp_group',
        commands=[],
    )

    first_command = feature.add_command(
        name='First Command',
        attribute_id='first_attr',
    )
    second_command = feature.add_command(
        name='Second Command',
        attribute_id='second_attr',
    )
    third_command = feature.add_command(
        name='Third Command',
        attribute_id='third_attr',
    )

    # Clamp low: move middle command to a negative index, which should clamp to 0.
    feature.reorder_command(1, -10)
    assert feature.commands == [second_command, first_command, third_command]

    # Reset order and clamp high: move middle command beyond the end, which
    # should clamp to the list length.
    feature.commands = [first_command, second_command, third_command]

    feature.reorder_command(1, 10)
    assert feature.commands == [first_command, third_command, second_command]

# ** test: feature_reorder_command_invalid_current_position
def test_feature_reorder_command_invalid_current_position(feature: Feature) -> None:
    '''
    Test that ``reorder_command`` returns ``None`` and leaves the commands
    list unchanged for invalid ``current_position`` values.
    '''

    # Add two commands to the feature.
    first_command = feature.add_command(
        name='First Command',
        attribute_id='first_attr',
    )
    second_command = feature.add_command(
        name='Second Command',
        attribute_id='second_attr',
    )

    original_commands = list(feature.commands)

    # Out-of-range positive index should return None and not modify the list.
    assert feature.reorder_command(5, 0) is None
    assert feature.commands == original_commands

    # Non-integer index should also return None and not modify the list.
    assert feature.reorder_command('invalid', 0) is None
    assert feature.commands == original_commands
