"""Tiferet Container Contracts"""

# *** imports

# ** core
from abc import abstractmethod
from typing import (
    List,
    Dict,
    Tuple,
    Any
)

# ** app
from ..mappers import (
    ContainerAttributeAggregate,
)
from .settings import Service

# *** interfaces

# ** interface: container_service
class ContainerService(Service):
    '''
    Service interface for managing container attributes and constants.
    '''

    # * method: attribute_exists
    @abstractmethod
    def attribute_exists(self, id: str) -> bool:
        '''
        Check if a container attribute exists by ID.

        :param id: The container attribute identifier.
        :type id: str
        :return: True if the container attribute exists, otherwise False.
        :rtype: bool
        '''
        # Not implemented.
        raise NotImplementedError('attribute_exists method is required for ContainerService.')

    # * method: get_attribute
    @abstractmethod
    def get_attribute(self, attribute_id: str, flag: str = None) -> ContainerAttributeAggregate:
        '''
        Retrieve a container attribute by ID, optionally filtered by flag.

        :param attribute_id: The container attribute identifier.
        :type attribute_id: str
        :param flag: Optional flag to filter the attribute.
        :type flag: str
        :return: The container attribute aggregate.
        :rtype: ContainerAttributeAggregate
        '''
        # Not implemented.
        raise NotImplementedError('get_attribute method is required for ContainerService.')

    # * method: list_all
    @abstractmethod
    def list_all(self) -> Tuple[List[ContainerAttributeAggregate], Dict[str, str]]:
        '''
        List all container attributes and constants.

        :return: A tuple containing a list of container attribute aggregates and a dictionary of constants.
        :rtype: Tuple[List[ContainerAttributeAggregate], Dict[str, str]]
        '''
        # Not implemented.
        raise NotImplementedError('list_all method is required for ContainerService.')

    # * method: save_attribute
    @abstractmethod
    def save_attribute(self, attribute: ContainerAttributeAggregate) -> None:
        '''
        Save or update a container attribute.

        :param attribute: The container attribute aggregate to save.
        :type attribute: ContainerAttributeAggregate
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('save_attribute method is required for ContainerService.')

    # * method: delete_attribute
    @abstractmethod
    def delete_attribute(self, attribute_id: str) -> None:
        '''
        Delete a container attribute by ID. This operation should be idempotent.

        :param attribute_id: The container attribute identifier.
        :type attribute_id: str
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('delete_attribute method is required for ContainerService.')

    # * method: save_constants
    @abstractmethod
    def save_constants(self, constants: Dict[str, Any] = {}) -> None:
        '''
        Save or update container constants.

        :param constants: The container constants to save.
        :type constants: Dict[str, Any]
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('save_constants method is required for ContainerService.')
