"""Managed instance-patching feature experiments; no global collaborator patching."""

# *** imports

# ** core
import logging
import tempfile
from copy import deepcopy
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

# ** infra
import pytest
import yaml
from pydantic import ValidationError

# ** app
from tiferet.assets import TiferetError
from tiferet.blueprints.tester import build_phase_runtime, build_test_session, run_test_module, _build_module_test
from tiferet.contexts.request import RequestContext
from tiferet.contexts.tester_phase import PhaseRuntimeContext
from tiferet.domain import ModelError
from tiferet.domain.tester_phase import Execution
from tiferet.interfaces import ServiceError
from tiferet.mappers.tester_phase import ExecutionConfigObject, TestConfigObject
from tiferet.utils.tester_stage import STAGE_PREFIX

# *** constants

# ** constant: module_path
MODULE = 'experiments.tester_efficacy.tests.test_live_patch'

# ** constant: created_consumers
CREATED = []

# *** classes

# ** class: live_driver
class LiveDriver:
    """Represent a real already-created collaborator, distinct per consumer."""

    # * method: operate
    def operate(self, value):
        """Return a real driver result.

        :param value: The value forwarded to the collaborator.
        :type value: Any
        """

        return 'real:' + value

    # * method: dangerous (property)
    @property
    def dangerous(self):
        """Detect accidental invocation of an unsupported descriptor."""

        raise AssertionError('property must not be read while patching')

    # * method: static_method (static)
    @staticmethod
    def static_method():
        """Declare a descriptor outside this instance-only feature."""

        return None

# ** class: live_consumer
class LiveConsumer:
    """Own and call its real driver, wrapping failures with their cause intact."""

    # * init
    def __init__(self):
        """Create distinct live collaborators before any patch is installed."""

        self.driver = LiveDriver()
        self.other = LiveDriver()
        CREATED.append(self)

    # * method: serve
    def serve(self, value):
        """Wrap a real driver OSError, without swallowing or dropping its cause.

        :param value: The value forwarded to the collaborator.
        :type value: Any
        """

        try:
            return self.driver.operate(value)
        except OSError as error:
            ServiceError.raise_for(self, 'LIVE_FAILED', 'live driver failed', cause=error)

    # * method: other_serve
    def other_serve(self, value):
        """Call the unrelated instance to detect accidental global replacement.

        :param value: The value forwarded to the collaborator.
        :type value: Any
        """

        return self.other.operate(value)

    # * method: explode
    def explode(self):
        """Raise an ordinary uncaught execution failure."""

        raise RuntimeError('execution exploded')

    # * method: abort
    def abort(self):
        """Raise a BaseException outside raises:true capture."""

        raise KeyboardInterrupt('execution aborted')

# *** functions

# ** function: case_and_coordinates
def case_and_coordinates():
    """Load fresh experiment data and runtime coordinates."""

    path = Path(__file__).parents[1] / 'tiferet_tests/test_live_patch.yml'
    tester = yaml.safe_load(path.read_text())['testers']['live_consumer']
    return deepcopy(tester['tests']['injected_live_method']), {
        'tester_module_path': tester['module_path'],
        'tester_class_name': tester['class_name'],
    }

# ** function: run_mapping
def run_mapping(mapping, coordinates=None):
    """Run an actual mapped phase test using a fresh runtime.

    :param mapping: The three-phase test mapping.
    :type mapping: Any
    :param coordinates: The tester runtime coordinates.
    :type coordinates: Any
    """

    if coordinates is None:
        _, coordinates = case_and_coordinates()
    runtime = build_phase_runtime(session=RequestContext(), **coordinates)
    test = TestConfigObject.model_validate(mapping).map(id='live.patch', name='live.patch')
    runtime.run(test)
    return runtime

# ** function: assert_restored
def assert_restored(consumer):
    """Check exact descriptor visibility and no instance shadow residue.

    :param consumer: The real consumer whose driver must be restored.
    :type consumer: Any
    """

    assert 'operate' not in vars(consumer.driver)
    assert consumer.driver.operate.__func__ is type(consumer.driver).operate
    assert consumer.driver.operate('after') == 'real:after'
    assert consumer.other.operate('after') == 'real:after'

# *** tests

# ** test: actual_consumer_and_unrelated_instance
def test_actual_consumer_and_unrelated_instance():
    """Prove injected cause reaches the real owner and other instances stay real."""

    mapping, _ = case_and_coordinates()
    runtime = run_mapping(mapping)
    assert isinstance(runtime.session.data['failure'].__cause__, OSError)
    assert str(runtime.session.data['failure'].__cause__) == 'injected'
    assert_restored(runtime.session.data['consumer'])
    assert not runtime._patches._exit_callbacks
    assert runtime.stage is None

