"""Tiferet Tester Blueprints"""

# *** imports

# ** core
import builtins
import functools
import inspect
import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict

# ** app
from .. import a
from ..assets import TiferetError
from ..assets.tester import (
    CORE_DEFAULT_TESTERS,
    CORE_DEFAULT_TESTER_SESSIONS,
    TEST_MODULE_LOAD_FAILED_ID,
)
from ..contexts.app import (
    add_default_app_constants,
    add_default_app_services,
    add_default_app_sessions,
)
from ..contexts.cache import CacheContext
from ..contexts.core import BaseContext
from ..contexts.test import PhaseRuntime, PhaseRuntimeContext
from ..contexts.tester import (
    AggregateTesterContext,
    ContextTesterContext,
    DomainEventTesterContext,
    DomainTesterContext,
    GenericTesterContext,
    RepoTesterContext,
    ServiceEventTesterContext,
    TestSessionContext,
    TesterContext,
    TesterObject,
    TransferObjectTesterContext,
    add_default_testers,
)
from ..contexts.test_module import TestModuleContext
from ..events import DomainEvent
from ..events.yaml import GetAnchoredYaml
from . import core

# *** functions

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

# ** function: wrap_member
def _wrap_member(member: Any, test_ctx: TesterContext) -> Any:
    '''
    Wrap a class member when its signature lists test_ctx or session.

    Duck-type unwrap pytest fixture objects without importing pytest, wrap
    the inner callable, and restore the fixture object.

    :param member: The class member to inspect.
    :type member: Any
    :param test_ctx: The decoration-time master tester context.
    :type test_ctx: TesterContext
    :return: The wrapped member, or the original member when no wrap applies.
    :rtype: Any
    '''

    # Duck-type unwrap a pytest fixture object to its underlying function.
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

    # Skip members whose callable signature cannot be read.
    if not callable(inner):
        return member
    try:
        parameters = inspect.signature(inner).parameters
    except (TypeError, ValueError):
        return member

    # Wrap only members that declare test_ctx or session.
    if 'test_ctx' not in parameters and 'session' not in parameters:
        return member
    wrapped = _inject_test_session(inner, test_ctx)

    # Restore a fixture object so pytest still recognizes the member.
    if restore_attr is None:
        return wrapped
    setattr(member, restore_attr, wrapped)
    if getattr(member, '__wrapped__', None) is inner:
        member.__wrapped__ = wrapped
    if getattr(member, '_fixture_function', None) is inner:
        member._fixture_function = wrapped
    return member

# ** function: test_module_context
def _test_module_context(rel: str, base_dir: str):
    '''Bind a test-module context with the event-supplied YAML callable.'''

    # The event may import the loader. This blueprint does not.
    extension = DomainEvent.handle(GetAnchoredYaml)
    return TestModuleContext.bind(rel, base_dir, yaml_extension=extension)

# ** function: read_test_module_text
def _read_test_module_text(path: str):
    '''Read module bytes. A missing file is None and is not created.'''

    file = Path(path)
    if not file.is_file():
        return None
    try:
        raw = file.read_bytes()
    except OSError as error:
        TiferetError.raise_error(
            TEST_MODULE_LOAD_FAILED_ID,
            f'Failed to read the test module: {error}.',
            path=path,
        )
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError:
        TiferetError.raise_error(
            TEST_MODULE_LOAD_FAILED_ID,
            'A test module must be utf-8.',
            path=path,
        )

# ** function: created_parent_directories
def _created_parent_directories(parent: Path) -> list:
    '''Create missing parents and return the directories this call created.'''

    missing = []
    cursor = parent
    while not cursor.exists():
        missing.append(cursor)
        cursor = cursor.parent
    parent.mkdir(parents=True, exist_ok=True)
    return missing

# ** function: replace_test_module
def _replace_test_module(path: Path, text: str, *, create: bool) -> None:
    '''Replace the module with a sibling temp file. Delete that temp on failure.'''

    created = []
    temp_name = None
    replaced = False
    try:
        if create:
            created = _created_parent_directories(path.parent)
        descriptor, temp_name = tempfile.mkstemp(
            prefix='.test-module-',
            suffix='.yml',
            dir=str(path.parent),
        )
        with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(text)
        os.replace(temp_name, path)
        replaced = True
        temp_name = None
    finally:
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except OSError:
                pass
        if not replaced:
            for directory in created:
                try:
                    directory.rmdir()
                except OSError:
                    break

# ** function: write_test_module
def _write_test_module(rel: str, base_dir: str, edit) -> None:
    '''Read bytes, delegate the edit, then replace. A failure leaves the file.'''

    context = _test_module_context(rel, base_dir)
    raw = _read_test_module_text(context.domain.path)
    text = edit(context, raw)
    _replace_test_module(Path(context.domain.path), text, create=raw is None)

# ** function: read_test_module
def _read_test_module(rel: str, base_dir: str, edit):
    '''Read bytes and delegate. Do not replace the file.'''

    context = _test_module_context(rel, base_dir)
    raw = _read_test_module_text(context.domain.path)
    return edit(context, raw)


