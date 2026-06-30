"""Tiferet DI Domain Events"""

# *** imports

# ** core
from typing import Tuple, List, Dict, Any, Optional

# ** app
from .settings import DomainEvent, a
from ..domain.di import ServiceRegistration
from ..interfaces.di import DIService
from ..mappers.di import ServiceRegistrationAggregate

# *** events

# ** event: di_event
class DIEvent(DomainEvent):
    '''
    Base event providing the shared DIService dependency for DI domain events.
    '''

    # * attribute: di_service
    di_service: DIService

    # * init
    def __init__(self, di_service: DIService):
        '''
        Initialize the DI event with its shared service dependency.

        :param di_service: The DI service shared across DI events.
        :type di_service: DIService
        '''

        # Set the DI service dependency.
        self.di_service = di_service

# ** event: add_service_registration
class AddServiceRegistration(DIEvent):
    '''
    A domain event to add a new service registration.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(
        self,
        id: str,
        module_path: Optional[str] = None,
        class_name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = {},
        flagged_dependencies: Optional[List[Dict[str, Any]]] = [],
        **kwargs,
    ) -> ServiceRegistration:
        '''
        Add a new service registration.

        :param id: Required unique identifier.
        :type id: str
        :param module_path: Optional default module path.
        :type module_path: str | None
        :param class_name: Optional default class name.
        :type class_name: str | None
        :param parameters: Optional registration parameters (default {}).
        :type parameters: Dict[str, Any] | None
        :param flagged_dependencies: Optional list of flagged dependencies (default []).
        :type flagged_dependencies: List[Dict[str, Any]] | None
        :return: Created ServiceRegistration model.
        :rtype: ServiceRegistration
        '''

        # Coerce optional collection arguments to their empty defaults.
        parameters = parameters or {}
        flagged_dependencies = flagged_dependencies or []

        # Check for an existing registration id.
        self.verify(
            not self.di_service.registration_exists(id),
            a.const.SERVICE_REGISTRATION_ALREADY_EXISTS_ID,
            id=id,
        )

        # Validate at least one type source (default type or flagged dependencies).
        has_default = bool(module_path and class_name)
        has_deps = bool(flagged_dependencies)
        self.verify(
            has_default or has_deps,
            a.const.INVALID_SERVICE_REGISTRATION_ID,
        )

        # Create the service registration aggregate from dependency dicts.
        registration = ServiceRegistrationAggregate(
            id=id,
            module_path=module_path,
            class_name=class_name,
            parameters=parameters,
            dependencies=flagged_dependencies,
        )

        # Save the new registration and return it.
        self.di_service.save_registration(registration)
        return registration

# ** event: set_default_service_registration
class SetDefaultServiceRegistration(DIEvent):
    '''
    A domain event to set or update the default service registration for an
    existing service registration.
    '''

    # * method: execute
    def execute(
        self,
        id: str,
        module_path: Optional[str] = None,
        class_name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> ServiceRegistration:
        '''
        Set or update the default module/class and parameters for an
        existing service registration.

        :param id: The unique service registration identifier.
        :type id: str
        :param module_path: Optional default module path.
        :type module_path: str | None
        :param class_name: Optional default class name.
        :type class_name: str | None
        :param parameters: Optional registration parameters. When None,
            existing parameters are cleared.
        :type parameters: Dict[str, Any] | None
        :return: The updated service registration.
        :rtype: ServiceRegistration
        '''

        # Retrieve the existing registration.
        registration = self.di_service.get_registration(id)

        # Verify that the registration exists.
        self.verify(
            registration is not None,
            a.const.SERVICE_REGISTRATION_NOT_FOUND_ID,
            id=id,
        )

        # If either module_path or class_name is provided, both must be
        # non-None to ensure an atomic default type update.
        if module_path is not None or class_name is not None:
            self.verify(
                module_path is not None and class_name is not None,
                a.const.INVALID_SERVICE_REGISTRATION_ID,
            )

            # Update both type and parameters via the model helper.
            registration.set_default_type(
                module_path,
                class_name,
                parameters,
            )
        else:
            # Only parameters are being updated (or cleared). Keep the
            # existing module_path and class_name but delegate parameter
            # handling/cleanup to the model helper.
            registration.set_default_type(
                registration.module_path,
                registration.class_name,
                parameters,
            )

        # Persist the updated registration and return it.
        self.di_service.save_registration(registration)
        return registration

# ** event: set_service_dependency
class SetServiceDependency(DIEvent):
    '''
    A domain event to set or update a flagged dependency on an existing
    service registration.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['flag'])
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
        Set or update a flagged dependency for the given service
        registration.

        :param id: The service registration identifier.
        :type id: str
        :param flag: The flag that identifies the dependency.
        :type flag: str
        :param module_path: The module path for the dependency.
        :type module_path: str
        :param class_name: The class name for the dependency.
        :type class_name: str
        :param parameters: Parameters for the dependency.
        :type parameters: Dict[str, Any]
        :return: The service registration id.
        :rtype: str
        '''

        # Coerce optional parameters to an empty dict.
        parameters = parameters or {}

        # Ensure module_path and class_name are both provided for a valid
        # flagged dependency.
        self.verify(
            bool(module_path) and bool(class_name),
            a.const.INVALID_FLAGGED_DEPENDENCY_ID,
        )

        # Retrieve the existing registration.
        registration = self.di_service.get_registration(id)

        # Verify that the registration exists.
        self.verify(
            registration is not None,
            a.const.SERVICE_REGISTRATION_NOT_FOUND_ID,
            id=id,
        )

        # Delegate to the model to set/update the flagged dependency.
        registration.set_dependency(
            flag=flag,
            module_path=module_path,
            class_name=class_name,
            parameters=parameters,
        )

        # Persist the updated registration.
        self.di_service.save_registration(registration)

        # Return the id for convenience/confirmation.
        return id

# ** event: remove_service_dependency
class RemoveServiceDependency(DIEvent):
    '''
    A domain event to remove a flagged dependency from an existing service
    registration.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['flag'])
    def execute(
        self,
        id: str,
        flag: str,
        **kwargs,
    ) -> str:
        '''
        Remove a flagged dependency from the given service registration.

        :param id: The service registration identifier.
        :type id: str
        :param flag: The flag that identifies the dependency to remove.
        :type flag: str
        :return: The service registration id.
        :rtype: str
        '''

        # Retrieve the existing registration.
        registration = self.di_service.get_registration(id)

        # Verify that the registration exists.
        self.verify(
            registration is not None,
            a.const.SERVICE_REGISTRATION_NOT_FOUND_ID,
            id=id,
        )

        # Remove the dependency by flag (idempotent at the model level).
        registration.remove_dependency(flag)

        # Post-removal validation: ensure a remaining type source.
        has_default = bool(registration.module_path and registration.class_name)
        has_deps = bool(registration.dependencies)
        self.verify(
            has_default or has_deps,
            a.const.INVALID_SERVICE_REGISTRATION_ID,
        )

        # Persist the updated registration.
        self.di_service.save_registration(registration)

        # Return the id for convenience/confirmation.
        return id

