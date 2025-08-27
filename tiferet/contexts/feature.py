# *** imports

# ** app
from .container import ContainerContext
from .cache import CacheContext
from .request import RequestContext
from ..handlers.feature import FeatureService
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
        self.container = container
        self.cache = cache if cache else CacheContext()

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
            
    # * method: handle_command
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
        try:
            result = command.execute(
                **request.data,
                **kwargs
            )

        # If an error occurs during command execution, handle it based on the pass_on_error flag.
        except Exception as e:
            if not pass_on_error:
                raise e
            
            # Set the result to None if passing on the error.
            result = None

        # If a data key is provided, store the result in the request data.
        if data_key:
            request.data[data_key] = result

        # Otherwise, set the result.
        else:
            request.result = result

    # * method: execute_feature
    def execute_feature(self, feature_id: str, request: RequestContext, **kwargs):
        '''
        Execute a feature by its ID with the provided request.
        
        :param request: The request context object.
        :type request: RequestContext
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Try to get the feature by its id from the cache.
        # If it does not exist, retrieve it from the feature handler and cache it.
        feature = self.cache.get(feature_id)
        if not feature:
            feature = self.feature_service.get_feature(feature_id)
            self.cache.set(feature_id, feature)

        # Load the command dependencies from the container for the feature.
        commands = [
            self.load_feature_command(cmd.attribute_id)
            for cmd in feature.commands
        ]
              
        # Execute the feature with the request and commands.
        for index, cmd in enumerate(commands):

            # Get the feature command from the feature.
            feature_command = feature.commands[index]

            # Parse the command parameters
            params = {
                param: self.feature_service.parse_parameter(value, request)
                for param, value in feature_command.parameters.items()
            }

            # Execute the command with the request data and parameters.
            self.handle_command(
                cmd,
                request,
                data_key=feature_command.data_key,
                pass_on_error=feature_command.pass_on_error,
                **params,
                features=self.feature_service,
                container=self.container,
                cache=self.cache,
                **kwargs
            )