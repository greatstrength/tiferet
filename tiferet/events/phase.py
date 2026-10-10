"""Tiferet Phase Events"""

# *** imports

# ** core
import asyncio
import inspect
import threading
from typing import Any, Dict, List
from unittest.mock import call

# ** infra
from pydantic import Field, ValidationError

# ** app
from .core import AsyncDomainEvent, DomainEvent, a
from ..assets import TiferetError
from ..domain import (
    INVALID_MODEL_ATTRIBUTE_ID,
    INVALID_MODEL_VALUE_ID,
    DomainObject,
    ModelError,
    describe_model,
    unpack_validation_error,
)
from ..interfaces.check import CheckService

# *** functions

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

# ** function: await_result
def _await_result(coro: Any) -> Any:
    '''
    Drive one coroutine the middleware check owns.

    :param coro: The coroutine to finish.
    :type coro: Any
    :return: The coroutine result.
    :rtype: Any
    '''

    # Use asyncio.run when no loop is already running.
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    # A running loop cannot be re-entered. Finish on a dedicated thread.
    box: Dict[str, Any] = {}

    def _runner():
        try:
            box['result'] = asyncio.run(coro)
        except BaseException as error:
            box['error'] = error

    thread = threading.Thread(target=_runner)
    thread.start()
    thread.join()
    if 'error' in box:
        raise box['error']
    return box.get('result')

