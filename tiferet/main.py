# *** imports

# ** core
from typing import Dict, Any

# ** app
from .configs import *
from .events import DomainEvent
from .events.app import *


# *** classes

# ** class: app_manager
class AppManager(object):

    # * attribute: settings
    settings: Dict[str, Any] = {}

    # * method: init
    def __init__(self, settings: Dict[str, Any] = DEFAULT_APP_MANAGER_SETTINGS):
        '''
        Initialize the application context.

        :param settings: The application settings.
        :type settings: dict
        '''

        # Set the application settings.
        self.settings = settings

    # * method: load_settings
    def load_settings(self, app_name: str, **kwargs) -> AppSettings:
        '''
        Load the application settings.

        :param app_name: The name of the application.
        :type app_name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The application settings.
        :rtype: AppSettings
        '''

        # Load the application settings.
        return DomainEvent.handle(
            LoadAppSettings,
            **self.settings,
            app_name=app_name,
            **kwargs
        )

    # * method: load_instance
    def load_instance(self, app_name: str, dependencies: Dict[str, Any] = {}, **kwargs) -> AppContext:
        '''
        Load an instance of the application.

        :param app_name: The name of the application.
        :type app_name: str
        :param dependencies: The dependencies for the application interface.
        :type dependencies: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The application instance context.
        :rtype: AppInstanceContext
        '''

        # Load the application settings.
        settings = self.load_settings(app_name, **kwargs)

        # Execute the command to load the app instance.
        return DomainEvent.handle(
            LoadAppContext,
            settings=settings,
            dependencies=dependencies,
            **kwargs
        )

    # * method: execute_feature
    def execute_feature(self, app_name: str, feature_id: str, dependencies: Dict[str, Any] = {}, **kwargs) -> Any:
        '''
        Execute a feature of the application.

        :param app_name: The name of the application.
        :type app_name: str
        :param feature_id: The ID of the feature to execute.
        :type feature_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of the feature execution.
        :rtype: Any
        '''

        # Load the application instance.
        instance = self.load_instance(app_name, dependencies)

        # Execute the feature in the application instance.
        try:
            return instance.execute_feature(feature_id, **kwargs)
        except Exception as e:
            # Handle any exceptions that occur during feature execution.
            return instance.handle_error(e, **kwargs)