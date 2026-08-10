"""Tiferet Core Domain Models"""

# *** imports

# ** core
from importlib import import_module
from typing import Any, Dict, List
import json

# ** infra
from pydantic import BaseModel, ConfigDict, Field, ValidationError

# *** constants

# ** constant: invalid_model_attribute_id
INVALID_MODEL_ATTRIBUTE_ID = 'INVALID_MODEL_ATTRIBUTE'

# ** constant: invalid_model_value_id
INVALID_MODEL_VALUE_ID = 'INVALID_MODEL_VALUE'

# ** constant: attribute_not_settable_id
ATTRIBUTE_NOT_SETTABLE_ID = 'ATTRIBUTE_NOT_SETTABLE'

# ** constant: model_identity_fields
MODEL_IDENTITY_FIELDS = (
    'id',
    'name',
    'key',
)

# *** functions

# ** function: describe_model
# >> see: @guides/domain/core.md#core-describe-model
def describe_model(model: Any) -> Dict[str, Any]:
    '''
    Summarize the model instance a violation originated from.

    The descriptor reports the model's type identity plus whichever identifying
    fields the model happens to declare, so a model error names the offending
    instance without holding a reference to it or serializing its whole state.

    :param model: The model instance to describe.
    :type model: Any
    :return: The model descriptor.
    :rtype: Dict[str, Any]
    '''

    # Start with the model's type identity.
    descriptor: Dict[str, Any] = {
        'type': type(model).__name__,
        'module': type(model).__module__,
    }

    # Add each identifying field the model exposes as a primitive value.
    for field in MODEL_IDENTITY_FIELDS:
        value = getattr(model, field, None)
        if isinstance(value, (bool, float, int, str)):
            descriptor[field] = value

    # Return the descriptor.
    return descriptor

# ** function: unpack_validation_error
# >> see: @guides/domain/core.md#core-unpack-validation-error
def unpack_validation_error(error: ValidationError) -> List[Dict[str, Any]]:
    '''
    Flatten a Pydantic validation error into a list of structured violations.

    Each violation reports the dotted field location, the Pydantic violation
    type, and the human-readable message, so the whole set can travel as error
    context without exposing the Pydantic error object itself.

    :param error: The Pydantic validation error to flatten.
    :type error: ValidationError
    :return: The flattened violations.
    :rtype: List[Dict[str, Any]]
    '''

    # Flatten each reported error into a field/type/message triple.
    return [
        {
            'field': '.'.join(str(loc) for loc in err.get('loc', ())),
            'type': err.get('type'),
            'message': err.get('msg'),
        }
        for err in error.errors()
    ]

# *** classes

