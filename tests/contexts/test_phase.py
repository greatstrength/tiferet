"""Tiferet Phase Runtime Dialect Tests"""

# *** imports

# ** core
import inspect
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest import mock

# ** infra
import pytest

# ** app
from tiferet.assets import TiferetError
from tiferet.blueprints.tester import build_phase_runtime, register_phase_handlers
from tiferet.contexts.request import RequestContext
from tiferet.contexts.tester_phase import PhaseRuntimeContext, compile_phase_steps
from tiferet.domain.core import ModelError
from tiferet.domain.tester_phase import (
    ArrangedMock,
    Assertion,
    Conditions,
    Execution,
    ExecutionTarget,
    PhaseRuntime,
    Test,
)
from tiferet.events import DomainEvent
from tiferet.events.tester_module import TestEvent
from tiferet.events.tester_phase import EvaluateAssertion
from tiferet.mappers.tester_phase import AssertionConfigObject, ExecutionConfigObject
from tiferet.utils.tester_check import Check
from tiferet.utils.tester_stage import STAGE_PREFIX, Stage

# *** constants

# ** constant: module_path
MODULE_PATH = 'tests.contexts.test_phase'

# ** constant: handle_target_message
HANDLE_TARGET_MESSAGE = 'handle requires target self, a class target, $mock.<name>, or $r.<key>.'

# ** constant: error_message_fixture
ERROR_MESSAGE_FIXTURE = {
    'module_path': 'tiferet.domain.error',
    'class_name': 'ErrorMessage',
    'attributes': {
        'lang': 'en_US',
        'text': 'An error occurred.',
    },
}

# ** constant: handle_dependencies_message
HANDLE_DEPENDENCIES_MESSAGE = 'dependencies is legal only on handle with a named event target.'

# *** functions

# ** function: echo
def echo(value: Any) -> Any:
    '''
    Return the value unchanged.

    :param value: The value to return.
    :type value: Any
    :return: The same value.
    :rtype: Any
    '''

    # Return the value unchanged.
    return value

# ** function: named_event_class
def named_event_class() -> type:
    '''
    Return the NamedEvent class.

    :return: The NamedEvent class.
    :rtype: type
    '''

    # Return the class.
    return NamedEvent

# ** function: stage_directories
def _stage_directories() -> set:
    '''
    Return the stage directory names under the temporary root.

    :return: The names that start with STAGE_PREFIX.
    :rtype: set
    '''

    # List the temporary root and keep the stage names.
    return {
        name
        for name in os.listdir(tempfile.gettempdir())
        if name.startswith(STAGE_PREFIX)
    }

# ** function: test
def _test(test_id: str, conditions: Conditions, executes: list, asserts: list) -> Test:
    '''
    Build one test with the given phases.

    :param test_id: The test id and name.
    :type test_id: str
    :param conditions: The conditions phase.
    :type conditions: Conditions
    :param executes: The execute steps.
    :type executes: list
    :param asserts: The assert steps.
    :type asserts: list
    :return: The test.
    :rtype: Test
    '''

    # Build the test with no added field.
    return Test(id=test_id, name=test_id, conditions=conditions, executes=executes, asserts=asserts)

# ** function: runtime
def _runtime(
        tester_module_path: str,
        tester_class_name: str,
        tester_attributes: dict = None,
        root_fixtures: dict = None,
        tester_fixtures: dict = None,
    ) -> PhaseRuntimeContext:
    '''
    Build a phase runtime on a fresh session through build_phase_runtime.

    :param tester_module_path: The tester class module path.
    :type tester_module_path: str
    :param tester_class_name: The tester class name.
    :type tester_class_name: str
    :param tester_attributes: Attributes new passes to the tester class.
    :type tester_attributes: dict
    :param root_fixtures: Root fixture specs.
    :type root_fixtures: dict
    :param tester_fixtures: Tester-local fixture specs.
    :type tester_fixtures: dict
    :return: The phase runtime context.
    :rtype: PhaseRuntimeContext
    '''

    # Build the runtime on a fresh session.
    return build_phase_runtime(
        RequestContext(),
        tester_module_path,
        tester_class_name,
        tester_attributes=tester_attributes,
        root_fixtures=root_fixtures,
        tester_fixtures=tester_fixtures,
    )

