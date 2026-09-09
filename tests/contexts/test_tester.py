"""Tests for Tiferet Tester Contexts"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.assets import TiferetError
from tiferet.contexts.core import BaseContext
from tiferet.contexts.request import RequestContext
from tiferet.contexts.tester import (
    AggregateTesterContext,
    DomainTesterContext,
    TestRequestContext as _TestRequestContext,
    TestSessionContext as _TestSessionContext,
    TEST_PRESET_CACHE_PREFIX,
    TESTER_CACHE_PREFIX,
    TransferObjectTesterContext,
    add_default_test_presets,
    add_default_testers,
)
from tiferet.contexts.cache import CacheContext
from tiferet.domain import (
    AggregateTesterObject,
    DomainTesterObject,
    Request,
    TransferObjectTesterObject,
    Verification,
)
from tiferet.domain import INVALID_MODEL_ATTRIBUTE_ID
from tiferet.domain.error import ErrorMessage
from tiferet.mappers.error import (
    ErrorAggregate,
    ErrorConfigObject,
)

# *** tests

# ** test: variant_tester_contexts_bind_from_domain
def test_variant_tester_contexts_bind_from_domain() -> None:
    '''Test that each variant context registers and constructs via from_domain.'''

    # Bind one tester of each existing variant.
    domain_tester = DomainTesterObject(
        id='domain.ErrorMessage',
        module_path=ErrorMessage.__module__,
        class_name=ErrorMessage.__name__,
        sample_data={'lang': 'en_US', 'text': 'An error occurred.'},
        equality_fields=['lang', 'text'],
    )
    aggregate_tester = AggregateTesterObject(
        id='aggregate.ErrorAggregate',
        module_path=ErrorAggregate.__module__,
        class_name=ErrorAggregate.__name__,
        sample_data={'id': 'TEST_ERROR', 'name': 'Test Error'},
        equality_fields=['id', 'name'],
    )
    transfer_tester = TransferObjectTesterObject(
        id='transfer_object.ErrorConfigObject',
        module_path=ErrorConfigObject.__module__,
        class_name=ErrorConfigObject.__name__,
        sample_data={'id': 'TEST_ERROR', 'name': 'Test Error'},
        equality_fields=['id', 'name'],
        aggregate_module_path=ErrorAggregate.__module__,
        aggregate_class_name=ErrorAggregate.__name__,
        aggregate_sample_data={'id': 'TEST_ERROR', 'name': 'Test Error'},
    )

    # Construct each context from its bound domain object.
    domain_context = DomainTesterContext.from_domain(domain_tester)
    aggregate_context = AggregateTesterContext.from_domain(aggregate_tester)
    transfer_context = TransferObjectTesterContext.from_domain(transfer_tester)

    # Assert registry mapping and ordinary construction methods.
    assert BaseContext.for_domain(DomainTesterObject) is DomainTesterContext
    assert BaseContext.for_domain(AggregateTesterObject) is AggregateTesterContext
    assert BaseContext.for_domain(TransferObjectTesterObject) is TransferObjectTesterContext
    assert isinstance(domain_context.make_target(), ErrorMessage)
    assert isinstance(aggregate_context.make_target(), ErrorAggregate)
    assert isinstance(transfer_context.make_target(), ErrorAggregate)

    # Exercise ordinary assertion methods on the bound testers.
    domain_context.assert_new()
    domain_context.assert_description()
    aggregate_context.assert_new()
    aggregate_context.assert_set_attribute()
    transfer_context.assert_map()
    transfer_context.assert_from_model()
    transfer_context.assert_round_trip()

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

# ** test: add_default_testers
def test_add_default_testers_seeds_polymorphic_domain_objects() -> None:
    '''
    Test the dedicated tester decorator validates polymorphic definitions into
    domain objects before storing them under the tester cache namespace.
    '''

    # Decorate a minimal bare cache builder with one tester of each variant.
    builder = add_default_testers(
        {
            'domain.ErrorMessage': {
                'type': 'domain',
                'module_path': 'tiferet.domain.error',
                'class_name': 'ErrorMessage',
                'sample_data': {},
            },
            'aggregate.ErrorAggregate': {
                'type': 'aggregate',
                'module_path': 'tiferet.mappers.error',
                'class_name': 'ErrorAggregate',
                'sample_data': {},
                'set_attribute_params': [],
            },
            'transfer_object.ErrorConfigObject': {
                'type': 'transfer_object',
                'module_path': 'tiferet.mappers.error',
                'class_name': 'ErrorConfigObject',
                'sample_data': {},
                'aggregate_module_path': 'tiferet.mappers.error',
                'aggregate_class_name': 'ErrorAggregate',
                'aggregate_sample_data': {},
            },
        },
    )(lambda cache=None: CacheContext(cache=cache))
    cache = builder()

    # Verify the seeded values are domain variants, not tester aggregates.
    domain_tester = cache.get('domain.ErrorMessage', *TESTER_CACHE_PREFIX)
    aggregate_tester = cache.get('aggregate.ErrorAggregate', *TESTER_CACHE_PREFIX)
    transfer_tester = cache.get('transfer_object.ErrorConfigObject', *TESTER_CACHE_PREFIX)
    assert isinstance(domain_tester, DomainTesterObject)
    assert isinstance(aggregate_tester, AggregateTesterObject)
    assert isinstance(transfer_tester, TransferObjectTesterObject)
    assert aggregate_tester.id == 'aggregate.ErrorAggregate'
    assert aggregate_tester.type == 'aggregate'

# ** test: test_session_context
def test_session_context_runs_direct_event_and_clears_pending_state() -> None:
    '''Test a direct event chain captures its result and clears its lifecycle.'''

    # Define a self-contained direct event for the fluent session.
    class AddEvent:
        def __call__(self, a, b):
            return a + b

    # Compose a context with a specialized request factory.
    context = _TestSessionContext.from_domain(
        type('Session', (), {'id': 'tester'})(),
        get_dependency=lambda *args: None,
        create_request_handler=lambda session_id, feature_id, headers, data: _TestRequestContext(
            session_id=session_id,
            feature_id=feature_id,
            headers=headers,
            data=data,
        ),
    )

    # Run a complete chain and verify its result and clean lifecycle.
    result = context.given(a=1).invoke(event=AddEvent(), b=2).verify(3).run()
    assert result == 3
    assert context._pending_request is None

# ** test: test_session_context_preset
def test_session_context_merges_preset_and_rejects_missing_preset() -> None:
    '''Test named presets merge state and unresolved names raise a domain error.'''

    # Seed a test-session cache with one raw given-state preset.
    cache = add_default_test_presets({'sum': {'a': 1, 'b': 2}})(
        lambda: CacheContext(),
    )()
    context = _TestSessionContext(
        get_dependency=lambda *args: None,
        cache=cache,
        create_request_handler=lambda session_id, feature_id, headers, data: _TestRequestContext(
            session_id=session_id,
            feature_id=feature_id,
            headers=headers,
            data=data,
        ),
    )
    context.domain = type('Session', (), {'id': 'tester'})()

    # Assert preset state merges before literal overrides.
    context.given('sum', b=3)
    assert context._pending_request.data == {'a': 1, 'b': 3}
    assert cache.get('sum', *TEST_PRESET_CACHE_PREFIX) == {'a': 1, 'b': 2}

    # Assert missing presets raise the catalogued domain error.
    with pytest.raises(TiferetError) as exc_info:
        context.given('missing')
    assert exc_info.value.error_code == 'TEST_PRESET_NOT_FOUND'

# ** test: aggregate_tester_context_set_attribute_cases
def test_aggregate_tester_context_set_attribute_cases() -> None:
    '''Test mutation assertions iterate declared cases on fresh targets.'''

    # Bind an aggregate tester with valid and invalid mutation cases.
    context = AggregateTesterContext.from_domain(
        AggregateTesterObject(
            id='aggregate.ErrorAggregate',
            module_path=ErrorAggregate.__module__,
            class_name=ErrorAggregate.__name__,
            sample_data={'id': 'TEST_ERROR', 'name': 'Test Error'},
            equality_fields=['id', 'name'],
            set_attribute_params=[
                ('name', 'Updated Error', None),
                ('invalid_attribute', 'value', INVALID_MODEL_ATTRIBUTE_ID),
            ],
        ),
    )

    # Assert every declared mutation case on a fresh target.
    context.assert_set_attribute()
