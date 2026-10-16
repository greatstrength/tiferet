"""Tiferet Phase Events"""

# *** imports

# ** core
import asyncio
import threading
from typing import Any, Dict
from unittest.mock import call

# ** app
from .core import DomainEvent, AsyncDomainEvent, a
from ..interfaces.tester_check import CheckService

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