# ** function: evaluate_domain_contract
def _evaluate_domain_contract(check_service: CheckService) -> str | None:
    '''
    Run the domain-object protocol. This event constructs the objects.

    :param check_service: The check that compares values.
    :type check_service: CheckService
    :return: A mismatch, or None when the protocol holds.
    :rtype: str | None
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
    mismatch = check_service.equal(domain_object.attribute, 'test')
    if mismatch:
        return 'Construction did not keep the attribute.'

    # An extra field is a ValidationError.
    try:
        TestDomainObject(attribute='test', unknown='nope')
    except ValidationError:
        pass
    else:
        return 'An extra field should be rejected.'

    # Assignment of an invalid value fails before it is classified.
    try:
        domain_object.attribute = ['not', 'a', 'string']
    except ValidationError:
        pass
    else:
        return 'Invalid assignment should fail.'

    # unpack_validation_error flattens a missing field.
    try:
        TestDomainObject()
    except ValidationError as error:
        violations = unpack_validation_error(error)
    else:
        return 'A missing field should fail.'
    if violations[0]['field'] != 'attribute' or set(violations[0]) != {'field', 'type', 'message'}:
        return 'unpack_validation_error did not flatten the violation.'

    # describe_model reports identity and omits a non-primitive field.
    identified = TestIdentifiedObject(id='test_id', name='Test Name')
    descriptor = describe_model(identified)
    mismatch = check_service.equal(descriptor.get('type'), 'TestIdentifiedObject')
    if mismatch:
        return 'describe_model did not report the identity.'
    mismatch = check_service.equal(descriptor.get('id'), 'test_id')
    if mismatch:
        return 'describe_model did not report the identity.'
    if 'key' in descriptor:
        return 'describe_model reported an undeclared identity field.'
    if 'id' in describe_model(Stub()):
        return 'describe_model kept a non-primitive identity.'

    # raise_for_validation, unknown attribute, with and without a model.
    mismatch = _raise_for_validation(
        check_service,
        domain_object,
        'not_a_field',
        1,
        INVALID_MODEL_ATTRIBUTE_ID,
        with_model=False,
    )
    if mismatch:
        return mismatch
    mismatch = _raise_for_validation(
        check_service,
        identified,
        'not_a_field',
        1,
        INVALID_MODEL_ATTRIBUTE_ID,
        with_model=True,
    )
    if mismatch:
        return mismatch

    # raise_for_validation, invalid value, with and without a model.
    mismatch = _raise_for_validation(
        check_service,
        domain_object,
        'attribute',
        ['not', 'a', 'string'],
        INVALID_MODEL_VALUE_ID,
        with_model=False,
    )
    if mismatch:
        return mismatch
    return _raise_for_validation(
        check_service,
        identified,
        'name',
        ['not', 'a', 'string'],
        INVALID_MODEL_VALUE_ID,
        with_model=True,
    )

# ** function: raise_for_validation
def _raise_for_validation(check_service: CheckService,
        model: Any,
        attribute: str,
        value: Any,
        error_code: str,
        with_model: bool,
    ) -> str | None:
    '''
    Classify one assignment failure, with or without the model instance.

    :param check_service: The check that compares codes.
    :type check_service: CheckService
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
    :return: A mismatch, or None when the classification holds.
    :rtype: str | None
    '''

    # Capture the assignment failure, then classify it.
    try:
        setattr(model, attribute, value)
    except ValidationError as error:
        captured = error
    else:
        return 'Assignment should have failed.'
    try:
        if with_model:
            ModelError.raise_for_validation(captured, model=model, attribute=attribute)
        else:
            ModelError.raise_for_validation(captured, attribute=attribute)
    except ModelError as error:
        mismatch = check_service.codes(error.error_code, error_code)
        if mismatch:
            return mismatch
        mismatch = check_service.equal(
            error.model.get('type'),
            type(model).__name__,
        )
        if mismatch and with_model:
            return 'raise_for_validation did not describe the model.'
        if mismatch and not with_model:
            return 'raise_for_validation did not fall back to the error title.'
        return None
    return 'raise_for_validation did not raise.'

# ** function: expect_required
def _expect_required(check_service: CheckService,
        event_cls: type,
        name: str,
        kwargs: Dict[str, Any],
    ) -> str | None:
    '''
    Assert one invalid call raises COMMAND_PARAMETER_REQUIRED and names the parameter.

    :param check_service: The check that compares codes.
    :type check_service: CheckService
    :param event_cls: The harness event.
    :type event_cls: type
    :param name: The parameter name.
    :type name: str
    :param kwargs: The invalid call arguments.
    :type kwargs: Dict[str, Any]
    :return: A mismatch, or None when the call fails as required.
    :rtype: str | None
    '''

    # The code is COMMAND_PARAMETER_REQUIRED. The name is in the message.
    try:
        DomainEvent.handle(event_cls, **kwargs)
    except TiferetError as error:
        mismatch = check_service.codes(
            error.error_code,
            a.error.COMMAND_PARAMETER_REQUIRED_ID,
        )
        if mismatch:
            return f'{name} raised {error.error_code}.'
        if name not in str(error):
            return f'{name} is not in the message.'
        return None
    return f'{name} did not raise COMMAND_PARAMETER_REQUIRED.'

# ** function: evaluate_parameters_required
def _evaluate_parameters_required(check_service: CheckService, names: List[str]) -> str | None:
    '''
    Run the decorator matrix on a harness-owned event.

    :param check_service: The check that compares codes.
    :type check_service: CheckService
    :param names: The required parameter names.
    :type names: List[str]
    :return: A mismatch, or None when the matrix holds.
    :rtype: str | None
    '''

    # The harness owns the event. The names come from the check.
    required = list(names)

    class RequiredEvent(DomainEvent):
        '''Harness event for the parameters_required matrix.'''

        @DomainEvent.parameters_required(required)
        def execute(self, **kwargs):
            return 'ok'

    # A valid call passes. It is not a second meaning of error_code.
    result = DomainEvent.handle(
        RequiredEvent,
        **{name: 'value' for name in required},
    )
    mismatch = check_service.equal(result, 'ok')
    if mismatch:
        return 'A valid call should pass parameters_required.'
    for name in required:
        others = {
            other: 'value'
            for other in required
            if other != name
        }
        for kwargs in (
            others,
            {**others, name: None},
            {**others, name: ''},
            {**others, name: '   '},
        ):
            mismatch = _expect_required(check_service, RequiredEvent, name, kwargs)
            if mismatch:
                return mismatch
    return None

# ** function: lock_method
def _lock_method(check_service: CheckService, cls: type, spec: Dict[str, Any]) -> str | None:
    '''
    Lock one method's parameters, defaults, annotations, and return.

    :param check_service: The check that compares values.
    :type check_service: CheckService
    :param cls: The service class.
    :type cls: type
    :param spec: The method table row.
    :type spec: Dict[str, Any]
    :return: A mismatch, or None when the method matches.
    :rtype: str | None
    '''

    # name and params are required. The rest are optional.
    name = spec['name']
    if not hasattr(cls, name):
        return f'Missing method {name}.'
    signature = inspect.signature(getattr(cls, name))
    params = list(signature.parameters)
    mismatch = check_service.equal(params, list(spec['params']))
    if mismatch:
        return f'{name} params {params} != {spec["params"]}.'
    for param_name, expected in (spec.get('defaults') or {}).items():
        if signature.parameters[param_name].default != expected:
            return f'{name} default {param_name} does not match.'
    for param_name, expected in (spec.get('annotations') or {}).items():
        actual = _annotation_name(signature.parameters[param_name].annotation)
        if actual != expected:
            return f'{name} annotation {param_name} is {actual!r}.'
    if 'returns' in spec and _annotation_name(signature.return_annotation) != spec['returns']:
        return f'{name} return annotation does not match.'
    return None

# ** function: evaluate_service_contract
def _evaluate_service_contract(check_service: CheckService,
        cls: type,
        abstracts: List[str],
        methods: List[Dict[str, Any]],
        absent: List[str],
    ) -> str | None:
    '''
    Lock the service method table and fail direct construction when abstract.

    :param check_service: The check that compares values.
    :type check_service: CheckService
    :param cls: The service class.
    :type cls: type
    :param abstracts: The expected abstract names.
    :type abstracts: List[str]
    :param methods: The method table.
    :type methods: List[Dict[str, Any]]
    :param absent: Names that must be absent.
    :type absent: List[str]
    :return: A mismatch, or None when the contract holds.
    :rtype: str | None
    '''

    # The tester class is the service. This is not assert_contract.
    declared = set(getattr(cls, '__abstractmethods__', ()))
    mismatch = check_service.equal(declared, set(abstracts))
    if mismatch:
        return f'Abstracts {declared} != {set(abstracts)}.'
    for spec in methods:
        mismatch = _lock_method(check_service, cls, spec)
        if mismatch:
            return mismatch
    for name in absent or []:
        if hasattr(cls, name):
            return f'{name} is not absent.'
    if not abstracts:
        return None
    try:
        cls()
    except TypeError:
        return None
    return 'Direct construction should fail.'

# ** function: run_chain
def _run_chain(middleware: list, **kwargs) -> Any:
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

    return DomainEvent.handle(Probe, middleware=middleware, **kwargs)

# ** function: run_single
def _run_single(check_service: CheckService) -> str | None:
    '''
    Prove one wrapper calls next and returns the event result.

    :param check_service: The check that compares values.
    :type check_service: CheckService
    :return: A mismatch, or None when the wrapper continues.
    :rtype: str | None
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
    result = _run_chain([wrapper])
    mismatch = check_service.equal(result, 'ran')
    if mismatch or not wrapper.seen:
        return 'A single wrapper should continue the chain.'
    return None

