"""Tiferet Phase Events"""

# *** imports

# ** core
import asyncio
import inspect
import threading
from typing import Any, Dict
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

# *** events

# ** event: check_event
class CheckEvent(DomainEvent):
    '''
    Holds the shared check for one phase verification.

    Concrete events extend this base and define only execute. The check
    answers the comparison. The event raises the catalogued failure.
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

        # Store the check. This base has no other service.
        self.check_service = check_service

# ** event: evaluate_assertion
class EvaluateAssertion(CheckEvent):
    '''
    Evaluates one comparison and returns the assertion when it holds.

    The comparisons are equals, null, fields, is, message, type, error_code,
    cause, absent, and event_base. A protocol that builds a harness is not
    this event.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['assertion'])
    def execute(self,
                assertion: Any,
                values: Dict[str, Any] = None,
                **kwargs) -> Any:
        '''
        Compare the resolved values and return the assertion when the check holds.

        :param assertion: The assert item.
        :type assertion: Any
        :param values: The values the phase method resolved.
        :type values: Dict[str, Any]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The assertion when the check holds.
        :rtype: Any
        '''

        # The context resolved the refs. This event does not see the session.
        resolved = values or {}
        name = assertion.check
        outcome = resolved.get('outcome')
        mismatch = None
        if name == 'equals':
            mismatch = self.check_service.equal(outcome, resolved.get('equals'))
        elif name == 'null':
            mismatch = self.check_service.equal(outcome, None)
            if outcome is not None and mismatch:
                mismatch = f'Expected None, got {outcome!r}.'
        elif name == 'fields':
            mismatch = self.check_service.equal(outcome, resolved.get('fields'))
        elif name == 'is':
            expected = resolved.get('expected')
            same = outcome is expected
            mismatch = self.check_service.equal(same, True)
            if mismatch:
                mismatch = f'{outcome!r} is not {expected!r}.'
        elif name == 'message':
            present = assertion.message in str(outcome)
            mismatch = self.check_service.equal(present, True)
            if mismatch:
                mismatch = f'{assertion.message!r} is not in {outcome!r}.'
        elif name == 'type':
            matched = isinstance(outcome, resolved.get('cls'))
            expected_match = not assertion.negate
            mismatch = self.check_service.equal(matched, expected_match)
            if mismatch and assertion.negate:
                mismatch = f'{outcome!r} is an instance of {assertion.class_name}.'
            elif mismatch:
                mismatch = f'{outcome!r} is not an instance of {assertion.class_name}.'
        elif name == 'error_code':
            if not resolved.get('has_error_code'):
                mismatch = 'Outcome has no error_code.'
            else:
                mismatch = self.check_service.codes(
                    resolved.get('error_code'),
                    assertion.error_code,
                )
        elif name == 'cause':
            cause = outcome.__cause__
            typed = isinstance(cause, resolved.get('cls'))
            mismatch = self.check_service.equal(typed, True)
            if mismatch:
                mismatch = 'Cause type does not match.'
            else:
                contained = assertion.message in str(cause)
                mismatch = self.check_service.equal(contained, True)
                if mismatch:
                    mismatch = 'Cause message does not match.'
        elif name == 'absent':
            if isinstance(outcome, dict):
                dumped = outcome
            elif hasattr(outcome, 'model_dump'):
                dumped = outcome.model_dump()
            else:
                dumped = None
            if dumped is None:
                mismatch = 'absent requires a mapping or a model.'
            else:
                mismatch = self.check_service.role_dump(dumped, assertion.absent)
                if mismatch:
                    mismatch = mismatch.replace(' is in the dump.', ' is present.')
        elif name == 'event_base':
            event_cls = resolved.get('event_cls')
            base_cls = resolved.get('base_cls')
            is_sub = issubclass(event_cls, base_cls)
            mismatch = self.check_service.equal(is_sub, True)
            if mismatch:
                mismatch = f'{event_cls.__name__} is not a {assertion.class_name}.'
            else:
                instance = event_cls(**resolved.get('mocks', {}))
                for mock_name, mock in resolved.get('mocks', {}).items():
                    stored = getattr(instance, mock_name) is mock
                    mismatch = self.check_service.equal(stored, True)
                    if mismatch:
                        mismatch = f'{mock_name} was not stored on the event.'
                        break
        else:
            mismatch = f'{name} is not a comparison.'

        # A mismatch is the catalogued check failure. A hold returns the assertion.
        self.verify(
            expression=mismatch is None,
            error_code=a.error.PHASE_CHECK_FAILED_ID,
            check=name,
            detail=mismatch or '',
        )
        return assertion

