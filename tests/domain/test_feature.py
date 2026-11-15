"""Tests for Tiferet Domain Feature"""

# *** imports

# ** core
import json
from types import MappingProxyType

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.domain import INVALID_MODEL_VALUE_ID, ModelError
from tiferet.domain.feature import (
    Feature,
    FeatureStep,
    EventFeatureStep,
    ParameterSpecification,
    RequestSpecification,
)

# *** functions

# ** function: assert_model_value_error
def assert_model_value_error(error: ModelError, message: str) -> None:
    '''
    Assert a ModelError carries INVALID_MODEL_VALUE_ID and the expected message.

    :param error: The raised model error.
    :type error: ModelError
    :param message: The expected message text.
    :type message: str
    '''

    # Assert the error code and the exact message payload.
    assert error.error_code == INVALID_MODEL_VALUE_ID
    assert json.loads(str(error))['message'] == message

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

# ** test: request_specification_coerce_coerces_and_preserves_extra
def test_request_specification_coerce_coerces_and_preserves_extra() -> None:
    '''
    Test that coerce coerces typed fields, applies defaults, and preserves extra keys.
    '''

    # Coerce a payload against a schema with a defaulted optional field.
    spec = RequestSpecification.model_validate(
        {'a': 'int', 'b': {'type': 'float', 'required': False, 'default': 1.0}}
    )
    result = spec.coerce({'a': '5', 'extra': 'keep'})

    # Assert coercion, default application, and extra-key preservation.
    assert result['a'] == 5
    assert isinstance(result['a'], int)
    assert result['b'] == 1.0
    assert result['extra'] == 'keep'

# ** test: request_specification_coerce_missing_required_raises
def test_request_specification_coerce_missing_required_raises() -> None:
    '''
    Test that missing required parameters raise a Pydantic ValidationError.
    '''

    # Coerce an empty payload against a required schema.
    spec = RequestSpecification.model_validate({'a': 'int'})
    with pytest.raises(ValidationError) as exc_info:
        spec.coerce({})

    # Assert one field error is reported by Pydantic.
    assert len(exc_info.value.errors()) == 1

# ** test: request_specification_coerce_aggregates_multiple_errors
def test_request_specification_coerce_aggregates_multiple_errors() -> None:
    '''
    Test that multiple validation failures are aggregated into one ValidationError.
    '''

    # Coerce a payload that fails two fields.
    spec = RequestSpecification.model_validate({'a': 'int', 'b': 'int'})
    with pytest.raises(ValidationError) as exc_info:
        spec.coerce({'a': 'x', 'b': 'y'})

    # Assert both field errors are aggregated.
    assert len(exc_info.value.errors()) == 2

# ** test: request_specification_coerce_choices
def test_request_specification_coerce_choices() -> None:
    '''
    Test that choices restrict values via a Literal annotation.
    '''

    # Coerce a payload constrained by choices.
    spec = RequestSpecification.model_validate(
        {'mode': {'type': 'str', 'choices': ['add', 'sub']}}
    )

    # Assert a valid choice passes and an invalid choice fails.
    assert spec.coerce({'mode': 'add'})['mode'] == 'add'
    with pytest.raises(ValidationError):
        spec.coerce({'mode': 'bad'})

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

# ** test: event_feature_step_middleware_defaults_to_empty
def test_event_feature_step_middleware_defaults_to_empty() -> None:
    '''
    Test that EventFeatureStep.middleware defaults to an empty list.
    '''

    # Create an EventFeatureStep without middleware.
    event = EventFeatureStep(
        name='Test Event',
        service_id='test_event_service',
    )

    # Assert middleware defaults to empty list.
    assert event.middleware == []

# ** test: event_feature_step_middleware_preserves_value
def test_event_feature_step_middleware_preserves_value() -> None:
    '''
    Test that EventFeatureStep.middleware preserves an explicitly provided value.
    '''

    # Create an EventFeatureStep with an explicit middleware list.
    event = EventFeatureStep(
        name='Test Event',
        service_id='test_event_service',
        middleware=['log', 'time'],
    )

    # Assert middleware is preserved.
    assert event.middleware == ['log', 'time']