# ** class: model_error
# >> see: @guides/domain/core.md#modelerror
class ModelError(Exception):
    '''
    The vocabulary for naming a defect within a single domain model instance
    distinctly from a domain outcome or an infrastructural failure.

    A ModelError is deliberately **not** a ``TiferetError`` subclass: a model
    inconsistency is a consumer defect rather than a domain outcome, so it is
    not catalogued, not localized, and not formatted as an API response. It
    carries its own message and leaks to the top as an unhandled exception.

    Because the error is read as a defect report rather than a response, it also
    names the offending instance: the ``model`` descriptor identifies which model
    raised the violation, which is the metadata a catalogued ``TiferetError``
    never needs to carry.
    '''

    # * attribute: error_code
    error_code: str

    # * attribute: model
    model: Dict[str, Any]

    # * attribute: violations
    violations: List[Dict[str, Any]]

    # * attribute: kwargs
    kwargs: Dict[str, Any]

    # * init
    def __init__(self,
            error_code: str,
            message: str = None,
            model: Dict[str, Any] = None,
            violations: List[Dict[str, Any]] = None,
            **kwargs):
        '''
        Initialize the ModelError with an error code, message, model descriptor,
        and violations.

        :param error_code: The model error code.
        :type error_code: str
        :param message: The error message carried by the error itself.
        :type message: str
        :param model: The descriptor of the model that raised the error, as
            produced by :func:`describe_model`.
        :type model: Dict[str, Any]
        :param violations: The structured field violations, when available.
        :type violations: List[Dict[str, Any]]
        :param kwargs: Additional error keyword arguments.
        :type kwargs: dict
        '''

        # Set the error code, model descriptor, violations, and additional arguments.
        self.error_code = error_code
        self.model = model or {}
        self.violations = violations or []
        self.kwargs = kwargs

        # Initialize the base exception with the serialized error data.
        super().__init__(
            json.dumps({
                'error_code': error_code,
                'message': message,
                'model': self.model,
                'violations': self.violations,
                **kwargs,
            })
        )

    # * method: raise_error
    # >> see: @guides/domain/core.md#modelerror-raise-error
    @classmethod
    def raise_error(cls, error_code: str, message: str = None, model: Any = None, **kwargs) -> None:
        '''
        Raise a model error with the given code and message.

        :param error_code: The model error code to raise.
        :type error_code: str
        :param message: The error message to carry.
        :type message: str
        :param model: The model instance that raised the error, described into
            error context when supplied.
        :type model: Any
        :param kwargs: Additional error keyword arguments.
        :type kwargs: dict
        '''

        # Raise the model error with the supplied code, described model, and context.
        raise cls(
            error_code,
            message=message,
            model=describe_model(model) if model is not None else None,
            **kwargs,
        )

    # * method: raise_for_validation
    # >> see: @guides/domain/core.md#modelerror-raise-for-validation
    @classmethod
    def raise_for_validation(cls,
            error: ValidationError,
            message: str = None,
            model: Any = None,
            **kwargs) -> None:
        '''
        Convert a Pydantic validation error into a model error, classifying the
        failure and preserving the original error as the exception cause.

        :param error: The Pydantic validation error to convert.
        :type error: ValidationError
        :param message: An optional message overriding the derived one.
        :type message: str
        :param model: The model instance that raised the error; when omitted the
            descriptor falls back to the type the validation error reports.
        :type model: Any
        :param kwargs: Additional error keyword arguments.
        :type kwargs: dict
        '''

        # Flatten the reported violations.
        violations = unpack_validation_error(error)

        # Describe the offending instance, falling back to the type name the
        # validation error itself reports when no instance was supplied.
        descriptor = (
            describe_model(model)
            if model is not None
            else {'type': error.title}
        )

        # An unknown field and an invalid value are distinct failures; Pydantic
        # reports the former as a no_such_attribute violation.
        error_code = (
            INVALID_MODEL_ATTRIBUTE_ID
            if any(v['type'] == 'no_such_attribute' for v in violations)
            else INVALID_MODEL_VALUE_ID
        )

        # Raise the classified model error, preserving the Pydantic cause.
        raise cls(
            error_code,
            message=message or f'{descriptor["type"]} validation failed: {violations}.',
            model=descriptor,
            violations=violations,
            **kwargs,
        ) from error

# ** class: domain_object
# >> see: @guides/domain/core.md#domainobject
class DomainObject(BaseModel):
    '''
    The shared foundation every domain object builds on — a single, consistent
    contract for validation and read-only design so no domain module has to
    redefine what a domain object is.

    Subclasses declare fields with idiomatic ``name: T = Field(...)`` annotations.
    Domain objects are intended to be read-only at the base level; mutation logic
    lives on Aggregate subclasses in :mod:`tiferet.mappers`.
    '''

    # * attribute: model_config
    model_config = ConfigDict(
        extra='forbid',
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        coerce_numbers_to_str=True,
    )

# *** models

# ** model: service_dependency
# >> see: @guides/domain/core.md#servicedependency
class ServiceDependency(DomainObject):
    '''
    The minimal, reusable shape for describing "a service implementation,
    named" — the common contract every domain-specific dependency
    (``AppServiceDependency``, ``FlaggedDependency``, ``ServiceRegistration``)
    extends instead of redeclaring module/class/parameter fields itself.
    '''

    # * attribute: module_path
    module_path: str = Field(
        ...,
        description='The module path for the service dependency.',
    )

    # * attribute: class_name
    class_name: str = Field(
        ...,
        description='The class name for the service dependency.',
    )

    # * attribute: parameters
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        description='The parameters for the service dependency.',
    )

    # * method: get_service_type
    # >> see: @guides/domain/core.md#servicedependency-get-service-type
    def get_service_type(self) -> type:
        '''
        Import and return the service class identified by this dependency.

        :return: The service class type.
        :rtype: type
        '''

        # Import the module and return the named class.
        return getattr(import_module(self.module_path), self.class_name)
