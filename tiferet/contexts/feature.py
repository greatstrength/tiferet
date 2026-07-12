"""Tiferet Feature Contexts"""

# *** imports

# ** core
import asyncio
import threading
from typing import Any, Callable, Generator, List, Tuple, Dict

# ** app
from .settings import BaseContext
from .cache import CacheContext
from .request import RequestContext
from ..assets.constants import (
    FEATURE_STEP_LOADING_FAILED_ID,
    MIDDLEWARE_LOADING_FAILED_ID,
    REQUEST_NOT_FOUND_ID,
    PARAMETER_NOT_FOUND_ID
)
from ..events import (
    DomainEvent,
    RaiseError,
    ParseParameter
)
from ..domain import Feature, EventFeatureStep

# *** functions

# ** function: run_coroutine
def run_coroutine(coro: Any) -> Any:
    '''
    Drive a coroutine to completion from synchronous code.

    Uses ``asyncio.run`` when no event loop is currently running. When a loop
    is already running (e.g. inside an async host), the coroutine is executed
    on a short-lived dedicated thread with its own event loop so the
    synchronous caller never raises ``RuntimeError``.

    Because this function accepts a **coroutine instance** (not the async
    function itself), the async method that produced the coroutine remains
    genuinely awaitable for any future async caller that wants to ``await``
    it directly.

    :param coro: The coroutine to execute.
    :type coro: Any
    :return: The coroutine result.
    :rtype: Any
    '''

    # Use asyncio.run directly when no event loop is currently running.
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    # A loop is already running; execute the coroutine on a dedicated
    # thread with its own event loop, capturing the result or error.
    box: Dict[str, Any] = {}

    def _runner():
        try:
            box['result'] = asyncio.run(coro)
        except BaseException as error:  # re-raised on the calling thread
            box['error'] = error

    # Run the worker thread to completion.
    thread = threading.Thread(target=_runner)
    thread.start()
    thread.join()

    # Re-raise any error captured on the worker thread.
    if 'error' in box:
        raise box['error']

    # Return the captured coroutine result.
    return box.get('result')

# ** function: merge_step_kwargs
def merge_step_kwargs(
        context_data: Dict[str, Any],
        request_data: Dict[str, Any],
        step_params: Dict[str, Any],
        **kwargs,
) -> Dict[str, Any]:
    '''
    Build the merged kwargs dict for a feature step execution.

    Merges context defaults (lowest priority), request data, step-level
    parameters, and any caller-supplied overrides (highest priority).

    :param context_data: Context-level execution defaults.
    :type context_data: Dict[str, Any]
    :param request_data: Current request data.
    :type request_data: Dict[str, Any]
    :param step_params: Parsed step-level parameters.
    :type step_params: Dict[str, Any]
    :param kwargs: Additional caller-supplied overrides.
    :type kwargs: dict
    :return: Merged kwargs ready for command execution.
    :rtype: Dict[str, Any]
    '''

    # Merge in priority order: context < request < step params < overrides.
    return {**context_data, **request_data, **step_params, **kwargs}

# ** function: build_step_chain
def build_step_chain(
        command: DomainEvent,
        merged_kwargs: Dict[str, Any],
        middleware: list,
        is_async: bool = False,
) -> Callable:
    '''
    Build an execution chain for a feature step, with or without middleware.

    Returns a zero-argument callable (sync) or zero-argument coroutine
    function (async). Both paths share the same reversed-middleware iteration
    loop; only the wrapper closure type and the base invocation differ.

    For the async path the base callable detects whether the command's
    ``execute`` is a coroutine function and awaits it when necessary,
    allowing a mixed sync/async step chain.

    :param command: The domain event to execute.
    :type command: DomainEvent
    :param merged_kwargs: Pre-merged execution kwargs.
    :type merged_kwargs: Dict[str, Any]
    :param middleware: Ordered list of resolved middleware callables
        (outermost first); may be ``None`` or empty.
    :type middleware: list
    :param is_async: When ``True`` the chain is async-aware.
    :type is_async: bool
    :return: A callable (sync) or coroutine function (async) that executes
        the step, optionally wrapped in the middleware chain.
    :rtype: Callable
    '''

    if is_async:

        # Build the async base callable, awaiting async commands.
        async def base():
            if asyncio.iscoroutinefunction(command.execute):
                return await command.execute(**merged_kwargs)
            return command.execute(**merged_kwargs)

        # Return the base when no middleware is configured.
        if not middleware:
            return base

        # Compose the async middleware chain (outermost first = reversed iteration).
        chain = base
        for mw in reversed(middleware):
            def _make_async_wrapper(_mw, _next):
                async def wrapper():
                    result = _mw(command, merged_kwargs, _next)
                    if asyncio.iscoroutine(result):
                        return await result
                    return result
                return wrapper
            chain = _make_async_wrapper(mw, chain)

        # Return the composed async chain.
        return chain

    # Build the sync base callable.
    def base():
        return command.execute(**merged_kwargs)

    # Return the base when no middleware is configured.
    if not middleware:
        return base

    # Compose the sync middleware chain (outermost first = reversed iteration).
    chain = base
    for mw in reversed(middleware):
        def _make_wrapper(_mw, _next):
            def wrapper():
                return _mw(command, merged_kwargs, _next)
            return wrapper
        chain = _make_wrapper(mw, chain)

    # Return the composed sync chain.
    return chain