# ** test: feature_middleware_defaults_to_empty
def test_feature_middleware_defaults_to_empty() -> None:
    '''
    Test that Feature.middleware defaults to an empty list.
    '''

    # Create a Feature without middleware.
    feature = Feature(id='calc.add', name='Add')

    # Assert middleware defaults to empty list.
    assert feature.middleware == []

# ** test: feature_middleware_preserves_value
def test_feature_middleware_preserves_value() -> None:
    '''
    Test that Feature.middleware preserves an explicitly provided value.
    '''

    # Create a Feature with an explicit middleware list.
    feature = Feature(id='calc.add', name='Add', middleware=['log'])

    # Assert middleware is preserved.
    assert feature.middleware == ['log']

# ** test: feature_is_async_defaults_to_false
def test_feature_is_async_defaults_to_false() -> None:
    '''
    Test that Feature.is_async defaults to False.
    '''

    # Create a Feature without is_async.
    feature = Feature(id='calc.add', name='Add')

    # Assert is_async defaults to False.
    assert feature.is_async is False

# ** test: feature_is_async_true
def test_feature_is_async_true() -> None:
    '''
    Test that Feature.is_async accepts and preserves True.
    '''

    # Create a Feature with is_async set to True.
    feature = Feature(id='calc.add', name='Add', is_async=True)

    # Assert is_async is True.
    assert feature.is_async is True

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

# *** testers

