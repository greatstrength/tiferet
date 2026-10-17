"""Tiferet Tester Blueprints"""

# *** imports

# ** core
import builtins
import copy
import functools
import inspect
import os
import tempfile
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Dict, List

# ** app
from .. import assets as a
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
from ..contexts.tester_phase import (
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
    ModelError,
    ModuleRunContext,
    RepoTesterContext,
    ServiceEventTesterContext,
    TesterContext,
    TesterObject,
    TestSessionContext,
    TransferObjectTesterContext,
    add_default_testers,
)
from ..contexts.tester_module import TestModuleContext
from ..events import DomainEvent
from ..events.tester_module import (
    AddFixture,
    AddTest,
    AddTester,
    AttachTest,
    DetachTest,
    GetFixture,
    GetTest,
    GetTester,
    ListFixtures,
    ListTests,
    ListTesters,
    ReadTestModuleDocument,
    RemoveFixture,
    RemoveTest,
    RemoveTester,
    UpdateFixture,
    UpdateTest,
    UpdateTester,
    WriteTestModuleDocument,
)
from ..mappers.tester_phase import TestConfigObject
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

    Duck-types fixture objects without importing pytest.

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

# ** function: read_test_module_text
def _read_test_module_text(path: str) -> str:
    '''
    A missing file returns null and is not created.

    :param path: The filesystem path to read.
    :type path: str
    :return: The utf-8 text, or null when the file is missing.
    :rtype: str
    '''

    # A missing file returns null and is not created.
    if not os.path.isfile(path):
        return None

    # Read the bytes. An OS error names the load failure.
    try:
        with open(path, 'rb') as handle:
            raw = handle.read()
    except OSError as error:
        raise TiferetError(
            TEST_MODULE_LOAD_FAILED_ID,
            'Failed to read the test module',
        ) from error

    # Bytes that are not utf-8 raise the same code.
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError as error:
        raise TiferetError(
            TEST_MODULE_LOAD_FAILED_ID,
            'The test module text is not utf-8.',
        ) from error

# ** function: created_parent_directories
def _created_parent_directories(parent: Path) -> List[Path]:
    '''
    Create missing parents. Return the directories this call created.

    :param parent: The directory to ensure.
    :type parent: Path
    :return: The directories this call created, parents before children.
    :rtype: List[Path]
    '''

    # Collect missing parents from the leaf toward an existing ancestor.
    missing = []
    current = parent
    while not current.exists():
        missing.append(current)
        if current == current.parent:
            break
        current = current.parent

    # Create them root-first and keep only the directories this call made.
    created = []
    try:
        for directory in reversed(missing):
            directory.mkdir()
            created.append(directory)
    except OSError:
        for directory in reversed(created):
            try:
                directory.rmdir()
            except OSError:
                break
        raise

    # Return the created directories.
    return created

# ** function: replace_test_module
def _replace_test_module(path: Path, text: str, *, create: bool) -> None:
    '''
    Write a sibling temp file, then replace the module path.

    :param path: The destination path.
    :type path: Path
    :param text: The document text.
    :type text: str
    :param create: Whether to create missing parents first.
    :type create: bool
    :return: None
    :rtype: None
    '''

    # Create missing parents only when asked.
    created = []
    temp_path = None
    if create:
        created = _created_parent_directories(path.parent)

    # Write a sibling temp file, then replace. Clean up only this call's work.
    try:
        handle = tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            newline='\n',
            prefix='.test-module-',
            suffix='.yml',
            dir=str(path.parent),
            delete=False,
        )
        temp_path = Path(handle.name)
        with handle:
            handle.write(text)
        os.replace(temp_path, path)
    except Exception:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
        for directory in reversed(created):
            try:
                directory.rmdir()
            except OSError:
                break
        raise

