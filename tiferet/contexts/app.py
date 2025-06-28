# *** imports

# ** core
from typing import Dict, Any

# ** app
from .feature import FeatureContext
from .error import ErrorContext
from ..models.feature import Request
from ..commands import (
    Command,
    ModelObject,
    import_dependency,
    TiferetError
)
from ..commands.app import (
    AppInterface,
    AppRepository,
    ImportAppRepository
)
from ..commands.dependencies import create_injector, Injector


# *** contexts

# ** context: app_context
class AppContext(object):

    # * attribute: settings
    settings: Dict[str, Any]

    # * method: init
    def __init__(self, settings: Dict[str, Any] = {}):
        '''
        Initialize the application context.
        
        :param settings: The application settings.
        :type settings: dict
        '''
        
        # Assign settings attribute.
        self.settings = settings

    # * method: import_app_repo
    def import_app_repo(self) -> AppRepository:
        '''
        Import the app repository.

        :param module_path: The module path.
        :type module_path: str
        :param class_name: The class name.
        :type class_name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The app repository.
        :rtype: AppRepository
        '''

        # Run and return the import app repository command.
        return Command.handle(
            ImportAppRepository,
            **self.settings
        )
    
    # * method: get_interface_settings
    def get_interface_settings(self, interface_id: str) -> AppInterface:
        '''
        Get the settings for the application interface.

        :param interface_id: The interface ID.
        :type interface_id: str
        :return: The application interface settings.
        :rtype: AppInterface
        '''

        # Import the app repository.
        app_repo = self.import_app_repo()

        # Get the app interface.
        return app_repo.get_interface(interface_id)

    # ** method: create_app_injector
    def create_app_injector(self, app_interface: AppInterface) -> Injector:
        '''
        Create the app dependency injector.

        :param app_interface: The app interface.
        :type app_interface: AppInterface
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The dependencies injector.
        :rtype: Injector
        '''

        # Retrieve the app context dependency.
        dependencies = dict(
            app_context=import_dependency.execute(
                app_interface.module_path,
                app_interface.class_name,
            )
        )

        # Add the remaining app context attributes.
        for attr in app_interface.attributes:
            dependencies[attr.attribute_id] = import_dependency.execute(
                attr.module_path,
                attr.class_name,
            )

        # Create the injector.
        injector = create_injector.execute(
            app_interface.id, 
            dependencies,
            interface_id=app_interface.id,
            **app_interface.constants
        )

        # Return the injector.
        return injector
    
       # * method: load_interface
    def load_interface(self, interface_id: str) -> 'AppInterfaceContext':
        '''
        Load the application interface.

        :param interface_id: The interface ID.
        :type interface_id: str
        :return: The application interface context.
        :rtype: AppInterfaceContext
        '''

        # Get the app interface.
        app_interface = self.get_interface_settings(interface_id)

        # Create the app injector.
        injector = self.create_app_injector(app_interface)

        # Load the app interface context.
        return getattr(injector, 'app_context')

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

    # * method: init
    def __init__(self, interface_id: str, features: FeatureContext, errors: ErrorContext):
        '''
        Initialize the application interface context.

        :param interface_id: The interface ID.
        :type interface_id: str
        :param app_name: The application name.
        :type app_name: str
        :param features: The feature context.
        :type features: FeatureContext
        :param errors: The error context.
        :type errors: ErrorContext
        '''

        # Assign instance variables.
        self.interface_id = interface_id
        self.features = features
        self.errors = errors

    # * method: parse_request
    def parse_request(self, headers: Dict[str, str] = {}, data: Dict[str, Any] = {}) -> Request:
        '''
        Parse the incoming request.

        :param headers: The request headers.
        :type headers: dict
        :param data: The request data.
        :type data: dict
        :return: The parsed request.
        :rtype: Request
        '''

        # Add the interface id to the request headers.
        headers.update(dict(
            interface_id=self.interface_id,
        ))

        # Create the request model object.
        request = ModelObject.new(
            Request,
            headers=headers,
            data=data,
        )

        # Return the request model object.
        return request
    
    # * method: execute_feature
    def execute_feature(self, feature_id: str, request: Request, **kwargs):
        '''
        Execute the feature context.

        :param feature_id: The feature identifier.
        :type feature_id: str
        :param request: The request.
        :type request: Request
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
        
        # Print the error to the console.
        print('Error:', error)

        # Handle the error and return the response.
        return self.errors.handle_error(error)

    # * method: handle_response
    def handle_response(self, request: Request) -> Any:
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
        
        # Parse request.
        request = self.parse_request(headers, data)

        # Execute feature context and return session.
        try:
            self.execute_feature(feature_id, request, **kwargs)

        # Handle error and return response if triggered.
        except TiferetError as e:
            return self.handle_error(e)

        # Handle response.
        return self.handle_response(request)