# ** tester: test_parameter_specification
@use_tester(
    type='domain',
    target_cls=ParameterSpecification,
    equality_fields=[],
)
class TestParameterSpecification:
    '''
    Tests for ParameterSpecification configuration and runtime faces.
    '''

    # * test: from_config_entry_shorthand
    def test_from_config_entry_shorthand(self):
        '''
        Test that a type string constructs a required parameter of that type.
        '''

        # Construct a shorthand entry for each supported type.
        for type_name in ('str', 'int', 'float', 'bool', 'list', 'dict'):
            result = ParameterSpecification.from_config_entry('a', type_name)

            # Assert the name, type, requiredness, and remaining defaults.
            assert isinstance(result, ParameterSpecification)
            assert result.name == 'a'
            assert result.type == type_name
            assert result.required is True
            assert result.default is None
            assert result.description is None
            assert result.minimum is None
            assert result.maximum is None
            assert result.min_length is None
            assert result.max_length is None
            assert result.pattern is None
            assert result.choices is None

    # * test: from_config_entry_expanded
    def test_from_config_entry_expanded(self):
        '''
        Test that an expanded mapping preserves declared fields and defaults.
        '''

        # Read a fully declared expanded mapping and an empty expanded mapping.
        declared = {
            'type': 'float',
            'required': False,
            'default': 1.0,
            'description': 'Amount',
            'minimum': 0,
            'maximum': 10,
        }
        original_declared = dict(declared)
        first = ParameterSpecification.from_config_entry('b', declared)
        empty = {}
        second = ParameterSpecification.from_config_entry('c', empty)

        # Assert the declared fields on the first outcome.
        assert first.name == 'b'
        assert first.type == 'float'
        assert first.required is False
        assert first.default == 1.0
        assert first.description == 'Amount'
        assert first.minimum == 0.0
        assert first.maximum == 10.0

        # Assert the second outcome uses ordinary domain defaults.
        assert second.name == 'c'
        assert second.type == 'str'
        assert second.required is True
        assert second.default is None
        assert second.description is None
        assert second.minimum is None
        assert second.maximum is None
        assert second.min_length is None
        assert second.max_length is None
        assert second.pattern is None
        assert second.choices is None

        # Assert the input mappings were not mutated.
        assert declared == original_declared
        assert empty == {}

    # * test: from_config_entry_drops_equal_name
    def test_from_config_entry_drops_equal_name(self):
        '''
        Test that an equal inner name is dropped before construction.
        '''

        # Read an expanded mapping whose inner name matches the outer name.
        mapping = {'name': 'a', 'type': 'int'}
        result = ParameterSpecification.from_config_entry('a', mapping)

        # Assert the constructed fields and that the input mapping is unchanged.
        assert result.name == 'a'
        assert result.type == 'int'
        assert mapping == {'name': 'a', 'type': 'int'}

    # * test: from_config_entry_name_mismatch_raises
    def test_from_config_entry_name_mismatch_raises(self):
        '''
        Test that a conflicting inner name raises a model error.
        '''

        # Read an expanded mapping whose inner name conflicts with the outer name.
        with pytest.raises(ModelError) as exc_info:
            ParameterSpecification.from_config_entry('a', {'name': 'b', 'type': 'int'})

        # Assert the exact conflicting-name model error.
        assert_model_value_error(
            exc_info.value,
            "Parameter 'a' config value names a different parameter: 'b'.",
        )

    # * test: from_config_entry_none_inner_name_raises
    def test_from_config_entry_none_inner_name_raises(self):
        '''
        Test that an explicit null inner name is a conflicting name and raises a model error.
        '''

        # Read an expanded mapping whose inner name is explicitly null.
        with pytest.raises(ModelError) as exc_info:
            ParameterSpecification.from_config_entry('a', {'name': None, 'type': 'str'})

        # Assert the exact conflicting-name model error.
        assert_model_value_error(
            exc_info.value,
            "Parameter 'a' config value names a different parameter: None.",
        )

    # * test: from_config_entry_bad_value_raises
    def test_from_config_entry_bad_value_raises(self):
        '''
        Test that a non-string, non-mapping entry raises a model error.
        '''

        # Read invalid entry values and assert the exact invalid-entry messages.
        for value, type_name in ((None, 'NoneType'), (1, 'int'), ([], 'list')):
            with pytest.raises(ModelError) as exc_info:
                ParameterSpecification.from_config_entry('a', value)
            assert_model_value_error(
                exc_info.value,
                f"Parameter 'a' config value must be a type string or a mapping, not {type_name}.",
            )

    # * test: from_config_entry_unknown_type_raises
    def test_from_config_entry_unknown_type_raises(self):
        '''
        Test that an unknown type string raises a Pydantic validation error.
        '''

        # Read an unknown type string.
        with pytest.raises(ValidationError) as exc_info:
            ParameterSpecification.from_config_entry('a', 'unknown')

        # Assert the validation error names the type field and the unknown value.
        message = str(exc_info.value)
        assert 'type' in message
        assert 'unknown' in message

    # * test: to_config_value_shorthand_rule
    def test_to_config_value_shorthand_rule(self):
        '''
        Test that a required parameter with no extras emits the type string.
        '''

        # Emit the configuration value for each supported type with no extras.
        for type_name in ('str', 'int', 'float', 'bool', 'list', 'dict'):
            result = ParameterSpecification(name='a', type=type_name).to_config_value()
            assert result == type_name

    # * test: to_config_value_key_order
    def test_to_config_value_key_order(self):
        '''
        Test that an expanded configuration value emits type, default, required, then the constraint fields.
        '''

        # Emit the configuration value for a parameter with every optional field set.
        result = ParameterSpecification(
            name='a',
            type='str',
            default='',
            required=False,
            description='',
            minimum=0,
            maximum=0,
            min_length=0,
            max_length=0,
            pattern='',
            choices=[],
        ).to_config_value()

        # Assert the ordered mapping, including numeric bounds coerced to 0.0.
        assert result == {
            'type': 'str',
            'default': '',
            'required': False,
            'description': '',
            'minimum': 0.0,
            'maximum': 0.0,
            'min_length': 0,
            'max_length': 0,
            'pattern': '',
            'choices': [],
        }
        assert list(result.keys()) == [
            'type',
            'default',
            'required',
            'description',
            'minimum',
            'maximum',
            'min_length',
            'max_length',
            'pattern',
            'choices',
        ]

    # * test: to_config_value_falsy_defaults
    def test_to_config_value_falsy_defaults(self):
        '''
        Test that meaningful falsy defaults are retained in the configuration value.
        '''

        # Emit the configuration value for each falsy default.
        for default in (0, False, [], {}):
            result = ParameterSpecification(name='a', default=default).to_config_value()
            assert result == {'type': 'str', 'default': default}

    # * test: from_config_map_order
    def test_from_config_map_order(self):
        '''
        Test that a configuration map is read in insertion order, including a parameters key.
        '''

        # Read an insertion-ordered map and an empty map.
        result = ParameterSpecification.from_config_map(
            {'b': 'float', 'parameters': 'dict', 'a': {'type': 'int'}},
        )
        empty = ParameterSpecification.from_config_map({})

        # Assert the ordered names, types, and empty-map result.
        assert [param.name for param in result] == ['b', 'parameters', 'a']
        assert [param.type for param in result] == ['float', 'dict', 'int']
        assert all(isinstance(param, ParameterSpecification) for param in result)
        assert empty == []

    # * test: from_config_map_non_mapping_raises
    def test_from_config_map_non_mapping_raises(self):
        '''
        Test that a non-mapping configuration value raises a model error.
        '''

        # Read invalid configuration containers and assert the exact messages.
        for config, type_name in (([], 'list'), (None, 'NoneType'), ('a', 'str')):
            with pytest.raises(ModelError) as exc_info:
                ParameterSpecification.from_config_map(config)
            assert_model_value_error(
                exc_info.value,
                f'Parameter config map must be a mapping, not {type_name}.',
            )

    # * test: to_config_map_order
    def test_to_config_map_order(self):
        '''
        Test that a runtime list is written in list order and can be read back.
        '''

        # Write canonical runtime items in b-then-a order.
        items = [
            ParameterSpecification(name='b', type='float'),
            ParameterSpecification(name='a', type='int', required=False, default=0),
        ]
        written = ParameterSpecification.to_config_map(items)
        reread = ParameterSpecification.from_config_map(written)

        # Assert the written map, key order, and re-read fields.
        assert written == {
            'b': 'float',
            'a': {'type': 'int', 'default': 0, 'required': False},
        }
        assert list(written.keys()) == ['b', 'a']
        assert reread[0].name == 'b'
        assert reread[0].type == 'float'
        assert reread[0].required is True
        assert reread[0].default is None
        assert reread[1].name == 'a'
        assert reread[1].type == 'int'
        assert reread[1].required is False
        assert reread[1].default == 0

    # * test: to_config_map_empty
    def test_to_config_map_empty(self):
        '''
        Test that an empty runtime list writes an empty configuration map.
        '''

        # Write an empty runtime list.
        result = ParameterSpecification.to_config_map([])

        # Assert the written map is empty.
        assert result == {}

    # * test: keyed_by_name_order
    def test_keyed_by_name_order(self):
        '''
        Test that a list or tuple of mixed items is normalized in input order.
        '''

        # Normalize a list and a tuple containing an existing instance and a canonical mapping.
        existing = ParameterSpecification(name='a', type='int')
        mapping = {'name': 'b', 'type': 'bool'}
        original_mapping = dict(mapping)
        original_list = [existing, mapping]
        original_tuple = (existing, dict(mapping))
        from_list = ParameterSpecification.keyed_by_name(original_list)
        from_tuple = ParameterSpecification.keyed_by_name(original_tuple)
        empty_list = ParameterSpecification.keyed_by_name([])
        empty_tuple = ParameterSpecification.keyed_by_name(())

        # Assert list outcomes, types, instance identity, and unchanged inputs.
        assert isinstance(from_list, list)
        assert [param.name for param in from_list] == ['a', 'b']
        assert [param.type for param in from_list] == ['int', 'bool']
        assert from_list[0] is existing
        assert original_list == [existing, mapping]
        assert mapping == original_mapping

        # Assert the same fields for the tuple input and the empty containers.
        assert isinstance(from_tuple, list)
        assert [param.name for param in from_tuple] == ['a', 'b']
        assert [param.type for param in from_tuple] == ['int', 'bool']
        assert from_tuple[0] is existing
        assert original_tuple == (existing, {'name': 'b', 'type': 'bool'})
        assert empty_list == []
        assert empty_tuple == []

    # * test: keyed_by_name_repeated_name_raises
    def test_keyed_by_name_repeated_name_raises(self):
        '''
        Test that a repeated parameter name raises a model error.
        '''

        # Normalize dictionary, instance, and mixed pairs named a, including via to_config_map.
        instance = ParameterSpecification(name='a', type='int')
        mapping = {'name': 'a', 'type': 'str'}
        pairs = (
            [dict(mapping), dict(mapping)],
            [instance, ParameterSpecification(name='a', type='bool')],
            [instance, dict(mapping)],
        )
        for pair in pairs:
            with pytest.raises(ModelError) as exc_info:
                ParameterSpecification.keyed_by_name(pair)
            assert_model_value_error(
                exc_info.value,
                "Parameter 'a' is declared more than once.",
            )
            with pytest.raises(ModelError) as exc_info:
                ParameterSpecification.to_config_map(pair)
            assert_model_value_error(
                exc_info.value,
                "Parameter 'a' is declared more than once.",
            )

    # * test: keyed_by_name_dict_raises
    def test_keyed_by_name_dict_raises(self):
        '''
        Test that a non-list runtime container raises a model error.
        '''

        # Normalize invalid runtime containers, including via to_config_map.
        for parameters, type_name in (
            ({'a': 'int'}, 'dict'),
            ('a', 'str'),
            (None, 'NoneType'),
            (1, 'int'),
        ):
            message = f'Parameter runtime list must be a list, not {type_name}.'
            with pytest.raises(ModelError) as exc_info:
                ParameterSpecification.keyed_by_name(parameters)
            assert_model_value_error(exc_info.value, message)
            with pytest.raises(ModelError) as exc_info:
                ParameterSpecification.to_config_map(parameters)
            assert_model_value_error(exc_info.value, message)

    # * test: keyed_by_name_invalid_item
    def test_keyed_by_name_invalid_item(self):
        '''
        Test that an invalid runtime list item raises a model error.
        '''

        # Normalize lists of invalid items, including via to_config_map.
        for item, type_name in (('int', 'str'), (None, 'NoneType'), (1, 'int')):
            message = (
                'Parameter runtime list item must be a parameter specification '
                f'or a mapping, not {type_name}.'
            )
            with pytest.raises(ModelError) as exc_info:
                ParameterSpecification.keyed_by_name([item])
            assert_model_value_error(exc_info.value, message)
            with pytest.raises(ModelError) as exc_info:
                ParameterSpecification.to_config_map([item])
            assert_model_value_error(exc_info.value, message)

    # * test: keyed_by_name_canonical_validation
    def test_keyed_by_name_canonical_validation(self):
        '''
        Test that canonical mappings still raise ordinary Pydantic validation errors.
        '''

        # Normalize invalid canonical mappings and an expanded entry with an unexpected key.
        cases = (
            ([{'type': 'int'}], 'name'),
            ([{'name': 'a', 'type': 'unknown'}], 'type'),
            ([{'name': 'a', 'unexpected': True}], 'unexpected'),
        )
        for parameters, field_name in cases:
            with pytest.raises(ValidationError) as exc_info:
                ParameterSpecification.keyed_by_name(parameters)
            assert field_name in str(exc_info.value)

        # Read an expanded configuration entry with an unexpected key.
        with pytest.raises(ValidationError) as exc_info:
            ParameterSpecification.from_config_entry('a', {'unexpected': True})
        assert 'unexpected' in str(exc_info.value)

