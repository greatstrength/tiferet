"""Tests for Tiferet Domain Settings"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import (
    DomainObject,
    StringType,
)

# *** fixtures

# ** fixture: test_domain_object
@pytest.fixture
def test_domain_object() -> DomainObject:
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

# ** test: domain_object_new
def test_domain_object_new(test_domain_object: DomainObject):
    '''
    Test the DomainObject.new method.

    :param test_domain_object: The DomainObject subclass to test.
    :type test_domain_object: DomainObject
    '''

    # Create a new domain object using the fixture.
    domain_object = DomainObject.new(test_domain_object, attribute='test')

    # Assert the domain object is valid.
    assert isinstance(domain_object, test_domain_object)
    assert domain_object.attribute == 'test'
