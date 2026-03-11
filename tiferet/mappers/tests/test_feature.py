"""Tiferet Feature Mapper Tests"""

# *** imports

# ** app
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
    'parameters': {'a': '1', 'b': '2'},
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
    'id': 'calc.add',
    'name': 'Add Number',
    'group_id': 'calc',
    'feature_key': 'add',
    'description': 'Adds one number to another',
    'steps': [
        {
            'name': 'Add a and b',
            'service_id': 'add_number_event',
            'parameters': {'precision': '2'},
        },
    ],
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
    '''Normalize a step (dict or domain object) into a comparable tuple.'''

    if isinstance(s, dict):
        return (
            s.get('name'),
            s.get('service_id'),
            tuple(sorted(s.get('parameters', {}).items())),
            s.get('data_key'),
            s.get('pass_on_error', False),
        )
    return (
        s.name,
        s.service_id,
        tuple(sorted((s.parameters or {}).items())),
        s.data_key,
        s.pass_on_error or False,
    )

# ** constant: feature_field_normalizers
FEATURE_FIELD_NORMALIZERS = {
    'steps': lambda steps: tuple(sorted(STEP_TUPLE(s) for s in (steps or []))),
}


# *** classes

# ** class: TestFeatureEventAggregate
class TestFeatureEventAggregate(AggregateTestBase):
    '''Tests for FeatureEventAggregate construction, set_attribute, and domain-specific mutations.'''

    aggregate_cls = FeatureEventAggregate
    sample_data = FEATURE_EVENT_AGGREGATE_SAMPLE_DATA
    equality_fields = FEATURE_EVENT_EQUALITY_FIELDS

    set_attribute_params = [
        ('name',       'Renamed Event', None),
        ('service_id', 'new_handler',   None),
    ]

    # *** domain-specific mutation tests

    # ** test: set_pass_on_error
    def test_set_pass_on_error(self, aggregate):
        '''Verifies string normalization ("false", "False", truthy).'''

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
        '''Verifies merge, None-prune, and no-op on None.'''

        # Merge new parameters (a updated, c added).
        aggregate.set_parameters({'a': '10', 'c': '3'})
        assert aggregate.parameters == {'a': '10', 'b': '2', 'c': '3'}

        # Prune keys with None values.
        aggregate.set_parameters({'b': None})
        assert aggregate.parameters == {'a': '10', 'c': '3'}

        # None input is a no-op.
        aggregate.set_parameters(None)
        assert aggregate.parameters == {'a': '10', 'c': '3'}

    # ** test: set_attribute_delegation
    def test_set_attribute_delegation(self, aggregate):
        '''Verifies delegation to specialized helpers.'''

        # set_attribute for parameters should delegate to set_parameters.
        aggregate.set_attribute('parameters', {'c': '3'})
        assert aggregate.parameters == {'a': '1', 'b': '2', 'c': '3'}

        # set_attribute for pass_on_error should delegate to set_pass_on_error.
        aggregate.set_attribute('pass_on_error', 'false')
        assert aggregate.pass_on_error is False

        # set_attribute for other attributes should use setattr.
        aggregate.set_attribute('name', 'Renamed Event')
        assert aggregate.name == 'Renamed Event'


