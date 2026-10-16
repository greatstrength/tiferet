"""Tiferet Phase Event Tests"""

# *** imports

# ** core
from unittest.mock import Mock

# ** infra
import pytest

# ** app
from tiferet import use_tester
from tiferet.events.core import DomainEvent, TiferetError, a
from tiferet.interfaces.tester_check import CheckService
from tiferet.events.tester_phase import (
    CheckEvent,
    EvaluateAssertion,
    ExerciseCalled,
    ExerciseMiddlewareChain,
)

# *** fixtures

# ** fixture: check_service
@pytest.fixture
def check_service() -> Mock:
    '''
    A mock CheckService for phase event handle rows.

    :return: A Mock whose spec is CheckService.
    :rtype: Mock
    '''

    # Build a mock comparison service for handle rows.
    return Mock(spec=CheckService)

# *** testers

# ** tester: test_check_event
class TestCheckEvent:
    '''
    Tests for the CheckEvent base event.
    '''

    # * test: stores_check_service
    def test_stores_check_service(self, check_service):
        '''
        Construct CheckEvent and assert it stores the same check service.

        :param check_service: The mock CheckService fixture.
        :type check_service: Mock
        '''

        # Construct the subject with the fixture mock.
        result = CheckEvent(check_service=check_service)

        # Assert the outcome's check_service is that same mock.
        assert result.check_service is check_service

    # * test: omits_execute
    def test_omits_execute(self):
        '''
        Assert execute is absent from CheckEvent's own namespace.
        '''

        # Read the class's own namespace and assert execute is absent.
        assert 'execute' not in CheckEvent.__dict__

# ** tester: test_evaluate_assertion
@use_tester(
    type='domain_event',
    target_cls=EvaluateAssertion,
    dependencies={
        'check_service': {
            'module_path': 'tiferet.interfaces.tester_check',
            'class_name': 'CheckService',
        },
    },
    sample_kwargs={
        'assertion': Mock(check='equals'),
    },
    required_params=['assertion'],
)
class TestEvaluateAssertion:
    '''
    Tests for EvaluateAssertion.
    '''

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''
        Assert missing assertion raises COMMAND_PARAMETER_REQUIRED.

        :param test_ctx: The bound domain-event tester context.
        :type test_ctx: DomainEventTesterContext
        '''

        # Assert the harness required-parameter contract for assertion.
        test_ctx.assert_missing_required_params()

    # * test: dispatches_equals
    def test_dispatches_equals(self, check_service):
        '''
        Assert equals that holds returns the same assertion object.

        :param check_service: The mock CheckService fixture.
        :type check_service: Mock
        '''

        # Configure equals to report a match and build the assertion.
        check_service.equal.return_value = None
        assertion = Mock()
        assertion.check = 'equals'

        # Handle the event with equals values.
        result = DomainEvent.handle(
            EvaluateAssertion,
            dependencies={'check_service': check_service},
            assertion=assertion,
            values={'outcome': 1, 'equals': 1},
        )

        # Assert the outcome is that same assertion object.
        assert result is assertion

    # * test: mismatch_raises_phase_check_failed
    def test_mismatch_raises_phase_check_failed(self, check_service):
        '''
        Assert equals that fails raises PHASE_CHECK_FAILED naming equals.

        :param check_service: The mock CheckService fixture.
        :type check_service: Mock
        '''

        # Configure equals to report a mismatch and build the assertion.
        check_service.equal.return_value = '1 != 2.'
        assertion = Mock()
        assertion.check = 'equals'

        # Handle the event and expect the catalogued phase-check failure.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                EvaluateAssertion,
                dependencies={'check_service': check_service},
                assertion=assertion,
                values={'outcome': 1, 'equals': 1},
            )

        # Assert the code and that the message names the equals check.
        assert exc_info.value.error_code == a.error.PHASE_CHECK_FAILED_ID
        assert 'equals' in str(exc_info.value)

    # * test: declares_execute_only
    def test_declares_execute_only(self):
        '''
        Assert EvaluateAssertion's own namespace declares only execute.
        '''

        # Read the class's own namespace for execute, init, and check_service.
        assert 'execute' in EvaluateAssertion.__dict__
        assert '__init__' not in EvaluateAssertion.__dict__
        assert 'check_service' not in EvaluateAssertion.__dict__

# ** tester: test_exercise_middleware_chain
@use_tester(
    type='domain_event',
    target_cls=ExerciseMiddlewareChain,
    dependencies={
        'check_service': {
            'module_path': 'tiferet.interfaces.tester_check',
            'class_name': 'CheckService',
        },
    },
    sample_kwargs={
        'assertion': Mock(),
    },
    required_params=['assertion'],
)
class TestExerciseMiddlewareChain:
    '''
    Tests for ExerciseMiddlewareChain.
    '''

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''
        Assert missing assertion raises COMMAND_PARAMETER_REQUIRED.

        :param test_ctx: The bound domain-event tester context.
        :type test_ctx: DomainEventTesterContext
        '''

        # Assert the harness required-parameter contract for assertion.
        test_ctx.assert_missing_required_params()

    # * test: success
    def test_success(self, check_service):
        '''
        Assert equal returning null then handle returns that same assertion object.

        :param check_service: The mock CheckService fixture.
        :type check_service: Mock
        '''

        # Configure equal to report a match and build a none-shape assertion.
        check_service.equal.return_value = None
        assertion = Mock()
        assertion.middleware_chain = 'none'

        # Handle the event with the none chain shape.
        result = DomainEvent.handle(
            ExerciseMiddlewareChain,
            dependencies={'check_service': check_service},
            assertion=assertion,
        )

        # Assert the outcome is that same assertion object.
        assert result is assertion

    # * test: failure
    def test_failure(self, check_service):
        '''
        Assert a mismatch then handle raises PHASE_CHECK_FAILED naming middleware_chain.

        :param check_service: The mock CheckService fixture.
        :type check_service: Mock
        '''

        # Configure equal to report a mismatch and build a none-shape assertion.
        check_service.equal.return_value = 'mismatch'
        assertion = Mock()
        assertion.middleware_chain = 'none'

        # Handle the event and expect the catalogued phase-check failure.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                ExerciseMiddlewareChain,
                dependencies={'check_service': check_service},
                assertion=assertion,
            )

        # Assert the code and that the message names the middleware_chain check.
        assert exc_info.value.error_code == a.error.PHASE_CHECK_FAILED_ID
        assert 'middleware_chain' in str(exc_info.value)

    # * test: illegal_shape
    def test_illegal_shape(self, check_service):
        '''
        Assert middleware_chain sideways raises PHASE_STEP_FAILED naming sideways.

        :param check_service: The mock CheckService fixture.
        :type check_service: Mock
        '''

        # Build an assertion whose chain shape is not legal.
        assertion = Mock()
        assertion.middleware_chain = 'sideways'

        # Handle the event and expect the catalogued phase-step failure.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                ExerciseMiddlewareChain,
                dependencies={'check_service': check_service},
                assertion=assertion,
            )

        # Assert the code and that the message names sideways.
        assert exc_info.value.error_code == a.error.PHASE_STEP_FAILED_ID
        assert 'sideways' in str(exc_info.value)

    # * test: declares_execute_only
    def test_declares_execute_only(self):
        '''
        Assert ExerciseMiddlewareChain's own namespace declares only execute.
        '''

        # Read the class's own namespace for execute, init, and check_service.
        assert 'execute' in ExerciseMiddlewareChain.__dict__
        assert '__init__' not in ExerciseMiddlewareChain.__dict__
        assert 'check_service' not in ExerciseMiddlewareChain.__dict__

