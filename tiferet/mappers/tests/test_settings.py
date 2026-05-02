"""Mapper Settings Tests"""

# *** imports

# ** infra
from typing import Any, ClassVar, Dict

import pytest
from pydantic import Field, ValidationError

# ** app
from ...assets import TiferetError
from ...domain import DomainObject
from ..settings import Aggregate, TransferObject

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

        id: str = Field(..., description='The unique identifier.')
        name: str = Field(..., description='The name of the aggregate.')

    return TestAggregate

# ** fixture: test_data_object
@pytest.fixture
def test_data_object() -> type:
    '''
    Provides a fixture for a TransferObject subclass.

    :return: The TransferObject subclass.
    :rtype: type
    '''

    class TestDataObject(TransferObject):
        '''
        A test TransferObject for testing purposes.
        '''

        _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
            'to_data': {},
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
    Provides a fixture for a real DomainObject instance suitable for from_model.

    :return: A populated DomainObject subclass instance.
    :rtype: DomainObject
    '''

    class SourceModel(DomainObject):
        id: str = Field(..., description='The unique identifier.')
        name: str = Field(..., description='The display name.')

    return SourceModel(id='test_id', name='Test Model')

# *** tests

# ** test: aggregate_construct
def test_aggregate_construct(test_aggregate: type):
    '''
    Test direct construction of an Aggregate subclass.

    :param test_aggregate: The Aggregate subclass to test.
    :type test_aggregate: type
    '''

    aggregate = test_aggregate(id='test_id', name='Test Aggregate')
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

    with pytest.raises(ValidationError):
        test_aggregate(id='test_id', name='Test Aggregate', extra_field='ignored')

# ** test: aggregate_set_attribute_success
def test_aggregate_set_attribute_success(test_aggregate: type):
    '''
    Test setting a valid attribute on an Aggregate instance.

    :param test_aggregate: The Aggregate subclass to test.
    :type test_aggregate: type
    '''

    aggregate = test_aggregate(id='test_id', name='Original Name')
    aggregate.set_attribute('name', 'Updated Name')
    assert aggregate.name == 'Updated Name'

# ** test: aggregate_set_attribute_invalid
def test_aggregate_set_attribute_invalid(test_aggregate: type):
    '''
    Test setting an unknown attribute raises a TiferetError.

    :param test_aggregate: The Aggregate subclass to test.
    :type test_aggregate: type
    '''

    aggregate = test_aggregate(id='test_id', name='Test Name')

    with pytest.raises(TiferetError) as exc_info:
        aggregate.set_attribute('invalid_attribute', 'value')

    assert exc_info.value.error_code == 'INVALID_MODEL_ATTRIBUTE'

# ** test: aggregate_set_attribute_validates_assignment
def test_aggregate_set_attribute_validates_assignment(test_aggregate: type):
    '''
    Test that ``validate_assignment=True`` triggers field validation on set_attribute.

    :param test_aggregate: The Aggregate subclass to test.
    :type test_aggregate: type
    '''

    aggregate = test_aggregate(id='test_id', name='Original Name')

    # A list cannot be coerced to ``str`` even with ``coerce_numbers_to_str=True``.
    with pytest.raises(ValidationError):
        aggregate.set_attribute('name', ['not', 'a', 'string'])

# ** test: transfer_object_from_data
def test_transfer_object_from_data(test_data_object: type):
    '''
    Test creating a TransferObject from a dictionary via ``model_validate``.

    :param test_data_object: The TransferObject subclass to test.
    :type test_data_object: type
    '''

    data_object = test_data_object.model_validate(
        {'id': 'test_id', 'name': 'Test Data'}
    )
    assert isinstance(data_object, test_data_object)
    assert data_object.to_primitive() == {'id': 'test_id', 'name': 'Test Data'}

# ** test: transfer_object_from_model
def test_transfer_object_from_model(source_model: DomainObject, test_data_object: type):
    '''
    Test creating a TransferObject from a DomainObject via ``from_model``.

    :param source_model: The source DomainObject instance.
    :type source_model: DomainObject
    :param test_data_object: The TransferObject subclass to test.
    :type test_data_object: type
    '''

    data_object = test_data_object.from_model(source_model)
    assert isinstance(data_object, test_data_object)
    assert data_object.to_primitive() == {'id': 'test_id', 'name': 'Test Model'}

# ** test: transfer_object_from_model_with_overrides
def test_transfer_object_from_model_with_overrides(
        source_model: DomainObject,
        test_data_object: type,
    ):
    '''
    Test that ``from_model`` overrides win over the source model's data.

    :param source_model: The source DomainObject instance.
    :type source_model: DomainObject
    :param test_data_object: The TransferObject subclass to test.
    :type test_data_object: type
    '''

    data_object = test_data_object.from_model(
        source_model,
        name='Overridden Name',
    )
    assert data_object.to_primitive() == {'id': 'test_id', 'name': 'Overridden Name'}

# ** test: transfer_object_map
def test_transfer_object_map(test_aggregate: type, test_data_object: type):
    '''
    Test mapping a TransferObject onto an Aggregate type via ``map``.

    :param test_aggregate: The Aggregate subclass to map onto.
    :type test_aggregate: type
    :param test_data_object: The TransferObject subclass to map from.
    :type test_data_object: type
    '''

    data_object = test_data_object.model_validate(
        {'id': 'test_id', 'name': 'Test Data'}
    )
    aggregate = data_object.map(test_aggregate)
    assert isinstance(aggregate, test_aggregate)
    assert aggregate.id == 'test_id'
    assert aggregate.name == 'Test Data'

# ** test: transfer_object_to_primitive_with_role
def test_transfer_object_to_primitive_with_role():
    '''
    Test that ``to_primitive(role)`` resolves role-specific kwargs and applies them.
    '''

    class WithRoles(TransferObject):
        '''
        A TransferObject with explicit roles.
        '''

        _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
            'to_data.yaml': {'exclude': {'id'}},
        }

        id: str = Field(..., description='The unique identifier.')
        name: str = Field(..., description='The display name.')

    obj = WithRoles(id='test_id', name='Test Data')

    # Default dump returns canonical names.
    assert obj.to_primitive() == {'id': 'test_id', 'name': 'Test Data'}

    # Role-keyed dump excludes the requested field.
    assert obj.to_primitive('to_data.yaml') == {'name': 'Test Data'}

    # Unknown roles fall back to the default kwargs.
    assert obj.to_primitive('unknown_role') == {'id': 'test_id', 'name': 'Test Data'}
