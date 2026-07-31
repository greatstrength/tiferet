"""Tiferet Feature Context Tests"""

# *** imports

# ** core
from typing import Any, Callable
from unittest import mock

# ** infra
import pytest

# ** app
from tiferet.assets import TiferetError
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.core import BaseContext, ContextMeta
from tiferet.contexts.feature import (
    FeatureContext,
    RequestContext,
    FEATURE_CACHE_PREFIX,
    add_default_features,
    run_coroutine,
    merge_step_kwargs,
    build_step_chain,
    compose_step_middleware,
    parse_request_parameter,
    evaluate_condition,
    validate_request,
)
from tiferet.events import DomainEvent, AsyncDomainEvent
from tiferet.domain import Feature, EventFeatureStep

# *** fixtures

# ** fixture: test_command
@pytest.fixture
def test_command() -> DomainEvent:
    '''
    Fixture providing a synchronous domain event for step execution.

    :return: A synchronous domain event instance.
    :rtype: DomainEvent
    '''

    # Define a synchronous domain event returning a canned response.
    class TestEvent(DomainEvent):

        def execute(self, key: str = None, param: str = None, **kwargs) -> Any:

            # Verify that a key was supplied for execution.
            self.verify(key, 'KEY_NOT_FOUND', 'No key provided for command execution.')

            # Return the response, including the parameter when provided.
            if not param:
                return {'status': 'success', 'data': {'key': key}}
            return {'status': 'success', 'data': {'key': key, 'param': param}}

    # Return an instance of the synchronous event.
    return TestEvent()

# ** fixture: async_test_command
@pytest.fixture
def async_test_command() -> AsyncDomainEvent:
    '''
    Fixture providing an asynchronous domain event for step execution.

    :return: An asynchronous domain event instance.
    :rtype: AsyncDomainEvent
    '''

    # Define an asynchronous domain event returning a canned response.
    class AsyncTestEvent(AsyncDomainEvent):

        async def execute(self, key: str = None, param: str = None, **kwargs) -> Any:

            # Verify that a key was supplied for execution.
            self.verify(key, 'KEY_NOT_FOUND', 'No key provided for command execution.')

            # Return the response, including the parameter when provided.
            if not param:
                return {'status': 'async_success', 'data': {'key': key}}
            return {'status': 'async_success', 'data': {'key': key, 'param': param}}

    # Return an instance of the asynchronous event.
    return AsyncTestEvent()

# ** fixture: services
@pytest.fixture
def services(test_command: DomainEvent) -> mock.Mock:
    '''
    Fixture providing a mock service resolver exposing a get_dependency handler.

    :param test_command: The synchronous domain event to resolve.
    :type test_command: DomainEvent
    :return: A mock exposing a get_dependency resolution handler.
    :rtype: mock.Mock
    '''

    # Create a mock resolver returning the synchronous event for any service id.
    services = mock.Mock()
    services.get_dependency.return_value = test_command

    # Return the mock resolver.
    return services

# ** fixture: async_services
@pytest.fixture
def async_services(async_test_command: AsyncDomainEvent) -> mock.Mock:
    '''
    Fixture providing a mock service resolver returning the async domain event.

    :param async_test_command: The asynchronous domain event to resolve.
    :type async_test_command: AsyncDomainEvent
    :return: A mock exposing a get_dependency resolution handler.
    :rtype: mock.Mock
    '''

    # Create a mock resolver returning the asynchronous event for any service id.
    services = mock.Mock()
    services.get_dependency.return_value = async_test_command

    # Return the mock resolver.
    return services

# ** fixture: feature_context
@pytest.fixture
def feature_context(services: mock.Mock) -> FeatureContext:
    '''
    Fixture to create a new FeatureContext wired with the sync resolver.

    :param services: The mock service resolver.
    :type services: mock.Mock
    :return: A FeatureContext instance.
    :rtype: FeatureContext
    '''

    # Create an instance of FeatureContext with the injected resolution handler.
    return FeatureContext(get_dependency=services.get_dependency)

# ** fixture: async_feature_context
@pytest.fixture
def async_feature_context(async_services: mock.Mock) -> FeatureContext:
    '''
    Fixture to create a new FeatureContext wired with the async resolver.

    :param async_services: The mock service resolver returning an async event.
    :type async_services: mock.Mock
    :return: A FeatureContext instance.
    :rtype: FeatureContext
    '''

    # Create an instance of FeatureContext with the injected resolution handler.
    return FeatureContext(get_dependency=async_services.get_dependency)

# ** fixture: feature
@pytest.fixture
def feature() -> Feature:
    '''
    Fixture to create a stepless feature domain object.

    :return: A Feature domain object with no steps.
    :rtype: Feature
    '''

    # Build and return a feature with an empty step list.
    return Feature(
        id='test_group.test_feature',
        group_id='test_group',
        feature_key='test_feature',
        name='Test Feature',
        description='A feature for testing purposes.',
        steps=[],
    )

# ** fixture: base_cache_builder
@pytest.fixture
def base_cache_builder() -> Callable:
    '''
    Fixture providing a plain cache-builder callable with no pre-seeding.

    :return: A callable that returns a fresh CacheContext.
    :rtype: Callable
    '''

    # Define a minimal cache-builder mirroring the unwrapped build_cache.
    def build_cache(cache: dict = None) -> CacheContext:
        return CacheContext(cache=cache)

    # Return the cache-builder.
    return build_cache

# *** tests

