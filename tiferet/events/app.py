# *** imports

# ** core
from typing import Any, Dict, List

# ** app
from .settings import DomainEvent, a
from ..domain import AppInterface, AppServiceDependency
from ..interfaces import AppService
from ..mappers import AppInterfaceAggregate

# *** events

# ** event: add_app_interface
class AddAppInterface(DomainEvent):
    '''
    A domain event to add a new application interface configuration via the AppService.
    '''

    # * attribute: app_service
    app_service: AppService

    # * init
    def __init__(self, app_service: AppService):
        '''
        Initialize the AddAppInterface event.

        :param app_service: The application service used to persist app interfaces.
        :type app_service: AppService
        '''

        self.app_service = app_service

    # * method: execute
    @DomainEvent.parameters_required(['id', 'name', 'module_path', 'class_name'])
    def execute(
        self,
        id: str,
        name: str,
        module_path: str,
        class_name: str,
        description: str | None = None,
        logger_id: str = 'default',
        flags: List[str] = ['default'],
        services: List[Dict[str, Any]] = [],
        constants: Dict[str, str] = {},
        **kwargs,
    ) -> AppInterface:
        '''
        Create and save a new AppInterface using the injected AppService.

        Required parameters: ``id``, ``name``, ``module_path``, ``class_name``.

        :param id: Unique identifier for the app interface.
        :type id: str
        :param name: Human readable name of the interface.
        :type name: str
        :param module_path: Python module path of the app context class.
        :type module_path: str
        :param class_name: Name of the app context class.
        :type class_name: str
        :param description: Optional description.
        :type description: str | None
        :param logger_id: Optional logger identifier, defaults to ``'default'``.
        :type logger_id: str | None
        :param flags: Optional list of flags, defaults to ``['default']``.
        :type flags: List[str]
        :param services: Optional list of service dependency definitions; each item is a
            dict with keys ``service_id``, ``module_path``, ``class_name`` and
            optional ``parameters``.
        :type services: List[Dict[str, Any]] | None
        :param constants: Optional dictionary of constant values.
        :type constants: Dict[str, str] | None
        :return: The created AppInterface.
        :rtype: AppInterface
        '''

        # Coerce optional list/dict args that argparse may pass as None.
        logger_id = logger_id or 'default'
        flags = flags or ['default']
        services = services or []
        constants = constants or {}

        # Collect the app interface data.
        app_interface_data = {
            'id': id,
            'name': name,
            'module_path': module_path,
            'class_name': class_name,
            'description': description,
            'logger_id': logger_id,
            'flags': flags,
            'services': services,
            'constants': constants,
        }

        # Create the AppInterface model; flags defaults to ['default'].
        interface = AppInterfaceAggregate(**app_interface_data)

        # Persist the new interface via the app service.
        self.app_service.save(interface)

        # Return the created AppInterface instance.
        return interface

