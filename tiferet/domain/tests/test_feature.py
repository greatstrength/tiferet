"""Tests for Tiferet Domain Feature"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import DomainObject
from ..feature import (
    Feature,
    FeatureStep,
    FeatureEvent,
)

# *** fixtures

# ** fixture: feature
@pytest.fixture
def feature() -> Feature:
    '''
    Fixture for a basic Feature instance.

    :return: The Feature instance.
    :rtype: Feature
    '''

    # Create and return a new Feature.
    return DomainObject.new(
        Feature,
        id='test_group.test_feature',
        name='Test Feature',
        group_id='test_group',
        feature_key='test_feature',
        description='Test Feature',
        steps=[],
    )

# *** tests

# ** test: feature_step_type_defaults_to_event
def test_feature_step_type_defaults_to_event() -> None:
    '''
    Test that FeatureEvent defaults type to 'event' and preserves it through round-trip serialization.
    '''

    # Create a FeatureEvent with minimal required fields.
    event = DomainObject.new(
        FeatureEvent,
        name='Test Event',
        attribute_id='test_event_attr',
    )

    # Assert type defaults to 'event'.
    assert event.type == 'event'

    # Serialize via to_primitive() and reload.
    primitive = event.to_primitive()
    reloaded = DomainObject.new(FeatureEvent, **primitive)

    # Assert type is preserved through round-trip.
    assert reloaded.type == 'event'

# ** test: feature_event_flags_creation_and_round_trip
def test_feature_event_flags_creation_and_round_trip() -> None:
    '''
    Test that FeatureEvent flags are set correctly and preserved through round-trip serialization.
    '''

    # Create a FeatureEvent with flags.
    event = DomainObject.new(
        FeatureEvent,
        name='Flagged Event',
        attribute_id='flagged_event_attr',
        flags=['flag1', 'flag2'],
    )

    # Assert flags are set correctly.
    assert event.flags == ['flag1', 'flag2']

    # Serialize via to_primitive() and reload.
    primitive = event.to_primitive()
    reloaded = DomainObject.new(FeatureEvent, **primitive)

    # Assert flags are preserved through round-trip.
    assert reloaded.flags == ['flag1', 'flag2']

# ** test: feature_get_step_valid_and_invalid_indices
def test_feature_get_step_valid_and_invalid_indices(feature: Feature) -> None:
    '''
    Test that Feature.get_step() returns the correct step for valid indices and None for invalid indices.

    :param feature: The Feature fixture.
    :type feature: Feature
    '''

    # Create two FeatureEvent steps.
    step_0 = DomainObject.new(
        FeatureEvent,
        name='Step Zero',
        attribute_id='step_zero_attr',
    )
    step_1 = DomainObject.new(
        FeatureEvent,
        name='Step One',
        attribute_id='step_one_attr',
    )

    # Add steps to the feature.
    feature.steps = [step_0, step_1]

    # Assert valid indices return correct steps.
    assert feature.get_step(0).name == 'Step Zero'
    assert feature.get_step(1).name == 'Step One'

    # Assert out-of-range index returns None.
    assert feature.get_step(2) is None

    # Assert invalid type returns None.
    assert feature.get_step('invalid') is None
