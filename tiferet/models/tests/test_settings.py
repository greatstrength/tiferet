# *** imports

# ** infra
import pytest

# ** app
from ..settings import *


# *** fixtures

# ** fixture: test_model_object
@pytest.fixture
def test_model_object():
    class TestModelObject(ModelObject):
        attribute = StringType(
            required=True,
            metadata=dict(
                description='The attribute.'
            ),
        )
    return TestModelObject


# ** fixture: test_entity
@pytest.fixture
def test_entity():
    class TestEntity(Entity):
        id = StringType(
            required=True,
            metadata=dict(
                description='The entity unique identifier.'
            ),
        )
    return TestEntity


# ** fixture: test_value_object
@pytest.fixture
def test_value_object():
    class TestValueObject(ValueObject):
        attribute = StringType(
            required=True,
            metadata=dict(
                description='The attribute.'
            ),
        )
    return TestValueObject


# *** tests

# ** domain: test_model_object_new
def test_model_object_new(test_model_object):
    
    # Create a new model object using the fixture.
    model_object = ModelObject.new(test_model_object, attribute='test')

    # Assert the model object is valid.
    assert isinstance(model_object, test_model_object)
    assert model_object.attribute == 'test'


# ** domain: test_entity_new
def test_entity_new(test_entity):

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


# ** domain: test_value_object_new
def test_value_object_new(test_value_object):

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