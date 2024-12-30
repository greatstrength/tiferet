# *** imports

# ** infra
import pytest

# ** app
from ..core import *


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


# ** fixture: test_data_object
@pytest.fixture
def test_data_object():
    class TestDataObject(DataObject):
        attribute = StringType(
            required=True,
            metadata=dict(
                description='The attribute.'
            ),
        )
    return TestDataObject


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
    entity = Entity.new(test_entity, id='test')

    # Assert the entity is valid.
    assert isinstance(entity, test_entity)
    assert entity.id == 'test'


# ** domain: test_value_object_new
def test_value_object_new(test_value_object):

    # Create a new value object using the fixture.
    value_object = ValueObject.new(test_value_object, attribute='test')

    # Assert the value object is valid.
    assert isinstance(value_object, test_value_object)
    assert value_object.attribute == 'test'


# ** domain: test_data_object_from_model
def test_data_object_from_model(test_model_object):

    # Create a new model object from the fixture.
    model_object = test_model_object.new(test_model_object, attribute='test')

    # Create a new data object from the model object.
    data_object = DataObject.from_model(DataObject, model_object)

    # Assert the data object is valid.
    assert isinstance(data_object, DataObject)


# ** domain: test_data_object_from_data
def test_data_object_from_data(test_data_object):

    # Create a new data object using the fixture.
    data_object = DataObject.from_data(test_data_object, attribute='test')

    # Assert the data object is valid.
    assert isinstance(data_object, test_data_object)
    assert data_object.attribute == 'test'


# ** domain: test_data_object_allow
def test_data_object_allow():

    # Create a new allow role.
    role = DataObject.allow('test')

    # Assert the role is valid.
    assert role.fields == {'test'}


# ** domain: test_data_object_deny
def test_data_object_deny():

    # Create a new deny role.
    role = DataObject.deny('test')

    # Assert the role is valid.
    assert role.fields == {'test'}
