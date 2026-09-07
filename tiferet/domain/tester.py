"""Tiferet Tester Domain Models"""

# *** imports

# ** core
from importlib import import_module
from typing import Any, Callable, Dict, List, Literal, Tuple

# ** infra
from pydantic import Field, model_validator

# ** app
from .core import DomainObject

# *** models

# ** model: tester_object
class TesterObject(DomainObject):
    '''
    Declares the dependency-free description of a constructible framework
    component and the assertions used to verify its declared behavior.
    '''

    # * attribute: type
    type: Literal['domain', 'aggregate', 'transfer_object'] = Field(
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

# ** model: domain_tester_object
class DomainTesterObject(TesterObject):
    '''
    Describes assertions for a pure domain object, including optional checks
    of its descriptive properties and methods.
    '''

    # * attribute: type
    type: Literal['domain'] = Field(
        default='domain',
        description='The type of tester object.',
    )

    # * attribute: description_cases
    description_cases: List[Tuple[str, Tuple[Any, ...], Any]] = Field(
        default_factory=list,
        description='Property or method description assertions.',
    )

# ** model: aggregate_tester_object
class AggregateTesterObject(TesterObject):
    '''
    Describes assertions for a mutable aggregate, including optional
    set_attribute mutation cases.
    '''

    # * attribute: type
    type: Literal['aggregate'] = Field(
        default='aggregate',
        description='The type of tester object.',
    )

    # * attribute: set_attribute_params
    set_attribute_params: List[Tuple[str, Any, str | None]] = Field(
        default_factory=list,
        description='Aggregate attribute mutation assertions.',
    )

# ** model: transfer_object_tester_object
class TransferObjectTesterObject(TesterObject):
    '''
    Describes assertions for a transfer object and the aggregate type it maps
    to, preserving the distinct source and expected aggregate data shapes.
    '''

    # * attribute: type
    type: Literal['transfer_object'] = Field(
        default='transfer_object',
        description='The type of tester object.',
    )

    # * attribute: aggregate_module_path
    aggregate_module_path: str = Field(
        ...,
        description='The module path of the target aggregate class.',
    )

    # * attribute: aggregate_class_name
    aggregate_class_name: str = Field(
        ...,
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
