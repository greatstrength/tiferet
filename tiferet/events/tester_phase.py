"""Tiferet Phase Events"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from .core import DomainEvent, a
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
