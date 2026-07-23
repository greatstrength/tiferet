# *** imports

# ** core
import re
from typing import Any, Callable

# ** app
from .di import DIContext
from .cache import CacheContext
from .request import RequestContext
from ..assets.core import (
    FEATURE_COMMAND_LOADING_FAILED_ID,
    REQUEST_NOT_FOUND_ID,
    PARAMETER_NOT_FOUND_ID
)
from ..events import (
    DomainEvent,
    RaiseError,
    ParseParameter
)
from ..domain import Feature, FeatureEvent

# *** contexts

# ** context: feature_context
class FeatureContext(object):

    # * attribute: services
    services: DIContext

    # * attribute: cache
    cache: CacheContext

    # * attribute: get_feature_handler
    get_feature_handler: Callable

    # * init
    def __init__(self,
            get_feature_evt: DomainEvent,
            services: DIContext,
            cache: CacheContext = None):
        '''
        Initialize the feature context.

        :param get_feature_evt: The event used to retrieve features.
        :type get_feature_evt: DomainEvent
        :param services: The DI context for dependency injection.
        :type services: DIContext
        :param cache: The cache context to use for caching feature data.
        :type cache: CacheContext
        '''

        # Assign the attributes.
        self.services = services
        self.cache = cache if cache else CacheContext()
        self.get_feature_handler = get_feature_evt.execute

    # * method: load_feature_step
    def load_feature_step(self, feature_event: FeatureEvent, feature_flags: list[str] = None) -> DomainEvent:
        '''
        Load a feature event step from the DI context using its service ID and
        any configured flags.

        :param feature_event: The feature event metadata describing the
            service configuration and flags.
        :type feature_event: FeatureEvent
        :param feature_flags: Optional list of flags from the parent feature.
        :type feature_flags: list[str]
        :return: The resolved domain event.
        :rtype: DomainEvent
        '''

        # Resolve the service identifier for the event.
        service_id = feature_event.service_id

        # Combine flags: feature-level (higher priority) first, then step-level.
        combined_flags = (feature_flags or []) + (feature_event.flags or [])

        # Attempt to retrieve the event from the DI context using the combined flags.
        try:
            return self.services.get_dependency(
                service_id,
                *combined_flags,
            )

        # If the event is not found, raise an error.
        except Exception as e:
            RaiseError.execute(
                FEATURE_COMMAND_LOADING_FAILED_ID,
                f'Failed to load feature step attribute: {service_id}. Ensure the container is configured with the appropriate default settings/flags.',
                service_id=service_id,
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
        command: DomainEvent,
        request: RequestContext,
        data_key: str = None,
        pass_on_error: bool = False,
        **kwargs
    ):
        '''
        Handle the execution of a command with the provided request and command-handling options.
        
        :param command: The command to execute.
        :type command: DomainEvent
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

        # Store the result via the request context.
        request.set_result(result, data_key)

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

    # * method: evaluate_condition
    def evaluate_condition(self, condition: str, request: RequestContext) -> bool:
        '''
        Evaluate a boolean expression against request data.
        Returns True when condition is None or empty.

        :param condition: The boolean expression to evaluate. Uses ``$r.`` prefix
            to reference values from ``request.data``.
        :type condition: str
        :param request: The request context containing the data to resolve references against.
        :type request: RequestContext
        :return: The boolean result of the evaluated expression.
        :rtype: bool
        '''

        # Return True if condition is None or empty (unconditional step).
        if not condition or not condition.strip():
            return True

        # Resolve $r. references by substituting values from request data.
        def _resolve_ref(match: re.Match) -> str:
            key = match.group(1)
            value = request.data.get(key)
            if value is None:
                return 'None'
            return repr(value)

        # Replace all $r.<key> references with their repr'd values.
        resolved = re.sub(r'\$r\.(\w+)', _resolve_ref, condition)

        # Evaluate the resolved expression safely; return False on failure.
        try:
            return bool(eval(resolved, {"__builtins__": {}}, {}))  # noqa: S307
        except Exception:
            return False

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

        # Execute the feature by iterating over its configured steps.
        for feature_event in feature.steps:

            # Evaluate the step condition; skip if False.
            if not self.evaluate_condition(feature_event.condition, request):
                continue

            # Load the event dependency for this step, honoring any configured flags.
            cmd = self.load_feature_step(feature_event, feature_flags=feature.flags)

            # Parse the step parameters.
            params = {
                param: self.parse_request_parameter(value, request)
                for param, value in feature_event.parameters.items()
            }

            # Execute the step with the request data and parameters.
            self.handle_command(
                cmd,
                request,
                data_key=feature_event.data_key,
                pass_on_error=feature_event.pass_on_error,
                **params,
                services=self.services,
                cache=self.cache,
                **kwargs
            )
