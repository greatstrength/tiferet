# *** imports

# ** core
from typing import Dict, Any

# ** app
from ..commands import (
    import_dependency,
    TiferetError,
    raise_error
)
from ..commands.dependencies import create_injector, get_dependency
from ..contracts.app import *


# *** handlers

# ** handler: app_handler
class AppHandler(AppService):
    '''
    An app handler is a class that is used to manage app interfaces.
    '''

    # * method: load_app_repository
    def load_app_repository(self, app_repo_module_path: str = 'tiferet.proxies.yaml.app',
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
            result = import_dependency.execute(
                app_repo_module_path,
                app_repo_class_name
            )(**app_repo_params)

        # Raise an error if the import fails.
        except TiferetError as e:
            raise_error.execute(
                'APP_REPOSITORY_IMPORT_FAILED',
                f'Failed to import app repository: {e}.',
                str(e)
            )

        # Return the imported app repository.
        return result
    
    # * method: load_app_instance
    def load_app_instance(self, app_interface: AppInterface, default_attrs: List[AppAttribute] = []) -> Any:
        '''
        Load the app instance based on the provided app interface settings.

        :param app_interface: The app interface.
        :type app_interface: AppInterface
        :param default_attrs: The default configured attributes for the app.
        :type default_attrs: List[AppAttribute]
        :return: The app instance.
        :rtype: Any
        '''

         # Retrieve the app context dependency.
        dependencies = dict(
            app_context=import_dependency.execute(
                app_interface.module_path,
                app_interface.class_name,
            ),
            logger_id=app_interface.logger_id,
        )

        # Add the remaining app context attributes and parameters to the dependencies.
        for attr in app_interface.attributes:
            dependencies[attr.attribute_id] = import_dependency.execute(
                attr.module_path,
                attr.class_name,
            )
            for param, value in attr.parameters.items():
                dependencies[param] = value

        # Add the default attributes and parameters to the dependencies if they do not already exist in the dependencies.
        for attr in default_attrs:
            if attr.attribute_id not in dependencies:
                dependencies[attr.attribute_id] = import_dependency.execute(
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