# ** function: delegate_test_module
def _delegate_test_module(
        rel: str,
        base_dir: str,
        event_cls,
        *,
        write: bool,
        **kwargs,
    ) -> Any:
    '''
    Resolve the address, handle one verb, and replace only after a write verb.

    :param rel: The test-module stem.
    :type rel: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param event_cls: The verb event class.
    :type event_cls: type
    :param write: Whether to replace the document after the verb.
    :type write: bool
    :param kwargs: Verb keyword arguments.
    :type kwargs: dict
    :return: The verb result when write is false, otherwise null.
    :rtype: Any
    '''

    # Resolve the address. Do not import domain.
    address = TestModuleContext._address(rel, base_dir)

    # Read the text. A missing file is null and is not created here.
    raw = _read_test_module_text(address.path)

    # Load the document from the read text.
    document = DomainEvent.handle(
        ReadTestModuleDocument,
        address=address,
        text=raw,
    )

    # Bind the working graph and handle the verb.
    context = TestModuleContext.bind(document)
    result = DomainEvent.handle(
        event_cls,
        document=document,
        working=context.working,
        **kwargs,
    )

    # A false write returns the verb result and does not replace.
    if not write:
        return result

    # A verb failure does not reach the replace. Serialize, then replace.
    written = DomainEvent.handle(
        WriteTestModuleDocument,
        document=document,
        working=context.working,
    )
    _replace_test_module(
        Path(address.path),
        written.text,
        create=raw is None,
    )

    # A mutation returns null.
    return None

# ** function: copy_tree
def _copy_tree(value: Any) -> Any:
    '''
    Copy a loaded mapping so two tests do not share one object.

    :param value: The value to copy.
    :type value: Any
    :return: A deep copy of the value.
    :rtype: Any
    '''

    # Two tests do not share one loaded mapping.
    return copy.deepcopy(value)

# ** function: phase_get_dependency
def _phase_get_dependency(test: Any, slot: Dict[str, Any]) -> Callable:
    '''
    Return a get_dependency callable. It is not the app resolver and not a feature catalog.

    :param test: The bound test.
    :type test: Any
    :param slot: The empty slot the runtime callable closes over.
    :type slot: Dict[str, Any]
    :return: A get_dependency callable.
    :rtype: Callable
    '''

    # Register handlers by dialect name, not by service id.
    handlers = register_phase_handlers()
    queues = {
        PHASE_CONDITIONS_ID: ('conditions', [test.conditions]),
        PHASE_EXECUTE_ID: ('execute', list(test.executes)),
        PHASE_ASSERT_ID: ('assert', list(test.asserts)),
    }

    # Each resolution advances that queue once, in document order, and ignores flags.
    def get_dependency(service_id, *flags):
        kind, items = queues[service_id]
        item = items.pop(0)

        # The returned object's execute reads the slot and calls the handler.
        def execute(**kwargs):
            runtime = slot['runtime']
            handlers[kind](runtime, item)
            data_key = getattr(item, 'data_key', None)
            if data_key:
                return runtime.session.data[data_key]
            return None

        return SimpleNamespace(execute=execute)

    # Return the callable. Flags are accepted and ignored.
    return get_dependency

# ** function: count_line
def _count_line(passed: int, failed: int) -> str:
    '''
    Format the count line. No skipped count.

    :param passed: The number of passed tests.
    :type passed: int
    :param failed: The number of failed tests.
    :type failed: int
    :return: The count line.
    :rtype: str
    '''

    # Both counts name failed first. Failed only omits the pass count.
    if failed and passed:
        return f'{failed} failed, {passed} passed'
    if failed:
        return f'{failed} failed'

    # Otherwise name the pass count, including zero.
    return f'{passed} passed'

