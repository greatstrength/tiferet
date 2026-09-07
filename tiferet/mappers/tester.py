"""Tiferet Tester Mappers"""

# *** imports

# ** core
from importlib import import_module
from typing import Any, ClassVar, Dict
# ** infra
from pydantic import ConfigDict

# ** app
from ..assets import TiferetError
from ..assets.error import INVALID_TESTER_TYPE_ID
from ..domain import (
    AggregateTesterObject,
    DomainTesterObject,
    TesterObject,
    TransferObjectTesterObject,
)
from .core import Aggregate, TransferObject

# *** mappers

# ** mapper: tester_aggregate
class TesterAggregate(TesterObject, Aggregate):
    '''Mutable configuration aggregate for a declarative component tester.'''
    # * attribute: model_config
    model_config = ConfigDict(
        extra='allow',
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        coerce_numbers_to_str=True,
    )

    # * method: build_config_object (class)
    @classmethod
    def build_config_object(cls, data: dict) -> Any:
        '''
        Validate raw tester configuration into its declared variant.

        :param data: Raw tester configuration data.
        :type data: dict
        :return: The matching variant-specific configuration object.
        :rtype: Any
        :raises TiferetError: When the tester type is unrecognized.
        '''

        # Select the configuration class from the declared discriminator.
        config_class = {
            'domain': DomainTesterConfigObject,
            'aggregate': AggregateTesterConfigObject,
            'transfer_object': TransferObjectTesterConfigObject,
        }.get(data.get('type'))
        if config_class is None:
            TiferetError.raise_error(
                INVALID_TESTER_TYPE_ID,
                f'Invalid tester type: {data.get("type")}.',
                type=data.get('type'),
            )

        # Validate and return the matching configuration object.
        return config_class.model_validate(data)

    # * method: retarget
    def retarget(self, module_path: str, class_name: str) -> None:
        '''Retarget the configured class.

        :param module_path: The target module path.
        :type module_path: str
        :param class_name: The target class name.
        :type class_name: str
        :return: None
        :rtype: None
        '''

        # Update both parts of the target reference.
        self.module_path = module_path
        self.class_name = class_name

    # * method: set_sample_data
    def set_sample_data(self, data: dict) -> None:
        '''Merge values into the tester sample data.

        :param data: The data to merge.
        :type data: dict
        :return: None
        :rtype: None
        '''

        # Merge with last-write-wins semantics.
        sample_data = dict(self.sample_data)
        sample_data.update(data or {})
        self.sample_data = sample_data

    # * method: resolve_target_type
    def resolve_target_type(self) -> type:
        '''Resolve the configured target class.

        :return: The imported target class.
        :rtype: type
        '''

        # Import the configured module and return its class.
        return getattr(import_module(self.module_path), self.class_name)

    # * method: set_attribute
    def set_attribute(self, attribute: str, value: Any) -> None:
        '''Set a tester attribute with sample-data merge support.

        :param attribute: The attribute to update.
        :type attribute: str
        :param value: The new value.
        :type value: Any
        :return: None
        :rtype: None
        '''

        # Merge rather than replace sample data.
        if attribute == 'sample_data':
            self.set_sample_data(value)
            return

        # Delegate ordinary assignment to the aggregate base.
        super().set_attribute(attribute, value)

# ** mapper: domain_tester_config_object
class DomainTesterConfigObject(DomainTesterObject, TransferObject):
    '''Configuration representation of a domain-object tester.'''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {'exclude': {'id'}},
    }

    # * method: map
    def map(self, **overrides) -> TesterAggregate:
        '''Map configuration data to a tester aggregate.

        :param overrides: Additional mapping values.
        :type overrides: dict
        :return: The tester aggregate.
        :rtype: TesterAggregate
        '''

        # Map to the mutable aggregate type.
        return super().map(TesterAggregate, **overrides)

    # * method: from_model
    @classmethod
    def from_model(cls, tester: TesterObject, **overrides) -> 'DomainTesterConfigObject':
        '''Create config data from a tester model.

        :param tester: The source tester model.
        :type tester: TesterObject
        :param overrides: Additional mapping values.
        :type overrides: dict
        :return: The configuration object.
        :rtype: DomainTesterConfigObject
        '''

        # Delegate source serialization to the transfer-object base.
        return super().from_model(tester, **overrides)

# ** mapper: aggregate_tester_config_object
class AggregateTesterConfigObject(AggregateTesterObject, TransferObject):
    '''Configuration representation of an aggregate tester.'''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {'exclude': {'id'}},
    }

    # * attribute: name
    name: str = ''

    # * method: map
    def map(self, **overrides) -> TesterAggregate:
        '''Map configuration data to a tester aggregate.

        :param overrides: Additional mapping values.
        :type overrides: dict
        :return: The tester aggregate.
        :rtype: TesterAggregate
        '''

        # Map to the mutable aggregate type.
        return super().map(TesterAggregate, **overrides)

    # * method: from_model
    @classmethod
    def from_model(cls, tester: TesterObject, **overrides) -> 'AggregateTesterConfigObject':
        '''Create config data from a tester model.

        :param tester: The source tester model.
        :type tester: TesterObject
        :param overrides: Additional mapping values.
        :type overrides: dict
        :return: The configuration object.
        :rtype: AggregateTesterConfigObject
        '''

        # Delegate source serialization to the transfer-object base.
        return super().from_model(tester, **overrides)

# ** mapper: transfer_object_tester_config_object
class TransferObjectTesterConfigObject(TransferObjectTesterObject, TransferObject):
    '''Configuration representation of a transfer-object tester.'''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {'exclude': {'id'}},
    }

    # * attribute: name
    name: str = ''

    # * method: map
    def map(self, **overrides) -> TesterAggregate:
        '''Map configuration data to a tester aggregate.

        :param overrides: Additional mapping values.
        :type overrides: dict
        :return: The tester aggregate.
        :rtype: TesterAggregate
        '''

        # Map to the mutable aggregate type.
        return super().map(TesterAggregate, **overrides)

    # * method: from_model
    @classmethod
    def from_model(cls, tester: TesterObject, **overrides) -> 'TransferObjectTesterConfigObject':
        '''Create config data from a tester model.

        :param tester: The source tester model.
        :type tester: TesterObject
        :param overrides: Additional mapping values.
        :type overrides: dict
        :return: The configuration object.
        :rtype: TransferObjectTesterConfigObject
        '''

        # Delegate source serialization to the transfer-object base.
        return super().from_model(tester, **overrides)