# ** function: parse_request_parameter
def parse_request_parameter(parameter: str, request: RequestContext = None) -> str:
    '''
    Parse a request-aware parameter value.

    Delegates non-prefixed parameters to :func:`ParseParameter.execute`. For
    ``$r.``-prefixed references, extracts the value keyed by the suffix from
    ``request.data``, raising a structured error when the request is absent or
    the key is missing.

    :param parameter: The parameter value to parse.
    :type parameter: str
    :param request: The request context object containing data for parameter parsing.
    :type request: RequestContext
    :return: The parsed parameter value.
    :rtype: str
    '''

    # Delegate non-prefixed parameters to the ParseParameter static event.
    if not parameter.startswith('$r.'):
        return ParseParameter.execute(parameter)

    # Raise an error if the request is not provided for a request-backed parameter.
    if not request:
        RaiseError.execute(
            REQUEST_NOT_FOUND_ID,
            'Request data is not available for parameter parsing.',
            parameter=parameter
        )

    # Extract the value from the request data using the key after the $r. prefix.
    result = request.data.get(parameter[3:], None)

    # Raise an error if the parameter key is not found in the request data.
    if result is None:
        RaiseError.execute(
            PARAMETER_NOT_FOUND_ID,
            f'Parameter {parameter} not found in request data.',
            parameter=parameter
        )

    # Return the parsed parameter value.
    return result

# ** function: evaluate_condition
def evaluate_condition(condition: str, request: RequestContext) -> bool:
    '''
    Evaluate a boolean expression against request data.

    Returns ``True`` when ``condition`` is ``None`` or empty (unconditional
    step). Resolves ``$r.<key>`` references from ``request.data`` via regex
    substitution, then evaluates the resulting expression in a sandboxed
    environment. Returns ``False`` on any evaluation failure.

    :param condition: The boolean expression to evaluate. Uses ``$r.`` prefix
        to reference values from ``request.data``.
    :type condition: str
    :param request: The request context containing the data to resolve references against.
    :type request: RequestContext
    :return: The boolean result of the evaluated expression.
    :rtype: bool
    '''

    import re

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

# ** function: validate_request
def validate_request(feature: Feature, request: RequestContext) -> None:
    '''
    Validate and coerce request data against the feature's request schema.

    When the feature declares no ``params_schema`` the request is left
    unchanged; otherwise the coerced result replaces ``request.data`` so all
    downstream steps receive validated, type-coerced inputs. A schema failure
    raises a single ``REQUEST_VALIDATION_FAILED`` error before any step runs.

    :param feature: The pre-loaded feature domain object.
    :type feature: Feature
    :param request: The request context whose data is validated in place.
    :type request: RequestContext
    '''

    # Skip validation when the feature declares no request schema.
    if feature.params_schema is None:
        return

    # Validate and coerce the request data, assigning the merged result back.
    request.data = feature.params_schema.validate(
        request.data,
        feature_id=feature.id,
    )

# *** contexts