# ** function: refuse_python_module
def _refuse_python_module(path: Path) -> None:
    '''
    Refuse before any document load.

    :param path: The Python test module path.
    :type path: Path
    :return: None
    :rtype: None
    '''

    # A path that is not a file is missing.
    if not path.is_file():
        raise ValueError('Python test module not found')

    # The suffix and the test_ prefix name a Python test module.
    name = path.name
    if path.suffix != '.py' or not name.startswith('test_'):
        raise ValueError('Not a Python test module')

    # conftest and package init are not test modules.
    if name in ('conftest.py', '__init__.py'):
        raise ValueError('Not a Python test module')

    # The path must sit under tests and must not sit under tests_int.
    parts = path.parts
    if 'tests_int' in parts or 'tests' not in parts:
        raise ValueError('Not a tests/ module')

# ** function: yaml_counterpart
def _yaml_counterpart(path: Path) -> tuple:
    '''
    Return the stem under the last tests part and the parent of that directory.

    :param path: The Python test module path.
    :type path: Path
    :return: The relative stem and the base directory.
    :rtype: tuple
    '''

    # Use the last tests part. Do not build a second document path.
    parts = path.parts
    index = max(
        position
        for position, part in enumerate(parts)
        if part == 'tests'
    )
    rel = Path(*parts[index + 1:]).with_suffix('').as_posix()
    parent = parts[:index]
    base_dir = str(Path(*parent)) if parent else '.'

    # Return the stem and the parent of that tests directory.
    return rel, base_dir

# ** function: iter_document_tests
def _iter_document_tests(document: Dict[str, Any], node_root: str):
    '''
    Yield root tests, then each tester's contained tests, in document order.

    :param document: The plain test-module mapping.
    :type document: Dict[str, Any]
    :param node_root: The node-id prefix.
    :type node_root: str
    :return: Yields node id, test key, test mapping, and coordinates.
    :rtype: tuple
    '''

    # A non-mapping fixtures value is refused. An absent key is empty.
    if 'fixtures' in document and not isinstance(document['fixtures'], dict):
        raise ValueError('fixtures must be a mapping.')
    fixtures = document.get('fixtures') or {}

    # Root tests come first. A tester is not a test. A fixture is not a test.
    tests = document.get('tests') or {}
    if not isinstance(tests, dict):
        raise ValueError('tests must be a mapping.')
    for test_key, test_mapping in tests.items():
        yield (
            f'{node_root}::{test_key}',
            test_key,
            test_mapping,
            {
                'tester_module_path': '',
                'tester_class_name': '',
                'tester_attributes': {},
                'root_fixtures': _copy_tree(fixtures),
                'tester_fixtures': {},
            },
        )

    # Contained tests follow, one tester at a time, in document order.
    testers = document.get('testers') or {}
    if not isinstance(testers, dict):
        raise ValueError('Tester must be a mapping.')
    for tester_key, tester in testers.items():
        if not isinstance(tester, dict):
            raise ValueError(f'Tester {tester_key} must be a mapping.')
        if 'tests' in tester and not isinstance(tester['tests'], dict):
            raise ValueError('tests must be a mapping.')
        contained = tester.get('tests') or {}
        for test_key, test_mapping in contained.items():
            yield (
                f'{node_root}::{tester_key}::{test_key}',
                test_key,
                test_mapping,
                {
                    'tester_module_path': tester.get('module_path') or '',
                    'tester_class_name': tester.get('class_name') or '',
                    'tester_attributes': tester.get('attributes') or {},
                    'root_fixtures': _copy_tree(fixtures),
                    'tester_fixtures': _copy_tree(tester.get('fixtures') or {}),
                },
            )