# ** function: observe
def _observe(value: Any, asserts: list, executes: list = None, conditions: Conditions = None) -> PhaseRuntimeContext:
    '''
    Store a value at as key got through echo, then run the asserts.

    :param value: The value to store at got.
    :type value: Any
    :param asserts: The asserts to run; empty means a type hold on got.
    :type asserts: list
    :param executes: Executes that run after the store.
    :type executes: list
    :param conditions: The conditions phase.
    :type conditions: Conditions
    :return: The phase runtime context.
    :rtype: PhaseRuntimeContext
    '''

    # Build a runtime on RecordingEvent.
    ctx = _runtime(MODULE_PATH, 'RecordingEvent')

    # Build the execution that stores the value through echo.
    store = Execution(
        target=ExecutionTarget(module_path=MODULE_PATH, attribute='echo'),
        method='echo',
        args=[value],
        data_key='got',
    )

    # Hold the stored type when no assert is supplied.
    held = asserts or [
        Assertion(
            check='type',
            outcome='got',
            module_path=type(value).__module__,
            class_name=type(value).__qualname__,
        ),
    ]

    # Run the test and return the runtime.
    ctx.run(_test(
        'phase.observe',
        conditions or Conditions(),
        [store] + list(executes or []),
        held,
    ))
    return ctx

# *** classes

# ** class: has_new
class HasNew:
    '''
    A tester double with a value, whose new method is not the reserved-new factory.
    '''

    # * init
    def __init__(self, value: Any = None) -> None:
        '''
        Store the value.

        :param value: The constructor value.
        :type value: Any
        :return: None
        :rtype: None
        '''

        # Store the value.
        self.value = value

    # * method: new
    def new(self) -> None:
        '''
        Mark the instance, then raise to prove reserved new did not call this method.

        :return: Never returns.
        :rtype: None
        '''

        # Mark the call, then raise the guard error.
        self._called_new = True
        raise AssertionError('HasNew.new was called.')

# ** class: recording_event
class RecordingEvent(DomainEvent):
    '''
    A domain event that stores its constructor mapping and returns its execute kwargs.
    '''

    # * init
    def __init__(self, **dependencies) -> None:
        '''
        Store the constructor mapping.

        :param dependencies: The constructor mapping.
        :type dependencies: dict
        :return: None
        :rtype: None
        '''

        # Store the constructor mapping.
        self.dependencies = dependencies

    # * method: execute
    def execute(self, **kwargs) -> dict:
        '''
        Return only the execute kwargs.

        :param kwargs: The execute keyword arguments.
        :type kwargs: dict
        :return: The execute kwargs.
        :rtype: dict
        '''

        # Return the execute kwargs.
        return kwargs

# ** class: named_event
class NamedEvent(DomainEvent):
    '''
    A domain event with one constructor parameter dep that defaults to None.
    '''

    # * init
    def __init__(self, dep: Any = None) -> None:
        '''
        Store the dep collaborator.

        :param dep: The constructor collaborator.
        :type dep: Any
        :return: None
        :rtype: None
        '''

        # Store the collaborator.
        self.dep = dep

    # * method: execute
    def execute(self, **kwargs) -> dict:
        '''
        Return the dep collaborator and the execute kwargs.

        :param kwargs: The execute keyword arguments.
        :type kwargs: dict
        :return: The dep collaborator and kwargs.
        :rtype: dict
        '''

        # Return the collaborator and kwargs.
        return {'dep': self.dep, 'kwargs': kwargs}

# ** class: failing_close_stage
class FailingCloseStage(Stage):
    '''
    A stage whose close removes the directory, then raises.
    '''

    # * method: close
    def close(self) -> None:
        '''
        Close the stage, then raise a cleanup error.

        :return: None
        :rtype: None
        '''

        # Close the stage, then raise.
        Stage.close(self)
        raise OSError('cleanup failed')