# ** test: feature_cache_prefix_value
def test_feature_cache_prefix_value():
    '''
    Test that FEATURE_CACHE_PREFIX is the expected namespace tuple.
    '''

    # Assert the prefix constant has the correct value.
    assert FEATURE_CACHE_PREFIX == ('app', 'features')

# ** test: add_default_features_seeds_cache
def test_add_default_features_seeds_cache(base_cache_builder: Callable):
    '''
    Test that add_default_features seeds Feature domain objects under the feature prefix.

    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Define a raw default-feature catalog keyed by feature id.
    catalog = {
        'test_group.test_feature': {
            'group_id': 'test_group',
            'feature_key': 'test_feature',
            'name': 'Test Feature',
            'steps': [],
        },
    }

    # Wrap the cache-builder and invoke it.
    cache = add_default_features(catalog)(base_cache_builder)()

    # Assert a typed Feature domain object was seeded under the prefix.
    feature = cache.get('test_group.test_feature', *FEATURE_CACHE_PREFIX)
    assert isinstance(feature, Feature)
    assert feature.id == 'test_group.test_feature'
    assert feature.name == 'Test Feature'

# ** test: add_default_features_empty_catalog
def test_add_default_features_empty_catalog(base_cache_builder: Callable):
    '''
    Test that add_default_features leaves the feature namespace empty for an empty catalog.

    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Wrap the cache-builder with an empty catalog and invoke it.
    cache = add_default_features({})(base_cache_builder)()

    # Assert the feature namespace holds no entries.
    assert cache.get_by_prefix(*FEATURE_CACHE_PREFIX) == {}

# ** test: run_coroutine_no_loop
def test_run_coroutine_no_loop():
    '''
    Test that run_coroutine drives a coroutine when no event loop is running.
    '''

    # Define a trivial coroutine.
    async def _coro():
        return 42

    # Assert the coroutine is driven to completion synchronously.
    assert run_coroutine(_coro()) == 42

# ** test: run_coroutine_from_running_loop
@pytest.mark.asyncio
async def test_run_coroutine_from_running_loop():
    '''
    Test that run_coroutine uses the thread fallback when a loop is already running.
    '''

    # Define a trivial coroutine.
    async def _coro():
        return 'threaded'

    # Assert the coroutine completes without raising RuntimeError.
    assert run_coroutine(_coro()) == 'threaded'

# ** test: merge_step_kwargs_priority
def test_merge_step_kwargs_priority():
    '''
    Test that merge_step_kwargs merges context, request, step, and override values in priority order.
    '''

    # Merge four sources that each declare the same key.
    merged = merge_step_kwargs(
        {'key': 'context', 'ctx_only': 1},
        {'key': 'request', 'req_only': 2},
        {'key': 'step', 'step_only': 3},
        key='override',
    )

    # Assert the highest-priority value wins and all sources contribute.
    assert merged['key'] == 'override'
    assert merged['ctx_only'] == 1
    assert merged['req_only'] == 2
    assert merged['step_only'] == 3

# ** test: build_step_chain_sync
def test_build_step_chain_sync(test_command: DomainEvent):
    '''
    Test that build_step_chain returns a sync callable that executes the command.

    :param test_command: The synchronous domain event to execute.
    :type test_command: DomainEvent
    '''

    # Build the synchronous chain with no middleware.
    chain = build_step_chain(test_command, {'key': 'value'}, [], is_async=False)

    # Assert the chain executes the command directly.
    assert chain() == {'status': 'success', 'data': {'key': 'value'}}

# ** test: build_step_chain_async
@pytest.mark.asyncio
async def test_build_step_chain_async(async_test_command: AsyncDomainEvent):
    '''
    Test that build_step_chain returns an async callable that awaits async commands.

    :param async_test_command: The asynchronous domain event to execute.
    :type async_test_command: AsyncDomainEvent
    '''

    # Build the asynchronous chain with no middleware.
    chain = build_step_chain(async_test_command, {'key': 'value'}, [], is_async=True)

    # Assert the awaited chain returns the async result.
    assert await chain() == {'status': 'async_success', 'data': {'key': 'value'}}

# ** test: build_step_chain_async_with_sync_command
@pytest.mark.asyncio
async def test_build_step_chain_async_with_sync_command(test_command: DomainEvent):
    '''
    Test that the async chain path handles a synchronous command correctly.

    :param test_command: The synchronous domain event to execute.
    :type test_command: DomainEvent
    '''

    # Build the asynchronous chain around a synchronous command.
    chain = build_step_chain(test_command, {'key': 'value'}, [], is_async=True)

    # Assert the sync command is called without awaiting its result.
    assert await chain() == {'status': 'success', 'data': {'key': 'value'}}

# ** test: build_step_chain_with_middleware
def test_build_step_chain_with_middleware(test_command: DomainEvent):
    '''
    Test that build_step_chain wraps the command in middleware in the correct order.

    :param test_command: The synchronous domain event to execute.
    :type test_command: DomainEvent
    '''

    # Track the middleware execution order.
    order = []

    # Define a middleware that records entry and exit.
    class TrackMiddleware:
        def __call__(self, event, kwargs, next_fn):
            order.append('pre')
            result = next_fn()
            order.append('post')
            return result

    # Build and execute the chain with a single middleware.
    build_step_chain(test_command, {'key': 'value'}, [TrackMiddleware()], is_async=False)()

    # Assert the middleware wrapped the command execution.
    assert order == ['pre', 'post']