# ** function: build_module_test
def _build_module_test(
        test_key: str,
        test_mapping: Any,
        coordinates: Dict[str, Any],
    ) -> TestContext:
    '''
    Build one Test through TestConfigObject and bind a TestContext.

    :param test_key: The test name.
    :type test_key: str
    :param test_mapping: The test body.
    :type test_mapping: Any
    :param coordinates: Tester and fixture coordinates.
    :type coordinates: Dict[str, Any]
    :return: The bound test context.
    :rtype: TestContext
    '''

    # Accept a mapping only when its key set is exactly the three phase keys.
    if (
        not isinstance(test_mapping, dict)
        or set(test_mapping) != {'conditions', 'execute', 'assert'}
    ):
        raise ValueError(
            'A test body must name conditions, execute, and assert.'
        )

    # Validate a copy, then map identity onto the noun.
    config = TestConfigObject.model_validate(_copy_tree(test_mapping))
    test = config.map(id=f'test.{test_key}', name=test_key)

    # Compile the phase steps. Do not construct the runtime by hand.
    test.steps = compile_phase_steps(test)
    slot = {}
    return TestContext.from_domain(
        test,
        get_dependency=_phase_get_dependency(test, slot),
        build_phase_runtime_handler=build_phase_runtime,
        phase_runtime_slot=slot,
        **coordinates,
    )

# ** function: run_one_test
def _run_one_test(
        test_key: str,
        test_mapping: Any,
        coordinates: Dict[str, Any],
    ) -> tuple:
    '''
    Return the error and session for one test. A pass is a null error.

    :param test_key: The test name.
    :type test_key: str
    :param test_mapping: The test body.
    :type test_mapping: Any
    :param coordinates: Tester and fixture coordinates.
    :type coordinates: Dict[str, Any]
    :return: The error and session. A pass is a null error.
    :rtype: tuple
    '''

    # A model error from the build returns the error and a null session.
    try:
        test_ctx = _build_module_test(test_key, test_mapping, coordinates)
    except ModelError as error:
        return error, None

    # Build the session with keyword-only test_context and no tester context.
    session = build_test_session(test_context=test_ctx)
    try:
        test_ctx.execute_feature(session)
    except ModelError as error:
        return error, session
    except TiferetError as error:
        return error, session

    # A returned run is a pass. Any other exception propagates.
    return None, session

# ** function: registered_check
def _registered_check() -> Any:
    '''
    Resolve Check from its module and class strings, then call it with no arguments.

    :return: The constructed check.
    :rtype: Any
    '''

    # Do not import the util at module level.
    module = import_module('tiferet.utils.tester_check')
    check_cls = getattr(module, 'Check')

    # Call the resolved class with no arguments.
    return check_cls()

# ** function: reporter_cache
@add_default_errors(a.error.CORE_DEFAULT_ERRORS)
def _reporter_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''
    Decorated only with the error catalog. Return a cache context.

    :param cache: An optional initial cache dictionary.
    :type cache: Dict[str, Any]
    :return: The reporter cache.
    :rtype: CacheContext
    '''

    # Do not move this decorator onto build_cache.
    return CacheContext(cache=cache)

# ** function: module_run_session
def _module_run_session() -> ModuleRunContext:
    '''
    Build one module-run session from the reporter cache.

    :return: The module-run session.
    :rtype: ModuleRunContext
    '''

    # The reporter cache must not resolve get_error_evt.
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
@add_default_app_constants({
    a.app.DI_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
    a.app.FEATURE_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
})
@add_default_app_services({
    a.app.DI_SERVICE_ID: a.app.DI_SERVICE_DATA,
    a.app.FEATURE_SERVICE_ID: a.app.FEATURE_SERVICE_DATA,
    a.app.GET_FEATURE_EVT_ID: a.app.GET_FEATURE_EVT_DATA,
})
def build_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''
    Build the tester-dialect cache without standard app catalogs.

    :param cache: An optional initial cache dictionary for the root namespace.
    :type cache: Dict[str, Any]
    :return: The tester-dialect cache.
    :rtype: CacheContext
    '''

    # Delegate to the core cache builder. Do not seed the error catalog here.
    return core.build_cache(cache)

# ** blueprint: unused_dependency
def _unused_dependency(*args, **kwargs) -> None:
    '''
    Raises RuntimeError whose message names get_error_evt. The reporter cache must not resolve that event.

    :param args: Ignored positional arguments.
    :type args: tuple
    :param kwargs: Ignored keyword arguments.
    :type kwargs: dict
    :return: This function always raises and does not return.
    :rtype: None
    '''

    # The reporter cache must not resolve that event.
    raise RuntimeError('get_error_evt')

