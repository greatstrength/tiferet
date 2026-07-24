# *** imports

# ** core
from typing import List, Dict, Any

# ** app
from .core import DomainEvent, a
from ..domain import AppInterface, AppSession
from ..interfaces import AppService
from ..mappers import AppInterfaceAggregate, AppSessionAggregate

# *** events

# ** event: app_event
class AppEvent(DomainEvent):
    '''
    Base event providing the shared AppService dependency for app domain events.
    '''

    # * attribute: app_service
    app_service: AppService

    # * init
    def __init__(self, app_service: AppService):
        '''
        Initialize the app event with its shared service dependency.

        :param app_service: The app service shared across app events.
        :type app_service: AppService
        '''

        # Set the app service dependency.
        self.app_service = app_service

# ** event: add_app_session
class AddAppSession(AppEvent):
    '''
    A domain event to add a new application session configuration via the AppService.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id', 'name'])
    def execute(
        self,
        id: str,
        name: str,
        description: str | None = None,
        logger_id: str = 'default',
        flags: List[str] = ['default'],
        services: List[Dict[str, Any]] = [],
        constants: Dict[str, str] = {},
        **kwargs,
    ) -> AppSession:
        '''
        Create and save a new AppSession using the injected AppService.

        Required parameters: ``id``, ``name``.

        :param id: Unique identifier for the app session.
        :type id: str
        :param name: Human readable name of the session.
        :type name: str
        :param description: Optional description.
        :type description: str | None
        :param logger_id: Optional logger identifier, defaults to ``'default'``.
        :type logger_id: str
        :param flags: Optional list of DI flags, defaults to ``['default']``.
        :type flags: List[str]
        :param services: Optional list of service dependency definitions.
        :type services: List[Dict[str, Any]]
        :param constants: Optional dictionary of constant values.
        :type constants: Dict[str, str]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created AppSession.
        :rtype: AppSession
        '''

        # Coerce optional arguments that argparse may pass as None to their defaults.
        logger_id = logger_id or 'default'
        flags = flags or ['default']
        services = services or []
        constants = constants or {}

        # Create the AppSessionAggregate.
        app_session = AppSessionAggregate(
            id=id,
            name=name,
            description=description,
            logger_id=logger_id,
            flags=flags,
            services=services,
            constants=constants,
        )

        # Persist the new session via the app service.
        self.app_service.save(app_session)

        # Return the created AppSession instance.
        return app_session


# ** event: get_app_session
class GetAppSession(AppEvent):
    '''
    A domain event to retrieve an app session using the ``AppService`` abstraction.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> AppSession:
        '''
        Execute the event to load the application session.

        :param id: The ID of the application session to load.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The loaded application session.
        :rtype: AppSession
        :raises TiferetError: If the session cannot be found.
        '''

        # Retrieve the app session via the app service.
        app_session = self.app_service.get(id)

        # Verify the session exists; raise error if not found.
        self.verify(
            expression=app_session is not None,
            error_code=a.const.APP_SESSION_NOT_FOUND_ID,
            id=id,
        )

        # Return the loaded application session.
        return app_session


# ** event: add_app_interface
# -- obsolete: Superseded by AddAppSession. Retire in Parity V Story 13.
class AddAppInterface(AppEvent):
    '''
    A domain event to add a new application interface configuration via the AppService.
    '''

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

        # Coerce optional arguments that argparse may pass as None to their defaults.
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
# -- obsolete: Superseded by GetAppSession. Retire in Parity V Story 13.
class GetAppInterface(AppEvent):
    '''
    A domain event to retrieve an app interface using the ``AppService`` abstraction.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['interface_id'])
    def execute(self, interface_id: str, **kwargs) -> AppInterface:
        '''
        Execute the event to load the application interface.

        :param interface_id: The ID of the application interface to load.
        :type interface_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The loaded application interface.
        :rtype: AppInterface
        :raises TiferetError: If the interface cannot be found.
        '''

        # Retrieve the app interface via the app service.
        interface = self.app_service.get(interface_id)

        # Raise an error if the interface is not found.
        if not interface:
            self.raise_error(
                a.const.APP_INTERFACE_NOT_FOUND_ID,
                f'App interface with ID {interface_id} not found.',
                interface_id=interface_id,
            )

        # Return the loaded application interface.
        return interface

# ** event: update_app_interface
class UpdateAppInterface(AppEvent):
    '''
    A domain event to update scalar attributes of an existing app interface.
    '''

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
class SetAppConstants(AppEvent):
    '''
    A domain event to set or clear constants on an app interface.
    '''

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
class ListAppInterfaces(AppEvent):
    '''
    A domain event to list all configured app interfaces.
    '''

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
class SetServiceDependency(AppEvent):
    '''
    A domain event to set or update a service dependency on an app interface.
    '''

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
class RemoveServiceDependency(AppEvent):
    '''
    A domain event to remove a service dependency from an app interface (idempotent).
    '''

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
class RemoveAppInterface(AppEvent):
    '''
    A domain event to remove an entire app interface configuration by ID (idempotent).
    '''

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
