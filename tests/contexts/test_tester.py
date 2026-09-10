"""Tests for Tiferet Tester Contexts"""

# *** imports

# ** core
import inspect

# ** infra
import pytest

# ** app
from tiferet.blueprints.tester import build_test_session, build_tester_context, use_tester
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.cli import CliSessionContext
from tiferet.contexts.core import BaseContext, ContextMeta
from tiferet.contexts.request import RequestContext
from tiferet.contexts.tester import (
    AggregateTesterContext,
    ContextTesterContext,
    DomainEventTesterContext,
    DomainTesterContext,
    GenericTesterContext,
    RepoTesterContext,
    ServiceEventTesterContext,
    TESTER_CACHE_PREFIX,
    TEST_PRESET_CACHE_PREFIX,
    TestSessionContext as _TestSessionContext,
    TesterContext,
    TransferObjectTesterContext,
    add_default_test_presets,
    add_default_testers,
)
from tiferet.domain import (
    AppSession,
    Request,
    TesterObject,
    Verification,
)
from tiferet.domain import INVALID_MODEL_ATTRIBUTE_ID
from tiferet.domain.error import ErrorMessage
from tiferet.events.error import GetError
from tiferet.interfaces import ErrorService
from tiferet.mappers.error import (
    ErrorAggregate,
    ErrorConfigObject,
)

# *** constants

# ** constant: error_message_sample_data
ERROR_MESSAGE_SAMPLE_DATA = {
    'lang': 'en_US',
    'text': 'An error occurred.',
}

# *** functions

# ** function: build_error_message_tester
def _build_error_message_tester() -> TesterObject:
    '''
    Build a domain tester for ErrorMessage.

    :return: The ErrorMessage tester domain object.
    :rtype: TesterObject
    '''

    # Construct a reusable domain tester for session proofs.
    return TesterObject(
        type='domain',
        id='domain.ErrorMessage',
        module_path=ErrorMessage.__module__,
        class_name=ErrorMessage.__name__,
        sample_data=dict(ERROR_MESSAGE_SAMPLE_DATA),
        equality_fields=['lang', 'text'],
    )

# ** function: add_values
def _add_values(a, b):
    '''Add two values for generic run proving tests.'''

    return a + b

# *** fixtures

# ** fixture: injection_marker
@pytest.fixture
def injection_marker() -> str:
    '''
    Provide a marker proving pytest fixtures still inject by name.

    :return: The marker value.
    :rtype: str
    '''

    # Return a distinct fixture value.
    return 'marker'

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
    assert 'domain_type' not in RepoTesterContext.__dict__
    assert 'domain_type' not in ContextTesterContext.__dict__
    assert isinstance(BaseContext.from_domain(tester), TesterContext)
    assert isinstance(DomainTesterContext.from_domain(tester), DomainTesterContext)

# ** test: test_session_context_preserves_request_and_tester_registration
def test_session_context_preserves_request_and_tester_registration() -> None:
    '''
    Test that TestSessionContext omits domain_type and leaves Request and
    TesterObject registrations unchanged.
    '''

    # Assert the session does not steal Request or TesterObject registration.
    assert 'domain_type' not in _TestSessionContext.__dict__
    assert BaseContext.for_domain(Request) is RequestContext
    assert BaseContext.for_domain(TesterObject) is TesterContext

    # Assert the session is a request, not an application hub.
    assert issubclass(_TestSessionContext, RequestContext)
    assert not issubclass(_TestSessionContext, AppSessionContext)

# ** test: test_session_context_given_merges_state_and_returns_self
def test_session_context_given_merges_state_and_returns_self() -> None:
    '''
    Test that given shallowly merges state, lets later values win, and supports
    fluent chaining without mutating sample data.
    '''

    # Bind a session to a domain tester and capture sample identity.
    tester = _build_error_message_tester()
    test_ctx = DomainTesterContext.from_domain(tester)
    sample = test_ctx.domain.sample_data
    session = build_test_session(test_ctx)
    returned_session = session.given(a=1).given(a=2)

    # Assert the original session was returned with the final shallow state.
    assert returned_session is session
    assert session.data == {'a': 2}

    # Assert given-state overlays the request, never the tester sample payload.
    assert test_ctx.domain.sample_data is sample
    assert 'a' not in sample
    assert sample == ERROR_MESSAGE_SAMPLE_DATA