# ** blueprint: register_phase_handlers
def register_phase_handlers() -> Dict[str, Callable]:
    '''
    Returns the mapping conditions to PhaseRuntimeContext.handle_conditions, execute to PhaseRuntimeContext.handle_execution, assert to PhaseRuntimeContext.handle_assertion. These handlers do not decorate build_cache and are not a feature catalog.

    :return: The phase handler mapping.
    :rtype: Dict[str, Callable]
    '''

    # These handlers do not decorate build_cache and are not a feature catalog.
    return {
        'conditions': PhaseRuntimeContext.handle_conditions,
        'execute': PhaseRuntimeContext.handle_execution,
        'assert': PhaseRuntimeContext.handle_assertion,
    }

# ** blueprint: build_phase_runtime
def build_phase_runtime(
        session,
        tester_module_path: str,
        tester_class_name: str,
        tester_attributes: Dict[str, Any] = None,
        root_fixtures: Dict[str, Dict[str, Any]] = None,
        tester_fixtures: Dict[str, Dict[str, Any]] = None,
    ):
    '''
    Build a PhaseRuntime with those fields, empty mappings when null.

    :param session: The test session.
    :type session: Any
    :param tester_module_path: The tester class module path.
    :type tester_module_path: str
    :param tester_class_name: The tester class name.
    :type tester_class_name: str
    :param tester_attributes: Attributes new passes to the tester class.
    :type tester_attributes: Dict[str, Any]
    :param root_fixtures: Root fixture specs.
    :type root_fixtures: Dict[str, Dict[str, Any]]
    :param tester_fixtures: Tester-local fixture specs.
    :type tester_fixtures: Dict[str, Dict[str, Any]]
    :return: The phase runtime context.
    :rtype: PhaseRuntimeContext
    '''

    # Build the domain value. Empty mappings stand in for null.
    value = PhaseRuntime(
        tester_module_path=tester_module_path,
        tester_class_name=tester_class_name,
        tester_attributes=tester_attributes if tester_attributes is not None else {},
        root_fixtures=root_fixtures if root_fixtures is not None else {},
        tester_fixtures=tester_fixtures if tester_fixtures is not None else {},
    )

    # Resolve the context. Do not construct it by hand and do not return the domain value.
    return BaseContext.from_domain(
        value,
        session=session,
        check=_registered_check(),
    )

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
        'repo': RepoTesterContext,
        'context': ContextTesterContext,
    }[tester.type]

    # Bind the tester and inject the phase-runtime factory.
    return context_cls.from_domain(
        tester,
        build_phase_runtime_handler=build_phase_runtime,
    )

# ** blueprint: build_test_session
def build_test_session(
        tester_ctx: TesterContext = None,
        *,
        test_context: TestContext = None,
        **request_fields,
    ) -> TestSessionContext:
    '''
    Pass tester_ctx or test_context, not both and not neither.

    :param tester_ctx: The bound tester context.
    :type tester_ctx: TesterContext
    :param test_context: The bound test context. Keyword-only.
    :type test_context: TestContext
    :param request_fields: RequestContext fields such as session_id and data.
    :type request_fields: dict
    :return: The test session.
    :rtype: TestSessionContext
    '''

    # Refuse both collaborators and neither before construction.
    if (tester_ctx is None) == (test_context is None):
        raise ValueError(
            'Pass tester_ctx or test_context, not both and not neither.'
        )

    # Construct the session. Do not store a TestContext in tester_ctx.
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
    domain_cls = fields.pop('domain_cls', None)

    # Fill import coordinates from target_cls when those fields are unset.
    if target_cls is not None:
        if not module_path:
            module_path = target_cls.__module__
        if not class_name:
            class_name = target_cls.__name__

    # Fill aggregate import coordinates from aggregate_cls when unset.
    if aggregate_cls is not None:
        fields.setdefault('aggregate_module_path', aggregate_cls.__module__)
        fields.setdefault('aggregate_class_name', aggregate_cls.__name__)

    # Fill domain import coordinates from domain_cls when unset.
    if domain_cls is not None:
        fields.setdefault('domain_module_path', domain_cls.__module__)
        fields.setdefault('domain_class_name', domain_cls.__name__)

    # Derive the tester id from type and class_name when omitted.
    tester_id = id or f'{type}.{class_name}'

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
        if isinstance(obj, builtins.type):
            for name, member in list(obj.__dict__.items()):
                if name.startswith('__'):
                    continue
                setattr(obj, name, _wrap_member(member, test_ctx))
            return obj

        # Wrap a single function.
        return _inject_test_session(obj, test_ctx)

    # Return the decorator.
    return decorator

