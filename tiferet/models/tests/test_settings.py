"""Tests for Tiferet Models Settings"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import (
    ModelObject,
    Entity,
    ValueObject,
    StringType,
)

# *** fixtures

# ** fixture: test_model_object
@pytest.fixture
def test_model_object() -> ModelObject:
    '''
    Fixture for a basic ModelObject subclass.

    :return: The ModelObject subclass.
    :rtype: ModelObject
    '''

    # Define a simple ModelObject subclass.
    class TestModelObject(ModelObject):
        attribute = StringType(
            required=True,
            metadata=dict(
                description='The attribute.'
            ),
        )

    # Return the class.
    return TestModelObject

# ** fixture: test_entity
@pytest.fixture
def test_entity() -> Entity:
    '''
    Fixture for a basic Entity subclass.

    :return: The Entity subclass.
    :rtype: Entity
    '''

    # Define a simple Entity subclass.
    class TestEntity(Entity):
        id = StringType(
            required=True,
            metadata=dict(
                description='The entity unique identifier.'
            ),
        )

    # Return the class.
    return TestEntity

# ** fixture: test_value_object
@pytest.fixture
def test_value_object() -> ValueObject:
    '''
    Fixture for a basic ValueObject subclass.

    :return: The ValueObject subclass.
    :rtype: ValueObject
    '''

    # Define a simple ValueObject subclass.
    class TestValueObject(ValueObject):
        attribute = StringType(
            required=True,
            metadata=dict(
                description='The attribute.'
            ),
        )

    # Return the class.
    return TestValueObject

# *** tests

# ** test: model_object_new
def test_model_object_new(test_model_object: ModelObject):
    '''
    Test the ModelObject.new method.

    :param test_model_object: The ModelObject subclass to test.
    :type test_model_object: ModelObject
    '''

    # Create a new model object using the fixture.
    model_object = ModelObject.new(test_model_object, attribute='test')

    # Assert the model object is valid.
    assert isinstance(model_object, test_model_object)
    assert model_object.attribute == 'test'

# ** test: entity_new
def test_entity_new(test_entity: Entity):
    '''
    Test the Entity.new method.

    :param test_entity: The Entity subclass to test.
    :type test_entity: Entity
    '''

    # Create a new entity using the fixture.
    entity = Entity.new(test_entity, 
        id='test',
        name='Test Entity',
        description='This is a test entity.'
    )

    # Assert the entity is valid.
    assert isinstance(entity, test_entity)
    assert entity.id == 'test'
    assert entity.name == 'Test Entity'
    assert entity.description == 'This is a test entity.'

# ** test: value_object_new
def test_value_object_new(test_value_object: ValueObject):
    '''
    Test the ValueObject.new method.

    :param test_value_object: The ValueObject subclass to test.
    :type test_value_object: ValueObject
    '''

    # Create a new value object using the fixture.
    value_object = ValueObject.new(test_value_object, 
        attribute='test',
        name='Test Value Object',
        description='This is a test value object.'
    )

    # Assert the value object is valid.
    assert isinstance(value_object, test_value_object)
    assert value_object.attribute == 'test'
    assert value_object.name == 'Test Value Object'
    assert value_object.description == 'This is a test value object.'