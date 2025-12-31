# *** imports

# ** core
from typing import List, Dict, Any

# ** app
from ..assets.constants import APP_REPOSITORY_IMPORT_FAILED_ID
from ..commands import (
    ImportDependency,
    TiferetError,
    RaiseError
)
from ..commands.dependencies import create_injector, get_dependency
from ..contracts.app import *

# *** handlers

# ** handler: app_handler
class AppHandler(AppService):
    '''
    An app handler is a class that is used to manage app interfaces.
    '''

    # * attribute: app_repo
    app_repo: AppRepository

    # * init
    def __init__(self, app_repo: AppRepository = None, settings: Dict[str, Any] = {}):
        '''
        Initialize the app handler with an app repository.

        :param app_repo: The app repository to use for retrieving app interfaces.
        :type app_repo: AppRepository
        '''

        # Assign the app repository.
        # If an app repository is provided, use it.
        # If not, load the app repository using the provided settings.
        # If no settings are provided, load the default app repository.
        if app_repo:
            self.app_repo = app_repo
        elif settings:
            self.app_repo = self.load_app_repository(**settings)
        else:
            self.app_repo = self.load_app_repository()

    # * method: load_app_repository
    def load_app_repository(
        self, app_repo_module_path: str = 'tiferet.proxies.yaml.app',
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
        '''

        # Import the app repository.
        try:
            result = ImportDependency.execute(
                app_repo_module_path,
                app_repo_class_name
            )(**app_repo_params)

        # Raise an error if the import fails.
        except TiferetError as e:
            RaiseError.execute(
                APP_REPOSITORY_IMPORT_FAILED_ID,
                f'Failed to import app repository: {e}.',
                exception=str(e)
            )

        # Return the imported app repository.
        return result
    
    # * method: load_app_instance
    def load_app_instance(self, app_interface: AppInterfaceContract, default_attrs: List[AppAttributeContract] = []) -> Any:
        '''
        Load the app instance based on the provided app interface settings.

        :param app_interface: The app interface.
        :type app_interface: AppInterfaceContract
        :param default_attrs: The default configured attributes for the app.
        :type default_attrs: List[AppAttributeContract]
        :return: The app instance.
        :rtype: Any
        '''

         # Retrieve the app context dependency.
        dependencies = dict(
            app_context=ImportDependency.execute(
                app_interface.module_path,
                app_interface.class_name,
            ),
            logger_id=app_interface.logger_id,
        )

        # Add the remaining app context attributes and parameters to the dependencies.
        for attr in app_interface.attributes:
            dependencies[attr.attribute_id] = ImportDependency.execute(
                attr.module_path,
                attr.class_name,
            )
            for param, value in attr.parameters.items():
                dependencies[param] = value

        # Add the default attributes and parameters to the dependencies if they do not already exist in the dependencies.
        for attr in default_attrs:
            if attr.attribute_id not in dependencies:
                dependencies[attr.attribute_id] = ImportDependency.execute(
                    attr.module_path,
                    attr.class_name,
                )
                for param, value in attr.parameters.items():
                    dependencies[param] = value

        # Add the constants from the app interface to the dependencies.
        dependencies.update(app_interface.constants)

        # Create the injector.
        injector = create_injector.execute(
            app_interface.id, 
            dependencies,
            interface_id=app_interface.id
        )

        # Return the app interface context.
        return get_dependency.execute(
            injector,
            dependency_name='app_context',
        )
    
    # * method: get_app_interface
    def get_app_interface(self, interface_id: str) -> AppInterfaceContract:
        '''
        Get the app interface settings by ID.

        :param interface_id: The ID of the app interface.
        :type interface_id: str
        :return: The app interface.
        :rtype: AppInterfaceContract
        '''

        # Retrieve the app interface from the app repository.
        app_interface = self.app_repo.get_interface(interface_id)
        
        # Raise an error if the app interface is not found.
        if not app_interface:
            raise_error.execute(
                'APP_INTERFACE_NOT_FOUND',
                f'App interface not found: {interface_id}.',
                interface_id,
            )

        # Return the app interface.
        return app_interface