# *** tests

# ** test: named_handle_passes_reserved_kwargs
def test_named_handle_passes_reserved_kwargs():
    '''
    Assert a named handle forwards reserved names to execute as data.
    '''

    # Arrange the reserved mapping and the named class target.
    reserved = {'dependencies': ['a'], 'middleware': ['b'], 'event_cls': 'c'}
    target = ExecutionTarget(module_path=MODULE_PATH, class_name='NamedEvent')
    step = Execution(
        target=target,
        method='handle',
        dependencies={'dep': 'value'},
        kwargs=reserved,
        data_key='seen',
    )

    # Observe a value, then run the named handle.
    ctx = _observe('loader', [], executes=[step])

    # The constructor mapping and the reserved keywords stay separate.
    assert ctx.session.data['seen'] == {
        'dep': 'value',
        'kwargs': {'dependencies': ['a'], 'middleware': ['b'], 'event_cls': 'c'},
    }

# ** test: handle_step_passes_dependencies_kwarg
def test_handle_step_passes_dependencies_kwarg():
    '''
    Assert a self handle forwards reserved names to execute as data.
    '''

    # Arrange the reserved mapping, the runtime, and the error service mock.
    reserved = {'dependencies': ['a'], 'middleware': ['b'], 'event_cls': 'c'}
    ctx = _runtime(MODULE_PATH, 'RecordingEvent')
    conditions = Conditions(mocks={
        'error_service': ArrangedMock(module_path='tiferet.interfaces', class_name='ErrorService'),
    })

    # Run the handle step, then check the fields and the required names.
    outcome = None
    try:
        ctx.run(_test(
            'phase.handle_reserved',
            conditions,
            [Execution(target='self', method='handle', kwargs=reserved, data_key='seen')],
            [
                Assertion(check='fields', outcome='seen', fields=reserved),
                Assertion(check='parameters_required', names=['dependencies', 'middleware', 'event_cls']),
            ],
        ))
    except TiferetError as error:
        outcome = error

    # The run raises no error and the session holds the reserved mapping.
    assert outcome is None
    assert ctx.session.data['seen'] == {'dependencies': ['a'], 'middleware': ['b'], 'event_cls': 'c'}

# ** test: parameters_required_over_reserved_names
def test_parameters_required_over_reserved_names():
    '''
    Assert the parameters_required harness accepts transport-reserved names.
    '''

    # Arrange the runtime and the error service mock.
    ctx = _runtime(MODULE_PATH, 'RecordingEvent')
    conditions = Conditions(mocks={
        'error_service': ArrangedMock(module_path='tiferet.interfaces', class_name='ErrorService'),
    })

    # Run the handle step and the required-names check.
    outcome = None
    try:
        ctx.run(_test(
            'phase.parameters_required_reserved',
            conditions,
            [Execution(target='self', method='handle', kwargs={}, data_key='seen')],
            [Assertion(check='parameters_required', names=['dependencies', 'middleware', 'event_cls'])],
        ))
    except TiferetError as error:
        outcome = error

    # The run raises no error.
    assert outcome is None

# *** testers

