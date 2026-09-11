"""Tiferet Tester Blueprints"""

# *** imports

# ** core
import functools
import inspect
from typing import Any, Callable, Dict

# ** app
from ..assets.tester import (
    CORE_DEFAULT_TESTERS,
    CORE_DEFAULT_TESTER_SESSIONS,
)
from ..contexts.app import add_default_app_sessions
from ..contexts.cache import CacheContext
from ..contexts.tester import (
    AggregateTesterContext,
    DomainEventTesterContext,
    DomainTesterContext,
    GenericTesterContext,
    ServiceEventTesterContext,
    TesterContext,
    TesterObject,
    TestSessionContext,
    TransferObjectTesterContext,
    add_default_testers,
)
from . import core

# *** functions

# ** function: inject_test_session
def _inject_test_session(fn: Callable, test_ctx: TesterContext) -> Callable:
    '''
    Wrap a callable to inject test_ctx and session by parameter name.

    :param fn: The callable to wrap.
    :type fn: Callable
    :param test_ctx: The master tester context reused across calls.
    :type test_ctx: TesterContext
    :return: The wrapped callable with test_ctx and session stripped from its signature.
    :rtype: Callable
    '''

    # Read the original parameter names once.
    signature = inspect.signature(fn)
    parameters = signature.parameters

    # Inject by name on each call and strip those names from the wrapper signature.
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):

        # Build a fresh session per call; reuse the master tester context.
        session = build_test_session(test_ctx)
        if 'test_ctx' in parameters:
            kwargs['test_ctx'] = test_ctx
        if 'session' in parameters:
            kwargs['session'] = session

        # Delegate to the original callable.
        return fn(*args, **kwargs)

    # Drop test_ctx and session so pytest does not look them up as fixtures.
    wrapper.__signature__ = signature.replace(
        parameters=[
            parameter
            for parameter in signature.parameters.values()
            if parameter.name not in ('test_ctx', 'session')
        ]
    )

    # Return the injecting wrapper.
    return wrapper

# ** function: wrap_member
def _wrap_member(member: Any, test_ctx: TesterContext) -> Any:
    '''
    Wrap a class member when its signature declares test_ctx or session.

    Duck-types pytest fixture objects without importing pytest.

    :param member: The class member to consider.
    :type member: Any
    :param test_ctx: The master tester context reused across calls.
    :type test_ctx: TesterContext
    :return: The original fixture object or the wrapped callable.
    :rtype: Any
    '''

    # Unwrap duck-typed fixture objects, then fall back to the member itself.
    inner = member
    restore_attr = None
    for attr in ('_fixture_function', 'func'):
        candidate = getattr(member, attr, None)
        if callable(candidate) and candidate is not member:
            inner = candidate
            restore_attr = attr
            break
    else:
        candidate = getattr(member, '__wrapped__', None)
        if (
            callable(candidate)
            and candidate is not member
            and not inspect.isfunction(member)
        ):
            inner = candidate
            restore_attr = '__wrapped__'

    # Skip non-callables and members whose signature cannot be read.
    if not callable(inner):
        return member
    try:
        parameters = inspect.signature(inner).parameters
    except (TypeError, ValueError):
        return member

    # Skip members that declare neither injection name.
    if 'test_ctx' not in parameters and 'session' not in parameters:
        return member

    # Wrap the inner callable.
    wrapped = _inject_test_session(inner, test_ctx)

    # Restore the wrapped inner onto the fixture object when unwrapped.
    if restore_attr is not None:
        setattr(member, restore_attr, wrapped)
        if getattr(member, '__wrapped__', None) is inner:
            member.__wrapped__ = wrapped
        if getattr(member, '_fixture_function', None) is inner:
            member._fixture_function = wrapped
        return member

    # Return the wrapped callable when no unwrap occurred.
    return wrapped

# *** blueprints