# ** blueprint: add_fixture
def add_fixture(
        rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
        payload: Any = None,
        fragment: str = None,
        alias: str = None,
        anchor: str = None,
        merge: str = None,
    ) -> None:
    '''
    Add one fixture and leave the payload opaque.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The fixture name.
    :type name: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: The optional tester that contains the fixture.
    :type tester: str
    :param payload: The plain payload, or null.
    :type payload: Any
    :param fragment: The YAML fragment, or null.
    :type fragment: str
    :param alias: The alias name, or null.
    :type alias: str
    :param anchor: The anchor to record, or null.
    :type anchor: str
    :param merge: The merge anchor, or null.
    :type merge: str
    :return: None
    :rtype: None
    '''

    # Delegate the add. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        AddFixture,
        write=True,
        name=name,
        tester=tester,
        payload=payload,
        fragment=fragment,
        alias=alias,
        anchor=anchor,
        merge=merge,
    )

# ** blueprint: get_fixture
def get_fixture(
        rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
    ) -> Any:
    '''
    Read one fixture and do not replace.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The fixture name.
    :type name: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: The optional tester that contains the fixture.
    :type tester: str
    :return: The fixture projection.
    :rtype: Any
    '''

    # Delegate the read. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        GetFixture,
        write=False,
        name=name,
        tester=tester,
    )

# ** blueprint: list_fixtures
def list_fixtures(
        rel: str,
        *,
        base_dir: str = '.',
        tester: str = None,
    ) -> Any:
    '''
    List fixture names in document order.

    :param rel: The test-module stem.
    :type rel: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: The optional tester that contains the fixtures.
    :type tester: str
    :return: The fixture names in document order.
    :rtype: Any
    '''

    # Delegate the list. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        ListFixtures,
        write=False,
        tester=tester,
    )

# ** blueprint: update_fixture
def update_fixture(
        rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
        payload: Any = None,
        fragment: str = None,
        merge: str = None,
    ) -> None:
    '''
    Patch one fixture and leave the node object.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The fixture name.
    :type name: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: The optional tester that contains the fixture.
    :type tester: str
    :param payload: The plain payload, or null.
    :type payload: Any
    :param fragment: The YAML fragment, or null.
    :type fragment: str
    :param merge: The merge anchor, or null.
    :type merge: str
    :return: None
    :rtype: None
    '''

    # Delegate the patch. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        UpdateFixture,
        write=True,
        name=name,
        tester=tester,
        payload=payload,
        fragment=fragment,
        merge=merge,
    )

# ** blueprint: remove_fixture
def remove_fixture(
        rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
    ) -> None:
    '''
    Remove one fixture pair, and a missing name does not write.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The fixture name.
    :type name: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: The optional tester that contains the fixture.
    :type tester: str
    :return: None
    :rtype: None
    '''

    # Delegate the remove. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        RemoveFixture,
        write=True,
        name=name,
        tester=tester,
    )