# ** event: remove_service_registration
class RemoveServiceRegistration(DIEvent):
    '''
    A domain event to remove a service registration by ID.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a service registration.

        :param id: The unique identifier of the registration to remove.
        :type id: str
        :param kwargs: Additional context.
        :type kwargs: dict
        :return: The removed registration ID.
        :rtype: str
        '''

        # Delete (idempotent; underlying service handles non-existent IDs).
        self.di_service.delete_registration(id)

        # Return id for confirmation.
        return id

# ** event: set_service_constants
class SetServiceConstants(DIEvent):
    '''
    A domain event to set or clear service-level constants.
    '''

    # * method: execute
    def execute(
        self,
        constants: Optional[Dict[str, Any]] = {},
        **kwargs,
    ) -> Dict[str, Any]:
        '''
        Set service constants.

        :param constants: New constants dictionary, or None to clear all.
            Keys with None value are removed using pop-style semantics.
        :type constants: Dict[str, Any] | None
        :param kwargs: Additional context.
        :type kwargs: dict
        :return: The updated constants dictionary.
        :rtype: Dict[str, Any]
        '''

        # Retrieve current constants from the DI service.
        _, current_constants = self.di_service.list_all()

        if constants is None:
            # Clear all constants.
            updated = {}
        else:
            # Start from existing constants, then apply updates/removals.
            updated = dict(current_constants or {})

            # Update the current constants giving preference to the added ones.
            updated.update(constants)

            # Remove any constants with a value of None.
            updated = {k: v for k, v in updated.items() if v != None}

        # Persist the updated constants.
        self.di_service.save_constants(updated)

        # Return the updated constants dictionary.
        return updated

# ** event: list_all_settings
class ListAllSettings(DIEvent):
    '''
    A domain event to list all service registrations and constants.
    '''

    # * method: execute
    def execute(self, **kwargs) -> Tuple[List[ServiceRegistration], Dict[str, Any]]:
        '''
        Execute the list all settings event.

        :param kwargs: Additional context.
        :type kwargs: dict
        :return: The list of all service registrations and constants.
        :rtype: Tuple[List[ServiceRegistration], Dict[str, Any]]
        '''

        # Return the list of all service registrations from the DI service.
        return self.di_service.list_all()
