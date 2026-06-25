"""Tests for Tiferet Domain Feature"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.domain.feature import (
    Feature,
    FeatureStep,
    EventFeatureStep,
    ParameterSpecification,
    RequestSpecification,
)
from tiferet.assets import TiferetError

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
    Test that EventFeatureStep defaults type to 'event' and preserves it through round-trip serialization.
    '''

    # Create an EventFeatureStep with minimal required fields.
    event = EventFeatureStep(
        name='Test Event',
        service_id='test_event_service',
    )

    # Assert type defaults to 'event'.
    assert event.type == 'event'

    # Serialize via model_dump() and reload.
    primitive = event.model_dump()
    reloaded = EventFeatureStep(**primitive)

    # Assert type is preserved through round-trip.
    assert reloaded.type == 'event'

# ** test: event_feature_step_flags_creation_and_round_trip
def test_event_feature_step_flags_creation_and_round_trip() -> None:
    '''
    Test that EventFeatureStep flags are set correctly and preserved through round-trip serialization.
    '''

    # Create an EventFeatureStep with flags.
    event = EventFeatureStep(
        name='Flagged Event',
        service_id='flagged_event_service',
        flags=['flag1', 'flag2'],
    )

    # Assert flags are set correctly.
    assert event.flags == ['flag1', 'flag2']

    # Serialize via model_dump() and reload.
    primitive = event.model_dump()
    reloaded = EventFeatureStep(**primitive)

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

# ** test: event_feature_step_condition_defaults_to_none
def test_event_feature_step_condition_defaults_to_none() -> None:
    '''
    Test that EventFeatureStep condition defaults to None when not provided.
    '''

    # Create an EventFeatureStep without condition.
    event = EventFeatureStep(
        name='Test Event',
        service_id='test_event_service',
    )

    # Assert condition defaults to None.
    assert event.condition is None

# ** test: event_feature_step_condition_preserves_value
def test_event_feature_step_condition_preserves_value() -> None:
    '''
    Test that EventFeatureStep condition is preserved through construction and round-trip.
    '''

    # Create an EventFeatureStep with a condition.
    event = EventFeatureStep(
        name='Conditional Event',
        service_id='conditional_event_service',
        condition='$r.x > 0',
    )

    # Assert condition is set correctly.
    assert event.condition == '$r.x > 0'

    # Serialize via model_dump() and reload.
    primitive = event.model_dump()
    reloaded = EventFeatureStep(**primitive)

    # Assert condition is preserved through round-trip.
    assert reloaded.condition == '$r.x > 0'

# ** test: feature_get_step_valid_and_invalid_indices
def test_feature_get_step_valid_and_invalid_indices(feature: Feature) -> None:
    '''
    Test that Feature.get_step() returns the correct step for valid indices and None for invalid indices.

    :param feature: The Feature fixture.
    :type feature: Feature
    '''

    # Create two EventFeatureStep steps.
    step_0 = EventFeatureStep(
        name='Step Zero',
        service_id='step_zero_service',
    )
    step_1 = EventFeatureStep(
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

# ** test: parameter_specification_get_type_mapping
def test_parameter_specification_get_type_mapping() -> None:
    '''
    Test that ParameterSpecification.get_type maps declared type strings to Python types.
    '''

    # Assert each supported type string maps to its Python type.
    assert ParameterSpecification(name='a', type='str').get_type() is str
    assert ParameterSpecification(name='a', type='int').get_type() is int
    assert ParameterSpecification(name='a', type='float').get_type() is float
    assert ParameterSpecification(name='a', type='bool').get_type() is bool
    assert ParameterSpecification(name='a', type='list').get_type() is list
    assert ParameterSpecification(name='a', type='dict').get_type() is dict

# ** test: parameter_specification_field_definition_required
def test_parameter_specification_field_definition_required() -> None:
    '''
    Test that a required parameter produces a required field definition.
    '''

    # Build the field definition for a required parameter.
    annotation, field = ParameterSpecification(name='a', type='int').field_definition()

    # Assert the annotation and requiredness.
    assert annotation is int
    assert field.is_required()

# ** test: parameter_specification_field_definition_optional_with_default
def test_parameter_specification_field_definition_optional_with_default() -> None:
    '''
    Test that an optional parameter with a default is not required and carries the default.
    '''

    # Build the field definition for an optional parameter with a default.
    spec = ParameterSpecification(name='b', type='float', required=False, default=1.0)
    _annotation, field = spec.field_definition()

    # Assert the field is optional with the configured default.
    assert not field.is_required()
    assert field.default == 1.0

# ** test: request_specification_normalizes_shorthand
def test_request_specification_normalizes_shorthand() -> None:
    '''
    Test that the shorthand keyed form expands to a required parameter.
    '''

    # Normalize a shorthand keyed mapping.
    spec = RequestSpecification.model_validate({'a': 'int'})

    # Assert the expanded parameter is required.
    assert len(spec.parameters) == 1
    assert spec.parameters[0].name == 'a'
    assert spec.parameters[0].type == 'int'
    assert spec.parameters[0].required is True

# ** test: request_specification_normalizes_expanded
def test_request_specification_normalizes_expanded() -> None:
    '''
    Test that the expanded keyed form preserves constraints and defaults.
    '''

    # Normalize an expanded keyed mapping.
    spec = RequestSpecification.model_validate(
        {'b': {'type': 'float', 'required': False, 'default': 1.0, 'minimum': 0}}
    )
    param = spec.parameters[0]

    # Assert the parameter constraints are preserved.
    assert param.name == 'b'
    assert param.type == 'float'
    assert param.required is False
    assert param.default == 1.0
    assert param.minimum == 0.0

# ** test: request_specification_validate_coerces_and_preserves_extra
def test_request_specification_validate_coerces_and_preserves_extra() -> None:
    '''
    Test that validate coerces typed fields, applies defaults, and preserves extra keys.
    '''

    # Validate a payload against a schema with a defaulted optional field.
    spec = RequestSpecification.model_validate(
        {'a': 'int', 'b': {'type': 'float', 'required': False, 'default': 1.0}}
    )
    result = spec.validate({'a': '5', 'extra': 'keep'})

    # Assert coercion, default application, and extra-key preservation.
    assert result['a'] == 5
    assert isinstance(result['a'], int)
    assert result['b'] == 1.0
    assert result['extra'] == 'keep'

# ** test: request_specification_validate_missing_required_raises
def test_request_specification_validate_missing_required_raises() -> None:
    '''
    Test that missing required parameters raise a single REQUEST_VALIDATION_FAILED error.
    '''

    # Validate an empty payload against a required schema.
    spec = RequestSpecification.model_validate({'a': 'int'})
    with pytest.raises(TiferetError) as exc_info:
        spec.validate({}, feature_id='calc.add')

    # Assert the structured validation error with one violation.
    assert exc_info.value.error_code == 'REQUEST_VALIDATION_FAILED'
    assert exc_info.value.kwargs.get('feature_id') == 'calc.add'
    assert len(exc_info.value.kwargs.get('violations')) == 1

# ** test: request_specification_validate_aggregates_multiple_errors
def test_request_specification_validate_aggregates_multiple_errors() -> None:
    '''
    Test that multiple validation failures are aggregated into one error.
    '''

    # Validate a payload that fails two fields.
    spec = RequestSpecification.model_validate({'a': 'int', 'b': 'int'})
    with pytest.raises(TiferetError) as exc_info:
        spec.validate({'a': 'x', 'b': 'y'}, feature_id='calc.add')

    # Assert both violations are aggregated.
    assert exc_info.value.error_code == 'REQUEST_VALIDATION_FAILED'
    assert len(exc_info.value.kwargs.get('violations')) == 2

# ** test: request_specification_validate_choices
def test_request_specification_validate_choices() -> None:
    '''
    Test that choices restrict values via a Literal annotation.
    '''

    # Validate a payload constrained by choices.
    spec = RequestSpecification.model_validate(
        {'mode': {'type': 'str', 'choices': ['add', 'sub']}}
    )

    # Assert a valid choice passes and an invalid choice fails.
    assert spec.validate({'mode': 'add'})['mode'] == 'add'
    with pytest.raises(TiferetError):
        spec.validate({'mode': 'bad'})

# ** test: request_specification_is_satisfied_by
def test_request_specification_is_satisfied_by() -> None:
    '''
    Test the convenience is_satisfied_by predicate.
    '''

    # Build a simple required schema.
    spec = RequestSpecification.model_validate({'a': 'int'})

    # Assert satisfied and unsatisfied payloads.
    assert spec.is_satisfied_by({'a': 3}) is True
    assert spec.is_satisfied_by({}) is False

# ** test: feature_params_schema_defaults_to_none
def test_feature_params_schema_defaults_to_none() -> None:
    '''
    Test that Feature.params_schema defaults to None.
    '''

    # Create a Feature without a params schema.
    feature = Feature(id='calc.add', name='Add')

    # Assert the schema defaults to None.
    assert feature.params_schema is None

# ** test: feature_params_schema_construction
def test_feature_params_schema_construction() -> None:
    '''
    Test that Feature.params_schema is built from keyed config.
    '''

    # Create a Feature with a keyed params schema.
    feature = Feature(id='calc.add', name='Add', params_schema={'a': 'int', 'b': 'int'})

    # Assert the schema parsed into a RequestSpecification.
    assert isinstance(feature.params_schema, RequestSpecification)
    assert [p.name for p in feature.params_schema.parameters] == ['a', 'b']