# ** event: exercise_mapper_bases
class ExerciseMapperBases(CheckEvent):
    '''
    Runs the mapper protocol through a check and returns the assertion.

    The event constructs the domain source the protocol copies. It does not
    import mappers, and it does not keep the old contract runner.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['assertion'])
    def execute(self, assertion: Any, **kwargs) -> Any:
        '''
        Build the domain source, call the check, and return the assertion.

        :param assertion: The mapper_contract check.
        :type assertion: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The assertion when the protocol holds.
        :rtype: Any
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
        mismatch = self.check_service.mapper_contract(
            list(assertion.exclude or []),
            source,
        )
        self.verify(
            expression=mismatch is None,
            error_code=a.error.PHASE_CHECK_FAILED_ID,
            check='mapper_contract',
            detail=mismatch or '',
        )
        return assertion

# ** event: exercise_domain_contract
class ExerciseDomainContract(CheckEvent):
    '''
    Runs the domain-object protocol and returns the assertion.

    The harness classes are constructed here. The check compares values.
    The service does not construct a domain object.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['assertion'])
    def execute(self, assertion: Any, **kwargs) -> Any:
        '''
        Run the domain-object matrix and return the assertion.

        :param assertion: The domain_contract check.
        :type assertion: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The assertion when the protocol holds.
        :rtype: Any
        '''

        # Classify one assignment. This stays inside execute.
        def classify(model: Any, attribute: str, value: Any, error_code: str, with_model: bool) -> str:
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
                mismatch = self.check_service.codes(error.error_code, error_code)
                if mismatch:
                    return mismatch
                typed = self.check_service.equal(
                    error.model.get('type'),
                    type(model).__name__,
                )
                if typed and with_model:
                    return 'raise_for_validation did not describe the model.'
                if typed and not with_model:
                    return 'raise_for_validation did not fall back to the error title.'
                return ''
            return 'raise_for_validation did not raise.'

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
        mismatch = self.check_service.equal(domain_object.attribute, 'test')
        if mismatch:
            mismatch = 'Construction did not keep the attribute.'

        # An extra field is a ValidationError.
        if mismatch is None:
            try:
                TestDomainObject(attribute='test', unknown='nope')
            except ValidationError:
                pass
            else:
                mismatch = 'An extra field should be rejected.'

        # Assignment of an invalid value fails before it is classified.
        if mismatch is None:
            try:
                domain_object.attribute = ['not', 'a', 'string']
            except ValidationError:
                pass
            else:
                mismatch = 'Invalid assignment should fail.'

        # unpack_validation_error flattens a missing field.
        if mismatch is None:
            try:
                TestDomainObject()
            except ValidationError as error:
                violations = unpack_validation_error(error)
            else:
                violations = None
                mismatch = 'A missing field should fail.'
            if mismatch is None and (
                violations[0]['field'] != 'attribute'
                or set(violations[0]) != {'field', 'type', 'message'}
            ):
                mismatch = 'unpack_validation_error did not flatten the violation.'

        # describe_model reports identity and omits a non-primitive field.
        if mismatch is None:
            identified = TestIdentifiedObject(id='test_id', name='Test Name')
            descriptor = describe_model(identified)
            mismatch = self.check_service.equal(descriptor.get('type'), 'TestIdentifiedObject')
            if mismatch:
                mismatch = 'describe_model did not report the identity.'
            if mismatch is None:
                mismatch = self.check_service.equal(descriptor.get('id'), 'test_id')
                if mismatch:
                    mismatch = 'describe_model did not report the identity.'
            if mismatch is None and 'key' in descriptor:
                mismatch = 'describe_model reported an undeclared identity field.'
            if mismatch is None and 'id' in describe_model(Stub()):
                mismatch = 'describe_model kept a non-primitive identity.'
        else:
            identified = None

        # raise_for_validation, unknown attribute and invalid value.
        if mismatch is None:
            mismatch = classify(
                domain_object,
                'not_a_field',
                1,
                INVALID_MODEL_ATTRIBUTE_ID,
                False,
            ) or None
        if mismatch is None:
            mismatch = classify(
                identified,
                'not_a_field',
                1,
                INVALID_MODEL_ATTRIBUTE_ID,
                True,
            ) or None
        if mismatch is None:
            mismatch = classify(
                domain_object,
                'attribute',
                ['not', 'a', 'string'],
                INVALID_MODEL_VALUE_ID,
                False,
            ) or None
        if mismatch is None:
            mismatch = classify(
                identified,
                'name',
                ['not', 'a', 'string'],
                INVALID_MODEL_VALUE_ID,
                True,
            ) or None

        # A mismatch is the catalogued check failure. A hold returns the assertion.
        self.verify(
            expression=mismatch is None,
            error_code=a.error.PHASE_CHECK_FAILED_ID,
            check='domain_contract',
            detail=mismatch or '',
        )
        return assertion

# ** event: exercise_parameters_required
class ExerciseParametersRequired(CheckEvent):
    '''
    Runs the parameters_required matrix and returns the assertion.

    The harness event is constructed here. A valid call passes. A missing,
    blank, or None value raises COMMAND_PARAMETER_REQUIRED.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['assertion'])
    def execute(self, assertion: Any, **kwargs) -> Any:
        '''
        Run the decorator matrix and return the assertion.

        :param assertion: The parameters_required check.
        :type assertion: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The assertion when the matrix holds.
        :rtype: Any
        '''

        # One invalid call must name the missing parameter.
        def expect_required(event_cls: type, name: str, call_kwargs: Dict[str, Any]) -> str:
            try:
                DomainEvent.handle(event_cls, **call_kwargs)
            except TiferetError as error:
                mismatch = self.check_service.codes(
                    error.error_code,
                    a.error.COMMAND_PARAMETER_REQUIRED_ID,
                )
                if mismatch:
                    return f'{name} raised {error.error_code}.'
                if name not in str(error):
                    return f'{name} is not in the message.'
                return ''
            return f'{name} did not raise COMMAND_PARAMETER_REQUIRED.'

        # The harness owns the event. The names come from the check.
        required = list(assertion.names)

        class RequiredEvent(DomainEvent):
            '''Harness event for the parameters_required matrix.'''

            @DomainEvent.parameters_required(required)
            def execute(self, **event_kwargs):
                return 'ok'

        # A valid call passes. It is not a second meaning of error_code.
        result = DomainEvent.handle(
            RequiredEvent,
            **{name: 'value' for name in required},
        )
        mismatch = self.check_service.equal(result, 'ok')
        if mismatch:
            mismatch = 'A valid call should pass parameters_required.'
        if mismatch is None:
            for name in required:
                others = {
                    other: 'value'
                    for other in required
                    if other != name
                }
                for call_kwargs in (
                    others,
                    {**others, name: None},
                    {**others, name: ''},
                    {**others, name: '   '},
                ):
                    mismatch = expect_required(RequiredEvent, name, call_kwargs) or None
                    if mismatch:
                        break
                if mismatch:
                    break

        # A mismatch is the catalogued check failure. A hold returns the assertion.
        self.verify(
            expression=mismatch is None,
            error_code=a.error.PHASE_CHECK_FAILED_ID,
            check='parameters_required',
            detail=mismatch or '',
        )
        return assertion

