"""Tiferet Tester Blueprints"""

# *** imports

# ** core
import builtins
import copy
import functools
import inspect
import os
from importlib import import_module
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Dict, List

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
from ..contexts.error import add_default_errors
from ..contexts.core import BaseContext
from ..contexts.test import (
    PHASE_ASSERT_ID,
    PHASE_CONDITIONS_ID,
    PHASE_EXECUTE_ID,
    PhaseRuntime,
    PhaseRuntimeContext,
    TestContext,
    compile_phase_steps,
)
from ..contexts.tester import (
    AggregateTesterContext,
    ContextTesterContext,
    DomainEventTesterContext,
    DomainTesterContext,
    GenericTesterContext,
    RepoTesterContext,
    ServiceEventTesterContext,
    ModelError,
    ModuleRunContext,
    TestSessionContext,
    TesterContext,
    TesterObject,
    TransferObjectTesterContext,
    add_default_testers,
)
from ..contexts.test_module import TestModuleContext
from ..events import DomainEvent
from ..events.yaml import GetAnchoredYaml, LoadYamlMapping
from ..mappers.test import TestConfigObject
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

# ** function: copy_tree
def _copy_tree(value: Any) -> Any:
    '''
    Copy a loaded mapping so two tests do not share one dict.

    :param value: The loaded value.
    :type value: Any
    :return: The copy.
    :rtype: Any
    '''

    # Anchors are already resolved. The copy is what a fixture or test builds from.
    return copy.deepcopy(value)

# ** function: phase_get_dependency
def _phase_get_dependency(test: Any, slot: Dict[str, Any]) -> Callable:
    '''
    Resolve compiled phase steps to the registered handlers.

    The handlers are not a default feature catalog and not the app resolver.

    :param test: The bound test whose phase objects the steps address.
    :type test: Any
    :param slot: The slot filled with the phase runtime before steps run.
    :type slot: Dict[str, Any]
    :return: A get_dependency callable.
    :rtype: Callable
    '''

    # The registered names are the dialect names, not the compiled service ids.
    handlers = register_phase_handlers()
    queues = {
        PHASE_CONDITIONS_ID: (
            'conditions',
            [test.conditions],
        ),
        PHASE_EXECUTE_ID: (
            'execute',
            list(test.executes),
        ),
        PHASE_ASSERT_ID: (
            'assert',
            list(test.asserts),
        ),
    }
    cursors = {
        service_id: 0
        for service_id in queues
    }

    # Each compiled step resolves once, in document order.
    def get_dependency(service_id: str, *flags) -> Any:
        kind, items = queues[service_id]
        index = cursors[service_id]
        cursors[service_id] = index + 1
        item = items[index]
        handler = handlers[kind]

        # Return the stored result so the feature step does not overwrite it.
        def execute(**kwargs):
            runtime = slot['runtime']
            handler(runtime, item)
            data_key = getattr(item, 'data_key', None)
            if data_key:
                return runtime.session.data[data_key]
            return None

        return SimpleNamespace(execute=execute)

    return get_dependency

# ** function: count_line
def _count_line(passed: int, failed: int) -> str:
    '''
    Format the count line. There is no skipped count.

    :param passed: The number of passed tests.
    :type passed: int
    :param failed: The number of failed tests.
    :type failed: int
    :return: The count line.
    :rtype: str
    '''

    # Both counts print failed first. An empty run is 0 passed.
    if failed and passed:
        return f'{failed} failed, {passed} passed'
    if failed:
        return f'{failed} failed'
    return f'{passed} passed'

# ** function: refuse_python_module
def _refuse_python_module(path: Path) -> None:
    '''
    Refuse a path that is not a Python test module under tests/.

    :param path: The input path.
    :type path: Path
    :return: None.
    :rtype: None
    '''

    # A missing file is a ValueError before any YAML load.
    if not path.is_file():
        raise ValueError(f'Python test module not found: {path}.')

    # Refuse YAML input, conftest, package markers, and non-test modules.
    if path.suffix != '.py' or not path.name.startswith('test_'):
        raise ValueError(f'Not a Python test module: {path}.')
    if path.name in ('conftest.py', '__init__.py'):
        raise ValueError(f'Not a Python test module: {path}.')
    if 'tests_int' in path.parts or 'tests' not in path.parts:
        raise ValueError(f'Not a tests/ module: {path}.')

# ** function: yaml_counterpart
def _yaml_counterpart(path: Path) -> tuple:
    '''
    Derive the YAML counterpart from a Python test module path.

    :param path: The Python module path.
    :type path: Path
    :return: The relative stem and the YAML path.
    :rtype: tuple
    '''

    # rel is the path under tests/, without the .py suffix.
    parts = path.parts
    index = len(parts) - 1 - list(reversed(parts)).index('tests')
    relative = Path(*parts[index + 1:]).with_suffix('')
    tests_root = Path(*parts[:index + 1])
    yaml_path = tests_root.parent / 'tiferet_tests' / relative.with_suffix('.yml')
    return relative.as_posix(), yaml_path

