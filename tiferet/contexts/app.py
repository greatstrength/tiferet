# *** imports

# ** app
from ..configs import *
from ..commands.app import *
from ..models.app import *

# ** app - contexts
from .request import RequestContext
from .feature import FeatureContext
from .error import ErrorContext, raise_error
from .cache import CacheContext
from .container import create_injector, import_dependency


# *** contexts

# ** context: app_context
class AppContext(Model):

    # * attribute: interfaces
    interfaces = DictType(
        ModelType(AppInterface),
        required=True,
        metadata=dict(
            description='The application interfaces.'
        ),
    )

    # * method: init
    def __init__(self,
                 app_repo_module_path: str = DEFAULT_APP_REPO_MODULE_PATH,
                 app_repo_class_name: str = DEFAULT_APP_REPO_CLASS_NAME,
                 app_repo_parameters: Dict[str, Any] = DEFAULT_APP_REPO_PARAMETERS):
        '''
        Initialize the application context.

        :param app_repo_module_path: The application repository proxy module path.
        :type app_repo_module_path: str
        :param app_repo_class_name: The application repository proxy class name.
        :type app_repo_class_name: str
        :param app_repo_parameters: The application repository parameters.
        :type app_repo_parameters: dict
        '''

        # Import the app repository.
        app_repo = ServiceCommand.handle_command(
            ImportAppRepository,
            app_repo_module_path=app_repo_module_path,
            app_repo_class_name=app_repo_class_name,
            **app_repo_parameters
        )

        # Load the interfaces.
        interfaces = ServiceCommand.handle_command(
            ListAppInterfaces,
            dependencies=dict(
                app_repo=app_repo
            )
        )
        
        # Initialize the model.
        super().__init__(dict(
            interfaces={interface.id: interface for interface in interfaces}
        ))

    # * method: load_interface
    def load_interface(self, interface_id: str, dependencies: Dict[str, Any] = {}, **kwargs) -> AppInterface:
        '''
        Load the application interface.

        :param interface_id: The interface ID.
        :type interface_id: str
        :param dependencies: The dependencies.
        :type dependencies: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The application interface.
        :rtype: AppInterface
        '''

        # Get the app interface.
        app_interface = self.interfaces.get(interface_id)

        # Raise an error if the app interface is not found.
        if not app_interface:
            raise_error(
                'APP_INTERFACE_NOT_FOUND',
                interface_id
            )

        # Raise an error if the app interface is invalid.
        if not app_interface.get_dependency('app_context'):
            raise_error(
                'APP_INTERFACE_INVALID',
                app_interface.id,
            )

        # Get the dependencies for the app interface.
        dependencies.update(dict(
            interface_id=app_interface.id,
            app_name=app_interface.name,
            feature_flag=app_interface.feature_flag,
            data_flag=app_interface.data_flag,
            **app_interface.constants
        ))

        # Add the remaining dependencies from the app interface.
        dependencies.update({dep.attribute_id: import_dependency(
            dep.module_path, dep.class_name) for dep in app_interface.dependencies})
        
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
        injector = create_injector(app_interface.name, **dependencies, **kwargs)

        # Load the app interface context.
        return getattr(injector, 'app_context')


# ** context: app_interface_context
class AppInterfaceContext(Model):
    '''
    The application interface context is a class that is used to create and run the application interface.
    '''

    # * attribute: interface_id
    interface_id = StringType(
        required=True,
        metadata=dict(
            description='The interface ID.'
        ),
    )

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The application name.'
        ),
    )

    # * field: features
    features = ModelType(
        FeatureContext,
        required=True,
        metadata=dict(
            description='The feature context.'
        ),
    )

    # * field: errors
    errors = ModelType(
        ErrorContext,
        required=True,
        metadata=dict(
            description='The error context.'
        ),
    )

    # * attribute: cache
    cache = ModelType(
        CacheContext,
        metadata=dict(
            description='The cache context.'
        ),
    )

    # * method: init
    def __init__(self, interface_id: str, app_name: str, feature_context: FeatureContext, error_context: ErrorContext, cache_context: CacheContext = CacheContext()):
        '''
        Initialize the application interface context.

        :param interface_id: The interface ID.
        :type interface_id: str
        :param app_name: The application name.
        :type app_name: str
        :param feature_context: The feature context.
        :type feature_context: FeatureContext
        :param error_context: The error context.
        :type error_context: ErrorContext
        '''

        # Initialize the model.
        super().__init__(dict(
            interface_id=interface_id,
            name=app_name
        ))
        self.cache = cache_context
        self.features = feature_context
        self.errors = error_context

    # * method: parse_request
    def parse_request(self,
        feature_id: str,
        data: Dict[str, Any] = {},
        headers: Dict[str, str] = {},
        **kwargs
    ) -> RequestContext:
        '''
        Parse the incoming request.

        :param feature_id: The feature ID.
        :type feature_id: str
        :param data: The data.
        :type data: dict
        :param headers: The headers.
        :type headers: dict
        :return: The request context.
        :rtype: RequestContext
        '''

        # Parse the incoming data type value.
        for key, value in data.items():

            # If if the value is a string, integer, float, or boolean, continue to the next iteration.
            if isinstance(value, (str, int, float, bool)):
                continue

            # If the value is a list, dictionary, convert it to a JSON string.
            elif isinstance(value, (list, dict)):
                data[key] = json.dumps(value)

            # If the value is a model, convert it to a primitive dictionary and then to a JSON string.
            elif isinstance(value, Model):
                data[key] = json.dumps(value.to_primitive())

            # If the value is not a string, integer, float, boolean, list, dictionary, or model, raise an error.
            else:
                raise_error(
                    'REQUEST_DATA_INVALID',
                    key,
                    str(value)
                )
            
        # Add app interface id and name to the headers.
        headers.update(dict(
            app_interface_id=self.interface_id,
            app_name=self.name
        ))

        # Parse request.
        return RequestContext(
            feature_id=feature_id,
            data=data,
            headers=headers,
            **kwargs
        )
    
    # * method: execute_feature
    def execute_feature(self, request: RequestContext, **kwargs):
        '''
        Execute the feature request.

        :param request: The request context object.
        :type
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Execute feature context.
        self.features.execute(request, cache=self.cache, **kwargs)

    # * method: handle_error
    def handle_error(self, exception: Exception, **kwargs) -> Any:
        '''
        Handle passed exceptions as an error.

        :param exception: An exception thrown during a feature request.
        :type exception: Exception
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The error data.
        :rtype: Any
        '''
        
        print('Error:', exception)
        return self.errors.handle_error(exception, **kwargs)
    
    # * method: handle_response
    def handle_response(self, request: RequestContext, **kwargs) -> Any:
        '''
        Handle the application response.

        :param request: The request context object.
        :type request: RequestContext
        :return: The response data.
        :rtype: dict
        '''

        # Handle the response from the request.
        return request.handle_response(**kwargs)

    # * method: run
    def run(self, feature_id: str, **kwargs):
        '''
        Run the application interface.

        :param feature_id: The feature ID.
        :type feature_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Parse request.
        request = self.parse_request(feature_id, **kwargs)

        # Execute feature context and return session.
        # Handle error and return response if triggered.
        try:
            self.execute_feature(request, **kwargs)
        except Exception as e:
            return self.handle_error(e)

        # Handle response.
        return self.handle_response(request)
