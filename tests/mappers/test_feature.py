"""Tiferet Feature Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.domain import INVALID_MODEL_ATTRIBUTE_ID, EventFeatureStep
from tiferet.mappers.feature import (
    EventFeatureStepAggregate,
    EventFeatureStepConfigObject,
    FeatureAggregate,
    FeatureConfigObject,
)
from tiferet.blueprints.tester import use_tester

# *** constants

# ** constant: feature_event_aggregate_sample_data
FEATURE_EVENT_AGGREGATE_SAMPLE_DATA = {
    'name': 'Test Event',
    'service_id': 'test_event_handler',
    'parameters': {'key': 'value'},
    'data_key': 'result',
    'pass_on_error': True,
    'condition': '$r.x > 0',
}

# ** constant: feature_event_equality_fields
FEATURE_EVENT_EQUALITY_FIELDS = [
    'name',
    'service_id',
    'parameters',
    'data_key',
    'pass_on_error',
    'condition',
]

# ** constant: feature_aggregate_sample_data
FEATURE_AGGREGATE_SAMPLE_DATA = {
    'name': 'Add Number',
    'group_id': 'calc',
    'feature_key': 'add_number',
    'id': 'calc.add_number',
    'description': 'Add Number',
}

# ** constant: feature_equality_fields
FEATURE_EQUALITY_FIELDS = [
    'id',
    'name',
    'group_id',
    'feature_key',
    'description',
    'steps',
]

# ** constant: step_tuple
def STEP_TUPLE(s):
    '''
    Normalize a single step (dict or domain object) into a comparable tuple.
    '''

    if isinstance(s, dict):
        return (
            s.get('name', ''),
            s.get('service_id', ''),
            tuple(sorted(s.get('parameters', {}).items())),
        )
    return (
        getattr(s, 'name', ''),
        getattr(s, 'service_id', ''),
        tuple(sorted((getattr(s, 'parameters', None) or {}).items())),
    )

# ** constant: feature_field_normalizers
FEATURE_FIELD_NORMALIZERS = {
    'steps': lambda steps: tuple(sorted(STEP_TUPLE(s) for s in (steps or []))),
}

# ** constant: test_feature_config_object_sample_data
TEST_FEATURE_CONFIG_OBJECT_SAMPLE_DATA = {
        'id': 'calc.add',
        'name': 'Add Number',
        'group_id': 'calc',
        'feature_key': 'add',
        'description': 'Adds one number to another',
        'steps': [{
            'name': 'Add a and b',
            'service_id': 'add_number_event',
            'params': {'precision': '2'},
        }],
    }

# ** constant: test_feature_config_object_aggregate_sample_data
TEST_FEATURE_CONFIG_OBJECT_AGGREGATE_SAMPLE_DATA = {
        'id': 'calc.add',
        'name': 'Add Number',
        'group_id': 'calc',
        'feature_key': 'add',
        'description': 'Adds one number to another',
        'steps': [{
            'name': 'Add a and b',
            'service_id': 'add_number_event',
            'parameters': {'precision': '2'},
        }],
    }

# *** tests

# ** test: feature_config_object_maps_params_schema
def test_feature_config_object_maps_params_schema():
    '''
    Test that FeatureConfigObject maps a keyed params_schema into the aggregate.
    '''

    # Create a YAML object with a keyed params_schema and map it.
    yaml_obj = FeatureConfigObject.model_validate(dict(
        id='calc.add',
        name='Add Number',
        group_id='calc',
        feature_key='add',
        steps=[],
        params_schema={'a': 'int', 'b': {'type': 'float', 'required': False, 'default': 1.0}},
    ))
    aggregate = yaml_obj.map()

    # Verify the params_schema mapped onto the aggregate with constraints intact.
    params = {p.name: p for p in aggregate.params_schema.parameters}
    assert params['a'].type == 'int'
    assert params['a'].required is True
    assert params['b'].type == 'float'
    assert params['b'].required is False
    assert params['b'].default == 1.0

# ** test: feature_config_object_serializes_params_schema_keyed
def test_feature_config_object_serializes_params_schema_keyed():
    '''
    Test that params_schema serializes to the ergonomic keyed mapping.
    '''

    # Build an aggregate carrying a params_schema.
    aggregate = FeatureConfigObject.model_validate(dict(
        id='calc.add',
        name='Add Number',
        group_id='calc',
        feature_key='add',
        steps=[],
        params_schema={'a': 'int', 'b': {'type': 'float', 'required': False, 'default': 1.0}},
    )).map()

    # Serialize the aggregate back to data form.
    data = FeatureConfigObject.from_model(aggregate).to_primitive('to_data')

    # Verify shorthand and expanded keyed forms.
    assert data['params_schema']['a'] == 'int'
    assert data['params_schema']['b']['type'] == 'float'
    assert data['params_schema']['b']['default'] == 1.0
    assert data['params_schema']['b']['required'] is False

# ** test: feature_config_object_params_schema_round_trip
def test_feature_config_object_params_schema_round_trip():
    '''
    Test that params_schema is preserved through a map/from_model round-trip.
    '''

    # Map then reverse-map the feature.
    aggregate = FeatureConfigObject.model_validate(dict(
        id='calc.add',
        name='Add Number',
        group_id='calc',
        feature_key='add',
        steps=[],
        params_schema={'a': 'int', 'b': {'type': 'float', 'required': False, 'default': 1.0}},
    )).map()
    aggregate2 = FeatureConfigObject.from_model(aggregate).map()

    # Verify the params survive the round-trip.
    params = {p.name: (p.type, p.required, p.default) for p in aggregate2.params_schema.parameters}
    assert params['a'] == ('int', True, None)
    assert params['b'] == ('float', False, 1.0)

# *** testers

# ** tester: event_feature_step_aggregate_tester
@use_tester(
    type='aggregate',
    target_cls=EventFeatureStepAggregate,
    sample_data=FEATURE_EVENT_AGGREGATE_SAMPLE_DATA,
    equality_fields=FEATURE_EVENT_EQUALITY_FIELDS,
    set_attribute_params=[
        ('name', 'Updated Event', None),
        ('service_id', 'updated_handler', None),
        ('data_key', 'new_key', None),
        ('condition', '$r.y != 0', None),
    ],
)
class EventFeatureStepAggregateTester:
    '''
    Tests for EventFeatureStepAggregate construction, set_attribute, and domain-specific mutations.
    '''

    # * test: new
    def test_new(self, test_ctx):
        '''Verify aggregate construction against declared expected data.'''

        test_ctx.assert_new()

    # * test: set_attribute
    def test_set_attribute(self, test_ctx):
        '''Verify declared set_attribute cases.'''

        test_ctx.assert_set_attribute()

    aggregate_cls = EventFeatureStepAggregate

    sample_data = FEATURE_EVENT_AGGREGATE_SAMPLE_DATA

    equality_fields = FEATURE_EVENT_EQUALITY_FIELDS

    set_attribute_params = [
        # valid
        ('name', 'Updated Event', None),
        ('service_id', 'updated_handler', None),
        ('data_key', 'new_key', None),
        ('condition', '$r.y != 0', None),
    ]

    # * test: set_pass_on_error
    def test_set_pass_on_error(self, test_ctx):
        '''
        Verifies string normalization ("false", "False", truthy).
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # String "false" should normalize to False.
        aggregate.set_pass_on_error('false')
        assert aggregate.pass_on_error is False

        # String "False" should normalize to False.
        aggregate.set_pass_on_error('False')
        assert aggregate.pass_on_error is False

        # Truthy string should normalize to True.
        aggregate.set_pass_on_error('true')
        assert aggregate.pass_on_error is True

        # Boolean True should remain True.
        aggregate.set_pass_on_error(True)
        assert aggregate.pass_on_error is True

    # * test: set_parameters
    def test_set_parameters(self, test_ctx):
        '''
        Verifies merge, None-prune, and no-op on None.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # Merge new parameters (new_key added, key updated).
        aggregate.set_parameters({'key': '10', 'new_key': '3'})
        assert aggregate.parameters == {'key': '10', 'new_key': '3'}

        # Prune keys with None values.
        aggregate.set_parameters({'new_key': None})
        assert aggregate.parameters == {'key': '10'}

        # None input is a no-op.
        aggregate.set_parameters(None)
        assert aggregate.parameters == {'key': '10'}

    # * test: set_attribute_delegation
    def test_set_attribute_delegation(self, test_ctx):
        '''
        Verifies delegation to specialized helpers.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # set_attribute for parameters should delegate to set_parameters.
        aggregate.set_attribute('parameters', {'y': '2'})
        assert 'y' in aggregate.parameters

        # set_attribute for pass_on_error should delegate to set_pass_on_error.
        aggregate.set_attribute('pass_on_error', 'false')
        assert aggregate.pass_on_error is False

        # set_attribute for other attributes should use setattr.
        aggregate.set_attribute('name', 'Renamed Event')
        assert aggregate.name == 'Renamed Event'

# ** tester: feature_aggregate_tester
@use_tester(
    type='aggregate',
    target_cls=FeatureAggregate,
    sample_data=FEATURE_AGGREGATE_SAMPLE_DATA,
    equality_fields=FEATURE_EQUALITY_FIELDS,
    field_normalizers=FEATURE_FIELD_NORMALIZERS,
    set_attribute_params=[
        ('name', 'Updated Feature', None),
        ('description', 'Updated description', None),
        ('invalid_attr', 'value', INVALID_MODEL_ATTRIBUTE_ID),
    ],
)
class FeatureAggregateTester:
    '''
    Tests for FeatureAggregate construction, set_attribute, and domain-specific mutations.
    '''

    # * test: new
    def test_new(self, test_ctx):
        '''Verify aggregate construction against declared expected data.'''

        test_ctx.assert_new()

    # * test: set_attribute
    def test_set_attribute(self, test_ctx):
        '''Verify declared set_attribute cases.'''

        test_ctx.assert_set_attribute()

    aggregate_cls = FeatureAggregate

    sample_data = FEATURE_AGGREGATE_SAMPLE_DATA

    equality_fields = FEATURE_EQUALITY_FIELDS

    field_normalizers = FEATURE_FIELD_NORMALIZERS

    set_attribute_params = [
        # valid
        ('name', 'Updated Feature', None),
        ('description', 'Updated description', None),
        # invalid
        ('invalid_attr', 'value', INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # * test: smart_derivation
    def test_smart_derivation(self, test_ctx):
        '''
        Verifies smart derivation (name -> feature_key -> id).
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # Assert smart derivation of feature_key and id.
        assert aggregate.feature_key == 'add_number'
        assert aggregate.id == 'calc.add_number'
        assert aggregate.description == 'Add Number'

    # * test: add_step
    def test_add_step(self, test_ctx):
        '''
        Verifies step append.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # Add a step.
        step = aggregate.add_step(
            name='Step One',
            service_id='step_one_event',
        )

        # Assert the step was appended.
        assert len(aggregate.steps) == 1
        assert aggregate.steps[0] is step
        assert step.name == 'Step One'
        assert step.service_id == 'step_one_event'

    # * test: add_step_position
    def test_add_step_position(self, test_ctx):
        '''
        Verifies step insertion at position 0.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # Add two steps, inserting the second at position 0.
        aggregate.add_step(name='Step One', service_id='step_one_event')
        inserted = aggregate.add_step(
            name='Step Zero',
            service_id='step_zero_event',
            position=0,
        )

        # Assert the step was inserted at position 0.
        assert len(aggregate.steps) == 2
        assert aggregate.steps[0] is inserted
        assert aggregate.steps[0].name == 'Step Zero'
        assert aggregate.steps[1].name == 'Step One'

    # * test: remove_step
    def test_remove_step(self, test_ctx):
        '''
        Verifies removal and invalid position handling.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # Add two steps.
        aggregate.add_step(name='Step One', service_id='step_one_event')
        aggregate.add_step(name='Step Two', service_id='step_two_event')

        # Remove the first step.
        removed = aggregate.remove_step(0)
        assert removed is not None
        assert removed.name == 'Step One'
        assert len(aggregate.steps) == 1

        # Attempt to remove at invalid positions.
        assert aggregate.remove_step(-1) is None
        assert aggregate.remove_step(99) is None

    # * test: reorder_step
    def test_reorder_step(self, test_ctx):
        '''
        Verifies move with clamping.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # Add three steps.
        aggregate.add_step(name='A', service_id='a_event')
        aggregate.add_step(name='B', service_id='b_event')
        aggregate.add_step(name='C', service_id='c_event')

        # Move step A (position 0) to position 2.
        moved = aggregate.reorder_step(0, 2)
        assert moved is not None
        assert moved.name == 'A'
        assert aggregate.steps[0].name == 'B'
        assert aggregate.steps[1].name == 'C'
        assert aggregate.steps[2].name == 'A'

    # * test: rename
    def test_rename(self, test_ctx):
        '''
        Verifies name update without id change.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # Record original id and rename the feature.
        original_id = aggregate.id
        aggregate.rename('New Name')

        # Assert the name was updated but the id was not.
        assert aggregate.name == 'New Name'
        assert aggregate.id == original_id

    # * test: set_description
    def test_set_description(self, test_ctx):
        '''
        Verifies set and clear.
        '''

        target = test_ctx.make_target()

        # Bind the generated target fixture to the established local name.
        aggregate = target

        # Set a description.
        aggregate.set_description('A custom description')
        assert aggregate.description == 'A custom description'

        # Clear the description.
        aggregate.set_description(None)
        assert aggregate.description is None

# ** tester: feature_config_object_tester
@use_tester(
    type='transfer_object',
    target_cls=FeatureConfigObject,
    aggregate_cls=FeatureAggregate,
    sample_data=TEST_FEATURE_CONFIG_OBJECT_SAMPLE_DATA,
    aggregate_sample_data=TEST_FEATURE_CONFIG_OBJECT_AGGREGATE_SAMPLE_DATA,
    equality_fields=FEATURE_EQUALITY_FIELDS,
    field_normalizers=FEATURE_FIELD_NORMALIZERS,
)
class FeatureConfigObjectTester:
    '''
    Tests for FeatureConfigObject mapping, round-trip, and nested EventFeatureStepConfigObject.
    '''

    # * test: map
    def test_map(self, test_ctx):
        '''Verify transfer construction and mapping to the declared aggregate.'''

        test_ctx.assert_map()

    # * test: from_model
    def test_from_model(self, test_ctx):
        '''Verify aggregate conversion to the declared transfer-object type.'''

        test_ctx.assert_from_model()

    # * test: round_trip
    def test_round_trip(self, test_ctx):
        '''Verify aggregate conversion through the transfer object and back.'''

        test_ctx.assert_round_trip()

    transfer_cls = FeatureConfigObject
    aggregate_cls = FeatureAggregate

    # YAML-format sample data (steps with params alias and service_id).
    sample_data = TEST_FEATURE_CONFIG_OBJECT_SAMPLE_DATA

    # Aggregate-format expected data (defaults filled in).
    aggregate_sample_data = TEST_FEATURE_CONFIG_OBJECT_AGGREGATE_SAMPLE_DATA

    equality_fields = FEATURE_EQUALITY_FIELDS

    field_normalizers = FEATURE_FIELD_NORMALIZERS

    # ** constant: feature_event_sample_data
    feature_event_sample_data = {
        'name': 'Test Event',
        'service_id': 'test_event_handler',
        'params': {'key': 'value'},
        'data_key': 'result',
        'pass_on_error': True,
        'condition': '$r.x > 0',
    }

    # * test: feature_event_yaml_map_basic
    def test_feature_event_yaml_map_basic(self):
        '''
        Test mapping a EventFeatureStepConfigObject to a EventFeatureStepAggregate.
        '''

        # Create a YAML object and map it.
        yaml_obj = EventFeatureStepConfigObject.model_validate(
            self.feature_event_sample_data,
        )
        event = yaml_obj.map()

        # Verify the mapped entity.
        assert isinstance(event, EventFeatureStepAggregate)
        assert event.name == 'Test Event'
        assert event.service_id == 'test_event_handler'
        assert event.parameters == {'key': 'value'}
        assert event.data_key == 'result'
        assert event.pass_on_error is True

    # * test: feature_event_yaml_params_alias
    def test_feature_event_yaml_params_alias(self):
        '''
        Test that the "params" alias is correctly deserialized.
        '''

        # Create YAML object using the 'params' alias.
        yaml_obj = EventFeatureStepConfigObject.model_validate(dict(
            name='Alias Event',
            service_id='alias_handler',
            params={'alias_key': 'value'},
        ))
        event = yaml_obj.map()

        # Verify aliased parameters were deserialized correctly.
        assert event.parameters == {'alias_key': 'value'}

    # * test: feature_event_yaml_map_with_condition
    def test_feature_event_yaml_map_with_condition(self):
        '''
        Test mapping a EventFeatureStepConfigObject with a condition field.
        '''

        # Create a YAML object with a condition and map it.
        yaml_obj = EventFeatureStepConfigObject.model_validate(dict(
            name='Conditional Event',
            service_id='conditional_handler',
            condition='$r.b != 0',
        ))
        event = yaml_obj.map()

        # Verify the condition is preserved.
        assert isinstance(event, EventFeatureStepAggregate)
        assert event.condition == '$r.b != 0'

    # * test: feature_event_yaml_from_model
    def test_feature_event_yaml_from_model(self):
        '''
        Test that EventFeatureStepConfigObject can be created from a EventFeatureStep model.
        '''

        # Create a EventFeatureStep model via direct constructor.
        model = EventFeatureStep(
            name='Test Event',
            service_id='test_event_handler',
            parameters={'key': 'value'},
            data_key='result',
            pass_on_error=True,
        )

        # Create a YAML object from the model.
        yaml_obj = EventFeatureStepConfigObject.from_model(model)

        # Verify the YAML object has the correct values.
        assert isinstance(yaml_obj, EventFeatureStepConfigObject)
        assert yaml_obj.name == model.name
        assert yaml_obj.service_id == model.service_id
        assert yaml_obj.parameters == model.parameters

    # * test: feature_event_yaml_middleware_round_trip
    def test_feature_event_yaml_middleware_round_trip(self):
        '''
        Test that middleware is preserved through EventFeatureStepConfigObject map/from_model round-trip.
        '''

        # Create a YAML object with middleware and map to aggregate.
        yaml_obj = EventFeatureStepConfigObject.model_validate(dict(
            name='Middleware Event',
            service_id='mw_handler',
            middleware=['timing_middleware', 'audit_middleware'],
        ))
        event = yaml_obj.map()

        # Verify the middleware list is preserved on the aggregate.
        assert event.middleware == ['timing_middleware', 'audit_middleware']

        # Round-trip: aggregate -> ConfigObject -> re-map.
        yaml_obj2 = EventFeatureStepConfigObject.from_model(event)
        event2 = yaml_obj2.map()
        assert event2.middleware == ['timing_middleware', 'audit_middleware']

    # * test: feature_yaml_middleware_round_trip
    def test_feature_yaml_middleware_round_trip(self):
        '''
        Test that feature-level middleware is preserved through FeatureConfigObject round-trip.
        '''

        # Create a YAML object with feature-level middleware.
        yaml_obj = FeatureConfigObject.model_validate(dict(
            id='calc.add',
            name='Add Number',
            group_id='calc',
            feature_key='add',
            middleware=['timing_middleware'],
            steps=[],
        ))
        aggregate = yaml_obj.map()

        # Verify feature-level middleware on the aggregate.
        assert aggregate.middleware == ['timing_middleware']

        # Round-trip: aggregate -> ConfigObject -> re-map.
        yaml_obj2 = FeatureConfigObject.from_model(aggregate)
        aggregate2 = yaml_obj2.map()
        assert aggregate2.middleware == ['timing_middleware']

    # * test: feature_aggregate_add_step_with_middleware
    def test_feature_aggregate_add_step_with_middleware(self):
        '''
        Test that add_step accepts and stores a middleware list.
        '''

        # Create a FeatureAggregate and add a step with middleware.
        agg = FeatureAggregate(name='Add Number', group_id='calc')
        step = agg.add_step(
            name='Step One',
            service_id='step_one_event',
            middleware=['timing_middleware'],
        )

        # Verify the middleware is attached to the step.
        assert step.middleware == ['timing_middleware']
        assert agg.steps[0].middleware == ['timing_middleware']
