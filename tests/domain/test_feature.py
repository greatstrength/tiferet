"""Tests for Tiferet Domain Feature"""

# *** imports

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.domain.feature import (
    Feature,
    EventFeatureStep,
    ParameterSpecification,
    RequestSpecification,
)

# *** constants

# ** constant: feature_sample_data
FEATURE_SAMPLE_DATA = {
    'id': 'calc.add',
    'name': 'Add',
}

# ** constant: event_feature_step_sample_data
EVENT_FEATURE_STEP_SAMPLE_DATA = {
    'name': 'Test Event',
    'service_id': 'test_event_service',
}

# ** constant: parameter_specification_sample_data
PARAMETER_SPECIFICATION_SAMPLE_DATA = {
    'name': 'a',
    'type': 'int',
}

# ** constant: request_specification_sample_data
REQUEST_SPECIFICATION_SAMPLE_DATA = {
    'parameters': [
        {'name': 'a', 'type': 'int', 'required': True},
    ],
}

# *** testers

# ** tester: test_event_feature_step
@use_tester(
    type='domain',
    target_cls=EventFeatureStep,
    sample_data=EVENT_FEATURE_STEP_SAMPLE_DATA,
    expected_data={
        'name': 'Test Event',
        'service_id': 'test_event_service',
        'type': 'event',
        'condition': None,
        'middleware': [],
        'flags': [],
    },
    equality_fields=['name', 'service_id', 'type', 'condition', 'middleware', 'flags'],
)
class TestEventFeatureStep:
    '''Tests for EventFeatureStep construction, defaults, and round-trip.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify EventFeatureStep defaults type, condition, middleware, and flags.'''

        test_ctx.assert_new()

    # * test: flags_creation_and_round_trip
    def test_flags_creation_and_round_trip(self, test_ctx) -> None:
        '''Test that flags are set correctly and preserved through round-trip serialization.'''

        event = test_ctx.make_target(
            data={
                'name': 'Flagged Event',
                'service_id': 'flagged_event_service',
                'flags': ['flag1', 'flag2'],
            },
        )

        assert event.flags == ['flag1', 'flag2']
        reloaded = EventFeatureStep(**event.model_dump())
        assert reloaded.flags == ['flag1', 'flag2']

    # * test: type_round_trip
    def test_type_round_trip(self, test_ctx) -> None:
        '''Test that type is preserved through round-trip serialization.'''

        event = test_ctx.make_target()
        reloaded = EventFeatureStep(**event.model_dump())

        assert reloaded.type == 'event'

    # * test: condition_preserves_value
    def test_condition_preserves_value(self, test_ctx) -> None:
        '''Test that condition is preserved through construction and round-trip.'''

        event = test_ctx.make_target(
            data={
                'name': 'Conditional Event',
                'service_id': 'conditional_event_service',
                'condition': '$r.x > 0',
            },
        )

        assert event.condition == '$r.x > 0'
        reloaded = EventFeatureStep(**event.model_dump())
        assert reloaded.condition == '$r.x > 0'

    # * test: middleware_preserves_value
    def test_middleware_preserves_value(self, test_ctx) -> None:
        '''Test that middleware is preserved through construction and round-trip.'''

        event = test_ctx.make_target(
            data={
                'name': 'Middleware Event',
                'service_id': 'middleware_event_service',
                'middleware': ['timing_middleware', 'audit_middleware'],
            },
        )

        assert event.middleware == ['timing_middleware', 'audit_middleware']
        reloaded = EventFeatureStep(**event.model_dump())
        assert reloaded.middleware == ['timing_middleware', 'audit_middleware']

