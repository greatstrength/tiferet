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

# ** test: service_dependency_construct
def test_service_dependency_construct():
    '''
    Test construction of a ServiceDependency with the required fields.
    '''

    # Construct with the required module_path and class_name.
    dependency = ServiceDependency(
        module_path='tiferet.domain.core',
        class_name='ServiceDependency',
    )

    # Assert the required fields are set and parameters default to empty.
    assert dependency.module_path == 'tiferet.domain.core'
    assert dependency.class_name == 'ServiceDependency'
    assert dependency.parameters == {}

# ** test: service_dependency_with_parameters
def test_service_dependency_with_parameters():
    '''
    Test that ServiceDependency retains supplied parameters.
    '''

    # Construct with an explicit parameters mapping.
    dependency = ServiceDependency(
        module_path='some.module',
        class_name='SomeClass',
        parameters={'key': 'value'},
    )

    # Assert the parameters mapping is preserved.
    assert dependency.parameters == {'key': 'value'}

# ** test: service_dependency_missing_required
def test_service_dependency_missing_required():
    '''
    Test that omitting a required field raises a ValidationError.
    '''

    # Omitting class_name should raise.
    with pytest.raises(ValidationError):
        ServiceDependency(module_path='some.module')

# ** test: service_dependency_extra_field_rejected
def test_service_dependency_extra_field_rejected():
    '''
    Test that ServiceDependency rejects unknown fields under ``extra='forbid'``.
    '''

    # Constructing with an unknown field should raise.
    with pytest.raises(ValidationError):
        ServiceDependency(
            module_path='some.module',
            class_name='SomeClass',
            unknown='nope',
        )

# ** test: service_dependency_get_service_type
def test_service_dependency_get_service_type():
    '''
    Test that ServiceDependency.get_service_type resolves the configured class type.
    '''

    # Build a dependency whose module path and class name resolve to a real type.
    dependency = ServiceDependency(
        module_path='tiferet.domain.core',
        class_name='ServiceDependency',
    )

    # Assert the resolved type matches the expected class.
    assert dependency.get_service_type() is ServiceDependency