# ** blueprint: build_cache
@add_default_app_sessions(CORE_DEFAULT_TESTER_SESSIONS)
@add_default_testers(CORE_DEFAULT_TESTERS)
def build_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''
    Build the tester-scoped cache by wrapping core.build_cache.

    :param cache: An optional initial cache dictionary for the root namespace.
    :type cache: Dict[str, Any]
    :return: The cache seeded with testers and the tester session.
    :rtype: CacheContext
    '''

    # Delegate to the core cache builder; stacked decorators seed testers and sessions.
    return core.build_cache(cache)

# ** blueprint: build_tester_context
def build_tester_context(tester: TesterObject) -> TesterContext:
    '''
    Bind a TesterObject to the matching specialized tester context.

    :param tester: The tester domain object.
    :type tester: TesterObject
    :return: The variant tester context bound to the tester.
    :rtype: TesterContext
    '''

    # Select the specialized context class from the tester type.
    context_cls = {
        'domain': DomainTesterContext,
        'aggregate': AggregateTesterContext,
        'transfer_object': TransferObjectTesterContext,
        'domain_event': DomainEventTesterContext,
        'service_event': ServiceEventTesterContext,
        'generic': GenericTesterContext,
    }[tester.type]

    # Bind and return the selected context.
    return context_cls.from_domain(tester)

# ** blueprint: build_test_session
def build_test_session(
        tester_ctx: TesterContext,
        **request_fields: Any,
    ) -> TestSessionContext:
    '''
    Construct a test session bound to a tester context.

    :param tester_ctx: The bound tester context.
    :type tester_ctx: TesterContext
    :param request_fields: RequestContext fields such as session_id and data.
    :type request_fields: dict
    :return: The test session.
    :rtype: TestSessionContext
    '''

    # Construct the session as a request with the tester collaborator.
    return TestSessionContext(tester_ctx, **request_fields)

# ** blueprint: use_tester
def use_tester(
        type: str = 'generic',
        target_cls: type = None,
        id: str = None,
        **fields,
    ) -> Callable:
    '''
    Decorate a test class or function with a bound tester context and session.

    :param type: The tester type. Defaults to generic.
    :type type: str
    :param target_cls: Optional target class used to fill module_path and class_name.
    :type target_cls: type
    :param id: Optional tester id. Derived as ``{type}.{class_name}`` when omitted.
    :type id: str
    :param fields: Remaining TesterObject fields, including module_path and class_name.
    :type fields: dict
    :return: A class or function decorator.
    :rtype: Callable
    '''

    # Pop construction fields that are not TesterObject attributes.
    module_path = fields.pop('module_path', None)
    class_name = fields.pop('class_name', None)
    aggregate_cls = fields.pop('aggregate_cls', None)

    # Fill import coordinates from target_cls when those fields are unset.
    if target_cls is not None:
        if module_path is None:
            module_path = target_cls.__module__
        if class_name is None:
            class_name = target_cls.__name__

    # Fill aggregate import coordinates from aggregate_cls when unset.
    if aggregate_cls is not None:
        fields.setdefault('aggregate_module_path', aggregate_cls.__module__)
        fields.setdefault('aggregate_class_name', aggregate_cls.__name__)

    # Derive the tester id from type and class_name when omitted.
    tester_id = id
    if not tester_id and class_name:
        tester_id = f'{type}.{class_name}'

    # Construct one tester and one master context at decoration.
    tester = TesterObject(
        type=type,
        id=tester_id,
        module_path=module_path,
        class_name=class_name,
        **fields,
    )
    test_ctx = build_tester_context(tester)

    # Return a decorator that reuses the same master context.
    def decorator(obj):

        # Wrap own-namespace class members that declare test_ctx or session.
        if inspect.isclass(obj):
            for name, member in list(obj.__dict__.items()):
                if name.startswith('__'):
                    continue
                setattr(obj, name, _wrap_member(member, test_ctx))
            return obj

        # Wrap a single function.
        return _inject_test_session(obj, test_ctx)

    # Return the decorator.
    return decorator
