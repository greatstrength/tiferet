"""Tests for Tiferet Core Domain Models"""

# *** imports

# ** core
import json

# ** infra
import pytest
from pydantic import Field, ValidationError

# ** app
from tiferet.domain.core import (
    INVALID_MODEL_VALUE_ID,
    ATTRIBUTE_NOT_SETTABLE_ID,
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

# ** test: model_error_carries_code_violations_and_context
def test_model_error_carries_code_violations_and_context():
    '''
    Test that ModelError carries its error code, violations, and context arguments.
    '''

    # Construct a ModelError with a message, violations, and a context argument.
    error = ModelError(
        INVALID_MODEL_VALUE_ID,
        message='Bad value.',
        violations=[{'field': 'name', 'type': 'string_type', 'message': 'nope'}],
        attribute='name',
    )

    # Assert the code, violations, context, message, and defaulted model.
    assert error.error_code == INVALID_MODEL_VALUE_ID
    assert error.violations[0]['field'] == 'name'
    assert error.kwargs == {'attribute': 'name'}
    assert 'Bad value.' in str(error)
    assert error.model == {}

# ** test: model_error_raise_error
def test_model_error_raise_error():
    '''
    Test that ModelError.raise_error raises a ModelError with empty violations.
    '''

    # Raise a ModelError through the classmethod raiser.
    with pytest.raises(ModelError) as exc_info:
        ModelError.raise_error(
            ATTRIBUTE_NOT_SETTABLE_ID,
            message='Not settable.',
            attribute='id',
        )

    # Assert the code, context argument, and defaulted violations.
    assert exc_info.value.error_code == ATTRIBUTE_NOT_SETTABLE_ID
    assert exc_info.value.kwargs.get('attribute') == 'id'
    assert exc_info.value.violations == []

# ** test: model_error_serializes_model_descriptor
def test_model_error_serializes_model_descriptor():
    '''
    Test that ModelError stores and serializes a supplied model descriptor.
    '''

    # Construct a ModelError with a model descriptor.
    error = ModelError(
        ATTRIBUTE_NOT_SETTABLE_ID,
        message='Not settable.',
        model={'type': 'CliCommandAggregate', 'id': 'calc.add'},
        attribute='id',
    )

    # Assert the descriptor is stored and serialized.
    assert error.model == {'type': 'CliCommandAggregate', 'id': 'calc.add'}
    assert 'CliCommandAggregate' in str(error)
    assert 'calc.add' in str(error)

# ** test: model_error_defaults_empty_collections
def test_model_error_defaults_empty_collections():
    '''
    Test that ModelError defaults absent model and violations to empty collections.
    Added coverage beyond the reference prototype.
    '''

    # Construct a ModelError with only an error code.
    error = ModelError(INVALID_MODEL_VALUE_ID)

    # Assert the stored collections default to empty values.
    assert error.model == {}
    assert error.violations == []

    # Assert the serialized payload carries the empty collections.
    payload = json.loads(str(error))
    assert payload['model'] == {}
    assert payload['violations'] == []

# ** test: unpack_validation_error_flattens_violations
def test_unpack_validation_error_flattens_violations(test_domain_object: type):
    '''
    Test that unpack_validation_error flattens a ValidationError into violation descriptors.

    :param test_domain_object: The DomainObject subclass to test.
    :type test_domain_object: type
    '''

    # Construct the domain object without its required attribute.
    with pytest.raises(ValidationError) as exc_info:
        test_domain_object()

    # Unpack the validation error.
    violations = unpack_validation_error(exc_info.value)

    # Assert a single violation naming the missing attribute.
    assert len(violations) == 1
    assert violations[0]['field'] == 'attribute'
    assert set(violations[0].keys()) == {'field', 'type', 'message'}

# ** test: unpack_validation_error_defaults_missing_keys
def test_unpack_validation_error_defaults_missing_keys():
    '''
    Test that unpack_validation_error defaults missing error keys.
    Added coverage beyond the reference prototype.
    '''

    # Define a stand-in whose errors carry no keys.
    class StandInError:
        def errors(self):
            return [{}]

    # Unpack the stand-in.
    violations = unpack_validation_error(StandInError())

    # Assert the missing loc gives an empty field and missing type and msg stay None.
    assert violations == [{'field': '', 'type': None, 'message': None}]
