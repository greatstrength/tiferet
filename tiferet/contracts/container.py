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

    # * attribute: type
    type: str

    # * attribute: dependencies
    dependencies: List[FlaggedDependency]

    # * method: get_dependency
    @abstractmethod
    def get_dependency(self, flag: str) -> FlaggedDependency:
        '''
        Gets a container dependency by flag.

        :param flag: The flag for the container dependency.
        :type flag: str
        :return: The container dependency.
        :rtype: FlaggedDependency
        '''
        raise NotImplementedError()


# ** contract: container_repository
class ContainerRepository(Repository):
    '''
    An interface for accessing container attributes.
    '''

    # * method: get_attribute
    @abstractmethod
    def get_attribute(self, attribute_id: str, type: str) -> ContainerAttribute:
        '''
        Get the attribute from the container repository.

        :param attribute_id: The attribute id.
        :type attribute_id: str
        :param type: The attribute type.
        :type type: str
        :return: The container attribute.
        :rtype: ContainerAttribute
        '''
        raise NotImplementedError()

    # * method: list_all
    @abstractmethod
    def list_all(self) -> Tuple[List[ContainerAttribute], Dict[str, str]]:
        '''
        List all the container attributes and constants.

        :return: The list of container attributes and constants.
        :rtype: Tuple[List[ContainerAttribute], Dict[str, str]]
        '''
        raise NotImplementedError()


# ** contract: container_service
class ContainerService(object):
    '''
    An interface for accessing container dependencies.
    '''

    # * method: get_dependency
    @abstractmethod
    def get_dependency(self, app_id: str, attribute_id: str, **kwargs) -> Any:
        '''
        Get the attribute dependency from the container.

        :param app_id: The application instance id.
        :type app_id: str
        :param attribute_id: The attribute id.
        :type attribute_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The attribute dependency.
        :rtype: Any
        '''
        raise NotImplementedError()