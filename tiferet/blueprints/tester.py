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
from ..contexts.tester import (
    TESTER_CACHE_PREFIX,
    AggregateTesterContext,
    DomainEventTesterContext,
    DomainTesterContext,
    GenericTesterContext,
    ServiceEventTesterContext,
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
@add_default_app_sessions(a.tester.CORE_DEFAULT_TESTER_SESSIONS)
@add_default_testers(a.tester.CORE_DEFAULT_TESTERS)
@add_default_app_constants(
    {
        a.app.DI_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
        a.app.FEATURE_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
    },
)
@add_default_app_services(
    {
        a.app.DI_SERVICE_ID: a.app.DI_SERVICE_DATA,
        a.app.FEATURE_SERVICE_ID: a.app.FEATURE_SERVICE_DATA,
        a.app.GET_FEATURE_EVT_ID: a.app.GET_FEATURE_EVT_DATA,
    },
)
def build_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''Build the tester-dialect cache without standard app catalogs.

    :param cache: Optional root namespace seed values.
    :type cache: Dict[str, Any] | None
    :return: The tester-scoped cache.
    :rtype: CacheContext
    '''

    # Extend the bare core cache with only tester dialect catalogs.
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
        'domain_event': DomainEventTesterContext,
        'service_event': ServiceEventTesterContext,
        'generic': GenericTesterContext,
    }[tester.type]

    # Bind the selected subclass to the tester domain object.
    return context_cls.from_domain(tester)

# ** blueprint: build_test_session
def build_test_session(
        tester_ctx: TesterContext,
        **request_fields: Any,
    ) -> TestSessionContext:
    '''
    Construct a test session bound to a tester context.

    :param tester_ctx: The bound variant tester context.
    :type tester_ctx: TesterContext
    :param request_fields: Optional RequestContext initialization fields.
    :type request_fields: dict
    :return: A new test session for one test request.
    :rtype: TestSessionContext
    '''

    # Construct the session directly; the tester context is a collaborator.
    return TestSessionContext(tester_ctx, **request_fields)

# ** function: inject_test_session
def _inject_test_session(fn: Callable, test_ctx: TesterContext) -> Callable:
    '''Wrap a test callable so it receives test_ctx and session by name.'''

    # Preserve metadata while injecting the bound master and a new session.
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):

        # Always build both internally; inject only the names the test declares.
        session = build_test_session(test_ctx)
        parameters = inspect.signature(fn).parameters
        if 'test_ctx' in parameters:
            kwargs['test_ctx'] = test_ctx
        if 'session' in parameters:
            kwargs['session'] = session
        return fn(*args, **kwargs)

    # Strip injected names so pytest does not look up missing fixtures.
    signature = inspect.signature(fn)
    wrapper.__signature__ = signature.replace(
        parameters=[
            parameter
            for name, parameter in signature.parameters.items()
            if name not in ('test_ctx', 'session')
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
    Decorate a test function or class with a bound tester context and session.

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

    # Construct one tester and one master context at decoration time.
    tester = TesterObject(
        type=type,
        id=id or f'{type}.{class_name}',
        module_path=module_path,
        class_name=class_name,
        **fields,
    )
    test_ctx = build_tester_context(tester)

    # Decorate a function, or wrap every test_* method on a class.
    def decorator(obj: Callable) -> Callable:
        if isinstance(obj, builtins.type):
            for name, member in list(obj.__dict__.items()):
                if name.startswith('test_') and callable(member):
                    setattr(obj, name, _inject_test_session(member, test_ctx))
            return obj
        return _inject_test_session(obj, test_ctx)

    return decorator