# ** test: compose_step_middleware_feature_first
def test_compose_step_middleware_feature_first():
    '''
    Test that compose_step_middleware places feature-level middleware before step-level.
    '''

    # Create distinct middleware instances.
    feature_mw, step_mw = mock.Mock(), mock.Mock()

    # Assert feature-level middleware precedes step-level middleware.
    assert compose_step_middleware([feature_mw], [step_mw]) == [feature_mw, step_mw]

# ** test: compose_step_middleware_partial_inputs
def test_compose_step_middleware_partial_inputs():
    '''
    Test that compose_step_middleware tolerates empty and None inputs.
    '''

    # Create a single middleware instance.
    middleware = mock.Mock()

    # Assert each partial combination resolves to the expected list.
    assert compose_step_middleware([], []) == []
    assert compose_step_middleware(None, None) == []
    assert compose_step_middleware([middleware], []) == [middleware]
    assert compose_step_middleware([], [middleware]) == [middleware]

# ** test: parse_request_parameter_request_ref
def test_parse_request_parameter_request_ref():
    '''
    Test that parse_request_parameter extracts a $r.-prefixed value from request data.
    '''

    # Create a request containing the referenced key.
    request = RequestContext(data={'key': 'value'})

    # Assert the referenced value is returned.
    assert parse_request_parameter('$r.key', request) == 'value'

# ** test: parse_request_parameter_request_not_found
def test_parse_request_parameter_request_not_found():
    '''
    Test that parse_request_parameter raises REQUEST_NOT_FOUND when no request is given.
    '''

    # Assert the structured error is raised when no request is provided.
    with pytest.raises(TiferetError) as exc_info:
        parse_request_parameter('$r.key', None)

    # Assert the error carries the offending parameter.
    assert exc_info.value.error_code == 'REQUEST_NOT_FOUND'
    assert exc_info.value.kwargs.get('parameter') == '$r.key'

# ** test: parse_request_parameter_key_missing
def test_parse_request_parameter_key_missing():
    '''
    Test that parse_request_parameter raises PARAMETER_NOT_FOUND when the key is absent.
    '''

    # Create a request that does not contain the referenced key.
    request = RequestContext(data={})

    # Assert the structured error is raised when the key is missing.
    with pytest.raises(TiferetError) as exc_info:
        parse_request_parameter('$r.missing', request)

    # Assert the error carries the offending parameter.
    assert exc_info.value.error_code == 'PARAMETER_NOT_FOUND'
    assert exc_info.value.kwargs.get('parameter') == '$r.missing'

