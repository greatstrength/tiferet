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

# ** test: test_data_object_from_model
def test_data_object_from_model(test_model_object):

    # Create a new model object from the fixture.
    model_object = test_model_object.new(test_model_object, attribute='test')

    # Create a new data object from the model object.
    data_object = DataObject.from_model(DataObject, model_object)

    # Assert the data object is valid.
    assert isinstance(data_object, DataObject)


# ** test: test_data_object_from_data
def test_data_object_from_data(test_data_object):

    # Create a new data object using the fixture.
    data_object = DataObject.from_data(test_data_object, attribute='test')

    # Assert the data object is valid.
    assert isinstance(data_object, test_data_object)
    assert data_object.attribute == 'test'


# ** test: test_data_object_allow
def test_data_object_allow():

    # Create a new allow role.
    role = DataObject.allow('test')

    # Assert the role is valid.
    assert role.fields == {'test'}


# ** test: test_data_object_deny
def test_data_object_deny():

    # Create a new deny role.
    role = DataObject.deny('test')

    # Assert the role is valid.
    assert role.fields == {'test'}