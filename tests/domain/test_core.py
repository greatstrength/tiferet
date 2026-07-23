"""Tests for Tiferet Core Domain Models"""

# *** imports

# ** infra
import pytest
from pydantic import Field, ValidationError

# ** app
from tiferet.domain.core import DomainObject, ServiceDependency

# *** fixtures

# ** fixture: test_domain_object
@pytest.fixture
def test_domain_object() -> type:
    '''
    Fixture for a basic DomainObject subclass.

    :return: The DomainObject subclass.
    :rtype: type
    '''

    # Define a simple DomainObject subclass with one required field.
    class TestDomainObject(DomainObject):
        attribute: str = Field(
            ...,
            description='The attribute.',
        )

    # Return the class.
    return TestDomainObject

# *** tests

# ** test: domain_object_construct
def test_domain_object_construct(test_domain_object: type):
    '''
    Test direct construction of a DomainObject subclass.

    :param test_domain_object: The DomainObject subclass to test.
    :type test_domain_object: type
    '''

    # Construct via the standard Pydantic constructor.
    domain_object = test_domain_object(attribute='test')

    # Assert the domain object is valid.
    assert isinstance(domain_object, test_domain_object)
    assert domain_object.attribute == 'test'

# ** test: domain_object_strict_extra_field
def test_domain_object_strict_extra_field(test_domain_object: type):
    '''
    Test that DomainObject rejects unknown fields under ``extra='forbid'``.

    :param test_domain_object: The DomainObject subclass to test.
    :type test_domain_object: type
    '''

    # Constructing with an unknown field should raise.
    with pytest.raises(ValidationError):
        test_domain_object(attribute='test', unknown='nope')

# ** test: domain_object_validate_assignment
def test_domain_object_validate_assignment(test_domain_object: type):
    '''
    Test that DomainObject re-validates on attribute assignment.

    :param test_domain_object: The DomainObject subclass to test.
    :type test_domain_object: type
    '''

    # Construct and then assign an invalid type to the attribute. A list is
    # not coercible to ``str`` even with ``coerce_numbers_to_str=True``.
    domain_object = test_domain_object(attribute='test')
    with pytest.raises(ValidationError):
        domain_object.attribute = ['not', 'a', 'string']

# ** test: domain_object_forbids_extra_fields
def test_domain_object_forbids_extra_fields(test_domain_object: type):
    '''
    Test that constructing a DomainObject subclass with an unknown field raises ValidationError.

    :param test_domain_object: The DomainObject subclass to test.
    :type test_domain_object: type
    '''

    # Constructing with an extra field must raise ValidationError.
    with pytest.raises(ValidationError):
        test_domain_object(attribute='test', extra_field='value')

# ** test: service_dependency_required_fields
def test_service_dependency_required_fields():
    '''
    Test that ServiceDependency requires module_path and class_name.
    '''

    # Construction with both required fields succeeds.
    dep = ServiceDependency(
        module_path='tiferet.domain.core',
        class_name='DomainObject',
    )
    assert dep.module_path == 'tiferet.domain.core'
    assert dep.class_name == 'DomainObject'

    # Missing module_path raises ValidationError.
    with pytest.raises(ValidationError):
        ServiceDependency(class_name='DomainObject')

    # Missing class_name raises ValidationError.
    with pytest.raises(ValidationError):
        ServiceDependency(module_path='tiferet.domain.core')

# ** test: service_dependency_parameters_defaults_to_empty
def test_service_dependency_parameters_defaults_to_empty():
    '''
    Test that ServiceDependency.parameters defaults to an empty dict when not supplied.
    '''

    # Construct without parameters.
    dep = ServiceDependency(
        module_path='tiferet.domain.core',
        class_name='DomainObject',
    )

    # Assert parameters default to empty dict.
    assert dep.parameters == {}

# ** test: service_dependency_get_service_type
def test_service_dependency_get_service_type():
    '''
    Test that ServiceDependency.get_service_type returns the correct class.
    '''

    # Construct a dependency pointing at DomainObject itself.
    dep = ServiceDependency(
        module_path='tiferet.domain.core',
        class_name='DomainObject',
    )

    # Assert the returned type is DomainObject.
    assert dep.get_service_type() is DomainObject