# ** test: restoration_on_all_exits
@pytest.mark.parametrize('entry', ['phase', 'feature'])
@pytest.mark.parametrize('exit_kind', ['success', 'assertion', 'execution', 'base_exception', 'partial_setup'])
def test_restoration_on_all_exits(entry, exit_kind):
    """Both phase and compiled-feature entries own restoration on every exit.

    :param entry: The phase or compiled-feature execution entry.
    :type entry: Any
    :param exit_kind: The success or failure scenario.
    :type exit_kind: Any
    """

    mapping, coordinates = case_and_coordinates()
    expected = None
    if exit_kind == 'assertion':
        mapping['assert'][0]['error_code'] = 'WRONG_CODE'
        expected = TiferetError
    elif exit_kind in ('execution', 'base_exception'):
        method = 'explode' if exit_kind == 'execution' else 'abort'
        mapping['execute'].append({'target': '$r.consumer', 'method': method})
        expected = RuntimeError if exit_kind == 'execution' else KeyboardInterrupt
    elif exit_kind == 'partial_setup':
        invalid = deepcopy(mapping['execute'][2])
        invalid['kwargs']['class_name'] = 'str'
        mapping['execute'].insert(3, invalid)
        expected = TiferetError
    module = import_module(MODULE)
    before = len(module.CREATED)
    handlers = list(logging.getLogger().handlers)
    level = logging.getLogger().level
    directories = set(Path(tempfile.gettempdir()).glob(STAGE_PREFIX + '*'))
    if entry == 'phase':
        action = lambda: run_mapping(mapping, coordinates)
    else:
        context = _build_module_test('restoration', mapping, coordinates)
        action = lambda: context.execute_feature(build_test_session(test_context=context))
    if expected:
        with pytest.raises(expected):
            action()
    else:
        action()
    assert len(module.CREATED) == before + 1
    assert_restored(module.CREATED[-1])
    assert list(logging.getLogger().handlers) == handlers
    assert logging.getLogger().level == level
    assert set(Path(tempfile.gettempdir()).glob(STAGE_PREFIX + '*')) == directories

# ** test: nested_shadow_restores_original_value
def test_nested_shadow_restores_original_value():
    """Two injections unwind LIFO and restore a preexisting own value by identity."""

    driver = LiveDriver()
    original = lambda value: 'own:' + value
    driver.operate = original
    runtime = build_phase_runtime(session=RequestContext(), tester_module_path=MODULE, tester_class_name='LiveConsumer')
    runtime.session.data['driver'] = driver
    runtime.as_keys.add('driver')
    for message in ('first', 'second'):
        runtime.handle_execution(Execution(target='$r.driver', method='patch_raises', kwargs={
            'method': 'operate', 'module_path': 'builtins', 'class_name': 'OSError', 'message': message,
        }))
        with pytest.raises(OSError, match=message):
            driver.operate('payload')
    runtime.close_resources()
    assert vars(driver)['operate'] is original
    runtime.close_resources()
    assert driver.operate('after') == 'own:after'

# ** test: invalid_patch_shape
@pytest.mark.parametrize('change', [
    {'target': 'self'}, {'target': '$fixture.driver'}, {'target': '$r.driver.extra'},
    {'args': [1]}, {'raises': True, 'as': 'error'}, {'dependencies': {}},
    {'kwargs': {'method': 'operate', 'module_path': 'bad..module', 'class_name': 'OSError'}},
    {'kwargs': {'method': 'operate', 'module_path': 'builtins', 'class_name': 'OSError', 'message': lambda: None}},
    {'kwargs': {}}, {'kwargs': {'method': '__call__', 'module_path': 'builtins', 'class_name': 'OSError'}},
    {'kwargs': {'method': 'operate', 'module_path': 'builtins', 'class_name': 'OSError', 'callback': 'no'}},
    {'kwargs': {'method': 'operate', 'module_path': 'builtins', 'class_name': 'OSError', 'message': []}},
])
def test_invalid_patch_shape(change):
    """Reject malformed syntax before a runtime can mutate any collaborator.

    :param change: The invalid execute-item override.
    :type change: Any
    """

    item = {'target': '$r.driver', 'method': 'patch_raises', 'kwargs': {
        'method': 'operate', 'module_path': 'builtins', 'class_name': 'OSError',
    }}
    item.update(change)
    with pytest.raises((ModelError, ValidationError)):
        ExecutionConfigObject.model_validate(item)

# ** test: unsafe_runtime_target_rejected
@pytest.mark.parametrize('target,method', [
    (LiveDriver, 'operate'), (SimpleNamespace(), 'operate'), (42, 'operate'),
    (LiveDriver(), 'missing'), (LiveDriver(), 'dangerous'), (LiveDriver(), 'static_method'),
])
def test_unsafe_runtime_target_rejected(target, method):
    """Reject classes, unsupported descriptors and targets without touching classes.

    :param target: The unsupported runtime target.
    :type target: Any
    :param method: The live method name under test.
    :type method: Any
    """

    runtime = build_phase_runtime(session=RequestContext(), tester_module_path=MODULE, tester_class_name='LiveConsumer')
    runtime.session.data['driver'] = target
    runtime.as_keys.add('driver')
    with pytest.raises(TiferetError):
        runtime.handle_execution(Execution(target='$r.driver', method='patch_raises', kwargs={
            'method': method, 'module_path': 'builtins', 'class_name': 'OSError',
        }))
    runtime.close_resources()