# ** test: parse_request_parameter_delegates_to_parse_parameter
def test_parse_request_parameter_delegates_to_parse_parameter(monkeypatch: pytest.MonkeyPatch):
    '''
    Test that non-$r. parameters are forwarded to ParseParameter.execute.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Import the static events module to patch the parameter parser.
    from tiferet.events import static as static_events

    # Capture the parameter forwarded to the static event.
    called = {}

    def fake_execute(parameter: str):
        called['parameter'] = parameter
        return 'parsed-value'

    # Patch the static parameter parser.
    monkeypatch.setattr(static_events.ParseParameter, 'execute', staticmethod(fake_execute))

    # Assert the non-prefixed parameter was delegated and its result returned.
    assert parse_request_parameter('$env.MY_VAR', RequestContext(data={})) == 'parsed-value'
    assert called['parameter'] == '$env.MY_VAR'

# ** test: evaluate_condition_empty
def test_evaluate_condition_empty():
    '''
    Test that evaluate_condition returns True for None, empty, and blank conditions.
    '''

    # Create an empty request.
    request = RequestContext(data={})

    # Assert unconditional steps evaluate to True.
    assert evaluate_condition(None, request) is True
    assert evaluate_condition('', request) is True
    assert evaluate_condition('   ', request) is True

# ** test: evaluate_condition_request_ref
def test_evaluate_condition_request_ref():
    '''
    Test that evaluate_condition resolves $r. references from request data.
    '''

    # Create a request with numeric and string values.
    request = RequestContext(data={'x': 5, 'mode': 'advanced'})

    # Assert the resolved expressions evaluate correctly.
    assert evaluate_condition('$r.x > 0', request) is True
    assert evaluate_condition('$r.x > 100', request) is False
    assert evaluate_condition("$r.mode == 'advanced'", request) is True

# ** test: evaluate_condition_invalid_returns_false
def test_evaluate_condition_invalid_returns_false():
    '''
    Test that evaluate_condition returns False for missing keys and unparseable expressions.
    '''

    # Create an empty request.
    request = RequestContext(data={})

    # Assert failures resolve to False rather than raising.
    assert evaluate_condition('$r.x > 0', request) is False
    assert evaluate_condition('$r.x >>>!!! invalid', request) is False

# ** test: validate_request_no_schema_is_noop
def test_validate_request_no_schema_is_noop(feature: Feature):
    '''
    Test that validate_request leaves request data unchanged when the feature has no schema.

    :param feature: The schema-less feature domain object.
    :type feature: Feature
    '''

    # Create a request with raw string data.
    request = RequestContext(data={'a': '5'})

    # Validate against a schema-less feature.
    validate_request(feature, request)

    # Assert the data is unchanged.
    assert request.data == {'a': '5'}

# ** test: validate_request_coerces_data
def test_validate_request_coerces_data():
    '''
    Test that validate_request coerces request data to the feature's declared types.
    '''

    # Build a feature declaring an int/float schema.
    feature = Feature(
        id='calc.add',
        name='Add',
        params_schema={'a': 'int', 'b': 'float'},
        steps=[],
    )
    request = RequestContext(data={'a': '5', 'b': '2'})

    # Validate and coerce the request.
    validate_request(feature, request)

    # Assert the data was coerced to the declared types.
    assert request.data['a'] == 5
    assert request.data['b'] == 2.0

# ** test: validate_request_invalid_data_raises
def test_validate_request_invalid_data_raises():
    '''
    Test that validate_request raises REQUEST_VALIDATION_FAILED for type-incompatible data.
    '''

    # Build a feature declaring an int schema.
    feature = Feature(
        id='calc.add',
        name='Add',
        params_schema={'a': 'int'},
        steps=[],
    )
    request = RequestContext(data={'a': 'notint'})

    # Assert the structured validation error is raised.
    with pytest.raises(TiferetError) as exc_info:
        validate_request(feature, request)

    # Assert the error code identifies the validation failure.
    assert exc_info.value.error_code == 'REQUEST_VALIDATION_FAILED'

# ** test: feature_context_init
def test_feature_context_init(services: mock.Mock):
    '''
    Test that the constructor stores the resolution handler, cache, and context data.

    :param services: The mock service resolver.
    :type services: mock.Mock
    '''

    # Create a context with an explicit cache and context data.
    cache = CacheContext()
    context = FeatureContext(
        get_dependency=services.get_dependency,
        cache=cache,
        context_data={'ctx': 'value'},
    )

    # Assert each collaborator was stored as provided.
    assert context.get_dependency is services.get_dependency
    assert context.cache is cache
    assert context.context_data == {'ctx': 'value'}

# ** test: feature_context_init_defaults
def test_feature_context_init_defaults(feature_context: FeatureContext):
    '''
    Test that the constructor defaults the cache and context data when omitted.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    '''

    # Assert the cache defaults to a fresh context and the data to an empty dict.
    assert isinstance(feature_context.cache, CacheContext)
    assert feature_context.context_data == {}

# ** test: feature_context_domain_type
def test_feature_context_domain_type():
    '''
    Test that FeatureContext declares Feature as its domain type and is registered.
    '''

    # Assert the context declares the feature domain type.
    assert FeatureContext.domain_type is Feature

    # Assert the context is resolvable from the context registry.
    assert ContextMeta.registry.get(Feature) is FeatureContext
    assert BaseContext.for_domain(Feature) is FeatureContext

# ** test: feature_context_resolve_step_event_combines_flags
def test_feature_context_resolve_step_event_combines_flags(
    feature_context: FeatureContext,
    services: mock.Mock,
    test_command: DomainEvent,
):
    '''
    Test that resolve_step_event combines feature-level and step-level flags in order.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param services: The mock service resolver.
    :type services: mock.Mock
    :param test_command: The resolved domain event.
    :type test_command: DomainEvent
    '''

    # Build a step declaring its own flags.
    step = EventFeatureStep(
        name='Test Command',
        service_id='test_command',
        flags=['step_flag'],
    )

    # Resolve the step event with feature-level flags.
    event = feature_context.resolve_step_event(step, feature_flags=['feature_flag'])

    # Assert the resolver received both flag tiers in additive order.
    assert event is test_command
    services.get_dependency.assert_called_once_with('test_command', 'feature_flag', 'step_flag')

# ** test: feature_context_resolve_step_event_without_flags
def test_feature_context_resolve_step_event_without_flags(
    feature_context: FeatureContext,
    services: mock.Mock,
    test_command: DomainEvent,
):
    '''
    Test that resolve_step_event resolves a step that declares no flags.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param services: The mock service resolver.
    :type services: mock.Mock
    :param test_command: The resolved domain event.
    :type test_command: DomainEvent
    '''

    # Resolve a step with no configured flags.
    event = feature_context.resolve_step_event(
        EventFeatureStep(name='Test Command', service_id='test_command'),
    )

    # Assert the resolver was called with the service id alone.
    assert event is test_command
    services.get_dependency.assert_called_once_with('test_command')

# ** test: feature_context_resolve_step_event_failed
def test_feature_context_resolve_step_event_failed(feature_context: FeatureContext, services: mock.Mock):
    '''
    Test that resolve_step_event raises FEATURE_STEP_LOADING_FAILED on resolution failure.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param services: The mock service resolver.
    :type services: mock.Mock
    '''

    # Configure the resolver to fail for the step's service id.
    services.get_dependency.side_effect = TiferetError(
        'TEST_ERROR',
        'Feature step not found in services: non_existent_command',
    )

    # Assert the structured step-loading error is raised.
    with pytest.raises(TiferetError) as exc_info:
        feature_context.resolve_step_event(
            EventFeatureStep(name='Missing Command', service_id='non_existent_command'),
        )

    # Assert the error identifies the failing service id.
    assert exc_info.value.error_code == 'FEATURE_STEP_LOADING_FAILED'
    assert exc_info.value.kwargs.get('service_id') == 'non_existent_command'
    assert 'Failed to load feature step: non_existent_command' in str(exc_info.value)

# ** test: feature_context_resolve_middleware
def test_feature_context_resolve_middleware(
    feature_context: FeatureContext,
    services: mock.Mock,
    test_command: DomainEvent,
):
    '''
    Test that resolve_middleware resolves each service id from the app-scoped container.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param services: The mock service resolver.
    :type services: mock.Mock
    :param test_command: The resolved middleware instance.
    :type test_command: DomainEvent
    '''

    # Resolve two middleware service ids.
    middleware = feature_context.resolve_middleware(['mw_one', 'mw_two'])

    # Assert both resolved in order via the reserved 'app' flag.
    assert middleware == [test_command, test_command]
    services.get_dependency.assert_has_calls([
        mock.call('mw_one', 'app'),
        mock.call('mw_two', 'app'),
    ])

# ** test: feature_context_resolve_middleware_empty
def test_feature_context_resolve_middleware_empty(feature_context: FeatureContext, services: mock.Mock):
    '''
    Test that resolve_middleware returns an empty list for empty or None input.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param services: The mock service resolver.
    :type services: mock.Mock
    '''

    # Assert both empty inputs short-circuit without resolution.
    assert feature_context.resolve_middleware([]) == []
    assert feature_context.resolve_middleware(None) == []
    services.get_dependency.assert_not_called()

# ** test: feature_context_resolve_middleware_failed
def test_feature_context_resolve_middleware_failed(feature_context: FeatureContext, services: mock.Mock):
    '''
    Test that resolve_middleware raises MIDDLEWARE_LOADING_FAILED on resolution failure.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param services: The mock service resolver.
    :type services: mock.Mock
    '''

    # Configure the resolver to fail for the middleware id.
    services.get_dependency.side_effect = TiferetError(
        'TEST_ERROR',
        'Middleware not found in services: missing_mw',
    )

    # Assert the structured middleware-loading error is raised.
    with pytest.raises(TiferetError) as exc_info:
        feature_context.resolve_middleware(['missing_mw'])

    # Assert the error identifies the failing middleware id.
    assert exc_info.value.error_code == 'MIDDLEWARE_LOADING_FAILED'
    assert exc_info.value.kwargs.get('service_id') == 'missing_mw'
    assert 'Failed to load middleware: missing_mw' in str(exc_info.value)

# ** test: feature_context_execute_step_stores_result
def test_feature_context_execute_step_stores_result(feature_context: FeatureContext, test_command: DomainEvent):
    '''
    Test that execute_step stores the command result on the request.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param test_command: The synchronous domain event to execute.
    :type test_command: DomainEvent
    '''

    # Create a request carrying the command inputs.
    request = RequestContext(data={'key': 'value'})

    # Execute the step with pre-merged kwargs.
    feature_context.execute_step(test_command, request, request.data)

    # Assert the result is available as the request response.
    assert request.handle_response() == {'status': 'success', 'data': {'key': 'value'}}

# ** test: feature_context_execute_step_with_data_key
def test_feature_context_execute_step_with_data_key(feature_context: FeatureContext, test_command: DomainEvent):
    '''
    Test that execute_step stores the result under the data key when provided.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param test_command: The synchronous domain event to execute.
    :type test_command: DomainEvent
    '''

    # Create a request carrying the command inputs.
    request = RequestContext(data={'key': 'value'})

    # Execute the step with a data key.
    feature_context.execute_step(test_command, request, request.data, data_key='response_data')

    # Assert the result was stored in the request data.
    assert request.data.get('response_data') == {'status': 'success', 'data': {'key': 'value'}}

# ** test: feature_context_execute_step_with_error
def test_feature_context_execute_step_with_error(feature_context: FeatureContext, test_command: DomainEvent):
    '''
    Test that execute_step propagates errors raised by the domain event.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param test_command: The synchronous domain event to execute.
    :type test_command: DomainEvent
    '''

    # Create a request that causes the event to fail verification.
    request = RequestContext(data={'key': None})

    # Assert the domain error propagates.
    with pytest.raises(TiferetError) as exc_info:
        feature_context.execute_step(test_command, request, request.data)

    # Assert the raised error is the event's own error.
    assert exc_info.value.error_code == 'KEY_NOT_FOUND'

# ** test: feature_context_execute_step_with_pass_on_error
def test_feature_context_execute_step_with_pass_on_error(feature_context: FeatureContext, test_command: DomainEvent):
    '''
    Test that execute_step suppresses errors when pass_on_error is True.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param test_command: The synchronous domain event to execute.
    :type test_command: DomainEvent
    '''

    # Create a request that causes the event to fail verification.
    request = RequestContext(data={'key': None})

    # Execute with pass_on_error so no exception propagates.
    feature_context.execute_step(test_command, request, request.data, pass_on_error=True)

    # Assert no result was recorded.
    assert not request.handle_response()

# ** test: feature_context_execute_step_with_middleware
def test_feature_context_execute_step_with_middleware(feature_context: FeatureContext, test_command: DomainEvent):
    '''
    Test that execute_step applies the provided middleware chain.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param test_command: The synchronous domain event to execute.
    :type test_command: DomainEvent
    '''

    # Track the middleware execution order.
    order = []

    # Define a middleware that records entry and exit.
    class TrackMiddleware:
        def __call__(self, event, kwargs, next_fn):
            order.append('pre')
            result = next_fn()
            order.append('post')
            return result

    # Execute the step wrapped in the middleware.
    request = RequestContext(data={'key': 'value'})
    feature_context.execute_step(test_command, request, request.data, middleware=[TrackMiddleware()])

    # Assert the middleware wrapped the execution and the result was stored.
    assert order == ['pre', 'post']
    assert request.handle_response() == {'status': 'success', 'data': {'key': 'value'}}

# ** test: feature_context_execute_step_async_with_async_command
@pytest.mark.asyncio
async def test_feature_context_execute_step_async_with_async_command(
    async_feature_context: FeatureContext,
    async_test_command: AsyncDomainEvent,
):
    '''
    Test that _execute_step_async awaits an asynchronous domain event.

    :param async_feature_context: The feature context to test.
    :type async_feature_context: FeatureContext
    :param async_test_command: The asynchronous domain event to execute.
    :type async_test_command: AsyncDomainEvent
    '''

    # Create a request carrying the command inputs.
    request = RequestContext(data={'key': 'value'})

    # Await the async step handler.
    await async_feature_context._execute_step_async(async_test_command, request, request.data)

    # Assert the awaited result was stored on the request.
    assert request.handle_response() == {'status': 'async_success', 'data': {'key': 'value'}}

# ** test: feature_context_execute_step_async_with_sync_command
@pytest.mark.asyncio
async def test_feature_context_execute_step_async_with_sync_command(
    async_feature_context: FeatureContext,
    test_command: DomainEvent,
):
    '''
    Test that _execute_step_async dispatches a synchronous domain event directly.

    :param async_feature_context: The feature context to test.
    :type async_feature_context: FeatureContext
    :param test_command: The synchronous domain event to execute.
    :type test_command: DomainEvent
    '''

    # Create a request carrying the command inputs.
    request = RequestContext(data={'key': 'value'})

    # Await the async step handler around a sync command.
    await async_feature_context._execute_step_async(test_command, request, request.data)

    # Assert the sync command result was stored on the request.
    assert request.handle_response() == {'status': 'success', 'data': {'key': 'value'}}

# ** test: feature_context_execute_step_async_pass_on_error
@pytest.mark.asyncio
async def test_feature_context_execute_step_async_pass_on_error(
    async_feature_context: FeatureContext,
    async_test_command: AsyncDomainEvent,
):
    '''
    Test that _execute_step_async suppresses errors when pass_on_error is True.

    :param async_feature_context: The feature context to test.
    :type async_feature_context: FeatureContext
    :param async_test_command: The asynchronous domain event to execute.
    :type async_test_command: AsyncDomainEvent
    '''

    # Create a request that causes the event to fail verification.
    request = RequestContext(data={'key': None})

    # Await the async step handler with pass_on_error enabled.
    await async_feature_context._execute_step_async(
        async_test_command,
        request,
        request.data,
        pass_on_error=True,
    )

    # Assert no result was recorded.
    assert not request.handle_response()

# ** test: feature_context_resolve_feature_steps_yields_steps
def test_feature_context_resolve_feature_steps_yields_steps(
    feature_context: FeatureContext,
    feature: Feature,
    test_command: DomainEvent,
):
    '''
    Test that resolve_feature_steps yields an (event, step, params) tuple per step.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param feature: The feature domain object to resolve.
    :type feature: Feature
    :param test_command: The resolved domain event.
    :type test_command: DomainEvent
    '''

    # Add two steps to the feature.
    step_a = EventFeatureStep(name='Step A', service_id='test_command')
    step_b = EventFeatureStep(name='Step B', service_id='test_command')
    feature.steps.extend([step_a, step_b])

    # Resolve the feature's steps.
    resolved = list(feature_context.resolve_feature_steps(feature, RequestContext(data={'key': 'value'})))

    # Assert both steps were yielded with the resolved event and empty params.
    assert resolved == [(test_command, step_a, {}), (test_command, step_b, {})]

# ** test: feature_context_resolve_feature_steps_skips_false_condition
def test_feature_context_resolve_feature_steps_skips_false_condition(
    feature_context: FeatureContext,
    feature: Feature,
):
    '''
    Test that resolve_feature_steps skips steps whose condition resolves to False.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param feature: The feature domain object to resolve.
    :type feature: Feature
    '''

    # Add a conditionally skipped step and an unconditional step.
    skipped = EventFeatureStep(name='Skipped', service_id='test_command', condition='$r.x > 100')
    executed = EventFeatureStep(name='Executed', service_id='test_command')
    feature.steps.extend([skipped, executed])

    # Resolve the feature's steps against data that fails the condition.
    resolved = list(feature_context.resolve_feature_steps(feature, RequestContext(data={'x': 5})))

    # Assert only the unconditional step was yielded.
    assert len(resolved) == 1
    assert resolved[0][1] is executed

# ** test: feature_context_resolve_feature_steps_parses_parameters
def test_feature_context_resolve_feature_steps_parses_parameters(
    feature_context: FeatureContext,
    feature: Feature,
):
    '''
    Test that resolve_feature_steps parses request-backed step parameters.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param feature: The feature domain object to resolve.
    :type feature: Feature
    '''

    # Add a step declaring a request-backed parameter.
    feature.steps.append(EventFeatureStep(
        name='Parameterized',
        service_id='test_command',
        parameters={'param': '$r.key'},
    ))

    # Resolve the feature's steps.
    resolved = list(feature_context.resolve_feature_steps(feature, RequestContext(data={'key': 'resolved_value'})))

    # Assert the parameter was resolved from the request data.
    assert resolved[0][2] == {'param': 'resolved_value'}

# ** test: feature_context_resolve_feature_steps_combines_flags_additively
def test_feature_context_resolve_feature_steps_combines_flags_additively(
    feature_context: FeatureContext,
    services: mock.Mock,
):
    '''
    Test that resolve_feature_steps combines execution, feature, and step flags additively.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param services: The mock service resolver.
    :type services: mock.Mock
    '''

    # Build a feature declaring a feature-level flag and a flagged step.
    feature = Feature(
        id='test.step_flags',
        name='Step Flags',
        flags=['feature_flag'],
        steps=[
            EventFeatureStep(
                name='Flagged Step',
                service_id='test_command',
                flags=['step_flag'],
            ),
        ],
    )

    # Resolve the steps with an execution-level flag.
    list(feature_context.resolve_feature_steps(feature, RequestContext(data={'key': 'value'}), 'exec_flag'))

    # Assert the resolver received all three flag tiers in additive order.
    services.get_dependency.assert_called_once_with(
        'test_command',
        'exec_flag',
        'feature_flag',
        'step_flag',
    )

# ** test: feature_context_execute_feature_sync
def test_feature_context_execute_feature_sync(feature_context: FeatureContext, feature: Feature):
    '''
    Test that execute_feature executes a synchronous feature step.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param feature: The feature domain object to execute.
    :type feature: Feature
    '''

    # Add a standard synchronous step.
    feature.steps.append(EventFeatureStep(name='Test Command', service_id='test_command'))

    # Execute the pre-loaded feature.
    request = RequestContext(data={'key': 'value'})
    feature_context.execute_feature(feature, request)

    # Assert the step result was recorded as the response.
    assert request.handle_response() == {'status': 'success', 'data': {'key': 'value'}}

# ** test: feature_context_execute_feature_with_request_parameter
def test_feature_context_execute_feature_with_request_parameter(feature_context: FeatureContext, feature: Feature):
    '''
    Test that execute_feature passes parsed step parameters to the step event.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param feature: The feature domain object to execute.
    :type feature: Feature
    '''

    # Add a step declaring a request-backed parameter and a data key.
    feature.steps.append(EventFeatureStep(
        name='Test Command',
        service_id='test_command',
        parameters=dict(param='$r.key'),
        data_key='response_data',
    ))

    # Execute the pre-loaded feature.
    request = RequestContext(data={'key': 'value'})
    feature_context.execute_feature(feature, request)

    # Assert the parameterized result was stored under the data key.
    assert request.data.get('response_data') == {
        'status': 'success',
        'data': {'key': 'value', 'param': 'value'},
    }

# ** test: feature_context_execute_feature_with_pass_on_error
def test_feature_context_execute_feature_with_pass_on_error(feature_context: FeatureContext, feature: Feature):
    '''
    Test that execute_feature honors a step's pass_on_error flag.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param feature: The feature domain object to execute.
    :type feature: Feature
    '''

    # Add a step that fails but passes on its error.
    feature.steps.append(EventFeatureStep(
        name='Test Command',
        service_id='test_command',
        pass_on_error=True,
    ))

    # Execute the pre-loaded feature with failing request data.
    request = RequestContext(data={'key': None})
    feature_context.execute_feature(feature, request)

    # Assert the error was suppressed and no result recorded.
    assert not request.handle_response()

# ** test: feature_context_execute_feature_accepts_flags
def test_feature_context_execute_feature_accepts_flags(feature_context: FeatureContext, feature: Feature):
    '''
    Test that execute_feature accepts caller-supplied execution flags.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param feature: The feature domain object to execute.
    :type feature: Feature
    '''

    # Add a standard synchronous step.
    feature.steps.append(EventFeatureStep(name='Test Command', service_id='test_command'))

    # Execute the feature with execution flags.
    request = RequestContext(data={'key': 'value'})
    feature_context.execute_feature(feature, request, 'flag_a', 'flag_b')

    # Assert execution completed normally.
    assert request.handle_response() == {'status': 'success', 'data': {'key': 'value'}}

# ** test: feature_context_execute_feature_with_feature_middleware
def test_feature_context_execute_feature_with_feature_middleware(
    feature_context: FeatureContext,
    services: mock.Mock,
    feature: Feature,
    test_command: DomainEvent,
):
    '''
    Test that execute_feature resolves and applies feature-level middleware.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param services: The mock service resolver.
    :type services: mock.Mock
    :param feature: The feature domain object to execute.
    :type feature: Feature
    :param test_command: The resolved domain event.
    :type test_command: DomainEvent
    '''

    # Track the middleware invocation counts.
    call_counts = {'pre': 0, 'post': 0}

    # Define a counting middleware.
    class CountMiddleware:
        def __call__(self, event, kwargs, next_fn):
            call_counts['pre'] += 1
            result = next_fn()
            call_counts['post'] += 1
            return result

    # Declare feature-level middleware and a single step.
    feature.middleware = ['count_middleware']
    feature.steps.append(EventFeatureStep(name='Test Command', service_id='test_command'))

    # Resolve the middleware and the step event per service id.
    middleware = CountMiddleware()
    services.get_dependency.side_effect = lambda service_id, *flags: (
        middleware if service_id == 'count_middleware' else test_command
    )

    # Execute the pre-loaded feature.
    request = RequestContext(data={'key': 'value'})
    feature_context.execute_feature(feature, request)

    # Assert the middleware wrapped the single step execution once.
    assert call_counts == {'pre': 1, 'post': 1}
    assert request.handle_response() == {'status': 'success', 'data': {'key': 'value'}}

# ** test: feature_context_execute_feature_validates_and_coerces
def test_feature_context_execute_feature_validates_and_coerces(
    feature_context: FeatureContext,
    services: mock.Mock,
):
    '''
    Test that execute_feature coerces request data before any step runs.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param services: The mock service resolver.
    :type services: mock.Mock
    '''

    # Capture the kwargs the step event receives.
    captured = {}

    class CaptureEvent(DomainEvent):
        def execute(self, a=None, b=None, **kwargs):
            captured.update(a=a, b=b)
            return {'a': a, 'b': b}

    # Resolve the capturing event for the step.
    services.get_dependency.return_value = CaptureEvent()

    # Build a feature declaring a params schema.
    feature = Feature(
        id='calc.add',
        name='Add',
        params_schema={'a': 'int', 'b': 'float'},
        steps=[EventFeatureStep(name='cap', service_id='cap')],
    )

    # Execute the feature with raw string request data.
    request = RequestContext(data={'a': '5', 'b': '2'})
    feature_context.execute_feature(feature, request)

    # Assert the data was coerced before the step received it.
    assert request.data['a'] == 5
    assert request.data['b'] == 2.0
    assert captured == {'a': 5, 'b': 2.0}

# ** test: feature_context_execute_feature_invalid_request_fails_fast
def test_feature_context_execute_feature_invalid_request_fails_fast(
    feature_context: FeatureContext,
    services: mock.Mock,
):
    '''
    Test that invalid request data fails before any step executes.

    :param feature_context: The feature context to test.
    :type feature_context: FeatureContext
    :param services: The mock service resolver.
    :type services: mock.Mock
    '''

    # Track step executions.
    calls = {'count': 0}

    class CountEvent(DomainEvent):
        def execute(self, **kwargs):
            calls['count'] += 1

    # Resolve the counting event for the step.
    services.get_dependency.return_value = CountEvent()

    # Build a feature whose schema rejects the request.
    feature = Feature(
        id='calc.add',
        name='Add',
        params_schema={'a': 'int'},
        steps=[EventFeatureStep(name='cap', service_id='cap')],
    )

    # Assert the validation error is raised.
    with pytest.raises(TiferetError) as exc_info:
        feature_context.execute_feature(feature, RequestContext(data={'a': 'notint'}))

    # Assert no step ran.
    assert exc_info.value.error_code == 'REQUEST_VALIDATION_FAILED'
    assert calls['count'] == 0

# ** test: feature_context_execute_feature_async_feature
def test_feature_context_execute_feature_async_feature(
    async_feature_context: FeatureContext,
    feature: Feature,
):
    '''
    Test that an async feature drives the full step loop via run_coroutine.

    :param async_feature_context: The feature context to test.
    :type async_feature_context: FeatureContext
    :param feature: The feature domain object to execute.
    :type feature: Feature
    '''

    # Flag the feature as async and add a step.
    feature.is_async = True
    feature.steps.append(EventFeatureStep(name='Async Command', service_id='async_test_command'))

    # Execute the feature synchronously.
    request = RequestContext(data={'key': 'value'})
    async_feature_context.execute_feature(feature, request)

    # Assert the async step result was recorded.
    assert request.handle_response() == {'status': 'async_success', 'data': {'key': 'value'}}

# ** test: feature_context_execute_feature_async_mixed_chain
def test_feature_context_execute_feature_async_mixed_chain(feature: Feature):
    '''
    Test that an async feature supports a mixed sync/async step chain.

    :param feature: The feature domain object to execute.
    :type feature: Feature
    '''

    # Define a synchronous and an asynchronous step event.
    class SyncStep(DomainEvent):
        def execute(self, key=None, **kwargs):
            return {'sync': True, 'key': key}

    class AsyncStep(AsyncDomainEvent):
        async def execute(self, key=None, **kwargs):
            return {'async': True, 'key': key}

    # Resolve each event by service id.
    sync_event, async_event = SyncStep(), AsyncStep()
    services = mock.Mock()
    services.get_dependency.side_effect = lambda service_id, *flags: (
        sync_event if service_id == 'sync_step' else async_event
    )

    # Flag the feature as async and add both steps.
    feature.is_async = True
    feature.steps.append(EventFeatureStep(name='Sync Step', service_id='sync_step', data_key='sync_result'))
    feature.steps.append(EventFeatureStep(name='Async Step', service_id='async_step', data_key='async_result'))

    # Execute the feature synchronously.
    request = RequestContext(data={'key': 'mixed'})
    FeatureContext(get_dependency=services.get_dependency).execute_feature(feature, request)

    # Assert both steps executed and stored their results.
    assert request.data.get('sync_result') == {'sync': True, 'key': 'mixed'}
    assert request.data.get('async_result') == {'async': True, 'key': 'mixed'}

# ** test: feature_context_execute_feature_step_level_async
def test_feature_context_execute_feature_step_level_async(
    async_feature_context: FeatureContext,
    feature: Feature,
):
    '''
    Test that an async step within a sync feature is driven via run_coroutine.

    :param async_feature_context: The feature context to test.
    :type async_feature_context: FeatureContext
    :param feature: The feature domain object to execute.
    :type feature: Feature
    '''

    # Add an async step to an otherwise synchronous feature.
    feature.steps.append(EventFeatureStep(
        name='Async Step',
        service_id='async_cmd',
        is_async=True,
    ))

    # Execute the feature synchronously.
    request = RequestContext(data={'key': 'value'})
    async_feature_context.execute_feature(feature, request)

    # Assert the async step produced the expected result.
    assert request.handle_response() == {'status': 'async_success', 'data': {'key': 'value'}}
