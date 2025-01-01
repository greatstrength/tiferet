# *** imports

# ** app
from ..configs import *
from ..models.app import *
from ..repos.app import *

# ** app - contexts
from .request import RequestContext
from .feature import FeatureContext
from .error import ErrorContext
from .container import create_injector, import_dependency


# *** contexts

# ** context: app_context
class AppContext(Model):

    # * attribute: app_repo_module_path
    app_repo_module_path = StringType(
        required=True,
        metadata=dict(
            description='The application repository proxy module path.'
        ),
    )

    # * attribute: app_repo_class_name
    app_repo_class_name = StringType(
        required=True,
        metadata=dict(
            description='The application repository proxy class name.'
        ),
    )

    # * attribute: app_repo_parameters
    app_repo_parameters = DictType(
        StringType(),
        metadata=dict(
            description='The application repository parameters.'
        ),
    )

    # * method: init
    def __init__(self,
                 app_repo_module_path: str = 'tiferet.proxies.app_yaml',
                 app_repo_class_name: str = 'AppYamlProxy',
                 app_repo_parameters: Dict[str, str] = dict(
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

        # Initialize the model.
        super().__init__(dict(
            app_repo_module_path=app_repo_module_path,
            app_repo_class_name=app_repo_class_name,
            app_repo_parameters=app_repo_parameters
        ))

    # * method: run
    def run(self, interface_id: str, dependencies: Dict[str, Any] = {}, **kwargs) -> Any:
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
        app_interface = self.load_interface(interface_id, **dependencies)

        # Run the interface.
        return app_interface.run(**kwargs)

    # * method: load_interface
    def load_interface(self, interface_id: str, **dependencies) -> AppInterface:
        '''
        Load the application interface.

        :param interface_id: The interface ID.
        :type interface_id: str
        :param dependencies: The dependencies.
        :type dependencies: dict
        :return: The application interface.
        :rtype: AppInterface
        '''

        # Import the app repository.
        app_repo = self.import_app_repo(
            self.app_repo_module_path,
            self.app_repo_class_name,
            **self.app_repo_parameters
        )

        # Get the app interface.
        app_interface = app_repo.get_interface(interface_id)

        # Create the injector.
        injector = self.create_injector(app_interface, **dependencies)

        # Load the app interface context.
        return getattr(injector, 'app_context')

    # * method: import_app_repo
    def import_app_repo(self, module_path: str, class_name: str, **kwargs) -> AppRepository:
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

        # Try to import the module provided.
        try:
            return import_dependency(module_path, class_name)(**kwargs)

        # Return None if nothing comes up.
        except:
            return None

    # ** method: create_injector
    def create_injector(self, app_interface: AppInterface, **kwargs) -> Any:
        '''
        Create the injector.

        :param app_interface: The app interface.
        :type app_interface: AppInterface
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The injector.
        :rtype: Any
        '''

        # Retrieve the app context dependency.
        app_context = app_interface.get_dependency('app_context')

        # Get the dependencies for the app interface.
        dependencies = dict(
            interface_id=app_interface.id,
            app_name=app_interface.name,
            feature_flag=app_interface.feature_flag,
            data_flag=app_interface.data_flag,
            app_context=import_dependency(
                app_context.module_path,
                app_context.class_name,
            ),
            **app_interface.constants
        )

        # Add the remaining dependencies from the app interface.
        dependencies.update({dep.attribute_id: import_dependency(
            dep.module_path, dep.class_name) for dep in app_interface.dependencies})

        # Create the injector.
        return create_injector(app_interface.id, **dependencies, **kwargs)


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

    # * method: init
    def __init__(self, interface_id: str, app_name: str, feature_context: FeatureContext, error_context: ErrorContext):
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
        Execute the feature context.

        :param request: The request context.
        :type request: RequestContext
        '''

        # Execute feature context and return session.
        self.features.execute(request, **kwargs)

    # * method: handle_response
    def handle_response(self, request: RequestContext) -> Any:
        '''
        Handle the response.

        :param request: The request context.
        :type request: RequestContext
        :return: The response.
        :rtype: Any
        '''

        # Import the JSON module.
        import json

        # Return the response.
        return json.loads(request.result) if request.result else None

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
            self.execute_feature(request, **kwargs)

        # Handle error and return response if triggered.
        except Exception as e:
            print('Error:', e)
            return self.errors.handle_error(e)

        # Handle response.
        return self.handle_response(request)