# ** context: feature_context
class FeatureContext(BaseContext):
    '''
    The feature context orchestrates feature step execution, resolving each
    step's domain event via the injected service-resolution handler and
    applying any configured middleware. It handles both synchronous and
    asynchronous features through a unified ``execute_feature`` entry point.

    Async features (``feature.is_async=True``) drive the entire step loop via
    the module-level ``run_coroutine`` wrapper. Individual async steps
    (``step.is_async=True``) within a synchronous feature are also driven
    per-step via ``run_coroutine``, so mixed sync/async features work without
    flagging the entire feature as async.
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
            command execution.
        :type context_data: Dict[str, Any]
        '''

        # Initialize the base context.
        super().__init__()

        # Wire in the shared cache context, defaulting to a fresh one.
        self.cache = cache if cache is not None else CacheContext()

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

        # If the event is not found, raise a structured error.
        except Exception as e:
            RaiseError.execute(
                FEATURE_STEP_LOADING_FAILED_ID,
                f'Failed to load feature step: {service_id}. Ensure the container is configured with the appropriate default settings/flags.',
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

        # Resolve each middleware service ID via the injected handler, raising a
        # structured error if any resolution fails.
        middleware = []
        for mid_id in middleware_ids:
            try:
                middleware.append(self.get_dependency(mid_id))

            # If the middleware cannot be loaded, raise an error.
            except Exception as e:
                RaiseError.execute(
                    MIDDLEWARE_LOADING_FAILED_ID,
                    f'Failed to load middleware: {mid_id}. Ensure the container is configured with the appropriate default settings/flags.',
                    service_id=mid_id,
                    exception=str(e)
                )

        # Return the resolved middleware instances.
        return middleware

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
        Execute a feature step synchronously with the provided request and options.

        When ``middleware`` is provided the command execution is wrapped in an
        ordered chain. Each middleware callable receives
        ``(event, kwargs, next_fn)`` and must call ``next_fn()`` to continue.

        :param command: The domain event to execute.
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

        # Build the merged kwargs and the sync execution chain.
        merged_kwargs = merge_step_kwargs(self.context_data, request.data, {}, **kwargs)
        chain = build_step_chain(command, merged_kwargs, middleware or [], is_async=False)

        # Execute the chain, handling errors per pass_on_error.
        try:
            result = chain()

        # Handle errors based on the pass_on_error flag.
        except Exception as e:
            if not pass_on_error:
                raise e

            # Set the result to None if passing on the error.
            result = None

        # Store the result via the request context.
        request.set_result(result, data_key)

    # * method: _handle_step_async
    async def _handle_step_async(self,
        command: DomainEvent,
        request: RequestContext,
        data_key: str = None,
        pass_on_error: bool = False,
        middleware: list = None,
        **kwargs
    ):
        '''
        Execute a feature step asynchronously, supporting both sync and async
        domain events and middleware.

        Detects whether the command's ``execute`` is a coroutine function and
        awaits it when necessary, otherwise calls it synchronously. When
        ``middleware`` is provided the execution is wrapped in an ordered async
        chain; async middleware must ``await next_fn()``.

        :param command: The domain event to execute (sync or async).
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

        # Build the merged kwargs and the async execution chain.
        merged_kwargs = merge_step_kwargs(self.context_data, request.data, {}, **kwargs)
        chain = build_step_chain(command, merged_kwargs, middleware or [], is_async=True)

        # Execute the async chain, handling errors per pass_on_error.
        try:
            result = await chain()

        # Handle errors based on the pass_on_error flag.
        except Exception as e:
            if not pass_on_error:
                raise e

            # Set the result to None if passing on the error.
            result = None

        # Store the result via the request context.
        request.set_result(result, data_key)

    # * method: _execute_async
    async def _execute_async(self, feature: Feature, request: RequestContext, *flags, **kwargs):
        '''
        Execute a pre-loaded async feature, awaiting each step in turn.

        Supports mixed sync/async step chains: each step is dispatched through
        ``_handle_step_async``, which detects and awaits coroutine-based
        domain events while calling synchronous events directly.

        This method is a genuine async coroutine and stays awaitable for any
        future async host. From synchronous code it is driven via
        ``run_coroutine(self._execute_async(feature, request, ...))``.

        :param feature: The pre-loaded feature domain object.
        :type feature: Feature
        :param request: The request context object.
        :type request: RequestContext
        :param flags: Optional execution flags; consumed by the FE3
            flag-verification hook.
        :type flags: str
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

            await self._handle_step_async(
                cmd,
                request,
                data_key=step.data_key,
                pass_on_error=step.pass_on_error,
                middleware=combined_middleware,
                **params,
                cache=self.cache,
                **kwargs
            )

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
            if not evaluate_condition(feature_event.condition, request):
                continue

            # Load the event dependency for this step, honoring any configured flags.
            cmd = self.load_feature_step(feature_event, feature_flags=feature.flags)

            # Parse the step parameters.
            params = {
                param: parse_request_parameter(value, request)
                for param, value in feature_event.parameters.items()
            }

            # Yield the resolved step.
            yield cmd, feature_event, params

    # * method: verify_feature_flags
    def verify_feature_flags(self, feature: Feature, flags: tuple) -> None:
        '''
        Verify that the feature's declared flags are satisfied by the
        execution flags passed to ``execute_feature``.

        .. note::
            This method is a hook stub; the verification logic and the new
            ``FEATURE_FLAGS_NOT_SATISFIED`` error are wired in at FE3.

        :param feature: The pre-loaded feature domain object.
        :type feature: Feature
        :param flags: The execution flags passed to ``execute_feature``.
        :type flags: tuple
        '''

        # ++ todo: implement flag subset check at FE3 — set(feature.flags) ⊆ set(flags)
        pass

    # * method: execute_feature
    def execute_feature(self, feature: Feature, request: RequestContext, *flags, **kwargs):
        '''
        Execute a pre-loaded feature with the provided request.

        Handles three dispatch cases based on ``is_async`` flags:

        1. ``feature.is_async=True`` — the entire step loop runs asynchronously
           via ``run_coroutine(self._execute_async(...))``.
        2. ``feature.is_async=False``, ``step.is_async=True`` — a per-step
           ``run_coroutine(self._handle_step_async(...))`` drives individual
           async steps within an otherwise synchronous feature.
        3. Both flags ``False`` — fully synchronous ``handle_feature_step``
           execution.

        :param feature: The pre-loaded feature domain object.
        :type feature: Feature
        :param request: The request context object.
        :type request: RequestContext
        :param flags: Optional execution flags for feature-level service
            resolution; consumed by the flag-verification hook at FE3.
        :type flags: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Validate and coerce request data against the feature schema first,
        # failing fast before any step executes.
        validate_request(feature, request)

        # Case 1: entire feature is async — drive the full loop via run_coroutine.
        if feature.is_async:
            run_coroutine(self._execute_async(feature, request, *flags, **kwargs))
            return

        # Cases 2 & 3: synchronous feature loop with per-step async detection.
        feature_middleware = self.load_feature_middleware(feature.middleware)

        for cmd, step, params in self.resolve_feature_steps(feature, request):

            # Compose feature-level (outer) + step-level (inner) middleware.
            step_middleware = self.load_feature_middleware(step.middleware)
            combined_middleware = feature_middleware + step_middleware or None

            # Case 2: individual step is async — drive it via run_coroutine.
            if step.is_async:
                run_coroutine(self._handle_step_async(
                    cmd,
                    request,
                    data_key=step.data_key,
                    pass_on_error=step.pass_on_error,
                    middleware=combined_middleware,
                    **params,
                    cache=self.cache,
                    **kwargs
                ))
                continue

            # Case 3: fully synchronous step.
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


# ** context: async_feature_context (obsolete)
# -- obsolete: superseded by FeatureContext (async handling folded in at FE2); remove at v2.0.0 stable
class AsyncFeatureContext(FeatureContext):
    '''
    Async feature context.

    NOTE: Obsolete — superseded by :class:`FeatureContext`, which now handles
    both synchronous and asynchronous feature execution through a unified
    ``execute_feature`` entry point. Use ``FeatureContext`` directly and set
    ``feature.is_async=True`` or ``step.is_async=True`` as appropriate.
    '''

    # * method: handle_feature_step_async (obsolete)
    # -- obsolete: superseded by FeatureContext._handle_step_async; remove at v2.0.0 stable
    async def handle_feature_step_async(self,
        command: DomainEvent,
        request: RequestContext,
        data_key: str = None,
        pass_on_error: bool = False,
        middleware: list = None,
        **kwargs
    ):
        '''
        Handle the execution of a command asynchronously.

        NOTE: Obsolete — delegates to :meth:`FeatureContext._handle_step_async`.
        Call that method directly instead.
        '''

        # Delegate to the unified private async step handler.
        await self._handle_step_async(
            command, request,
            data_key=data_key,
            pass_on_error=pass_on_error,
            middleware=middleware,
            **kwargs,
        )

    # * method: execute_feature_async (obsolete)
    # -- obsolete: superseded by FeatureContext._execute_async (driven via run_coroutine); remove at v2.0.0 stable
    async def execute_feature_async(self, feature: Feature, request: RequestContext, *flags, **kwargs):
        '''
        Execute a pre-loaded feature asynchronously.

        NOTE: Obsolete — delegates to :meth:`FeatureContext._execute_async`.
        Use ``FeatureContext.execute_feature`` with ``feature.is_async=True`` instead.
        '''

        # Delegate to the unified private async execution loop.
        await self._execute_async(feature, request, *flags, **kwargs)
