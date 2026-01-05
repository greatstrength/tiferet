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
    SERVICE_CONFIGURATION_NOT_FOUND_ID,
    INVALID_FLAGGED_DEPENDENCY_ID,
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

# ** command: set_default_service_configuration
class SetDefaultServiceConfiguration(Command):
    '''
    Command to set or update the default service configuration for an
    existing container attribute.
    '''

    # * attribute: container_service
    container_service: ContainerService

    # * method: init
    def __init__(self, container_service: ContainerService):
        '''
        Initialize the set default service configuration command.

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
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> ContainerAttribute:
        '''
        Set or update the default module/class and parameters for an
        existing container attribute.

        :param id: The unique container attribute identifier.
        :type id: str
        :param module_path: Optional default module path.
        :type module_path: str | None
        :param class_name: Optional default class name.
        :type class_name: str | None
        :param parameters: Optional attribute parameters. When None,
            existing parameters are cleared.
        :type parameters: Dict[str, Any] | None
        :return: The updated container attribute.
        :rtype: ContainerAttribute
        '''

        # Retrieve the existing attribute.
        attribute = self.container_service.get_attribute(id)

        # Verify that the attribute exists.
        self.verify(
            attribute is not None,
            SERVICE_CONFIGURATION_NOT_FOUND_ID,
            id=id,
        )

        # If either module_path or class_name is provided, both must be
        # non-None to ensure an atomic default type update.
        if module_path is not None or class_name is not None:
            self.verify(
                module_path is not None and class_name is not None,
                INVALID_SERVICE_CONFIGURATION_ID,
            )

            # Update both type and parameters via the model helper.
            attribute.set_default_type(
                module_path,
                class_name,
                parameters,
            )
        else:
            # Only parameters are being updated (or cleared). Keep the
            # existing module_path and class_name but delegate parameter
            # handling/cleanup to the model helper.
            attribute.set_default_type(
                attribute.module_path,
                attribute.class_name,
                parameters,
            )

        # Persist the updated attribute and return it.
        self.container_service.save_attribute(attribute)
        return attribute

# ** command: set_service_dependency
class SetServiceDependency(Command):
    '''
    Command to set or update a flagged dependency on an existing container
    attribute.
    '''

    # * attribute: container_service
    container_service: ContainerService

    # * method: init
    def __init__(self, container_service: ContainerService):
        '''
        Initialize the set service dependency command.

        :param container_service: The container service.
        :type container_service: ContainerService
        '''

        # Set the command attributes.
        self.container_service = container_service

    # * method: execute
    def execute(
        self,
        id: str,
        flag: str,
        module_path: str,
        class_name: str,
        parameters: Dict[str, Any] = {},
        **kwargs,
    ) -> str:
        '''
        Set or update a flagged dependency for the given container
        attribute.

        :param id: The container attribute identifier.
        :type id: str
        :param flag: The flag that identifies the dependency.
        :type flag: str
        :param module_path: The module path for the dependency.
        :type module_path: str
        :param class_name: The class name for the dependency.
        :type class_name: str
        :param parameters: Parameters for the dependency.
        :type parameters: Dict[str, Any]
        :return: The container attribute id.
        :rtype: str
        '''

        # Validate required flag (id is validated implicitly via lookup).
        self.verify_parameter(
            parameter=flag,
            parameter_name='flag',
            command_name=self.__class__.__name__,
        )

        # Ensure module_path and class_name are both provided for a valid
        # flagged dependency.
        self.verify(
            bool(module_path) and bool(class_name),
            INVALID_FLAGGED_DEPENDENCY_ID,
        )

        # Retrieve the existing attribute.
        attribute = self.container_service.get_attribute(id)

        # Verify that the attribute exists.
        self.verify(
            attribute is not None,
            SERVICE_CONFIGURATION_NOT_FOUND_ID,
            id=id,
        )

        # Delegate to the model to set/update the flagged dependency.
        attribute.set_dependency(
            flag=flag,
            module_path=module_path,
            class_name=class_name,
            parameters=parameters,
        )

        # Persist the updated attribute.
        self.container_service.save_attribute(attribute)

        # Return the id for convenience/confirmation.
        return id


# ** command: remove_service_dependency
class RemoveServiceDependency(Command):
    '''
    Command to remove a flagged dependency from an existing container
    attribute.
    '''

    # * attribute: container_service
    container_service: ContainerService

    # * method: init
    def __init__(self, container_service: ContainerService):
        '''
        Initialize the remove service dependency command.

        :param container_service: The container service.
        :type container_service: ContainerService
        '''

        # Set the command attributes.
        self.container_service = container_service

    # * method: execute
    def execute(
        self,
        id: str,
        flag: str,
        **kwargs,
    ) -> str:
        '''
        Remove a flagged dependency from the given container attribute.

        :param id: The container attribute identifier.
        :type id: str
        :param flag: The flag that identifies the dependency to remove.
        :type flag: str
        :return: The container attribute id.
        :rtype: str
        '''

        # Validate required flag.
        self.verify_parameter(
            parameter=flag,
            parameter_name='flag',
            command_name=self.__class__.__name__,
        )

        # Retrieve the existing attribute.
        attribute = self.container_service.get_attribute(id)

        # Verify that the attribute exists.
        self.verify(
            attribute is not None,
            SERVICE_CONFIGURATION_NOT_FOUND_ID,
            id=id,
        )

        # Remove the dependency by flag (idempotent at the model level).
        attribute.remove_dependency(flag)

        # Post-removal validation: ensure a remaining type source.
        has_default = bool(attribute.module_path and attribute.class_name)
        has_deps = bool(attribute.dependencies)
        self.verify(
            has_default or has_deps,
            INVALID_SERVICE_CONFIGURATION_ID,
        )

        # Persist the updated attribute.
        self.container_service.save_attribute(attribute)

        # Return the id for convenience/confirmation.
        return id

# ** command: remove_service_configuration
class RemoveServiceConfiguration(Command):
    '''
    Command to remove a container attribute (service configuration) by ID.
    '''

    # * attribute: container_service
    container_service: ContainerService

    # * init
    def __init__(self, container_service: ContainerService):
        '''
        Initialize the remove service configuration command.

        :param container_service: The container service.
        :type container_service: ContainerService
        '''

        # Set the command attributes.
        self.container_service = container_service

    # * method: execute
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a container attribute.

        :param id: The unique identifier of the attribute to remove.
        :type id: str
        :param kwargs: Additional context.
        :type kwargs: dict
        :return: The removed attribute ID.
        :rtype: str
        '''

        # Validate required id (non-empty string).
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )

        # Delete (idempotent; underlying service handles non-existent IDs).
        self.container_service.delete_attribute(id)

        # Return id for confirmation.
        return id