# ** test: test_session_context_verify_normalizes_predicates_and_literals
def test_session_context_verify_normalizes_predicates_and_literals() -> None:
    '''
    Test that verify queues exactly one Verification for callable and literal
    expectations while returning the original fluent session.
    '''

    # Queue a callable and literal expectation on one session.
    session = build_test_session(DomainTesterContext.from_domain(
        _build_error_message_tester(),
    ))
    predicate = lambda outcome: outcome == 3
    assert session.verify(predicate) is session
    assert session.verify(3, message='literal outcome') is session

    # Assert both inputs have the unified Verification representation.
    assert len(session.verifications) == 2
    assert all(
        isinstance(verification, Verification)
        for verification in session.verifications
    )
    assert session.verifications[0].predicate is predicate
    assert session.verifications[0].source is predicate
    assert session.verifications[1].source == 3
    assert session.verifications[1].predicate(3)

# ** test: test_session_context_evaluates_all_verifications_and_clears_queue
def test_session_context_evaluates_all_verifications_and_clears_queue() -> None:
    '''
    Test that verification failures aggregate once and the consumed queue is
    cleared on both failing and passing evaluation paths.
    '''

    # Queue two failing and one passing assertion against the shared outcome.
    session = build_test_session(DomainTesterContext.from_domain(
        _build_error_message_tester(),
    ))
    session.verify(lambda outcome: outcome == 1, message='first failure')
    session.verify(lambda outcome: outcome == 3, message='second failure')
    session.verify(lambda outcome: outcome == 2, message='passing check')
    session.capture_outcome(2)

    # Assert all failures appear in one assertion and the queue is consumed.
    with pytest.raises(AssertionError) as exc_info:
        session.evaluate_verifications()
    assert 'first failure' in str(exc_info.value)
    assert 'second failure' in str(exc_info.value)
    assert len(session.verifications) == 0

    # Queue a passing assertion and assert successful evaluation also consumes it.
    session.verify(2)
    assert session.evaluate_verifications() is None
    assert len(session.verifications) == 0

# ** test: test_session_context_records_raised_predicates_and_continues
def test_session_context_records_raised_predicates_and_continues() -> None:
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
    session = build_test_session(DomainTesterContext.from_domain(
        _build_error_message_tester(),
    ))
    session.verify(raises_error, message='raised predicate')
    session.verify(records_evaluation, message='continued predicate')
    session.capture_outcome('outcome')

    # Assert both failures are reported and the later predicate was evaluated.
    with pytest.raises(AssertionError) as exc_info:
        session.evaluate_verifications()
    assert 'raised predicate' in str(exc_info.value)
    assert 'predicate error' in str(exc_info.value)
    assert 'continued predicate' in str(exc_info.value)
    assert evaluated == ['outcome']
    assert len(session.verifications) == 0

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

# ** test: add_default_test_presets
def test_add_default_test_presets_seeds_raw_given_state() -> None:
    '''Test named presets remain cache-seeded without a session hub.'''

    # Seed a cache with one raw given-state preset.
    cache = add_default_test_presets({'sum': {'a': 1, 'b': 2}})(
        lambda: CacheContext(),
    )()

    # Assert the preset is stored raw under the test-preset namespace.
    assert cache.get('sum', *TEST_PRESET_CACHE_PREFIX) == {'a': 1, 'b': 2}

# ** test: test_session_context_run_exercises_bound_tester
def test_session_context_run_exercises_bound_tester() -> None:
    '''Test given/verify/run exercises the bound tester without invoke.'''

    # Bind a session and overlay a valid construction field.
    tester = _build_error_message_tester()
    test_ctx = DomainTesterContext.from_domain(tester)
    sample = test_ctx.domain.sample_data
    session = build_test_session(test_ctx)

    # Run without invoke and verify the overlaid construction outcome.
    result = session.given(text='overlay').verify(
        lambda outcome: outcome.text == 'overlay',
    ).run()
    assert result.text == 'overlay'
    assert result.lang == 'en_US'
    assert len(session.verifications) == 0

    # Assert sample data identity is unchanged after run.
    assert test_ctx.domain.sample_data is sample
    assert sample == ERROR_MESSAGE_SAMPLE_DATA

    # Assert run does not call the application hub pipeline.
    source = inspect.getsource(_TestSessionContext.run)
    assert 'execute_feature' not in source
    assert 'build_logger' not in source
    assert 'handle_error' not in source
    assert 'TiferetAPIError' not in source

