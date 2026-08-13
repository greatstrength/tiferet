"""Tiferet Core Domain Models"""

# *** imports

# ** core
from importlib import import_module
import json
from typing import Any, Dict, List

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
    Build a safe descriptor for a model instance, naming its type and any
    identity fields it exposes as primitive values.

    :param model: The model instance to describe.
    :type model: Any
    :return: A descriptor dict with type/module and identity field values.
    :rtype: Dict[str, Any]
    '''

    # Start with the model's type and module.
    descriptor: Dict[str, Any] = {
        'type': type(model).__name__,
        'module': type(model).__module__,
    }

    # Include each identity field the model exposes as a primitive value.
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
    Flatten a Pydantic ValidationError into a list of violation descriptors.

    :param error: The validation error to unpack.
    :type error: ValidationError
    :return: A list of violation dicts with field, type, and message keys.
    :rtype: List[Dict[str, Any]]
    '''

    # Flatten each underlying error into a comparable descriptor.
    return [
        {
            'field': '.'.join(str(loc) for loc in err['loc']),
            'type': err['type'],
            'message': err['msg'],
        }
        for err in error.errors()
    ]

# *** classes

# ** class: model_error
# >> see: @guides/domain/core.md#modelerror
class ModelError(Exception):
    '''
    The vocabulary for naming a defect within a single domain model instance,
    distinct from a domain outcome or an infrastructural failure.

    Deliberately not a TiferetError subclass: a model inconsistency is a
    consumer defect rather than a domain outcome, so it is never catalogued,
    localized, or formatted as an API response -- it leaks to the top as an
    unhandled exception, naming the offending instance along the way.
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
    def __init__(
        self,
        error_code: str,
        message: str = None,
        model: Dict[str, Any] = None,
        violations: List[Dict[str, Any]] = None,
        **kwargs,
    ):
        '''
        Initialize the ModelError with an error code, message, model descriptor,
        violations, and additional arguments.

        :param error_code: The error code.
        :type error_code: str
        :param message: The error message.
        :type message: str
        :param model: A descriptor for the offending model instance.
        :type model: Dict[str, Any]
        :param violations: The flattened validation violations.
        :type violations: List[Dict[str, Any]]
        :param kwargs: Additional error keyword arguments.
        :type kwargs: dict
        '''

        # Set the error code, model descriptor, violations, and additional arguments.
        self.error_code = error_code
        self.model = model
        self.violations = violations
        self.kwargs = kwargs

        # Initialize base exception with error data.
        super().__init__(
            json.dumps({
                'error_code': error_code,
                'message': message,
                'model': model,
                'violations': violations,
                **kwargs,
            })
        )

    # * method: raise_error
    # >> see: @guides/domain/core.md#modelerror-raise-error
    @classmethod
    def raise_error(cls, error_code: str, message: str = None, model: Any = None, **kwargs) -> None:
        '''
        Raise a ModelError, describing the offending model instance when provided.

        :param error_code: The error code to raise.
        :type error_code: str
        :param message: The error message to raise.
        :type message: str
        :param model: The offending model instance to describe.
        :type model: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Raise a ModelError, describing the model instance when one is provided.
        raise cls(
            error_code,
            message=message,
            model=describe_model(model) if model is not None else None,
            **kwargs,
        )

    # * method: raise_for_validation
    # >> see: @guides/domain/core.md#modelerror-raise-for-validation
    @classmethod
    def raise_for_validation(cls, error: ValidationError, message: str = None, model: Any = None, **kwargs) -> None:
        '''
        Convert a Pydantic ValidationError into a classified ModelError.

        :param error: The Pydantic validation error to convert.
        :type error: ValidationError
        :param message: The error message to raise.
        :type message: str
        :param model: The offending model instance to describe.
        :type model: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Flatten the validation error into a list of violations.
        violations = unpack_validation_error(error)

        # Describe the offending model instance, falling back to the error's title.
        descriptor = describe_model(model) if model is not None else {'type': error.title}

        # Classify the error code by whether any violation names an unknown attribute.
        error_code = (
            INVALID_MODEL_ATTRIBUTE_ID
            if any(violation['type'] == 'no_such_attribute' for violation in violations)
            else INVALID_MODEL_VALUE_ID
        )

        # Raise the classified ModelError, chaining the original validation error.
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
    The shared foundation every domain object builds on -- a single,
    consistent contract for validation and read-only design so no domain
    module has to redefine what a domain object is.

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
    named" -- the common contract every domain-specific dependency extends
    instead of redeclaring module/class/parameter fields itself.
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
