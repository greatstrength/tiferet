"""Tests for Tiferet Models Settings"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import (
    ModelObject,
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