# *** blueprints

# ** blueprint: build_cache
@add_default_app_sessions(CORE_DEFAULT_TESTER_SESSIONS)
@add_default_testers(CORE_DEFAULT_TESTERS)
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

# ** blueprint: register_phase_handlers
def register_phase_handlers() -> Dict[str, Any]:
    '''
    Register the three phase handlers by name.

    The handlers are not entries in a default feature catalog. They do not
    decorate ``core.build_cache``. They are not dispatched through
    ``AppSessionContext``.

    :return: The handler registry, keyed by phase name.
    :rtype: Dict[str, Any]
    '''

    # Register the three handlers the dialect runs, in phase order.
    return {
        'conditions': PhaseRuntimeContext.handle_conditions,
        'execute': PhaseRuntimeContext.handle_execution,
        'assert': PhaseRuntimeContext.handle_assertion,
    }

# ** blueprint: build_phase_runtime
def build_phase_runtime(
        session: Any,
        tester_module_path: str,
        tester_class_name: str,
        tester_attributes: Dict[str, Any] = None,
        root_fixtures: Dict[str, Dict[str, Any]] = None,
        tester_fixtures: Dict[str, Dict[str, Any]] = None,
    ) -> PhaseRuntimeContext:
    '''
    Build the runtime that executes one test's phases.

    The value is a ``PhaseRuntime``. ``from_domain`` selects
    ``PhaseRuntimeContext``. This function does not construct that context
    by hand and does not return the domain value.

    :param session: The session whose data stores ``as`` results.
    :type session: Any
    :param tester_module_path: The tester class module.
    :type tester_module_path: str
    :param tester_class_name: The tester class name.
    :type tester_class_name: str
    :param tester_attributes: Attributes used by ``new``.
    :type tester_attributes: Dict[str, Any]
    :param root_fixtures: Root fixture specs.
    :type root_fixtures: Dict[str, Dict[str, Any]]
    :param tester_fixtures: Tester-local fixture specs.
    :type tester_fixtures: Dict[str, Dict[str, Any]]
    :return: The phase runtime context.
    :rtype: PhaseRuntimeContext
    '''

    # Build the value, then let the registry select the context.
    value = PhaseRuntime(
        tester_module_path=tester_module_path,
        tester_class_name=tester_class_name,
        tester_attributes=tester_attributes or {},
        root_fixtures=root_fixtures or {},
        tester_fixtures=tester_fixtures or {},
    )
    return BaseContext.from_domain(value, session=session)

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
        'repo': RepoTesterContext,
        'context': ContextTesterContext,
    }[tester.type]

    # Bind the selected subclass and inject the phase-runtime factory.
    return context_cls.from_domain(
        tester,
        build_phase_runtime_handler=build_phase_runtime,
    )

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

