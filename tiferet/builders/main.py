"""Tiferet App Builders"""

# *** imports

# ** core
from typing import Dict, Any, List

# ** app
from ..contexts.app import AppInterfaceContext
from ..assets import TiferetError
from .. import assets as a
from ..domain import (
    DomainObject,
    AppServiceDependency,
)
from ..events import (
    DomainEvent,
    ImportDependency,
    RaiseError,
)
from ..events.dependencies import (
    create_injector,
    get_dependency,
)
from ..events.app import GetAppInterface

# *** constants

# ** constant: app_service_key
APP_SERVICE_KEY = 'app_service'

# *** builders

# ** builder: app_builder
class AppBuilder(object):
    '''
    The AppBuilder is responsible for managing the application context.
    It provides methods to load the application interface and run features.
    '''

    # * attribute: cache
    cache: Dict[str, Any]

    # * init
    def __init__(self):
        '''
        Initialize the AppBuilder.
        '''

        # Initialize the cache.
        self.cache = {}

    # * method: load_app_service
    def load_app_service(self,
            module_path: str = a.const.DEFAULT_APP_SERVICE_MODULE_PATH,
            class_name: str = a.const.DEFAULT_APP_SERVICE_CLASS_NAME,
            **parameters
        ):
        '''
        Load the application service using the provided module path, class name, and parameters.

        :param module_path: The module path of the app service implementation.
        :type module_path: str
        :param class_name: The class name of the app service implementation.
        :type class_name: str
        :param parameters: Additional parameters to pass to the app service constructor.
        :type parameters: dict
        :return: The application service instance.
        :rtype: Any
        '''

        # Import and construct the app service.
        try:
            service_cls = ImportDependency.execute(
                module_path,
                class_name,
            )
            app_service = service_cls(**parameters)

        # Wrap import failures in a structured Tiferet error.
        except TiferetError as e:
            RaiseError.execute(
                a.const.APP_REPOSITORY_IMPORT_FAILED_ID,
                f'Failed to import app service: {e}.',
                exception=str(e),
            )

        # Add the app service to the cache.
        self.cache[APP_SERVICE_KEY] = app_service

        # Return the app service.
        return app_service

    # * method: load_default_services
    def load_default_services(self) -> List[AppServiceDependency]:
        '''
        Load the default app service dependencies from the configuration constants.

        :return: A list of default app service dependencies.
        :rtype: List[AppServiceDependency]
        '''

        # Retrieve the default service dependencies from the configuration constants.
        return [
            DomainObject.new(
                AppServiceDependency,
                **attr_data,
                validate=False,
            )
            for attr_data in a.const.DEFAULT_ATTRIBUTES
        ]

    # * method: load_app_instance
    def load_app_instance(self, app_interface: Any, default_services: List[AppServiceDependency]) -> Any:
        '''
        Load the app instance based on the provided app interface settings.

        :param app_interface: The app interface definition.
        :type app_interface: Any
        :param default_services: The default configured service dependencies for the app.
        :type default_services: List[AppServiceDependency]
        :return: The app interface context instance.
        :rtype: Any
        '''

        # Retrieve the app context dependency and logger id.
        dependencies = dict(
            app_context=ImportDependency.execute(
                app_interface.module_path,
                app_interface.class_name,
            ),
            logger_id=getattr(app_interface, 'logger_id', None),
        )

        # Add the remaining app context service dependencies and parameters.
        for dep in app_interface.services:
            dependencies[dep.attribute_id] = ImportDependency.execute(
                dep.module_path,
                dep.class_name,
            )
            for param, value in dep.parameters.items():
                dependencies[param] = value

        # Add the default service dependencies and parameters if they do not already exist.
        for dep in default_services:
            if dep.attribute_id not in dependencies:
                dependencies[dep.attribute_id] = ImportDependency.execute(
                    dep.module_path,
                    dep.class_name,
                )
                for param, value in dep.parameters.items():
                    dependencies[param] = value

        # Add the constants from the app interface to the dependencies.
        dependencies.update(app_interface.constants)

        # Create the injector.
        injector = create_injector.execute(
            app_interface.id,
            dependencies,
            interface_id=app_interface.id,
        )

        # Return the app interface context.
        return get_dependency.execute(
            injector,
            dependency_name='app_context',
        )

    # * method: load_interface
    def load_interface(self, interface_id: str) -> AppInterfaceContext:
        '''
        Load the application interface.

        :param interface_id: The interface ID.
        :type interface_id: str
        :return: The application interface context.
        :rtype: AppInterfaceContext
        '''

        # Retrieve the app service from the cache.
        app_service = self.cache[APP_SERVICE_KEY]

        # Get the app interface settings via the AppService abstraction.
        app_interface = DomainEvent.handle(
            GetAppInterface,
            dependencies=dict(
                app_service=app_service,
            ),
            interface_id=interface_id,
        )

        # Retrieve the default service dependencies from the configuration.
        default_services = self.load_default_services()

        # Create the app interface context.
        app_interface_context = self.load_app_instance(app_interface, default_services=default_services)

        # Verify that the app interface context is valid.
        if not isinstance(app_interface_context, AppInterfaceContext):
            RaiseError.execute(
                a.const.INVALID_APP_INTERFACE_TYPE_ID,
                f'App context for interface is not valid: {interface_id}.',
                interface_id=interface_id,
            )

        # Return the app interface context.
        return app_interface_context

    # * method: run
    def run(self,
            interface_id: str,
            feature_id: str,
            headers: Dict[str, str] = {},
            data: Dict[str, Any] = {},
            debug: bool = False,
            **kwargs
        ) -> Any:
        '''
        Run the application interface.

        :param interface_id: The interface ID.
        :type interface_id: str
        :param feature_id: The feature ID.
        :type feature_id: str
        :param headers: The request headers.
        :type headers: dict
        :param data: The request data.
        :type data: dict
        :param debug: Whether to run in debug mode.
        :type debug: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The response.
        :rtype: Any
        '''

        # Load the interface.
        app_interface = self.load_interface(interface_id)

        # Run the interface.
        return app_interface.run(
            feature_id, 
            headers, 
            data, 
            debug=debug,
            **kwargs
        )
