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
from .core import DomainEvent, AsyncDomainEvent, a
from ..assets import TiferetError
from ..domain.core import (
    INVALID_MODEL_ATTRIBUTE_ID,
    INVALID_MODEL_VALUE_ID,
    DomainObject,
    ModelError,
    describe_model,
    unpack_validation_error,
)
from ..interfaces.tester_check import CheckService

# *** functions

# ** function: annotation_name
def _annotation_name(annotation: Any) -> str | None:
    '''
    Return the annotation name, or None when it is empty.

    :param annotation: The annotation to name.
    :type annotation: Any
    :return: The annotation name, or None when it is empty.
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
        Initialize the check event with its shared check service.

        :param check_service: The injected comparison service.
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
        Evaluate one comparison and return the assertion when it holds.

        :param assertion: The assertion describing the comparison to run.
        :type assertion: Any
        :param values: The resolved values for the comparison; defaults to None.
        :type values: Dict[str, Any]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The assertion when the check holds.
        :rtype: Any
        '''

        # Treat a missing values mapping as empty.
        resolved = values or {}

        # Read the comparison name and the outcome under check.
        name = assertion.check
        outcome = resolved.get('outcome')
        mismatch = None

        # Dispatch the named comparison through the check service.
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
            mismatch = self.check_service.equal(matched, not assertion.negate)
            if mismatch:
                if assertion.negate:
                    mismatch = (
                        f'{outcome!r} is an instance of {assertion.class_name}.'
                    )
                else:
                    mismatch = (
                        f'{outcome!r} is not an instance of '
                        f'{assertion.class_name}.'
                    )

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
            mismatch = self.check_service.equal(
                isinstance(cause, resolved.get('cls')),
                True,
            )
            if mismatch:
                mismatch = 'Cause type does not match.'
            else:
                mismatch = self.check_service.equal(
                    assertion.message in str(cause),
                    True,
                )
                if mismatch:
                    mismatch = 'Cause message does not match.'

        elif name == 'absent':
            if isinstance(outcome, dict):
                dumped = outcome
                mismatch = self.check_service.role_dump(dumped, assertion.absent)
                if mismatch:
                    mismatch = mismatch.replace(
                        ' is in the dump.',
                        ' is present.',
                    )
            elif hasattr(outcome, 'model_dump'):
                dumped = outcome.model_dump()
                mismatch = self.check_service.role_dump(dumped, assertion.absent)
                if mismatch:
                    mismatch = mismatch.replace(
                        ' is in the dump.',
                        ' is present.',
                    )
            else:
                mismatch = 'absent requires a mapping or a model.'

        elif name == 'event_base':
            mismatch = self.check_service.equal(
                issubclass(
                    resolved.get('event_cls'),
                    resolved.get('base_cls'),
                ),
                True,
            )
            if mismatch:
                event_cls = resolved.get('event_cls')
                mismatch = (
                    f'{event_cls.__name__} is not a {assertion.class_name}.'
                )
            else:
                instance = resolved.get('event_cls')(
                    **resolved.get('mocks', {}),
                )
                for mock_name, mock in resolved.get('mocks', {}).items():
                    mismatch = self.check_service.equal(
                        getattr(instance, mock_name) is mock,
                        True,
                    )
                    if mismatch:
                        mismatch = (
                            f'{mock_name} was not stored on the event.'
                        )
                        break

        else:
            mismatch = f'{name} is not a comparison.'

        # Verify the comparison held; raise the catalogued failure when not.
        self.verify(
            expression=mismatch is None,
            error_code=a.error.PHASE_CHECK_FAILED_ID,
            check=name,
            detail=mismatch or '',
        )

        # Return the assertion when the check holds.
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
    def execute(self,
                assertion: Any,
                **kwargs) -> Any:
        '''
        Run the mapper protocol and return the assertion when it holds.

        :param assertion: The assertion describing the protocol to run.
        :type assertion: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The assertion when the protocol holds.
        :rtype: Any
        '''

        # Define the domain source the mapper protocol copies.
        class SourceModel(DomainObject):
            '''
            Harness source model for from_model.
            '''

            id: str = Field(..., description='The identifier.')
            name: str = Field(..., description='The name.')

        # Build the source and run the mapper protocol through the check.
        source = SourceModel(id='test_id', name='Test Model')
        mismatch = self.check_service.mapper_contract(
            list(assertion.exclude or []),
            source,
        )

        # Verify the protocol held; raise the catalogued failure when not.
        self.verify(
            expression=mismatch is None,
            error_code=a.error.PHASE_CHECK_FAILED_ID,
            check='mapper_contract',
            detail=mismatch or '',
        )

        # Return the assertion when the protocol holds.
        return assertion

