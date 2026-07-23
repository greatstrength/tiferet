"""Tiferet Mapper Core Tests"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** infra
import pytest
from pydantic import Field, ValidationError

# ** app
from tiferet.domain import DomainObject
from tiferet.mappers.core import Aggregate, TransferObject
from tiferet.assets import TiferetError

# *** fixtures

# ** fixture: test_aggregate
@pytest.fixture
def test_aggregate() -> type:
    '''
    Provides a fixture for a test Aggregate class.

    :return: The Aggregate subclass.
    :rtype: type
    '''

    class TestAggregate(Aggregate):
        '''
        A test Aggregate for testing purposes.
        '''

        id: str = Field(
            ...,
            description='The unique identifier.',
        )

        name: str = Field(
            ...,
            description='The name of the aggregate.',
        )

    return TestAggregate

# ** fixture: test_data_object
@pytest.fixture
def test_data_object(test_aggregate: type) -> type:
    '''
    Provides a fixture for a TransferObject subclass with _ROLES.

    :param test_aggregate: The Aggregate subclass used as the map target.
    :type test_aggregate: type
    :return: The TransferObject subclass.
    :rtype: type
    '''

    class TestDataObject(TransferObject):
        '''
        A test TransferObject for testing purposes.
        '''

        _ROLES = {
            'to_data': {'exclude': {'id'}},
            'to_model': {},
        }

        id: str = Field(
            ...,
            description='The unique identifier for the data object.',
        )

        name: str = Field(
            ...,
            description='The name of the data object.',
        )

    return TestDataObject

# ** fixture: source_model
@pytest.fixture
def source_model() -> DomainObject:
    '''
    Provides a real DomainObject instance for from_model tests.

    :return: A DomainObject instance.
    :rtype: DomainObject
    '''

    # Define a simple source model.
    class SourceModel(DomainObject):
        id: str = Field(...)
        name: str = Field(...)

    # Return an instance with sample data.
    return SourceModel(id='test_id', name='Test Model')

# *** tests

# ** test: aggregate_construct
def test_aggregate_construct(test_aggregate: type):
    '''
    Test direct construction of an Aggregate subclass.

    :param test_aggregate: The Aggregate subclass to test.
    :type test_aggregate: type
    '''

    # Construct via the standard Pydantic constructor.
    aggregate = test_aggregate(id='test_id', name='Test Aggregate')

    # Assert the aggregate is correctly instantiated.
    assert isinstance(aggregate, test_aggregate)
    assert aggregate.id == 'test_id'
    assert aggregate.name == 'Test Aggregate'

# ** test: aggregate_extra_field_rejected
def test_aggregate_extra_field_rejected(test_aggregate: type):
    '''
    Test that Aggregate rejects unknown fields under ``extra='forbid'``.

    :param test_aggregate: The Aggregate subclass to test.
    :type test_aggregate: type
    '''

    # Constructing with an unknown field should raise.
    with pytest.raises(ValidationError):
        test_aggregate(id='test_id', name='Test', extra_field='nope')

# ** test: aggregate_set_attribute_success
def test_aggregate_set_attribute_success(test_aggregate: type):
    '''
    Test setting a valid attribute on an Aggregate instance.

    :param test_aggregate: The Aggregate subclass to test.
    :type test_aggregate: type
    '''

    # Create an aggregate instance.
    aggregate = test_aggregate(id='test_id', name='Original Name')

    # Update the name attribute.
    aggregate.set_attribute('name', 'Updated Name')

    # Assert the attribute was updated.
    assert aggregate.name == 'Updated Name'

# ** test: aggregate_set_attribute_invalid
def test_aggregate_set_attribute_invalid(test_aggregate: type):
    '''
    Test setting an invalid attribute raises TiferetError.

    :param test_aggregate: The Aggregate subclass to test.
    :type test_aggregate: type
    '''

    # Create an aggregate instance.
    aggregate = test_aggregate(id='test_id', name='Test Name')

    # Attempt to set an invalid attribute.
    with pytest.raises(TiferetError) as exc_info:
        aggregate.set_attribute('invalid_attribute', 'value')

    # Assert the correct error is raised.
    assert exc_info.value.error_code == 'INVALID_MODEL_ATTRIBUTE'

# ** test: aggregate_set_attribute_validates_assignment
def test_aggregate_set_attribute_validates_assignment(test_aggregate: type):
    '''
    Test that set_attribute triggers Pydantic validate_assignment on invalid type.

    :param test_aggregate: The Aggregate subclass to test.
    :type test_aggregate: type
    '''

    # Create an aggregate instance.
    aggregate = test_aggregate(id='test_id', name='Test Name')

    # Assigning a non-coercible type should raise ValidationError.
    with pytest.raises(ValidationError):
        aggregate.set_attribute('name', ['not', 'a', 'string'])

# ** test: transfer_object_from_data
def test_transfer_object_from_data(test_data_object: type):
    '''
    Test the creation of a TransferObject via model_validate.

    :param test_data_object: The TransferObject subclass to test.
    :type test_data_object: type
    '''

    # Create a TransferObject using model_validate.
    data_object = test_data_object.model_validate(dict(
        id='test_id',
        name='Test Data',
    ))

    # Assert the attributes are correctly set.
    assert isinstance(data_object, test_data_object)
    assert data_object.id == 'test_id'
    assert data_object.name == 'Test Data'

# ** test: transfer_object_from_model
def test_transfer_object_from_model(source_model: DomainObject, test_data_object: type):
    '''
    Test the creation of a TransferObject from a DomainObject.

    :param source_model: The source DomainObject instance.
    :type source_model: DomainObject
    :param test_data_object: The TransferObject subclass to test.
    :type test_data_object: type
    '''

    # Create a TransferObject from the model.
    data_object = test_data_object.from_model(source_model)

    # Assert the data object is valid.
    assert isinstance(data_object, test_data_object)
    assert data_object.id == 'test_id'
    assert data_object.name == 'Test Model'

# ** test: transfer_object_from_model_with_overrides
def test_transfer_object_from_model_with_overrides(source_model: DomainObject, test_data_object: type):
    '''
    Test that from_model overrides take priority over model data.

    :param source_model: The source DomainObject instance.
    :type source_model: DomainObject
    :param test_data_object: The TransferObject subclass to test.
    :type test_data_object: type
    '''

    # Create a TransferObject from the model with an override.
    data_object = test_data_object.from_model(source_model, name='Overridden Name')

    # Assert the override takes priority.
    assert isinstance(data_object, test_data_object)
    assert data_object.id == 'test_id'
    assert data_object.name == 'Overridden Name'

# ** test: transfer_object_map
def test_transfer_object_map(test_data_object: type, test_aggregate: type):
    '''
    Test mapping a TransferObject to an Aggregate.

    :param test_data_object: The TransferObject subclass to test.
    :type test_data_object: type
    :param test_aggregate: The Aggregate subclass to map to.
    :type test_aggregate: type
    '''

    # Create a TransferObject instance.
    data_object = test_data_object(id='test_id', name='Test Data')

    # Map to an aggregate.
    result = data_object.map(target=test_aggregate)

    # Assert the mapped aggregate is valid.
    assert isinstance(result, test_aggregate)
    assert result.id == 'test_id'
    assert result.name == 'Test Data'

# ** test: transfer_object_to_primitive_with_role
def test_transfer_object_to_primitive_with_role(test_data_object: type):
    '''
    Test to_primitive with _ROLES role resolution, exclude behavior, and unknown-role fallback.

    :param test_data_object: The TransferObject subclass to test.
    :type test_data_object: type
    '''

    # Create a TransferObject instance.
    data_object = test_data_object(id='test_id', name='Test Data')

    # to_data role should exclude 'id'.
    to_data = data_object.to_primitive(role='to_data')
    assert 'id' not in to_data
    assert to_data['name'] == 'Test Data'

    # to_model role should include all fields.
    to_model = data_object.to_primitive(role='to_model')
    assert to_model == {'id': 'test_id', 'name': 'Test Data'}

    # Unknown role should fall back to defaults (exclude_none only).
    fallback = data_object.to_primitive(role='unknown_role')
    assert fallback == {'id': 'test_id', 'name': 'Test Data'}