# ** test: test_session_context_invoke_merges_params_and_returns_self
def test_session_context_invoke_merges_params_and_returns_self() -> None:
    '''Test invoke merges onto request data and is not a feature pipeline.'''

    # Invoke parameters onto a bound session and run the tester target.
    session = build_test_session(DomainTesterContext.from_domain(
        _build_error_message_tester(),
    ))
    assert session.invoke(text='from invoke') is session
    assert session.data == {'text': 'from invoke'}
    result = session.verify(lambda outcome: outcome.text == 'from invoke').run()
    assert result.text == 'from invoke'
    assert 'feature_id' not in inspect.signature(_TestSessionContext.invoke).parameters

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

# ** test: use_tester_reuses_master_and_creates_new_sessions
def test_use_tester_reuses_master_and_creates_new_sessions() -> None:
    '''Test decoration builds one master and a new session per test method.'''

    # Decorate a probe class with two test methods that return injected objects.
    @use_tester(
        type='domain',
        target_cls=ErrorMessage,
        sample_data=dict(ERROR_MESSAGE_SAMPLE_DATA),
        equality_fields=['lang', 'text'],
    )
    class Probe:
        def test_a(self, test_ctx, session):
            return test_ctx, session

        def test_b(self, test_ctx, session):
            return test_ctx, session

    # Invoke both wrappers and compare the injected instances.
    probe = Probe()
    test_ctx_a, session_a = probe.test_a()
    test_ctx_b, session_b = probe.test_b()
    assert test_ctx_a is test_ctx_b
    assert session_a is not session_b
    assert isinstance(session_a, _TestSessionContext)
    assert isinstance(session_b, _TestSessionContext)
    assert session_a.tester_ctx is test_ctx_a
    assert session_b.tester_ctx is test_ctx_b

# ** test: use_tester_wraps_class_fixture_members
def test_use_tester_wraps_class_fixture_members() -> None:
    '''Test class-form @use_tester injects test_ctx into member fixtures.'''

    # Decorate a probe class whose fixture lists test_ctx.
    @use_tester(
        type='domain',
        target_cls=ErrorMessage,
        sample_data=dict(ERROR_MESSAGE_SAMPLE_DATA),
        equality_fields=['lang', 'text'],
    )
    class Probe:
        @pytest.fixture
        def bound(self, test_ctx):
            return test_ctx

        def test_same(self, test_ctx):
            return test_ctx

    # Unwrap the restored fixture object without importing pytest in tiferet/.
    fixture_member = Probe.__dict__['bound']
    inner = getattr(
        fixture_member,
        '_fixture_function',
        getattr(fixture_member, '__wrapped__', fixture_member),
    )

    # Assert test_ctx was stripped from the pytest-visible signatures.
    assert 'test_ctx' not in inspect.signature(inner).parameters
    assert 'test_ctx' not in inspect.signature(Probe.test_same).parameters

    # Assert the fixture and test method receive the same decoration-time master.
    probe = Probe()
    fixture_ctx = inner(probe)
    test_ctx = probe.test_same()
    assert fixture_ctx is test_ctx
    assert isinstance(test_ctx, DomainTesterContext)

