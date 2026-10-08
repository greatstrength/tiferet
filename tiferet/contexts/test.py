"""Tiferet Test Contexts"""

# *** imports

# ** core
import inspect
import re
from importlib import import_module
from types import SimpleNamespace
from typing import Any, Dict, List, Mapping, Tuple

# ** infra
from pydantic import Field, ValidationError
from unittest.mock import Mock, call

# ** app
from .core import BaseContext
from .feature import FeatureContext, run_coroutine
from .request import RequestContext
from .. import a
from ..assets import TiferetError
from ..assets.core import REQUEST_REF_PREFIX
from ..domain import (
    INVALID_MODEL_ATTRIBUTE_ID,
    INVALID_MODEL_VALUE_ID,
    DomainObject,
    EventFeatureStep,
    ModelError,
    describe_model,
    unpack_validation_error,
)
from ..domain.test import (
    Assertion,
    Conditions,
    Execution,
    ExecutionTarget,
    Test,
)
from ..events import AsyncDomainEvent, DomainEvent
from ..events.phase import run_mapper_contract

# *** constants

# ** constant: fixture_ref_prefix
FIXTURE_REF_PREFIX = '$fixture.'

# ** constant: mock_ref_prefix
MOCK_REF_PREFIX = '$mock.'

# ** constant: python_tag
PYTHON_TAG = '!!python/'

# ** constant: ref_name
REF_NAME = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

# ** constant: conditions_keys
CONDITIONS_KEYS: Tuple[str, ...] = (
    'fixtures',
    'mocks',
)

# ** constant: execute_keys
EXECUTE_KEYS: Tuple[str, ...] = (
    'target',
    'method',
    'args',
    'kwargs',
    'as',
    'raises',
)

# ** constant: fixture_spec_keys
FIXTURE_SPEC_KEYS: Tuple[str, ...] = (
    'module_path',
    'class_name',
    'attributes',
)

# ** constant: mock_spec_keys
MOCK_SPEC_KEYS: Tuple[str, ...] = (
    'module_path',
    'class_name',
    'context',
    'return_value',
)

# ** constant: import_keys
IMPORT_KEYS: Tuple[str, ...] = (
    'module_path',
    'class_name',
)

# ** constant: call_spec_keys
CALL_SPEC_KEYS: Tuple[str, ...] = (
    'args',
    'kwargs',
    'times',
    'calls',
)

# ** constant: data_checks
DATA_CHECKS: Tuple[str, ...] = (
    'equals',
    'null',
    'fields',
    'absent',
    'error_code',
    'type',
    'is',
    'message',
    'assert_called_once_with',
)

# ** constant: harness_checks
HARNESS_CHECKS: Tuple[str, ...] = (
    'domain_contract',
    'mapper_contract',
    'event_base',
    'parameters_required',
    'service_contract',
    'middleware_chain',
    'cause',
)

# ** constant: illegal_keys
ILLEGAL_KEYS: Tuple[str, ...] = (
    'predicate',
    'field_normalizers',
    'side_effect',
    'eval',
    'code',
    'python',
    'body',
    'contains',
    'any',
    'target_method',
    'abstract_methods',
    'subclass_of',
)

# ** constant: phase_conditions_id
PHASE_CONDITIONS_ID = 'phase_conditions'

# ** constant: phase_execute_id
PHASE_EXECUTE_ID = 'phase_execute'

# ** constant: phase_assert_id
PHASE_ASSERT_ID = 'phase_assert'

# ** constant: middleware_chains
MIDDLEWARE_CHAINS: Tuple[str, ...] = (
    'none',
    'single',
    'order',
    'capture',
    'intercept',
    'async',
)

# ** constant: reserved_methods
RESERVED_METHODS: Tuple[str, ...] = (
    'new',
    'handle',
)

# ** constant: builtin_types
BUILTIN_TYPES: Dict[str, type] = {
    'int': int,
    'str': str,
    'float': float,
    'bool': bool,
    'list': list,
    'dict': dict,
}

