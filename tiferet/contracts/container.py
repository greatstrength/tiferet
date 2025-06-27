# *** imports

# ** core
from typing import List, Dict, Tuple, Any
from abc import abstractmethod

# ** app
from .settings import *


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


# ** contract: container_service
class ContainerService(Service):
    '''
    An interface for accessing container dependencies.
    '''

   # * method: list_all
    @abstractmethod
    def list_all(self) -> Tuple[List[ContainerAttribute], Dict[str, str]]:
        '''
        List all container attributes and constants.

        :return: A tuple containing a list of container attributes and a dictionary of constants.
        :rtype: Tuple[List[ContainerAttribute], Dict[str, str]]
        '''
        raise NotImplementedError('list_all method must be implemented in the ContainerService class.')
    
     # * method: load_constants
    @abstractmethod
    def load_constants(self, attributes: List[ContainerAttribute], constants: Dict[str, str] = {}, flags: List[str] = []) -> Dict[str, str]:
        '''
        Load constants from the container attributes.

        :param attributes: The list of container attributes.
        :type attributes: List[ContainerAttribute]
        :param constants: The dictionary of constants.
        :type constants: Dict[str, str]
        :param flags: Optional list of flags to filter the constants.
        :type flags: List[str]
        :return: A dictionary of constants.
        :rtype: Dict[str, str]
        '''
        raise NotImplementedError('load_constants method must be implemented in the ContainerService class.')
    
    # * method: get_dependency_type
    @abstractmethod
    def get_dependency_type(self, attribute: ContainerAttribute, flags: List[str] = []) -> type:
        '''
        Get the type of a container attribute.

        :param attribute: The container attribute.
        :type attribute: ContainerAttribute
        :param flags: Optional list of flags to filter the dependency type.
        :type flags: List[str]
        :return: The type of the container attribute.
        :rtype: type
        '''
        raise NotImplementedError('get_dependency_type method must be implemented in the ContainerService class.')