# ** tester: test_feature
@use_tester(
    type='domain',
    target_cls=Feature,
    sample_data=FEATURE_SAMPLE_DATA,
    expected_data={
        'id': 'calc.add',
        'name': 'Add',
        'group_id': 'calc',
        'feature_key': 'add',
        'description': 'Add',
        'middleware': [],
        'is_async': False,
        'params_schema': None,
    },
    equality_fields=[
        'id',
        'name',
        'group_id',
        'feature_key',
        'description',
        'middleware',
        'is_async',
        'params_schema',
    ],
)
class TestFeature:
    '''Tests for Feature construction, derived keys, and step lookup.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify Feature derives group_id, feature_key, and description from id and name.'''

        test_ctx.assert_new()

    # * test: derive_keys_from_group_and_name
    def test_derive_keys_from_group_and_name(self, test_ctx) -> None:
        '''Test that Feature auto-derives feature_key and id from group_id and name.'''

        feature = test_ctx.make_target(data={'group_id': 'calc', 'name': 'Add Number'})

        assert feature.feature_key == 'add_number'
        assert feature.id == 'calc.add_number'
        assert feature.description == 'Add Number'

    # * test: explicit_description_preserved
    def test_explicit_description_preserved(self, test_ctx) -> None:
        '''Test that an explicit description is not overwritten by the validator.'''

        feature = test_ctx.make_target(
            data={'id': 'calc.add', 'name': 'Add', 'description': 'Custom description'},
        )

        assert feature.description == 'Custom description'

    # * test: middleware_preserves_value
    def test_middleware_preserves_value(self, test_ctx) -> None:
        '''Test that Feature middleware is preserved through construction and round-trip.'''

        feature = test_ctx.make_target(
            data={'id': 'calc.add', 'name': 'Add', 'middleware': ['timing_middleware']},
        )

        assert feature.middleware == ['timing_middleware']
        reloaded = Feature(**feature.model_dump())
        assert reloaded.middleware == ['timing_middleware']

    # * test: is_async_preserves_value
    def test_is_async_preserves_value(self, test_ctx) -> None:
        '''Test that Feature is_async is preserved through construction and round-trip.'''

        feature = test_ctx.make_target(
            data={'id': 'calc.add', 'name': 'Add', 'is_async': True},
        )

        assert feature.is_async is True
        reloaded = Feature(**feature.model_dump())
        assert reloaded.is_async is True

    # * test: get_step_valid_and_invalid_indices
    def test_get_step_valid_and_invalid_indices(self, test_ctx) -> None:
        '''Test that get_step returns the correct step or None for invalid indices.'''

        feature = test_ctx.make_target(
            data={
                'id': 'test_group.test_feature',
                'name': 'Test Feature',
                'group_id': 'test_group',
                'feature_key': 'test_feature',
                'description': 'Test Feature',
                'steps': [],
            },
        )
        step_0 = EventFeatureStep(name='Step Zero', service_id='step_zero_service')
        step_1 = EventFeatureStep(name='Step One', service_id='step_one_service')
        feature.steps = [step_0, step_1]

        assert feature.get_step(0).name == 'Step Zero'
        assert feature.get_step(1).name == 'Step One'
        assert feature.get_step(2) is None
        assert feature.get_step('invalid') is None

    # * test: params_schema_construction
    def test_params_schema_construction(self, test_ctx) -> None:
        '''Test that Feature.params_schema is built from keyed config.'''

        feature = test_ctx.make_target(
            data={'id': 'calc.add', 'name': 'Add', 'params_schema': {'a': 'int', 'b': 'int'}},
        )

        assert isinstance(feature.params_schema, RequestSpecification)
        assert [p.name for p in feature.params_schema.parameters] == ['a', 'b']

# ** tester: test_parameter_specification
@use_tester(
    type='domain',
    target_cls=ParameterSpecification,
    sample_data=PARAMETER_SPECIFICATION_SAMPLE_DATA,
    equality_fields=['name', 'type'],
    description_cases=[
        ('get_type', (), int),
    ],
)
class TestParameterSpecification:
    '''Tests for ParameterSpecification type mapping and field definitions.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify ParameterSpecification construction against declared sample data.'''

        test_ctx.assert_new()

    # * test: description
    def test_description(self, test_ctx) -> None:
        '''Verify get_type maps the declared type string.'''

        test_ctx.assert_description()

    # * test: get_type_mapping
    def test_get_type_mapping(self, test_ctx) -> None:
        '''Test that get_type maps declared type strings to Python types.'''

        assert test_ctx.make_target(data={'name': 'a', 'type': 'str'}).get_type() is str
        assert test_ctx.make_target(data={'name': 'a', 'type': 'int'}).get_type() is int
        assert test_ctx.make_target(data={'name': 'a', 'type': 'float'}).get_type() is float
        assert test_ctx.make_target(data={'name': 'a', 'type': 'bool'}).get_type() is bool
        assert test_ctx.make_target(data={'name': 'a', 'type': 'list'}).get_type() is list
        assert test_ctx.make_target(data={'name': 'a', 'type': 'dict'}).get_type() is dict

    # * test: field_definition_required
    def test_field_definition_required(self, test_ctx) -> None:
        '''Test that a required parameter produces a required field definition.'''

        annotation, field = test_ctx.make_target().field_definition()

        assert annotation is int
        assert field.is_required()

    # * test: field_definition_optional_with_default
    def test_field_definition_optional_with_default(self, test_ctx) -> None:
        '''Test that an optional parameter with a default is not required.'''

        spec = test_ctx.make_target(
            data={'name': 'b', 'type': 'float', 'required': False, 'default': 1.0},
        )
        _annotation, field = spec.field_definition()

        assert not field.is_required()
        assert field.default == 1.0