# ** event: get_app_interface
class GetAppInterface(DomainEvent):
    '''
    A domain event to retrieve an app interface using the ``AppService`` abstraction.
    '''

    # * attribute: app_service
    app_service: AppService

    # * init
    def __init__(self, app_service: AppService) -> None:
        '''
        Initialize the GetAppInterface event.

        :param app_service: The app service used to retrieve interfaces.
        :type app_service: AppService
        '''

        # Set the app service dependency.
        self.app_service = app_service

    # * method: get_from_defaults
    def get_from_defaults(
            self,
            interface_id: str,
            default_interfaces: List[Dict[str, Any]],
        ) -> AppInterfaceAggregate | None:
        '''
        Search the provided default interface definitions for a matching id
        and return a constructed ``AppInterfaceAggregate``, or ``None`` when
        no match is found.

        :param interface_id: The interface ID to look up.
        :type interface_id: str
        :param default_interfaces: List of interface definition dicts, each
            containing at minimum an ``id`` key.
        :type default_interfaces: List[Dict[str, Any]]
        :return: The matching aggregate, or ``None``.
        :rtype: AppInterfaceAggregate | None
        '''

        # Find the first dict whose id matches the requested interface_id.
        matching = next(
            (d for d in default_interfaces if d.get('id') == interface_id),
            None,
        )

        # Construct and return the aggregate, or None if no match found.
        return AppInterfaceAggregate(**matching) if matching else None

    # * method: execute
    @DomainEvent.parameters_required(['interface_id'])
    def execute(
            self,
            interface_id: str,
            default_interfaces: List[Dict[str, Any]] = [],
            default_services: List[AppServiceDependency] | None = None,
            default_constants: Dict[str, str] | None = None,
            **kwargs,
        ) -> AppInterface:
        '''
        Execute the event to load the application interface.

        :param interface_id: The ID of the application interface to load.
        :type interface_id: str
        :param default_interfaces: A list of interface definition dicts used as a
            fallback when the interface is not found in the repository. The first
            dict whose ``id`` matches ``interface_id`` is used. Defaults to an
            empty list (no fallback).
        :type default_interfaces: List[Dict[str, Any]]
        :param default_services: A list of AppServiceDependency objects to merge
            into the interface for any service_id not already present.
        :type default_services: List[AppServiceDependency] | None
        :param default_constants: A mapping of default constants to merge into the
            interface for any key not already present.
        :type default_constants: Dict[str, str] | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The loaded application interface.
        :rtype: AppInterface
        :raises TiferetError: If the interface cannot be found.
        '''

        # Retrieve from the repository, falling back to defaults when absent.
        interface = (
            self.app_service.get(interface_id)
            or self.get_from_defaults(interface_id, default_interfaces)
        )

        # Raise an error if the interface is still not found.
        if not interface:
            self.raise_error(
                a.const.APP_INTERFACE_NOT_FOUND_ID,
                f'App interface with ID {interface_id} not found.',
                interface_id=interface_id,
            )

        # Ensure the interface is mutable before applying service/constant merges.
        if not isinstance(interface, AppInterfaceAggregate):
            interface = AppInterfaceAggregate(**interface.model_dump())

        # Merge default services into the interface for any service_id not already present.
        if default_services:

            # Build a set of existing service_ids for lookup.
            existing_ids = {dep.service_id for dep in interface.services}

            # Add any default service whose service_id is not already present.
            for dep in default_services:
                if dep.service_id not in existing_ids:
                    interface.add_service(
                        service_id=dep.service_id,
                        module_path=dep.module_path,
                        class_name=dep.class_name,
                        parameters=dep.parameters,
                    )
                    existing_ids.add(dep.service_id)

        # Merge default constants only for keys that do not already exist.
        if default_constants:

            # Create a set of missing constants that are not already defined.
            missing_constants = {
                key: value
                for key, value in default_constants.items()
                if key not in interface.constants
            }

            # Apply only missing constants, preserving user-defined constants.
            if missing_constants:
                interface.set_constants(missing_constants)

        # Return the loaded application interface.
        return interface

# ** event: update_app_interface
class UpdateAppInterface(DomainEvent):
    '''
    A domain event to update scalar attributes of an existing app interface.
    '''

    # * attribute: app_service
    app_service: AppService

    # * init
    def __init__(self, app_service: AppService) -> None:
        '''
        Initialize the UpdateAppInterface command.

        :param app_service: The app service used to manage app interfaces.
        :type app_service: AppService
        '''

        # Set the app service dependency.
        self.app_service = app_service

    # * method: execute
    @DomainEvent.parameters_required(['id', 'attribute'])
    def execute(self, id: str, attribute: str, value: Any, **kwargs) -> str:
        '''
        Update a scalar attribute on an existing app interface.

        :param id: The unique identifier for the app interface to update.
        :type id: str
        :param attribute: The attribute name to update.
        :type attribute: str
        :param value: The new value for the attribute.
        :type value: Any
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The ID of the updated app interface.
        :rtype: str
        '''

        # Retrieve the app interface via the app service.
        interface = self.app_service.get(id)

        # Verify that the interface exists.
        self.verify(
            expression=interface is not None,
            error_code=a.const.APP_INTERFACE_NOT_FOUND_ID,
            message=f'App interface with ID {id} not found.',
            interface_id=id,
        )

        # Update the attribute via the model method.
        interface.set_attribute(attribute, value)

        # Persist the updated interface.
        self.app_service.save(interface)

        # Return the interface ID.
        return id

# ** event: set_app_constants
class SetAppConstants(DomainEvent):
    '''
    A domain event to set or clear constants on an app interface.
    '''

    # * attribute: app_service
    app_service: AppService

    # * init
    def __init__(self, app_service: AppService) -> None:
        '''
        Initialize the SetAppConstants command.

        :param app_service: The app service used to manage app interfaces.
        :type app_service: AppService
        '''

        # Set the app service dependency.
        self.app_service = app_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(
            self,
            id: str,
            constants: dict[str, Any] | None = None,
            **kwargs,
        ) -> str:
        '''
        Set constants on an app interface.

        :param id: The unique identifier for the app interface.
        :type id: str
        :param constants: A mapping of constants to apply. ``None`` clears all constants.
        :type constants: dict[str, Any] | None
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The ID of the app interface whose constants were updated.
        :rtype: str
        '''

        # Retrieve the app interface via the app service.
        interface = self.app_service.get(id)

        # Verify that the interface exists.
        self.verify(
            expression=interface is not None,
            error_code=a.const.APP_INTERFACE_NOT_FOUND_ID,
            message=f'App interface with ID {id} not found.',
            interface_id=id,
        )

        # Update constants via the model method.
        interface.set_constants(constants)

        # Persist the updated interface.
        self.app_service.save(interface)

        # Return the interface ID.
        return id

