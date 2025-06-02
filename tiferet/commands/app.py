# *** imports

# ** app
from .settings import *
from ..configs import (
    DEFAULT_APP_CONTEXT_DEPENDENCIES,
    DEFAULT_APP_CONTEXT_CONSTANTS,
    DEFAULT_APP_CONTEXT_DEPENDENCY
)
from ..models import ModelObject
from ..models.app import AppSettings, AppDependency
from ..contracts.app import AppRepository
from ..contexts import import_dependency, create_injector
from ..contexts.app import AppContext


# *** commands:

# ** command: load_app_settings
class LoadAppSettings(Command):
    '''
    A command to load the app settings from a repository.
    '''

    # * method: execute
    def execute(self,
                repo_module_path: str,
                repo_class_name: str,
                repo_params: Dict[str, Any] = {},
                app_name: str = None,
                **kwargs
                ) -> AppSettings:
        '''
        Execute the command.

        :param repo_module_path: The app repository module path.
        :type repo_module_path: str
        :param repo_class_name: The app repository class name.
        :type repo_class_name: str
        :param repo_params: The app repository parameters.
        :type repo_params: dict
        :param app_name: The name of the app to load settings for.
        :type app_name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: None
        '''

        # Import the app repository.
        try:
            
            # Import the app repository class.
            app_repo: AppRepository = import_dependency(
                repo_module_path, 
                repo_class_name
            )(**repo_params, **kwargs)
        
        # Handle the import error.
        # Raise an error if the import fails.
        except TiferetError as e:
            raise TiferetError(
                'APP_REPOSITORY_IMPORT_FAILED',
                f'Failed to import app repository: {e}.',
                str(e)
            )
        
        try:
            # Retrieve the app settings.
            settings: AppSettings = app_repo.get_settings(
                app_name=app_name
            )

            # Raise an error if the settings are not found.
            if not settings:
                raise TiferetError(
                    'APP_SETTINGS_NOT_FOUND',
                    f'App settings for {app_name} not found.'
                )

            # If the default app context is not set, set it to the default dependency.
            if not settings.get_dependency('app_context'):
                settings.add_dependency(**DEFAULT_APP_CONTEXT_DEPENDENCY)
            
        # Handle the app settings retrieval error should a critical error occur in the repository.
        except Exception as e:
            raise TiferetError(
                'APP_SETTINGS_LOADING_FAILED',
                f'Failed to load app settings: {e}.',
                str(e)
            )
        
        # Return the app settings.
        return settings


# ** command: load_app_context
class LoadAppContext(Command):
    '''
    A command to load an app instance from a repository.
    '''

    # * method: execute
    def execute(self,
                settings: AppSettings,
                dependencies: Dict[str, Any] = {},
                **kwargs
                ) -> AppContext:
        '''
        Execute the command.

        :param repo_module_path: The app repository module path.
        :type repo_module_path: str
        :param repo_class_name: The app repository class name.
        :type repo_class_name: str
        :param repo_params: The app repository parameters.
        :type repo_params: dict
        :param app_name: The name of the app to load settings for.
        :type app_name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: None
        '''  

        # Raise an error if the settings are not provided.
        if not settings:
            raise TiferetError(
                'APP_SETTINGS_NOT_PROVIDED',
                'App settings must be provided to load the app context.'
            )  

        # Raise an error if the app interface is invalid.
        if not settings.get_dependency('app_context'):
            raise TiferetError(
                'APP_SETTINGS_INVALID',
                settings.id,
            )

        # Get the dependencies for the app interface.
        dependencies.update(dict(
            app_name=settings.name,
            feature_flag=settings.feature_flag,
            data_flag=settings.data_flag,
            **settings.constants
        ))

        # Add the remaining dependencies from the app interface.
        dependencies.update({dep.attribute_id: import_dependency(
            dep.module_path, dep.class_name) for dep in settings.dependencies})
        
        # Add the default dependencies if they are not already present.
        for dep in DEFAULT_APP_CONTEXT_DEPENDENCIES:

            # Convert the dependency to a model object.
            dep_model = ModelObject.new(AppDependency, **dep)

            # If the dependency is not already present, add it to the dependencies.
            if dep_model.attribute_id not in dependencies:
                dependencies[dep_model.attribute_id] = import_dependency(
                    dep_model.module_path, dep_model.class_name
                )

        # Add the default app context constants to the dependencies.
        for const in DEFAULT_APP_CONTEXT_CONSTANTS:
            if const not in dependencies:
                dependencies[const] = DEFAULT_APP_CONTEXT_CONSTANTS[const]

        # Create the injector.
        injector = create_injector(settings.name, **dependencies, **kwargs)

        try:
            return getattr(injector, 'app_context')
        except Exception as e:
            raise TiferetError(
                'APP_CONTEXT_LOADING_FAILED',
                f'Failed to load app context: {e}.',
                str(e)
            )