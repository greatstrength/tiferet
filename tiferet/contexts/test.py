"""Tiferet Test Contexts"""

# *** imports

# ** core
import inspect
import re
from importlib import import_module
from types import SimpleNamespace
from typing import Any, Callable, Dict, List
from unittest.mock import Mock

# ** app
from .core import BaseContext
from .feature import FeatureContext
from .request import RequestContext
from .. import a
from ..assets import TiferetError
from ..assets.core import REQUEST_REF_PREFIX
from ..domain import EventFeatureStep
from ..domain.test import (
    Assertion,
    Conditions,
    Execution,
    ExecutionTarget,
    PhaseRuntime,
    Test,
)
from ..events import DomainEvent
from ..events.phase import EvaluateAssertion, ExerciseMapperBases

# *** constants

# ** constant: fixture_ref_prefix
FIXTURE_REF_PREFIX = '$fixture.'

# ** constant: mock_ref_prefix
MOCK_REF_PREFIX = '$mock.'

# ** constant: ref_name
REF_NAME = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

# ** constant: phase_conditions_id
PHASE_CONDITIONS_ID = 'phase_conditions'

# ** constant: phase_execute_id
PHASE_EXECUTE_ID = 'phase_execute'

# ** constant: phase_assert_id
PHASE_ASSERT_ID = 'phase_assert'

# ** constant: builtin_types
BUILTIN_TYPES: Dict[str, type] = {
    'int': int,
    'str': str,
    'float': float,
    'bool': bool,
    'list': list,
    'dict': dict,
}

# *** functions

# ** function: import_named
def import_named(module_path: str, name: str) -> Any:
    '''
    Import one attribute from a module.

    :param module_path: The module that holds the attribute.
    :type module_path: str
    :param name: The attribute name.
    :type name: str
    :return: The imported attribute.
    :rtype: Any
    '''

    # Import the module, then the named attribute. A miss is None.
    try:
        module = import_module(module_path)
    except (ImportError, TypeError, ValueError):
        return None
    if not hasattr(module, name):
        return None
    return getattr(module, name)