# ** constant: assertion_yaml_fields
ASSERTION_YAML_FIELDS: Dict[str, Dict[str, Tuple[str, ...]]] = {
    'equals': {
        'required': (
            'outcome',
            'equals',
        ),
        'allowed': (
            'outcome',
            'equals',
        ),
    },
    'null': {
        'required': (
            'outcome',
            'null',
        ),
        'allowed': (
            'outcome',
            'null',
        ),
    },
    'fields': {
        'required': (
            'outcome',
            'fields',
        ),
        'allowed': (
            'outcome',
            'fields',
        ),
    },
    'absent': {
        'required': (
            'outcome',
            'absent',
        ),
        'allowed': (
            'outcome',
            'absent',
        ),
    },
    'error_code': {
        'required': (
            'outcome',
            'error_code',
        ),
        'allowed': (
            'outcome',
            'error_code',
        ),
    },
    'type': {
        'required': (
            'outcome',
            'type',
        ),
        'allowed': (
            'outcome',
            'type',
            'negate',
        ),
    },
    'is': {
        'required': (
            'outcome',
            'is',
        ),
        'allowed': (
            'outcome',
            'is',
        ),
    },
    'message': {
        'required': (
            'outcome',
            'message',
        ),
        'allowed': (
            'outcome',
            'message',
        ),
    },
    'assert_called_once_with': {
        'required': (
            'mock',
            'method',
            'assert_called_once_with',
        ),
        'allowed': (
            'mock',
            'method',
            'assert_called_once_with',
        ),
    },
    'domain_contract': {
        'required': (
            'domain_contract',
        ),
        'allowed': (
            'domain_contract',
        ),
    },
    'mapper_contract': {
        'required': (
            'mapper_contract',
        ),
        'allowed': (
            'mapper_contract',
            'exclude',
        ),
    },
    'event_base': {
        'required': (
            'event_base',
        ),
        'allowed': (
            'event_base',
        ),
    },
    'parameters_required': {
        'required': (
            'parameters_required',
        ),
        'allowed': (
            'parameters_required',
        ),
    },
    'service_contract': {
        'required': (
            'service_contract',
        ),
        'allowed': (
            'service_contract',
        ),
    },
    'middleware_chain': {
        'required': (
            'middleware_chain',
        ),
        'allowed': (
            'middleware_chain',
        ),
    },
    'cause': {
        'required': (
            'outcome',
            'cause',
        ),
        'allowed': (
            'outcome',
            'cause',
        ),
    },
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

    # Import the module, then the named attribute.
    module = import_module(module_path)
    if not hasattr(module, name):
        raise ValueError(f'{module_path} has no {name}.')
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

# ** function: reject_illegal_keys
def _reject_illegal_keys(mapping: Dict[str, Any]) -> None:
    '''
    Reject an illegal check key, even when its value is data.

    :param mapping: The phase mapping.
    :type mapping: Dict[str, Any]
    :return: None.
    :rtype: None
    '''

    # These keys are not checks. A data value does not make them legal.
    found = set(mapping) & set(ILLEGAL_KEYS)
    if found:
        raise ValueError(f'Illegal phase key {sorted(found)}.')

# ** function: reject_python_tags
def _reject_python_tags(value: Any) -> None:
    '''
    Reject a YAML Python tag or a stored callable.

    :param value: The value to walk.
    :type value: Any
    :return: None.
    :rtype: None
    '''

    # A tag or a callable is a Python body. Data is not.
    if isinstance(value, str) and PYTHON_TAG in value:
        raise ValueError('A YAML Python tag is not legal.')
    if isinstance(value, dict):
        for item in value.values():
            _reject_python_tags(item)
        return
    if isinstance(value, list):
        for item in value:
            _reject_python_tags(item)
        return
    if callable(value):
        raise ValueError('A stored callable is not legal.')

# ** function: require_import_spec
def _require_import_spec(spec: Any, label: str) -> None:
    '''
    Require a mapping of module_path and class_name.

    :param spec: The candidate import mapping.
    :type spec: Any
    :param label: The check name used in the failure.
    :type label: str
    :return: None.
    :rtype: None
    '''

    # The import is two strings, not a class body.
    if not isinstance(spec, dict) or set(spec) != set(IMPORT_KEYS):
        raise ValueError(f'{label} is module_path and class_name.')
    if not isinstance(spec['module_path'], str) or not isinstance(spec['class_name'], str):
        raise ValueError(f'{label} names a class by string.')

# ** function: validate_conditions_mapping
def validate_conditions_mapping(mapping: Dict[str, Any]) -> None:
    '''
    Reject a conditions mapping outside the closed key set.

    :param mapping: The conditions mapping.
    :type mapping: Dict[str, Any]
    :return: None.
    :rtype: None
    '''

    # conditions is a mapping of fixtures and mocks, or empty.
    if not isinstance(mapping, dict):
        raise ValueError('conditions is a mapping.')
    _reject_illegal_keys(mapping)
    _reject_python_tags(mapping)
    unknown = set(mapping) - set(CONDITIONS_KEYS)
    if unknown:
        raise ValueError(f'conditions does not allow {sorted(unknown)}.')

    # Fixture names are a list. Mock specs are a mapping.
    if 'fixtures' in mapping and not isinstance(mapping['fixtures'], list):
        raise ValueError('fixtures is a list of names.')
    if 'mocks' not in mapping:
        return
    if not isinstance(mapping['mocks'], dict):
        raise ValueError('mocks is a mapping.')
    for spec in mapping['mocks'].values():
        if not isinstance(spec, dict) or not set(spec) <= set(MOCK_SPEC_KEYS):
            raise ValueError('A mock is module_path, class_name, and optional return_value.')
        if 'module_path' not in spec or 'class_name' not in spec:
            raise ValueError('A mock requires module_path and class_name.')

# ** function: validate_execution_mapping
def validate_execution_mapping(mapping: Dict[str, Any]) -> None:
    '''
    Reject an execute item outside the closed key set.

    :param mapping: The execute item.
    :type mapping: Dict[str, Any]
    :return: None.
    :rtype: None
    '''

    # An execute item names a target and a method, and nothing else.
    if not isinstance(mapping, dict):
        raise ValueError('An execute item is a mapping.')
    _reject_illegal_keys(mapping)
    _reject_python_tags(mapping)
    unknown = set(mapping) - set(EXECUTE_KEYS)
    if unknown:
        raise ValueError(f'An execute item does not allow {sorted(unknown)}.')
    if 'target' not in mapping or 'method' not in mapping:
        raise ValueError('An execute item requires target and method.')
    if mapping.get('raises') not in (None, True, False):
        raise ValueError('raises is true or false.')
    if mapping.get('raises') is True and 'as' not in mapping:
        raise ValueError('raises requires as.')

# ** function: validate_execute_phase
def validate_execute_phase(items: List[Dict[str, Any]]) -> None:
    '''
    Reject an execute phase that is empty or contains an illegal item.

    :param items: The execute phase.
    :type items: List[Dict[str, Any]]
    :return: None.
    :rtype: None
    '''

    # execute is a non-empty list of closed items.
    if not isinstance(items, list) or not items:
        raise ValueError('execute is a non-empty list.')
    for item in items:
        validate_execution_mapping(item)

# ** function: validate_check_value
def _validate_check_value(check: str, mapping: Dict[str, Any]) -> None:
    '''
    Reject a check value that is not the closed form for that check.

    :param check: The check key.
    :type check: str
    :param mapping: The assert item.
    :type mapping: Dict[str, Any]
    :return: None.
    :rtype: None
    '''

    # Boolean checks accept only true.
    if check in ('null', 'domain_contract', 'mapper_contract'):
        if mapping[check] is not True:
            raise ValueError(f'{check} accepts only true.')

    # equals null is the null check, not an expected value.
    if check == 'equals' and mapping['equals'] is None:
        raise ValueError('YAML null under equals is rejected.')

    # type and event_base name one imported class.
    if check == 'type':
        _require_import_spec(mapping['type'], 'type')
    if check == 'event_base':
        _require_import_spec(mapping['event_base'], 'event_base')

    # is is an import or a builtin, not both.
    if check == 'is':
        spec = mapping['is']
        if not isinstance(spec, dict):
            raise ValueError('is names a class or a builtin.')
        if set(spec) == {'builtin'}:
            if spec['builtin'] not in BUILTIN_TYPES:
                raise ValueError('is builtin is not a legal live type.')
        elif set(spec) == set(IMPORT_KEYS):
            _require_import_spec(spec, 'is')
        else:
            raise ValueError('is requires module_path and class_name, or builtin, not both.')

    # cause names the chained exception. It is not a frame walk.
    if check == 'cause':
        spec = mapping['cause']
        if not isinstance(spec, dict) or set(spec) != {'module_path', 'class_name', 'message'}:
            raise ValueError('cause is module_path, class_name, and message.')

    # parameters_required is the decorator matrix, not a second error_code.
    if check == 'parameters_required':
        spec = mapping['parameters_required']
        if not isinstance(spec, dict) or set(spec) != {'names'} or not isinstance(spec['names'], list):
            raise ValueError('parameters_required is {names: [...]}.' )

    # service_contract locks a table. abstract_methods is not the key.
    if check == 'service_contract':
        spec = mapping['service_contract']
        if not isinstance(spec, dict):
            raise ValueError('service_contract is a mapping.')
        unknown = set(spec) - {'abstracts', 'methods', 'absent'}
        if unknown or 'abstracts' not in spec or 'methods' not in spec:
            raise ValueError('service_contract takes abstracts, methods, and optional absent.')

    # middleware_chain is one of the harness shapes. There is no async phase key.
    if check == 'middleware_chain' and mapping['middleware_chain'] not in MIDDLEWARE_CHAINS:
        raise ValueError('middleware_chain is not a legal shape.')

    # An exclude set is a list. No YAML set.
    if check == 'mapper_contract' and 'exclude' in mapping:
        if isinstance(mapping['exclude'], set) or not isinstance(mapping['exclude'], list):
            raise ValueError('An exclude set is a list. No YAML set.')

    # times 0 cannot carry args.
    if check == 'assert_called_once_with':
        spec = mapping['assert_called_once_with']
        if not isinstance(spec, dict) or not set(spec) <= set(CALL_SPEC_KEYS):
            raise ValueError('assert_called_once_with is args, kwargs, times, or calls.')
        if spec.get('times') == 0 and ('args' in spec or 'kwargs' in spec):
            raise ValueError('times 0 requires args to be omitted.')

# ** function: validate_assertion_mapping
def validate_assertion_mapping(mapping: Dict[str, Any]) -> None:
    '''
    Reject an assert item that does not have exactly one closed check.

    :param mapping: The assert item.
    :type mapping: Dict[str, Any]
    :return: None.
    :rtype: None
    '''

    # Exactly one data check or one harness check.
    if not isinstance(mapping, dict):
        raise ValueError('An assert item is a mapping.')
    _reject_illegal_keys(mapping)
    _reject_python_tags(mapping)
    checks = [
        key
        for key in mapping
        if key in DATA_CHECKS or key in HARNESS_CHECKS
    ]
    if len(checks) != 1:
        raise ValueError('An assert item has exactly one check key.')
    check = checks[0]
    allowed = set(ASSERTION_YAML_FIELDS[check]['allowed'])
    unknown = set(mapping) - allowed
    if unknown:
        raise ValueError(f'Check {check} does not allow {sorted(unknown)}.')
    missing = set(ASSERTION_YAML_FIELDS[check]['required']) - set(mapping)
    if missing:
        raise ValueError(f'Check {check} requires {sorted(missing)}.')
    _validate_check_value(check, mapping)

# ** function: validate_assert_phase
def validate_assert_phase(items: List[Dict[str, Any]]) -> None:
    '''
    Reject an assert phase that is empty or contains an illegal item.

    :param items: The assert phase.
    :type items: List[Dict[str, Any]]
    :return: None.
    :rtype: None
    '''

    # assert is a non-empty list of closed items.
    if not isinstance(items, list) or not items:
        raise ValueError('assert is a non-empty list.')
    for item in items:
        validate_assertion_mapping(item)

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

# ** context: phase_runtime
class PhaseRuntime(BaseContext):
    '''
    Runs one test's phases. The handlers take Conditions, Execution, and
    Assertion. They are not dispatched through AppSessionContext.
    '''

    # * attribute: session
    session: RequestContext

    # * attribute: fixtures
    fixtures: Dict[str, Any]

    # * attribute: mocks
    mocks: Dict[str, Mock]

    # * attribute: as_keys
    as_keys: set

    # * init
    def __init__(self,
            session: RequestContext,
            tester_module_path: str,
            tester_class_name: str,
            tester_attributes: Dict[str, Any] = None,
            root_fixtures: Dict[str, Dict[str, Any]] = None,
            tester_fixtures: Dict[str, Dict[str, Any]] = None,
        ) -> None:
        '''
        Initialize a phase runtime for one test.

        :param session: The session whose data stores ``as`` results.
        :type session: RequestContext
        :param tester_module_path: The tester class module.
        :type tester_module_path: str
        :param tester_class_name: The tester class name.
        :type tester_class_name: str
        :param tester_attributes: Attributes used by ``new``.
        :type tester_attributes: Dict[str, Any]
        :param root_fixtures: Root fixture specs, looked up after tester-local.
        :type root_fixtures: Dict[str, Dict[str, Any]]
        :param tester_fixtures: Tester-local fixture specs.
        :type tester_fixtures: Dict[str, Dict[str, Any]]
        :return: None.
        :rtype: None
        '''

        # Do not register a domain type. Test stays mapped to TestContext.
        super().__init__()

        # Hold the session and the tester coordinates the reserved actions use.
        self.session = session
        self.tester_module_path = tester_module_path
        self.tester_class_name = tester_class_name
        self.tester_attributes = tester_attributes or {}
        self.root_fixtures = root_fixtures or {}
        self.tester_fixtures = tester_fixtures or {}

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
            raise ValueError('Handlers take Conditions, not a dict.')

        # A mock name and a fixture name must not collide.
        overlap = set(conditions.mocks) & (set(conditions.fixtures) | set(self.fixtures))
        if overlap:
            raise ValueError(f'Mock and fixture names collide: {sorted(overlap)}.')

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
            raise ValueError('Handlers take Execution, not a dict.')
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
            raise ValueError('Handlers take Assertion, not a dict.')
        checker = {
            'equals': self._check_equals,
            'null': self._check_null,
            'fields': self._check_fields,
            'absent': self._check_absent,
            'error_code': self._check_error_code,
            'type': self._check_type,
            'is': self._check_is,
            'message': self._check_message,
            'assert_called_once_with': self._check_called,
            'domain_contract': self._check_domain_contract,
            'mapper_contract': self._check_mapper_contract,
            'event_base': self._check_event_base,
            'parameters_required': self._check_parameters_required,
            'service_contract': self._check_service_contract,
            'middleware_chain': self._check_middleware_chain,
            'cause': self._check_cause,
        }[assertion.check]
        checker(assertion)

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
            raise ValueError('A test is a Test, not a dict.')
        if not test.executes:
            raise ValueError('execute is a non-empty list.')
        if not test.asserts:
            raise ValueError('assert is a non-empty list.')

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

        # Tester-local wins. A tester-local fixture is not promoted.
        if name in self.tester_fixtures:
            spec = self.tester_fixtures[name]
        elif name in self.root_fixtures:
            spec = self.root_fixtures[name]
        else:
            raise ValueError(f'Fixture {name} was not found.')
        if set(spec) != set(FIXTURE_SPEC_KEYS):
            raise ValueError('A fixture entry is module_path, class_name, and attributes.')

        # Call the class. Do not call a method named new.
        cls = import_named(spec['module_path'], spec['class_name'])
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
        cls = import_named(arranged.module_path, arranged.class_name)
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
            raise ValueError('return_value and raises are mutually exclusive.')
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
            raise ValueError('raises is module_path, class_name, and optional message.')
        if set(spec) - {'module_path', 'class_name', 'message'}:
            raise ValueError('raises is module_path, class_name, and optional message.')
        exc_cls = import_named(spec['module_path'], spec['class_name'])
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
            raise ValueError('A stored callable is not legal.')
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
            raise ValueError('$r. is illegal in conditions.')
        if value.startswith(FIXTURE_REF_PREFIX):
            return self._lookup_ref(value, FIXTURE_REF_PREFIX, self.fixtures)
        if value.startswith(MOCK_REF_PREFIX):
            return self._lookup_ref(value, MOCK_REF_PREFIX, self.mocks)
        if value.startswith(REQUEST_REF_PREFIX):
            name = self._ref_name(value, REQUEST_REF_PREFIX)
            if name not in self.as_keys:
                raise ValueError(f'Missing runtime reference {value}.')
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
            raise ValueError(f'Missing runtime reference {value}.')
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

        # $r.built.lang is not a path.
        name = value[len(prefix):]
        if not REF_NAME.fullmatch(name):
            raise ValueError(f'{value} is not a runtime reference.')
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
            raise AssertionError('A step marked raises did not raise.')
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
            raise ValueError('self is legal only for new and handle.')
        if isinstance(execution.target, ExecutionTarget) and execution.target.attribute:
            if execution.method != execution.target.attribute:
                raise ValueError('A module attribute target calls that attribute.')
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
        cls = import_named(self.tester_module_path, self.tester_class_name)
        attributes = self._resolve_value(_copy_data(self.tester_attributes))
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
        cls = import_named(self.tester_module_path, self.tester_class_name)
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
                return import_named(target.module_path, target.class_name)
            return import_named(target.module_path, target.attribute)
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
            raise ValueError(
                f'Target {target} is not a fixture. A bare name is not a prior as key.',
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
            raise ValueError(f'{name} is both an as key and a fixture name.')
        if outcome.startswith(REQUEST_REF_PREFIX):
            if name not in self.as_keys:
                raise ValueError(f'Missing runtime reference {outcome}.')
            return self.session.data[name]
        if name in self.as_keys:
            return self.session.data[name]
        if name in self.fixtures:
            return self.fixtures[name]
        raise ValueError(f'Outcome {name} is not an as key or a fixture.')

    # * method: compare
    def _compare(self, actual: Any, expected: Any) -> None:
        '''
        Compare one fields value. Extra object attributes are ignored.

        :param actual: The actual value.
        :type actual: Any
        :param expected: The expected value.
        :type expected: Any
        :return: None.
        :rtype: None
        '''

        # A keyed list replaces field_normalizers. It is not an index path.
        if isinstance(expected, dict) and isinstance(actual, list) and self._is_keyed_list(expected):
            self._compare_keyed(actual, expected)
            return
        if isinstance(expected, dict):
            self._compare_mapping(actual, expected)
            return
        if isinstance(expected, list):
            if not isinstance(actual, list) or len(actual) != len(expected):
                self._fail('List field length does not match.')
            for actual_item, expected_item in zip(actual, expected):
                self._compare(actual_item, expected_item)
            return
        if actual != expected:
            self._fail(f'{actual!r} != {expected!r}.')

    # * method: is_keyed_list
    def _is_keyed_list(self, expected: Dict[str, Any]) -> bool:
        '''
        Report whether an expected value is the keyed-list form.

        :param expected: The expected mapping.
        :type expected: Dict[str, Any]
        :return: True when the mapping is key plus items.
        :rtype: bool
        '''

        # The form is exactly those two keys. Other mappings are attributes.
        return (
            set(expected) == {'key', 'items'}
            and isinstance(expected.get('key'), str)
            and isinstance(expected.get('items'), dict)
        )

    # * method: compare_mapping
    def _compare_mapping(self, actual: Any, expected: Dict[str, Any]) -> None:
        '''
        Compare a mapping or an object's attributes. A missing expected key fails.

        :param actual: The actual mapping or object.
        :type actual: Any
        :param expected: The expected attributes.
        :type expected: Dict[str, Any]
        :return: None.
        :rtype: None
        '''

        # A mapping compares keys. An object compares attributes.
        if isinstance(actual, Mapping):
            for key, item in expected.items():
                if key not in actual:
                    self._fail(f'Missing key {key}.')
                self._compare(actual[key], item)
            return
        for key, item in expected.items():
            if not hasattr(actual, key):
                self._fail(f'Missing attribute {key}.')
            self._compare(getattr(actual, key), item)

    # * method: compare_keyed
    def _compare_keyed(self, actual: List[Any], expected: Dict[str, Any]) -> None:
        '''
        Match a list of objects to a mapping keyed by one attribute.

        :param actual: The actual list.
        :type actual: List[Any]
        :param expected: The keyed-list form.
        :type expected: Dict[str, Any]
        :return: None.
        :rtype: None
        '''

        # Every object matches one item, and every item matches one object.
        attr = expected['key']
        items = expected['items']
        if len(actual) != len(items):
            self._fail('Keyed list length does not match items.')
        seen = {}
        for obj in actual:
            if not hasattr(obj, attr):
                self._fail(f'Missing key attribute {attr}.')
            key = getattr(obj, attr)
            if key in seen:
                self._fail(f'Duplicate key {key}.')
            seen[key] = obj
        if set(seen) != set(items):
            self._fail('Keyed list keys do not match items.')
        for key, fields in items.items():
            self._compare(seen[key], fields)

    # * method: check_equals
    def _check_equals(self, assertion: Assertion) -> None:
        '''
        Assert equality after ref resolution.

        :param assertion: The equals check.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # YAML null is not an expected value.
        if assertion.equals is None:
            raise ValueError('YAML null under equals is rejected.')
        outcome = self._resolve_outcome(assertion.outcome)
        expected = self._resolve_value(assertion.equals)
        if outcome != expected:
            self._fail(f'{outcome!r} != {expected!r}.')

    # * method: check_null
    def _check_null(self, assertion: Assertion) -> None:
        '''
        Assert the outcome is None.

        :param assertion: The null check.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # null: true is is None. It is not equals null.
        outcome = self._resolve_outcome(assertion.outcome)
        if outcome is not None:
            self._fail(f'Expected None, got {outcome!r}.')

    # * method: check_fields
    def _check_fields(self, assertion: Assertion) -> None:
        '''
        Compare the fields tree. No normalizer and no index path.

        :param assertion: The fields check.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # Resolve refs in the tree, then compare attributes.
        outcome = self._resolve_outcome(assertion.outcome)
        expected = self._resolve_value(assertion.fields)
        self._compare(outcome, expected)

    # * method: check_absent
    def _check_absent(self, assertion: Assertion) -> None:
        '''
        Assert each name is absent from a mapping or a model dump.

        :param assertion: The absent check.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # A mapping uses keys. A model uses model_dump.
        outcome = self._resolve_outcome(assertion.outcome)
        if isinstance(outcome, Mapping):
            for name in assertion.absent:
                if name in outcome:
                    self._fail(f'{name} is present.')
            return
        if not hasattr(outcome, 'model_dump'):
            self._fail('absent requires a mapping or a model.')
        dumped = outcome.model_dump()
        for name in assertion.absent:
            if name in dumped:
                self._fail(f'{name} is present.')

    # * method: check_error_code
    def _check_error_code(self, assertion: Assertion) -> None:
        '''
        Compare outcome.error_code to the expected string.

        :param assertion: The error_code check.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # A missing attribute fails. The string is the code, not a constant.
        outcome = self._resolve_outcome(assertion.outcome)
        missing = object()
        code = getattr(outcome, 'error_code', missing)
        if code is missing:
            self._fail('Outcome has no error_code.')
        if code != assertion.error_code:
            self._fail(f'{code!r} != {assertion.error_code!r}.')

    # * method: check_type
    def _check_type(self, assertion: Assertion) -> None:
        '''
        Assert isinstance against one imported class.

        :param assertion: The type check.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # negate means not an instance. A subclass passes unless negated.
        outcome = self._resolve_outcome(assertion.outcome)
        cls = import_named(assertion.module_path, assertion.class_name)
        matched = isinstance(outcome, cls)
        if assertion.negate:
            if matched:
                self._fail(f'{outcome!r} is an instance of {assertion.class_name}.')
            return
        if not matched:
            self._fail(f'{outcome!r} is not an instance of {assertion.class_name}.')

    # * method: check_is
    def _check_is(self, assertion: Assertion) -> None:
        '''
        Assert identity with an imported class or a builtin type.

        :param assertion: The is check.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # This is the live type. It is not isinstance.
        outcome = self._resolve_outcome(assertion.outcome)
        if assertion.builtin:
            expected = BUILTIN_TYPES[assertion.builtin]
        else:
            expected = import_named(assertion.module_path, assertion.class_name)
        if outcome is not expected:
            self._fail(f'{outcome!r} is not {expected!r}.')

    # * method: check_message
    def _check_message(self, assertion: Assertion) -> None:
        '''
        Assert the message is a substring of str(outcome).

        :param assertion: The message check.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # message is not a general contains.
        outcome = self._resolve_outcome(assertion.outcome)
        if assertion.message not in str(outcome):
            self._fail(f'{assertion.message!r} is not in {outcome!r}.')

    # * method: check_called
    def _check_called(self, assertion: Assertion) -> None:
        '''
        Assert the named mock method was called as specified.

        :param assertion: The assert_called_once_with check.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # Resolve refs in the call spec before comparing.
        if assertion.mock not in self.mocks:
            raise ValueError(f'Missing mock {assertion.mock}.')
        method = getattr(self.mocks[assertion.mock], assertion.method)
        spec = self._resolve_value(assertion.assert_called_once_with)
        if 'calls' in spec:
            expected_calls = [
                call(*item.get('args', []), **item.get('kwargs', {}))
                for item in spec['calls']
            ]
            if list(method.call_args_list) != expected_calls:
                self._fail(f'Calls {method.call_args_list!r} != {expected_calls!r}.')
            return
        times = spec.get('times', 1)
        if times == 0:
            if 'args' in spec or 'kwargs' in spec:
                raise ValueError('times 0 requires args to be omitted.')
            if method.call_count != 0:
                self._fail(f'Expected no calls, got {method.call_count}.')
            return
        args = spec.get('args', [])
        kwargs = spec.get('kwargs', {})
        if times == 1 and ('args' in spec or 'kwargs' in spec):
            method.assert_called_once_with(*args, **kwargs)
            return
        if method.call_count != times:
            self._fail(f'Expected {times} calls, got {method.call_count}.')
        if 'args' in spec or 'kwargs' in spec:
            expected = call(*args, **kwargs)
            for actual in method.call_args_list:
                if actual != expected:
                    self._fail(f'{actual!r} != {expected!r}.')

    # * method: check_domain_contract
    def _check_domain_contract(self, assertion: Assertion) -> None:
        '''
        Run the DomainObject and model-error protocol on harness-owned classes.

        :param assertion: The domain_contract check.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # The harness owns these classes. The YAML file does not define them.
        class TestDomainObject(DomainObject):
            '''Harness domain object.'''

            attribute: str = Field(
                ...,
                description='The attribute.',
            )

        class TestIdentifiedObject(DomainObject):
            '''Harness identified domain object.'''

            id: str = Field(
                ...,
                description='The identifier.',
            )

            name: str = Field(
                ...,
                description='The name.',
            )

        class Stub:
            '''Harness stub with a non-primitive identity.'''

            id = {'nested': 'value'}

        # Construction.
        domain_object = TestDomainObject(attribute='test')
        if domain_object.attribute != 'test':
            self._fail('Construction did not keep the attribute.')

        # An extra field is a ValidationError.
        try:
            TestDomainObject(attribute='test', unknown='nope')
        except ValidationError:
            pass
        else:
            self._fail('An extra field should be rejected.')

        # Assignment of an invalid value fails before it is classified.
        try:
            domain_object.attribute = ['not', 'a', 'string']
        except ValidationError:
            pass
        else:
            self._fail('Invalid assignment should fail.')

        # unpack_validation_error flattens a missing field.
        try:
            TestDomainObject()
        except ValidationError as error:
            violations = unpack_validation_error(error)
        else:
            self._fail('A missing field should fail.')
        if violations[0]['field'] != 'attribute' or set(violations[0]) != {'field', 'type', 'message'}:
            self._fail('unpack_validation_error did not flatten the violation.')

        # describe_model reports identity and omits a non-primitive field.
        identified = TestIdentifiedObject(id='test_id', name='Test Name')
        descriptor = describe_model(identified)
        if descriptor.get('type') != 'TestIdentifiedObject' or descriptor.get('id') != 'test_id':
            self._fail('describe_model did not report the identity.')
        if 'key' in descriptor:
            self._fail('describe_model reported an undeclared identity field.')
        if 'id' in describe_model(Stub()):
            self._fail('describe_model kept a non-primitive identity.')

        # raise_for_validation, unknown attribute, with and without a model.
        self._raise_for_validation(domain_object, 'not_a_field', 1, INVALID_MODEL_ATTRIBUTE_ID, with_model=False)
        self._raise_for_validation(identified, 'not_a_field', 1, INVALID_MODEL_ATTRIBUTE_ID, with_model=True)

        # raise_for_validation, invalid value, with and without a model.
        self._raise_for_validation(
            domain_object,
            'attribute',
            ['not', 'a', 'string'],
            INVALID_MODEL_VALUE_ID,
            with_model=False,
        )
        self._raise_for_validation(
            identified,
            'name',
            ['not', 'a', 'string'],
            INVALID_MODEL_VALUE_ID,
            with_model=True,
        )

    # * method: raise_for_validation
    def _raise_for_validation(self,
            model: Any,
            attribute: str,
            value: Any,
            error_code: str,
            with_model: bool,
        ) -> None:
        '''
        Classify one assignment failure, with or without the model instance.

        :param model: The model to assign on.
        :type model: Any
        :param attribute: The attribute to assign.
        :type attribute: str
        :param value: The value to assign.
        :type value: Any
        :param error_code: The expected model error code.
        :type error_code: str
        :param with_model: Whether to pass the model into the raiser.
        :type with_model: bool
        :return: None.
        :rtype: None
        '''

        # Capture the assignment failure, then classify it.
        try:
            setattr(model, attribute, value)
        except ValidationError as error:
            captured = error
        else:
            self._fail('Assignment should have failed.')
        try:
            if with_model:
                ModelError.raise_for_validation(captured, model=model, attribute=attribute)
            else:
                ModelError.raise_for_validation(captured, attribute=attribute)
        except ModelError as error:
            if error.error_code != error_code:
                self._fail(f'{error.error_code} != {error_code}.')
            if with_model and error.model.get('type') != type(model).__name__:
                self._fail('raise_for_validation did not describe the model.')
            if not with_model and error.model.get('type') != type(model).__name__:
                self._fail('raise_for_validation did not fall back to the error title.')
            return
        self._fail('raise_for_validation did not raise.')

    # * method: check_mapper_contract
    def _check_mapper_contract(self, assertion: Assertion) -> None:
        '''
        Run the mapper base protocol. Contexts do not import mappers.

        :param assertion: The mapper_contract check.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # The events module holds the procedure because it may import mappers.
        run_mapper_contract(exclude=assertion.exclude)

    # * method: check_event_base
    def _check_event_base(self, assertion: Assertion) -> None:
        '''
        Assert the bound event subclasses the named base and stores its mocks.

        :param assertion: The event_base check.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # One check covers a bare base-event tester.
        event_cls = import_named(self.tester_module_path, self.tester_class_name)
        base_cls = import_named(assertion.module_path, assertion.class_name)
        if not issubclass(event_cls, base_cls):
            self._fail(f'{self.tester_class_name} is not a {assertion.class_name}.')
        instance = event_cls(**self.mocks)
        for name, mock in self.mocks.items():
            if getattr(instance, name) is not mock:
                self._fail(f'{name} was not stored on the event.')

    # * method: check_parameters_required
    def _check_parameters_required(self, assertion: Assertion) -> None:
        '''
        Run the decorator matrix on a harness-owned event.

        :param assertion: The parameters_required check.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # The harness owns the event. The names come from the check.
        names = list(assertion.names)

        class RequiredEvent(DomainEvent):
            '''Harness event for the parameters_required matrix.'''

            @DomainEvent.parameters_required(names)
            def execute(self, **kwargs):
                return 'ok'

        # A valid call passes. It is not a second meaning of error_code.
        result = DomainEvent.handle(
            RequiredEvent,
            **{name: 'value' for name in names},
        )
        if result != 'ok':
            self._fail('A valid call should pass parameters_required.')
        for name in names:
            others = {
                other: 'value'
                for other in names
                if other != name
            }
            self._expect_required(RequiredEvent, name, others)
            self._expect_required(RequiredEvent, name, {**others, name: None})
            self._expect_required(RequiredEvent, name, {**others, name: ''})
            self._expect_required(RequiredEvent, name, {**others, name: '   '})

    # * method: expect_required
    def _expect_required(self, event_cls: type, name: str, kwargs: Dict[str, Any]) -> None:
        '''
        Assert one invalid call raises COMMAND_PARAMETER_REQUIRED and names the parameter.

        :param event_cls: The harness event.
        :type event_cls: type
        :param name: The parameter name.
        :type name: str
        :param kwargs: The invalid call arguments.
        :type kwargs: Dict[str, Any]
        :return: None.
        :rtype: None
        '''

        # The code is COMMAND_PARAMETER_REQUIRED. The name is in the message.
        try:
            DomainEvent.handle(event_cls, **kwargs)
        except TiferetError as error:
            if error.error_code != a.error.COMMAND_PARAMETER_REQUIRED_ID:
                self._fail(f'{name} raised {error.error_code}.')
            if name not in str(error):
                self._fail(f'{name} is not in the message.')
            return
        self._fail(f'{name} did not raise COMMAND_PARAMETER_REQUIRED.')

    # * method: check_service_contract
    def _check_service_contract(self, assertion: Assertion) -> None:
        '''
        Lock the service method table and fail direct construction when abstract.

        :param assertion: The service_contract check.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # The tester class is the service. This is not assert_contract.
        cls = import_named(self.tester_module_path, self.tester_class_name)
        abstracts = set(assertion.abstracts)
        declared = set(getattr(cls, '__abstractmethods__', ()))
        if abstracts != declared:
            self._fail(f'Abstracts {declared} != {abstracts}.')
        for spec in assertion.methods:
            self._lock_method(cls, spec)
        for name in assertion.absent or []:
            if hasattr(cls, name):
                self._fail(f'{name} is not absent.')
        if not abstracts:
            return
        try:
            cls()
        except TypeError:
            return
        self._fail('Direct construction should fail.')

    # * method: lock_method
    def _lock_method(self, cls: type, spec: Dict[str, Any]) -> None:
        '''
        Lock one method's parameters, defaults, annotations, and return.

        :param cls: The service class.
        :type cls: type
        :param spec: The method table row.
        :type spec: Dict[str, Any]
        :return: None.
        :rtype: None
        '''

        # name and params are required. The rest are optional.
        name = spec['name']
        if not hasattr(cls, name):
            self._fail(f'Missing method {name}.')
        signature = inspect.signature(getattr(cls, name))
        params = list(signature.parameters)
        if params != list(spec['params']):
            self._fail(f'{name} params {params} != {spec["params"]}.')
        for param_name, expected in (spec.get('defaults') or {}).items():
            if signature.parameters[param_name].default != expected:
                self._fail(f'{name} default {param_name} does not match.')
        for param_name, expected in (spec.get('annotations') or {}).items():
            actual = _annotation_name(signature.parameters[param_name].annotation)
            if actual != expected:
                self._fail(f'{name} annotation {param_name} is {actual!r}.')
        if 'returns' in spec and _annotation_name(signature.return_annotation) != spec['returns']:
            self._fail(f'{name} return annotation does not match.')

    # * method: check_middleware_chain
    def _check_middleware_chain(self, assertion: Assertion) -> None:
        '''
        Run one middleware chain shape. The harness owns the wrappers.

        :param assertion: The middleware_chain check.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # No lambda in the YAML file. The wrappers are defined here.
        shape = assertion.middleware_chain
        if shape == 'none':
            self._run_chain([])
            return
        if shape == 'single':
            self._run_single()
            return
        if shape == 'order':
            self._run_order()
            return
        if shape == 'capture':
            self._run_capture()
            return
        if shape == 'intercept':
            self._run_intercept()
            return
        if shape == 'async':
            self._run_async_chain()
            return
        raise ValueError(f'middleware_chain {shape} is not legal.')

    # * method: run_chain
    def _run_chain(self, middleware: list, **kwargs) -> Any:
        '''
        Run a synchronous probe event through the given wrappers.

        :param middleware: The harness wrappers.
        :type middleware: list
        :param kwargs: Event arguments.
        :type kwargs: dict
        :return: The chain result.
        :rtype: Any
        '''

        # The probe is a harness event, not a YAML class.
        class Probe(DomainEvent):
            '''Harness event for a synchronous chain.'''

            def execute(self, **event_kwargs):
                return 'ran'

        result = DomainEvent.handle(Probe, middleware=middleware, **kwargs)
        if result != 'ran' and middleware == []:
            self._fail('An empty chain should return the event result.')
        return result

    # * method: run_single
    def _run_single(self) -> None:
        '''
        Prove one wrapper calls next and returns the event result.

        :return: None.
        :rtype: None
        '''

        # One wrapper, outermost and only.
        class Single:
            '''Harness wrapper that continues the chain.'''

            def __init__(self):
                self.seen = False

            def __call__(self, event, kwargs, next_fn):
                self.seen = True
                return next_fn()

        wrapper = Single()
        result = self._run_chain([wrapper])
        if result != 'ran' or not wrapper.seen:
            self._fail('A single wrapper should continue the chain.')

    # * method: run_order
    def _run_order(self) -> None:
        '''
        Prove two wrappers run outermost first.

        :return: None.
        :rtype: None
        '''

        # Entry is outer then inner. Exit is inner then outer.
        order = []

        class Track:
            '''Harness wrapper that records entry and exit.'''

            def __init__(self, name):
                self.name = name

            def __call__(self, event, kwargs, next_fn):
                order.append(self.name)
                result = next_fn()
                order.append(f'{self.name}-post')
                return result

        self._run_chain([Track('outer'), Track('inner')])
        if order != ['outer', 'inner', 'inner-post', 'outer-post']:
            self._fail(f'Wrapper order was {order}.')

    # * method: run_capture
    def _run_capture(self) -> None:
        '''
        Prove a wrapper sees the event and the kwargs.

        :return: None.
        :rtype: None
        '''

        # The wrapper records what the chain passed it.
        captured = {}

        class Capture:
            '''Harness wrapper that records the call.'''

            def __call__(self, event, kwargs, next_fn):
                captured['event'] = event
                captured['kwargs'] = dict(kwargs)
                return next_fn()

        self._run_chain([Capture()], token='yes')
        if captured.get('kwargs', {}).get('token') != 'yes':
            self._fail('The wrapper did not see the kwargs.')
        if type(captured.get('event')).__name__ != 'Probe':
            self._fail('The wrapper did not see the event.')

    # * method: run_intercept
    def _run_intercept(self) -> None:
        '''
        Prove a wrapper can return without calling next.

        :return: None.
        :rtype: None
        '''

        # Intercept does not call the event.
        called = {'value': False}

        class Probe(DomainEvent):
            '''Harness event that records whether execute ran.'''

            def execute(self, **kwargs):
                called['value'] = True
                return 'ran'

        class Intercept:
            '''Harness wrapper that stops the chain.'''

            def __call__(self, event, kwargs, next_fn):
                return 'stopped'

        result = DomainEvent.handle(Probe, middleware=[Intercept()])
        if result != 'stopped' or called['value']:
            self._fail('Intercept should stop the chain.')

    # * method: run_async_chain
    def _run_async_chain(self) -> None:
        '''
        Await an async wrapper. There is no async phase key.

        :return: None.
        :rtype: None
        '''

        # The check awaits. The wrapper is owned here, not in the YAML file.
        class AsyncProbe(AsyncDomainEvent):
            '''Harness async event.'''

            async def execute(self, **kwargs):
                return 'async-ran'

        class AsyncWrap:
            '''Harness async wrapper.'''

            async def __call__(self, event, kwargs, next_fn):
                return await next_fn()

        result = run_coroutine(DomainEvent.handle_async(
            AsyncProbe,
            middleware=[AsyncWrap()],
        ))
        if result != 'async-ran':
            self._fail('The async chain did not await the event.')

    # * method: check_cause
    def _check_cause(self, assertion: Assertion) -> None:
        '''
        Read outcome.__cause__. This is not a frame walk.

        :param assertion: The cause check.
        :type assertion: Assertion
        :return: None.
        :rtype: None
        '''

        # The chained exception is the cause. The frame is not consulted.
        outcome = self._resolve_outcome(assertion.outcome)
        cause = outcome.__cause__
        cls = import_named(assertion.module_path, assertion.class_name)
        if not isinstance(cause, cls):
            self._fail('Cause type does not match.')
        if assertion.message not in str(cause):
            self._fail('Cause message does not match.')

    # * method: fail
    def _fail(self, message: str) -> None:
        '''
        Fail the check.

        :param message: The failure message.
        :type message: str
        :return: None.
        :rtype: None
        '''

        # The first failure fails the test.
        raise AssertionError(message)

# ** context: test_context
class TestContext(FeatureContext):
    '''
    The session's view of one test. It extends ``FeatureContext`` so a test
    runs as a feature, and it declares ``domain_type = Test`` in its own
    namespace so ``Feature`` stays mapped to ``FeatureContext``.
    '''

    # * attribute: domain_type
    domain_type = Test