# ** event: exercise_service_contract
class ExerciseServiceContract(CheckEvent):
    '''
    Locks one service method table and returns the assertion.

    The context already imported the service class. This event does not
    see the session.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['assertion', 'cls'])
    def execute(self,
                assertion: Any,
                cls: type,
                **kwargs) -> Any:
        '''
        Lock the method table and return the assertion.

        :param assertion: The service_contract check.
        :type assertion: Any
        :param cls: The service class the context imported.
        :type cls: type
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The assertion when the contract holds.
        :rtype: Any
        '''

        # Lock one method's parameters, defaults, annotations, and return.
        def lock_method(spec: Dict[str, Any]) -> str:
            method_name = spec['name']
            if not hasattr(cls, method_name):
                return f'Missing method {method_name}.'
            signature = inspect.signature(getattr(cls, method_name))
            params = list(signature.parameters)
            mismatch = self.check_service.equal(params, list(spec['params']))
            if mismatch:
                return f'{method_name} params {params} != {spec["params"]}.'
            for param_name, expected in (spec.get('defaults') or {}).items():
                if signature.parameters[param_name].default != expected:
                    return f'{method_name} default {param_name} does not match.'
            for param_name, expected in (spec.get('annotations') or {}).items():
                actual = _annotation_name(signature.parameters[param_name].annotation)
                if actual != expected:
                    return f'{method_name} annotation {param_name} is {actual!r}.'
            if 'returns' in spec and _annotation_name(signature.return_annotation) != spec['returns']:
                return f'{method_name} return annotation does not match.'
            return ''

        # The tester class is the service. This is not assert_contract.
        abstracts = list(assertion.abstracts or [])
        declared = set(getattr(cls, '__abstractmethods__', ()))
        mismatch = self.check_service.equal(declared, set(abstracts))
        if mismatch:
            mismatch = f'Abstracts {declared} != {set(abstracts)}.'
        if mismatch is None:
            for spec in assertion.methods or []:
                mismatch = lock_method(spec) or None
                if mismatch:
                    break
        if mismatch is None:
            for absent_name in assertion.absent or []:
                if hasattr(cls, absent_name):
                    mismatch = f'{absent_name} is not absent.'
                    break
        if mismatch is None and abstracts:
            try:
                cls()
            except TypeError:
                pass
            else:
                mismatch = 'Direct construction should fail.'

        # A mismatch is the catalogued check failure. A hold returns the assertion.
        self.verify(
            expression=mismatch is None,
            error_code=a.error.PHASE_CHECK_FAILED_ID,
            check='service_contract',
            detail=mismatch or '',
        )
        return assertion

# ** event: exercise_middleware_chain
class ExerciseMiddlewareChain(CheckEvent):
    '''
    Runs one middleware chain shape and returns the assertion.

    The shapes are a parameter. They are not six events. The harness owns
    the wrappers.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['assertion'])
    def execute(self, assertion: Any, **kwargs) -> Any:
        '''
        Run the named chain shape and return the assertion.

        :param assertion: The middleware_chain check.
        :type assertion: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The assertion when the shape holds.
        :rtype: Any
        '''

        # Drive one coroutine this event owns.
        def await_result(coro: Any) -> Any:
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                return asyncio.run(coro)
            box: Dict[str, Any] = {}

            def runner():
                try:
                    box['result'] = asyncio.run(coro)
                except BaseException as error:
                    box['error'] = error

            thread = threading.Thread(target=runner)
            thread.start()
            thread.join()
            if 'error' in box:
                raise box['error']
            return box.get('result')

        # Run a synchronous probe through the given wrappers.
        def run_chain(middleware: list, **chain_kwargs) -> Any:
            class Probe(DomainEvent):
                '''Harness event for a synchronous chain.'''

                def execute(self, **event_kwargs):
                    return 'ran'

            return DomainEvent.handle(Probe, middleware=middleware, **chain_kwargs)

        # No lambda in the YAML file. The wrappers are defined here.
        shape = assertion.middleware_chain
        mismatch = None
        if shape == 'none':
            result = run_chain([])
            mismatch = self.check_service.equal(result, 'ran')
            if mismatch:
                mismatch = 'An empty chain should return the event result.'
        elif shape == 'single':
            class Single:
                '''Harness wrapper that continues the chain.'''

                def __init__(self):
                    self.seen = False

                def __call__(self, event, kwargs, next_fn):
                    self.seen = True
                    return next_fn()

            wrapper = Single()
            result = run_chain([wrapper])
            mismatch = self.check_service.equal(result, 'ran')
            if mismatch or not wrapper.seen:
                mismatch = 'A single wrapper should continue the chain.'
        elif shape == 'order':
            order = []

            class Track:
                '''Harness wrapper that records entry and exit.'''

                def __init__(self, label):
                    self.label = label

                def __call__(self, event, kwargs, next_fn):
                    order.append(self.label)
                    result = next_fn()
                    order.append(f'{self.label}-post')
                    return result

            run_chain([Track('outer'), Track('inner')])
            mismatch = self.check_service.equal(
                order,
                ['outer', 'inner', 'inner-post', 'outer-post'],
            )
            if mismatch:
                mismatch = f'Wrapper order was {order}.'
        elif shape == 'capture':
            captured = {}

            class Capture:
                '''Harness wrapper that records the call.'''

                def __call__(self, event, kwargs, next_fn):
                    captured['event'] = event
                    captured['kwargs'] = dict(kwargs)
                    return next_fn()

            run_chain([Capture()], token='yes')
            mismatch = self.check_service.equal(captured.get('kwargs', {}).get('token'), 'yes')
            if mismatch:
                mismatch = 'The wrapper did not see the kwargs.'
            elif type(captured.get('event')).__name__ != 'Probe':
                mismatch = 'The wrapper did not see the event.'
        elif shape == 'intercept':
            called = {'value': False}

            class Probe(DomainEvent):
                '''Harness event that records whether execute ran.'''

                def execute(self, **event_kwargs):
                    called['value'] = True
                    return 'ran'

            class Intercept:
                '''Harness wrapper that stops the chain.'''

                def __call__(self, event, kwargs, next_fn):
                    return 'stopped'

            result = DomainEvent.handle(Probe, middleware=[Intercept()])
            mismatch = self.check_service.equal(result, 'stopped')
            if mismatch or called['value']:
                mismatch = 'Intercept should stop the chain.'
        elif shape == 'async':
            class AsyncProbe(AsyncDomainEvent):
                '''Harness async event.'''

                async def execute(self, **event_kwargs):
                    return 'async-ran'

            class AsyncWrap:
                '''Harness async wrapper.'''

                async def __call__(self, event, kwargs, next_fn):
                    return await next_fn()

            result = await_result(DomainEvent.handle_async(
                AsyncProbe,
                middleware=[AsyncWrap()],
            ))
            mismatch = self.check_service.equal(result, 'async-ran')
            if mismatch:
                mismatch = 'The async chain did not await the event.'
        else:
            self.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail=f'middleware_chain {shape} is not legal.',
            )

        # A mismatch is the catalogued check failure. A hold returns the assertion.
        self.verify(
            expression=mismatch is None,
            error_code=a.error.PHASE_CHECK_FAILED_ID,
            check='middleware_chain',
            detail=mismatch or '',
        )
        return assertion

