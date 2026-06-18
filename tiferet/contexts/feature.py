"""Tiferet Feature Contexts"""

# *** imports

# ** core
import asyncio
import re
from typing import Any, Callable, Generator, List, Tuple, Dict

# ** app
from .base import BaseContext
from .cache import CacheContext
from .request import RequestContext
from ..assets.constants import (
    FEATURE_COMMAND_LOADING_FAILED_ID,
    REQUEST_NOT_FOUND_ID,
    PARAMETER_NOT_FOUND_ID
)
from ..events import (
    DomainEvent,
    RaiseError,
    ParseParameter
)
from ..domain import Feature, EventFeatureStep

# *** contexts

# ** context: feature_context
class FeatureContext(BaseContext):
    '''
    The feature context orchestrates feature step execution, resolving each
    step's domain event via the injected service-resolution handler and
    applying any configured middleware. It operates on pre-loaded ``Feature``
    domain objects supplied by the application interface hub.
    '''

    # * attribute: domain_type
    domain_type = Feature

    # * attribute: get_dependency
    get_dependency: Callable

    # * attribute: cache
    cache: CacheContext

    # * attribute: context_data
    context_data: Dict[str, Any]

    # * init
    def __init__(self,
            get_dependency: Callable,
            cache: CacheContext = None,
            context_data: Dict[str, Any] = None):
        '''
        Initialize the feature context.

        :param get_dependency: The service-resolution handler used to resolve each
            feature step's domain event and middleware by service id and flags.
        :type get_dependency: Callable
        :param cache: The shared cache context to use for caching feature data.
        :type cache: CacheContext
        :param context_data: Lowest-priority context defaults merged into every
            command execution (e.g. bootstrap ``default_commands_list``).
        :type context_data: Dict[str, Any]
        '''

        # Initialize the shared cache via the base context.
        super().__init__(cache=cache)

        # Store the injected service-resolution handler.
        self.get_dependency = get_dependency

        # Store the context-level execution defaults.
        self.context_data = context_data if context_data is not None else {}

    # * method: load_feature_step
    def load_feature_step(self, feature_event: EventFeatureStep, feature_flags: List[str] = None) -> DomainEvent:
        '''
        Resolve a feature event step via the injected service-resolution
        handler using its service ID and any configured flags.

        :param feature_event: The feature event metadata describing the
            service configuration and flags.
        :type feature_event: EventFeatureStep
        :param feature_flags: Optional list of flags from the parent feature.
        :type feature_flags: List[str]
        :return: The resolved domain event.
        :rtype: DomainEvent
        '''

        # Resolve the service identifier for the event.
        service_id = feature_event.service_id

        # Combine flags: feature-level (higher priority) first, then step-level.
        combined_flags = (feature_flags or []) + (feature_event.flags or [])

        # Attempt to resolve the event via the injected handler using the combined flags.
        try:
            return self.get_dependency(
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

    # * method: load_feature_middleware
    def load_feature_middleware(self, middleware_ids: list) -> list:
        '''
        Resolve a list of middleware service IDs to callable middleware instances.

        :param middleware_ids: Ordered list of service IDs to resolve.
        :type middleware_ids: list
        :return: Resolved middleware instances in the same order.
        :rtype: list
        '''

        # Return early when no middleware is configured.
        if not middleware_ids:
            return []

        # Resolve each service ID via the injected handler.
        return [self.get_dependency(mid_id) for mid_id in middleware_ids]

    # * method: handle_feature_step
    def handle_feature_step(self,
        command: DomainEvent,
        request: RequestContext,
        data_key: str = None,
        pass_on_error: bool = False,
        middleware: list = None,
        **kwargs
    ):
        '''
        Handle the execution of a command with the provided request and command-handling options.

        When ``middleware`` is provided the command execution is wrapped in an
        ordered chain.  Each middleware callable receives
        ``(event, kwargs, next_fn)`` and must call ``next_fn()`` to continue.

        :param command: The command to execute.
        :type command: DomainEvent
        :param request: The request context object.
        :type request: RequestContext
        :param data_key: Optional key to store the result in the request data.
        :type data_key: str
        :param pass_on_error: If True, pass on the error instead of raising it.
        :type pass_on_error: bool
        :param middleware: Optional ordered list of resolved middleware callables.
        :type middleware: list | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Merge context defaults (lowest priority), request data, and step parameters.
        merged_kwargs = {**self.context_data, **request.data, **kwargs}

        # Build the base execution callable.
        def base():
            return command.execute(**merged_kwargs)

        # Compose middleware chain when middleware is configured.
        if middleware:
            chain = base
            for mw in reversed(middleware):
                _next = chain
                _mw = mw
                def _make_wrapper(_mw, _next):
                    def wrapper():
                        return _mw(command, merged_kwargs, _next)
                    return wrapper
                chain = _make_wrapper(_mw, _next)
        else:
            chain = base

        # Execute the command (or chain), handling errors per pass_on_error.
        try:
            result = chain()

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

    # * method: resolve_feature_steps
    def resolve_feature_steps(self,
            feature: Feature,
            request: RequestContext,
        ) -> Generator[Tuple[DomainEvent, EventFeatureStep, Dict[str, str]], None, None]:
        '''
        Resolve and yield executable steps for a pre-loaded feature.

        Evaluates step conditions, resolves each step's domain event from the
        DI context, and parses its parameters. Yields tuples of
        ``(command, feature_event, params)`` for each step that should execute.

        :param feature: The pre-loaded feature domain object.
        :type feature: Feature
        :param request: The request context for condition evaluation and parameter parsing.
        :type request: RequestContext
        :return: A generator yielding (command, feature_event, params) tuples.
        :rtype: Generator[Tuple[DomainEvent, EventFeatureStep, Dict[str, str]], None, None]
        '''

        # Iterate over the feature's configured steps.
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

            # Yield the resolved step.
            yield cmd, feature_event, params

    # * method: execute_feature
    def execute_feature(self, feature: Feature, request: RequestContext, **kwargs):
        '''
        Execute a pre-loaded feature with the provided request.

        :param feature: The pre-loaded feature domain object.
        :type feature: Feature
        :param request: The request context object.
        :type request: RequestContext
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Resolve feature-level middleware once for all steps.
        feature_middleware = self.load_feature_middleware(feature.middleware)

        # Resolve and execute each step synchronously.
        for cmd, step, params in self.resolve_feature_steps(feature, request):

            # Compose feature-level (outer) + step-level (inner) middleware.
            step_middleware = self.load_feature_middleware(step.middleware)
            combined_middleware = feature_middleware + step_middleware or None

            self.handle_feature_step(
                cmd,
                request,
                data_key=step.data_key,
                pass_on_error=step.pass_on_error,
                middleware=combined_middleware,
                **params,
                cache=self.cache,
                **kwargs
            )


# ** context: async_feature_context
class AsyncFeatureContext(FeatureContext):
    '''
    The async feature context extends :class:`FeatureContext` with
    asynchronous step execution, awaiting coroutine-based domain events while
    reusing the shared step-resolution, parameter-parsing, condition, and
    middleware helpers inherited from the synchronous context. It is selected
    by the application interface hub when a loaded ``Feature`` has ``is_async``
    set to ``True``.
    '''

    # * method: handle_feature_step_async
    async def handle_feature_step_async(self,
        command: DomainEvent,
        request: RequestContext,
        data_key: str = None,
        pass_on_error: bool = False,
        middleware: list = None,
        **kwargs
    ):
        '''
        Handle the execution of a command with the provided request,
        supporting both sync and async commands.

        Detects whether the command's ``execute`` is a coroutine function
        and awaits it when necessary, otherwise calls it synchronously.
        When ``middleware`` is provided the execution is wrapped in an ordered
        async chain; async middleware must ``await next_fn()``.

        :param command: The command to execute (sync or async).
        :type command: DomainEvent
        :param request: The request context object.
        :type request: RequestContext
        :param data_key: Optional key to store the result in the request data.
        :type data_key: str
        :param pass_on_error: If True, pass on the error instead of raising it.
        :type pass_on_error: bool
        :param middleware: Optional ordered list of resolved middleware callables.
        :type middleware: list | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Merge context defaults (lowest priority), request data, and step parameters.
        merged_kwargs = {**self.context_data, **request.data, **kwargs}

        # Build the base async execution callable.
        async def base():
            if asyncio.iscoroutinefunction(command.execute):
                return await command.execute(**merged_kwargs)
            return command.execute(**merged_kwargs)

        # Compose async middleware chain when middleware is configured.
        if middleware:
            chain = base
            for mw in reversed(middleware):
                _next = chain
                _mw = mw
                def _make_async_wrapper(_mw, _next):
                    async def wrapper():
                        # Call the middleware; await the result if it is a coroutine
                        # (handles both async def functions and async def __call__ instances).
                        result = _mw(command, merged_kwargs, _next)
                        if asyncio.iscoroutine(result):
                            return await result
                        return result
                    return wrapper
                chain = _make_async_wrapper(_mw, _next)
        else:
            chain = base

        # Execute the chain, handling errors per pass_on_error.
        try:
            result = await chain()

        # If an error occurs during command execution, handle it based on the pass_on_error flag.
        except Exception as e:
            if not pass_on_error:
                raise e

            # Set the result to None if passing on the error.
            result = None

        # Store the result via the request context.
        request.set_result(result, data_key)

    # * method: execute_feature_async
    async def execute_feature_async(self, feature: Feature, request: RequestContext, **kwargs):
        '''
        Execute a pre-loaded feature with the provided request, supporting
        mixed sync/async step chains.

        :param feature: The pre-loaded feature domain object.
        :type feature: Feature
        :param request: The request context object.
        :type request: RequestContext
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Resolve feature-level middleware once for all steps.
        feature_middleware = self.load_feature_middleware(feature.middleware)

        # Resolve and execute each step, awaiting async commands as needed.
        for cmd, step, params in self.resolve_feature_steps(feature, request):

            # Compose feature-level (outer) + step-level (inner) middleware.
            step_middleware = self.load_feature_middleware(step.middleware)
            combined_middleware = feature_middleware + step_middleware or None

            await self.handle_feature_step_async(
                cmd,
                request,
                data_key=step.data_key,
                pass_on_error=step.pass_on_error,
                middleware=combined_middleware,
                **params,
                cache=self.cache,
                **kwargs
            )
