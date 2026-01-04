"""Tiferet Container Commands"""

# *** imports

# ** core
from typing import Tuple, List, Dict, Any, Optional

# ** app
from ..models import ContainerAttribute
from ..commands import Command
from ..contracts import ContainerService
from ..models.settings import ModelObject
from ..assets.constants import (
    INVALID_SERVICE_CONFIGURATION_ID,
    ATTRIBUTE_ALREADY_EXISTS_ID,
)

# *** commands

# ** command: add_service_configuration
class AddServiceConfiguration(Command):
    '''
    Command to add a new container attribute (service configuration).
    '''

    # * attribute: container_service
    container_service: ContainerService

    # * method: init
    def __init__(self, container_service: ContainerService):
        '''
        Initialize the add service configuration command.

        :param container_service: The container service.
        :type container_service: ContainerService
        '''

        # Set the command attributes.
        self.container_service = container_service

    # * method: execute
    def execute(
        self,
        id: str,
        module_path: Optional[str] = None,
        class_name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = {},
        dependencies: Optional[List[Dict[str, Any]]] = [],
        **kwargs,
    ) -> ContainerAttribute:
        '''
        Add a new container attribute.

        :param id: Required unique identifier.
        :type id: str
        :param module_path: Optional default module path.
        :type module_path: str | None
        :param class_name: Optional default class name.
        :type class_name: str | None
        :param parameters: Optional attribute parameters (default {}).
        :type parameters: Dict[str, Any] | None
        :param dependencies: Optional list of flagged dependencies (default []).
        :type dependencies: List[Dict[str, Any]] | None
        :return: Created ContainerAttribute model.
        :rtype: ContainerAttribute
        '''

        # Validate required id using base verify_parameter helper.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )

        # Check for existing attribute id.
        self.verify(
            not self.container_service.attribute_exists(id),
            ATTRIBUTE_ALREADY_EXISTS_ID,
            id=id,
        )

        # Validate at least one type source (default type or dependencies).
        has_default = bool(module_path and class_name)
        has_deps = bool(dependencies)
        self.verify(
            has_default or has_deps,
            INVALID_SERVICE_CONFIGURATION_ID,
        )

        # Create container attribute model directly from dependency dicts.
        attribute = ModelObject.new(
            ContainerAttribute,
            id=id,
            module_path=module_path,
            class_name=class_name,
            parameters=parameters,
            dependencies=dependencies,
        )

        # Save the new attribute and return it.
        self.container_service.save_attribute(attribute)
        return attribute

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