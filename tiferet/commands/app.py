# *** imports

# ** app
from .settings import *
from ..contracts.app import AppRepository
from ..contexts import import_dependency


# *** commands:


# ** command: import_app_repository
class ImportAppRepository(Command):
    '''
    A command to import the app repository.
    '''

    # * method: execute
    def execute(self,
                app_repo_module_path: str,
                app_repo_class_name: str,
                **kwargs
                ) -> AppRepository:
        '''
        Execute the command.

        :param app_repo_module_path: The app repository module path.
        :type app_repo_module_path: str
        :param app_repo_class_name: The app repository class name.
        :type app_repo_class_name: str
        :param kwargs: The command arguments.
        :type kwargs: dict
        :return: None
        '''

        # Import the app repository.
        try:
            
            # Import the app repository class.
            return import_dependency(
                app_repo_module_path, 
                app_repo_class_name
            )(**kwargs)
        
        # Handle the import error.
        # Raise an error if the import fails.
        except TiferetError as e:
            raise TiferetError(
                'APP_REPOSITORY_IMPORT_FAILED',
                f'Failed to import app repository: {e}.',
                str(e)
            )


# ** command: list_app_interfaces
class ListAppInterfaces(Command):
    '''
    A command to list the app interfaces.
    '''

    def __init__(self, app_repo: AppRepository):
        '''
        Initialize the command.

        :param app_repo: The app repository.
        :type app_repo: AppRepository
        '''

        # Set the app repository.
        self.app_repo = app_repo

    # * method: execute
    def execute(self, **kwargs):
        '''
        Execute the command.

        :param kwargs: The command arguments.
        :type kwargs: dict
        :return: The command result.
        :rtype: List[AppInterface]
        '''

        # List the app interfaces.
        try:
            return self.app_repo.list_interfaces()
        except Exception as e:
            raise TiferetError(
                'APP_INTERFACE_LOADING_FAILED',
                f'Failed to load app interfaces: {e}.',
                str(e)
            )
