"""Tiferet Container Data Transfer Objects"""

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
from .settings import (
    ModelContract,
    Repository,
    Service,
)

# *** contracts

# ** contract: flagged_dependency
class FlaggedDependency(ModelContract):
    '''
    A contract for flagged dependencies.
    '''

    # * attribute: flag
    flag: str

    # * attribute: parameters
    parameters: Dict[str, str]

    # * attribute: module_path
    module_path: str

    # * attribute: class_name
    class_name: str

# ** contract: container_attribute
class ContainerAttribute(ModelContract):
    '''
    A contract defining container injector attributes.
    '''

    # * attribute: id
    id: str

    # * attribute: module_path
    module_path: str

    # * attribute: class_name
    class_name: str

    # * attribute: parameters
    parameters: Dict[str, Any]

    # * attribute: dependencies
    dependencies: List[FlaggedDependency]

    # * method: get_dependency
    @abstractmethod
    def get_dependency(self, *flags) -> FlaggedDependency:
        '''
        Gets a container dependency by flag.

        :param flags: The flags for the flagged container dependency.
        :type flags: Tuple[str, ...]
        :return: The container dependency.
        :rtype: FlaggedDependency
        '''
        raise NotImplementedError('get_dependency method must be implemented in the ContainerAttribute class.')
    
    # * method: get_type
    @abstractmethod
    def get_type(self, *flags) -> type:
        '''
        Gets the type of the container attribute based on the provided flags.

        :param flags: The flags for the flagged container dependency.
        :type flags: Tuple[str, ...]
        :return: The type of the container attribute.
        :rtype: type
        '''
        raise NotImplementedError('get_type method must be implemented in the ContainerAttribute class.')

# ** contract: container_repository
class ContainerRepository(Repository):
    '''
    An interface for accessing container attributes.
    '''

    # * method: get_attribute
    @abstractmethod
    def get_attribute(self, attribute_id: str, flag: str = None) -> ContainerAttribute:
        '''
        Get the attribute from the container repository.

        :param attribute_id: The attribute id.
        :type attribute_id: str
        :param flag: An optional flag to filter the attribute.
        :type flag: str
        :return: The container attribute.
        :rtype: ContainerAttribute
        '''
        raise NotImplementedError('get_attribute method must be implemented in the ContainerRepository class.')

    # * method: list_all
    @abstractmethod
    def list_all(self) -> Tuple[List[ContainerAttribute], Dict[str, str]]:
        '''
        List all the container attributes and constants.

        :return: The list of container attributes and constants.
        :rtype: Tuple[List[ContainerAttribute], Dict[str, str]]
        '''
        raise NotImplementedError('list_all method must be implemented in the ContainerRepository class.')

    # * method: save_attribute
    @abstractmethod
    def save_attribute(self, attribute: ContainerAttribute):
        '''
        Save the container attribute.

        :param attribute: The container attribute to save.
        :type attribute: ContainerAttribute
        '''
        raise NotImplementedError('save_attribute method must be implemented in the ContainerRepository class.')
    
    @abstractmethod
    def delete_attribute(self, attribute_id: str):
        '''
        Delete the container attribute by its unique identifier.

        :param attribute_id: The unique identifier for the attribute to delete.
        :type attribute_id: str
        '''
        raise NotImplementedError('delete_attribute method must be implemented in the ContainerRepository class.')
    
    @abstractmethod
    def save_constants(self, constants: Dict[str, str]):
        '''
        Save the container constants.

        :param constants: The container constants to save.
        :type constants: Dict[str, str]
        '''
        raise NotImplementedError('save_constants method must be implemented in the ContainerRepository class.')

# ** contract: container_service
class ContainerService(Service):
    '''
    An interface for accessing container dependencies.
    '''

    # * method: attribute_exists
    @abstractmethod
    def attribute_exists(self, id: str) -> bool:
        '''
        Check if the container attribute exists.

        :param id: The container attribute id.
        :type id: str
        :return: Whether the container attribute exists.
        :rtype: bool
        '''
        raise NotImplementedError('attribute_exists method must be implemented in the ContainerService class.')

    # * method: get_attribute
    @abstractmethod
    def get_attribute(self, attribute_id: str, flag: str = None) -> ContainerAttribute:
        '''
        Get the attribute from the container service.

        :param attribute_id: The attribute id.
        :type attribute_id: str
        :param flag: An optional flag to filter the attribute.
        :type flag: str
        :return: The container attribute.
        :rtype: ContainerAttribute
        '''
        raise NotImplementedError('get_attribute method must be implemented in the ContainerService class.')

    # * method: list_all
    @abstractmethod
    def list_all(self) -> Tuple[List[ContainerAttribute], Dict[str, str]]:
        '''
        List all container attributes and constants from the service.

        :return: A tuple containing a list of container attributes and a dictionary of constants.
        :rtype: Tuple[List[ContainerAttribute], Dict[str, str]]
        '''
        raise NotImplementedError('list_all method must be implemented in the ContainerService class.')

    # * method: save_attribute
    @abstractmethod
    def save_attribute(self, attribute: ContainerAttribute):
        '''
        Save the container attribute through the service.

        :param attribute: The container attribute to save.
        :type attribute: ContainerAttribute
        '''
        raise NotImplementedError('save_attribute method must be implemented in the ContainerService class.')

    # * method: delete_attribute
    @abstractmethod
    def delete_attribute(self, attribute_id: str):
        '''
        Delete the container attribute by its unique identifier through
        the service.

        :param attribute_id: The unique identifier for the attribute to delete.
        :type attribute_id: str
        '''
        raise NotImplementedError('delete_attribute method must be implemented in the ContainerService class.')

    # * method: save_constants
    @abstractmethod
    def save_constants(self, constants: Dict[str, Any] = {}):
        '''
        Save the container constants through the service.

        :param constants: The container constants to save.
        :type constants: Dict[str, Any]
        '''
        raise NotImplementedError('save_constants method must be implemented in the ContainerService class.')
