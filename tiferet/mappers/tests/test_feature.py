"""Tiferet Feature Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import (
    TransferObject,
)
from ..feature import (
    FeatureEventAggregate,
    FeatureEventYamlObject,
    FeatureAggregate,
    FeatureYamlObject,
)
from ...domain import (
    Feature,
    FeatureEvent,
)

# *** fixtures

# ** fixture: feature_event_yaml_object
@pytest.fixture
def feature_event_yaml_object() -> FeatureEventYamlObject:
    '''
    Provides a feature event YAML object fixture with pass_on_error,
    data_key, and params alias.

    :return: The feature event YAML object instance.
    :rtype: FeatureEventYamlObject
    '''

    # Create and return a feature event YAML object.
    return TransferObject.from_data(
        FeatureEventYamlObject,
        name='Test Event',
        attribute_id='test_event_handler',
        params={'key': 'value'},
        data_key='result',
        pass_on_error=True,
    )


# ** fixture: feature_yaml_object
@pytest.fixture
def feature_yaml_object() -> FeatureYamlObject:
    '''
    Provides a feature YAML object fixture with one step containing params.

    :return: The feature YAML object instance.
    :rtype: FeatureYamlObject
    '''

    # Create and return a feature YAML object.
    return TransferObject.from_data(
        FeatureYamlObject,
        id='calc.add',
        name='Add Number',
        group_id='calc',
        feature_key='add',
        description='Adds one number to another',
        steps=[{
            'name': 'Add a and b',
            'attribute_id': 'add_number_event',
            'params': {'precision': '2'},
        }],
    )


# *** tests

# ** test: feature_event_data_init
def test_feature_event_data_init(feature_event_yaml_object: FeatureEventYamlObject):
    '''
    Verifies from_data() initialization including params alias.

    :param feature_event_yaml_object: The feature event YAML object.
    :type feature_event_yaml_object: FeatureEventYamlObject
    '''

    # Assert basic attributes.
    assert feature_event_yaml_object.name == 'Test Event'
    assert feature_event_yaml_object.attribute_id == 'test_event_handler'
    assert feature_event_yaml_object.data_key == 'result'
    assert feature_event_yaml_object.pass_on_error is True

    # Assert the params alias resolved correctly.
    assert feature_event_yaml_object.parameters == {'key': 'value'}


# ** test: feature_event_data_map
def test_feature_event_data_map(feature_event_yaml_object: FeatureEventYamlObject):
    '''
    Verifies map() produces a FeatureEvent with correct fields.

    :param feature_event_yaml_object: The feature event YAML object.
    :type feature_event_yaml_object: FeatureEventYamlObject
    '''

    # Map the feature event data to a feature event aggregate.
    event = feature_event_yaml_object.map()

    # Assert the mapped object is a FeatureEventAggregate.
    assert isinstance(event, FeatureEventAggregate)
    assert event.name == 'Test Event'
    assert event.attribute_id == 'test_event_handler'
    assert event.parameters == {'key': 'value'}
    assert event.data_key == 'result'
    assert event.pass_on_error is True


# ** test: feature_data_from_data
def test_feature_data_from_data(feature_yaml_object: FeatureYamlObject):
    '''
    Verifies nested steps initialization.

    :param feature_yaml_object: The feature YAML object.
    :type feature_yaml_object: FeatureYamlObject
    '''

    # Assert basic attributes.
    assert feature_yaml_object.id == 'calc.add'
    assert feature_yaml_object.name == 'Add Number'
    assert feature_yaml_object.group_id == 'calc'
    assert feature_yaml_object.feature_key == 'add'
    assert feature_yaml_object.description == 'Adds one number to another'

    # Assert the steps were initialized as FeatureEventYamlObject instances.
    assert len(feature_yaml_object.steps) == 1
    step = feature_yaml_object.steps[0]
    assert isinstance(step, FeatureEventYamlObject)
    assert step.name == 'Add a and b'
    assert step.attribute_id == 'add_number_event'
    assert step.parameters == {'precision': '2'}


# ** test: feature_data_map
def test_feature_data_map(feature_yaml_object: FeatureYamlObject):
    '''
    Verifies map() produces a FeatureAggregate with nested steps.

    :param feature_yaml_object: The feature YAML object.
    :type feature_yaml_object: FeatureYamlObject
    '''

    # Map the feature data to a feature aggregate.
    feature = feature_yaml_object.map()

    # Assert the mapped object is a FeatureAggregate.
    assert isinstance(feature, FeatureAggregate)
    assert feature.id == 'calc.add'
    assert feature.name == 'Add Number'
    assert feature.group_id == 'calc'
    assert feature.feature_key == 'add'

    # Assert nested steps were mapped correctly.
    assert len(feature.steps) == 1
    step = feature.steps[0]
    assert isinstance(step, FeatureEventAggregate)
    assert step.name == 'Add a and b'
    assert step.attribute_id == 'add_number_event'
    assert step.parameters == {'precision': '2'}


# ** test: feature_aggregate_new
def test_feature_aggregate_new():
    '''
    Verifies smart derivation (name → feature_key → id).
    '''

    # Create a feature aggregate with only name and group_id.
    feature = FeatureAggregate.new(
        name='Add Number',
        group_id='calc',
    )

    # Assert smart derivation of feature_key and id.
    assert feature.feature_key == 'add_number'
    assert feature.id == 'calc.add_number'
    assert feature.description == 'Add Number'


# ** test: feature_aggregate_add_step
def test_feature_aggregate_add_step():
    '''
    Verifies step append.
    '''

    # Create a feature aggregate.
    feature = FeatureAggregate.new(
        name='Test Feature',
        group_id='test',
    )

    # Add a step.
    step = feature.add_step(
        name='Step One',
        attribute_id='step_one_event',
    )

    # Assert the step was appended.
    assert len(feature.steps) == 1
    assert feature.steps[0] is step
    assert step.name == 'Step One'
    assert step.attribute_id == 'step_one_event'


# ** test: feature_aggregate_add_step_position
def test_feature_aggregate_add_step_position():
    '''
    Verifies step insertion at position 0.
    '''

    # Create a feature aggregate with an existing step.
    feature = FeatureAggregate.new(
        name='Test Feature',
        group_id='test',
    )
    feature.add_step(name='Step One', attribute_id='step_one_event')

    # Insert a new step at position 0.
    inserted = feature.add_step(
        name='Step Zero',
        attribute_id='step_zero_event',
        position=0,
    )

    # Assert the step was inserted at position 0.
    assert len(feature.steps) == 2
    assert feature.steps[0] is inserted
    assert feature.steps[0].name == 'Step Zero'
    assert feature.steps[1].name == 'Step One'


# ** test: feature_aggregate_remove_step
def test_feature_aggregate_remove_step():
    '''
    Verifies removal and invalid position handling.
    '''

    # Create a feature aggregate with steps.
    feature = FeatureAggregate.new(
        name='Test Feature',
        group_id='test',
    )
    feature.add_step(name='Step One', attribute_id='step_one_event')
    feature.add_step(name='Step Two', attribute_id='step_two_event')

    # Remove the first step.
    removed = feature.remove_step(0)
    assert removed is not None
    assert removed.name == 'Step One'
    assert len(feature.steps) == 1

    # Attempt to remove at an invalid position.
    assert feature.remove_step(-1) is None
    assert feature.remove_step(99) is None


# ** test: feature_aggregate_reorder_step
def test_feature_aggregate_reorder_step():
    '''
    Verifies move with clamping.
    '''

    # Create a feature aggregate with steps.
    feature = FeatureAggregate.new(
        name='Test Feature',
        group_id='test',
    )
    feature.add_step(name='A', attribute_id='a_event')
    feature.add_step(name='B', attribute_id='b_event')
    feature.add_step(name='C', attribute_id='c_event')

    # Move step A (position 0) to position 2.
    moved = feature.reorder_step(0, 2)
    assert moved is not None
    assert moved.name == 'A'
    assert feature.steps[0].name == 'B'
    assert feature.steps[1].name == 'C'
    assert feature.steps[2].name == 'A'


# ** test: feature_aggregate_rename
def test_feature_aggregate_rename():
    '''
    Verifies name update without id change.
    '''

    # Create a feature aggregate.
    feature = FeatureAggregate.new(
        name='Old Name',
        group_id='test',
    )
    original_id = feature.id

    # Rename the feature.
    feature.rename('New Name')

    # Assert the name was updated but the id was not.
    assert feature.name == 'New Name'
    assert feature.id == original_id


# ** test: feature_aggregate_set_description
def test_feature_aggregate_set_description():
    '''
    Verifies set and clear.
    '''

    # Create a feature aggregate.
    feature = FeatureAggregate.new(
        name='Test Feature',
        group_id='test',
    )

    # Set a description.
    feature.set_description('A custom description')
    assert feature.description == 'A custom description'

    # Clear the description.
    feature.set_description(None)
    assert feature.description is None


# ** test: feature_event_aggregate_set_pass_on_error
def test_feature_event_aggregate_set_pass_on_error():
    '''
    Verifies string normalization ("false", "False", truthy).
    '''

    # Create a feature event aggregate.
    event = FeatureEventAggregate.new(
        name='Test Event',
        attribute_id='test_handler',
    )

    # String "false" should normalize to False.
    event.set_pass_on_error('false')
    assert event.pass_on_error is False

    # String "False" should normalize to False.
    event.set_pass_on_error('False')
    assert event.pass_on_error is False

    # Truthy string should normalize to True.
    event.set_pass_on_error('true')
    assert event.pass_on_error is True

    # Boolean True should remain True.
    event.set_pass_on_error(True)
    assert event.pass_on_error is True


# ** test: feature_event_aggregate_set_parameters
def test_feature_event_aggregate_set_parameters():
    '''
    Verifies merge, None-prune, and no-op on None.
    '''

    # Create a feature event aggregate with initial parameters.
    event = FeatureEventAggregate.new(
        name='Test Event',
        attribute_id='test_handler',
        parameters={'a': '1', 'b': '2'},
    )

    # Merge new parameters (c added, a updated).
    event.set_parameters({'a': '10', 'c': '3'})
    assert event.parameters == {'a': '10', 'b': '2', 'c': '3'}

    # Prune keys with None values.
    event.set_parameters({'b': None})
    assert event.parameters == {'a': '10', 'c': '3'}

    # None input is a no-op.
    event.set_parameters(None)
    assert event.parameters == {'a': '10', 'c': '3'}


# ** test: feature_event_aggregate_set_attribute
def test_feature_event_aggregate_set_attribute():
    '''
    Verifies delegation to specialized helpers.
    '''

    # Create a feature event aggregate.
    event = FeatureEventAggregate.new(
        name='Test Event',
        attribute_id='test_handler',
        parameters={'x': '1'},
    )

    # set_attribute for parameters should delegate to set_parameters.
    event.set_attribute('parameters', {'y': '2'})
    assert event.parameters == {'x': '1', 'y': '2'}

    # set_attribute for pass_on_error should delegate to set_pass_on_error.
    event.set_attribute('pass_on_error', 'false')
    assert event.pass_on_error is False

    # set_attribute for other attributes should use setattr.
    event.set_attribute('name', 'Renamed Event')
    assert event.name == 'Renamed Event'
