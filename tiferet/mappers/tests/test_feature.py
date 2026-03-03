"""Tiferet Feature Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import (
    TransferObject,
)
from ..feature import (
    FeatureYamlObject,
    FeatureEventYamlObject,
    FeatureAggregate,
    FeatureEventAggregate,
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
    A fixture for a feature event YAML object.

    :return: The feature event YAML object.
    :rtype: FeatureEventYamlObject
    '''

    # Return the feature event YAML object.
    return TransferObject.from_data(
        FeatureEventYamlObject,
        name='Test Feature Event',
        attribute_id='test_feature_event',
        params={},
        return_to_data=True,
        data_key='test_data',
        pass_on_error=True
    )

# ** fixture: feature_yaml_object
@pytest.fixture
def feature_yaml_object() -> FeatureYamlObject:
    '''
    A fixture for a feature YAML object.

    :return: The feature YAML object.
    :rtype: FeatureYamlObject
    '''

    # Return the feature YAML object.
    return TransferObject.from_data(
        FeatureYamlObject,
        id='test_group.test_feature',
        name='Test Feature',
        description='This is a test feature.',
        feature_key='test_feature',
        group_id='test_group',
        steps=[
            dict(
                name='Test Feature Event',
                attribute_id='test_feature_event',
                params={'test_param': 'test_value'},
                return_to_data=True,
                data_key='test_data',
                pass_on_error=True
            )
        ]
    )

# *** tests

# ** test: feature_event_data_init
def test_feature_event_data_init(feature_event_yaml_object: FeatureEventYamlObject):
    '''
    Test the feature event data initialization.

    :param feature_event_yaml_object: The feature event YAML object.
    :type feature_event_yaml_object: FeatureEventYamlObject
    '''

    # Assert the feature event data attributes.
    assert feature_event_yaml_object.name == 'Test Feature Event'
    assert feature_event_yaml_object.attribute_id == 'test_feature_event'
    assert feature_event_yaml_object.parameters == {}
    assert feature_event_yaml_object.return_to_data == True
    assert feature_event_yaml_object.data_key == 'test_data'
    assert feature_event_yaml_object.pass_on_error == True

# ** test: feature_event_data_map
def test_feature_event_data_map(feature_event_yaml_object: FeatureEventYamlObject):
    '''
    Test the feature event data mapping.

    :param feature_event_yaml_object: The feature event YAML object.
    :type feature_event_yaml_object: FeatureEventYamlObject
    '''

    # Map the feature event data to a feature event object.
    feature_event = feature_event_yaml_object.map()

    # Assert the feature event type.
    assert isinstance(feature_event, FeatureEvent)

    # Assert the feature event attributes.
    assert feature_event.name == 'Test Feature Event'
    assert feature_event.attribute_id == 'test_feature_event'
    assert feature_event.parameters == {}
    assert feature_event.return_to_data == True
    assert feature_event.data_key == 'test_data'
    assert feature_event.pass_on_error == True

# ** test: feature_data_from_data
def test_feature_data_from_data(feature_yaml_object: FeatureYamlObject):
    '''
    Test the feature data from data method.

    :param feature_data: The feature data object.
    :type feature_data: FeatureData
    '''

    # Assert the feature data attributes.
    assert feature_yaml_object.name == 'Test Feature'
    assert feature_yaml_object.feature_key == 'test_feature'
    assert feature_yaml_object.description == 'This is a test feature.'
    assert feature_yaml_object.group_id == 'test_group'
    assert len(feature_yaml_object.steps) == 1

    # Assert the feature event data attributes.
    feature_event_data = feature_yaml_object.steps[0]
    assert feature_event_data.name == 'Test Feature Event'
    assert feature_event_data.attribute_id == 'test_feature_event'
    assert feature_event_data.parameters == {'test_param': 'test_value'}
    assert feature_event_data.return_to_data == True
    assert feature_event_data.data_key == 'test_data'
    assert feature_event_data.pass_on_error == True

# ** test: feature_data_map
def test_feature_data_map(feature_yaml_object: FeatureYamlObject):
    '''
    Test the feature YAML object mapping.

    :param feature_yaml_object: The feature YAML object.
    :type feature_yaml_object: FeatureYamlObject
    '''

    # Map the feature data to a feature aggregate.
    feature = feature_yaml_object.map()

    # Assert the feature type.
    assert isinstance(feature, FeatureAggregate)

    # Assert the feature attributes.
    assert feature.name == 'Test Feature'
    assert feature.feature_key == 'test_feature'
    assert feature.description == 'This is a test feature.'
    assert feature.group_id == 'test_group'
    assert len(feature.steps) == 1

    # Assert the feature event attributes.
    feature_event = feature.steps[0]
    assert feature_event.name == 'Test Feature Event'
    assert feature_event.attribute_id == 'test_feature_event'
    assert feature_event.parameters == {'test_param': 'test_value'}
    assert feature_event.return_to_data == True
    assert feature_event.data_key == 'test_data'
    assert feature_event.pass_on_error == True

# ** test: feature_aggregate_new
def test_feature_aggregate_new():
    '''
    Test creating a new FeatureAggregate.
    '''

    # Create a feature aggregate.
    aggregate = FeatureAggregate.new(
        name='Test Feature',
        group_id='test_group',
    )

    # Assert the aggregate is valid.
    assert isinstance(aggregate, FeatureAggregate)
    assert aggregate.id == 'test_group.test_feature'
    assert aggregate.feature_key == 'test_feature'
    assert aggregate.name == 'Test Feature'

# ** test: feature_aggregate_add_step
def test_feature_aggregate_add_step():
    '''
    Test adding a step to a FeatureAggregate.
    '''

    # Create a feature aggregate.
    aggregate = FeatureAggregate.new(
        name='Test Feature',
        group_id='test_group',
        steps=[],
    )

    # Add a step using raw attributes.
    step = aggregate.add_step(
        name='Test Step',
        attribute_id='test_attr',
        parameters={'p1': 'v1'},
    )

    # Assert the step was added.
    assert len(aggregate.steps) == 1
    assert aggregate.steps[0] is step
    assert step.pass_on_error is False

# ** test: feature_aggregate_add_step_position
def test_feature_aggregate_add_step_position():
    '''
    Test inserting a step at a specific position in a FeatureAggregate.
    '''

    # Create a feature aggregate.
    aggregate = FeatureAggregate.new(
        name='Test Feature',
        group_id='test_group',
        steps=[],
    )

    # Add two steps.
    first = aggregate.add_step(
        name='First Step',
        attribute_id='first_attr',
    )
    inserted = aggregate.add_step(
        name='Inserted Step',
        attribute_id='inserted_attr',
        position=0,
    )

    # Assert the inserted step is at position 0.
    assert aggregate.steps[0] is inserted
    assert aggregate.steps[1] is first

# ** test: feature_aggregate_remove_step
def test_feature_aggregate_remove_step():
    '''
    Test removing a step from a FeatureAggregate.
    '''

    # Create a feature aggregate with steps.
    aggregate = FeatureAggregate.new(
        name='Test Feature',
        group_id='test_group',
        steps=[],
    )
    first = aggregate.add_step(name='First', attribute_id='a')
    second = aggregate.add_step(name='Second', attribute_id='b')

    # Remove the first step.
    removed = aggregate.remove_step(0)
    assert removed is first
    assert aggregate.steps == [second]

    # Invalid positions return None.
    assert aggregate.remove_step(5) is None
    assert aggregate.remove_step(-1) is None

# ** test: feature_aggregate_reorder_step
def test_feature_aggregate_reorder_step():
    '''
    Test reordering steps in a FeatureAggregate.
    '''

    # Create a feature aggregate with steps.
    aggregate = FeatureAggregate.new(
        name='Test Feature',
        group_id='test_group',
        steps=[],
    )
    first = aggregate.add_step(name='First', attribute_id='a')
    second = aggregate.add_step(name='Second', attribute_id='b')
    third = aggregate.add_step(name='Third', attribute_id='c')

    # Move first step to the end.
    moved = aggregate.reorder_step(0, 2)
    assert moved is first
    assert aggregate.steps == [second, third, first]

    # Invalid current position returns None.
    assert aggregate.reorder_step(5, 0) is None

# ** test: feature_aggregate_rename
def test_feature_aggregate_rename():
    '''
    Test renaming a FeatureAggregate.
    '''

    # Create a feature aggregate.
    aggregate = FeatureAggregate.new(
        name='Original Name',
        group_id='test_group',
    )

    # Rename the feature.
    aggregate.rename('Renamed Feature')

    # Assert only the name changed.
    assert aggregate.name == 'Renamed Feature'
    assert aggregate.id == 'test_group.original_name'

# ** test: feature_aggregate_set_description
def test_feature_aggregate_set_description():
    '''
    Test setting description on a FeatureAggregate.
    '''

    # Create a feature aggregate.
    aggregate = FeatureAggregate.new(
        name='Test Feature',
        group_id='test_group',
    )

    # Set a new description.
    aggregate.set_description('New description.')
    assert aggregate.description == 'New description.'

    # Clear the description.
    aggregate.set_description(None)
    assert aggregate.description is None

# ** test: feature_event_aggregate_set_pass_on_error
def test_feature_event_aggregate_set_pass_on_error():
    '''
    Test ``set_pass_on_error`` on FeatureEventAggregate.
    '''

    # Create a feature event aggregate.
    aggregate = FeatureEventAggregate.new(
        name='Test Step',
        attribute_id='attr',
    )

    # Explicit "false" string should result in False.
    aggregate.set_pass_on_error('false')
    assert aggregate.pass_on_error is False

    # Mixed-case should also be False.
    aggregate.set_pass_on_error('False')
    assert aggregate.pass_on_error is False

    # Truthy value should result in True.
    aggregate.set_pass_on_error(1)
    assert aggregate.pass_on_error is True

# ** test: feature_event_aggregate_set_parameters
def test_feature_event_aggregate_set_parameters():
    '''
    Test ``set_parameters`` merge and cleanup on FeatureEventAggregate.
    '''

    # Create a feature event aggregate with initial parameters.
    aggregate = FeatureEventAggregate.new(
        name='Test Step',
        attribute_id='attr',
        parameters={'a': '1', 'b': '2'},
    )

    # Merge new parameters.
    aggregate.set_parameters({'b': '3', 'c': None})
    assert aggregate.parameters == {'a': '1', 'b': '3'}

    # None should be a no-op.
    aggregate.set_parameters(None)
    assert aggregate.parameters == {'a': '1', 'b': '3'}

# ** test: feature_event_aggregate_set_attribute
def test_feature_event_aggregate_set_attribute():
    '''
    Test ``set_attribute`` delegation on FeatureEventAggregate.
    '''

    # Create a feature event aggregate.
    aggregate = FeatureEventAggregate.new(
        name='Test Step',
        attribute_id='attr',
        parameters={'a': '1'},
    )

    # Update parameters via set_attribute.
    aggregate.set_attribute('parameters', {'a': None, 'b': '2'})
    assert aggregate.parameters == {'b': '2'}

    # Update pass_on_error via set_attribute.
    aggregate.set_attribute('pass_on_error', 'false')
    assert aggregate.pass_on_error is False

    # Fallback to setattr for other attributes.
    aggregate.set_attribute('data_key', 'result')
    assert aggregate.data_key == 'result'