# ** tester: test_request_specification
@use_tester(
    type='domain',
    target_cls=RequestSpecification,
    equality_fields=[],
)
class TestRequestSpecification:
    '''
    Tests for RequestSpecification parameter normalization faces.
    '''

    # * test: normalizes_canonical
    def test_normalizes_canonical(self):
        '''
        Test that a canonical parameter list preserves order and types.
        '''

        # Validate a canonical list containing an existing instance and a mapping.
        existing = ParameterSpecification(name='a', type='int')
        spec = RequestSpecification.model_validate(
            {'parameters': [existing, {'name': 'b', 'type': 'bool'}]},
        )

        # Assert the preserved order and types.
        assert [param.name for param in spec.parameters] == ['a', 'b']
        assert [param.type for param in spec.parameters] == ['int', 'bool']
        assert spec.parameters[0] is existing

    # * test: normalizes_repeated_canonical_name_raises
    def test_normalizes_repeated_canonical_name_raises(self):
        '''
        Test that a repeated canonical name raises a model error.
        '''

        # Validate two canonical entries with the same name.
        with pytest.raises(ModelError) as exc_info:
            RequestSpecification.model_validate(
                {'parameters': [
                    {'name': 'a', 'type': 'int'},
                    {'name': 'a', 'type': 'str'},
                ]},
            )

        # Assert the exact duplicate-name model error.
        assert_model_value_error(
            exc_info.value,
            "Parameter 'a' is declared more than once.",
        )

    # * test: normalizes_key_named_parameters
    def test_normalizes_key_named_parameters(self):
        '''
        Test that a key named parameters is a declaration, and that an empty map is empty.
        '''

        # Validate shorthand and expanded declarations named parameters, plus an empty map.
        shorthand = RequestSpecification.model_validate({'parameters': 'dict'})
        expanded = RequestSpecification.model_validate(
            {'parameters': {'type': 'dict', 'required': False}},
        )
        empty = RequestSpecification.model_validate({})

        # Assert one parameter named parameters in each declared outcome.
        assert len(shorthand.parameters) == 1
        assert shorthand.parameters[0].name == 'parameters'
        assert shorthand.parameters[0].type == 'dict'
        assert shorthand.parameters[0].required is True
        assert len(expanded.parameters) == 1
        assert expanded.parameters[0].name == 'parameters'
        assert expanded.parameters[0].type == 'dict'
        assert expanded.parameters[0].required is False
        assert empty.parameters == []

    # * test: normalizes_non_dict_passthrough
    def test_normalizes_non_dict_passthrough(self):
        '''
        Test that non-dict input is returned unchanged by normalize_parameters.
        '''

        # Call the validator directly with non-dict shapes, including a non-dict mapping.
        mapping = MappingProxyType({'a': 'int'})
        for value in (None, ['a'], 'a', mapping):
            result = RequestSpecification.normalize_parameters(value)
            assert result == value
            assert result is value

    # * test: normalizes_bad_value_raises
    def test_normalizes_bad_value_raises(self):
        '''
        Test that an invalid configuration entry raises during request validation.
        '''

        # Validate a keyed map whose value is neither a string nor a mapping.
        with pytest.raises(ModelError) as exc_info:
            RequestSpecification.model_validate({'a': None})

        # Assert the exact invalid-entry model error.
        assert_model_value_error(
            exc_info.value,
            "Parameter 'a' config value must be a type string or a mapping, not NoneType.",
        )

    # * test: normalizes_name_mismatch_raises
    def test_normalizes_name_mismatch_raises(self):
        '''
        Test that a conflicting inner name raises during request validation.
        '''

        # Validate a keyed map whose expanded entry names a different parameter.
        with pytest.raises(ModelError) as exc_info:
            RequestSpecification.model_validate({'a': {'name': 'b'}})

        # Assert the exact conflicting-name model error.
        assert_model_value_error(
            exc_info.value,
            "Parameter 'a' config value names a different parameter: 'b'.",
        )

    # * test: normalizes_canonical_keeps_extra_key
    def test_normalizes_canonical_keeps_extra_key(self):
        '''
        Test that a canonical wrapper preserves extra keys for later rejection.
        '''

        # Validate a canonical wrapper that also carries an unexpected key.
        payload = {'parameters': [], 'unexpected': True}
        with pytest.raises(ValidationError) as exc_info:
            RequestSpecification.model_validate(payload)
        assert 'unexpected' in str(exc_info.value)

        # Call the validator directly and assert the payload is preserved and unchanged.
        result = RequestSpecification.normalize_parameters(payload)
        assert result == {'parameters': [], 'unexpected': True}
        assert payload == {'parameters': [], 'unexpected': True}

# ** tester: test_feature
@use_tester(
    type='domain',
    target_cls=Feature,
    equality_fields=[],
)
class TestFeature:
    '''
    Tests for Feature params_schema construction through parameter faces.
    '''

    # * test: params_schema_bad_value_raises
    def test_params_schema_bad_value_raises(self):
        '''
        Test that an invalid params_schema entry raises a model error.
        '''

        # Validate a feature whose params_schema entry is not a type string or mapping.
        with pytest.raises(ModelError) as exc_info:
            Feature.model_validate(
                {'id': 'calc.add', 'name': 'Add', 'params_schema': {'a': 5}},
            )

        # Assert the exact invalid-entry model error.
        assert_model_value_error(
            exc_info.value,
            "Parameter 'a' config value must be a type string or a mapping, not int.",
        )