# ** blueprint: add_test
def add_test(
        rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
        payload: Any = None,
        fragment: str = None,
        anchor: str = None,
    ) -> None:
    '''
    Add one test body, which is not attach.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The test name.
    :type name: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: The optional tester that contains the test.
    :type tester: str
    :param payload: The plain payload, or null.
    :type payload: Any
    :param fragment: The YAML fragment, or null.
    :type fragment: str
    :param anchor: The anchor to record, or null.
    :type anchor: str
    :return: None
    :rtype: None
    '''

    # Delegate the add. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        AddTest,
        write=True,
        name=name,
        tester=tester,
        payload=payload,
        fragment=fragment,
        anchor=anchor,
    )

# ** blueprint: get_test
def get_test(
        rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
    ) -> Any:
    '''
    Read one test and do not replace.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The test name.
    :type name: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: The optional tester that contains the test.
    :type tester: str
    :return: The test projection.
    :rtype: Any
    '''

    # Delegate the read. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        GetTest,
        write=False,
        name=name,
        tester=tester,
    )

# ** blueprint: list_tests
def list_tests(
        rel: str,
        *,
        base_dir: str = '.',
        tester: str = None,
    ) -> Any:
    '''
    List test names in document order.

    :param rel: The test-module stem.
    :type rel: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: The optional tester that contains the tests.
    :type tester: str
    :return: The test names in document order.
    :rtype: Any
    '''

    # Delegate the list. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        ListTests,
        write=False,
        tester=tester,
    )

# ** blueprint: update_test
def update_test(
        rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
        payload: Any = None,
        fragment: str = None,
    ) -> None:
    '''
    Patch one test and do not inspect phase keys.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The test name.
    :type name: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: The optional tester that contains the test.
    :type tester: str
    :param payload: The plain payload, or null.
    :type payload: Any
    :param fragment: The YAML fragment, or null.
    :type fragment: str
    :return: None
    :rtype: None
    '''

    # Delegate the patch. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        UpdateTest,
        write=True,
        name=name,
        tester=tester,
        payload=payload,
        fragment=fragment,
    )

# ** blueprint: remove_test
def remove_test(
        rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
    ) -> None:
    '''
    Remove one test pair.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The test name.
    :type name: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: The optional tester that contains the test.
    :type tester: str
    :return: None
    :rtype: None
    '''

    # Delegate the remove. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        RemoveTest,
        write=True,
        name=name,
        tester=tester,
    )

# ** blueprint: add_tester
def add_tester(
        rel: str,
        name: str,
        *,
        base_dir: str = '.',
        payload: Any = None,
        fragment: str = None,
        anchor: str = None,
    ) -> None:
    '''
    Add one tester mapping.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The tester name.
    :type name: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param payload: The plain payload, or null.
    :type payload: Any
    :param fragment: The YAML fragment, or null.
    :type fragment: str
    :param anchor: The anchor to record, or null.
    :type anchor: str
    :return: None
    :rtype: None
    '''

    # Delegate the add. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        AddTester,
        write=True,
        name=name,
        payload=payload,
        fragment=fragment,
        anchor=anchor,
    )

# ** blueprint: get_tester
def get_tester(
        rel: str,
        name: str,
        *,
        base_dir: str = '.',
    ) -> Any:
    '''
    Read one tester and do not replace.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The tester name.
    :type name: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :return: The tester projection.
    :rtype: Any
    '''

    # Delegate the read. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        GetTester,
        write=False,
        name=name,
    )

# ** blueprint: list_testers
def list_testers(rel: str, *, base_dir: str = '.') -> Any:
    '''
    List tester names in document order.

    :param rel: The test-module stem.
    :type rel: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :return: The tester names in document order.
    :rtype: Any
    '''

    # Delegate the list. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        ListTesters,
        write=False,
    )