# ** event: exercise_domain_contract
class ExerciseDomainContract(CheckEvent):
    '''
    Runs the domain-object protocol and returns the assertion.

    The harness classes are constructed here. The check compares values. The
    service does not construct a domain object.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['assertion'])
    def execute(self,
                assertion: Any,
                **kwargs) -> Any:
        '''
        Run the domain-object protocol and return the assertion when it holds.

        :param assertion: The assertion describing the protocol to run.
        :type assertion: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The assertion when the protocol holds.
        :rtype: Any
        '''

        # Classify an assignment failure through raise_for_validation.
        def classify(model, attribute, value, error_code, with_model) -> str:

            # Assign the value; success means the assignment should have failed.
            try:
                setattr(model, attribute, value)
                return 'Assignment should have failed.'

            except ValidationError as error:

                # Convert the validation error into a classified ModelError.
                try:
                    if with_model:
                        ModelError.raise_for_validation(
                            error,
                            model=model,
                            attribute=attribute,
                        )

                    else:
                        ModelError.raise_for_validation(
                            error,
                            attribute=attribute,
                        )

                    return 'raise_for_validation did not raise.'

                except ModelError as error:

                    # Compare the classified code; return a codes mismatch as-is.
                    mismatch = self.check_service.codes(
                        error.error_code,
                        error_code,
                    )
                    if mismatch:
                        return mismatch

                    # Compare the described type to the model class name.
                    mismatch = self.check_service.equal(
                        error.model.get('type'),
                        type(model).__name__,
                    )
                    if mismatch and with_model:
                        return (
                            'raise_for_validation did not describe the model.'
                        )
                    if mismatch:
                        return (
                            'raise_for_validation did not fall back to the '
                            'error title.'
                        )
                    return ''

        # Define the harness models the check compares.
        class TestDomainObject(DomainObject):
            '''
            Harness domain object.
            '''

            attribute: str = Field(..., description='The attribute.')

        class TestIdentifiedObject(DomainObject):
            '''
            Harness identified domain object.
            '''

            id: str = Field(..., description='The identifier.')
            name: str = Field(..., description='The name.')

        class Stub:
            '''
            Harness stub with a non-primitive identity.
            '''

            id = {'nested': True}

        # Construct the domain object and confirm the attribute is kept.
        domain_object = TestDomainObject(attribute='test')
        mismatch = self.check_service.equal(domain_object.attribute, 'test')
        if mismatch:
            mismatch = 'Construction did not keep the attribute.'

        # Reject an extra field at construction.
        if not mismatch:
            try:
                TestDomainObject(attribute='test', unknown='nope')
                mismatch = 'An extra field should be rejected.'
            except ValidationError:
                pass

        # Reject an invalid assignment.
        if not mismatch:
            try:
                domain_object.attribute = ['not', 'a', 'string']
                mismatch = 'Invalid assignment should fail.'
            except ValidationError:
                pass

        # Reject a missing field and flatten the validation error.
        if not mismatch:
            try:
                TestDomainObject()
                mismatch = 'A missing field should fail.'
            except ValidationError as error:
                violations = unpack_validation_error(error)
                first = violations[0]
                if (
                    first.get('field') != 'attribute'
                    or set(first) != {'field', 'type', 'message'}
                ):
                    mismatch = (
                        'unpack_validation_error did not flatten the '
                        'violation.'
                    )

        # Describe an identified model and reject a non-primitive identity.
        if not mismatch:
            identified = TestIdentifiedObject(id='test_id', name='Test Name')
            descriptor = describe_model(identified)
            mismatch = self.check_service.equal(
                descriptor.get('type'),
                'TestIdentifiedObject',
            )
            if not mismatch:
                mismatch = self.check_service.equal(
                    descriptor.get('id'),
                    'test_id',
                )
            if mismatch:
                mismatch = 'describe_model did not report the identity.'
            elif 'key' in descriptor:
                mismatch = (
                    'describe_model reported an undeclared identity field.'
                )
            elif 'id' in describe_model(Stub()):
                mismatch = 'describe_model kept a non-primitive identity.'

        # Classify an unknown attribute without a model descriptor.
        if not mismatch:
            mismatch = classify(
                domain_object,
                'not_a_field',
                1,
                INVALID_MODEL_ATTRIBUTE_ID,
                False,
            ) or None

        # Classify an unknown attribute with a model descriptor.
        if not mismatch:
            mismatch = classify(
                identified,
                'not_a_field',
                1,
                INVALID_MODEL_ATTRIBUTE_ID,
                True,
            ) or None

        # Classify an invalid value without a model descriptor.
        if not mismatch:
            mismatch = classify(
                domain_object,
                'attribute',
                ['not', 'a', 'string'],
                INVALID_MODEL_VALUE_ID,
                False,
            ) or None

        # Classify an invalid value with a model descriptor.
        if not mismatch:
            mismatch = classify(
                identified,
                'name',
                ['not', 'a', 'string'],
                INVALID_MODEL_VALUE_ID,
                True,
            ) or None

        # Verify the protocol held; raise the catalogued failure when not.
        self.verify(
            expression=mismatch is None,
            error_code=a.error.PHASE_CHECK_FAILED_ID,
            check='domain_contract',
            detail=mismatch or '',
        )

        # Return the assertion when the protocol holds.
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
    def execute(self,
                assertion: Any,
                **kwargs) -> Any:
        '''
        Run the parameters_required matrix and return the assertion when it
        holds.

        :param assertion: The assertion describing the protocol to run.
        :type assertion: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The assertion when the protocol holds.
        :rtype: Any
        '''

        # Read the required names from the assertion.
        required = list(assertion.names)

        # Define the harness event for the parameters_required matrix.
        class RequiredEvent(DomainEvent):
            '''
            Harness event for the parameters_required matrix.
            '''

            @DomainEvent.parameters_required(required)
            def execute(self, **kwargs):
                return 'ok'

        # Expect COMMAND_PARAMETER_REQUIRED for one missing name.
        def expect_required(event_cls, name, call_kwargs) -> str:

            # Handle the event and classify a missing-parameter failure.
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

        # A valid call must pass parameters_required.
        result = DomainEvent.handle(
            RequiredEvent,
            **{name: 'value' for name in required},
        )
        mismatch = self.check_service.equal(result, 'ok')
        if mismatch:
            mismatch = 'A valid call should pass parameters_required.'

        # Reject each required name when absent, None, blank, or whitespace.
        if not mismatch:
            for name in required:
                others = {
                    other: 'value'
                    for other in required
                    if other != name
                }
                cases = [
                    dict(others),
                    {**others, name: None},
                    {**others, name: ''},
                    {**others, name: '   '},
                ]
                for call_kwargs in cases:
                    mismatch = expect_required(
                        RequiredEvent,
                        name,
                        call_kwargs,
                    ) or None
                    if mismatch:
                        break
                if mismatch:
                    break

        # Verify the protocol held; raise the catalogued failure when not.
        self.verify(
            expression=mismatch is None,
            error_code=a.error.PHASE_CHECK_FAILED_ID,
            check='parameters_required',
            detail=mismatch or '',
        )

        # Return the assertion when the protocol holds.
        return assertion

# ** event: exercise_service_contract
class ExerciseServiceContract(CheckEvent):
    '''
    Locks one service method table and returns the assertion.

    The context already imported the service class. This event does not see
    the session.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['assertion', 'cls'])
    def execute(self,
                assertion: Any,
                cls: Any,
                **kwargs) -> Any:
        '''
        Lock one service method table and return the assertion when it holds.

        :param assertion: The assertion describing the protocol to run.
        :type assertion: Any
        :param cls: The already-imported service class to lock.
        :type cls: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The assertion when the protocol holds.
        :rtype: Any
        '''

        # Lock one method spec against the imported class.
        def lock_method(spec) -> str:

            # Reject a missing method.
            method_name = spec['name']
            if not hasattr(cls, method_name):
                return f'Missing method {method_name}.'

            # Compare the parameter names through the check.
            signature = inspect.signature(getattr(cls, method_name))
            params = list(signature.parameters)
            mismatch = self.check_service.equal(
                params,
                list(spec['params']),
            )
            if mismatch:
                return f'{method_name} params {params} != {spec["params"]}.'

            # Compare declared defaults without the check service.
            for param_name, expected in (spec.get('defaults') or {}).items():
                if signature.parameters[param_name].default != expected:
                    return (
                        f'{method_name} default {param_name} does not match.'
                    )

            # Compare declared annotations without the check service.
            for param_name, expected in (
                spec.get('annotations') or {}
            ).items():
                actual = _annotation_name(
                    signature.parameters[param_name].annotation,
                )
                if actual != expected:
                    return (
                        f'{method_name} annotation {param_name} is {actual!r}.'
                    )

            # Compare a declared return annotation without the check service.
            if 'returns' in spec:
                actual = _annotation_name(signature.return_annotation)
                if actual != spec['returns']:
                    return f'{method_name} return annotation does not match.'

            return ''

        # Compare declared abstracts to the class abstract method set.
        abstracts = list(assertion.abstracts or [])
        declared = set(getattr(cls, '__abstractmethods__', ()))
        mismatch = self.check_service.equal(declared, set(abstracts))
        if mismatch:
            mismatch = f'Abstracts {declared} != {set(abstracts)}.'

        # Lock each method spec.
        if not mismatch:
            for spec in assertion.methods or []:
                mismatch = lock_method(spec) or None
                if mismatch:
                    break

        # Reject a name that should be absent.
        if not mismatch:
            for absent_name in assertion.absent or []:
                if hasattr(cls, absent_name):
                    mismatch = f'{absent_name} is not absent.'
                    break

        # Direct construction must fail when abstracts are declared.
        if not mismatch and abstracts:
            try:
                cls()
                mismatch = 'Direct construction should fail.'
            except TypeError:
                pass

        # Verify the protocol held; raise the catalogued failure when not.
        self.verify(
            expression=mismatch is None,
            error_code=a.error.PHASE_CHECK_FAILED_ID,
            check='service_contract',
            detail=mismatch or '',
        )

        # Return the assertion when the protocol holds.
        return assertion

