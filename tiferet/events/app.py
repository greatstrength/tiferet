# *** imports

# ** core
from typing import List, Dict, Any

# ** app
from .core import DomainEvent, a
from ..domain import AppSession
from ..interfaces import AppService
from ..mappers import AppSessionAggregate

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
            error_code=a.error.APP_SESSION_NOT_FOUND_ID,
            id=id,
        )

        # Return the loaded application session.
        return app_session

# ** event: update_app_session
class UpdateAppSession(AppEvent):
    '''
    A domain event to update scalar attributes of an existing app session.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self,
            id: str,
            name: str | None = None,
            description: str | None = None,
            logger_id: str | None = None,
            **kwargs,
        ) -> AppSession:
        '''
        Update scalar attributes of an existing app session.

        :param id: The unique identifier for the app session to update.
        :type id: str
        :param name: The new name value, or None to leave unchanged.
        :type name: str | None
        :param description: The new description value, or None to leave unchanged.
        :type description: str | None
        :param logger_id: The new logger id value, or None to leave unchanged.
        :type logger_id: str | None
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The updated AppSession.
        :rtype: AppSession
        '''

        # Retrieve the app session via the app service.
        app_session = self.app_service.get(id)

        # Verify that the session exists.
        self.verify(
            expression=app_session is not None,
            error_code=a.error.APP_SESSION_NOT_FOUND_ID,
            message=f'App session with ID {id} not found.',
            id=id,
        )

        # Update each provided scalar attribute via the aggregate method.
        for attribute, value in (
            ('name', name),
            ('description', description),
            ('logger_id', logger_id),
        ):
            if value is not None:
                app_session.set_attribute(attribute, value)

        # Persist the updated session.
        self.app_service.save(app_session)

        # Return the updated app session.
        return app_session

# ** event: list_app_sessions
class ListAppSessions(AppEvent):
    '''
    A domain event to list all configured application sessions.
    '''

    # * method: execute
    def execute(self, **kwargs) -> List[AppSession]:
        '''
        List all configured application sessions.

        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The list of configured AppSession objects.
        :rtype: List[AppSession]
        '''

        # Delegate to the app service to retrieve all sessions.
        return self.app_service.list()

# ** event: remove_app_session
class RemoveAppSession(AppEvent):
    '''
    A domain event to remove an app session configuration by ID (idempotent).
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> None:
        '''
        Remove an app session by ID (idempotent).

        :param id: The unique identifier for the app session to remove.
        :type id: str
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: None
        :rtype: None
        '''

        # Delegate deletion to the app service (idempotent operation).
        self.app_service.delete(id)

# ** event: set_app_constants
class SetAppConstants(AppEvent):
    '''
    A domain event to set or clear constants on an app session.
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
        Set constants on an app session.

        :param id: The unique identifier for the app session.
        :type id: str
        :param constants: A mapping of constants to apply. ``None`` clears all constants.
        :type constants: dict[str, Any] | None
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The ID of the app session whose constants were updated.
        :rtype: str
        '''

        # Retrieve the app session via the app service.
        interface = self.app_service.get(id)

        # Verify that the session exists.
        self.verify(
            expression=interface is not None,
            error_code=a.error.APP_SESSION_NOT_FOUND_ID,
            message=f'App session with ID {id} not found.',
            id=id,
        )

        # Update constants via the model method.
        interface.set_constants(constants)

        # Persist the updated interface.
        self.app_service.save(interface)

        # Return the interface ID.
        return id

# ** event: set_service_dependency
class SetServiceDependency(AppEvent):
    '''
    A domain event to set or update a service dependency on an app session.
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
        Set or update a service dependency on an app session.

        :param id: The unique identifier for the app session.
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
        :return: The ID of the app session whose service dependency was set.
        :rtype: str
        '''

        # Retrieve the app session via the app service.
        interface = self.app_service.get(id)

        # Verify that the session exists.
        self.verify(
            expression=interface is not None,
            error_code=a.error.APP_SESSION_NOT_FOUND_ID,
            message=f'App session with ID {id} not found.',
            id=id,
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
    A domain event to remove a service dependency from an app session (idempotent).
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id', 'service_id'])
    def execute(self, id: str, service_id: str, **kwargs) -> str:
        '''
        Remove a service dependency by service_id.

        :param id: The unique identifier for the app session.
        :type id: str
        :param service_id: The service dependency identifier to remove.
        :type service_id: str
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The ID of the app session whose service dependency was removed.
        :rtype: str
        '''

        # Retrieve the app session via the app service.
        interface = self.app_service.get(id)

        # Verify that the session exists.
        self.verify(
            expression=interface is not None,
            error_code=a.error.APP_SESSION_NOT_FOUND_ID,
            message=f'App session with ID {id} not found.',
            id=id,
        )

        # Remove the service dependency idempotently from the interface.
        interface.remove_service(service_id=service_id)

        # Persist the updated interface.
        self.app_service.save(interface)

        # Return the interface ID.
        return id

