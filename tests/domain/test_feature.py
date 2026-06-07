"""Tests for Tiferet Domain Feature"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.domain.feature import (
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
    return Feature(
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
    event = FeatureEvent(
        name='Test Event',
        service_id='test_event_service',
    )

    # Assert type defaults to 'event'.
    assert event.type == 'event'

    # Serialize via model_dump() and reload.
    primitive = event.model_dump()
    reloaded = FeatureEvent(**primitive)

    # Assert type is preserved through round-trip.
    assert reloaded.type == 'event'

# ** test: feature_event_flags_creation_and_round_trip
def test_feature_event_flags_creation_and_round_trip() -> None:
    '''
    Test that FeatureEvent flags are set correctly and preserved through round-trip serialization.
    '''

    # Create a FeatureEvent with flags.
    event = FeatureEvent(
        name='Flagged Event',
        service_id='flagged_event_service',
        flags=['flag1', 'flag2'],
    )

    # Assert flags are set correctly.
    assert event.flags == ['flag1', 'flag2']

    # Serialize via model_dump() and reload.
    primitive = event.model_dump()
    reloaded = FeatureEvent(**primitive)

    # Assert flags are preserved through round-trip.
    assert reloaded.flags == ['flag1', 'flag2']

# ** test: feature_derive_keys_from_dotted_id
def test_feature_derive_keys_from_dotted_id() -> None:
    '''
    Test that Feature auto-derives group_id and feature_key from a dotted id.
    '''

    # Create a Feature with only id and name.
    feature = Feature(id='calc.add', name='Add')

    # Assert group_id and feature_key are derived.
    assert feature.group_id == 'calc'
    assert feature.feature_key == 'add'
    assert feature.description == 'Add'

# ** test: feature_derive_keys_from_group_and_name
def test_feature_derive_keys_from_group_and_name() -> None:
    '''
    Test that Feature auto-derives feature_key and id from group_id and name.
    '''

    # Create a Feature with group_id and name only.
    feature = Feature(group_id='calc', name='Add Number')

    # Assert feature_key is snake-cased from name, and id is composed.
    assert feature.feature_key == 'add_number'
    assert feature.id == 'calc.add_number'
    assert feature.description == 'Add Number'

# ** test: feature_derive_keys_description_defaults_to_name
def test_feature_derive_keys_description_defaults_to_name() -> None:
    '''
    Test that description defaults to name when not provided.
    '''

    # Create a Feature without description.
    feature = Feature(id='calc.add', name='Add')

    # Assert description equals name.
    assert feature.description == 'Add'

# ** test: feature_derive_keys_explicit_description_preserved
def test_feature_derive_keys_explicit_description_preserved() -> None:
    '''
    Test that an explicit description is not overwritten by the validator.
    '''

    # Create a Feature with an explicit description.
    feature = Feature(id='calc.add', name='Add', description='Custom description')

    # Assert the explicit description is preserved.
    assert feature.description == 'Custom description'

# ** test: feature_event_condition_defaults_to_none
def test_feature_event_condition_defaults_to_none() -> None:
    '''
    Test that FeatureEvent condition defaults to None when not provided.
    '''

    # Create a FeatureEvent without condition.
    event = FeatureEvent(
        name='Test Event',
        service_id='test_event_service',
    )

    # Assert condition defaults to None.
    assert event.condition is None

# ** test: feature_event_condition_preserves_value
def test_feature_event_condition_preserves_value() -> None:
    '''
    Test that FeatureEvent condition is preserved through construction and round-trip.
    '''

    # Create a FeatureEvent with a condition.
    event = FeatureEvent(
        name='Conditional Event',
        service_id='conditional_event_service',
        condition='$r.x > 0',
    )

    # Assert condition is set correctly.
    assert event.condition == '$r.x > 0'

    # Serialize via model_dump() and reload.
    primitive = event.model_dump()
    reloaded = FeatureEvent(**primitive)

    # Assert condition is preserved through round-trip.
    assert reloaded.condition == '$r.x > 0'

# ** test: feature_event_middleware_defaults_to_empty
def test_feature_event_middleware_defaults_to_empty() -> None:
    '''
    Test that FeatureEvent middleware defaults to an empty list.
    '''

    # Create a FeatureEvent without middleware.
    event = FeatureEvent(
        name='Test Event',
        service_id='test_event_service',
    )

    # Assert middleware defaults to empty list.
    assert event.middleware == []

# ** test: feature_event_middleware_preserves_value
def test_feature_event_middleware_preserves_value() -> None:
    '''
    Test that FeatureEvent middleware is preserved through construction and round-trip.
    '''

    # Create a FeatureEvent with middleware.
    event = FeatureEvent(
        name='Middleware Event',
        service_id='middleware_event_service',
        middleware=['timing_middleware', 'audit_middleware'],
    )

    # Assert middleware is set correctly.
    assert event.middleware == ['timing_middleware', 'audit_middleware']

    # Serialize via model_dump() and reload.
    primitive = event.model_dump()
    reloaded = FeatureEvent(**primitive)

    # Assert middleware is preserved through round-trip.
    assert reloaded.middleware == ['timing_middleware', 'audit_middleware']

# ** test: feature_middleware_defaults_to_empty
def test_feature_middleware_defaults_to_empty() -> None:
    '''
    Test that Feature middleware defaults to an empty list.
    '''

    # Create a Feature without middleware.
    feature = Feature(id='calc.add', name='Add')

    # Assert middleware defaults to empty list.
    assert feature.middleware == []

# ** test: feature_middleware_preserves_value
def test_feature_middleware_preserves_value() -> None:
    '''
    Test that Feature middleware is preserved through construction and round-trip.
    '''

    # Create a Feature with middleware.
    feature = Feature(
        id='calc.add',
        name='Add',
        middleware=['timing_middleware'],
    )

    # Assert middleware is set correctly.
    assert feature.middleware == ['timing_middleware']

    # Serialize via model_dump() and reload.
    primitive = feature.model_dump()
    reloaded = Feature(**primitive)

    # Assert middleware is preserved through round-trip.
    assert reloaded.middleware == ['timing_middleware']

# ** test: feature_get_step_valid_and_invalid_indices
def test_feature_get_step_valid_and_invalid_indices(feature: Feature) -> None:
    '''
    Test that Feature.get_step() returns the correct step for valid indices and None for invalid indices.

    :param feature: The Feature fixture.
    :type feature: Feature
    '''

    # Create two FeatureEvent steps.
    step_0 = FeatureEvent(
        name='Step Zero',
        service_id='step_zero_service',
    )
    step_1 = FeatureEvent(
        name='Step One',
        service_id='step_one_service',
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