# ** test: use_tester_injects_by_parameter_name
@use_tester(
    type='domain',
    target_cls=ErrorMessage,
    sample_data=dict(ERROR_MESSAGE_SAMPLE_DATA),
    equality_fields=['lang', 'text'],
)
def test_use_tester_injects_by_parameter_name(
        injection_marker,
        session,
        test_ctx,
    ) -> None:
    '''Test injection is by parameter name and keeps pytest fixtures working.'''

    # Assert the pytest fixture was not displaced by positional injection.
    assert injection_marker == 'marker'
    assert isinstance(test_ctx, DomainTesterContext)
    assert isinstance(session, _TestSessionContext)
    assert session.tester_ctx is test_ctx
    assert 'test_ctx' not in inspect.signature(
        test_use_tester_injects_by_parameter_name,
    ).parameters
    assert 'session' not in inspect.signature(
        test_use_tester_injects_by_parameter_name,
    ).parameters
    assert 'tester_ctx' not in inspect.signature(
        test_use_tester_injects_by_parameter_name,
    ).parameters

# ** test: use_tester_injects_only_declared_session
@use_tester(
    type='domain',
    target_cls=ErrorMessage,
    sample_data=dict(ERROR_MESSAGE_SAMPLE_DATA),
    equality_fields=['lang', 'text'],
)
def test_use_tester_injects_only_declared_session(session) -> None:
    '''Test a session-only test still receives a session bound to the master.'''

    assert isinstance(session, _TestSessionContext)
    assert isinstance(session.tester_ctx, DomainTesterContext)

# ** test: event_tester_contexts_omit_domain_type
def test_event_tester_contexts_omit_domain_type() -> None:
    '''Test event contexts omit domain_type and leave TesterContext registered.'''

    assert 'domain_type' not in DomainEventTesterContext.__dict__
    assert 'domain_type' not in ServiceEventTesterContext.__dict__
    assert BaseContext.for_domain(TesterObject) is TesterContext

# ** test: service_event_tester_context_handle_and_asserts
def test_service_event_tester_context_handle_and_asserts() -> None:
    '''Test service-event mocks, handle, not-found, and missing-param no-op.'''

    tester = TesterObject(
        type='service_event',
        id='service_event.GetError',
        module_path=GetError.__module__,
        class_name=GetError.__name__,
        sample_data={},
        dependencies={
            'error_service': {
                'module_path': 'tiferet.interfaces',
                'class_name': 'ErrorService',
            },
        },
        sample_kwargs={'id': 'TEST_ERROR'},
        required_params=[],
        service_attr='error_service',
        not_found_error_code='ERROR_NOT_FOUND',
    )
    test_ctx = ServiceEventTesterContext.from_domain(tester)
    assert isinstance(test_ctx, DomainEventTesterContext)
    dependencies = test_ctx.mock_dependencies()
    assert test_ctx.get_service_mock(dependencies) is dependencies['error_service']
    error = ErrorAggregate(
        id='TEST_ERROR',
        name='Test Error',
        message=[{'lang': 'en_US', 'text': 'An error occurred.'}],
    )
    dependencies['error_service'].get.return_value = error
    assert test_ctx.handle(dependencies) is error
    test_ctx.assert_not_found()
    test_ctx.assert_missing_required_params()

# ** test: use_tester_injects_service_event_test_ctx
@use_tester(
    type='service_event',
    target_cls=GetError,
    sample_data={},
    dependencies={
        'error_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'ErrorService',
        },
    },
    sample_kwargs={'id': 'TEST_ERROR'},
    service_attr='error_service',
    not_found_error_code='ERROR_NOT_FOUND',
)
def test_use_tester_injects_service_event_test_ctx(test_ctx) -> None:
    '''Test @use_tester injects ServiceEventTesterContext for service_event.'''

    assert isinstance(test_ctx, ServiceEventTesterContext)
    test_ctx.assert_not_found()

# ** test: generic_tester_context_omits_domain_type
def test_generic_tester_context_omits_domain_type() -> None:
    '''Test GenericTesterContext omits domain_type and leaves registry mappings.'''

    assert 'domain_type' not in GenericTesterContext.__dict__
    assert BaseContext.for_domain(TesterObject) is TesterContext
    assert BaseContext.for_domain(Request) is RequestContext
    assert not hasattr(GenericTesterContext, 'given')
    assert not hasattr(GenericTesterContext, 'invoke')
    assert not hasattr(GenericTesterContext, 'verify')
    assert not hasattr(GenericTesterContext, 'run')

