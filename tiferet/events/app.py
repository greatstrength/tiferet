# *** imports

# ** core
from typing import List, Dict, Any

# ** app
from .settings import Command, a
from ..entities import AppInterface
from ..interfaces import AppService
from ..mappers import AppInterfaceAggregate

# *** commands

# ** command: add_app_interface
class AddAppInterface(Command):
    '''
    Command to add a new application interface configuration via the AppService.
    '''

    # * attribute: app_service
    app_service: AppService

    # * init
    def __init__(self, app_service: AppService):
        '''
        Initialize the AddAppInterface command.

        :param app_service: The application service used to persist app interfaces.
        :type app_service: AppService
        '''

        self.app_service = app_service

    # * method: execute
    def execute(
        self,
        id: str,
        name: str,
        module_path: str,
        class_name: str,
        description: str | None = None,
        logger_id: str = 'default',
        feature_flag: str = 'default',
        data_flag: str = 'default',
        attributes: List[Dict[str, Any]] = [],
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
        :param feature_flag: Optional feature flag, defaults to ``'default'``.
        :type feature_flag: str | None
        :param data_flag: Optional data flag, defaults to ``'default'``.
        :type data_flag: str | None
        :param attributes: Optional list of attribute definitions; each item is a
            dict with keys ``attribute_id``, ``module_path``, ``class_name`` and
            optional ``parameters``.
        :type attributes: List[Dict[str, Any]] | None
        :param constants: Optional dictionary of constant values.
        :type constants: Dict[str, str] | None
        :return: The created AppInterface.
        :rtype: AppInterface
        '''

        # Validate required scalar parameters.
        for param_name, value in (
            ('id', id),
            ('name', name),
            ('module_path', module_path),
            ('class_name', class_name),
        ):
            self.verify_parameter(
                parameter=value,
                parameter_name=param_name,
                command_name=self.__class__.__name__,
            )

        # Collect the app interface data.
        app_interface_data = {
            'id': id,
            'name': name,
            'module_path': module_path,
            'class_name': class_name,
            'description': description,
            'logger_id': logger_id,
            'feature_flag': feature_flag,
            'data_flag': data_flag,
            'attributes': attributes,
            'constants': constants,
        }

        # Create the AppInterface model; feature_flag and data_flag default to 'default'.
        interface = AppInterfaceAggregate.new(
            app_interface_data=app_interface_data
        )

        # Persist the new interface via the app service.
        self.app_service.save(interface)

        # Return the created AppInterface instance.
        return interface

# ** command: get_app_interface
class GetAppInterface(Command):
    '''
    Command to retrieve an app interface using the ``AppService`` abstraction.
    '''

    # * attribute: app_service
    app_service: AppService

    # * init
    def __init__(self, app_service: AppService) -> None:
        '''
        Initialize the GetAppInterface command.

        :param app_service: The app service used to retrieve interfaces.
        :type app_service: AppService
        '''

        # Set the app service dependency.
        self.app_service = app_service

    # * method: execute
    def execute(self, interface_id: str, **kwargs) -> AppInterface:
        '''
        Execute the command to load the application interface.

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

# ** command: update_app_interface
class UpdateAppInterface(Command):
    '''
    Command to update scalar attributes of an existing app interface.
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

        # Validate required parameters.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )
        self.verify_parameter(
            parameter=attribute,
            parameter_name='attribute',
            command_name=self.__class__.__name__,
        )

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

# ** command: set_app_constants
class SetAppConstants(Command):
    '''
    Command to set or clear constants on an app interface.
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

        # Validate required id parameter.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )

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

# ** command: list_app_interfaces
class ListAppInterfaces(Command):
    '''
    Command to list all configured app interfaces.
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


# ** command: set_service_dependency
class SetServiceDependency(Command):
    '''
    Command to set or update a dependency attribute on an app interface.
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
    def execute(
            self,
            id: str,
            attribute_id: str,
            module_path: str,
            class_name: str,
            parameters: dict[str, Any] | None = None,
            **kwargs,
        ) -> str:
        '''
        Set or update a dependency attribute on an app interface.

        :param id: The unique identifier for the app interface.
        :type id: str
        :param attribute_id: The dependency attribute identifier.
        :type attribute_id: str
        :param module_path: The module path for the dependency implementation.
        :type module_path: str
        :param class_name: The class name for the dependency implementation.
        :type class_name: str
        :param parameters: Optional parameters for the dependency. ``None`` clears parameters.
        :type parameters: dict[str, Any] | None
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The ID of the app interface whose dependency was set.
        :rtype: str
        '''

        # Validate required parameters.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )
        self.verify_parameter(
            parameter=attribute_id,
            parameter_name='attribute_id',
            command_name=self.__class__.__name__,
        )
        self.verify_parameter(
            parameter=module_path,
            parameter_name='module_path',
            command_name=self.__class__.__name__,
        )
        self.verify_parameter(
            parameter=class_name,
            parameter_name='class_name',
            command_name=self.__class__.__name__,
        )

        # Retrieve the app interface via the app service.
        interface = self.app_service.get(id)

        # Verify that the interface exists.
        self.verify(
            expression=interface is not None,
            error_code=a.const.APP_INTERFACE_NOT_FOUND_ID,
            message=f'App interface with ID {id} not found.',
            interface_id=id,
        )

        # Set or update the dependency via the model method.
        interface.set_dependency(
            attribute_id=attribute_id,
            module_path=module_path,
            class_name=class_name,
            parameters=parameters,
        )

        # Persist the updated interface.
        self.app_service.save(interface)

        # Return the interface ID.
        return id

# ** command: remove_service_dependency
class RemoveServiceDependency(Command):
    '''
    Command to remove a dependency attribute from an app interface (idempotent).
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
    def execute(self, id: str, attribute_id: str, **kwargs) -> str:
        '''
        Remove a dependency attribute by attribute_id.

        :param id: The unique identifier for the app interface.
        :type id: str
        :param attribute_id: The dependency attribute identifier to remove.
        :type attribute_id: str
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The ID of the app interface whose dependency was removed.
        :rtype: str
        '''

        # Validate required parameters.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )
        self.verify_parameter(
            parameter=attribute_id,
            parameter_name='attribute_id',
            command_name=self.__class__.__name__,
        )

        # Retrieve the app interface via the app service.
        interface = self.app_service.get(id)

        # Verify that the interface exists.
        self.verify(
            expression=interface is not None,
            error_code=a.const.APP_INTERFACE_NOT_FOUND_ID,
            message=f'App interface with ID {id} not found.',
            interface_id=id,
        )

        # Remove the attribute idempotently via the model method.
        interface.remove_attribute(attribute_id)

        # Persist the updated interface.
        self.app_service.save(interface)

        # Return the interface ID.
        return id

# ** command: remove_app_interface
class RemoveAppInterface(Command):
    '''
    Command to remove an entire app interface configuration by ID (idempotent).
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

        # Validate required id parameter.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )

        # Delegate deletion to the app service (idempotent operation).
        self.app_service.delete(id)

        # Return the interface ID.
        return id
