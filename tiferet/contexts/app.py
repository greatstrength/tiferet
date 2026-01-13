"""Tiferet App Contexts"""

# *** imports

# ** core
from typing import Dict, Any, List

# ** app
from .feature import FeatureContext
from .error import ErrorContext
from .logging import LoggingContext
from .request import RequestContext
from ..assets import TiferetError
from ..assets.constants import (
    DEFAULT_ATTRIBUTES,
    APP_REPOSITORY_IMPORT_FAILED_ID,
)
from ..models import (
    ModelObject,
    AppAttribute,
)
from ..contracts.app import AppRepository
from ..commands import (
    Command,
    ImportDependency,
    TiferetError as CommandTiferetError,
    RaiseError,
)
from ..commands.dependencies import (
    create_injector,
    get_dependency,
)
from ..commands.app import GetAppInterface
from ..configs import TiferetError as LegacyTiferetError

# *** contexts

# ** context: app_manager_context
class AppManagerContext(object):
    '''
    The AppManagerContext is responsible for managing the application context.
    It provides methods to load the application interface and run features.
    '''

    # * attribute: settings
    settings: Dict[str, Any]

    # * init
    def __init__(self, settings: Dict[str, Any] = {}):
        '''
        Initialize the AppManagerContext with application settings.

        :param settings: The application settings used to configure the app repository.
        :type settings: dict
        '''

        # Set the settings.
        self.settings = settings

    # * method: load_app_repo
    def load_app_repo(self) -> AppRepository:
        '''
        Load the application repository using the configured settings.

        :return: The application repository instance.
        :rtype: AppRepository
        '''

        # Resolve repository module path, class name, and parameters from settings with defaults.
        app_repo_module_path = self.settings.get('app_repo_module_path', 'tiferet.proxies.yaml.app')
        app_repo_class_name = self.settings.get('app_repo_class_name', 'AppYamlProxy')
        app_repo_params = self.settings.get('app_repo_params', dict(
            app_config_file='app/configs/app.yml'
        ))

        # Import and construct the app repository.
        try:
            repository_cls = ImportDependency.execute(
                app_repo_module_path,
                app_repo_class_name,
            )
            app_repo: AppRepository = repository_cls(**app_repo_params)

        # Wrap import failures in a structured Tiferet error.
        except CommandTiferetError as e:
            RaiseError.execute(
                APP_REPOSITORY_IMPORT_FAILED_ID,
                f'Failed to import app repository: {e}.',
                exception=str(e),
            )

        # Return the imported app repository.
        return app_repo

    # * method: load_default_attributes
    def load_default_attributes(self) -> List[AppAttribute]:
        '''
        Load the default app attributes from the configuration constants.

        :return: A list of default app attributes.
        :rtype: List[AppAttribute]
        '''

        # Retrieve the default attributes from the configuration constants.
        return [
            ModelObject.new(
                AppAttribute,
                **attr_data,
                validate=False,
            )
            for attr_data in DEFAULT_ATTRIBUTES
        ]

    # * method: load_app_instance
    def load_app_instance(self, app_interface: Any, default_attrs: List[AppAttribute]) -> Any:
        '''
        Load the app instance based on the provided app interface settings.

        :param app_interface: The app interface definition.
        :type app_interface: Any
        :param default_attrs: The default configured attributes for the app.
        :type default_attrs: List[AppAttribute]
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

        # Add the remaining app context attributes and parameters to the dependencies.
        for attr in app_interface.attributes:
            dependencies[attr.attribute_id] = ImportDependency.execute(
                attr.module_path,
                attr.class_name,
            )
            for param, value in attr.parameters.items():
                dependencies[param] = value

        # Add the default attributes and parameters to the dependencies if they do not already exist.
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
            interface_id=app_interface.id,
        )

        # Return the app interface context.
        return get_dependency.execute(
            injector,
            dependency_name='app_context',
        )

    # * method: load_interface
    def load_interface(self, interface_id: str) -> 'AppInterfaceContext':
        '''
        Load the application interface.

        :param interface_id: The interface ID.
        :type interface_id: str
        :return: The application interface context.
        :rtype: AppInterfaceContext
        '''

        # Load the app repository or service implementation.
        app_repo: AppRepository = self.load_app_repo()

        # Get the app interface settings via the AppService abstraction.
        app_interface = Command.handle(
            GetAppInterface,
            dependencies=dict(
                app_service=app_repo,
            ),
            interface_id=interface_id,
        )

        # Retrieve the default attributes from the configuration.
        default_attrs = self.load_default_attributes()

        # Create the app interface context.
        app_interface_context = self.load_app_instance(app_interface, default_attrs=default_attrs)

        # Verify that the app interface context is valid.
        if not isinstance(app_interface_context, AppInterfaceContext):
            raise TiferetError(
                'APP_INTERFACE_INVALID',
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
        :param dependencies: The dependencies.
        :type dependencies: dict
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

# ** context: app_interface_context
class AppInterfaceContext(object): 
    '''
    The application interface context is a class that is used to create and run the application interface.
    '''

    # * attribute: interface_id
    interface_id: str

    # * attribute: features
    features: FeatureContext

    # * attribute: errors
    errors: ErrorContext

    # * attribute: logging
    logging: LoggingContext

    # * init
    def __init__(self, interface_id: str, features: FeatureContext, errors: ErrorContext, logging: LoggingContext):
        '''
        Initialize the application interface context.

        :param interface_id: The interface ID.
        :type interface_id: str
        :param features: The feature context.
        :type features: FeatureContext
        :param errors: The error context.
        :type errors: ErrorContext
        '''

        # Assign instance variables.
        self.interface_id = interface_id
        self.features = features
        self.errors = errors
        self.logging = logging

    # * method: parse_request
    def parse_request(self, headers: Dict[str, str] = {}, data: Dict[str, Any] = {}, feature_id: str = None) -> RequestContext:
        '''
        Parse the incoming request.

        :param headers: The request headers.
        :type headers: dict
        :param data: The request data.
        :type data: dict
        :param feature_id: The feature identifier if provided.
        :type feature_id: str
        :return: The parsed request as a request context.
        :rtype: RequestContext
        '''

        # Add the interface id to the request headers.
        headers.update(dict(
            interface_id=self.interface_id,
        ))

        # Create the request context object.
        request = RequestContext(
            headers=headers,
            data=data,
            feature_id=feature_id,
        )

        # Return the request model object.
        return request

    # * method: execute_feature
    def execute_feature(self, feature_id: str, request: RequestContext, **kwargs):
        '''
        Execute the feature context.

        :param feature_id: The feature identifier.
        :type feature_id: str
        :param request: The request context object.
        :type request: RequestContext
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Add the feature id to the request headers.
        request.headers.update(dict(
            feature_id=feature_id
        ))

        # Execute feature context and return session.
        self.features.execute_feature(feature_id, request, **kwargs)

    # * method: handle_error
    def handle_error(self, error: Exception) -> Any:
        '''
        Handle the error and return the response.

        :param error: The error to handle.
        :type error: Exception
        :return: The error response.
        :rtype: Any
        '''

        # If the error is not a TiferetError, wrap it in one.
        if not isinstance(error, TiferetError):
            error = TiferetError(
                'APP_ERROR',
                f'An error occurred in the app: {str(error)}',
                error=str(error)
            )

        # Handle the error and return the response.
        return self.errors.handle_error(error)

    # * method: handle_response
    def handle_response(self, request: RequestContext) -> Any:
        '''
        Handle the response from the request.

        :param request: The request context.
        :type request: RequestContext
        :return: The response.
        :rtype: Any
        '''

        # Handle the response and return it.
        return request.handle_response()

    # * method: run
    def run(self, 
            feature_id: str, 
            headers: Dict[str, str] = {}, 
            data: Dict[str, Any] = {},
            **kwargs) -> Any:
        '''
        Run the application interface by executing the feature.

        :param feature_id: The feature identifier.
        :type feature_id: str
        :param headers: The request headers.
        :type headers: dict
        :param data: The request data.
        :type data: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Create the logger for the app interface context.
        logger = self.logging.build_logger()

        # Parse request.
        logger.debug(f'Parsing request for feature: {feature_id}')
        request = self.parse_request(headers, data, feature_id)

        # Execute feature context and return session.
        try:
            logger.info(f'Executing feature: {feature_id}')
            logger.debug(f'Executing feature: {feature_id} with request: {request.data}')
            self.execute_feature(
                feature_id=feature_id, 
                request=request, 
                logger=logger,
                **kwargs)

        # Handle error and return response if triggered.
        except (TiferetError, LegacyTiferetError) as e:
            logger.error(f'Error executing feature {feature_id}: {str(e)}')
            return self.handle_error(e)

        # Handle response.
        logger.debug(f'Feature {feature_id} executed successfully, handling response.')
        return self.handle_response(request)

# ** context: app_context (obsolete)
class AppContext(AppManagerContext):
    '''
    The AppContext is an obsolete class that extends the AppManagerContext.
    It is kept for backward compatibility but should not be used in new code.
    '''

    # * init
    def __init__(self, settings: Dict[str, Any] = {}):
        '''
        Initialize the obsolete AppContext.

        :param settings: The application settings.
        :type settings: dict
        '''

        super().__init__(settings)