# ** test: generic_tester_context_assert_contract
def test_generic_tester_context_assert_contract() -> None:
    '''Test assert_contract no-ops on concrete classes and locks a real ABC.'''

    concrete_ctx = GenericTesterContext.from_domain(
        TesterObject(
            type='generic',
            id='generic.ErrorMessage',
            module_path=ErrorMessage.__module__,
            class_name=ErrorMessage.__name__,
            sample_data=dict(ERROR_MESSAGE_SAMPLE_DATA),
        ),
    )
    assert concrete_ctx.assert_contract() is None

    abc_ctx = GenericTesterContext.from_domain(
        TesterObject(
            type='generic',
            id='generic.ErrorService',
            module_path=ErrorService.__module__,
            class_name=ErrorService.__name__,
        ),
    )
    assert abc_ctx.assert_contract(target=ErrorService) is None
    for name in ErrorService.__abstractmethods__:
        assert hasattr(ErrorService, name)

# ** test: session_run_generic_invokes_local_callable
def test_session_run_generic_invokes_local_callable() -> None:
    '''Test generic run(target=fn) uses given-state and does not mutate sample_data.'''

    test_ctx = GenericTesterContext.from_domain(
        TesterObject(
            type='generic',
            id='generic.add_values',
            module_path=__name__,
            class_name='_add_values',
        ),
    )
    sample = test_ctx.domain.sample_data
    domain = test_ctx.domain
    session = build_test_session(test_ctx)
    result = session.given(a=1, b=2).verify(3).run(target=_add_values)
    assert result == 3
    assert test_ctx.domain is domain
    assert test_ctx.domain.sample_data is sample

    source = inspect.getsource(_TestSessionContext.run)
    assert 'execute_feature' not in source
    assert '_dispatch_event' not in source
    assert 'build_logger' not in source
    assert 'handle_error' not in source

# ** test: session_run_generic_uses_get_target_without_invoke
def test_session_run_generic_uses_get_target_without_invoke() -> None:
    '''Test generic run() without invoke still exercises get_target().'''

    test_ctx = GenericTesterContext.from_domain(
        TesterObject(
            type='generic',
            id='generic.add_values',
            module_path=__name__,
            class_name='_add_values',
        ),
    )
    result = build_test_session(test_ctx).given(a=2, b=3).verify(5).run()
    assert result == 5

# ** test: session_run_rejects_target_on_specialized_tester
def test_session_run_rejects_target_on_specialized_tester() -> None:
    '''Test specialized run raises when a live target is supplied.'''

    session = build_test_session(
        DomainTesterContext.from_domain(_build_error_message_tester()),
    )
    with pytest.raises(ValueError):
        session.run(target=_add_values)

# ** test: repo_tester_context_omits_domain_type
def test_repo_tester_context_omits_domain_type() -> None:
    '''Test RepoTesterContext omits domain_type and binds via from_domain.'''

    tester = TesterObject(
        type='repo',
        id='repo.ErrorConfigRepository',
        module_path='tiferet.repos.error',
        class_name='ErrorConfigRepository',
        config_parameter='error_config',
    )
    test_ctx = RepoTesterContext.from_domain(tester)
    assert 'domain_type' not in RepoTesterContext.__dict__
    assert BaseContext.for_domain(TesterObject) is TesterContext
    assert BaseContext.for_domain(Request) is RequestContext
    assert isinstance(test_ctx, RepoTesterContext)
    assert isinstance(test_ctx, TesterContext)

# ** test: repo_tester_context_empty_cases_are_noops
def test_repo_tester_context_empty_cases_are_noops() -> None:
    '''Test empty CRUD lists and unset aggregate_class_name are no-ops.'''

    test_ctx = RepoTesterContext.from_domain(
        TesterObject(
            type='repo',
            id='repo.ErrorConfigRepository',
            module_path='tiferet.repos.error',
            class_name='ErrorConfigRepository',
            config_parameter='error_config',
        ),
    )
    test_ctx.assert_exists(None)
    test_ctx.assert_get(None)
    test_ctx.assert_list(None)
    test_ctx.assert_save(None)
    test_ctx.assert_delete(None)

# *** testers