# ** tester: test_exercise_called
@use_tester(
    type='domain_event',
    target_cls=ExerciseCalled,
    dependencies={
        'check_service': {
            'module_path': 'tiferet.interfaces.tester_check',
            'class_name': 'CheckService',
        },
    },
    sample_kwargs={
        'assertion': Mock(),
        'method': Mock(),
        'spec': {},
    },
    required_params=['assertion', 'method', 'spec'],
)
class TestExerciseCalled:
    '''
    Tests for ExerciseCalled.
    '''

    # * test: missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''
        Assert missing assertion, method, or spec raises COMMAND_PARAMETER_REQUIRED.

        :param test_ctx: The bound domain-event tester context.
        :type test_ctx: DomainEventTesterContext
        '''

        # Assert the harness required-parameter contract for assertion, method, and spec.
        test_ctx.assert_missing_required_params()

    # * test: success
    def test_success(self, check_service):
        '''
        Assert equal returning null then handle returns that same assertion object.

        :param check_service: The mock CheckService fixture.
        :type check_service: Mock
        '''

        # Configure equal to report a match and a method with no calls.
        check_service.equal.return_value = None
        assertion = Mock()
        method = Mock()
        method.call_count = 0

        # Handle the event with times 0.
        result = DomainEvent.handle(
            ExerciseCalled,
            dependencies={'check_service': check_service},
            assertion=assertion,
            method=method,
            spec={'times': 0},
        )

        # Assert the outcome is that same assertion object.
        assert result is assertion

    # * test: failure
    def test_failure(self, check_service):
        '''
        Assert call_count 1 then handle raises PHASE_CHECK_FAILED naming assert_called_once_with.

        :param check_service: The mock CheckService fixture.
        :type check_service: Mock
        '''

        # Build a method that was called once; equal is not the deciding return.
        assertion = Mock()
        method = Mock()
        method.call_count = 1

        # Handle the event with times 0 and expect the catalogued phase-check failure.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                ExerciseCalled,
                dependencies={'check_service': check_service},
                assertion=assertion,
                method=method,
                spec={'times': 0},
            )

        # Assert the code and that the message names assert_called_once_with.
        assert exc_info.value.error_code == a.error.PHASE_CHECK_FAILED_ID
        assert 'assert_called_once_with' in str(exc_info.value)

    # * test: declares_execute_only
    def test_declares_execute_only(self):
        '''
        Assert ExerciseCalled's own namespace declares only execute.
        '''

        # Read the class's own namespace for execute, init, and check_service.
        assert 'execute' in ExerciseCalled.__dict__
        assert '__init__' not in ExerciseCalled.__dict__
        assert 'check_service' not in ExerciseCalled.__dict__
