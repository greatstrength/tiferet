"""Tiferet Container Commands"""

# *** imports

# ** core
from typing import Tuple, List, Dict, Any

# ** app
from ..models import ContainerAttribute
from ..commands import Command
from ..contracts import ContainerService

# *** commands

# ** command: list_all_settings
class ListAllSettings(Command):
    '''
    A command to list all container attributes from the container service.
    '''

    # * attribute: container_service
    container_service: ContainerService

    # * method: init
    def __init__(self, container_service: ContainerService):
        '''
        Initialize the list all settings command.

        :param container_service: The container service.
        :type container_service: ContainerService
        '''

        # Set the command attributes.
        self.container_service = container_service

    # * method: execute
    def execute(self) -> Tuple[List[ContainerAttribute], Dict[str, Any]]:
        '''
        Execute the list all settings command.

        :return: The list of all container attributes and constants.
        :rtype: Tuple[List[ContainerAttribute], Dict[str, Any]]
        '''

        # Return the list of all container attributes from the container service.
        return self.container_service.list_all()