# ** function: load_test_document
def _load_test_document(yaml_path: Path) -> Dict[str, Any]:
    '''
    Load the YAML document. Do not write it and do not expand runtime refs.

    :param yaml_path: The counterpart path.
    :type yaml_path: Path
    :return: The loaded mapping.
    :rtype: Dict[str, Any]
    '''

    # The event may import the loader. This blueprint does not.
    load = DomainEvent.handle(LoadYamlMapping)
    document = load(yaml_path)

    # An empty file is a legal document with no tests.
    if document is None:
        document = {}
    if not isinstance(document, dict):
        raise ValueError('A test module document must be a mapping.')
    illegal = [
        key
        for key in document
        if key not in ('fixtures', 'tests', 'testers')
    ]
    if illegal:
        raise ValueError(f'Illegal test-module root: {illegal[0]}.')
    return document

# ** function: iter_document_tests
def _iter_document_tests(document: Dict[str, Any], node_root: str):
    '''
    Yield root tests, then each tester's contained tests, in document order.

    A tester is not a test. Fixtures are not tests.

    :param document: The loaded document.
    :type document: Dict[str, Any]
    :param node_root: The YAML node-id prefix.
    :type node_root: str
    :return: Node id, test key, copied test mapping, and phase coordinates.
    :rtype: tuple
    '''

    # Copy root fixtures once per test so an alias is not a shared dict.
    root_fixtures = document.get('fixtures') or {}
    if not isinstance(root_fixtures, dict):
        raise ValueError('fixtures must be a mapping.')

    # Root tests come first. A tester is not yielded here.
    for test_key, test_mapping in (document.get('tests') or {}).items():
        yield (
            f'{node_root}::{test_key}',
            test_key,
            test_mapping,
            {
                'tester_module_path': '',
                'tester_class_name': '',
                'tester_attributes': {},
                'root_fixtures': _copy_tree(root_fixtures),
                'tester_fixtures': {},
            },
        )

    # Contained tests follow, tester by tester.
    for tester_key, tester in (document.get('testers') or {}).items():
        if not isinstance(tester, dict):
            raise ValueError(f'Tester {tester_key} must be a mapping.')
        contained = tester.get('tests') or {}
        if not isinstance(contained, dict):
            raise ValueError(f'Tester {tester_key} tests must be a mapping.')
        for test_key, test_mapping in contained.items():
            yield (
                f'{node_root}::{tester_key}::{test_key}',
                test_key,
                test_mapping,
                {
                    'tester_module_path': tester.get('module_path') or '',
                    'tester_class_name': tester.get('class_name') or '',
                    'tester_attributes': _copy_tree(tester.get('attributes') or {}),
                    'root_fixtures': _copy_tree(root_fixtures),
                    'tester_fixtures': _copy_tree(tester.get('fixtures') or {}),
                },
            )

# ** function: build_module_test
def _build_module_test(test_key: str, test_mapping: Any, coordinates: Dict[str, Any]) -> TestContext:
    '''
    Build one Test through the config object and bind a TestContext.

    :param test_key: The grammar key, used as the Test name.
    :type test_key: str
    :param test_mapping: The copied phase document.
    :type test_mapping: Any
    :param coordinates: Phase-runtime coordinates for this test.
    :type coordinates: Dict[str, Any]
    :return: The bound test context.
    :rtype: TestContext
    '''

    # A test mapping is legal only with the three phase keys.
    if not isinstance(test_mapping, dict) or set(test_mapping) != {
        'conditions',
        'execute',
        'assert',
    }:
        raise ValueError(
            f'Test {test_key} is legal only with conditions, execute, and assert.',
        )

    # The config object maps execute and assert. Do not construct those field names.
    test = TestConfigObject.model_validate(_copy_tree(test_mapping)).map(
        id=f'test.{test_key}',
        name=test_key,
    )
    test.steps = compile_phase_steps(test)

    # The resolver reads the runtime the context builds on execute.
    slot = {}
    return TestContext.from_domain(
        test,
        get_dependency=_phase_get_dependency(test, slot),
        build_phase_runtime_handler=build_phase_runtime,
        phase_runtime_slot=slot,
        **coordinates,
    )

