# *** imports

# ** app
from ..assets.constants import DEPENDENCY_TYPE_NOT_FOUND_ID
from ..commands import (
    ParseParameter,
    ImportDependency,
    RaiseError
)
from ..contracts.container import *

# *** handlers

# ** handler: container_handler
class ContainerHandler(ContainerService):

    '''
    A container handler is a class that is used to create a container object.
    '''

    # * attribute: container_repo
    container_repo: ContainerRepository

    # * method: __init__
    def __init__(self, container_repo: ContainerRepository):
        '''
        Initialize the container handler.

        :param container_repo: The container repository to use for managing container attributes.
        :type container_repo: ContainerRepository
        '''
        
        # Assign the container repository.
        self.container_repo = container_repo
    
    # * method: list_all
    def list_all(self) -> Tuple[List[ContainerAttribute], Dict[str, str]]:
        '''
        List all container attributes and constants.

        :return: A tuple containing a list of container attributes and a dictionary of constants.
        :rtype: Tuple[List[ContainerAttribute], Dict[str, str]]
        '''

        # Retrieve all container attributes and constants from the repository.
        attributes, constants = self.container_repo.list_all()

        # Return the attributes and constants.
        return attributes, constants