# ** blueprint: update_tester
def update_tester(
        rel: str,
        name: str,
        *,
        base_dir: str = '.',
        payload: Any = None,
        fragment: str = None,
    ) -> None:
    '''
    Patch one tester, and fixtures and tests are refused.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The tester name.
    :type name: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param payload: The plain payload, or null.
    :type payload: Any
    :param fragment: The YAML fragment, or null.
    :type fragment: str
    :return: None
    :rtype: None
    '''

    # Delegate the patch. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        UpdateTester,
        write=True,
        name=name,
        payload=payload,
        fragment=fragment,
    )

# ** blueprint: remove_tester
def remove_tester(rel: str, name: str, *, base_dir: str = '.') -> None:
    '''
    Remove one tester pair.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The tester name.
    :type name: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :return: None
    :rtype: None
    '''

    # Delegate the remove. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        RemoveTester,
        write=True,
        name=name,
    )

# ** blueprint: attach_test
def attach_test(
        rel: str,
        tester: str,
        name: str,
        *,
        base_dir: str = '.',
    ) -> None:
    '''
    Contain a root test by node identity and do not copy the body.

    :param rel: The test-module stem.
    :type rel: str
    :param tester: The tester name.
    :type tester: str
    :param name: The root test name.
    :type name: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :return: None
    :rtype: None
    '''

    # Delegate the attach. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        AttachTest,
        write=True,
        tester=tester,
        name=name,
    )

# ** blueprint: detach_test
def detach_test(
        rel: str,
        tester: str,
        name: str,
        *,
        base_dir: str = '.',
    ) -> None:
    '''
    Drop one containment and leave the root test and its anchor.

    :param rel: The test-module stem.
    :type rel: str
    :param tester: The tester name.
    :type tester: str
    :param name: The contained test name.
    :type name: str
    :param base_dir: The directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :return: None
    :rtype: None
    '''

    # Delegate the detach. The writer does not replace the file.
    return _delegate_test_module(
        rel,
        base_dir,
        DetachTest,
        write=True,
        tester=tester,
        name=name,
    )

# ** blueprint: run_test_module
def run_test_module(module_path: str, summary: bool = False) -> Dict[str, Any]:
    '''
    Run one Python test module from its counterpart and print the count line.

    :param module_path: The filesystem path of a Python test module.
    :type module_path: str
    :param summary: Whether to print only the count line.
    :type summary: bool
    :return: The module-run report.
    :rtype: Dict[str, Any]
    '''

    # Refuse before any line is printed.
    path = Path(module_path)
    _refuse_python_module(path)

    # Read the Python bytes. Do not decode them into a test.
    path.read_bytes()

    # Derive the counterpart and load it. A missing counterpart propagates.
    rel, base_dir = _yaml_counterpart(path)
    address = TestModuleContext._address(rel, base_dir)
    document = DomainEvent.handle(
        ReadTestModuleDocument,
        address=address,
        text=_read_test_module_text(address.path),
        required=True,
    )

    # A non-mapping, or an illegal root key, raises before any test line.
    mapping = document.mapping
    if not isinstance(mapping, dict):
        raise ValueError('A test module document must be a mapping.')
    for key in mapping:
        if key not in ('fixtures', 'tests', 'testers'):
            raise ValueError(f'Illegal test-module root: {key}')

    # Run each yielded test. One failure does not abort the module.
    session = _module_run_session()
    node_root = f'tiferet_tests/{rel}.yml'
    passed = 0
    failed = 0
    for node_id, test_key, test_mapping, coordinates in _iter_document_tests(
            mapping,
            node_root,
        ):
        error, test_session = _run_one_test(
            test_key,
            test_mapping,
            coordinates,
        )
        printable = session.note(node_id, error, test_session)
        if printable is None:
            passed += 1
            if not summary:
                print(f'{node_id} PASSED')
        else:
            failed += 1
            if not summary:
                print(f'{node_id} FAILED')
                print(printable)

    # The count line is always printed on a run that reaches it.
    print(_count_line(passed, failed))
    return session.report()
