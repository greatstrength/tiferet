"""Tiferet Feature Model Tests."""

# *** imports

# ** infra
import pytest

# ** app
from ..feature import (
    Feature,
    FeatureCommand,
    DomainObject
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

    return DomainObject.new(
        Feature,
        id='test_group.test_feature',
        name='Test Feature',
        group_id='test_group',
        feature_key='test_feature',
        description='Test Feature',
        commands=[],
    )

# *** tests

# ** test: feature_command_flags_creation_and_round_trip
def test_feature_command_flags_creation_and_round_trip() -> None:
    '''
    Test that ``FeatureCommand.flags`` can be set on creation and that the
    values are preserved through a serialization round-trip.
    '''

    command: FeatureCommand = DomainObject.new(
        FeatureCommand,
        name='Test Command',
        attribute_id='attr',
        flags=['flag1', 'flag2'],
    )

    assert command.flags == ['flag1', 'flag2']

    primitive = command.to_primitive()
    reloaded: FeatureCommand = DomainObject.new(FeatureCommand, **primitive)

    assert reloaded.flags == ['flag1', 'flag2']

# ** test: feature_get_command_valid_and_invalid_indices
def test_feature_get_command_valid_and_invalid_indices(feature: Feature) -> None:
    '''
    Test that ``get_command`` returns commands for valid indices and ``None``
    for invalid indices.
    '''

    # Add two commands to the feature.
    first_command = DomainObject.new(
        FeatureCommand,
        name='First Command',
        attribute_id='first_attr',
    )
    second_command = DomainObject.new(
        FeatureCommand,
        name='Second Command',
        attribute_id='second_attr',
    )
    feature.commands = [first_command, second_command]

    # Valid indices should return the corresponding commands.
    assert feature.get_command(0) is first_command
    assert feature.get_command(1) is second_command

    # Out-of-range indices should return None.
    assert feature.get_command(2) is None

    # Non-integer index should also return None.
    assert feature.get_command('invalid') is None