# ** class: TestFeatureAggregate
class TestFeatureAggregate(AggregateTestBase):
    '''Tests for FeatureAggregate construction, set_attribute, and domain-specific mutations.'''

    aggregate_cls = FeatureAggregate
    sample_data = FEATURE_AGGREGATE_SAMPLE_DATA
    equality_fields = FEATURE_EQUALITY_FIELDS
    field_normalizers = FEATURE_FIELD_NORMALIZERS

    set_attribute_params = [
        ('name',         'Updated Name',   None),
        ('description',  'New Description', None),
        ('invalid_attr', 'value',           a.const.INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # * method: make_aggregate
    def make_aggregate(self, data=None):
        '''Override for FeatureAggregate.new() custom signature.'''

        # Create an aggregate using the custom factory.
        d = (data if data is not None else self.sample_data).copy()
        return FeatureAggregate.new(**d)

    # *** domain-specific mutation tests

    # ** test: smart_derivation
    def test_smart_derivation(self):
        '''Verifies smart derivation (name → feature_key → id).'''

        # Create a feature aggregate with only name and group_id.
        feature = FeatureAggregate.new(name='Add Number', group_id='calc')

        # Assert smart derivation of feature_key and id.
        assert feature.feature_key == 'add_number'
        assert feature.id == 'calc.add_number'
        assert feature.description == 'Add Number'

    # ** test: add_step
    def test_add_step(self):
        '''Verifies step append.'''

        # Create a feature aggregate.
        feature = FeatureAggregate.new(name='Test Feature', group_id='test')

        # Add a step.
        step = feature.add_step(name='Step One', service_id='step_one_event')

        # Assert the step was appended.
        assert len(feature.steps) == 1
        assert feature.steps[0] is step
        assert step.name == 'Step One'
        assert step.service_id == 'step_one_event'

    # ** test: add_step_position
    def test_add_step_position(self):
        '''Verifies step insertion at position 0.'''

        # Create a feature aggregate with an existing step.
        feature = FeatureAggregate.new(name='Test Feature', group_id='test')
        feature.add_step(name='Step One', service_id='step_one_event')

        # Insert a new step at position 0.
        inserted = feature.add_step(
            name='Step Zero',
            service_id='step_zero_event',
            position=0,
        )

        # Assert the step was inserted at position 0.
        assert len(feature.steps) == 2
        assert feature.steps[0] is inserted
        assert feature.steps[0].name == 'Step Zero'
        assert feature.steps[1].name == 'Step One'

    # ** test: remove_step
    def test_remove_step(self):
        '''Verifies removal and invalid position handling.'''

        # Create a feature aggregate with steps.
        feature = FeatureAggregate.new(name='Test Feature', group_id='test')
        feature.add_step(name='Step One', service_id='step_one_event')
        feature.add_step(name='Step Two', service_id='step_two_event')

        # Remove the first step.
        removed = feature.remove_step(0)
        assert removed is not None
        assert removed.name == 'Step One'
        assert len(feature.steps) == 1

        # Attempt to remove at an invalid position.
        assert feature.remove_step(-1) is None
        assert feature.remove_step(99) is None

    # ** test: reorder_step
    def test_reorder_step(self):
        '''Verifies move with clamping.'''

        # Create a feature aggregate with steps.
        feature = FeatureAggregate.new(name='Test Feature', group_id='test')
        feature.add_step(name='A', service_id='a_event')
        feature.add_step(name='B', service_id='b_event')
        feature.add_step(name='C', service_id='c_event')

        # Move step A (position 0) to position 2.
        moved = feature.reorder_step(0, 2)
        assert moved is not None
        assert moved.name == 'A'
        assert feature.steps[0].name == 'B'
        assert feature.steps[1].name == 'C'
        assert feature.steps[2].name == 'A'

    # ** test: rename
    def test_rename(self, aggregate):
        '''Verifies name update without id change.'''

        # Record the original ID.
        original_id = aggregate.id

        # Rename the feature.
        aggregate.rename('New Name')

        # Assert the name was updated but the id was not.
        assert aggregate.name == 'New Name'
        assert aggregate.id == original_id

    # ** test: set_description
    def test_set_description(self, aggregate):
        '''Verifies set and clear.'''

        # Set a description.
        aggregate.set_description('A custom description')
        assert aggregate.description == 'A custom description'

        # Clear the description.
        aggregate.set_description(None)
        assert aggregate.description is None


# ** class: TestFeatureYamlObject
class TestFeatureYamlObject(TransferObjectTestBase):
    '''Tests for FeatureYamlObject mapping, round-trip, and nested FeatureEventYamlObject.'''

    transfer_cls = FeatureYamlObject
    aggregate_cls = FeatureAggregate

    # YAML-format sample data (params alias, steps nested).
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

    # Aggregate-format expected data (parameters, not params).
    aggregate_sample_data = FEATURE_AGGREGATE_SAMPLE_DATA
    equality_fields = FEATURE_EQUALITY_FIELDS
    field_normalizers = FEATURE_FIELD_NORMALIZERS

    # * method: make_aggregate
    def make_aggregate(self, data=None):
        '''Override for FeatureAggregate.new() custom signature.'''

        # Create an aggregate using the custom factory.
        d = (data if data is not None else self.aggregate_sample_data).copy()
        return FeatureAggregate.new(**d)

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
        '''Test FeatureEventYamlObject mapping to FeatureEventAggregate.'''

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
        '''Test that the "params" alias resolves to parameters correctly.'''

        # Create YAML object using the 'params' alias.
        yaml_obj = TransferObject.from_data(
            FeatureEventYamlObject,
            name='Alias Test',
            service_id='alias_handler',
            params={'alias_key': 'alias_value'},
        )

        # Assert the alias resolved correctly.
        assert yaml_obj.parameters == {'alias_key': 'alias_value'}

    # ** test: feature_event_yaml_from_model
    def test_feature_event_yaml_from_model(self):
        '''Test that FeatureEventYamlObject can be created from a FeatureEvent model.'''

        # Create a FeatureEventAggregate model.
        event = FeatureEventAggregate.new(
            name='Test Event',
            service_id='test_handler',
            parameters={'p': 'v'},
        )

        # Create a YAML object from the model.
        yaml_obj = FeatureEventYamlObject.from_model(event)

        # Verify the YAML object has the correct values.
        assert isinstance(yaml_obj, FeatureEventYamlObject)
        assert yaml_obj.name == event.name
        assert yaml_obj.service_id == event.service_id
        assert yaml_obj.parameters == event.parameters
