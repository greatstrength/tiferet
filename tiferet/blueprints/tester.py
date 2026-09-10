"""Tiferet Tester Blueprints"""

# *** imports

# ** core
import builtins
import functools
import inspect
from typing import Any, Callable, Dict

# ** app
from .. import a
from ..assets import tester
from ..contexts.app import (
    add_default_app_constants,
    add_default_app_services,
    add_default_app_sessions,
)
from ..contexts.cache import CacheContext
from ..contexts.error import add_default_errors
from ..contexts.logging import add_default_logging_settings
from ..contexts.tester import (
    TESTER_CACHE_PREFIX,
    AggregateTesterContext,
    DomainTesterContext,
    TestRequestContext,
    TestSessionContext,
    TesterContext,
    TesterObject,
    TransferObjectTesterContext,
    add_default_testers,
)
from ..events import DomainEvent
from ..events.tester import GetTester
from . import core

# *** blueprints

# ** blueprint: build_cache
@add_default_logging_settings(a.logging.CORE_DEFAULT_LOGGING_SETTINGS)
@add_default_app_sessions(a.tester.CORE_DEFAULT_TESTER_SESSIONS)
@add_default_testers(a.tester.CORE_DEFAULT_TESTERS)
@add_default_app_constants(
    {
        a.app.DI_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
        a.app.FEATURE_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
        a.app.LOGGING_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
        a.app.ERROR_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
    },
)
@add_default_app_services(
    {
        a.app.DI_SERVICE_ID: a.app.DI_SERVICE_DATA,
        a.app.FEATURE_SERVICE_ID: a.app.FEATURE_SERVICE_DATA,
        a.app.GET_FEATURE_EVT_ID: a.app.GET_FEATURE_EVT_DATA,
        a.app.LOGGING_SERVICE_ID: a.app.LOGGING_SERVICE_DATA,
        a.app.LOGGING_LIST_ALL_EVT_ID: a.app.LOGGING_LIST_ALL_EVT_DATA,
        a.app.ERROR_SERVICE_ID: a.app.ERROR_SERVICE_DATA,
        a.app.GET_ERROR_EVT_ID: a.app.GET_ERROR_EVT_DATA,
    },
)
@add_default_errors(a.error.CORE_DEFAULT_ERRORS)
def build_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''Build the tester-dialect cache without standard app session catalogs.

    Seeds logging settings, default errors, and the logging/error service
    trios needed for production-parity feature dispatch, while remaining
    isolated from ``CORE_DEFAULT_APP_SESSIONS``, CLI, and middleware.

    :param cache: Optional root namespace seed values.
    :type cache: Dict[str, Any] | None
    :return: The tester-scoped cache.
    :rtype: CacheContext
    '''

    # Extend the bare core cache with tester dialect catalogs plus logging/errors.
    return core.build_cache(cache)

# ** blueprint: resolve_tester
def resolve_tester(
        id: str,
        tester_config: str | None = None,
    ) -> TesterObject:
    '''Resolve one tester domain object from defaults or configuration.

    :param id: The tester identifier.
    :type id: str
    :param tester_config: Optional tester configuration file path.
    :type tester_config: str | None
    :return: The resolved tester domain object.
    :rtype: TesterObject
    '''

    # Build the isolated dialect cache and prefer its seeded default.
    cache = build_cache()
    tester = cache.get(id, *TESTER_CACHE_PREFIX)
    if tester is not None:
        return tester

    # Load the tester dialect session that declares its default service.
    app_session = core.get_app_session(a.tester.TIFERET_TESTER_ID, cache)

    # Apply a caller-supplied repository configuration without mutating the session.
    if tester_config is not None:
        constants = dict(app_session.constants)
        constants[a.tester.TESTER_CONFIG_ID] = tester_config
        app_session = app_session.model_copy(update={'constants': constants})

    # Compose the session's tester service through the standard app container.
    app_container = core.build_app_service_container(cache, app_session)
    tester_service = app_container.get_dependency(a.tester.TESTER_SERVICE_ID)

    # Resolve a non-default tester through its domain event and injected service.
    return DomainEvent.handle(
        GetTester,
        dependencies={
            'tester_service': tester_service,
        },
        id=id,
        default_tester_index=cache.get_by_prefix(*TESTER_CACHE_PREFIX),
    )

# ** blueprint: build_test_session_context
def build_test_session_context(
        app_session,
        cache: CacheContext,
        **context_kwargs,
    ) -> TestSessionContext:
    '''
    Build a fluent test-session context from a resolved app session.

    :param app_session: The resolved test application session.
    :type app_session: Any
    :param cache: The tester-scoped shared cache.
    :type cache: CacheContext
    :param context_kwargs: Additional context construction arguments.
    :type context_kwargs: dict
    :return: The fully wired fluent test-session context.
    :rtype: TestSessionContext
    '''

    # Compose the app container and feature-level resolver for this session.
    app_container = core.build_app_service_container(cache, app_session)
    resolver = core.build_service_resolver(app_container)

    # Compose the explicitly selected fluent session context and request handler.
    return core.compose_session_context(
        TestSessionContext,
        app_session,
        cache,
        app_container,
        resolver,
        create_request_handler=build_test_request,
        response_handler=core.response_handler,
        **context_kwargs,
    )

# ** blueprint: build_app
def build_app(
        interface_id: str = a.tester.TIFERET_TESTER_ID,
        module_path: str = a.app.DEFAULT_APP_SERVICE_MODULE_PATH,
        class_name: str = a.app.DEFAULT_APP_SERVICE_CLASS_NAME,
        **parameters: Any,
    ) -> TestSessionContext:
    '''
    Build the default fluent test session or a consumer-declared test session.

    :param interface_id: The test session identifier.
    :type interface_id: str
    :param module_path: The app-service module path for external sessions.
    :type module_path: str
    :param class_name: The app-service class name for external sessions.
    :type class_name: str
    :param parameters: Additional app-service constructor parameters.
    :type parameters: dict
    :return: The fully wired fluent test-session context.
    :rtype: TestSessionContext
    '''

    # Build the tester cache and resolve the requested session.
    cache = build_cache()
    app_session = core.get_app_session(
        interface_id,
        cache,
        module_path=module_path,
        class_name=class_name,
        **parameters,
    )

    # Compose and return the fluent test-session context.
    return build_test_session_context(app_session, cache)

# ** blueprint: build_tester_context
def build_tester_context(tester: TesterObject) -> TesterContext:
    '''Select the variant tester context class from the tester type.

    :param tester: The bound tester domain object.
    :type tester: TesterObject
    :return: The variant tester context.
    :rtype: TesterContext
    '''

    # Map the discriminator to the omitting-domain_type context subclass.
    context_cls = {
        'domain': DomainTesterContext,
        'aggregate': AggregateTesterContext,
        'transfer_object': TransferObjectTesterContext,
    }[tester.type]

    # Bind the selected subclass to the tester domain object.
    return context_cls.from_domain(tester)

# ** function: inject_test_ctx
def _inject_test_ctx(fn: Callable, tester: TesterObject) -> Callable:
    '''Wrap a test callable so it receives a bound tester context as test_ctx.'''

    # Preserve metadata while injecting the bound context.
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):

        # Bind a fresh variant context only when the test declares test_ctx.
        parameters = list(inspect.signature(fn).parameters)
        if 'test_ctx' not in parameters:
            return fn(*args, **kwargs)
        test_ctx = build_tester_context(tester)
        if parameters and parameters[0] == 'self':
            return fn(args[0], test_ctx, *args[1:], **kwargs)
        return fn(test_ctx, *args, **kwargs)

    # Strip test_ctx so pytest does not look up a missing fixture.
    signature = inspect.signature(fn)
    wrapper.__signature__ = signature.replace(
        parameters=[
            parameter
            for name, parameter in signature.parameters.items()
            if name != 'test_ctx'
        ],
    )
    return wrapper

# ** blueprint: use_tester
def use_tester(
        type: str,
        target_cls: type = None,
        id: str = None,
        **fields: Any,
    ) -> Callable:
    '''
    Decorate a test function or class with a bound tester context as test_ctx.

    :param type: The tester discriminator.
    :type type: str
    :param target_cls: Optional class that supplies module_path and class_name.
    :type target_cls: type
    :param id: Optional tester identifier.
    :type id: str
    :param fields: Remaining TesterObject fields, plus optional aggregate_cls.
    :type fields: Any
    :return: A function or class decorator.
    :rtype: Callable
    '''

    # Derive target coordinates from an optional class reference.
    module_path = fields.pop('module_path', None)
    class_name = fields.pop('class_name', None)
    aggregate_cls = fields.pop('aggregate_cls', None)
    if target_cls is not None:
        module_path = module_path or target_cls.__module__
        class_name = class_name or target_cls.__name__
    if aggregate_cls is not None:
        fields.setdefault('aggregate_module_path', aggregate_cls.__module__)
        fields.setdefault('aggregate_class_name', aggregate_cls.__name__)

    # Construct the single tester domain object once at decoration time.
    tester = TesterObject(
        type=type,
        id=id or f'{type}.{class_name}',
        module_path=module_path,
        class_name=class_name,
        **fields,
    )

    # Decorate a function, or wrap every test_* method on a class.
    def decorator(obj: Callable) -> Callable:
        if isinstance(obj, builtins.type):
            for name, member in list(obj.__dict__.items()):
                if name.startswith('test_') and callable(member):
                    setattr(obj, name, _inject_test_ctx(member, tester))
            return obj
        return _inject_test_ctx(obj, tester)

    return decorator

# ** blueprint: test_case
def test_case(
        interface_id: str = a.tester.TIFERET_TESTER_ID,
        **given: Any,
    ) -> Callable:
    '''
    Decorate a pytest test with a constant given-state baseline.

    :param interface_id: The test session identifier passed to Tester().
    :type interface_id: str
    :param given: Given-state values to seed before the test body.
    :type given: Any
    :return: A decorator that injects the tester context.
    :rtype: Callable
    '''

    # Return a wrapper that constructs the session without a pytest fixture.
    def decorator(fn: Callable) -> Callable:

        # Preserve function metadata while replacing fixture-based injection.
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):

            # Construct the fluent session and seed decoration-time state.
            tester_ctx = build_app(interface_id=interface_id)
            tester_ctx.given(**given)

            # Return the test body's result without dispatching the chain.
            return fn(tester_ctx, *args, **kwargs)

        # Strip tester_ctx so pytest does not look up a missing fixture.
        signature = inspect.signature(fn)
        wrapper.__signature__ = signature.replace(
            parameters=[
                parameter
                for name, parameter in signature.parameters.items()
                if name != 'tester_ctx'
            ],
        )
        return wrapper

    # Return the given-state decorator.
    return decorator

# ** blueprint: build_test_request
def build_test_request(
        interface_id: str,
        feature_id: str,
        headers: Dict[str, str] = None,
        data: Dict[str, Any] = None,
    ) -> TestRequestContext:
    '''
    Build a test-aware request context for a fluent session chain.

    :param interface_id: The test session identifier.
    :type interface_id: str
    :param feature_id: The pending feature identifier.
    :type feature_id: str
    :param headers: Optional request headers.
    :type headers: Dict[str, str] | None
    :param data: Optional request data.
    :type data: Dict[str, Any] | None
    :return: The initialized test request context.
    :rtype: TestRequestContext
    '''

    # Construct the specialized request and stamp its owning session id.
    return TestRequestContext(
        headers={**(headers or {}), 'interface_id': interface_id},
        data=data or {},
        feature_id=feature_id,
    )
