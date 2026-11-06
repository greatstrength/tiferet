"""Closed module/class forwarding-spy experiments."""

# *** imports

# ** core
import inspect
from copy import deepcopy
from importlib import import_module
from pathlib import Path

# ** infra
import pytest
import yaml
from pydantic import ValidationError

# ** app
from tiferet.assets import TiferetError
from tiferet.blueprints.tester import build_phase_runtime, build_test_session, _build_module_test, run_test_module
from tiferet.contexts.request import RequestContext
from tiferet.domain import ModelError
from tiferet.domain.tester_phase import Execution
from tiferet.mappers.tester_phase import ExecutionConfigObject, TestConfigObject

# *** constants

# ** constant: module_path
MODULE = 'experiments.tester_efficacy.tests.test_spies'

# *** functions

# ** function: module_echo
def module_echo(value, required, *, options=None):
    """Forward the same object without copying it.

    :param value: The value.
    :type value: Any
    :param required: The required.
    :type required: Any
    :param options: The options.
    :type options: Any
    """

    return value

# ** function: explode
def explode():
    """Fail after a spy is installed."""

    raise RuntimeError('execution failed')

# ** function: abort
def abort():
    """Abort outside Exception handling."""

    raise KeyboardInterrupt('aborted')

# ** function: runtime
def runtime():
    """Build a fresh scoped runtime."""

    return build_phase_runtime(session=RequestContext(), tester_module_path=MODULE, tester_class_name='Demo')

# ** function: install
def install(ctx, name, member, class_name=None):
    """Install an explicitly named spy through the normal Execution mapper.

    :param ctx: The ctx.
    :type ctx: Any
    :param name: The name.
    :type name: Any
    :param member: The member.
    :type member: Any
    :param class_name: The class name.
    :type class_name: Any
    """

    target = {'module_path': MODULE}
    kwargs = {'name': name}
    if class_name:
        target['class_name'] = class_name
        kwargs['method'] = member
    else:
        target['attribute'] = member
    item = ExecutionConfigObject.model_validate({'target': target, 'method': 'spy_calls', 'kwargs': kwargs}).map()
    ctx.handle_execution(item)
    return ctx.spies[name]

# *** classes

# ** class: demo
class Demo:
    """Expose ordinary, static, and class descriptors for faithful binding."""

    # * method: echo
    def echo(self, value, required, *, options=None):
        """Return the exact supplied object.

        :param value: The value.
        :type value: Any
        :param required: The required.
        :type required: Any
        :param options: The options.
        :type options: Any
        """

        return value

    # * method: static_echo (static)
    @staticmethod
    def static_echo(value, required, *, options=None):
        """Return the exact supplied object without binding.

        :param value: The value.
        :type value: Any
        :param required: The required.
        :type required: Any
        :param options: The options.
        :type options: Any
        """

        return value

    # * method: class_echo (classmethod)
    @classmethod
    def class_echo(cls, value, required, *, options=None):
        """Expose the actual dynamically bound class and original object.

        :param value: The value.
        :type value: Any
        :param required: The required.
        :type required: Any
        :param options: The options.
        :type options: Any
        """

        return cls, value

    # * method: dangerous (property)
    @property
    def dangerous(self):
        """A property is not a spy-able callable."""

        raise AssertionError('do not invoke property')

# ** class: derived_demo
class DerivedDemo(Demo):
    """Inherited members must restore to absence in this own namespace."""

# *** tests

# ** test: forwarding_binding_and_identity
@pytest.mark.parametrize('member', ['echo', 'static_echo', 'class_echo'])
@pytest.mark.parametrize('class_name', ['Demo', 'DerivedDemo'])
@pytest.mark.parametrize('via_class', [True, False])
def test_forwarding_binding_and_identity(member, class_name, via_class):
    """Preserve binding, required args and identity; restore exact descriptors.

    :param member: The member.
    :type member: Any
    :param class_name: The class name.
    :type class_name: Any
    :param via_class: The via class.
    :type via_class: Any
    """

    cls = getattr(import_module(MODULE), class_name)
    present = member in vars(cls)
    descriptor = inspect.getattr_static(cls, member)
    ctx = runtime()
    record = install(ctx, 'calls', member, class_name)
    value, options = [], {}
    instance = cls()
    try:
        if via_class and member == 'echo':
            result = getattr(cls, member)(instance, value, 'required', options=options)
        else:
            result = getattr(cls if via_class else instance, member)(value, 'required', options=options)
        assert (result[1] if member == 'class_echo' else result) is value
        args, kwargs = record.call_args
        offset = 0 if member == 'static_echo' else 1
        assert args[offset] is value and args[offset + 1] == 'required'
        assert kwargs['options'] is options
        if member == 'echo': assert args[0] is instance
        if member == 'class_echo': assert args[0] is cls and result[0] is cls
        assert record.call_count == 1
        assert not ctx.mocks
    finally:
        ctx.close_resources()
    assert (member in vars(cls)) is present
    assert inspect.getattr_static(cls, member) is descriptor