# ** function: run_order
def _run_order(check_service: CheckService) -> str | None:
    '''
    Prove two wrappers run outermost first.

    :param check_service: The check that compares values.
    :type check_service: CheckService
    :return: A mismatch, or None when the order holds.
    :rtype: str | None
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

    _run_chain([Track('outer'), Track('inner')])
    mismatch = check_service.equal(
        order,
        ['outer', 'inner', 'inner-post', 'outer-post'],
    )
    if mismatch:
        return f'Wrapper order was {order}.'
    return None

# ** function: run_capture
def _run_capture(check_service: CheckService) -> str | None:
    '''
    Prove a wrapper sees the event and the kwargs.

    :param check_service: The check that compares values.
    :type check_service: CheckService
    :return: A mismatch, or None when the wrapper saw the call.
    :rtype: str | None
    '''

    # The wrapper records what the chain passed it.
    captured = {}

    class Capture:
        '''Harness wrapper that records the call.'''

        def __call__(self, event, kwargs, next_fn):
            captured['event'] = event
            captured['kwargs'] = dict(kwargs)
            return next_fn()

    _run_chain([Capture()], token='yes')
    mismatch = check_service.equal(captured.get('kwargs', {}).get('token'), 'yes')
    if mismatch:
        return 'The wrapper did not see the kwargs.'
    if type(captured.get('event')).__name__ != 'Probe':
        return 'The wrapper did not see the event.'
    return None

# ** function: run_intercept
def _run_intercept(check_service: CheckService) -> str | None:
    '''
    Prove a wrapper can return without calling next.

    :param check_service: The check that compares values.
    :type check_service: CheckService
    :return: A mismatch, or None when the wrapper stops the chain.
    :rtype: str | None
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
    mismatch = check_service.equal(result, 'stopped')
    if mismatch or called['value']:
        return 'Intercept should stop the chain.'
    return None

