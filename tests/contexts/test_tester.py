"""Tests for Tiferet Tester Context Composition"""

# *** imports
# ** infra
import pytest

# ** app
from tiferet import add_verification
from tiferet.contexts.core import BaseContext
from tiferet.contexts.request import RequestContext
from tiferet.contexts.tester import (
    TestRequestContext as _TestRequestContext,
    create_aggregate_tester,
    create_domain_tester,
    create_transfer_object_tester,
)
from tiferet.domain import Request, Verification
from tiferet.domain.error import ErrorMessage
from tiferet.mappers.error import (
    ErrorAggregate,
    ErrorConfigObject,
)

# *** tests

# ** test: generated_tester_classes_construct_targets
def test_generated_tester_classes_construct_targets() -> None:
    '''
    Test that every tester decorator adds make_target and the target fixture
    for the target shape its assertions need.
    '''

    # Decorate one class for each tester variant.
    @create_domain_tester(
        domain_cls=ErrorMessage,
        sample_data={
            'lang': 'en_US',
            'text': 'An error occurred.',
        },
        equality_fields=[
            'lang',
            'text',
        ],
    )
    class DomainTester:
        pass

    @create_aggregate_tester(
        aggregate_cls=ErrorAggregate,
        sample_data={
            'id': 'TEST_ERROR',
            'name': 'Test Error',
        },
        equality_fields=[
            'id',
            'name',
        ],
    )
    class AggregateTester:
        pass

    @create_transfer_object_tester(
        transfer_cls=ErrorConfigObject,
        aggregate_cls=ErrorAggregate,
        sample_data={
            'id': 'TEST_ERROR',
            'name': 'Test Error',
        },
        aggregate_sample_data={
            'id': 'TEST_ERROR',
            'name': 'Test Error',
        },
    )
    class TransferObjectTester:
        pass

    # Assert every decorated class exposes its universal target construction API.
    assert isinstance(DomainTester().make_target(), ErrorMessage)
    assert isinstance(AggregateTester().make_target(), ErrorAggregate)
    assert isinstance(TransferObjectTester().make_target(), ErrorAggregate)
    assert hasattr(DomainTester, 'target')
    assert hasattr(AggregateTester, 'target')
    assert hasattr(TransferObjectTester, 'target')

# ** test: tester_decorator_preserves_explicit_members
def test_tester_decorator_preserves_explicit_members() -> None:
    '''
    Test that a decorator preserves an explicitly declared generated-method
    override on the consumer's own class.
    '''

    # Decorate a class that supplies its own construction assertion.
    @create_domain_tester(
        domain_cls=ErrorMessage,
        sample_data={
            'lang': 'en_US',
            'text': 'An error occurred.',
        },
        equality_fields=[
            'lang',
            'text',
        ],
    )
    class OverrideTester:

        # * test: test_new
        def test_new(self) -> str:
            '''Return a sentinel proving this explicit method was retained.'''

            return 'consumer override'

    # Assert the decorator retained the consumer's own member.
    assert OverrideTester().test_new() == 'consumer override'
    assert hasattr(OverrideTester, 'target')

# ** test: test_request_context_preserves_request_context_registration
def test_request_context_preserves_request_context_registration() -> None:
    '''
    Test that importing TestRequestContext does not replace RequestContext in
    the domain-context registry.
    '''

    # Assert the subclass does not redeclare a domain registration.
    assert 'domain_type' not in _TestRequestContext.__dict__

    # Assert Request retains its original registered context.
    assert BaseContext.for_domain(Request) is RequestContext

# ** test: test_request_context_given_merges_state_and_returns_self
def test_request_context_given_merges_state_and_returns_self() -> None:
    '''
    Test that given shallowly merges state, lets later values win, and supports
    fluent chaining.
    '''

    # Create a test request and merge duplicate state keys.
    context = _TestRequestContext()
    returned_context = context.given(a=1).given(a=2)

    # Assert the original context was returned with the final shallow state.
    assert returned_context is context
    assert context.data == {'a': 2}

