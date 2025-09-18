# *** imports

# ** app
from .settings import *
from .core import import_dependency
from ..contracts.app import AppRepository, AppInterface


# *** commands:

# ** command: import_app_repository
class ImportAppRepository(Command):
    '''
    A command to import an app repository.
    '''

    # * method: execute
    def execute(self,
                app_repo_module_path: str = 'tiferet.proxies.yaml.app',
                app_repo_class_name: str = 'AppYamlProxy',
                app_repo_params: Dict[str, Any] = dict(
                    app_config_file='app/configs/app.yml'
                ),
                **kwargs
                ) -> AppRepository:
        '''
        Execute the command.

        :param app_repo_module_path: The application repository module path.
        :type app_repo_module_path: str
        :param app_repo_class_name: The application repository class name.
        :type app_repo_class_name: str
        :param app_repo_params: The application repository parameters.
        :type app_repo_params: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The application repository instance.
        :rtype: AppRepository
        :raises TiferetError: If the import fails.
        '''

        # Import the app repository.
        try:
            result = import_dependency.execute(
                app_repo_module_path,
                app_repo_class_name
            )(**app_repo_params)

        # Raise an error if the import fails.
        except TiferetError as e:
            self.raise_error(
                'APP_REPOSITORY_IMPORT_FAILED',
                f'Failed to import app repository: {e}.',
                str(e)
            )

        # Return the imported app repository.
        return result


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
                'APP_INTERFACE_NOT_FOUND',
                f'App interface with ID {interface_id} not found.'
            )

        # Return the loaded application interface.
        return interface