# ** blueprint: use_tester
def use_tester(
        type: str = 'generic',
        target_cls: type = None,
        id: str = None,
        **fields: Any,
    ) -> Callable:
    '''
    Decorate a test function or class with a bound tester context and session.

    :param type: The tester discriminator. Defaults to generic. Pass a type
        only when the decorator should convert to a specialized context.
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
    domain_cls = fields.pop('domain_cls', None)
    if target_cls is not None:
        module_path = module_path or target_cls.__module__
        class_name = class_name or target_cls.__name__
    if aggregate_cls is not None:
        fields.setdefault('aggregate_module_path', aggregate_cls.__module__)
        fields.setdefault('aggregate_class_name', aggregate_cls.__name__)
    if domain_cls is not None:
        fields.setdefault('domain_module_path', domain_cls.__module__)
        fields.setdefault('domain_class_name', domain_cls.__name__)

    # Construct one tester and one master context at decoration time.
    tester = TesterObject(
        type=type,
        id=id or f'{type}.{class_name}',
        module_path=module_path,
        class_name=class_name,
        **fields,
    )
    test_ctx = build_tester_context(tester)

    # Decorate a function, or wrap every class member that lists test_ctx or session.
    def decorator(obj: Callable) -> Callable:
        if isinstance(obj, builtins.type):
            for name, member in list(obj.__dict__.items()):
                if name.startswith('__'):
                    continue
                setattr(obj, name, _wrap_member(member, test_ctx))
            return obj
        return _inject_test_session(obj, test_ctx)

    return decorator


# ** blueprint: add_fixture
def add_fixture(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
        payload=None,
        fragment: str = None,
        alias: str = None,
        anchor: str = None,
        merge: str = None,
    ) -> None:
    '''Add one fixture. The payload stays opaque. The file is replaced here.'''

    _write_test_module(
        rel,
        base_dir,
        lambda context, raw: context.add_fixture(
            raw,
            name,
            tester=tester,
            payload=payload,
            fragment=fragment,
            alias=alias,
            anchor=anchor,
            merge=merge,
        ),
    )

# ** blueprint: get_fixture
def get_fixture(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
    ):
    '''Read one fixture. This does not replace the file.'''

    return _read_test_module(
        rel,
        base_dir,
        lambda context, raw: context.get_fixture(raw, name, tester=tester),
    )

# ** blueprint: list_fixtures
def list_fixtures(rel: str, *, base_dir: str = '.', tester: str = None):
    '''List fixture names in document order.'''

    return _read_test_module(
        rel,
        base_dir,
        lambda context, raw: context.list_fixtures(raw, tester=tester),
    )

# ** blueprint: update_fixture
def update_fixture(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
        payload=None,
        fragment: str = None,
        merge: str = None,
    ) -> None:
    '''Patch one fixture. The node object stays. The file is replaced here.'''

    _write_test_module(
        rel,
        base_dir,
        lambda context, raw: context.update_fixture(
            raw,
            name,
            tester=tester,
            payload=payload,
            fragment=fragment,
            merge=merge,
        ),
    )

# ** blueprint: remove_fixture
def remove_fixture(rel: str, name: str, *, base_dir: str = '.', tester: str = None) -> None:
    '''Remove one fixture pair. A missing name does not write.'''

    _write_test_module(
        rel,
        base_dir,
        lambda context, raw: context.remove_fixture(raw, name, tester=tester),
    )

# ** blueprint: add_test
def add_test(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
        payload=None,
        fragment: str = None,
        anchor: str = None,
    ) -> None:
    '''Add one test body. This is not attach.'''

    _write_test_module(
        rel,
        base_dir,
        lambda context, raw: context.add_test(
            raw,
            name,
            tester=tester,
            payload=payload,
            fragment=fragment,
            anchor=anchor,
        ),
    )

# ** blueprint: get_test
def get_test(rel: str, name: str, *, base_dir: str = '.', tester: str = None):
    '''Read one test. This does not replace the file.'''

    return _read_test_module(
        rel,
        base_dir,
        lambda context, raw: context.get_test(raw, name, tester=tester),
    )

# ** blueprint: list_tests
def list_tests(rel: str, *, base_dir: str = '.', tester: str = None):
    '''List test names in document order.'''

    return _read_test_module(
        rel,
        base_dir,
        lambda context, raw: context.list_tests(raw, tester=tester),
    )

# ** blueprint: update_test
def update_test(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
        payload=None,
        fragment: str = None,
    ) -> None:
    '''Patch one test. Phase keys are not inspected.'''

    _write_test_module(
        rel,
        base_dir,
        lambda context, raw: context.update_test(
            raw,
            name,
            tester=tester,
            payload=payload,
            fragment=fragment,
        ),
    )

# ** blueprint: remove_test
def remove_test(rel: str, name: str, *, base_dir: str = '.', tester: str = None) -> None:
    '''Remove one test pair.'''

    _write_test_module(
        rel,
        base_dir,
        lambda context, raw: context.remove_test(raw, name, tester=tester),
    )

# ** blueprint: add_tester
def add_tester(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        payload=None,
        fragment: str = None,
        anchor: str = None,
    ) -> None:
    '''Add one tester mapping. The initial fragment may carry aliases.'''

    _write_test_module(
        rel,
        base_dir,
        lambda context, raw: context.add_tester(
            raw,
            name,
            payload=payload,
            fragment=fragment,
            anchor=anchor,
        ),
    )

# ** blueprint: get_tester
def get_tester(rel: str, name: str, *, base_dir: str = '.'):
    '''Read one tester. This does not replace the file.'''

    return _read_test_module(rel, base_dir, lambda context, raw: context.get_tester(raw, name))

# ** blueprint: list_testers
def list_testers(rel: str, *, base_dir: str = '.'):
    '''List tester names in document order.'''

    return _read_test_module(rel, base_dir, lambda context, raw: context.list_testers(raw))

# ** blueprint: update_tester
def update_tester(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        payload=None,
        fragment: str = None,
    ) -> None:
    '''Patch one tester. fixtures and tests are refused.'''

    _write_test_module(
        rel,
        base_dir,
        lambda context, raw: context.update_tester(raw, name, payload=payload, fragment=fragment),
    )

# ** blueprint: remove_tester
def remove_tester(rel: str, name: str, *, base_dir: str = '.') -> None:
    '''Remove one tester pair.'''

    _write_test_module(rel, base_dir, lambda context, raw: context.remove_tester(raw, name))

# ** blueprint: attach_test
def attach_test(rel: str, tester: str, name: str, *, base_dir: str = '.') -> None:
    '''Contain a root test by node identity. Do not copy the body.'''

    _write_test_module(
        rel,
        base_dir,
        lambda context, raw: context.attach_test(raw, tester, name),
    )

# ** blueprint: detach_test
def detach_test(rel: str, tester: str, name: str, *, base_dir: str = '.') -> None:
    '''Drop one containment. Leave the root test and its anchor.'''

    _write_test_module(
        rel,
        base_dir,
        lambda context, raw: context.detach_test(raw, tester, name),
    )