# ** tester: context_tester_context_tester
class ContextTesterContextTester:
    '''Prove ContextTesterContext registry, bind, and empty-case no-ops.'''

    # * test: omits_domain_type_and_preserves_registry
    def test_omits_domain_type_and_preserves_registry(self) -> None:
        '''ContextTesterContext does not clobber ContextMeta mappings.'''

        tester = TesterObject(
            type='context',
            id='context.RequestContext',
            module_path=RequestContext.__module__,
            class_name=RequestContext.__name__,
            domain_module_path=Request.__module__,
            domain_class_name=Request.__name__,
        )
        assert 'domain_type' not in ContextTesterContext.__dict__
        assert BaseContext.for_domain(TesterObject) is TesterContext
        assert BaseContext.for_domain(Request) is RequestContext
        assert BaseContext.for_domain(AppSession) is AppSessionContext
        assert BaseContext not in ContextMeta.registry.values()
        assert isinstance(BaseContext.from_domain(tester), TesterContext)
        bound = ContextTesterContext.from_domain(tester)
        assert isinstance(bound, ContextTesterContext)
        assert bound.domain is tester

    # * test: empty_case_lists_are_no_ops
    def test_empty_case_lists_are_no_ops(self) -> None:
        '''Empty from_domain, domain_type, and for_domain cases return immediately.'''

        test_ctx = ContextTesterContext.from_domain(
            TesterObject(
                type='context',
                id='context.RequestContext',
                module_path=RequestContext.__module__,
                class_name=RequestContext.__name__,
                domain_module_path=Request.__module__,
                domain_class_name=Request.__name__,
            ),
        )
        assert test_ctx.assert_from_domain() is None
        assert test_ctx.assert_domain_type() is None
        assert test_ctx.assert_for_domain() is None

    # * test: declaring_request_context_cases
    def test_declaring_request_context_cases(self) -> None:
        '''RequestContext declaring cases pass the three context assertions.'''

        test_ctx = ContextTesterContext.from_domain(
            TesterObject(
                type='context',
                id='context.RequestContext',
                module_path=RequestContext.__module__,
                class_name=RequestContext.__name__,
                sample_data={
                    'session_id': 'test-session',
                    'feature_id': 'test.feature',
                },
                domain_module_path=Request.__module__,
                domain_class_name=Request.__name__,
                from_domain_cases=[
                    {
                        'data': {
                            'session_id': 'test-session',
                            'feature_id': 'test.feature',
                        },
                    },
                ],
                domain_type_cases=[
                    {
                        'declares': True,
                    },
                ],
                for_domain_cases=[
                    {
                        'domain_module_path': Request.__module__,
                        'domain_class_name': Request.__name__,
                        'context_module_path': RequestContext.__module__,
                        'context_class_name': RequestContext.__name__,
                    },
                ],
            ),
        )
        test_ctx.assert_from_domain()
        test_ctx.assert_domain_type()
        test_ctx.assert_for_domain()

    # * test: omitting_cli_session_does_not_clobber_app_session
    def test_omitting_cli_session_does_not_clobber_app_session(self) -> None:
        '''An omitting case proves CliSessionContext leaves AppSession mapping.'''

        test_ctx = ContextTesterContext.from_domain(
            TesterObject(
                type='context',
                id='context.CliSessionContext',
                module_path=CliSessionContext.__module__,
                class_name=CliSessionContext.__name__,
                domain_module_path=AppSession.__module__,
                domain_class_name=AppSession.__name__,
                domain_type_cases=[
                    {
                        'declares': False,
                    },
                ],
                for_domain_cases=[
                    {
                        'domain_module_path': AppSession.__module__,
                        'domain_class_name': AppSession.__name__,
                        'context_module_path': AppSessionContext.__module__,
                        'context_class_name': AppSessionContext.__name__,
                    },
                    {
                        'domain_module_path': TesterObject.__module__,
                        'domain_class_name': TesterObject.__name__,
                        'context_module_path': TesterContext.__module__,
                        'context_class_name': TesterContext.__name__,
                    },
                ],
            ),
        )
        test_ctx.assert_domain_type()
        test_ctx.assert_for_domain()
