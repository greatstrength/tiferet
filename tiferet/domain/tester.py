"""Tiferet Tester Domain Models"""

# *** imports

# ** core
from importlib import import_module
from typing import Any, Callable, Dict, List, Literal, Tuple

# ** infra
from pydantic import Field, model_validator

# ** app
from .core import DomainObject, ServiceDependency

# *** models

# ** model: tester_object
class TesterObject(DomainObject):
    '''
    Declares the dependency-free description of a constructible framework
    component and the assertions used to verify its declared behavior.
    '''

    # * attribute: type
    type: Literal[
        'domain',
        'aggregate',
        'transfer_object',
        'domain_event',
        'service_event',
        'generic',
        'repo',
        'context',
    ] = Field(
        ...,
        description='The type of tester object.',
    )

    # * attribute: id
    id: str = Field(
        ...,
        description='The unique tester identifier.',
    )

    # * attribute: module_path
    module_path: str = Field(
        ...,
        description='The module path of the class under test.',
    )

    # * attribute: class_name
    class_name: str = Field(
        ...,
        description='The class name of the class under test.',
    )

    # * attribute: sample_data
    sample_data: Dict[str, Any] = Field(
        default_factory=dict,
        description='The sample data used to construct the class under test.',
    )

    # * attribute: expected_data
    expected_data: Dict[str, Any] | None = Field(
        default=None,
        description='The expected constructed model data.',
    )

    # * attribute: equality_fields
    equality_fields: List[str] = Field(
        default_factory=list,
        description='The fields compared between actual and expected models.',
    )

    # * attribute: field_normalizers
    field_normalizers: Dict[str, Callable[[Any], Any]] = Field(
        default_factory=dict,
        description='Per-field functions that normalize compared values.',
    )

    # * attribute: description_cases
    description_cases: List[Tuple[str, Tuple[Any, ...], Any]] = Field(
        default_factory=list,
        description='Property or method description assertions.',
    )

    # * attribute: set_attribute_params
    set_attribute_params: List[Tuple[str, Any, str | None]] = Field(
        default_factory=list,
        description='Aggregate attribute mutation assertions.',
    )

    # * attribute: aggregate_module_path
    aggregate_module_path: str | None = Field(
        default=None,
        description='The module path of the target aggregate class.',
    )

    # * attribute: aggregate_class_name
    aggregate_class_name: str | None = Field(
        default=None,
        description='The class name of the target aggregate class.',
    )

    # * attribute: aggregate_sample_data
    aggregate_sample_data: Dict[str, Any] = Field(
        default_factory=dict,
        description='The expected aggregate-format sample data.',
    )

    # * attribute: map_kwargs
    map_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description='Additional keyword arguments passed to map.',
    )

    # * attribute: dependencies
    dependencies: Dict[str, ServiceDependency] = Field(
        default_factory=dict,
        description='Constructor-parameter name to a mock service dependency.',
    )

    # * attribute: sample_kwargs
    sample_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description='Default keyword arguments for event execute and handle.',
    )

    # * attribute: required_params
    required_params: List[str] = Field(
        default_factory=list,
        description='Parameter names that must raise when missing or empty.',
    )

    # * attribute: service_attr
    service_attr: str | None = Field(
        default=None,
        description='The primary service mock name for a service event.',
    )

    # * attribute: not_found_error_code
    not_found_error_code: str | None = Field(
        default=None,
        description='Error code raised when the primary service get returns None.',
    )

    # * attribute: not_found_kwargs
    not_found_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description='Keyword arguments for the not-found path.',
    )

    # * attribute: config_parameter
    config_parameter: str | None = Field(
        default=None,
        description='Constructor keyword for the repository config file path.',
    )

    # * attribute: exists_cases
    exists_cases: List[Tuple[str, bool]] = Field(
        default_factory=list,
        description='Repository exists assertions as (id, expected).',
    )

    # * attribute: get_cases
    get_cases: List[Tuple[str, Dict[str, Any] | None]] = Field(
        default_factory=list,
        description='Repository get assertions as (id, expected_data_or_None).',
    )

    # * attribute: list_ids
    list_ids: List[str] = Field(
        default_factory=list,
        description='Expected identifiers from an unfiltered list().',
    )

    # * attribute: delete_ids
    delete_ids: List[str] = Field(
        default_factory=list,
        description='Identifiers deleted twice to prove idempotent delete.',
    )

    # * attribute: domain_module_path
    domain_module_path: str | None = Field(
        default=None,
        description='The module path of the domain object type under test.',
    )

    # * attribute: domain_class_name
    domain_class_name: str | None = Field(
        default=None,
        description='The class name of the domain object type under test.',
    )

    # * attribute: from_domain_cases
    from_domain_cases: List[Dict[str, Any]] = Field(
        default_factory=list,
        description='from_domain bind cases for a context tester.',
    )

    # * attribute: domain_type_cases
    domain_type_cases: List[Dict[str, Any]] = Field(
        default_factory=list,
        description='Own-namespace domain_type declaration cases.',
    )

    # * attribute: for_domain_cases
    for_domain_cases: List[Dict[str, str]] = Field(
        default_factory=list,
        description='BaseContext.for_domain mapping cases.',
    )

    # * method: _derive_expected_data (model validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_expected_data(cls, data: Any) -> Any:
        '''
        Default expected data to the sample input when it is absent or falsy.

        :param data: The raw input data passed to the model.
        :type data: Any
        :return: The canonicalized input data.
        :rtype: Any
        '''

        # Leave non-mapping input for Pydantic to handle.
        if not isinstance(data, dict):
            return data

        # Copy the input before deriving expected data.
        data = dict(data)
        if not data.get('expected_data'):
            data['expected_data'] = data.get('sample_data', {})

        # Return the canonicalized input data.
        return data

    # * method: get_target_type
    def get_target_type(self) -> type:
        '''
        Import and return the class this tester describes.

        :return: The target class type.
        :rtype: type
        '''

        # Import the module and return the named target class.
        return getattr(import_module(self.module_path), self.class_name)

    # * method: get_target
    def get_target(self) -> Any:
        '''
        Import and return the live target this tester describes.

        Functions and other non-class callables are returned as-is. Abstract
        classes are returned uninstantiated. Concrete classes are constructed
        from declaration-time sample data. Other attributes are returned as-is.

        :return: The live target object, callable, class, or instance.
        :rtype: Any
        '''

        # Import the named attribute from the declared module.
        obj = getattr(import_module(self.module_path), self.class_name)

        # Return functions and other non-class callables without calling them.
        if callable(obj) and not isinstance(obj, type):
            return obj

        # Return abstract classes uninstantiated.
        if isinstance(obj, type):
            abstract_methods = getattr(obj, '__abstractmethods__', None)
            if abstract_methods:
                return obj

            # Construct a concrete class from declaration-time sample data.
            return obj(**self.sample_data)

        # Return constants and other module-level values as-is.
        return obj

    # * method: get_aggregate_type
    def get_aggregate_type(self) -> type:
        '''
        Import and return the aggregate class this tester targets.

        :return: The target aggregate class type.
        :rtype: type
        '''

        # Import the module and return the named aggregate class.
        return getattr(
            import_module(self.aggregate_module_path),
            self.aggregate_class_name,
        )

    # * method: get_domain_type
    def get_domain_type(self) -> type:
        '''
        Import and return the domain object type this tester targets.

        :return: The target domain object type.
        :rtype: type
        '''

        # Import the module and return the named domain class.
        return getattr(
            import_module(self.domain_module_path),
            self.domain_class_name,
        )

# ** model: verification
class Verification(DomainObject):
    '''
    Captures one deferred test expectation so fluent test chains can evaluate
    all declared outcomes after dispatch has completed.
    '''

    # * attribute: predicate
    predicate: Callable[[Any], bool] = Field(
        ...,
        description='The outcome predicate evaluated by the verification.',
    )

    # * attribute: message
    message: str | None = Field(
        default=None,
        description='The optional failure message for the verification.',
    )

    # * attribute: source
    source: Any = Field(
        ...,
        description='The original predicate or literal expectation.',
    )
