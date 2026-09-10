"""Tests for Tiferet Tester Contexts"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.assets import TiferetAPIError, TiferetError
from tiferet.contexts.core import BaseContext
from tiferet.contexts.request import RequestContext
from tiferet.blueprints.tester import build_tester_context, use_tester
from tiferet.contexts.tester import (
    AggregateTesterContext,
    DomainTesterContext,
    TestRequestContext as _TestRequestContext,
    TestSessionContext as _TestSessionContext,
    TEST_PRESET_CACHE_PREFIX,
    TESTER_CACHE_PREFIX,
    TesterContext,
    TransferObjectTesterContext,
    add_default_test_presets,
    add_default_testers,
)
from tiferet.contexts.cache import CacheContext
from tiferet.domain import (
    Request,
    TesterObject,
    Verification,
)
from tiferet.domain import INVALID_MODEL_ATTRIBUTE_ID
from tiferet.domain.error import ErrorMessage
from tiferet.mappers.error import (
    ErrorAggregate,
    ErrorConfigObject,
)

# *** tests

# ** test: tester_context_registry_and_omitted_domain_type
def test_tester_context_registry_and_omitted_domain_type() -> None:
    '''Test TesterContext registration and variant classes omit domain_type.'''

    tester = TesterObject(
        type='domain',
        id='domain.ErrorMessage',
        module_path=ErrorMessage.__module__,
        class_name=ErrorMessage.__name__,
        sample_data={'lang': 'en_US', 'text': 'An error occurred.'},
        equality_fields=['lang', 'text'],
    )
    assert BaseContext.for_domain(TesterObject) is TesterContext
    assert 'domain_type' not in DomainTesterContext.__dict__
    assert 'domain_type' not in AggregateTesterContext.__dict__
    assert 'domain_type' not in TransferObjectTesterContext.__dict__
    assert isinstance(BaseContext.from_domain(tester), TesterContext)
    assert isinstance(DomainTesterContext.from_domain(tester), DomainTesterContext)

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

    domain_tester = cache.get('domain.ErrorMessage', *TESTER_CACHE_PREFIX)
    aggregate_tester = cache.get('aggregate.ErrorAggregate', *TESTER_CACHE_PREFIX)
    transfer_tester = cache.get('transfer_object.ErrorConfigObject', *TESTER_CACHE_PREFIX)
    assert isinstance(domain_tester, TesterObject)
    assert isinstance(aggregate_tester, TesterObject)
    assert isinstance(transfer_tester, TesterObject)
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

# ** test: test_session_context_feature_path_builds_logger
def test_session_context_feature_path_builds_logger_and_passes_it() -> None:
    '''Test feature dispatch builds a logger and passes it into execute_feature.'''

    # Compose a context with logger, execution, and response handlers wired.
    logger = mock.Mock()
    build_logger_handler = mock.Mock(return_value=logger)
    execute_feature_handler = mock.Mock()
    context = _TestSessionContext.from_domain(
        type('Session', (), {'id': 'tester', 'logger_id': 'default'})(),
        get_dependency=lambda *args: None,
        build_logger_handler=build_logger_handler,
        execute_feature_handler=execute_feature_handler,
        create_request_handler=lambda session_id, feature_id, headers, data: _TestRequestContext(
            session_id=session_id,
            feature_id=feature_id,
            headers=headers,
            data=data,
        ),
        response_handler=mock.Mock(return_value='ok'),
    )

    # Run a successful feature chain and assert logger construction.
    result = context.invoke(feature_id='test.empty').verify('ok').run()
    assert result == 'ok'
    build_logger_handler.assert_called_once_with('default')
    execute_feature_handler.assert_called_once()
    args, kwargs = execute_feature_handler.call_args
    assert args[0] == 'test.empty'
    assert kwargs.get('logger') is logger
    assert context._pending_request is None

# ** test: test_session_context_feature_path_formats_tiferet_error
def test_session_context_feature_path_formats_tiferet_error() -> None:
    '''Test a feature-path TiferetError is logged and raised as TiferetAPIError.'''

    # Arrange a feature handler that raises a catalogued domain error.
    logger = mock.Mock()
    domain_error = TiferetError('FEATURE_NOT_FOUND', feature_id='test.empty')
    api_error = TiferetAPIError(
        error_code='FEATURE_NOT_FOUND',
        name='Feature Not Found',
        message='Feature not found: test.empty.',
    )
    raise_error_handler = mock.Mock(side_effect=api_error)
    context = _TestSessionContext.from_domain(
        type('Session', (), {'id': 'tester', 'logger_id': 'default'})(),
        get_dependency=lambda *args: None,
        build_logger_handler=mock.Mock(return_value=logger),
        execute_feature_handler=mock.Mock(side_effect=domain_error),
        raise_error_handler=raise_error_handler,
        create_request_handler=lambda session_id, feature_id, headers, data: _TestRequestContext(
            session_id=session_id,
            feature_id=feature_id,
            headers=headers,
            data=data,
        ),
        response_handler=mock.Mock(),
    )

    # Dispatch the feature and capture the formatted API error.
    with pytest.raises(TiferetAPIError) as exc_info:
        context.invoke(feature_id='test.empty').run()

    # Assert logging, formatting, and pending-state cleanup.
    assert exc_info.value is api_error
    logger.error.assert_called_once()
    raise_error_handler.assert_called_once_with(domain_error)
    assert context._pending_request is None

# ** test: test_session_context_event_path_keeps_tiferet_error
def test_session_context_event_path_skips_logger_and_keeps_tiferet_error() -> None:
    '''Test invoke(event=...) does not call build_logger or handle_error.'''

    # Compose a context with logger and error handlers that must stay unused.
    build_logger_handler = mock.Mock()
    raise_error_handler = mock.Mock()

    def raise_domain_error():
        TiferetError.raise_error('FEATURE_NOT_FOUND', feature_id='missing')

    context = _TestSessionContext.from_domain(
        type('Session', (), {'id': 'tester', 'logger_id': 'default'})(),
        get_dependency=lambda *args: None,
        build_logger_handler=build_logger_handler,
        raise_error_handler=raise_error_handler,
        create_request_handler=lambda session_id, feature_id, headers, data: _TestRequestContext(
            session_id=session_id,
            feature_id=feature_id,
            headers=headers,
            data=data,
        ),
    )

    # Dispatch the event and capture the unformatted domain error.
    with pytest.raises(TiferetError) as exc_info:
        context.invoke(event=raise_domain_error).run()

    # Assert the event path skipped production logging and error formatting.
    assert type(exc_info.value) is TiferetError
    assert exc_info.value.error_code == 'FEATURE_NOT_FOUND'
    build_logger_handler.assert_not_called()
    raise_error_handler.assert_not_called()
    assert context._pending_request is None

# ** test: test_session_context_run_without_invoke_raises_tiferet_error
def test_session_context_run_without_invoke_raises_tiferet_error() -> None:
    '''Test harness run() target-selection errors remain raw TiferetError.'''

    # Compose a context with no pending invocation.
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

    # Run without invoke and assert the harness error is unformatted.
    with pytest.raises(TiferetError) as exc_info:
        context.run()
    assert type(exc_info.value) is TiferetError
    assert exc_info.value.error_code == 'COMMAND_PARAMETER_REQUIRED'

# ** test: build_tester_context_selects_variant_class
def test_build_tester_context_selects_variant_class() -> None:
    '''Test the blueprint selector returns the matching omitting-domain_type class.'''

    domain_ctx = build_tester_context(
        TesterObject(
            type='domain',
            id='domain.ErrorMessage',
            module_path=ErrorMessage.__module__,
            class_name=ErrorMessage.__name__,
        ),
    )
    aggregate_ctx = build_tester_context(
        TesterObject(
            type='aggregate',
            id='aggregate.ErrorAggregate',
            module_path=ErrorAggregate.__module__,
            class_name=ErrorAggregate.__name__,
            set_attribute_params=[
                ('name', 'Updated Error', None),
                ('invalid_attribute', 'value', INVALID_MODEL_ATTRIBUTE_ID),
            ],
            sample_data={'id': 'TEST_ERROR', 'name': 'Test Error'},
            equality_fields=['id', 'name'],
        ),
    )
    transfer_ctx = build_tester_context(
        TesterObject(
            type='transfer_object',
            id='transfer_object.ErrorConfigObject',
            module_path=ErrorConfigObject.__module__,
            class_name=ErrorConfigObject.__name__,
            aggregate_module_path=ErrorAggregate.__module__,
            aggregate_class_name=ErrorAggregate.__name__,
            sample_data={'id': 'TEST_ERROR', 'name': 'Test Error'},
            aggregate_sample_data={'id': 'TEST_ERROR', 'name': 'Test Error'},
            equality_fields=['id', 'name'],
        ),
    )
    assert isinstance(domain_ctx, DomainTesterContext)
    assert isinstance(aggregate_ctx, AggregateTesterContext)
    assert isinstance(transfer_ctx, TransferObjectTesterContext)
    aggregate_ctx.assert_set_attribute()
    transfer_ctx.assert_map()

# ** test: use_tester_injects_test_ctx
@use_tester(
    type='domain',
    target_cls=ErrorMessage,
    sample_data={'lang': 'en_US', 'text': 'An error occurred.'},
    equality_fields=['lang', 'text'],
)
def test_use_tester_injects_test_ctx(test_ctx) -> None:
    '''Test @use_tester injects a bound DomainTesterContext as test_ctx.'''

    assert isinstance(test_ctx, DomainTesterContext)
    test_ctx.assert_new()
