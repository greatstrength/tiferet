"""Tiferet Test Contexts"""

# *** imports

# ** core
import inspect
import re
from importlib import import_module
from types import SimpleNamespace
from typing import Any, Callable, Dict, List
from unittest.mock import MagicMock, Mock

# ** app
from .core import BaseContext
from .feature import FeatureContext
from .request import RequestContext
from .. import a
from ..assets import TiferetError
from ..assets.core import REQUEST_REF_PREFIX
from ..domain import EventFeatureStep
from ..domain.tester_phase import (
    Assertion,
    Conditions,
    Execution,
    ExecutionTarget,
    PhaseRuntime,
    Test,
)
from ..events import DomainEvent
from ..events.tester_phase import (
    EvaluateAssertion,
    ExerciseCalled,
    ExerciseDomainContract,
    ExerciseMapperBases,
    ExerciseMiddlewareChain,
    ExerciseParametersRequired,
    ExerciseServiceContract,
)

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
    Import a named attribute from a module path.

    :param module_path: The module path to import.
    :type module_path: str
    :param name: The attribute name to load.
    :type name: str
    :return: The imported attribute, or null when missing or unloadable.
    :rtype: Any
    '''

    # Import the module; return null for known load failures.
    try:
        module = import_module(module_path)
    except (ImportError, TypeError, ValueError):
        return None

    # Return the attribute when present; null when absent.
    return getattr(module, name, None)

# ** function: copy_data
def _copy_data(value: Any) -> Any:
    '''
    Copy a dict or list recursively, leaving scalars and live objects in place.

    :param value: The value to copy.
    :type value: Any
    :return: The copied value, or the original scalar or live object.
    :rtype: Any
    '''

    # Copy a dict by key with recursive values.
    if isinstance(value, dict):
        return {
            key: _copy_data(item)
            for key, item in value.items()
        }

    # Copy a list item by item.
    if isinstance(value, list):
        return [
            _copy_data(item)
            for item in value
        ]

    # Leave scalars and live objects in place.
    return value

# ** function: annotation_name
def _annotation_name(annotation: Any) -> str | None:
    '''
    Return a readable name for a type annotation.

    :param annotation: The annotation to name.
    :type annotation: Any
    :return: The annotation name, or null when empty.
    :rtype: str | None
    '''

    # Empty annotations have no name.
    if annotation is inspect.Signature.empty:
        return None

    # A string annotation is already its name.
    if isinstance(annotation, str):
        return annotation

    # Prefer the type name, then the string form.
    return getattr(annotation, '__name__', str(annotation))

# ** function: ref_name
def ref_name(value: str, prefix: str) -> str | None:
    '''
    Return the legal name after a reference prefix, or null when invalid.

    :param value: The full reference string.
    :type value: str
    :param prefix: The reference prefix to strip.
    :type prefix: str
    :return: The remainder when it is a legal name, otherwise null.
    :rtype: str | None
    '''

    # Strip the prefix and require a full name match.
    remainder = value[len(prefix):]
    if REF_NAME.fullmatch(remainder) is None:
        return None

    # Return the legal remainder.
    return remainder

# ** function: compile_phase_steps
def compile_phase_steps(test: Test) -> List[EventFeatureStep]:
    '''
    Compile a test into conditions, execute, and assert feature steps.

    :param test: The test whose phases are compiled.
    :type test: Test
    :return: The ordered feature steps for the phase runtime.
    :rtype: List[EventFeatureStep]
    '''

    # Always start with the conditions step.
    steps: List[EventFeatureStep] = [
        EventFeatureStep(
            name='conditions',
            service_id=PHASE_CONDITIONS_ID,
        ),
    ]

    # Append one execute step per execution item.
    for index, execution in enumerate(test.executes):
        step_kwargs: Dict[str, Any] = {
            'name': f'execute_{index}',
            'service_id': PHASE_EXECUTE_ID,
        }
        if execution.data_key is not None:
            step_kwargs['data_key'] = execution.data_key
        steps.append(EventFeatureStep(**step_kwargs))

    # Append one assert step per assertion item.
    for index, _assertion in enumerate(test.asserts):
        steps.append(
            EventFeatureStep(
                name=f'assert_{index}',
                service_id=PHASE_ASSERT_ID,
            ),
        )

    # Return the compiled steps.
    return steps

# *** contexts

# ** context: phase_runtime_context
class PhaseRuntimeContext(BaseContext):
    '''
    Runs one test's phases against a bound ``PhaseRuntime``. The model names
    the tester class and the fixture specs. Built fixtures, arranged mocks,
    and ``as`` keys are run state on this context. Handlers take ``Conditions``,
    ``Execution``, and ``Assertion``. They are not dispatched through
    ``AppSessionContext``.
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
        Initialize the phase runtime context.

        :param session: The session whose data stores ``as`` results.
        :type session: RequestContext
        :param check: The injected check comparison collaborator.
        :type check: Any
        :return: None
        :rtype: None
        '''

        # Initialize the base context.
        super().__init__()

        # Store the session and injected check.
        self.session = session
        self.check = check

        # Start run state empty; from_domain binds the PhaseRuntime after.
        self.fixtures = {}
        self.mocks = {}
        self.as_keys = set()
        self.steps = []

    # * method: handle_conditions
    def handle_conditions(self, conditions: Conditions) -> None:
        '''
        Build fixtures then arrange mocks for one conditions phase.

        :param conditions: The conditions phase object.
        :type conditions: Conditions
        :return: None
        :rtype: None
        '''

        # Reject a non-Conditions argument.
        if not isinstance(conditions, Conditions):
            TiferetError.raise_error(
                a.error.PHASE_HANDLER_MISMATCH_ID,
                received=type(conditions).__name__,
                expected='Conditions',
            )

        # Reject mock names that overlap current or already-built fixtures.
        overlap = set(conditions.mocks) & (
            set(conditions.fixtures) | set(self.fixtures)
        )
        if overlap:
            TiferetError.raise_error(
                a.error.PHASE_NAME_COLLISION_ID,
                names=sorted(overlap),
            )

        # Build each fixture name in list order.
        for name in conditions.fixtures:
            self._build_fixture(name)

        # Arrange each mock after fixtures are available.
        for name, arranged in conditions.mocks.items():
            self._arrange_mock(name, arranged)

    # * method: handle_execution
    def handle_execution(self, execution: Execution) -> None:
        '''
        Invoke one execution phase item.

        :param execution: The execution phase object.
        :type execution: Execution
        :return: None
        :rtype: None
        '''

        # Reject a non-Execution argument.
        if not isinstance(execution, Execution):
            TiferetError.raise_error(
                a.error.PHASE_HANDLER_MISMATCH_ID,
                received=type(execution).__name__,
                expected='Execution',
            )

        # Invoke the execution.
        self._invoke(execution)

    # * method: handle_assertion
    def handle_assertion(self, assertion: Assertion) -> None:
        '''
        Resolve values and dispatch one assertion through a phase event.

        :param assertion: The assertion phase object.
        :type assertion: Assertion
        :return: None
        :rtype: None
        '''

        # Reject a non-Assertion argument.
        if not isinstance(assertion, Assertion):
            TiferetError.raise_error(
                a.error.PHASE_HANDLER_MISMATCH_ID,
                received=type(assertion).__name__,
                expected='Assertion',
            )

        # Reject equals whose equals is null before resolving.
        if assertion.check == 'equals' and assertion.equals is None:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='YAML null under equals is rejected.',
            )

        # Resolve values, then dispatch the named check event.
        resolved = self._resolved_assertion_values(assertion)
        check = assertion.check

        if check == 'domain_contract':
            ExerciseDomainContract(self.check).execute(assertion=assertion)
        elif check == 'mapper_contract':
            ExerciseMapperBases(self.check).execute(assertion=assertion)
        elif check == 'parameters_required':
            ExerciseParametersRequired(self.check).execute(assertion=assertion)
        elif check == 'service_contract':
            ExerciseServiceContract(self.check).execute(
                assertion=assertion,
                cls=resolved['cls'],
            )
        elif check == 'middleware_chain':
            ExerciseMiddlewareChain(self.check).execute(assertion=assertion)
        elif check == 'assert_called_once_with':
            ExerciseCalled(self.check).execute(
                assertion=assertion,
                method=resolved['method'],
                spec=resolved['spec'],
            )
        else:
            EvaluateAssertion(self.check).execute(
                assertion=assertion,
                values=resolved,
            )

    # * method: run
    def run(self, test: Test) -> List[EventFeatureStep]:
        '''
        Run conditions, executes, and asserts for one test.

        :param test: The test to run.
        :type test: Test
        :return: The compiled phase steps.
        :rtype: List[EventFeatureStep]
        '''

        # Reject a non-Test argument.
        if not isinstance(test, Test):
            TiferetError.raise_error(
                a.error.PHASE_HANDLER_MISMATCH_ID,
                received=type(test).__name__,
                expected='Test',
            )

        # Reject empty executes.
        if not test.executes:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='execute is a non-empty list.',
            )

        # Reject empty asserts.
        if not test.asserts:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='assert is a non-empty list.',
            )

        # Compile steps, then run each phase in order.
        self.steps = compile_phase_steps(test)
        self.handle_conditions(test.conditions)
        for execution in test.executes:
            self.handle_execution(execution)
        for assertion in test.asserts:
            self.handle_assertion(assertion)

        # Return the last compiled steps.
        return self.steps

    # * method: build_fixture
    def _build_fixture(self, name: str) -> None:
        '''
        Build one fixture from the bound phase runtime specs.

        :param name: The fixture name to build.
        :type name: str
        :return: None
        :rtype: None
        '''

        # Look up the fixture spec; null means not found.
        spec = self.domain.fixture_spec(name)
        if spec is None:
            TiferetError.raise_error(
                a.error.PHASE_FIXTURE_NOT_FOUND_ID,
                name=name,
            )

        # Import the fixture class and resolve its attributes.
        cls = self._require_named(spec['module_path'], spec['class_name'])
        attributes = self._resolve_value(
            _copy_data(spec['attributes']),
            allow_request=False,
        )

        # Store the constructed fixture.
        self.fixtures[name] = cls(**attributes)

    # * method: arrange_mock
    def _arrange_mock(self, name: str, arranged: Any) -> None:
        '''
        Arrange one mock from import coordinates and optional return values.

        :param name: The mock name to store.
        :type name: str
        :param arranged: The arranged mock specification.
        :type arranged: Any
        :return: None
        :rtype: None
        '''

        # Import the class to use as the mock spec without constructing it.
        cls = self._require_named(arranged.module_path, arranged.class_name)

        # Build a context-manager mock or a plain mock.
        if arranged.context:
            mock = MagicMock(spec=cls)

            # Spec-bound MagicMock omits context-manager magics; enable them.
            methods = set(mock._mock_methods or [])
            methods.update({'__enter__', '__exit__'})
            mock._mock_methods = methods
            mock._mock_set_magics()
            mock.__enter__.return_value = mock
            mock.__exit__.return_value = None
        else:
            mock = Mock(spec=cls)

        # Arrange each method when return_value is truthy.
        if arranged.return_value:
            for method_name, value in arranged.return_value.items():
                self._arrange_method(mock, method_name, value)

        # Store the arranged mock.
        self.mocks[name] = mock

    # * method: arrange_method
    def _arrange_method(
            self,
            mock: Mock,
            method_name: str,
            value: Any,
        ) -> None:
        '''
        Arrange one mock method return value or raises side effect.

        :param mock: The mock whose method is arranged.
        :type mock: Mock
        :param method_name: The method name to arrange.
        :type method_name: str
        :param value: The return value, attributes bag, or raises spec.
        :type value: Any
        :return: None
        :rtype: None
        '''

        # A raises dict is exclusive of every other key.
        if isinstance(value, dict) and 'raises' in value:
            if set(value) != {'raises'}:
                TiferetError.raise_error(
                    a.error.PHASE_STEP_FAILED_ID,
                    detail='return_value and raises are mutually exclusive.',
                )
            self._arrange_raises(mock, method_name, value['raises'])
            return

        # Attach a child when the spec omits this method name.
        try:
            method = getattr(mock, method_name)
        except AttributeError:
            method = Mock()
            setattr(mock, method_name, method)

        # An attributes bag becomes a SimpleNamespace return value.
        if isinstance(value, dict) and set(value) == {'attributes'}:
            attributes = self._resolve_value(
                _copy_data(value['attributes']),
                allow_request=False,
            )
            method.return_value = SimpleNamespace(**attributes)
            return

        # Any other value, including null, is a resolved return value.
        method.return_value = self._resolve_value(
            _copy_data(value),
            allow_request=False,
        )

    # * method: arrange_raises
    def _arrange_raises(
            self,
            mock: Mock,
            method_name: str,
            spec: Dict[str, Any],
        ) -> None:
        '''
        Arrange a mock method to raise an imported exception class.

        :param mock: The mock whose method raises.
        :type mock: Mock
        :param method_name: The method name to arrange.
        :type method_name: str
        :param spec: The raises specification mapping.
        :type spec: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # Require a closed raises mapping.
        if (
            not isinstance(spec, dict)
            or 'module_path' not in spec
            or 'class_name' not in spec
            or set(spec) - {'module_path', 'class_name', 'message'}
        ):
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail=(
                    'raises is module_path, class_name, and optional message.'
                ),
            )

        # Import the exception class.
        exc_cls = self._require_named(spec['module_path'], spec['class_name'])

        # Attach a child when the spec omits this method name.
        try:
            method = getattr(mock, method_name)
        except AttributeError:
            method = Mock()
            setattr(mock, method_name, method)

        # Null or absent message uses the class; any other message uses an instance.
        message = spec.get('message')
        if message is None:
            method.side_effect = exc_cls
        else:
            method.side_effect = exc_cls(message)

    # * method: resolve_value
    def _resolve_value(
            self,
            value: Any,
            allow_request: bool = True,
        ) -> Any:
        '''
        Resolve whole-value refs in a scalar, list, or mapping.

        :param value: The value to resolve.
        :type value: Any
        :param allow_request: Whether ``$r.`` refs are legal.
        :type allow_request: bool
        :return: The resolved value.
        :rtype: Any
        '''

        # Resolve a string scalar.
        if isinstance(value, str):
            return self._resolve_scalar(value, allow_request=allow_request)

        # Resolve each list item with the same flag.
        if isinstance(value, list):
            return [
                self._resolve_value(item, allow_request=allow_request)
                for item in value
            ]

        # Resolve each mapping value with the same flag.
        if isinstance(value, dict):
            return {
                key: self._resolve_value(item, allow_request=allow_request)
                for key, item in value.items()
            }

        # Reject a stored callable.
        if callable(value):
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='A stored callable is not legal.',
            )

        # Anything else, including null, is returned as-is.
        return value

    # * method: resolve_scalar
    def _resolve_scalar(
            self,
            value: str,
            allow_request: bool = True,
        ) -> Any:
        '''
        Resolve one whole-value reference string.

        :param value: The scalar string to resolve.
        :type value: str
        :param allow_request: Whether ``$r.`` refs are legal.
        :type allow_request: bool
        :return: The resolved value, or the literal string.
        :rtype: Any
        '''

        # Reject request refs when forbidden, before any name check.
        if value.startswith(REQUEST_REF_PREFIX) and not allow_request:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='$r. is illegal in conditions.',
            )

        # Whole-value fixture and mock refs look up the store.
        if value.startswith(FIXTURE_REF_PREFIX):
            return self._lookup_ref(value, FIXTURE_REF_PREFIX, self.fixtures)
        if value.startswith(MOCK_REF_PREFIX):
            return self._lookup_ref(value, MOCK_REF_PREFIX, self.mocks)

        # Whole-value request refs require an as key this context stored.
        if value.startswith(REQUEST_REF_PREFIX):
            name = ref_name(value, REQUEST_REF_PREFIX)
            if name is None:
                return value
            if name not in self.as_keys:
                TiferetError.raise_error(
                    a.error.PHASE_REFERENCE_NOT_FOUND_ID,
                    reference=value,
                )
            return self.session.data[name]

        # A prefix inside a longer string is a literal.
        return value

    # * method: lookup_ref
    def _lookup_ref(
            self,
            value: str,
            prefix: str,
            store: Dict[str, Any],
        ) -> Any:
        '''
        Look up a whole-value fixture or mock reference.

        :param value: The full reference scalar.
        :type value: str
        :param prefix: The reference prefix.
        :type prefix: str
        :param store: The fixture or mock store.
        :type store: Dict[str, Any]
        :return: The stored value.
        :rtype: Any
        '''

        # Require a legal name after the prefix.
        name = self._ref_name(value, prefix)

        # Raise when the name is missing from the store.
        if name not in store:
            TiferetError.raise_error(
                a.error.PHASE_REFERENCE_NOT_FOUND_ID,
                reference=value,
            )

        # Return the stored value.
        return store[name]

    # * method: ref_name
    def _ref_name(self, value: str, prefix: str) -> str:
        '''
        Return the legal name after a reference prefix.

        :param value: The full reference scalar.
        :type value: str
        :param prefix: The reference prefix.
        :type prefix: str
        :return: The legal remainder name.
        :rtype: str
        '''

        # Reject an illegal remainder as a step failure.
        name = ref_name(value, prefix)
        if name is None:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail=f'{value} is not a runtime reference.',
            )

        # Return the legal name.
        return name

    # * method: invoke
    def _invoke(self, execution: Execution) -> None:
        '''
        Call one execution and store the result or caught exception.

        :param execution: The execution to invoke.
        :type execution: Execution
        :return: None
        :rtype: None
        '''

        # Call the target; catch when raises is expected.
        try:
            result = self._call(execution)
        except Exception as error:
            if not execution.raises:
                raise
            self._store(execution.data_key, error)
            return

        # raises true with a normal return is a step failure.
        if execution.raises:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='A step marked raises did not raise.',
            )

        # Store a normal return only when data_key is truthy.
        if execution.data_key:
            self._store(execution.data_key, result)

    # * method: call
    def _call(self, execution: Execution) -> Any:
        '''
        Resolve arguments and call the execution target.

        :param execution: The execution to call.
        :type execution: Execution
        :return: The call result.
        :rtype: Any
        '''

        # Resolve args and kwargs before branching on the method.
        args = self._resolve_value(execution.args, allow_request=True)
        kwargs = self._resolve_value(execution.kwargs, allow_request=True)

        # Reserved new constructs the tester class.
        if execution.method == 'new':
            return self._call_new()

        # Reserved handle injects constructor mocks into DomainEvent.handle.
        if execution.method == 'handle':
            return self._call_handle(kwargs)

        # Resolve the call target.
        target = self._resolve_target(execution)

        # self is legal only for the reserved methods above.
        if target == 'self':
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail='self is legal only for new and handle.',
            )

        # A module attribute target must call that attribute directly.
        if (
            isinstance(execution.target, ExecutionTarget)
            and execution.target.attribute is not None
        ):
            if execution.method != execution.target.attribute:
                TiferetError.raise_error(
                    a.error.PHASE_STEP_FAILED_ID,
                    detail='A module attribute target calls that attribute.',
                )
            return target(*args, **kwargs)

        # A class or fixture target uses getattr for the method.
        return getattr(target, execution.method)(*args, **kwargs)

    # * method: call_new
    def _call_new(self) -> Any:
        '''
        Construct the tester class from the bound phase runtime coordinates.

        :return: The constructed tester instance.
        :rtype: Any
        '''

        # Import the tester class and resolve its attributes.
        cls = self._require_named(
            self.domain.tester_module_path,
            self.domain.tester_class_name,
        )
        attributes = self._resolve_value(
            _copy_data(self.domain.tester_attributes),
            allow_request=True,
        )

        # Construct the class directly; do not call a method named new.
        return cls(**attributes)

    # * method: call_handle
    def _call_handle(self, kwargs: Dict[str, Any]) -> Any:
        '''
        Handle a domain event with constructor mocks as dependencies.

        :param kwargs: The resolved event keyword arguments.
        :type kwargs: Dict[str, Any]
        :return: The event handle result.
        :rtype: Any
        '''

        # Import the tester event class.
        cls = self._require_named(
            self.domain.tester_module_path,
            self.domain.tester_class_name,
        )

        # Build dependencies from init parameters or all mocks for **kwargs.
        signature = inspect.signature(cls.__init__)
        parameters = list(signature.parameters.values())
        if any(
            parameter.kind is inspect.Parameter.VAR_KEYWORD
            for parameter in parameters
        ):
            dependencies = dict(self.mocks)
        else:
            names = {
                parameter.name
                for parameter in parameters
                if parameter.name != 'self'
            }
            dependencies = {
                name: mock
                for name, mock in self.mocks.items()
                if name in names
            }

        # Handle the event; step kwargs are event arguments.
        return DomainEvent.handle(
            cls,
            dependencies=dependencies,
            **kwargs,
        )

    # * method: resolve_target
    def _resolve_target(self, execution: Execution) -> Any:
        '''
        Resolve the call target for one execution.

        :param execution: The execution whose target is resolved.
        :type execution: Execution
        :return: The resolved target object.
        :rtype: Any
        '''

        # An import target loads a class or module attribute.
        target = execution.target
        if isinstance(target, ExecutionTarget):
            if target.class_name is not None:
                return self._require_named(target.module_path, target.class_name)
            return self._require_named(target.module_path, target.attribute)

        # The string self returns the string self.
        if target == 'self':
            return 'self'

        # A whole-value ref resolves through the scalar path.
        if (
            isinstance(target, str)
            and (
                target.startswith(FIXTURE_REF_PREFIX)
                or target.startswith(MOCK_REF_PREFIX)
                or target.startswith(REQUEST_REF_PREFIX)
            )
        ):
            return self._resolve_scalar(target, allow_request=True)

        # A bare fixture name returns that fixture.
        if isinstance(target, str) and target in self.fixtures:
            return self.fixtures[target]

        # A bare name is not an as key.
        TiferetError.raise_error(
            a.error.PHASE_STEP_FAILED_ID,
            detail=(
                f'Target {target} is not a fixture. '
                f'A bare name is not a prior as key.'
            ),
        )

    # * method: store
    def _store(self, data_key: str, result: Any) -> None:
        '''
        Store a result on the session and record the as key.

        :param data_key: The session data key.
        :type data_key: str
        :param result: The value to store.
        :type result: Any
        :return: None
        :rtype: None
        '''

        # Write through the session, then track the as key.
        self.session.set_result(result, data_key=data_key)
        self.as_keys.add(data_key)

    # * method: resolve_outcome
    def _resolve_outcome(self, outcome: str) -> Any:
        '''
        Resolve an assertion outcome name from as keys or fixtures.

        :param outcome: The outcome name or ``$r.`` reference.
        :type outcome: str
        :return: The resolved outcome value.
        :rtype: Any
        '''

        # A $r. outcome takes its name from the reference remainder.
        if outcome.startswith(REQUEST_REF_PREFIX):
            name = self._ref_name(outcome, REQUEST_REF_PREFIX)
            scalar = outcome
        else:
            name = outcome
            scalar = None

        # Reject a name that is both an as key and a fixture.
        if name in self.as_keys and name in self.fixtures:
            TiferetError.raise_error(
                a.error.PHASE_NAME_COLLISION_ID,
                names=name,
            )

        # A $r. outcome must be an as key this context stored.
        if scalar is not None:
            if name not in self.as_keys:
                TiferetError.raise_error(
                    a.error.PHASE_REFERENCE_NOT_FOUND_ID,
                    reference=scalar,
                )
            return self.session.data[name]

        # Prefer an as key, then a fixture name.
        if name in self.as_keys:
            return self.session.data[name]
        if name in self.fixtures:
            return self.fixtures[name]

        # Raise when the bare name is missing.
        TiferetError.raise_error(
            a.error.PHASE_REFERENCE_NOT_FOUND_ID,
            reference=name,
        )

    # * method: require_named
    def _require_named(self, module_path: str, name: str) -> Any:
        '''
        Import a named attribute or raise a step failure.

        :param module_path: The module path to import.
        :type module_path: str
        :param name: The attribute name to load.
        :type name: str
        :return: The imported attribute.
        :rtype: Any
        '''

        # Import the attribute; null is a step failure.
        value = import_named(module_path, name)
        if value is None:
            TiferetError.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail=f'{module_path} has no {name}.',
            )

        # Return the imported attribute.
        return value

    # * method: resolved_assertion_values
    def _resolved_assertion_values(
            self,
            assertion: Assertion,
        ) -> Dict[str, Any]:
        '''
        Resolve the values one assertion event needs.

        :param assertion: The assertion whose values are resolved.
        :type assertion: Assertion
        :return: The resolved values mapping for the event.
        :rtype: Dict[str, Any]
        '''

        # Only fields this check names are resolved.
        named = set(assertion.value_fields())
        resolved: Dict[str, Any] = {}

        # Resolve outcome, equals, and fields when named and not null.
        if 'outcome' in named and assertion.outcome is not None:
            resolved['outcome'] = self._resolve_outcome(assertion.outcome)
        if 'equals' in named and assertion.equals is not None:
            resolved['equals'] = self._resolve_value(assertion.equals)
        if 'fields' in named and assertion.fields is not None:
            resolved['fields'] = self._resolve_value(assertion.fields)

        # error_code reads the outcome attribute when present.
        if assertion.check == 'error_code':
            outcome = resolved.get('outcome')
            has_error_code = hasattr(outcome, 'error_code')
            resolved['has_error_code'] = has_error_code
            if has_error_code:
                resolved['error_code'] = outcome.error_code

        # type, cause, and is without builtin import the named class.
        if assertion.check in ('type', 'cause') or (
            assertion.check == 'is' and assertion.builtin is None
        ):
            cls = self._require_named(
                assertion.module_path,
                assertion.class_name,
            )
            resolved['cls'] = cls
            if assertion.check == 'is':
                resolved['expected'] = cls

        # is with builtin uses the builtin type map.
        if assertion.check == 'is' and assertion.builtin is not None:
            resolved['expected'] = BUILTIN_TYPES[assertion.builtin]

        # assert_called_once_with resolves the mock method and call spec.
        if assertion.check == 'assert_called_once_with':
            if assertion.mock not in self.mocks:
                TiferetError.raise_error(
                    a.error.PHASE_REFERENCE_NOT_FOUND_ID,
                    reference=assertion.mock,
                )
            mock = self.mocks[assertion.mock]
            if assertion.method == '__call__':
                resolved['method'] = mock
            else:
                resolved['method'] = getattr(mock, assertion.method)
            spec = self._resolve_value(assertion.assert_called_once_with)
            if (
                isinstance(spec, dict)
                and spec.get('times') == 0
                and ('args' in spec or 'kwargs' in spec)
            ):
                TiferetError.raise_error(
                    a.error.PHASE_STEP_FAILED_ID,
                    detail='times 0 requires args to be omitted.',
                )
            resolved['spec'] = spec

        # event_base imports the tester class and the named base.
        if assertion.check == 'event_base':
            resolved['event_cls'] = self._require_named(
                self.domain.tester_module_path,
                self.domain.tester_class_name,
            )
            resolved['base_cls'] = self._require_named(
                assertion.module_path,
                assertion.class_name,
            )
            resolved['mocks'] = dict(self.mocks)

        # service_contract imports the tester class as the service under lock.
        if assertion.check == 'service_contract':
            resolved['cls'] = self._require_named(
                self.domain.tester_module_path,
                self.domain.tester_class_name,
            )

        # Return the resolved values; the event does not see the session.
        return resolved