# ** test: invalid_exception_rejected_without_mutation
@pytest.mark.parametrize('module_path,class_name', [('builtins', 'str'), ('builtins', 'KeyboardInterrupt'), ('missing_module_for_patch', 'Error')])
def test_invalid_exception_rejected_without_mutation(module_path, class_name):
    """Exception resolution must complete before shadowing the live method.

    :param module_path: The exception module name.
    :type module_path: Any
    :param class_name: The exception class name.
    :type class_name: Any
    """

    driver = LiveDriver()
    runtime = build_phase_runtime(session=RequestContext(), tester_module_path=MODULE, tester_class_name='LiveConsumer')
    runtime.session.data['driver'] = driver
    runtime.as_keys.add('driver')
    with pytest.raises(TiferetError):
        runtime.handle_execution(Execution(target='$r.driver', method='patch_raises', kwargs={
            'method': 'operate', 'module_path': module_path, 'class_name': class_name,
        }))
    assert 'operate' not in vars(driver)
    runtime.close_resources()

# ** test: disconnected_mutant_detected
def test_disconnected_mutant_detected(monkeypatch):
    """Patching a spare object instead of the live owner must fail the gate.

    :param monkeypatch: The reversible pytest patch facility.
    :type monkeypatch: Any
    """

    original = PhaseRuntimeContext._patch_instance_failure
    def disconnected(self, execution):
        target = self.session.data['driver']
        self.session.data['driver'] = import_module(MODULE).LiveDriver()
        try:
            return original(self, execution)
        finally:
            self.session.data['driver'] = target
    monkeypatch.setattr(PhaseRuntimeContext, '_patch_instance_failure', disconnected)
    mapping, _ = case_and_coordinates()
    with pytest.raises(TiferetError) as caught:
        run_mapping(mapping)
    assert caught.value.error_code == 'PHASE_STEP_FAILED'

# ** test: swallowed_exception_mutant_detected
def test_swallowed_exception_mutant_detected(monkeypatch):
    """A consumer swallowing the injected driver error must fail raises:true.

    :param monkeypatch: The reversible pytest patch facility.
    :type monkeypatch: Any
    """

    def swallow(self, value):
        try:
            return self.driver.operate(value)
        except OSError:
            return None
    monkeypatch.setattr(import_module(MODULE).LiveConsumer, 'serve', swallow)
    mapping, _ = case_and_coordinates()
    with pytest.raises(TiferetError) as caught:
        run_mapping(mapping)
    assert caught.value.error_code == 'PHASE_STEP_FAILED'

# ** test: yaml_entry_restores_live_instances
def test_yaml_entry_restores_live_instances():
    """The public module runner also restores its privately constructed instance."""

    module = import_module(MODULE)
    before = len(module.CREATED)
    report = run_test_module(str(Path(__file__)))
    assert not report['failures']
    for consumer in module.CREATED[before:]:
        assert_restored(consumer)

# ** test: cleanup_failure_does_not_leak_other_resources
@pytest.mark.parametrize('already_failed', [False, True])
def test_cleanup_failure_does_not_leak_other_resources(already_failed):
    """Continue all restorations and stage cleanup without masking prior errors.

    :param already_failed: Whether to preserve an active test failure.
    :type already_failed: Any
    """

    runtime = build_phase_runtime(session=RequestContext(), tester_module_path=MODULE, tester_class_name='LiveConsumer')
    events = []
    runtime._patches.callback(lambda: events.append('earlier'))
    def fail_cleanup():
        events.append('failure')
        raise OSError('cleanup failed')
    runtime._patches.callback(fail_cleanup)
    runtime.stage = SimpleNamespace(close=lambda: events.append('stage'))
    if already_failed:
        runtime.close_resources(failed=True)
    else:
        with pytest.raises(OSError, match='cleanup failed'):
            runtime.close_resources()
    assert events == ['failure', 'earlier', 'stage']
    assert runtime.stage is None
    assert not runtime._patches._exit_callbacks

# ** test: custom_lookup_and_slots_rejected
def test_custom_lookup_and_slots_rejected():
    """Do not bypass custom lookup or invent a class-wide fallback for slots."""

    class CustomLookup(LiveDriver):
        def __getattribute__(self, name):
            return object.__getattribute__(self, name)

    class SlottedDriver:
        __slots__ = ()
        def operate(self, value):
            return value

    for driver in (CustomLookup(), SlottedDriver()):
        runtime = build_phase_runtime(session=RequestContext(), tester_module_path=MODULE, tester_class_name='LiveConsumer')
        runtime.session.data['driver'] = driver
        runtime.as_keys.add('driver')
        with pytest.raises(TiferetError):
            runtime.handle_execution(Execution(target='$r.driver', method='patch_raises', kwargs={
                'method': 'operate', 'module_path': 'builtins', 'class_name': 'OSError',
            }))
        assert driver.operate('unchanged') == ('real:unchanged' if isinstance(driver, LiveDriver) else 'unchanged')
        runtime.close_resources()
