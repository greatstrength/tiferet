# *** imports

# ** app
from .container import ContainerContext
from .cache import CacheContext
from .request import RequestContext
from ..handlers.feature import (
    FeatureHandler,
    FeatureService
)
from ..models.feature import Feature, FeatureCommand
from ..commands import *

# *** contexts

# ** context: feature_context
class FeatureContext(object):

    # * attribute: container
    container: ContainerContext

    # * attribute: cache
    cache: CacheContext

    # * attribute: feature_service
    feature_service: FeatureService

    # * attribute: feature_handler
    feature_handler: FeatureHandler


    # * method: init
    def __init__(self, 
            feature_service: FeatureService,
            container: ContainerContext,
            cache: CacheContext = None):
        '''
        Initialize the feature context.

        :param feature_service: The feature service to use for executing feature requests.
        :type feature_service: FeatureService
        :param container: The container context for dependency injection.
        :type container: ContainerContext
        :param cache: The cache context to use for caching feature data.
        :type cache: CacheContext
        '''

        # Assign the attributes.
        self.feature_service = feature_service
        self.feature_handler = feature_service
        self.container = container
        self.cache = cache if cache else CacheContext()

    # * method: load_feature
    def load_feature(self, feature_id: str) -> Feature:
        '''
        Retrieve a FlaskFeature by its feature ID.

        :param feature_id: The feature ID to look up.
        :type feature_id: str
        :return: The corresponding Feature instance.
        :rtype: Feature
        '''
        
        # Try to get the feature by its id from the cache.
        # If it does not exist, retrieve it from the feature handler and cache it.
        feature = self.cache.get(feature_id)
        if not feature:
            feature = self.feature_handler.get_feature(feature_id)
            self.cache.set(feature_id, feature)

        # Return the feature.
        return feature

    # * method: load_feature_command
    def load_feature_command(self, attribute_id: str) -> Command:
        '''
        Load a feature command by its attribute ID from the container.

        :param attribute_id: The attribute ID of the command to load.
        :type attribute_id: str
        :return: The command object.
        :rtype: Command
        '''

        # Attempt to retrieve the command from the container.
        try:
            return self.container.get_dependency(attribute_id)
        
        # If the command is not found, raise an error.
        except Exception as e:
            raise_error.execute(
                'FEATURE_COMMAND_LOADING_FAILED',
                f'Failed to load feature command attribute: {attribute_id}. Ensure the container attributes is configured with the appropriate default settings/flags.',
                attribute_id,
                str(e)
        )
            
    # * method: parse_parameter
    def parse_parameter(self, parameter: str, request: RequestContext = None) -> str:
        '''
        Parse a parameter.

        :param parameter: The parameter to parse.
        :type parameter: str:
        param request: The request object containing data for parameter parsing.
        :type request: Request
        :return: The parsed parameter.
        :rtype: str
        '''

        # Parse the parameter if it not a request parameter.
        if not parameter.startswith('$r.'):
            return parse_parameter.execute(parameter)
        
        # Raise an error if the request is and the parameter comes from the request.
        if not request and parameter.startswith('$r.'):
            raise_error.execute(
                'REQUEST_NOT_FOUND',
                'Request data is not available for parameter parsing.',
                parameter
            )
    
        # Parse the parameter from the request if provided.
        result = request.data.get(parameter[3:], None)
        
        # Raise an error if the parameter is not found in the request data.
        if result is None:
            raise_error.execute(
                'PARAMETER_NOT_FOUND',
                f'Parameter {parameter} not found in request data.',
                parameter
            )

        # Return the parsed parameter.
        return result
            
    # * method: handle_command (obsolete)
    def handle_command(self,
        command: Command, 
        request: RequestContext,
        data_key: str = None,
        pass_on_error: bool = False,
        **kwargs
    ):
        '''
        Handle the execution of a command with the provided request and command-handling options.
        
        :param command: The command to execute.
        :type command: Command
        :param request: The request context object.
        :type request: RequestContext
        :param debug: Debug flag.
        :type debug: bool
        :param data_key: Optional key to store the result in the request data.
        :type data_key: str
        :param pass_on_error: If True, pass on the error instead of raising it.
        :type pass_on_error: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Execute the command with the request data and parameters, and optional contexts.
        # If an error occurs during command execution, handle it based on the pass_on_error flag.
        # Set the result to None if passing on the error.
        try:
            result = command.execute(
                **request.data,
                **kwargs
            )
        except Exception as e:
            if not pass_on_error:
                raise e
            result = None

        # If a data key is provided, store the result in the request data.
        request.set_result(result, data_key)

    # * method: handle_feature_command
    def handle_feature_command(self,
        command: Command,
        request: RequestContext,
        feature_command: 'FeatureCommand',
        **kwargs
    ):
        '''
        Handle the execution of a feature command with the provided request and command-handling options.
        :param command: The command to execute.
        :type command: Command
        :param request: The request context object.
        :type request: RequestContext
        :param feature_command: The feature command metadata.
        :type feature_command: FeatureCommand
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Handle the command with the request and feature command options.
        # NOTE: The  method executed is to be obsoleted, and this to be consolidated with handle_command for v2.
        self.handle_command(
            command,
            request,
            data_key=feature_command.data_key,
            pass_on_error=feature_command.pass_on_error,
            **{id: self.parse_parameter(param, request) for id, param in feature_command.parameters.items()},
            **kwargs
        )

    # * method: execute_feature
    def execute_feature(self, feature_id: str, request: RequestContext, **kwargs):
        '''
        Execute a feature by its ID with the provided request.
        
        :param request: The request context object.
        :type request: RequestContext
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Load the feature by its ID.
        feature = self.load_feature(feature_id)

        # Load the command dependencies from the container for the feature.
        commands = [
            self.load_feature_command(cmd.attribute_id)
            for cmd in feature.commands
        ]
              
        # Execute each command in the feature with the request and feature command options.
        for index, command in enumerate(commands):
            self.handle_feature_command(
                command=command,
                request=request,
                feature_command=feature.commands[index],
                features=self.feature_service,
                container=self.container,
                cache=self.cache,
                **kwargs
            )