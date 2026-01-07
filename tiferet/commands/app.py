# *** imports

# ** core
from typing import List, Dict, Any

# ** app
from .settings import Command
from ..assets.constants import APP_INTERFACE_NOT_FOUND_ID, COMMAND_PARAMETER_REQUIRED_ID
from ..contracts.app import AppRepository, AppInterface as AppInterfaceContract, AppService
from ..models.app import AppInterface
from ..models.settings import ModelObject
from ..assets import TiferetError


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
    ) -> AppInterfaceContract:
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
        :return: The created AppInterface contract.
        :rtype: AppInterfaceContract
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

        # Normalize collection defaults.
        attributes = attributes or []
        constants = constants or {}

        # Create the AppInterface model; feature_flag and data_flag default to 'default'.
        interface: AppInterface = ModelObject.new(
            AppInterface,
            id=id,
            name=name,
            description=description,
            module_path=module_path,
            class_name=class_name,
            logger_id=logger_id or 'default',
            feature_flag=feature_flag or 'default',
            data_flag=data_flag or 'default',
            attributes=attributes,
            constants=constants,
        )

        # Persist the new interface via the app service.
        self.app_service.save(interface)

        # Return the contract type (AppInterfaceContract) instance.
        return interface


# ** command: get_app_interface
class GetAppInterface(Command):
    '''
    A command to get the application interface by its ID.
    '''

    def __init__(self, app_service: AppService):
        '''
        Initialize the GetAppInterface command.

        :param app_service: The application service instance.
        :type app_service: AppService
        '''

        # Set the application service.
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

        # Load the application interface.
        # Raise an error if the interface is not found.
        interface = self.app_service.get(interface_id)
        if not interface:
            self.raise_error(
                APP_INTERFACE_NOT_FOUND_ID,
                f'App interface with ID {interface_id} not found.',
                interface_id=interface_id
            )

        # Return the loaded application interface.
        return interface


# ** command: list_app_interfaces
class ListAppInterfaces(Command):
    '''
    Command to list all configured app interfaces.
    '''

    # * attribute: app_service
    app_service: AppService

    # * init
    def __init__(self, app_service: AppService):
        '''
        Initialize the ListAppInterfaces command.

        :param app_service: The app service to use.
        :type app_service: AppService
        '''

        # Set the application service.
        self.app_service = app_service

    # * method: execute
    def execute(self, **kwargs) -> List[AppInterface]:
        '''
        List all app interfaces.

        :return: List of AppInterface models.
        :rtype: List[AppInterface]
        '''

        # Delegate to the app service to retrieve all interfaces.
        return self.app_service.list()


# ** command: update_app_interface
class UpdateAppInterface(Command):
    '''
    Command to update scalar attributes of an existing app interface.
    '''

    # * attribute: app_service
    app_service: AppService

    # * init
    def __init__(self, app_service: AppService):
        '''
        Initialize the UpdateAppInterface command.

        :param app_service: The application service used to retrieve and
            persist app interfaces.
        :type app_service: AppService
        '''

        # Set the application service.
        self.app_service = app_service

    # * method: execute
    def execute(self, id: str, attribute: str, value: Any, **kwargs) -> str:
        '''
        Update an app interface attribute.

        :param id: The unique identifier of the app interface to update.
        :type id: str
        :param attribute: The scalar attribute name to update.
        :type attribute: str
        :param value: The new value for the attribute.
        :type value: Any
        :return: The id of the updated app interface.
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

        # Retrieve the existing app interface.
        interface = self.app_service.get(id)
        self.verify(
            expression=interface is not None,
            error_code=APP_INTERFACE_NOT_FOUND_ID,
            message=f'App interface with ID {id} not found.',
            interface_id=id,
        )

        # Delegate mutation to the model helper.
        interface.set_attribute(attribute, value)

        # Persist the updated interface.
        self.app_service.save(interface)

        # Return the interface id for idempotent usage.
        return id
