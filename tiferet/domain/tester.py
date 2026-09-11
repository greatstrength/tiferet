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

# ** model: verification
class Verification(DomainObject):
    '''
    A runtime value for one queued check against a session outcome.
    '''

    # * attribute: predicate
    predicate: Callable[[Any], bool] = Field(
        ...,
        description='The callable evaluated against the session outcome.',
    )

    # * attribute: message
    message: str | None = Field(
        default=None,
        description='The optional failure label for the verification.',
    )

    # * attribute: source
    source: Any = Field(
        ...,
        description='The original predicate or literal supplied by the caller.',
    )

# ** model: tester_object
class TesterObject(DomainObject):
    '''
    One domain object that names a specialized component under test: identity,
    import coordinates, and optional assertion payloads.
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
    ] = Field(
        default='generic',
        description='The type of tester object. Defaults to generic.',
    )

    # * attribute: id
    id: str = Field(
        ...,
        description='The unique tester identifier.',
    )

    # * attribute: module_path
    module_path: str = Field(
        ...,
        description='The module path of the target class.',
    )

    # * attribute: class_name
    class_name: str = Field(
        ...,
        description='The target class name.',
    )

    # * attribute: sample_data
    sample_data: Dict[str, Any] = Field(
        default_factory=dict,
        description='The sample data for construction and comparison.',
    )

    # * attribute: expected_data
    expected_data: Dict[str, Any] | None = Field(
        default=None,
        description='The expected data for comparison. Defaults to sample_data when absent or falsy.',
    )

    # * attribute: equality_fields
    equality_fields: List[str] = Field(
        default_factory=list,
        description='The field names compared for equality.',
    )

    # * attribute: field_normalizers
    field_normalizers: Dict[str, Callable[[Any], Any]] = Field(
        default_factory=dict,
        description='Runtime callables that normalize field values for comparison.',
    )

    # * attribute: description_cases
    description_cases: List[Tuple[str, Tuple[Any, ...], Any]] = Field(
        default_factory=list,
        description='Description cases of (name, args, expected) for assert_description.',
    )

    # * attribute: set_attribute_params
    set_attribute_params: List[Tuple[str, Any, str | None]] = Field(
        default_factory=list,
        description='Set-attribute cases of (attr, value, expect_error_code_or_None).',
    )

    # * attribute: aggregate_module_path
    aggregate_module_path: str | None = Field(
        default=None,
        description='The module path of the aggregate class.',
    )

    # * attribute: aggregate_class_name
    aggregate_class_name: str | None = Field(
        default=None,
        description='The aggregate class name.',
    )

    # * attribute: aggregate_sample_data
    aggregate_sample_data: Dict[str, Any] = Field(
        default_factory=dict,
        description='The aggregate-format expected data.',
    )

    # * attribute: map_kwargs
    map_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description='Extra keyword arguments for TransferObject.map.',
    )

    # * attribute: dependencies
    dependencies: Dict[str, ServiceDependency] = Field(
        default_factory=dict,
        description='Constructor-parameter name to ServiceDependency mapping.',
    )

    # * attribute: sample_kwargs
    sample_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description='Default keyword arguments for execute and handle.',
    )

    # * attribute: required_params
    required_params: List[str] = Field(
        default_factory=list,
        description='Parameter names that must raise COMMAND_PARAMETER_REQUIRED when missing or empty.',
    )

    # * attribute: service_attr
    service_attr: str | None = Field(
        default=None,
        description='The primary service mock name.',
    )

    # * attribute: not_found_error_code
    not_found_error_code: str | None = Field(
        default=None,
        description='The error code when the primary service get returns None.',
    )

    # * attribute: not_found_kwargs
    not_found_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description='Not-found keyword arguments. Empty means use sample_kwargs.',
    )

    # * attribute: config_parameter
    config_parameter: str | None = Field(
        default=None,
        description='The repository constructor keyword for the config file path.',
    )

    # * attribute: exists_cases
    exists_cases: List[Tuple[str, bool]] = Field(
        default_factory=list,
        description='Exists cases of (id, expected) for assert_exists.',
    )

    # * attribute: get_cases
    get_cases: List[Tuple[str, Dict[str, Any] | None]] = Field(
        default_factory=list,
        description='Get cases of (id, expected_data_or_None) for assert_get.',
    )

    # * attribute: list_ids
    list_ids: List[str] = Field(
        default_factory=list,
        description='Expected ids from list() with no filter.',
    )

    # * attribute: delete_ids
    delete_ids: List[str] = Field(
        default_factory=list,
        description='Ids to delete, assert missing, then delete again.',
    )

    # * method: _derive_expected_data (model validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_expected_data(cls, data: Any) -> Any:
        '''
        Default falsy or absent ``expected_data`` to ``sample_data`` (or ``{}``).

        :param data: The raw input data passed to the model.
        :type data: Any
        :return: The (possibly augmented) input data.
        :rtype: Any
        '''

        # Leave non-mapping input for Pydantic to handle.
        if not isinstance(data, dict):
            return data

        # Copy before deriving a missing persisted field.
        data = dict(data)
        if not data.get('expected_data'):
            data['expected_data'] = data.get('sample_data', {})

        # Return the canonicalized raw input.
        return data

    # * method: get_target_type
    def get_target_type(self) -> type:
        '''
        Import and return the target class identified by this tester.

        :return: The target class type.
        :rtype: type
        '''

        # Import the module and return the named class.
        return getattr(import_module(self.module_path), self.class_name)

    # * method: get_target
    def get_target(self) -> Any:
        '''
        Import and return the live target identified by this tester.

        :return: The callable, class, constructed instance, or attribute.
        :rtype: Any
        '''

        # Import the named attribute.
        obj = getattr(import_module(self.module_path), self.class_name)

        # Return functions and other non-class callables as-is.
        if callable(obj) and not isinstance(obj, type):
            return obj

        # Return ABC classes without instantiating them.
        if isinstance(obj, type):
            abstracts = getattr(obj, '__abstractmethods__', None)
            if abstracts:
                return obj

            # Construct a concrete class from a copy of sample_data.
            return obj(**dict(self.sample_data or {}))

        # Return constants and other attributes as-is.
        return obj

    # * method: get_aggregate_type
    def get_aggregate_type(self) -> type:
        '''
        Import and return the aggregate class identified by this tester.

        :return: The aggregate class type.
        :rtype: type
        '''

        # Import the aggregate module and return the named class.
        return getattr(import_module(self.aggregate_module_path), self.aggregate_class_name)