# ** event: exercise_middleware_chain
class ExerciseMiddlewareChain(CheckEvent):
    '''
    Runs one middleware chain shape and returns the assertion.

    The shapes are a parameter. They are not six events. The harness
    owns the wrappers.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['assertion'])
    def execute(self, assertion: Any, **kwargs) -> Any:
        '''
        Run one middleware chain shape and return the assertion when it holds.

        :param assertion: The assertion naming the chain shape to run.
        :type assertion: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The assertion when the shape holds.
        :rtype: Any
        '''

        # Await a coroutine from this sync event, using a thread when a loop runs.
        def await_result(coro):
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                return asyncio.run(coro)

            box = {}

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

            return box['result']

        # Run a probe event through one synchronous middleware chain.
        def run_chain(middleware, **chain_kwargs):
            class Probe(DomainEvent):
                '''Harness event for a synchronous chain.'''

                def execute(self, **kwargs):
                    return 'ran'

            return DomainEvent.handle(
                Probe,
                middleware=middleware,
                **chain_kwargs,
            )

        # Read the named chain shape.
        shape = assertion.middleware_chain

        # Reject an illegal shape without verifying or comparing.
        if shape not in (
            'none',
            'single',
            'order',
            'capture',
            'intercept',
            'async',
        ):
            self.raise_error(
                a.error.PHASE_STEP_FAILED_ID,
                detail=f'middleware_chain {shape} is not legal.',
            )

        # Run the named shape and replace a service mismatch with its detail.
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
            class Capture:
                '''Harness wrapper that records the call.'''

                def __call__(self, event, kwargs, next_fn):
                    self.event = event
                    self.kwargs = dict(kwargs)
                    return next_fn()

            wrapper = Capture()
            run_chain([wrapper], token='yes')
            mismatch = self.check_service.equal(
                wrapper.kwargs.get('token'),
                'yes',
            )
            if mismatch:
                mismatch = 'The wrapper did not see the kwargs.'
            else:
                mismatch = self.check_service.equal(
                    wrapper.event.__class__.__name__,
                    'Probe',
                )
                if mismatch:
                    mismatch = 'The wrapper did not see the event.'

        elif shape == 'intercept':
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
            mismatch = self.check_service.equal(result, 'stopped')
            if mismatch or called['value']:
                mismatch = 'Intercept should stop the chain.'

        elif shape == 'async':
            class AsyncProbe(AsyncDomainEvent):
                '''Harness async event.'''

                async def execute(self, **kwargs):
                    return 'async-ran'

            class AsyncWrap:
                '''Harness async wrapper.'''

                async def __call__(self, event, kwargs, next_fn):
                    return await next_fn()

            result = await_result(
                DomainEvent.handle_async(
                    AsyncProbe,
                    middleware=[AsyncWrap()],
                ),
            )
            mismatch = self.check_service.equal(result, 'async-ran')
            if mismatch:
                mismatch = 'The async chain did not await the event.'

        # Verify the shape held; raise the catalogued failure when not.
        self.verify(
            expression=mismatch is None,
            error_code=a.error.PHASE_CHECK_FAILED_ID,
            check='middleware_chain',
            detail=mismatch or '',
        )

        # Return the assertion when the check holds.
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
        Compare one resolved mock call and return the assertion when the calls match.

        :param assertion: The assertion for the call comparison.
        :type assertion: Any
        :param method: The resolved mock already found by the context.
        :type method: Any
        :param spec: The call spec with times, args, kwargs, or calls.
        :type spec: Dict[str, Any]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The assertion when the calls match.
        :rtype: Any
        '''

        # Compare the resolved mock to the call spec.
        mismatch = None

        if 'calls' in spec:
            expected_calls = [
                call(*item.get('args', []), **item.get('kwargs', {}))
                for item in spec['calls']
            ]
            mismatch = self.check_service.equal(
                list(method.call_args_list),
                expected_calls,
            )
            if mismatch:
                mismatch = (
                    f'Calls {method.call_args_list!r} != {expected_calls!r}.'
                )

        else:
            times = spec.get('times', 1)

            if times == 0 and method.call_count != 0:
                mismatch = f'Expected no calls, got {method.call_count}.'

            elif times == 0 and method.call_count == 0:
                mismatch = self.check_service.equal(method.call_count, 0)

            elif times == 1 and ('args' in spec or 'kwargs' in spec):
                args = spec.get('args', [])
                call_kwargs = spec.get('kwargs', {})

                # Compare the single call through the mock assertion helper.
                try:
                    method.assert_called_once_with(*args, **call_kwargs)
                except AssertionError as error:
                    mismatch = str(error)
                else:
                    mismatch = self.check_service.equal(method.call_count, 1)

            elif method.call_count != times:
                mismatch = f'Expected {times} calls, got {method.call_count}.'

            elif 'args' in spec or 'kwargs' in spec:
                args = spec.get('args', [])
                call_kwargs = spec.get('kwargs', {})
                expected = call(*args, **call_kwargs)

                # Stop at the first mismatched actual call.
                for actual in method.call_args_list:
                    mismatch = self.check_service.equal(actual, expected)
                    if mismatch:
                        mismatch = f'{actual!r} != {expected!r}.'
                        break

            else:
                mismatch = self.check_service.equal(method.call_count, times)

        # Verify the calls matched; raise the catalogued failure when not.
        self.verify(
            expression=mismatch is None,
            error_code=a.error.PHASE_CHECK_FAILED_ID,
            check='assert_called_once_with',
            detail=mismatch or '',
        )

        # Return the assertion when the check holds.
        return assertion