# ** tester: test_phase_runtime
class TestPhaseRuntime:
    '''
    Observation dialect cases for the phase runtime.
    '''

    # * test: attribute_reads_one_key_or_attribute
    def test_attribute_reads_one_key_or_attribute(self):
        '''
        Assert an attribute reads one key of a mapping and one attribute of an object.
        '''

        # Read headers from a mapping and from an object.
        for value in ({'headers': {}}, SimpleNamespace(headers={})):
            ctx = _observe(value, [Assertion(check='equals', outcome='got', attribute='headers', equals={})])
            values = ctx._resolved_assertion_values(
                Assertion(check='equals', outcome='got', attribute='headers', equals={}),
            )

            # The value passed onward as outcome is the read value.
            assert values['outcome'] == {}

        # The context reads without attrgetter.
        source = inspect.getsource(PhaseRuntimeContext._read_attribute)
        assert 'attrgetter' not in source

        # A dotted request ref is still not a runtime reference.
        with pytest.raises(TiferetError) as raised:
            _observe({'lang': 'en'}, [Assertion(check='equals', outcome='$r.got.lang', equals='en')])
        assert 'is not a runtime reference.' in str(raised.value)

    # * test: attribute_equals_empty_mapping_is_strict
    def test_attribute_equals_empty_mapping_is_strict(self):
        '''
        Assert equals on an attribute compares an empty mapping exactly.
        '''

        # The empty attribute passes.
        equals = Assertion(check='equals', outcome='got', attribute='headers', equals={})
        _observe(SimpleNamespace(headers={}), [equals])

        # The attribute with another key fails.
        with pytest.raises(TiferetError) as raised:
            _observe(SimpleNamespace(headers={'x': 1}), [equals])
        assert raised.value.error_code == 'PHASE_CHECK_FAILED'

    # * test: attribute_model_rules
    def test_attribute_model_rules(self):
        '''
        Assert attribute is one name and is not legal on the harness check.
        '''

        # Construct the three bad names.
        for name in ('', 'a.b', '$a'):
            with pytest.raises(ModelError) as raised:
                Assertion(check='equals', outcome='got', attribute=name, equals=1)
            assert raised.value.error_code == 'INVALID_MODEL_VALUE'
            assert f'attribute must be one name, not {name!r}.' in str(raised.value)

        # Construct attribute on the harness check.
        with pytest.raises(ModelError) as raised:
            Assertion(check='assert_called_once_with', mock='command', method='run', attribute='headers')
        assert raised.value.error_code == 'INVALID_MODEL_ATTRIBUTE'

    # * test: attribute_null_container_fails
    def test_attribute_null_container_fails(self):
        '''
        Assert a null container fails the check without reading the attribute.
        '''

        # Run a null check on an attribute of a null outcome.
        with pytest.raises(TiferetError) as raised:
            _observe(None, [Assertion(check='null', outcome='got', attribute='feature_id')])

        # Assert the null-container detail.
        assert raised.value.error_code == 'PHASE_CHECK_FAILED'
        assert 'container is null' in str(raised.value)

    # * test: attribute_missing_is_named
    def test_attribute_missing_is_named(self):
        '''
        Assert a missing key or attribute names itself.
        '''

        # Run a data check on a missing attribute of a mapping and an object.
        for value in ({'present': 1}, SimpleNamespace(present=1)):
            with pytest.raises(TiferetError) as raised:
                _observe(value, [Assertion(check='equals', outcome='got', attribute='missing', equals=1)])

            # Assert the missing detail.
            assert raised.value.error_code == 'PHASE_CHECK_FAILED'
            assert 'missing is missing' in str(raised.value)

    # * test: field_null_uses_identity
    def test_field_null_uses_identity(self):
        '''
        Assert the attribute-null arm uses identity and does not call Check.equal.
        '''

        # Evaluate the None attribute with a spy check service.
        assertion = Assertion(check='null', outcome='got', attribute='value')
        check = mock.Mock(wraps=Check())
        EvaluateAssertion(check).execute(assertion=assertion, values={'outcome': None})
        check.equal.assert_not_called()

        # Evaluate the zero attribute.
        with pytest.raises(TiferetError) as raised:
            EvaluateAssertion(Check()).execute(assertion=assertion, values={'outcome': 0})
        assert raised.value.error_code == 'PHASE_CHECK_FAILED'
        assert 'attribute is not null' in str(raised.value)

        # Falsy values other than None fail.
        for value in (False, '', []):
            with pytest.raises(TiferetError):
                EvaluateAssertion(Check()).execute(assertion=assertion, values={'outcome': value})

    # * test: whole_outcome_null_is_unchanged
    def test_whole_outcome_null_is_unchanged(self):
        '''
        Assert the whole-outcome null arm still calls Check.equal.
        '''

        # The null outcome passes through Check.equal.
        assertion = Assertion(check='null', outcome='got')
        check = mock.Mock(wraps=Check())
        EvaluateAssertion(check).execute(assertion=assertion, values={'outcome': None})
        check.equal.assert_called_once_with(None, None)

        # The non-null outcome keeps the Expected None detail.
        with pytest.raises(TiferetError) as raised:
            EvaluateAssertion(Check()).execute(assertion=assertion, values={'outcome': 0})
        assert 'Expected None, got 0.' in str(raised.value)

    # * test: field_null_and_absent_are_distinct
    def test_field_null_and_absent_are_distinct(self):
        '''
        Assert the attribute-null observation is not the absent check.
        '''

        # The attribute-null check passes.
        _observe(SimpleNamespace(value=None), [Assertion(check='null', outcome='got', attribute='value')])

        # absent is not the field-null observation; a null key is still present.
        with pytest.raises(TiferetError) as raised:
            _observe({'value': None}, [Assertion(check='absent', outcome='got', absent=['value'])])
        assert raised.value.error_code == 'PHASE_CHECK_FAILED'

        # A missing attribute is the missing detail, not an absent pass.
        with pytest.raises(TiferetError) as raised:
            _observe(SimpleNamespace(), [Assertion(check='null', outcome='got', attribute='value')])
        assert 'value is missing' in str(raised.value)

    # * test: equals_null_still_rejected_with_attribute
    def test_equals_null_still_rejected_with_attribute(self):
        '''
        Assert equals null is rejected before the attribute is read.
        '''

        # Store an outcome with attribute value.
        ctx = _observe(SimpleNamespace(value=1), [])

        # Reject equals null on that attribute, before the read.
        assertion = Assertion.model_construct(check='equals', outcome='got', attribute='value', equals=None)
        with mock.patch.object(PhaseRuntimeContext, '_read_attribute') as read:
            with pytest.raises(TiferetError) as raised:
                ctx.handle_assertion(assertion)
        assert raised.value.error_code == 'PHASE_STEP_FAILED'
        assert 'YAML null under equals is rejected' in str(raised.value)
        read.assert_not_called()

    # * test: handle_model_rules
    def test_handle_model_rules(self):
        '''
        Assert the handle target, dependencies, and args rules.
        '''

        # Reject handle on targets that are not named events.
        targets = [
            'sample',
            '$fixture.sample',
            '$stage',
            ExecutionTarget(module_path=MODULE_PATH, attribute='echo'),
        ]
        for target in targets:
            with pytest.raises(ModelError) as raised:
                Execution(target=target, method='handle')
            assert raised.value.error_code == 'INVALID_MODEL_VALUE'
            assert HANDLE_TARGET_MESSAGE in str(raised.value)
            assert 'handle is legal only on target self.' not in str(raised.value)

        # Reject nonempty dependencies on a self handle; an empty mapping equals omit.
        with pytest.raises(ModelError) as raised:
            Execution(target='self', method='handle', dependencies={'dep': 1})
        assert raised.value.error_code == 'INVALID_MODEL_VALUE'
        assert HANDLE_DEPENDENCIES_MESSAGE in str(raised.value)
        assert Execution(target='self', method='handle', dependencies={}).dependencies == {}
        assert Execution(target='self', method='handle').dependencies == {}

        # Reject handle with args.
        with pytest.raises(ModelError) as raised:
            Execution(target='self', method='handle', args=[1])
        assert raised.value.error_code == 'INVALID_MODEL_VALUE'
        assert 'handle takes kwargs, not args.' in str(raised.value)

        # Reject a dependencies value that is not a mapping, including a present null.
        for value in (None, [], 'dep'):
            with pytest.raises(ModelError) as raised:
                Execution(target='$mock.command', method='handle', dependencies=value)
            assert 'dependencies must be a mapping.' in str(raised.value)

        # new is still legal only on self; handle on self stays legal.
        with pytest.raises(ModelError):
            Execution(target='sample', method='new')
        assert Execution(target='self', method='handle').is_named_handle() is False
        assert 'is_named_handle' not in Execution.model_fields

    # * test: named_handle_uses_explicit_dependencies
    def test_named_handle_uses_explicit_dependencies(self):
        '''
        Assert a class-target handle passes its explicit mapping as dependencies.
        '''

        # Arrange a mock dep the mapping does not cite and a loader value.
        conditions = Conditions(mocks={'dep': ArrangedMock(module_path=MODULE_PATH, class_name='HasNew')})
        target = ExecutionTarget(module_path=MODULE_PATH, class_name='NamedEvent')
        steps = [
            Execution(target=target, method='handle', dependencies={'dep': '$r.got'}, data_key='handled'),
        ]

        # Call the execution with TestEvent.handle_test wrapped.
        with mock.patch.object(TestEvent, 'handle_test', wraps=TestEvent.handle_test) as handle:
            ctx = _observe('loaded', [Assertion(check='equals', outcome='got', equals='loaded')], executes=steps, conditions=conditions)

        # TestEvent.handle_test receives NamedEvent and the explicit mapping.
        handle.assert_called_once_with(NamedEvent, dependencies={'dep': 'loaded'}, execute_kwargs={})
        assert ctx.session.data['handled']['dep'] == 'loaded'
        assert ctx.session.data['handled']['dep'] is not ctx.mocks['dep']

        # Absent dependencies passes an empty mapping.
        with mock.patch.object(TestEvent, 'handle_test', wraps=TestEvent.handle_test) as handle:
            _observe('loaded', [Assertion(check='equals', outcome='got', equals='loaded')], executes=[
                Execution(target=ExecutionTarget(module_path=MODULE_PATH, class_name='RecordingEvent'), method='handle'),
            ])
        handle.assert_called_once_with(RecordingEvent, dependencies={}, execute_kwargs={})

    # * test: named_handle_on_mock_and_ref
    def test_named_handle_on_mock_and_ref(self):
        '''
        Assert $mock. and $r. named handles, and a non-callable target.
        '''

        # Arrange a callable mock named command.
        conditions = Conditions(mocks={'command': ArrangedMock(module_path=MODULE_PATH, class_name='RecordingEvent')})
        step = Execution(
            target='$mock.command',
            method='handle',
            dependencies={'dep': '$r.got'},
            kwargs={'arg': 'test'},
        )

        # Call the mock handle.
        ctx = _observe('value', [Assertion(check='equals', outcome='got', equals='value')], executes=[step], conditions=conditions)

        # The mock is event_cls, the mapping is dependencies, arg is the event argument.
        command = ctx.mocks['command']
        command.assert_called_once_with(dep='value')
        command.return_value.execute.assert_called_once_with(arg='test')

        # A kwargs key named dependencies is an event argument, not the field.
        kwarg = Execution(target='$mock.command', method='handle', kwargs={'dependencies': {'dep': 1}})
        assert kwarg.dependencies == {}
        assert kwarg.kwargs == {'dependencies': {'dep': 1}}

        # The non-callable $r. target is a step failure.
        with pytest.raises(TiferetError) as raised:
            _observe('value', [], executes=[Execution(target='$r.got', method='handle')])
        assert raised.value.error_code == 'PHASE_STEP_FAILED'
        assert 'handle target $r.got is not callable.' in str(raised.value)

    # * test: named_handle_import_miss_detail
    def test_named_handle_import_miss_detail(self):
        '''
        Assert an unimportable module and a missing class name their details.
        '''

        # An unimportable module names its import error.
        with pytest.raises(TiferetError) as raised:
            _observe('value', [], executes=[
                Execution(target=ExecutionTarget(module_path='tests.missing_module', class_name='NamedEvent'), method='handle'),
            ])
        assert raised.value.error_code == 'PHASE_STEP_FAILED'
        assert 'Could not import module tests.missing_module: ' in str(raised.value)

        # An imported module without the class keeps its detail.
        with pytest.raises(TiferetError) as raised:
            _observe('value', [], executes=[
                Execution(target=ExecutionTarget(module_path=MODULE_PATH, class_name='MissingEvent'), method='handle'),
            ])
        assert raised.value.error_code == 'PHASE_STEP_FAILED'
        assert f'{MODULE_PATH} has no MissingEvent.' in str(raised.value)

    # * test: observation_fields_round_trip
    def test_observation_fields_round_trip(self):
        '''
        Assert dependencies and attribute map and dump as written.
        '''

        # Map an execution with dependencies and one without.
        target = {'module_path': MODULE_PATH, 'class_name': 'RecordingEvent'}
        omitted = ExecutionConfigObject.model_validate({'target': target, 'method': 'handle'})
        empty = ExecutionConfigObject.model_validate({'target': target, 'method': 'handle', 'dependencies': {}})
        present = ExecutionConfigObject.model_validate({'target': target, 'method': 'handle', 'dependencies': {'dep': 1}})
        assert present.map().dependencies == {'dep': 1}
        assert omitted.map().dependencies == {}

        # Dump the executions.
        assert omitted.to_primitive(role='to_data')['dependencies'] == {}
        assert empty.to_primitive(role='to_data')['dependencies'] == {}
        assert ExecutionConfigObject.from_model(omitted.map()).to_primitive(role='to_data')['dependencies'] == {}
        assert ExecutionConfigObject.from_model(present.map()).dependencies == {'dep': 1}

        # Dump an assertion without and with attribute.
        bare = AssertionConfigObject.model_validate({'outcome': 'got', 'equals': 1})
        read = AssertionConfigObject.model_validate({'outcome': 'got', 'attribute': 'headers', 'equals': {}})
        assert 'attribute' not in bare.to_primitive(role='to_data')
        assert read.to_primitive(role='to_data') == {'outcome': 'got', 'attribute': 'headers', 'equals': {}}
        assert read.map().attribute == 'headers'

        # A staged test still compiles one conditions step.
        steps = compile_phase_steps(_test('phase.round', Conditions(stage=True), [omitted.map()], [read.map()]))
        assert [step.service_id for step in steps].count('phase_conditions') == 1

    # * test: stage_adds_no_runtime_field_or_step
    def test_stage_adds_no_runtime_field_or_step(self):
        '''
        Assert the stage adds no runtime field, builder parameter, handler, or step.
        '''

        # The stage is not a PhaseRuntime field.
        assert ('stage' in PhaseRuntime.model_fields) is False

        # The runtime builder signature is unchanged.
        assert list(inspect.signature(build_phase_runtime).parameters) == [
            'session',
            'tester_module_path',
            'tester_class_name',
            'tester_attributes',
            'root_fixtures',
            'tester_fixtures',
        ]

        # The phase handlers add no stage step.
        assert list(register_phase_handlers()) == [
            'conditions',
            'execute',
            'assert',
        ]

        # A staged test compiles to one conditions step.
        steps = compile_phase_steps(_test(
            'phase.staged',
            Conditions(stage=True),
            [Execution(target='$stage', method='path', data_key='directory')],
            [Assertion(check='null', outcome='directory')],
        ))
        assert [step.service_id for step in steps].count('phase_conditions') == 1

    # * test: stage_rearrange_closes_the_live_stage
    def test_stage_rearrange_closes_the_live_stage(self):
        '''
        Assert a second staged conditions phase closes the live stage first.
        '''

        # Record stage directories.
        before = _stage_directories()

        # Arrange once and hold the first stage path.
        ctx = _runtime(MODULE_PATH, 'RecordingEvent')
        ctx.handle_conditions(Conditions(stage=True))
        first_directory = ctx.stage.path()

        # Arrange again; the first directory is gone.
        ctx.handle_conditions(Conditions(stage=True))
        assert Path(first_directory).exists() is False

        # Close the stage and assert nothing leaked.
        ctx.close_stage()
        assert ctx.stage is None
        assert _stage_directories() == before