# ** test: nested_layering
@pytest.mark.parametrize('member', ['module_echo', 'Demo.echo', 'Demo.static_echo', 'Demo.class_echo'])
def test_nested_layering(member):
    """Nested forwarding layers restore exact module or descriptor values.

    :param member: The member.
    :type member: Any
    """

    module = import_module(MODULE)
    owner, attr = (module, member) if '.' not in member else (module.Demo, member.split('.')[1])
    original = inspect.getattr_static(owner, attr)
    ctx = runtime()
    first = install(ctx, 'first', member)
    second = install(ctx, 'second', member)
    try:
        if owner is module: module.module_echo([], 'required')
        else: getattr(module.Demo(), attr)([], 'required')
        assert first.call_count == second.call_count == 1
    finally:
        ctx.close_resources()
    assert inspect.getattr_static(owner, attr) is original

# ** test: cleanup_all_entries
@pytest.mark.parametrize('entry', ['phase', 'feature'])
@pytest.mark.parametrize('exit_kind', ['success', 'assertion', 'execution', 'base_exception', 'partial_setup'])
def test_cleanup_all_entries(entry, exit_kind):
    """Restore namespace mutations through both lifecycle owners on every exit.

    :param entry: The entry.
    :type entry: Any
    :param exit_kind: The exit kind.
    :type exit_kind: Any
    """

    path = Path(__file__).parents[1] / 'tiferet_tests/test_spies.yml'
    mapping = deepcopy(yaml.safe_load(path.read_text())['tests']['module_forward'])
    expected = None
    if exit_kind == 'assertion':
        mapping['assert'][0]['equals'] = 'wrong'
        expected = TiferetError
    elif exit_kind in ('execution', 'base_exception'):
        method = 'explode' if exit_kind == 'execution' else 'abort'
        mapping['execute'].append({'target': {'module_path': MODULE, 'attribute': method}, 'method': method})
        expected = RuntimeError if exit_kind == 'execution' else KeyboardInterrupt
    elif exit_kind == 'partial_setup':
        item = deepcopy(mapping['execute'][0]);item['target']['attribute'] = 'missing'
        item['kwargs']['name'] = 'other';mapping['execute'].insert(1, item)
        expected = TiferetError
    module = import_module(MODULE)
    original = module.module_echo
    if entry == 'phase':
        ctx = runtime()
        model = TestConfigObject.model_validate(mapping).map(id='spy.proof', name='spy.proof')
        action = lambda: ctx.run(model)
    else:
        ctx = _build_module_test('spy_cleanup', mapping, {'tester_module_path': MODULE, 'tester_class_name': 'Demo'})
        action = lambda: ctx.execute_feature(build_test_session(test_context=ctx))
    if expected:
        with pytest.raises(expected):action()
    else:action()
    assert module.module_echo is original

# ** test: reject_invalid_declarations
@pytest.mark.parametrize('change', [
    {'target': '$r.any'}, {'args': [1]}, {'raises': True, 'as': 'failure'}, {'dependencies': {}},
    {'kwargs': {'name': 'x', 'callback': 'forbidden'}}, {'kwargs': {'name': 'x', 'method': 'echo'}},
    {'kwargs': {'name': 'bad.name'}},
    {'target': {'module_path': MODULE, 'attribute': 'Demo.dangerous.__call__'}},
])
def test_reject_invalid_declarations(change):
    """Closed shapes reject unsafe declarations before mutation.

    :param change: The change.
    :type change: Any
    """

    item = {'target': {'module_path': MODULE, 'attribute': 'module_echo'}, 'method': 'spy_calls', 'kwargs': {'name': 'x'}}
    item.update(change)
    with pytest.raises((ModelError, ValidationError, TiferetError)):
        ctx = runtime()
        try:ctx.handle_execution(ExecutionConfigObject.model_validate(item).map())
        finally:ctx.close_resources()

# ** test: aliases_do_not_inject_dependencies
def test_aliases_do_not_inject_dependencies():
    """Observation records do not become arranged constructor dependencies."""

    ctx = runtime()
    try:
        install(ctx, 'observed', 'module_echo')
        assert 'observed' not in ctx.mocks
        with pytest.raises(TiferetError):install(ctx, 'observed', 'module_echo')
    finally:ctx.close_resources()

# ** test: public_yaml_entry
def test_public_yaml_entry():
    """Existing called-once checks work unchanged for named spy records."""

    report = run_test_module(str(Path(__file__)))
    assert not report['failures']

# ** test: layering_with_instance_failure_patch
@pytest.mark.parametrize('instance_first', [True, False])
def test_layering_with_instance_failure_patch(instance_first):
    """Spies and instance failure patches share one reversible LIFO lifecycle.

    :param instance_first: The instance first.
    :type instance_first: Any
    """

    module = import_module(MODULE)
    original = inspect.getattr_static(module.Demo, 'echo')
    instance = module.Demo()
    ctx = runtime()
    ctx.session.data['instance'] = instance
    ctx.as_keys.add('instance')
    patch = Execution(target='$r.instance', method='patch_raises', kwargs={
        'method': 'echo', 'module_path': 'builtins', 'class_name': 'OSError', 'message': 'injected',
    })
    try:
        if instance_first:ctx.handle_execution(patch)
        record = install(ctx, 'class_record', 'echo', 'Demo')
        if not instance_first:ctx.handle_execution(patch)
        with pytest.raises(OSError, match='injected'):instance.echo([], 'required')
        assert record.call_count == 0
    finally:ctx.close_resources()
    assert 'echo' not in vars(instance)
    assert inspect.getattr_static(module.Demo, 'echo') is original
