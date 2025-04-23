# *** imports

# ** app
from .settings import *
from ..data.container import *


# *** repositories

# ** interface: container_repository
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