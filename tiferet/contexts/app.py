# *** imports

# ** app
from ..configs import *
from ..models.app import *
from ..repos.app import *

# ** app - contexts
from .request import RequestContext
from .feature import FeatureContext
from .error import ErrorContext
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
                 app_repo_module_path: str = 'tiferet.proxies.app_yaml',
                 app_repo_class_name: str = 'AppYamlProxy',
                 app_repo_parameters: Dict[str, Any] = dict(
                     app_config_file='app/configs/app.yml'
                 )):
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
        # Raise an error if the app repository cannot be imported.
        try:
            app_repo: AppRepository = import_dependency(app_repo_module_path, app_repo_class_name)(**app_repo_parameters)
        except Exception as e:
            raise AppRepositoryImportError(e)

        # Load the interfaces.
        # Raise an error if the interfaces cannot be loaded.
        try:
            interfaces = {interface.id: interface for interface in app_repo.list_interfaces()}
        except Exception as e:
            raise AppInterfacesLoadingError(e)
        
        # Initialize the model.
        super().__init__(dict(
            interfaces=interfaces
        ))

    # * method: run
    def run(self, interface_id: str, **kwargs) -> Any:
        '''
        Run the application interface.

        :param interface_id: The interface ID.
        :type interface_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The response.
        :rtype: Any
        '''

        # Get the app interface.
        app_interface = self.interfaces.get(interface_id)

        # Raise an error if the app interface is not found.
        if not app_interface:
            raise AppInterfaceNotFoundError(interface_id)

        # Load the interface context
        app_interface_context = self.load_interface(app_interface, **kwargs)

        # Run the interface.
        return app_interface_context.run(**kwargs)

    # * method: load_interface
    def load_interface(self, app_interface: AppInterface, dependencies: Dict[str, Any] = {}, **kwargs) -> AppInterface:
        '''
        Load the application interface.

        :param app_interface: The application interface.
        :type app_interface: AppInterface
        :param dependencies: The dependencies.
        :type dependencies: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The application interface.
        :rtype: AppInterface
        '''

        # Raise an error if the app interface is invalid.
        if not app_interface.get_dependency('app_context'):
            raise InvalidAppInterfaceError(app_interface.id)

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

        # Throw a data type invalid error if a value for a data key is not a string, integer, float, or boolean.
        for key, value in data.items():
            if not isinstance(value, (str, int, float, bool)):
                raise InvalidRequestDataError(key, value)
            
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
        try:
            self.features.execute(request, cache=self.cache, **kwargs)

        # Handle error and return response if triggered.
        except Exception as e:
            print('Error:', e)
            return self.errors.handle_error(e)

        # Handle response.
        return request.handle_response()


# *** exceptions

# ** exception: app_repository_import_error
class AppRepositoryImportError(TiferetError):
    '''
    An exception raised when the application repository cannot be imported.
    '''

    # * method: init
    def __init__(self, error: Exception):
        super().__init__(
            message=f'The application repository could not be imported: {str(error)}',
            error_code='APP_REPOSITORY_IMPORT_ERROR'
        )


# ** exception: app_interfaces_loading_error
class AppInterfacesLoadingError(TiferetError):
    '''
    An exception raised when the application interfaces cannot be loaded.
    '''

    # * method: init
    def __init__(self, error: Exception):
        super().__init__(
            message=f'The application interfaces could not be loaded: {str(error)}.',
            error_code='APP_INTERFACES_LOADING_ERROR',
        )


# ** exception: app_interface_not_found_error
class AppInterfaceNotFoundError(TiferetError):
    '''
    An exception raised when the application interface is not found.
    '''

    # * method: init
    def __init__(self, interface_id: str):
        super().__init__(
            message=f'The application interface was not found: {interface_id}',
            error_code='APP_INTERFACE_NOT_FOUND'
        )


# ** exception: invalid_app_interface_error
class InvalidAppInterfaceError(TiferetError):
    '''
    An exception raised when the application interface has no app context dependency.
    '''

    # * method: init
    def __init__(self, interface_id: str):
        super().__init__(
            message=f'The application interface is invalid: {interface_id}',
            error_code='INVALID_APP_INTERFACE'
        )



# ** exception: invalid_request_data_error
class InvalidRequestDataError(TiferetError):
    '''
    An exception raised when the request data is invalid.
    '''

    # * method: init
    def __init__(self, data_key: str, data_value: Any):
        super().__init__(
        message='The request data is invalid.',
        error_code='INVALID_REQUEST_DATA',
        *[data_key, str(data_value)]
    )