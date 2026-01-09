# *** imports

# ** core
from typing import Callable

# ** app
from .container import ContainerContext
from .cache import CacheContext
from .request import RequestContext
from ..assets.constants import (
    FEATURE_COMMAND_LOADING_FAILED_ID,
    REQUEST_NOT_FOUND_ID,
    PARAMETER_NOT_FOUND_ID
)
from ..commands import (
    Command,
    RaiseError,
    ParseParameter
)
from ..commands.feature import GetFeature
from ..models import Feature

# *** contexts

# ** context: feature_context
class FeatureContext(object):

    # * attribute: container
    container: ContainerContext

    # * attribute: cache
    cache: CacheContext

    # * attribute: get_feature_handler
    get_feature_handler: Callable

    # * method: init
    def __init__(self,
            get_feature_cmd: GetFeature,
            container: ContainerContext,
            cache: CacheContext = None):
        '''
        Initialize the feature context.

        :param get_feature_cmd: The command used to retrieve features.
        :type get_feature_cmd: GetFeature
        :param container: The container context for dependency injection.
        :type container: ContainerContext
        :param cache: The cache context to use for caching feature data.
        :type cache: CacheContext
        '''

        # Assign the attributes.
        self.container = container
        self.cache = cache if cache else CacheContext()
        self.get_feature_handler = get_feature_cmd.execute

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
            RaiseError.execute(
                FEATURE_COMMAND_LOADING_FAILED_ID,
                f'Failed to load feature command attribute: {attribute_id}. Ensure the container attributes is configured with the appropriate default settings/flags.',
                attribute_id=attribute_id,
                exception=str(e)
            )

    # * method: load_feature
    def load_feature(self, feature_id: str) -> Feature:
        '''
        Load a feature by ID, using cache when available.

        :param feature_id: The feature identifier.
        :type feature_id: str
        :return: The loaded feature.
        :rtype: Feature
        '''

        # Try to get the feature from the cache first.
        feature = self.cache.get(feature_id)

        # If not in cache, retrieve via command and cache the result.
        if not feature:
            feature = self.get_feature_handler(id=feature_id)
            self.cache.set(feature_id, feature)

        # Return the loaded feature.
        return feature
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

    # * method: parse_request_parameter
    def parse_request_parameter(self, parameter: str, request: RequestContext = None) -> str:
        '''
        Parse a request-aware parameter.

        :param parameter: The parameter to parse.
        :type parameter: str
        :param request: The request context object containing data for parameter parsing.
        :type request: RequestContext
        :return: The parsed parameter value.
        :rtype: str
        '''

        # Parse the parameter if it is not a request-backed parameter.
        if not parameter.startswith('$r.'):
            return ParseParameter.execute(parameter)

        # Raise an error if the request is not provided for a request-backed parameter.
        if not request:
            RaiseError.execute(
                REQUEST_NOT_FOUND_ID,
                'Request data is not available for parameter parsing.',
                parameter=parameter
            )

        # Parse the parameter from the request if provided.
        result = request.data.get(parameter[3:], None)

        # Raise an error if the parameter is not found in the request data.
        if result is None:
            RaiseError.execute(
                PARAMETER_NOT_FOUND_ID,
                f'Parameter {parameter} not found in request data.',
                parameter=parameter
            )

        # Return the parsed parameter.
        return result

    # * method: execute_feature
    def execute_feature(self, feature_id: str, request: RequestContext, **kwargs):
        '''
        Execute a feature by its ID with the provided request.
        
        :param request: The request context object.
        :type request: RequestContext
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Load the feature by id, using the cache when possible.
        feature = self.load_feature(feature_id)

        # Execute the feature by iterating over its configured commands.
        for feature_command in feature.commands:

            # Load the command dependency for this feature command.
            cmd = self.load_feature_command(feature_command.attribute_id)

            # Parse the command parameters.
            params = {
                param: self.parse_request_parameter(value, request)
                for param, value in feature_command.parameters.items()
            }

            # Execute the command with the request data and parameters.
            self.handle_command(
                cmd,
                request,
                data_key=feature_command.data_key,
                pass_on_error=feature_command.pass_on_error,
                **params,
                container=self.container,
                cache=self.cache,
                **kwargs
            )
