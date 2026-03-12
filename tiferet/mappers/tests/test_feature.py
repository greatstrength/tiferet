"""Tiferet Feature Mapper Tests"""

# *** imports

# ** app
from ...domain import DomainObject, FeatureEvent
from ...events import a
from ..settings import TransferObject
from ..feature import (
    FeatureEventAggregate,
    FeatureEventYamlObject,
    FeatureAggregate,
    FeatureYamlObject,
)
from .settings import AggregateTestBase, TransferObjectTestBase


# *** constants

# ** constant: feature_event_aggregate_sample_data
FEATURE_EVENT_AGGREGATE_SAMPLE_DATA = {
    'name': 'Test Event',
    'service_id': 'test_event_handler',
    'parameters': {'key': 'value'},
    'data_key': 'result',
    'pass_on_error': True,
}

# ** constant: feature_event_equality_fields
FEATURE_EVENT_EQUALITY_FIELDS = [
    'name',
    'service_id',
    'parameters',
    'data_key',
    'pass_on_error',
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


# *** classes

# ** class: TestFeatureEventAggregate
class TestFeatureEventAggregate(AggregateTestBase):
    '''
    Tests for FeatureEventAggregate construction, set_attribute, and domain-specific mutations.
    '''

    aggregate_cls = FeatureEventAggregate

    sample_data = FEATURE_EVENT_AGGREGATE_SAMPLE_DATA

    equality_fields = FEATURE_EVENT_EQUALITY_FIELDS

    set_attribute_params = [
        # valid
        ('name', 'Updated Event', None),
        ('service_id', 'updated_handler', None),
        ('data_key', 'new_key', None),
    ]

    # *** domain-specific mutation tests

    # ** test: set_pass_on_error
    def test_set_pass_on_error(self, aggregate):
        '''
        Verifies string normalization ("false", "False", truthy).
        '''

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

    # ** test: set_parameters
    def test_set_parameters(self, aggregate):
        '''
        Verifies merge, None-prune, and no-op on None.
        '''

        # Merge new parameters (new_key added, key updated).
        aggregate.set_parameters({'key': '10', 'new_key': '3'})
        assert aggregate.parameters == {'key': '10', 'new_key': '3'}

        # Prune keys with None values.
        aggregate.set_parameters({'new_key': None})
        assert aggregate.parameters == {'key': '10'}

        # None input is a no-op.
        aggregate.set_parameters(None)
        assert aggregate.parameters == {'key': '10'}

    # ** test: set_attribute_delegation
    def test_set_attribute_delegation(self, aggregate):
        '''
        Verifies delegation to specialized helpers.
        '''

        # set_attribute for parameters should delegate to set_parameters.
        aggregate.set_attribute('parameters', {'y': '2'})
        assert 'y' in aggregate.parameters

        # set_attribute for pass_on_error should delegate to set_pass_on_error.
        aggregate.set_attribute('pass_on_error', 'false')
        assert aggregate.pass_on_error is False

        # set_attribute for other attributes should use setattr.
        aggregate.set_attribute('name', 'Renamed Event')
        assert aggregate.name == 'Renamed Event'


# ** class: TestFeatureAggregate
class TestFeatureAggregate(AggregateTestBase):
    '''
    Tests for FeatureAggregate construction, set_attribute, and domain-specific mutations.
    '''

    aggregate_cls = FeatureAggregate

    sample_data = FEATURE_AGGREGATE_SAMPLE_DATA

    equality_fields = FEATURE_EQUALITY_FIELDS

    field_normalizers = FEATURE_FIELD_NORMALIZERS

    set_attribute_params = [
        # valid
        ('name', 'Updated Feature', None),
        ('description', 'Updated description', None),
        # invalid
        ('invalid_attr', 'value', a.const.INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> FeatureAggregate:
        '''
        Override to use FeatureAggregate.new() custom factory.
        '''

        # Create an aggregate using the custom factory.
        return FeatureAggregate.new(**(data or self.sample_data))

    # *** domain-specific tests

    # ** test: smart_derivation
    def test_smart_derivation(self, aggregate):
        '''
        Verifies smart derivation (name -> feature_key -> id).
        '''

        # Assert smart derivation of feature_key and id.
        assert aggregate.feature_key == 'add_number'
        assert aggregate.id == 'calc.add_number'
        assert aggregate.description == 'Add Number'

    # ** test: add_step
    def test_add_step(self, aggregate):
        '''
        Verifies step append.
        '''

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

    # ** test: add_step_position
    def test_add_step_position(self, aggregate):
        '''
        Verifies step insertion at position 0.
        '''

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

    # ** test: remove_step
    def test_remove_step(self, aggregate):
        '''
        Verifies removal and invalid position handling.
        '''

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

    # ** test: reorder_step
    def test_reorder_step(self, aggregate):
        '''
        Verifies move with clamping.
        '''

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

    # ** test: rename
    def test_rename(self, aggregate):
        '''
        Verifies name update without id change.
        '''

        # Record original id and rename the feature.
        original_id = aggregate.id
        aggregate.rename('New Name')

        # Assert the name was updated but the id was not.
        assert aggregate.name == 'New Name'
        assert aggregate.id == original_id

    # ** test: set_description
    def test_set_description(self, aggregate):
        '''
        Verifies set and clear.
        '''

        # Set a description.
        aggregate.set_description('A custom description')
        assert aggregate.description == 'A custom description'

        # Clear the description.
        aggregate.set_description(None)
        assert aggregate.description is None


# ** class: TestFeatureYamlObject
class TestFeatureYamlObject(TransferObjectTestBase):
    '''
    Tests for FeatureYamlObject mapping, round-trip, and nested FeatureEventYamlObject.
    '''

    transfer_cls = FeatureYamlObject
    aggregate_cls = FeatureAggregate

    # YAML-format sample data (steps with params alias and service_id).
    sample_data = {
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

    # Aggregate-format expected data (defaults filled in).
    aggregate_sample_data = {
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

    equality_fields = FEATURE_EQUALITY_FIELDS

    field_normalizers = FEATURE_FIELD_NORMALIZERS

    # * method: make_aggregate
    def make_aggregate(self, data: dict = None) -> FeatureAggregate:
        '''
        Override to use FeatureAggregate.new() custom factory.
        '''

        # Create an aggregate using the custom factory.
        data = data or self.aggregate_sample_data

        # Build steps as FeatureEventAggregate instances.
        steps = [
            FeatureEventAggregate.new(**step)
            for step in data.get('steps', [])
        ]

        # Create the feature aggregate with mapped steps.
        return FeatureAggregate.new(
            **{k: v for k, v in data.items() if k != 'steps'},
            steps=steps,
        )

    # *** child mapper: FeatureEventYamlObject

    # ** constant: feature_event_sample_data
    feature_event_sample_data = {
        'name': 'Test Event',
        'service_id': 'test_event_handler',
        'params': {'key': 'value'},
        'data_key': 'result',
        'pass_on_error': True,
    }

    # ** test: feature_event_yaml_map_basic
    def test_feature_event_yaml_map_basic(self):
        '''
        Test mapping a FeatureEventYamlObject to a FeatureEventAggregate.
        '''

        # Create a YAML object and map it.
        yaml_obj = TransferObject.from_data(
            FeatureEventYamlObject,
            **self.feature_event_sample_data,
        )
        event = yaml_obj.map()

        # Verify the mapped entity.
        assert isinstance(event, FeatureEventAggregate)
        assert event.name == 'Test Event'
        assert event.service_id == 'test_event_handler'
        assert event.parameters == {'key': 'value'}
        assert event.data_key == 'result'
        assert event.pass_on_error is True

    # ** test: feature_event_yaml_params_alias
    def test_feature_event_yaml_params_alias(self):
        '''
        Test that the "params" alias is correctly deserialized.
        '''

        # Create YAML object using the 'params' alias.
        yaml_obj = TransferObject.from_data(
            FeatureEventYamlObject,
            name='Alias Event',
            service_id='alias_handler',
            params={'alias_key': 'value'},
        )
        event = yaml_obj.map()

        # Verify aliased parameters were deserialized correctly.
        assert event.parameters == {'alias_key': 'value'}

    # ** test: feature_event_yaml_from_model
    def test_feature_event_yaml_from_model(self):
        '''
        Test that FeatureEventYamlObject can be created from a FeatureEvent model.
        '''

        # Create a FeatureEvent model.
        model = DomainObject.new(
            FeatureEvent,
            name='Test Event',
            service_id='test_event_handler',
            parameters={'key': 'value'},
            data_key='result',
            pass_on_error=True,
        )

        # Create a YAML object from the model.
        yaml_obj = FeatureEventYamlObject.from_model(model)

        # Verify the YAML object has the correct values.
        assert isinstance(yaml_obj, FeatureEventYamlObject)
        assert yaml_obj.name == model.name
        assert yaml_obj.service_id == model.service_id
        assert yaml_obj.parameters == model.parameters
