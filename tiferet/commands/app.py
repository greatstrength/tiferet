# *** imports

# ** app
from .settings import Command, const
from ..models import ModelObject, AppInterface
from ..contracts import AppRepository, AppService


# *** commands

# ** command: get_app_interface
class GetAppInterface(Command):
    '''
    A command to get the application interface by its ID.
    '''

    def __init__(self, app_repo: AppRepository):
        '''
        Initialize the LoadAppInterface command.

        :param app_repo: The application repository instance.
        :type app_repo: AppRepository
        '''

        # Set the application repository.
        self.app_repo = app_repo

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
        interface = self.app_repo.get_interface(interface_id)
        if not interface:
            self.raise_error(
                const.APP_INTERFACE_NOT_FOUND_ID,
                f'App interface with ID {interface_id} not found.',
                interface_id=interface_id,
            )

        # Return the loaded application interface.
        return interface


# ** command: add_app_interface
class AddAppInterface(Command):
    '''
    Command to add a new application interface via the ``AppService``.
    '''

    # * attribute: app_service
    app_service: AppService

    # * init
    def __init__(self, app_service: AppService) -> None:
        '''
        Initialize the AddAppInterface command.

        :param app_service: The app service used to manage app interfaces.
        :type app_service: AppService
        '''

        # Set the app service dependency.
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
            attributes: list[dict[str, object]] = [],
            constants: dict[str, str] = {},
            **kwargs,
        ) -> AppInterface:
        '''
        Add a new app interface configuration.

        :param id: The unique identifier for the app interface.
        :type id: str
        :param name: The display name of the app interface.
        :type name: str
        :param module_path: The module path for the app context implementation.
        :type module_path: str
        :param class_name: The class name for the app context implementation.
        :type class_name: str
        :param description: Optional human-readable description of the interface.
        :type description: str | None
        :param logger_id: Optional logger identifier (defaults to ``"default"``).
        :type logger_id: str
        :param feature_flag: Optional feature flag identifier (defaults to ``"default"``).
        :type feature_flag: str
        :param data_flag: Optional data flag identifier (defaults to ``"default"``).
        :type data_flag: str
        :param attributes: Optional list of attribute definitions for the interface.
        :type attributes: list[dict[str, object]]
        :param constants: Optional dictionary of constant values injected into the app context.
        :type constants: dict[str, str]
        :param kwargs: Additional keyword arguments forwarded to the model factory.
        :type kwargs: dict
        :return: The created ``AppInterface`` model instance.
        :rtype: AppInterface
        '''

        # Validate required parameters.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )
        self.verify_parameter(
            parameter=name,
            parameter_name='name',
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

        # Normalize logger_id, feature_flag, and data_flag to 'default' when falsy.
        normalized_logger_id = logger_id or 'default'
        normalized_feature_flag = feature_flag or 'default'
        normalized_data_flag = data_flag or 'default'

        # Ensure attributes and constants have sensible defaults.
        interface_attributes = attributes or []
        interface_constants = constants or {}

        # Construct the AppInterface model via the model factory.
        interface = ModelObject.new(
            AppInterface,
            id=id,
            name=name,
            module_path=module_path,
            class_name=class_name,
            description=description,
            logger_id=normalized_logger_id,
            feature_flag=normalized_feature_flag,
            data_flag=normalized_data_flag,
            attributes=interface_attributes,
            constants=interface_constants,
            **kwargs,
        )

        # Persist the new app interface via the app service.
        self.app_service.save(interface)

        # Return the created app interface.
        return interface