# ** command: set_service_constants
class SetServiceConstants(Command):
    '''
    Command to set or clear container-level constants.
    '''

    # * attribute: container_service
    container_service: ContainerService

    # * init
    def __init__(self, container_service: ContainerService):
        '''
        Initialize the SetServiceConstants command.

        :param container_service: The container service to use.
        :type container_service: ContainerService
        '''

        # Set the command attributes.
        self.container_service = container_service

    # * method: execute
    def execute(
        self,
        constants: Optional[Dict[str, Any]] = {},
        **kwargs,
    ) -> Dict[str, Any]:
        '''
        Set container constants.

        :param constants: New constants dictionary, or None to clear all.
            Keys with None value are removed using pop-style semantics.
        :type constants: Dict[str, Any] | None
        :param kwargs: Additional context.
        :type kwargs: dict
        :return: The updated constants dictionary.
        :rtype: Dict[str, Any]
        '''

        # Retrieve current constants from the container service.
        _, current_constants = self.container_service.list_all()

        if constants is None:
            # Clear all constants.
            updated = {}
        else:
            # Start from existing constants, then apply updates/removals.
            updated = dict(current_constants or {})

            # Update the current constants giving preference to the added ones.
            updated.update(constants)
        
            # Remove any constants with a value of None
            updated = {k: v for k, v in updated.items() if v != None}

        # Persist the updated constants.
        self.container_service.save_constants(updated)

        # Return the updated constants dictionary.
        return updated


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