# ** event: list_app_interfaces
class ListAppInterfaces(DomainEvent):
    '''
    A domain event to list all configured app interfaces.
    '''

    # * attribute: app_service
    app_service: AppService

    # * init
    def __init__(self, app_service: AppService) -> None:
        '''
        Initialize the ListAppInterfaces command.

        :param app_service: The app service to use.
        :type app_service: AppService
        '''

        # Set the app service dependency.
        self.app_service = app_service

    # * method: execute
    def execute(self, **kwargs) -> List[AppInterface]:
        '''
        List all app interfaces.

        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: List of AppInterface models.
        :rtype: List[AppInterface]
        '''

        # Delegate to the app service to retrieve all interfaces.
        return self.app_service.list()


# ** event: set_service_dependency
class SetServiceDependency(DomainEvent):
    '''
    A domain event to set or update a service dependency on an app interface.
    '''

    # * attribute: app_service
    app_service: AppService

    # * init
    def __init__(self, app_service: AppService) -> None:
        '''
        Initialize the SetServiceDependency command.

        :param app_service: The app service used to manage app interfaces.
        :type app_service: AppService
        '''

        # Set the app service dependency.
        self.app_service = app_service

    # * method: execute
    @DomainEvent.parameters_required(['id', 'service_id', 'module_path', 'class_name'])
    def execute(
            self,
            id: str,
            service_id: str,
            module_path: str,
            class_name: str,
            parameters: dict[str, Any] | None = None,
            **kwargs,
        ) -> str:
        '''
        Set or update a service dependency on an app interface.

        :param id: The unique identifier for the app interface.
        :type id: str
        :param service_id: The service dependency identifier.
        :type service_id: str
        :param module_path: The module path for the service dependency implementation.
        :type module_path: str
        :param class_name: The class name for the service dependency implementation.
        :type class_name: str
        :param parameters: Optional parameters for the service dependency. ``None`` clears parameters.
        :type parameters: dict[str, Any] | None
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The ID of the app interface whose service dependency was set.
        :rtype: str
        '''

        # Retrieve the app interface via the app service.
        interface = self.app_service.get(id)

        # Verify that the interface exists.
        self.verify(
            expression=interface is not None,
            error_code=a.const.APP_INTERFACE_NOT_FOUND_ID,
            message=f'App interface with ID {id} not found.',
            interface_id=id,
        )

        # Set or update the service dependency on the interface.
        interface.set_service(
            service_id=service_id,
            module_path=module_path,
            class_name=class_name,
            parameters=parameters,
        )

        # Persist the updated interface.
        self.app_service.save(interface)

        # Return the interface ID.
        return id

# ** event: remove_service_dependency
class RemoveServiceDependency(DomainEvent):
    '''
    A domain event to remove a service dependency from an app interface (idempotent).
    '''

    # * attribute: app_service
    app_service: AppService

    # * init
    def __init__(self, app_service: AppService) -> None:
        '''
        Initialize the RemoveServiceDependency command.

        :param app_service: The app service used to manage app interfaces.
        :type app_service: AppService
        '''

        # Set the app service dependency.
        self.app_service = app_service

    # * method: execute
    @DomainEvent.parameters_required(['id', 'service_id'])
    def execute(self, id: str, service_id: str, **kwargs) -> str:
        '''
        Remove a service dependency by service_id.

        :param id: The unique identifier for the app interface.
        :type id: str
        :param service_id: The service dependency identifier to remove.
        :type service_id: str
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The ID of the app interface whose service dependency was removed.
        :rtype: str
        '''

        # Retrieve the app interface via the app service.
        interface = self.app_service.get(id)

        # Verify that the interface exists.
        self.verify(
            expression=interface is not None,
            error_code=a.const.APP_INTERFACE_NOT_FOUND_ID,
            message=f'App interface with ID {id} not found.',
            interface_id=id,
        )

        # Remove the service dependency idempotently from the interface.
        interface.remove_service(service_id=service_id)

        # Persist the updated interface.
        self.app_service.save(interface)

        # Return the interface ID.
        return id

# ** event: remove_app_interface
class RemoveAppInterface(DomainEvent):
    '''
    A domain event to remove an entire app interface configuration by ID (idempotent).
    '''

    # * attribute: app_service
    app_service: AppService

    # * init
    def __init__(self, app_service: AppService) -> None:
        '''
        Initialize the RemoveAppInterface command.

        :param app_service: The app service used to manage app interfaces.
        :type app_service: AppService
        '''

        # Set the app service dependency.
        self.app_service = app_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove an app interface by ID.

        :param id: The interface ID.
        :type id: str
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The removed interface ID.
        :rtype: str
        '''

        # Delegate deletion to the app service (idempotent operation).
        self.app_service.delete(id)

        # Return the interface ID.
        return id
