# *** imports

# ** app
from .settings import *
from .core import import_dependency
from ..contracts.app import AppRepository


# *** commands:

# ** command: import_app_repository
class ImportAppRepository(Command):
    '''
    A command to import an app repository.
    '''

    # * method: execute
    def execute(self,
                app_repo_module_path: str = 'tiferet.proxies.app.yaml',
                app_repo_class_name: str = 'AppYamlProxy',
                app_repo_params: Dict[str, Any] = {},
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

            # Import the app repository class.
            return import_dependency.execute(
                app_repo_module_path,
                app_repo_class_name
            )(**app_repo_params)

        # Handle the import error.
        # Raise an error if the import fails.
        except TiferetError as e:
            self.raise_error(
                'APP_REPOSITORY_IMPORT_FAILED',
                f'Failed to import app repository: {e}.',
                str(e)
            )
       