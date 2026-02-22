"""Tests for Tiferet Models Settings"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import (
    DomainObject,
    StringType,
)

# *** fixtures

# ** fixture: test_model_object
@pytest.fixture
def test_model_object() -> DomainObject:
    '''
    Fixture for a basic DomainObject subclass.

    :return: The DomainObject subclass.
    :rtype: DomainObject
    '''

    # Define a simple DomainObject subclass.
    class TestDomainObject(DomainObject):
        attribute = StringType(
            required=True,
            metadata=dict(
                description='The attribute.'
            ),
        )

    # Return the class.
    return TestDomainObject

# *** tests

# ** test: model_object_new
def test_model_object_new(test_model_object: DomainObject):
    '''
    Test the DomainObject.new method.

    :param test_model_object: The DomainObject subclass to test.
    :type test_model_object: DomainObject
    '''

    # Create a new model object using the fixture.
    model_object = DomainObject.new(test_model_object, attribute='test')

    # Assert the model object is valid.
    assert isinstance(model_object, test_model_object)
    assert model_object.attribute == 'test'