# ** function: run_one_test
def _run_one_test(test_key: str, test_mapping: Any, coordinates: Dict[str, Any]) -> Any:
    '''
    Build and run one test. A model defect and a failed run stay distinct.

    :param test_key: The grammar key.
    :type test_key: str
    :param test_mapping: The phase document.
    :type test_mapping: Any
    :param coordinates: Phase-runtime coordinates.
    :type coordinates: Dict[str, Any]
    :return: The caught error, or None when the run returned.
    :rtype: Any
    '''

    # An illegal test mapping raises before that test is printed PASSED.
    try:
        test_ctx = _build_module_test(test_key, test_mapping, coordinates)
    except ModelError as error:
        return error, None

    # Pass means execute_feature returned. Fail means the run raised.
    session = None
    try:
        session = build_test_session(test_context=test_ctx)
        test_ctx.execute_feature(session)
    except ModelError as error:
        return error, session
    except TiferetError as error:
        return error, session
    return None, session

# ** function: registered_check
def _registered_check():
    '''Resolve Check from registration data. Do not import the util.'''

    # The same string shape as a default service dependency.
    registration = {
        'module_path': 'tiferet.utils.check',
        'class_name': 'Check',
    }
    module = import_module(registration['module_path'])
    return getattr(module, registration['class_name'])()

# ** function: unused_dependency
def _unused_dependency(*args, **kwargs):
    '''Fail if the reporter asks the tester cache for an event.'''

    # The seeded error catalog is a cache hit. This is not get_error_evt.
    raise RuntimeError('The reporter cache must not resolve get_error_evt.')

# ** function: reporter_cache
@add_default_errors(a.error.CORE_DEFAULT_ERRORS)
def _reporter_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''Seed the reporter cache with the core error catalog.'''

    # Do not add this decorator to build_cache.
    return CacheContext(cache=cache)

# ** function: module_run_session
def _module_run_session() -> ModuleRunContext:
    '''Construct the session that pools one module run.'''

    # The handler is a cache hit. It is not AppSessionContext.run.
    cache = _reporter_cache()
    return ModuleRunContext(
        get_dependency=_unused_dependency,
        cache=cache,
        raise_error_handler=core.raise_error_handler(
            core.get_error(cache, _unused_dependency),
        ),
    )

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
    return BaseContext.from_domain(
        value,
        session=session,
        check=_registered_check(),
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
        tester_ctx: TesterContext = None,
        *,
        test_context: TestContext = None,
        **request_fields: Any,
    ) -> TestSessionContext:
    '''
    Construct a test session bound to one collaborator.

    The positional form stays. ``@use_tester`` keeps calling it. The module
    run passes keyword-only ``test_context`` and does not pass a
    ``TesterContext``.

    :param tester_ctx: The bound variant tester context.
    :type tester_ctx: TesterContext
    :param test_context: The bound test context for a YAML module run.
    :type test_context: TestContext
    :param request_fields: Optional RequestContext initialization fields.
    :type request_fields: dict
    :return: A new test session for one test request.
    :rtype: TestSessionContext
    '''

    # One collaborator. Passing both, or neither, is a construction error.
    if (tester_ctx is None) == (test_context is None):
        raise ValueError(
            'Pass tester_ctx or test_context, not both and not neither.',
        )

    # Construct the session directly. Do not store a TestContext in tester_ctx.
    return TestSessionContext(
        tester_ctx,
        test_context=test_context,
        **request_fields,
    )

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

# ** blueprint: run_test_module
def run_test_module(module_path: str, summary: bool = False) -> Dict[str, Any]:
    '''
    Run one test module and print pytest-shaped lines plus a count.

    The argument is the filesystem path of a Python test module. The Python
    file is read only to prove it exists and to derive the YAML counterpart.
    It is not imported and it is not executed. ``summary=True`` prints only
    the count line. It is the same run, not a second runner. The return is
    the report the session pooled.

    :param module_path: The Python test module path, relative or absolute.
    :type module_path: str
    :param summary: When true, print only the count line.
    :type summary: bool
    :return: The session report, with outcomes and failures.
    :rtype: Dict[str, Any]
    '''

    # Refuse a bad path before any YAML load or test line.
    path = Path(module_path)
    _refuse_python_module(path)
    path.read_bytes()
    relative, yaml_path = _yaml_counterpart(path)
    document = _load_test_document(yaml_path)

    # The session pools. This function still walks the document.
    session = _module_run_session()
    node_root = f'tiferet_tests/{relative}.yml'
    passed = 0
    failed = 0
    for node_id, test_key, test_mapping, coordinates in _iter_document_tests(
        document,
        node_root,
    ):
        error, test_session = _run_one_test(test_key, test_mapping, coordinates)
        printable = session.note(node_id, error, test_session)
        if printable is None:
            passed += 1
            if not summary:
                print(f'{node_id} PASSED')
            continue

        # One failure does not abort the module and does not change the lines.
        failed += 1
        if not summary:
            print(f'{node_id} FAILED')
            print(printable)

    # The count is the same run. Printing changes. Execution does not.
    print(_count_line(passed, failed))
    return session.report()