# ** test: test_request_context_verify_normalizes_predicates_and_literals
def test_request_context_verify_normalizes_predicates_and_literals() -> None:
    '''
    Test that verify queues exactly one Verification for callable and literal
    expectations while returning the original fluent context.
    '''

    # Queue a callable and literal expectation on one context.
    context = _TestRequestContext()
    predicate = lambda outcome: outcome == 3
    assert context.verify(predicate) is context
    assert context.verify(3, message='literal outcome') is context

    # Assert both inputs have the unified Verification representation.
    assert len(context.verifications) == 2
    assert all(
        isinstance(verification, Verification)
        for verification in context.verifications
    )
    assert context.verifications[0].predicate is predicate
    assert context.verifications[0].source is predicate
    assert context.verifications[1].source == 3
    assert context.verifications[1].predicate(3)

# ** test: test_request_context_evaluates_all_verifications_and_clears_queue
def test_request_context_evaluates_all_verifications_and_clears_queue() -> None:
    '''
    Test that verification failures aggregate once and the consumed queue is
    cleared on both failing and passing evaluation paths.
    '''

    # Queue two failing and one passing assertion against the shared outcome.
    context = _TestRequestContext()
    context.verify(lambda outcome: outcome == 1, message='first failure')
    context.verify(lambda outcome: outcome == 3, message='second failure')
    context.verify(lambda outcome: outcome == 2, message='passing check')
    context.capture_outcome(2)

    # Assert all failures appear in one assertion and the queue is consumed.
    with pytest.raises(AssertionError) as exc_info:
        context.evaluate_verifications()
    assert 'first failure' in str(exc_info.value)
    assert 'second failure' in str(exc_info.value)
    assert len(context.verifications) == 0

    # Queue a passing assertion and assert successful evaluation also consumes it.
    context.verify(2)
    assert context.evaluate_verifications() is None
    assert len(context.verifications) == 0

# ** test: test_request_context_records_raised_predicates_and_continues
def test_request_context_records_raised_predicates_and_continues() -> None:
    '''
    Test that a raised predicate is recorded as a failure and does not stop a
    subsequent verification from running.
    '''

    # Define a predicate that errors and another that records its evaluation.
    evaluated = []

    def raises_error(outcome):
        raise ValueError('predicate error')

    def records_evaluation(outcome):
        evaluated.append(outcome)
        return False

    # Queue both predicates and capture their shared outcome.
    context = _TestRequestContext()
    context.verify(raises_error, message='raised predicate')
    context.verify(records_evaluation, message='continued predicate')
    context.capture_outcome('outcome')

    # Assert both failures are reported and the later predicate was evaluated.
    with pytest.raises(AssertionError) as exc_info:
        context.evaluate_verifications()
    assert 'raised predicate' in str(exc_info.value)
    assert 'predicate error' in str(exc_info.value)
    assert 'continued predicate' in str(exc_info.value)
    assert evaluated == ['outcome']
    assert len(context.verifications) == 0

# ** test: add_verification_attaches_metadata_without_wrapping
def test_add_verification_attaches_metadata_without_wrapping() -> None:
    '''
    Test that the root-exported decorator preserves function identity and
    accumulates Verification metadata in application order.
    '''

    # Declare a plain function with no decorator-created wrapper.
    def target() -> str:
        return 'called once'

    # Decorate the same function repeatedly with distinct expectations.
    first = add_verification(1, message='first')
    second = add_verification(lambda outcome: outcome == 2, message='second')
    assert first(target) is target
    assert second(target) is target

    # Assert the function behavior and ordered metadata remain intact.
    assert target() == 'called once'
    assert [item.message for item in target.__tiferet_verifications__] == [
        'first',
        'second',
    ]
    assert all(
        isinstance(verification, Verification)
        for verification in target.__tiferet_verifications__
    )
