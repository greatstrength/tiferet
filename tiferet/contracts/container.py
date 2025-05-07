# *** imports

# ** app
from .settings import *
from ..data.container import *


# *** contracts

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
    def get_dependency(self, attribute_id: str, **kwargs) -> Any:
        '''
        Get the attribute dependency from the container.

        :param attribute_id: The attribute id.
        :type attribute_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The attribute dependency.
        :rtype: Any
        '''
        raise NotImplementedError()
    
    # * method: parse_parameter
    @abstractmethod
    def parse_parameter(self, parameter: str) -> str:
        '''
        Parse the parameter from the container.

        :param parameter: The parameter to parse.
        :type parameter: str
        :return: The parsed parameter.
        :rtype: str
        '''
        raise NotImplementedError()