# ** tester: test_request_specification
@use_tester(
    type='domain',
    target_cls=RequestSpecification,
    sample_data=REQUEST_SPECIFICATION_SAMPLE_DATA,
    equality_fields=[],
)
class TestRequestSpecification:
    '''Tests for RequestSpecification normalization, coerce, and is_satisfied_by.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify RequestSpecification construction from canonical parameters.'''

        test_ctx.assert_new()

    # * test: normalizes_shorthand
    def test_normalizes_shorthand(self) -> None:
        '''Test that the shorthand keyed form expands to a required parameter.'''

        spec = RequestSpecification.model_validate({'a': 'int'})

        assert len(spec.parameters) == 1
        assert spec.parameters[0].name == 'a'
        assert spec.parameters[0].type == 'int'
        assert spec.parameters[0].required is True

    # * test: normalizes_expanded
    def test_normalizes_expanded(self) -> None:
        '''Test that the expanded keyed form preserves constraints and defaults.'''

        spec = RequestSpecification.model_validate(
            {'b': {'type': 'float', 'required': False, 'default': 1.0, 'minimum': 0}},
        )
        param = spec.parameters[0]

        assert param.name == 'b'
        assert param.type == 'float'
        assert param.required is False
        assert param.default == 1.0
        assert param.minimum == 0.0

    # * test: coerce_coerces_and_preserves_extra
    def test_coerce_coerces_and_preserves_extra(self) -> None:
        '''Test that coerce coerces typed fields, applies defaults, and preserves extra keys.'''

        spec = RequestSpecification.model_validate(
            {'a': 'int', 'b': {'type': 'float', 'required': False, 'default': 1.0}},
        )
        result = spec.coerce({'a': '5', 'extra': 'keep'})

        assert result['a'] == 5
        assert isinstance(result['a'], int)
        assert result['b'] == 1.0
        assert result['extra'] == 'keep'

    # * test: coerce_missing_required_raises
    def test_coerce_missing_required_raises(self, test_ctx) -> None:
        '''Test that missing required parameters raise the pydantic ValidationError.'''

        spec = test_ctx.make_target()
        with pytest.raises(ValidationError) as exc_info:
            spec.coerce({})

        assert len(exc_info.value.errors()) == 1

    # * test: coerce_aggregates_multiple_errors
    def test_coerce_aggregates_multiple_errors(self) -> None:
        '''Test that multiple validation failures are aggregated into one error.'''

        spec = RequestSpecification.model_validate({'a': 'int', 'b': 'int'})
        with pytest.raises(ValidationError) as exc_info:
            spec.coerce({'a': 'x', 'b': 'y'})

        assert len(exc_info.value.errors()) == 2

    # * test: coerce_choices
    def test_coerce_choices(self) -> None:
        '''Test that choices restrict values via a Literal annotation.'''

        spec = RequestSpecification.model_validate(
            {'mode': {'type': 'str', 'choices': ['add', 'sub']}},
        )

        assert spec.coerce({'mode': 'add'})['mode'] == 'add'
        with pytest.raises(ValidationError):
            spec.coerce({'mode': 'bad'})

    # * test: is_satisfied_by
    def test_is_satisfied_by(self, test_ctx) -> None:
        '''Test the convenience is_satisfied_by predicate.'''

        spec = test_ctx.make_target()

        assert spec.is_satisfied_by({'a': 3}) is True
        assert spec.is_satisfied_by({}) is False