# ** function: run_async_chain
def _run_async_chain(check_service: CheckService) -> str | None:
    '''
    Await an async wrapper. There is no async phase key.

    :param check_service: The check that compares values.
    :type check_service: CheckService
    :return: A mismatch, or None when the async chain holds.
    :rtype: str | None
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

    result = _await_result(DomainEvent.handle_async(
        AsyncProbe,
        middleware=[AsyncWrap()],
    ))
    mismatch = check_service.equal(result, 'async-ran')
    if mismatch:
        return 'The async chain did not await the event.'
    return None

# ** function: evaluate_middleware_chain
def _evaluate_middleware_chain(check_service: CheckService, shape: str) -> str | None:
    '''
    Run one middleware chain shape. The harness owns the wrappers.

    :param check_service: The check that compares values.
    :type check_service: CheckService
    :param shape: The chain shape.
    :type shape: str
    :return: A mismatch, or None when the shape holds.
    :rtype: str | None
    '''

    # No lambda in the YAML file. The wrappers are defined here.
    if shape == 'none':
        result = _run_chain([])
        mismatch = check_service.equal(result, 'ran')
        if mismatch:
            return 'An empty chain should return the event result.'
        return None
    if shape == 'single':
        return _run_single(check_service)
    if shape == 'order':
        return _run_order(check_service)
    if shape == 'capture':
        return _run_capture(check_service)
    if shape == 'intercept':
        return _run_intercept(check_service)
    if shape == 'async':
        return _run_async_chain(check_service)
    DomainEvent.raise_error(
        a.error.PHASE_STEP_FAILED_ID,
        detail=f'middleware_chain {shape} is not legal.',
    )

# ** function: evaluate_called
def _evaluate_called(check_service: CheckService, method: Any, spec: Dict[str, Any]) -> str | None:
    '''
    Compare one mock method to the resolved call spec.

    :param check_service: The check that compares values.
    :type check_service: CheckService
    :param method: The mock method.
    :type method: Any
    :param spec: The resolved call spec.
    :type spec: Dict[str, Any]
    :return: A mismatch, or None when the calls match.
    :rtype: str | None
    '''

    # Resolve refs in the call spec before comparing.
    if 'calls' in spec:
        expected_calls = [
            call(*item.get('args', []), **item.get('kwargs', {}))
            for item in spec['calls']
        ]
        mismatch = check_service.equal(list(method.call_args_list), expected_calls)
        if mismatch:
            return f'Calls {method.call_args_list!r} != {expected_calls!r}.'
        return None
    times = spec.get('times', 1)
    if times == 0:
        if method.call_count != 0:
            return f'Expected no calls, got {method.call_count}.'
        return None
    args = spec.get('args', [])
    kwargs = spec.get('kwargs', {})
    if times == 1 and ('args' in spec or 'kwargs' in spec):
        try:
            method.assert_called_once_with(*args, **kwargs)
        except AssertionError as error:
            return str(error)
        return None
    if method.call_count != times:
        return f'Expected {times} calls, got {method.call_count}.'
    if 'args' in spec or 'kwargs' in spec:
        expected = call(*args, **kwargs)
        for actual in method.call_args_list:
            mismatch = check_service.equal(actual, expected)
            if mismatch:
                return f'{actual!r} != {expected!r}.'
    return None

# ** function: evaluate_absent
def _evaluate_absent(check_service: CheckService, outcome: Any, names: List[str]) -> str | None:
    '''
    Assert each name is absent from a mapping or a model dump.

    :param check_service: The check that compares a dump to an exclude set.
    :type check_service: CheckService
    :param outcome: The resolved outcome.
    :type outcome: Any
    :param names: The names that must be absent.
    :type names: List[str]
    :return: A mismatch, or None when every name is absent.
    :rtype: str | None
    '''

    # A mapping uses keys. A model uses model_dump.
    if isinstance(outcome, dict):
        return check_service.role_dump(outcome, names)
    if not hasattr(outcome, 'model_dump'):
        return 'absent requires a mapping or a model.'
    mismatch = check_service.role_dump(outcome.model_dump(), names)
    if mismatch:
        return mismatch.replace(' is in the dump.', ' is present.')
    return None

# ** function: evaluate_error_code
def _evaluate_error_code(check_service: CheckService,
        values: Dict[str, Any],
        expected: str,
    ) -> str | None:
    '''
    Compare outcome.error_code to the expected string.

    :param check_service: The check that compares codes.
    :type check_service: CheckService
    :param values: The resolved values.
    :type values: Dict[str, Any]
    :param expected: The expected code.
    :type expected: str
    :return: A mismatch, or None when the codes match.
    :rtype: str | None
    '''

    # A missing attribute fails. The string is the code, not a constant.
    if not values.get('has_error_code'):
        return 'Outcome has no error_code.'
    return check_service.codes(values.get('error_code'), expected)

# ** function: evaluate_type
def _evaluate_type(values: Dict[str, Any], assertion: Any) -> str | None:
    '''
    Assert isinstance against one imported class.

    :param values: The resolved values.
    :type values: Dict[str, Any]
    :param assertion: The type check.
    :type assertion: Any
    :return: A mismatch, or None when the type matches.
    :rtype: str | None
    '''

    # negate means not an instance. A subclass passes unless negated.
    outcome = values.get('outcome')
    matched = isinstance(outcome, values.get('cls'))
    if assertion.negate:
        if matched:
            return f'{outcome!r} is an instance of {assertion.class_name}.'
        return None
    if not matched:
        return f'{outcome!r} is not an instance of {assertion.class_name}.'
    return None

# ** function: evaluate_event_base
def _evaluate_event_base(assertion: Any, values: Dict[str, Any]) -> str | None:
    '''
    Assert the bound event subclasses the named base and stores its mocks.

    :param assertion: The event_base check.
    :type assertion: Any
    :param values: The resolved classes and mocks.
    :type values: Dict[str, Any]
    :return: A mismatch, or None when the base holds.
    :rtype: str | None
    '''

    # One check covers a bare base-event tester.
    event_cls = values.get('event_cls')
    base_cls = values.get('base_cls')
    if not issubclass(event_cls, base_cls):
        return f'{event_cls.__name__} is not a {assertion.class_name}.'
    instance = event_cls(**values.get('mocks', {}))
    for name, mock in values.get('mocks', {}).items():
        if getattr(instance, name) is not mock:
            return f'{name} was not stored on the event.'
    return None

# ** function: evaluate_cause
def _evaluate_cause(assertion: Any, values: Dict[str, Any]) -> str | None:
    '''
    Read outcome.__cause__. This is not a frame walk.

    :param assertion: The cause check.
    :type assertion: Any
    :param values: The resolved outcome and cause class.
    :type values: Dict[str, Any]
    :return: A mismatch, or None when the cause matches.
    :rtype: str | None
    '''

    # The chained exception is the cause. The frame is not consulted.
    cause = values.get('outcome').__cause__
    if not isinstance(cause, values.get('cls')):
        return 'Cause type does not match.'
    if assertion.message not in str(cause):
        return 'Cause message does not match.'
    return None

# ** function: evaluate_check
def _evaluate_check(assertion: Any,
        values: Dict[str, Any],
        check_service: CheckService,
    ) -> str | None:
    '''
    Evaluate one assertion through the check service.

    :param assertion: The assert item.
    :type assertion: Any
    :param values: The values the phase method resolved.
    :type values: Dict[str, Any]
    :param check_service: The check that compares values.
    :type check_service: CheckService
    :return: A mismatch, or None when the check holds.
    :rtype: str | None
    '''

    # One procedure per check name. None of them is an event.
    name = assertion.check
    if name == 'equals':
        return check_service.equal(values.get('outcome'), values.get('equals'))
    if name == 'null':
        if values.get('outcome') is not None:
            return f'Expected None, got {values.get("outcome")!r}.'
        return None
    if name == 'fields':
        return check_service.equal(values.get('outcome'), values.get('fields'))
    if name == 'absent':
        return _evaluate_absent(check_service, values.get('outcome'), assertion.absent)
    if name == 'error_code':
        return _evaluate_error_code(check_service, values, assertion.error_code)
    if name == 'type':
        return _evaluate_type(values, assertion)
    if name == 'is':
        if values.get('outcome') is not values.get('expected'):
            return f'{values.get("outcome")!r} is not {values.get("expected")!r}.'
        return None
    if name == 'message':
        if assertion.message not in str(values.get('outcome')):
            return f'{assertion.message!r} is not in {values.get("outcome")!r}.'
        return None
    if name == 'assert_called_once_with':
        return _evaluate_called(
            check_service,
            values.get('method'),
            values.get('spec') or {},
        )
    if name == 'domain_contract':
        return _evaluate_domain_contract(check_service)
    if name == 'event_base':
        return _evaluate_event_base(assertion, values)
    if name == 'parameters_required':
        return _evaluate_parameters_required(check_service, list(assertion.names))
    if name == 'service_contract':
        return _evaluate_service_contract(
            check_service,
            values.get('cls'),
            list(assertion.abstracts or []),
            list(assertion.methods or []),
            list(assertion.absent or []),
        )
    if name == 'middleware_chain':
        return _evaluate_middleware_chain(check_service, assertion.middleware_chain)
    if name == 'cause':
        return _evaluate_cause(assertion, values)
    return f'{name} is not a check.'

# *** events

# ** event: exercise_mapper_bases
class ExerciseMapperBases(DomainEvent):
    '''
    Runs the mapper protocol through a check and raises the catalogued failure.

    The event constructs the domain source the protocol copies. It does not
    import mappers, and it does not keep the old contract runner.
    '''

    # * attribute: check_service
    check_service: CheckService

    # * init
    def __init__(self, check_service: CheckService) -> None:
        '''
        Initialize the event with the check it calls during this check.

        :param check_service: The check that runs the mapper protocol.
        :type check_service: CheckService
        :return: None.
        :rtype: None
        '''

        # Store the check. This event has no other service.
        self.check_service = check_service

    # * method: execute
    def execute(self, exclude: list = None, **kwargs) -> None:
        '''
        Build the domain source, call the check, and raise on a mismatch.

        :param exclude: Names the to_data role excludes.
        :type exclude: list
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: None when the protocol holds.
        :rtype: None
        '''

        # The source is a domain object the transfer object can copy.
        class SourceModel(DomainObject):
            '''Harness source model for from_model.'''

            id: str = Field(
                ...,
                description='The identifier.',
            )

            name: str = Field(
                ...,
                description='The name.',
            )

        source = SourceModel(id='test_id', name='Test Model')

        # The service returns a mismatch or None. It does not report the module.
        mismatch = self.check_service.mapper_contract(exclude, source)
        self.verify(
            expression=mismatch is None,
            error_code=a.error.PHASE_CHECK_FAILED_ID,
            check='mapper_contract',
            detail=mismatch or '',
        )
        return None

# ** event: evaluate_assertion
class EvaluateAssertion(DomainEvent):
    '''
    Evaluates one assertion through a check and raises the catalogued failure.

    It is the one event a phase method calls for every check except the mapper
    protocol. It is not a handler, and it is not one event per check name.
    '''

    # * attribute: check_service
    check_service: CheckService

    # * init
    def __init__(self, check_service: CheckService) -> None:
        '''
        Initialize the event with the check it calls during this check.

        :param check_service: The check that compares values.
        :type check_service: CheckService
        :return: None.
        :rtype: None
        '''

        # Store the check. This event has no other service.
        self.check_service = check_service

    # * method: execute
    def execute(self, assertion: Any, values: Dict[str, Any] = None, **kwargs) -> Any:
        '''
        Evaluate one assertion and return it when the check holds.

        :param assertion: The assert item.
        :type assertion: Any
        :param values: The values the phase method resolved.
        :type values: Dict[str, Any]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The assertion when the check holds.
        :rtype: Any
        '''

        # A procedure only this event uses lives in this module.
        mismatch = _evaluate_check(
            assertion,
            values or {},
            self.check_service,
        )
        self.verify(
            expression=mismatch is None,
            error_code=a.error.PHASE_CHECK_FAILED_ID,
            check=assertion.check,
            detail=mismatch or '',
        )
        return assertion