# ** context: test_context
class TestContext(FeatureContext):
    '''
    The session's view of one test. It extends ``FeatureContext`` so a test
    runs as a feature, and it declares ``domain_type = Test`` in its own
    namespace so ``Feature`` stays mapped to ``FeatureContext``. The phase
    runtime is not built here. The tester blueprint injects
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
    def __init__(
            self,
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
        Initialize the test context with an injected phase-runtime factory.

        :param get_dependency: The service-resolution handler.
        :type get_dependency: Callable
        :param build_phase_runtime_handler: The injected phase-runtime factory.
        :type build_phase_runtime_handler: Callable
        :param phase_runtime_slot: Shared slot the step resolver reads.
        :type phase_runtime_slot: Dict[str, Any]
        :param tester_module_path: Tester class module path.
        :type tester_module_path: str
        :param tester_class_name: Tester class name.
        :type tester_class_name: str
        :param tester_attributes: Attributes ``new`` uses.
        :type tester_attributes: Dict[str, Any]
        :param root_fixtures: Root fixture specs.
        :type root_fixtures: Dict[str, Dict[str, Any]]
        :param tester_fixtures: Tester-local fixture specs.
        :type tester_fixtures: Dict[str, Dict[str, Any]]
        :param kwargs: Passed through to ``FeatureContext``.
        :type kwargs: dict
        :return: None
        :rtype: None
        '''

        # Pass get_dependency and remaining kwargs to FeatureContext.
        super().__init__(get_dependency, **kwargs)

        # Store the injected factory; null means unwired.
        self._build_phase_runtime = build_phase_runtime_handler

        # Store the given slot object, or a new empty dict.
        self._phase_runtime_slot = (
            phase_runtime_slot if phase_runtime_slot is not None else {}
        )

        # Store tester coordinates, using empty mappings when null.
        self._tester_module_path = tester_module_path
        self._tester_class_name = tester_class_name
        self._tester_attributes = (
            tester_attributes if tester_attributes is not None else {}
        )
        self._root_fixtures = (
            root_fixtures if root_fixtures is not None else {}
        )
        self._tester_fixtures = (
            tester_fixtures if tester_fixtures is not None else {}
        )

    # * method: build_phase_runtime
    def build_phase_runtime(
            self,
            session,
            tester_module_path,
            tester_class_name,
            *,
            tester_attributes=None,
            root_fixtures=None,
            tester_fixtures=None,
        ):
        '''
        Delegate phase-runtime construction to the injected factory.

        :param session: The request session for the phase run.
        :type session: Any
        :param tester_module_path: The tester class module path.
        :type tester_module_path: str
        :param tester_class_name: The tester class name.
        :type tester_class_name: str
        :param tester_attributes: Attributes ``new`` uses.
        :type tester_attributes: dict | None
        :param root_fixtures: Root fixture specs.
        :type root_fixtures: dict | None
        :param tester_fixtures: Tester-local fixture specs.
        :type tester_fixtures: dict | None
        :return: The injected factory result.
        :rtype: Any
        '''

        # An absent factory is an unwired handler.
        if self._build_phase_runtime is None:
            a.core.raise_unwired_handler_error(
                'build_phase_runtime_handler',
                self.domain.id,
                error_code=a.error.APP_ERROR_ID,
            )

        # Delegate to the injected factory without reading stored coordinates.
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
        Build the phase runtime, fill the slot, then run the bound test feature.

        :param request: The request context for the test run.
        :type request: RequestContext
        :param flags: Execution flags passed through to FeatureContext.
        :type flags: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The FeatureContext execution result.
        :rtype: Any
        '''

        # Build the phase runtime from the stored coordinates.
        runtime = self.build_phase_runtime(
            request,
            self._tester_module_path,
            self._tester_class_name,
            tester_attributes=self._tester_attributes,
            root_fixtures=self._root_fixtures,
            tester_fixtures=self._tester_fixtures,
        )

        # Fill the shared slot before the feature loop runs.
        self._phase_runtime_slot['runtime'] = runtime

        # Run the bound Test as a feature and return that result.
        return super().execute_feature(request, *flags, **kwargs)
