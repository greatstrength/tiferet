"""Tests for Tiferet Core Domain Models"""

# *** imports

# ** infra
import pytest
from pydantic import Field, ValidationError

# ** app
from tiferet.assets import TiferetError
from tiferet.domain.core import (
    ATTRIBUTE_NOT_SETTABLE_ID,
    INVALID_MODEL_ATTRIBUTE_ID,
    INVALID_MODEL_VALUE_ID,
    DomainObject,
    ModelError,
    ServiceDependency,
    unpack_validation_error,
)

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

# ** test: unpack_validation_error_flattens_violations
def test_unpack_validation_error_flattens_violations(test_domain_object: type):
    '''
    Test that unpack_validation_error flattens a pydantic error into
    field/type/message triples.

    :param test_domain_object: The DomainObject subclass to test.
    :type test_domain_object: type
    '''

    # Capture a validation error from a missing required field.
    with pytest.raises(ValidationError) as exc_info:
        test_domain_object()

    # Flatten the captured error.
    violations = unpack_validation_error(exc_info.value)

    # Assert the flattened shape reports the offending field.
    assert len(violations) == 1
    assert violations[0]['field'] == 'attribute'
    assert set(violations[0]) == {'field', 'type', 'message'}

# ** test: model_error_is_not_a_tiferet_error
def test_model_error_is_not_a_tiferet_error():
    '''
    Test that ModelError sits outside the TiferetError hierarchy, so a model
    inconsistency leaks as a consumer defect rather than being catalogued and
    formatted as an API response.
    '''

    # Assert the class hierarchies are deliberately separate.
    assert issubclass(ModelError, Exception)
    assert not issubclass(ModelError, TiferetError)

# ** test: model_error_carries_code_violations_and_context
def test_model_error_carries_code_violations_and_context():
    '''
    Test that ModelError retains its code, violations, and context kwargs.
    '''

    # Construct an error with violations and additional context.
    error = ModelError(
        INVALID_MODEL_VALUE_ID,
        message='Bad value.',
        violations=[{'field': 'name', 'type': 'string_type', 'message': 'nope'}],
        attribute='name',
    )

    # Assert each attribute is preserved and the message is serialized.
    assert error.error_code == INVALID_MODEL_VALUE_ID
    assert error.violations[0]['field'] == 'name'
    assert error.kwargs == {'attribute': 'name'}
    assert 'Bad value.' in str(error)

# ** test: model_error_raise_error
def test_model_error_raise_error():
    '''
    Test that raise_error raises the model error with the supplied code and context.
    '''

    # Raise directly via the classmethod raiser.
    with pytest.raises(ModelError) as exc_info:
        ModelError.raise_error(
            ATTRIBUTE_NOT_SETTABLE_ID,
            message='Not settable.',
            attribute='id',
        )

    # Assert the code, context, and empty violations.
    assert exc_info.value.error_code == ATTRIBUTE_NOT_SETTABLE_ID
    assert exc_info.value.kwargs.get('attribute') == 'id'
    assert exc_info.value.violations == []

# ** test: model_error_raise_for_validation_unknown_attribute
def test_model_error_raise_for_validation_unknown_attribute(test_domain_object: type):
    '''
    Test that raise_for_validation classifies a no_such_attribute violation as
    an invalid model attribute.

    :param test_domain_object: The DomainObject subclass to test.
    :type test_domain_object: type
    '''

    # Capture the validation error raised by assigning an unknown attribute.
    domain_object = test_domain_object(attribute='test')
    with pytest.raises(ValidationError) as validation_info:
        domain_object.not_a_field = 1

    # Convert the captured error via the raiser.
    with pytest.raises(ModelError) as exc_info:
        ModelError.raise_for_validation(validation_info.value, attribute='not_a_field')

    # Assert the unknown-attribute branch was selected.
    assert exc_info.value.error_code == INVALID_MODEL_ATTRIBUTE_ID
    assert exc_info.value.violations[0]['type'] == 'no_such_attribute'

# ** test: model_error_raise_for_validation_invalid_value
def test_model_error_raise_for_validation_invalid_value(test_domain_object: type):
    '''
    Test that raise_for_validation classifies a field-level violation as an
    invalid model value and preserves the pydantic cause.

    :param test_domain_object: The DomainObject subclass to test.
    :type test_domain_object: type
    '''

    # Capture the validation error raised by assigning a non-coercible value.
    domain_object = test_domain_object(attribute='test')
    with pytest.raises(ValidationError) as validation_info:
        domain_object.attribute = ['not', 'a', 'string']

    # Convert the captured error via the raiser.
    with pytest.raises(ModelError) as exc_info:
        ModelError.raise_for_validation(validation_info.value, attribute='attribute')

    # Assert the value branch was selected and the cause was chained.
    assert exc_info.value.error_code == INVALID_MODEL_VALUE_ID
    assert exc_info.value.__cause__ is validation_info.value