# ** event: exercise_called
class ExerciseCalled(CheckEvent):
    '''
    Compares one resolved mock call and returns the assertion.

    The context finds the mock. This event does not see the session.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['assertion', 'method', 'spec'])
    def execute(self,
                assertion: Any,
                method: Any,
                spec: Dict[str, Any],
                **kwargs) -> Any:
        '''
        Compare the mock to the resolved call spec and return the assertion.

        :param assertion: The assert_called_once_with check.
        :type assertion: Any
        :param method: The mock method the context resolved.
        :type method: Any
        :param spec: The resolved call spec.
        :type spec: Dict[str, Any]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The assertion when the calls match.
        :rtype: Any
        '''

        # calls is the exact sequence. times 0 is not called.
        mismatch = None
        if 'calls' in spec:
            expected_calls = [
                call(*item.get('args', []), **item.get('kwargs', {}))
                for item in spec['calls']
            ]
            mismatch = self.check_service.equal(list(method.call_args_list), expected_calls)
            if mismatch:
                mismatch = f'Calls {method.call_args_list!r} != {expected_calls!r}.'
        else:
            times = spec.get('times', 1)
            if times == 0:
                if method.call_count != 0:
                    mismatch = f'Expected no calls, got {method.call_count}.'
                else:
                    mismatch = self.check_service.equal(method.call_count, 0)
            else:
                args = spec.get('args', [])
                call_kwargs = spec.get('kwargs', {})
                if times == 1 and ('args' in spec or 'kwargs' in spec):
                    try:
                        method.assert_called_once_with(*args, **call_kwargs)
                    except AssertionError as error:
                        mismatch = str(error)
                    else:
                        mismatch = self.check_service.equal(method.call_count, 1)
                elif method.call_count != times:
                    mismatch = f'Expected {times} calls, got {method.call_count}.'
                elif 'args' in spec or 'kwargs' in spec:
                    expected = call(*args, **call_kwargs)
                    for actual in method.call_args_list:
                        mismatch = self.check_service.equal(actual, expected)
                        if mismatch:
                            mismatch = f'{actual!r} != {expected!r}.'
                            break
                else:
                    mismatch = self.check_service.equal(method.call_count, times)

        # A mismatch is the catalogued check failure. A hold returns the assertion.
        self.verify(
            expression=mismatch is None,
            error_code=a.error.PHASE_CHECK_FAILED_ID,
            check='assert_called_once_with',
            detail=mismatch or '',
        )
        return assertion
