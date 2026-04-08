"""Tiferet App Builders"""

# *** imports

# ** core
from typing import Dict, Any, List

# ** app
from ..contexts.app import AppInterfaceContext
from ..di import ServiceProvider, DependenciesServiceProvider
from .. import assets as a
from ..domain import (
    DomainObject,
    AppInterface,
    AppServiceDependency,
)
from ..events import (
    DomainEvent,
    ImportDependency,
    RaiseError,
)
from ..events.app import GetAppInterface

# *** constants

# ** constant: app_service_key
APP_SERVICE_KEY = 'app_service'

# *** builders

# ** builder: app_builder
class AppBuilder(object):
    '''
    The main application builder for Tiferet v2.0+.
    
    Responsible for loading the app service, preparing default services/constants,
    resolving interfaces, and running features.
    '''

    # * attribute: cache
    cache: Dict[str, Any]

    # * attribute: service_provider
    service_provider: ServiceProvider

    # * init
    def __init__(self):
        '''
        Initialize the AppBuilder with empty cache and default service provider.
        '''

        # Initialize the cache.
        self.cache = {}

        # Initialize the service provider.
        self.service_provider = self.create_service_provider()

    # * method: create_service_provider (static)
    @staticmethod
    def create_service_provider(
        provider_type: type = DependenciesServiceProvider,
        type_map: Dict[str, type] = None,
        **constants
    ) -> ServiceProvider:
        '''
        Create a service provider from a type map and constants.

        :param provider_type: The concrete provider class to instantiate.
        :type provider_type: type
        :param type_map: A dictionary mapping service IDs to their types.
        :type type_map: Dict[str, type]
        :param constants: Constant parameters to register in the provider.
        :type constants: dict
        :return: The configured service provider instance.
        :rtype: ServiceProvider
        '''

        # Create the provider and register service types/constants.
        provider = provider_type()
        if type_map:
            provider.add_services(type_map)
        if constants:
            provider.add_constants(constants)

        # Return the configured service provider.
        return provider

    # * method: load_app_service
    def load_app_service(
        self,
        module_path: str = a.const.DEFAULT_APP_SERVICE_MODULE_PATH,
        class_name: str = a.const.DEFAULT_APP_SERVICE_CLASS_NAME,
        **parameters
    ) -> 'AppBuilder':
        '''
        Load the application service and store it in the cache.

        :param module_path: The module path of the app service implementation.
        :type module_path: str
        :param class_name: The class name of the app service implementation.
        :type class_name: str
        :param parameters: Additional parameters to pass to the app service constructor.
        :type parameters: dict
        :return: The application builder instance (for chaining).
        :rtype: AppBuilder
        '''

        # Import and construct the app service.
        service_cls = ImportDependency.execute(module_path, class_name)
        app_service = service_cls(**parameters)

        # Add the app service to the cache.
        self.cache[APP_SERVICE_KEY] = app_service

        # Return self for method chaining.
        return self

    # * method: load_default_services
    def load_default_services(self) -> List[AppServiceDependency]:
        '''
        Load the default app service dependencies from configuration constants.

        :return: A list of default app service dependencies.
        :rtype: List[AppServiceDependency]
        '''

        # Build domain dependency models from the default service configuration.
        return [
            DomainObject.new(
                AppServiceDependency,
                **attr_data,
                validate=False,
            )
            for attr_data in a.const.DEFAULT_SERVICES
        ]

    # * method: load_app_instance
    def load_app_instance(self, app_interface: AppInterface) -> Any:
        '''
        Load the concrete app interface context instance.

        :param app_interface: The prepared app interface definition.
        :type app_interface: AppInterface
        :return: The resolved app interface context.
        :rtype: Any
        '''

        # Build the app interface dependencies map.
        try:
            dependencies = app_interface.get_service_type_mapping()

        # Raise a structured error if dependency mapping fails.
        except Exception as e:
            RaiseError.execute(
                a.const.APP_SERVICE_IMPORT_FAILED_ID,
                exception=str(e),
            )

        # Register the create_service_provider callable for downstream contexts.
        dependencies['create_service_provider'] = self.create_service_provider

        # Add dependencies to the service provider.
        self.service_provider.add_services(dependencies)

        # Resolve and return the app interface context.
        return self.service_provider.get_service('app_context')

    # * method: load_interface
    def load_interface(self, interface_id: str) -> AppInterfaceContext:
        '''
        Load and prepare the application interface context.

        :param interface_id: The interface ID.
        :type interface_id: str
        :return: The fully prepared application interface context.
        :rtype: AppInterfaceContext
        '''

        # Retrieve the app service from the cache.
        app_service = self.cache.get(APP_SERVICE_KEY)
        if not app_service:
            RaiseError.execute(
                a.const.APP_SERVICE_NOT_LOADED_ID,
                interface_id=interface_id,
            )

        # Load the default app service dependencies.
        default_services = self.load_default_services()

        # Get the app interface via the event.
        app_interface = DomainEvent.handle(
            GetAppInterface,
            dependencies=dict(app_service=app_service),
            interface_id=interface_id,
            default_services=default_services,
            default_constants=a.const.DEFAULT_CONSTANTS,
        )

        # Create the concrete app interface context.
        app_interface_context = self.load_app_instance(app_interface)

        # Verify that the resolved context is valid.
        if not isinstance(app_interface_context, AppInterfaceContext):
            RaiseError.execute(
                a.const.INVALID_APP_INTERFACE_TYPE_ID,
                f'App context for interface is not valid: {interface_id}.',
                interface_id=interface_id,
            )

        # Return the app interface context.
        return app_interface_context

    # * method: run
    def run(
        self,
        interface_id: str,
        feature_id: str,
        headers: Dict[str, str] = None,
        data: Dict[str, Any] = None,
        debug: bool = False,
        **kwargs
    ) -> Any:
        '''
        Run a feature on the specified interface.

        :param interface_id: The interface ID.
        :type interface_id: str
        :param feature_id: The feature ID.
        :type feature_id: str
        :param headers: The request headers.
        :type headers: Dict[str, str]
        :param data: The request data.
        :type data: Dict[str, Any]
        :param debug: Whether to run in debug mode.
        :type debug: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The response from the feature.
        :rtype: Any
        '''

        # Normalize request structures.
        headers = headers or {}
        data = data or {}

        # Load the interface.
        app_interface_context = self.load_interface(interface_id)

        # Run the interface.
        return app_interface_context.run(
            feature_id=feature_id,
            headers=headers,
            data=data,
            debug=debug,
            **kwargs
        )