# ** function: copy_data
def _copy_data(value: Any) -> Any:
    '''
    Copy a data tree without sharing nested mappings or lists.

    :param value: The value to copy.
    :type value: Any
    :return: The copy.
    :rtype: Any
    '''

    # Copy mappings and lists. Leave scalars and live objects in place.
    if isinstance(value, dict):
        return {
            key: _copy_data(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [
            _copy_data(item)
            for item in value
        ]
    return value

# ** function: annotation_name
def _annotation_name(annotation: Any) -> str | None:
    '''
    Return the name of an annotation, or None when it is empty.

    :param annotation: The annotation to name.
    :type annotation: Any
    :return: The annotation name.
    :rtype: str | None
    '''

    # An empty annotation is not a type name.
    if annotation is inspect.Signature.empty:
        return None
    if isinstance(annotation, str):
        return annotation
    return getattr(annotation, '__name__', str(annotation))

# ** function: ref_name
def ref_name(value: str, prefix: str) -> str | None:
    '''
    Return the name of a whole-value ref, or None when it is not a name.

    :param value: The scalar ref.
    :type value: str
    :param prefix: The ref prefix.
    :type prefix: str
    :return: The ref name, or None when a further dot makes it illegal.
    :rtype: str | None
    '''

    # $r.built.lang is not a path. The method raises when this is None.
    name = value[len(prefix):]
    if not REF_NAME.fullmatch(name):
        return None
    return name

# ** function: compile_phase_steps
def compile_phase_steps(test: Test) -> List[EventFeatureStep]:
    '''
    Compile a test into feature steps without encoding the phase objects.

    ``as`` is already ``data_key`` on each Execution. The step stores that
    key. Parameters stay empty. ``pass_on_error`` is not set.

    :param test: The test to compile.
    :type test: Test
    :return: The compiled steps, conditions then executes then asserts.
    :rtype: List[EventFeatureStep]
    '''

    # The conditions step has no data key and no string parameters.
    steps = [
        EventFeatureStep(
            name='conditions',
            service_id=PHASE_CONDITIONS_ID,
        ),
    ]

    # Each execute item is one step. data_key is as. The object is not encoded.
    for index, execution in enumerate(test.executes):
        fields = {
            'name': f'execute_{index}',
            'service_id': PHASE_EXECUTE_ID,
        }
        if execution.data_key is not None:
            fields['data_key'] = execution.data_key
        steps.append(EventFeatureStep(**fields))

    # Assert items run after the execute items. They do not store a result.
    for index, _assertion in enumerate(test.asserts):
        steps.append(EventFeatureStep(
            name=f'assert_{index}',
            service_id=PHASE_ASSERT_ID,
        ))
    return steps

# *** contexts

# ** context: phase_runtime_context
class PhaseRuntimeContext(BaseContext):
    '''
    Runs one test's phases against a bound ``PhaseRuntime``. The model names
    the tester class and the fixture specs. Built fixtures, arranged mocks,
    and ``as`` keys are run state on this context. The handlers take
    Conditions, Execution, and Assertion. They are not dispatched through
    AppSessionContext.
    '''

    # * attribute: domain_type
    domain_type = PhaseRuntime

    # * attribute: session
    session: RequestContext

    # * attribute: fixtures
    fixtures: Dict[str, Any]

    # * attribute: mocks
    mocks: Dict[str, Mock]

    # * attribute: as_keys
    as_keys: set

    # * attribute: steps
    steps: List[EventFeatureStep]

    # * attribute: check
    check: Any

    # * init
    def __init__(self, session: RequestContext, check: Any = None) -> None:
        '''
        Initialize a phase runtime context for one session.

        ``from_domain`` binds the ``PhaseRuntime`` after construction. This
        constructor does not copy the model onto attributes. The check is
        injected. This context does not import it.

        :param session: The session whose data stores ``as`` results.
        :type session: RequestContext
        :param check: The injected check instance.
        :type check: Any
        :return: None.
        :rtype: None
        '''

        # Register through domain_type. Do not clobber Feature or Test.
        super().__init__()

        # Hold the session and the injected check.
        self.session = session
        self.check = check

        # Built fixtures, arranged mocks, and as keys start empty.
        self.fixtures = {}
        self.mocks = {}
        self.as_keys = set()
        self.steps = []

    # * method: handle_conditions
    def handle_conditions(self, conditions: Conditions) -> None:
        '''
        Build fixtures, then arrange mocks.

        :param conditions: The conditions phase.
        :type conditions: Conditions
        :return: None.
        :rtype: None
        '''

        # Handlers take the object, not an anonymous dict.
        if not isinstance(conditions, Conditions):
            TiferetError.raise_error(
                a.error.PHASE_HANDLER_MISMATCH_ID,
                received=type(conditions).__name__,
                expected='Conditions',
            )

        # A mock name and a fixture name must not collide.
        overlap = set(conditions.mocks) & (set(conditions.fixtures) | set(self.fixtures))
        if overlap:
            TiferetError.raise_error(
                a.error.PHASE_NAME_COLLISION_ID,
                names=sorted(overlap),
            )

        # Build fixtures first so a mock can reference one.
        for name in conditions.fixtures:
            self._build_fixture(name)

        # Arrange mocks after fixtures. $r. is illegal in this phase.
        for name, arranged in conditions.mocks.items():
            self._arrange_mock(name, arranged)

    # * method: handle_execution
    def handle_execution(self, execution: Execution) -> None:
        '''
        Perform one execute item and store its result at data_key.

        :param execution: The execute item.
        :type execution: Execution
        :return: None.
        :rtype: None
        '''

        # Handlers take the object, not an anonymous dict.
        if not isinstance(execution, Execution):
            TiferetError.raise_error(
                a.error.PHASE_HANDLER_MISMATCH_ID,
                received=type(execution).__name__,
                expected='Execution',
            )
        self._invoke(execution)

    # * method: handle_assertion
    def handle_assertion(self, assertion: Assertion) -> None:
        '''
        Run one named check. The first failure fails the test.

        :param assertion: The assert item.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # Handlers take the object, not an anonymous dict.
        if not isinstance(assertion, Assertion):
            TiferetError.raise_error(
                a.error.PHASE_HANDLER_MISMATCH_ID,
                received=type(assertion).__name__,
                expected='Assertion',
            )

        # mapper_contract is ExerciseMapperBases. Every other check is one event.
        if assertion.check == 'mapper_contract':
            self._check_mapper_contract(assertion, ExerciseMapperBases)
            return
        if assertion.check == 'equals' and assertion.equals is None:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='YAML null under equals is rejected.',
            )
        EvaluateAssertion(self.check).execute(
            assertion=assertion,
            values=self._resolved_assertion_values(assertion),
        )

    # * method: run
    def run(self, test: Test) -> List[EventFeatureStep]:
        '''
        Compile the test and run conditions, then each execute, then each assert.

        :param test: The test to run.
        :type test: Test
        :return: The compiled feature steps.
        :rtype: List[EventFeatureStep]
        '''

        # A test is one Test. execute and assert are non-empty.
        if not isinstance(test, Test):
            TiferetError.raise_error(
                a.error.PHASE_HANDLER_MISMATCH_ID,
                received=type(test).__name__,
                expected='Test',
            )
        if not test.executes:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='execute is a non-empty list.',
            )
        if not test.asserts:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='assert is a non-empty list.',
            )

        # Compile for data_key. Do not dispatch through AppSessionContext.
        self.steps = compile_phase_steps(test)
        self.handle_conditions(test.conditions)
        for execution in test.executes:
            self.handle_execution(execution)
        for assertion in test.asserts:
            self.handle_assertion(assertion)
        return self.steps

    # * method: build_fixture
    def _build_fixture(self, name: str) -> None:
        '''
        Construct one fixture by calling the class with attributes.

        :param name: The fixture name.
        :type name: str
        :return: None.
        :rtype: None
        '''

        # Tester-local wins. The model already closed the spec keys.
        spec = self.domain.fixture_spec(name)
        if spec is None:
            TiferetError.raise_error(
                a.error.PHASE_FIXTURE_NOT_FOUND_ID,
                name=name,
            )

        # Call the class. Do not call a method named new.
        cls = self._require_named(spec['module_path'], spec['class_name'])
        attributes = self._resolve_value(
            _copy_data(spec['attributes']),
            allow_request=False,
        )
        self.fixtures[name] = cls(**attributes)

    # * method: arrange_mock
    def _arrange_mock(self, name: str, arranged: Any) -> None:
        '''
        Build a spec mock and arrange its method results.

        :param name: The mock name.
        :type name: str
        :param arranged: The arranged mock.
        :type arranged: Any
        :return: None.
        :rtype: None
        '''

        # Spec the class. Do not construct it.
        cls = self._require_named(arranged.module_path, arranged.class_name)
        mock = Mock(spec=cls)
        if arranged.return_value:
            for method_name, value in arranged.return_value.items():
                self._arrange_method(mock, method_name, value)
        if arranged.context:
            mock.__enter__.return_value = mock
        self.mocks[name] = mock

    # * method: arrange_method
    def _arrange_method(self, mock: Mock, method_name: str, value: Any) -> None:
        '''
        Arrange one mock method as a return value, an attribute bag, or a raise.

        :param mock: The mock being arranged.
        :type mock: Mock
        :param method_name: The method name.
        :type method_name: str
        :param value: The method arrangement.
        :type value: Any
        :return: None.
        :rtype: None
        '''

        # raises and return_value are mutually exclusive on one method.
        if isinstance(value, dict) and 'raises' in value and set(value) != {'raises'}:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='return_value and raises are mutually exclusive.',
            )
        if isinstance(value, dict) and set(value) == {'raises'}:
            self._arrange_raises(mock, method_name, value['raises'])
            return

        # An attribute bag is data, not a callable.
        if isinstance(value, dict) and set(value) == {'attributes'}:
            attributes = self._resolve_value(
                _copy_data(value['attributes']),
                allow_request=False,
            )
            getattr(mock, method_name).return_value = SimpleNamespace(**attributes)
            return

        # A literal, null, or ref is the return value. YAML null stays None.
        resolved = self._resolve_value(_copy_data(value), allow_request=False)
        getattr(mock, method_name).return_value = resolved

    # * method: arrange_raises
    def _arrange_raises(self, mock: Mock, method_name: str, spec: Dict[str, Any]) -> None:
        '''
        Make one mock method raise an imported class.

        :param mock: The mock being arranged.
        :type mock: Mock
        :param method_name: The method name.
        :type method_name: str
        :param spec: The raises spec.
        :type spec: Dict[str, Any]
        :return: None.
        :rtype: None
        '''

        # The spec names a class and an optional message. It is not a callable.
        if not isinstance(spec, dict) or not {'module_path', 'class_name'} <= set(spec):
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='raises is module_path, class_name, and optional message.',
            )
        if set(spec) - {'module_path', 'class_name', 'message'}:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='raises is module_path, class_name, and optional message.',
            )
        exc_cls = self._require_named(spec['module_path'], spec['class_name'])
        message = spec.get('message')
        method = getattr(mock, method_name)
        if message is None:
            method.side_effect = exc_cls
            return
        method.side_effect = exc_cls(message)

    # * method: resolve_value
    def _resolve_value(self, value: Any, allow_request: bool = True) -> Any:
        '''
        Resolve whole-value refs. A ref that is not the entire scalar is a literal.

        :param value: The value to resolve.
        :type value: Any
        :param allow_request: Whether ``$r.`` is legal here.
        :type allow_request: bool
        :return: The resolved value.
        :rtype: Any
        '''

        # Do not eval. Do not call evaluate_condition.
        if isinstance(value, str):
            return self._resolve_scalar(value, allow_request=allow_request)
        if isinstance(value, list):
            return [
                self._resolve_value(item, allow_request=allow_request)
                for item in value
            ]
        if isinstance(value, dict):
            return {
                key: self._resolve_value(item, allow_request=allow_request)
                for key, item in value.items()
            }
        if callable(value):
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='A stored callable is not legal.',
            )
        return value

    # * method: resolve_scalar
    def _resolve_scalar(self, value: str, allow_request: bool = True) -> Any:
        '''
        Resolve one scalar ref, or return a literal.

        :param value: The scalar.
        :type value: str
        :param allow_request: Whether ``$r.`` is legal here.
        :type allow_request: bool
        :return: The resolved value or the literal.
        :rtype: Any
        '''

        # $r. is illegal in conditions, including as a path.
        if value.startswith(REQUEST_REF_PREFIX) and not allow_request:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='$r. is illegal in conditions.',
            )
        if value.startswith(FIXTURE_REF_PREFIX):
            return self._lookup_ref(value, FIXTURE_REF_PREFIX, self.fixtures)
        if value.startswith(MOCK_REF_PREFIX):
            return self._lookup_ref(value, MOCK_REF_PREFIX, self.mocks)
        if value.startswith(REQUEST_REF_PREFIX):
            name = self._ref_name(value, REQUEST_REF_PREFIX)
            if name not in self.as_keys:
                TiferetError.raise_error(
                    a.error.PHASE_REFERENCE_NOT_FOUND_ID,
                    reference=value,
                )
            return self.session.data[name]

        # A prefix inside a longer string is a literal, not a substitution.
        return value

    # * method: lookup_ref
    def _lookup_ref(self, value: str, prefix: str, store: Dict[str, Any]) -> Any:
        '''
        Resolve one whole-value ref from a store.

        :param value: The scalar ref.
        :type value: str
        :param prefix: The ref prefix.
        :type prefix: str
        :param store: The name to object mapping.
        :type store: Dict[str, Any]
        :return: The stored object.
        :rtype: Any
        '''

        # A missing name fails the step. It is not None.
        name = self._ref_name(value, prefix)
        if name not in store:
            TiferetError.raise_error(
                a.error.PHASE_REFERENCE_NOT_FOUND_ID,
                reference=value,
            )
        return store[name]

    # * method: ref_name
    def _ref_name(self, value: str, prefix: str) -> str:
        '''
        Return the name of a whole-value ref. A further dot is not a path.

        :param value: The scalar ref.
        :type value: str
        :param prefix: The ref prefix.
        :type prefix: str
        :return: The ref name.
        :rtype: str
        '''

        # The helper returns the name. An illegal ref fails here.
        name = ref_name(value, prefix)
        if name is None:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail=f'{value} is not a runtime reference.',
            )
        return name

    # * method: invoke
    def _invoke(self, execution: Execution) -> None:
        '''
        Call one execute item and store a result or a caught exception.

        :param execution: The execute item.
        :type execution: Execution
        :return: None.
        :rtype: None
        '''

        # raises stores the exception. It does not use pass_on_error.
        try:
            result = self._call(execution)
        except Exception as error:
            if not execution.raises:
                raise
            self._store(execution.data_key, error)
            return
        if execution.raises:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='A step marked raises did not raise.',
            )
        if execution.data_key:
            self._store(execution.data_key, result)

    # * method: call
    def _call(self, execution: Execution) -> Any:
        '''
        Perform the reserved action or the method call.

        :param execution: The execute item.
        :type execution: Execution
        :return: The call result.
        :rtype: Any
        '''

        # Resolve refs before the call. new and handle are not getattr.
        args = self._resolve_value(execution.args)
        kwargs = self._resolve_value(execution.kwargs)
        if execution.method == 'new':
            return self._call_new()
        if execution.method == 'handle':
            return self._call_handle(kwargs)

        # self is only the reserved target.
        target = self._resolve_target(execution)
        if target == 'self':
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='self is legal only for new and handle.',
            )
        if isinstance(execution.target, ExecutionTarget) and execution.target.attribute:
            if execution.method != execution.target.attribute:
                TiferetError.raise_error(
                    a.error.PHASE_STEP_FAILED_ID,
                    detail='A module attribute target calls that attribute.',
                )
            return target(*args, **kwargs)
        method = getattr(target, execution.method)
        return method(*args, **kwargs)

    # * method: call_new
    def _call_new(self) -> Any:
        '''
        Construct the tester class. Do not call a method named new.

        :return: The constructed instance.
        :rtype: Any
        '''

        # Attributes may contain fixture refs. They must already be built.
        cls = self._require_named(self.domain.tester_module_path, self.domain.tester_class_name)
        attributes = self._resolve_value(_copy_data(self.domain.tester_attributes))
        return cls(**attributes)

    # * method: call_handle
    def _call_handle(self, kwargs: Dict[str, Any]) -> Any:
        '''
        Call DomainEvent.handle with the arranged mocks and the step kwargs.

        :param kwargs: The resolved event arguments.
        :type kwargs: Dict[str, Any]
        :return: The event result.
        :rtype: Any
        '''

        # Do not merge sample_kwargs. Do not construct an instance here.
        cls = self._require_named(self.domain.tester_module_path, self.domain.tester_class_name)
        return DomainEvent.handle(
            cls,
            dependencies=dict(self.mocks),
            **kwargs,
        )

    # * method: resolve_target
    def _resolve_target(self, execution: Execution) -> Any:
        '''
        Resolve an execute target. A bare name is a fixture, not a prior as key.

        :param execution: The execute item.
        :type execution: Execution
        :return: The resolved target, or the string self.
        :rtype: Any
        '''

        # An import target is the class or the module attribute.
        target = execution.target
        if isinstance(target, ExecutionTarget):
            if target.class_name:
                return self._require_named(target.module_path, target.class_name)
            return self._require_named(target.module_path, target.attribute)
        if target == 'self':
            return 'self'
        if isinstance(target, str) and (
            target.startswith(FIXTURE_REF_PREFIX)
            or target.startswith(MOCK_REF_PREFIX)
            or target.startswith(REQUEST_REF_PREFIX)
        ):
            return self._resolve_scalar(target)

        # A bare name is a fixture. It is not an as key.
        if not isinstance(target, str) or target not in self.fixtures:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail=f'Target {target} is not a fixture. A bare name is not a prior as key.',
            )
        return self.fixtures[target]

    # * method: store
    def _store(self, data_key: str, result: Any) -> None:
        '''
        Store a result under the step data_key.

        :param data_key: The as key.
        :type data_key: str
        :param result: The result or caught exception.
        :type result: Any
        :return: None.
        :rtype: None
        '''

        # data_key is the feature data_key. $r.<as> reads this store.
        self.session.set_result(result, data_key=data_key)
        self.as_keys.add(data_key)

    # * method: resolve_outcome
    def _resolve_outcome(self, outcome: str) -> Any:
        '''
        Resolve an outcome name. Do not guess when it is both an as key and a fixture.

        :param outcome: The outcome name or ``$r.`` ref.
        :type outcome: str
        :return: The outcome.
        :rtype: Any
        '''

        # The name is the as key or the fixture name, with no further dot.
        if outcome.startswith(REQUEST_REF_PREFIX):
            name = self._ref_name(outcome, REQUEST_REF_PREFIX)
        else:
            name = outcome
        if name in self.as_keys and name in self.fixtures:
            TiferetError.raise_error(
                a.error.PHASE_NAME_COLLISION_ID,
                names=name,
            )
        if outcome.startswith(REQUEST_REF_PREFIX):
            if name not in self.as_keys:
                TiferetError.raise_error(
                    a.error.PHASE_REFERENCE_NOT_FOUND_ID,
                    reference=outcome,
                )
            return self.session.data[name]
        if name in self.as_keys:
            return self.session.data[name]
        if name in self.fixtures:
            return self.fixtures[name]
        TiferetError.raise_error(
            a.error.PHASE_REFERENCE_NOT_FOUND_ID,
            reference=name,
        )

    # * method: require_named
    def _require_named(self, module_path: str, name: str) -> Any:
        '''
        Import one attribute. A miss is PHASE_STEP_FAILED.

        :param module_path: The module that holds the attribute.
        :type module_path: str
        :param name: The attribute name.
        :type name: str
        :return: The imported attribute.
        :rtype: Any
        '''

        # The helper returns None. The method raises the catalogued miss.
        value = import_named(module_path, name)
        if value is None:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail=f'{module_path} has no {name}.',
            )
        return value

    # * method: check_mapper_contract
    def _check_mapper_contract(self, assertion: Assertion, event_cls: type = None) -> None:
        '''
        Run the mapper protocol through ExerciseMapperBases.

        :param assertion: The mapper_contract check.
        :type assertion: Assertion
        :param event_cls: The event that raises the catalogued failure.
        :type event_cls: type
        :return: None.
        :rtype: None
        '''

        # The event constructs the domain source and calls the check.
        event_cls = ExerciseMapperBases if event_cls is None else event_cls
        event_cls(self.check).execute(exclude=list(assertion.exclude or []))

    # * method: resolved_assertion_values
    def _resolved_assertion_values(self, assertion: Assertion) -> Dict[str, Any]:
        '''
        Resolve the values one check reads. The event does not see the session.

        :param assertion: The assert item.
        :type assertion: Assertion
        :return: The resolved values.
        :rtype: Dict[str, Any]
        '''

        # Outcome, expected trees, and imports are resolved here.
        values = {}
        if assertion.outcome is not None:
            values['outcome'] = self._resolve_outcome(assertion.outcome)
        if assertion.equals is not None:
            values['equals'] = self._resolve_value(assertion.equals)
        if assertion.fields is not None:
            values['fields'] = self._resolve_value(assertion.fields)
        if assertion.check == 'error_code':
            missing = object()
            code = getattr(values['outcome'], 'error_code', missing)
            values['has_error_code'] = code is not missing
            if code is not missing:
                values['error_code'] = code
        if assertion.check in ('type', 'cause') or (
            assertion.check == 'is' and not assertion.builtin
        ):
            values['cls'] = self._require_named(
                assertion.module_path,
                assertion.class_name,
            )
            if assertion.check == 'is':
                values['expected'] = values['cls']
        if assertion.check == 'is' and assertion.builtin:
            values['expected'] = BUILTIN_TYPES[assertion.builtin]
        if assertion.check == 'assert_called_once_with':
            if assertion.mock not in self.mocks:
                TiferetError.raise_error(
                    a.error.PHASE_REFERENCE_NOT_FOUND_ID,
                    reference=assertion.mock,
                )
            values['method'] = getattr(self.mocks[assertion.mock], assertion.method)
            spec = self._resolve_value(assertion.assert_called_once_with)
            if spec.get('times') == 0 and ('args' in spec or 'kwargs' in spec):
                TiferetError.raise_error(
                    a.error.PHASE_STEP_FAILED_ID,
                    detail='times 0 requires args to be omitted.',
                )
            values['spec'] = spec
        if assertion.check == 'event_base':
            values['event_cls'] = self._require_named(
                self.domain.tester_module_path,
                self.domain.tester_class_name,
            )
            values['base_cls'] = self._require_named(
                assertion.module_path,
                assertion.class_name,
            )
            values['mocks'] = dict(self.mocks)
        if assertion.check == 'service_contract':
            values['cls'] = self._require_named(
                self.domain.tester_module_path,
                self.domain.tester_class_name,
            )
        return values


# ** context: test_context
class TestContext(FeatureContext):
    '''
    The session's view of one test. It extends ``FeatureContext`` so a test
    runs as a feature, and it declares ``domain_type = Test`` in its own
    namespace so ``Feature`` stays mapped to ``FeatureContext``.

    The phase runtime is not built here. The tester blueprint injects
    ``build_phase_runtime``. This context stores that callable and wraps it.
    It does not import the blueprint.
    '''

    # * attribute: domain_type
    domain_type = Test

    # * attribute: _build_phase_runtime
    _build_phase_runtime: Callable

    # * attribute: _phase_runtime_slot
    _phase_runtime_slot: Dict[str, Any]

    # * attribute: _tester_module_path
    _tester_module_path: str

    # * attribute: _tester_class_name
    _tester_class_name: str

    # * attribute: _tester_attributes
    _tester_attributes: Dict[str, Any]

    # * attribute: _root_fixtures
    _root_fixtures: Dict[str, Dict[str, Any]]

    # * attribute: _tester_fixtures
    _tester_fixtures: Dict[str, Dict[str, Any]]

    # * init
    def __init__(self,
            get_dependency: Callable,
            build_phase_runtime_handler: Callable = None,
            phase_runtime_slot: Dict[str, Any] = None,
            tester_module_path: str = '',
            tester_class_name: str = '',
            tester_attributes: Dict[str, Any] = None,
            root_fixtures: Dict[str, Dict[str, Any]] = None,
            tester_fixtures: Dict[str, Dict[str, Any]] = None,
            **kwargs,
        ) -> None:
        '''
        Initialize a test context.

        The phase-runtime factory is injected. This context does not import
        the blueprint that builds it.

        :param get_dependency: The handler that resolves compiled phase steps.
        :type get_dependency: Callable
        :param build_phase_runtime_handler: The callable that builds a phase runtime.
        :type build_phase_runtime_handler: Callable
        :param phase_runtime_slot: Shared slot the step resolver reads after build.
        :type phase_runtime_slot: Dict[str, Any]
        :param tester_module_path: The tester class module, empty for a root test.
        :type tester_module_path: str
        :param tester_class_name: The tester class name, empty for a root test.
        :type tester_class_name: str
        :param tester_attributes: Attributes used by ``new``.
        :type tester_attributes: Dict[str, Any]
        :param root_fixtures: Root fixture specs.
        :type root_fixtures: Dict[str, Dict[str, Any]]
        :param tester_fixtures: Tester-local fixture specs.
        :type tester_fixtures: Dict[str, Dict[str, Any]]
        :param kwargs: Feature-context initialization arguments.
        :type kwargs: dict
        :return: None.
        :rtype: None
        '''

        # Initialize the feature context. The bound Test is the workflow.
        super().__init__(get_dependency, **kwargs)

        # Store the injected factory. An absent slot is unwired, not a fallback.
        self._build_phase_runtime = build_phase_runtime_handler
        self._phase_runtime_slot = phase_runtime_slot if phase_runtime_slot is not None else {}

        # Coordinates stay here. The context does not construct the runtime value.
        self._tester_module_path = tester_module_path
        self._tester_class_name = tester_class_name
        self._tester_attributes = tester_attributes or {}
        self._root_fixtures = root_fixtures or {}
        self._tester_fixtures = tester_fixtures or {}

    # * method: build_phase_runtime
    def build_phase_runtime(self,
            session: Any,
            tester_module_path: str,
            tester_class_name: str,
            tester_attributes: Dict[str, Any] = None,
            root_fixtures: Dict[str, Dict[str, Any]] = None,
            tester_fixtures: Dict[str, Dict[str, Any]] = None,
        ) -> Any:
        '''
        Build a phase runtime through the injected handler.

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
        :rtype: Any
        '''

        # An absent callable is an unwired handler, not a local construction.
        if self._build_phase_runtime is None:
            a.core.raise_unwired_handler_error(
                'build_phase_runtime_handler',
                self.domain.id,
                error_code=a.error.APP_ERROR_ID,
            )

        # Delegate. This context does not build the domain value.
        return self._build_phase_runtime(
            session,
            tester_module_path,
            tester_class_name,
            tester_attributes=tester_attributes,
            root_fixtures=root_fixtures,
            tester_fixtures=tester_fixtures,
        )

    # * method: execute_feature
    def execute_feature(self, request: RequestContext, *flags, **kwargs):
        '''
        Run the bound test. The session is the request.

        The phase runtime is reached through the injected callable before the
        compiled steps resolve. This is not ``AppSessionContext.run``.

        :param request: The test session.
        :type request: RequestContext
        :param flags: Execution flags forwarded to the feature loop.
        :type flags: tuple
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The feature execution result.
        :rtype: Any
        '''

        # Build the runtime first so step handlers can read it.
        runtime = self.build_phase_runtime(
            request,
            self._tester_module_path,
            self._tester_class_name,
            tester_attributes=self._tester_attributes,
            root_fixtures=self._root_fixtures,
            tester_fixtures=self._tester_fixtures,
        )
        self._phase_runtime_slot['runtime'] = runtime

        # The bound Test is the workflow. Do not look it up by feature id.
        return super().execute_feature(request, *flags, **kwargs)
