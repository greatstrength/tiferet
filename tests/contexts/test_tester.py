"""Tests for Tiferet Tester Contexts"""

# *** imports

# ** core
import inspect

# ** infra
import pytest

# ** app
from tiferet.blueprints.tester import (
    build_test_session,
    build_tester_context,
    use_tester,
)
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.cli import CliSessionContext
from tiferet.contexts.core import BaseContext, ContextMeta
from tiferet.contexts.request import RequestContext
from tiferet.contexts.tester import (
    TEST_PRESET_CACHE_PREFIX,
    TESTER_CACHE_PREFIX,
    AggregateTesterContext,
    ContextTesterContext,
    DomainEventTesterContext,
    DomainTesterContext,
    GenericTesterContext,
    RepoTesterContext,
    ServiceEventTesterContext,
    TestSessionContext as _TestSessionContext,
    TesterContext,
    TransferObjectTesterContext,
    add_default_test_presets,
    add_default_testers,
)
from tiferet.domain import (
    INVALID_MODEL_ATTRIBUTE_ID,
    AppSession,
    Request,
    TesterObject,
    Verification,
)
from tiferet.domain.error import ErrorMessage
from tiferet.events.error import GetError
from tiferet.interfaces import ErrorService
from tiferet.mappers.error import ErrorAggregate, ErrorConfigObject

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

    :return: The bound tester domain object.
    :rtype: TesterObject
    '''

    # Return a domain tester with a copied sample mapping.
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
    '''
    Add two values.

    :param a: The left operand.
    :type a: Any
    :param b: The right operand.
    :type b: Any
    :return: The sum.
    :rtype: Any
    '''

    # Return the sum.
    return a + b

# *** fixtures

# ** fixture: injection_marker
@pytest.fixture
def injection_marker() -> str:
    '''
    Return a marker that proves non-tester injection still works.

    :return: The marker string.
    :rtype: str
    '''

    # Return the marker.
    return 'marker'

# *** tests

# ** test: tester_context_registry_and_omitted_domain_type
def test_tester_context_registry_and_omitted_domain_type() -> None:
    '''
    Assert the tester registry and omitted variant domain types.

    :return: None
    :rtype: None
    '''

    # Build a domain tester for ErrorMessage.
    tester = TesterObject(
        type='domain',
        id='domain.ErrorMessage',
        module_path=ErrorMessage.__module__,
        class_name=ErrorMessage.__name__,
        sample_data={'lang': 'en_US', 'text': 'An error occurred.'},
        equality_fields=['lang', 'text'],
    )

    # The registry maps TesterObject to TesterContext only.
    assert BaseContext.for_domain(TesterObject) is TesterContext
    for context_cls in (
        DomainTesterContext,
        AggregateTesterContext,
        TransferObjectTesterContext,
        RepoTesterContext,
        ContextTesterContext,
    ):
        assert 'domain_type' not in context_cls.__dict__

    # from_domain binds the registered class and the named variant.
    assert isinstance(BaseContext.from_domain(tester), TesterContext)
    assert isinstance(DomainTesterContext.from_domain(tester), DomainTesterContext)

# ** test: test_session_context_preserves_request_and_tester_registration
def test_session_context_preserves_request_and_tester_registration() -> None:
    '''
    Assert the test session is a request and does not clobber registrations.

    :return: None
    :rtype: None
    '''

    # The session omits domain_type and stays a request, not an app hub.
    assert 'domain_type' not in _TestSessionContext.__dict__
    assert BaseContext.for_domain(Request) is RequestContext
    assert BaseContext.for_domain(TesterObject) is TesterContext
    assert issubclass(_TestSessionContext, RequestContext)
    assert not issubclass(_TestSessionContext, AppSessionContext)

# ** test: test_session_context_given_merges_state_and_returns_self
def test_session_context_given_merges_state_and_returns_self() -> None:
    '''
    Assert given merges request data without writing sample data.

    :return: None
    :rtype: None
    '''

    # Bind a domain tester and capture the sample mapping identity.
    tester = _build_error_message_tester()
    test_ctx = DomainTesterContext.from_domain(tester)
    session = build_test_session(test_ctx)
    sample = tester.sample_data

    # Later keys replace earlier keys on the same session.
    assert session.given(a=1).given(a=2) is session
    assert session.data == {'a': 2}
    assert tester.sample_data is sample
    assert 'a' not in sample
    assert sample == ERROR_MESSAGE_SAMPLE_DATA

# ** test: test_session_context_verify_normalizes_predicates_and_literals
def test_session_context_verify_normalizes_predicates_and_literals() -> None:
    '''
    Assert verify stores callables by identity and wraps literals.

    :return: None
    :rtype: None
    '''

    # Queue a callable and a literal on one session.
    session = build_test_session(
        DomainTesterContext.from_domain(_build_error_message_tester())
    )

    def predicate(outcome):
        return outcome == 3

    assert session.verify(predicate) is session
    assert session.verify(3, message='literal outcome') is session
    assert len(session.verifications) == 2
    assert isinstance(session.verifications[0], Verification)
    assert isinstance(session.verifications[1], Verification)
    assert session.verifications[0].predicate is predicate
    assert session.verifications[0].source is predicate
    assert session.verifications[1].source == 3
    assert session.verifications[1].predicate(3) is True

# ** test: test_session_context_evaluates_all_verifications_and_clears_queue
def test_session_context_evaluates_all_verifications_and_clears_queue() -> None:
    '''
    Assert evaluation reports every failure and clears the same queue.

    :return: None
    :rtype: None
    '''

    # Queue two failures and one pass against outcome 2.
    session = build_test_session(
        DomainTesterContext.from_domain(_build_error_message_tester())
    )
    session.verify(lambda outcome: outcome == 1, message='first failure')
    session.verify(lambda outcome: outcome == 3, message='second failure')
    session.verify(lambda outcome: outcome == 2, message='passing check')
    session.capture_outcome(2)

    # One assertion names both failures, then the queue is empty.
    with pytest.raises(AssertionError) as raised:
        session.evaluate_verifications()
    assert 'first failure' in str(raised.value)
    assert 'second failure' in str(raised.value)
    assert len(session.verifications) == 0

    # A later matching literal evaluates and leaves the queue empty.
    session.verify(2)
    assert session.evaluate_verifications() is None
    assert len(session.verifications) == 0

# ** test: test_session_context_records_raised_predicates_and_continues
def test_session_context_records_raised_predicates_and_continues() -> None:
    '''
    Assert a raised predicate is recorded and the next predicate still runs.

    :return: None
    :rtype: None
    '''

    # Queue a raising predicate and a predicate that records its outcome.
    session = build_test_session(
        DomainTesterContext.from_domain(_build_error_message_tester())
    )
    seen = []

    def raising(outcome):
        raise ValueError('predicate error')

    def continued(outcome):
        seen.append(outcome)
        return False

    session.verify(raising, message='raised predicate')
    session.verify(continued, message='continued predicate')
    session.capture_outcome('outcome')

    # Both failures are reported and the queue is cleared.
    with pytest.raises(AssertionError) as raised:
        session.evaluate_verifications()
    message = str(raised.value)
    assert 'raised predicate' in message
    assert 'predicate error' in message
    assert 'continued predicate' in message
    assert seen == ['outcome']
    assert len(session.verifications) == 0

# ** test: add_default_testers
def test_add_default_testers_seeds_polymorphic_domain_objects() -> None:
    '''
    Assert the tester seeder stores TesterObject values under the tester prefix.

    :return: None
    :rtype: None
    '''

    # Decorate a cache builder with three raw tester mappings.
    @add_default_testers({
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
    })
    def build(cache=None):
        return CacheContext(cache=cache)

    # Each key is a TesterObject with the mapping key as its id.
    cache = build()
    for key in (
        'domain.ErrorMessage',
        'aggregate.ErrorAggregate',
        'transfer_object.ErrorConfigObject',
    ):
        assert isinstance(cache.get(key, *TESTER_CACHE_PREFIX), TesterObject)
    aggregate = cache.get('aggregate.ErrorAggregate', *TESTER_CACHE_PREFIX)
    assert aggregate.id == 'aggregate.ErrorAggregate'
    assert aggregate.type == 'aggregate'

# ** test: add_default_test_presets
def test_add_default_test_presets_seeds_raw_given_state() -> None:
    '''
    Assert preset seeding stores the raw mapping, not a TesterObject.

    :return: None
    :rtype: None
    '''

    # Decorate a no-argument cache builder and call it.
    @add_default_test_presets({'sum': {'a': 1, 'b': 2}})
    def build():
        return CacheContext()

    stored = build().get('sum', *TEST_PRESET_CACHE_PREFIX)
    assert stored == {'a': 1, 'b': 2}
    assert not isinstance(stored, TesterObject)

# ** test: test_session_context_run_exercises_bound_tester
def test_session_context_run_exercises_bound_tester() -> None:
    '''
    Assert run overlays request data and does not dispatch a feature.

    :return: None
    :rtype: None
    '''

    # Overlay text and verify the constructed error message.
    tester = _build_error_message_tester()
    sample = tester.sample_data
    session = build_test_session(DomainTesterContext.from_domain(tester))
    outcome = session.given(text='overlay').verify(
        lambda result: result.text == 'overlay'
    ).run()
    assert isinstance(outcome, ErrorMessage)
    assert outcome.text == 'overlay'
    assert outcome.lang == 'en_US'
    assert len(session.verifications) == 0
    assert tester.sample_data is sample
    assert sample == ERROR_MESSAGE_SAMPLE_DATA
    source = inspect.getsource(_TestSessionContext.run)
    for forbidden in (
        'execute_feature',
        'build_logger',
        'handle_error',
        'TiferetAPIError',
    ):
        assert forbidden not in source

# ** test: test_session_context_invoke_merges_params_and_returns_self
def test_session_context_invoke_merges_params_and_returns_self() -> None:
    '''
    Assert invoke merges params and has no feature_id parameter.

    :return: None
    :rtype: None
    '''

    # Invoke overlays request data and returns the same session.
    session = build_test_session(
        DomainTesterContext.from_domain(_build_error_message_tester())
    )
    assert session.invoke(text='from invoke') is session
    assert session.data == {'text': 'from invoke'}
    outcome = session.verify(
        lambda result: result.text == 'from invoke'
    ).run()
    assert outcome.text == 'from invoke'
    assert 'feature_id' not in inspect.signature(_TestSessionContext.invoke).parameters

# ** test: build_tester_context_selects_variant_class
def test_build_tester_context_selects_variant_class() -> None:
    '''
    Assert the blueprint selector binds the matching variant context.

    :return: None
    :rtype: None
    '''

    # Domain, aggregate, and transfer testers select their variant classes.
    domain_ctx = build_tester_context(_build_error_message_tester())
    aggregate_ctx = build_tester_context(TesterObject(
        type='aggregate',
        id='aggregate.ErrorAggregate',
        module_path=ErrorAggregate.__module__,
        class_name=ErrorAggregate.__name__,
        sample_data={'id': 'TEST_ERROR', 'name': 'Test Error'},
        equality_fields=['id', 'name'],
        set_attribute_params=[
            ('name', 'Updated Error', None),
            ('invalid_attribute', 'value', INVALID_MODEL_ATTRIBUTE_ID),
        ],
    ))
    transfer_ctx = build_tester_context(TesterObject(
        type='transfer_object',
        id='transfer_object.ErrorConfigObject',
        module_path=ErrorConfigObject.__module__,
        class_name=ErrorConfigObject.__name__,
        aggregate_module_path=ErrorAggregate.__module__,
        aggregate_class_name=ErrorAggregate.__name__,
        sample_data={'id': 'TEST_ERROR', 'name': 'Test Error'},
        aggregate_sample_data={'id': 'TEST_ERROR', 'name': 'Test Error'},
        equality_fields=['id', 'name'],
    ))
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
    '''
    Assert use_tester injects a domain tester context.

    :param test_ctx: The injected domain tester context.
    :type test_ctx: DomainTesterContext
    :return: None
    :rtype: None
    '''

    # The injected context can construct the sample.
    assert isinstance(test_ctx, DomainTesterContext)
    test_ctx.assert_new()

# ** test: use_tester_reuses_master_and_creates_new_sessions
def test_use_tester_reuses_master_and_creates_new_sessions() -> None:
    '''
    Assert a decorated class reuses one tester context and fresh sessions.

    :return: None
    :rtype: None
    '''

    # Decorate a local class with two methods that return the injected pair.
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

    probe = Probe()
    ctx_a, session_a = probe.test_a()
    ctx_b, session_b = probe.test_b()
    assert ctx_a is ctx_b
    assert session_a is not session_b
    assert isinstance(session_a, _TestSessionContext)
    assert isinstance(session_b, _TestSessionContext)
    assert session_a.tester_ctx is ctx_a
    assert session_b.tester_ctx is ctx_b

# ** test: use_tester_wraps_class_fixture_members
def test_use_tester_wraps_class_fixture_members() -> None:
    '''
    Assert class fixtures are wrapped and their signatures drop test_ctx.

    :return: None
    :rtype: None
    '''

    # Decorate a class whose fixture and test both declare test_ctx.
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

    # Unwrap the fixture through the pytest slot, then the wrapper, then itself.
    member = Probe.__dict__['bound']
    fixture_fn = getattr(member, '_fixture_function', member)
    wrapped = getattr(fixture_fn, '__wrapped__', fixture_fn)
    unwrapped = wrapped if wrapped is not fixture_fn else member
    assert 'test_ctx' not in inspect.signature(fixture_fn).parameters
    assert 'test_ctx' not in inspect.signature(Probe.test_same).parameters
    probe = Probe()
    assert fixture_fn(probe) is probe.test_same()
    assert isinstance(probe.test_same(), DomainTesterContext)
    assert unwrapped is not None

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
    '''
    Assert injection is by parameter name and stripped from the signature.

    :param injection_marker: The pytest fixture marker.
    :type injection_marker: str
    :param session: The injected test session.
    :type session: _TestSessionContext
    :param test_ctx: The injected domain tester context.
    :type test_ctx: DomainTesterContext
    :return: None
    :rtype: None
    '''

    # The fixture, session, and tester arrive by name.
    assert injection_marker == 'marker'
    assert isinstance(test_ctx, DomainTesterContext)
    assert isinstance(session, _TestSessionContext)
    assert session.tester_ctx is test_ctx
    parameters = inspect.signature(test_use_tester_injects_by_parameter_name).parameters
    assert 'test_ctx' not in parameters
    assert 'session' not in parameters
    assert 'tester_ctx' not in parameters

# ** test: use_tester_injects_only_declared_session
@use_tester(
    type='domain',
    target_cls=ErrorMessage,
    sample_data=dict(ERROR_MESSAGE_SAMPLE_DATA),
    equality_fields=['lang', 'text'],
)
def test_use_tester_injects_only_declared_session(session) -> None:
    '''
    Assert a function that declares only session still receives a bound session.

    :param session: The injected test session.
    :type session: _TestSessionContext
    :return: None
    :rtype: None
    '''

    # The session is bound to a domain tester context.
    assert isinstance(session, _TestSessionContext)
    assert isinstance(session.tester_ctx, DomainTesterContext)

# ** test: event_tester_contexts_omit_domain_type
def test_event_tester_contexts_omit_domain_type() -> None:
    '''
    Assert event tester contexts do not register their own domain type.

    :return: None
    :rtype: None
    '''

    # Omission keeps TesterObject mapped to TesterContext.
    assert 'domain_type' not in DomainEventTesterContext.__dict__
    assert 'domain_type' not in ServiceEventTesterContext.__dict__
    assert BaseContext.for_domain(TesterObject) is TesterContext

# ** test: service_event_tester_context_handle_and_asserts
def test_service_event_tester_context_handle_and_asserts() -> None:
    '''
    Assert service-event handle, not-found, and empty required-param cases.

    :return: None
    :rtype: None
    '''

    # Bind a GetError service-event tester.
    test_ctx = ServiceEventTesterContext.from_domain(TesterObject(
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
    ))
    assert isinstance(test_ctx, DomainEventTesterContext)

    # The primary mock is the named dependency, and handle returns its get value.
    dependencies = test_ctx.mock_dependencies()
    assert test_ctx.get_service_mock(dependencies) is dependencies['error_service']
    aggregate = ErrorAggregate(
        id='TEST_ERROR',
        name='Test Error',
        message=[{'lang': 'en_US', 'text': 'An error occurred.'}],
    )
    test_ctx.get_service_mock(dependencies).get.return_value = aggregate
    assert test_ctx.handle(dependencies) is aggregate
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
    '''
    Assert use_tester injects a service-event tester context.

    :param test_ctx: The injected service-event tester context.
    :type test_ctx: ServiceEventTesterContext
    :return: None
    :rtype: None
    '''

    # The not-found assertion completes.
    assert isinstance(test_ctx, ServiceEventTesterContext)
    test_ctx.assert_not_found()

# ** test: generic_tester_context_omits_domain_type
def test_generic_tester_context_omits_domain_type() -> None:
    '''
    Assert the generic tester omits domain_type and fluent session verbs.

    :return: None
    :rtype: None
    '''

    # Registry mappings stay on the declaring contexts.
    assert 'domain_type' not in GenericTesterContext.__dict__
    assert BaseContext.for_domain(TesterObject) is TesterContext
    assert BaseContext.for_domain(Request) is RequestContext
    assert not hasattr(GenericTesterContext, 'given')
    assert not hasattr(GenericTesterContext, 'invoke')
    assert not hasattr(GenericTesterContext, 'verify')
    assert not hasattr(GenericTesterContext, 'run')

# ** test: generic_tester_context_assert_contract
def test_generic_tester_context_assert_contract() -> None:
    '''
    Assert contract checks pass for a concrete class and an ABC.

    :return: None
    :rtype: None
    '''

    # A concrete class and the ErrorService ABC both lock.
    message_ctx = build_tester_context(TesterObject(
        type='generic',
        id='generic.ErrorMessage',
        module_path=ErrorMessage.__module__,
        class_name=ErrorMessage.__name__,
        sample_data=dict(ERROR_MESSAGE_SAMPLE_DATA),
    ))
    service_ctx = build_tester_context(TesterObject(
        type='generic',
        id='generic.ErrorService',
        module_path=ErrorService.__module__,
        class_name=ErrorService.__name__,
    ))
    assert message_ctx.assert_contract() is None
    assert service_ctx.assert_contract(target=ErrorService) is None
    for name in ErrorService.__abstractmethods__:
        assert hasattr(ErrorService, name)

# ** test: session_run_generic_invokes_local_callable
def test_session_run_generic_invokes_local_callable() -> None:
    '''
    Assert a generic run invokes the supplied callable with request data.

    :return: None
    :rtype: None
    '''

    # Keep the tester and sample identities across the run.
    tester = TesterObject(
        type='generic',
        id='generic.add_values',
        module_path=__name__,
        class_name='_add_values',
    )
    sample = tester.sample_data
    session = build_test_session(build_tester_context(tester))
    outcome = session.given(a=1, b=2).verify(3).run(target=_add_values)
    assert outcome == 3
    assert session.tester_ctx.domain is tester
    assert tester.sample_data is sample
    source = inspect.getsource(_TestSessionContext.run)
    for forbidden in (
        'execute_feature',
        '_dispatch_event',
        'build_logger',
        'handle_error',
    ):
        assert forbidden not in source

# ** test: session_run_generic_uses_get_target_without_invoke
def test_session_run_generic_uses_get_target_without_invoke() -> None:
    '''
    Assert a generic run with no target uses get_target.

    :return: None
    :rtype: None
    '''

    # The named callable is resolved and invoked with given state.
    tester = TesterObject(
        type='generic',
        id='generic.add_values',
        module_path=__name__,
        class_name='_add_values',
    )
    session = build_test_session(build_tester_context(tester))
    assert session.given(a=2, b=3).verify(5).run() == 5

# ** test: session_run_rejects_target_on_specialized_tester
def test_session_run_rejects_target_on_specialized_tester() -> None:
    '''
    Assert a specialized tester rejects run(target=...).

    :return: None
    :rtype: None
    '''

    # The domain session raises before exercising the target.
    session = build_test_session(
        DomainTesterContext.from_domain(_build_error_message_tester())
    )
    with pytest.raises(ValueError):
        session.run(target=_add_values)

# ** test: repo_tester_context_omits_domain_type
def test_repo_tester_context_omits_domain_type() -> None:
    '''
    Assert the repo tester omits domain_type and preserves registry mappings.

    :return: None
    :rtype: None
    '''

    # from_domain returns the repo variant without re-registering.
    tester = TesterObject(
        type='repo',
        id='repo.ErrorConfigRepository',
        module_path='tiferet.repos.error',
        class_name='ErrorConfigRepository',
        config_parameter='error_config',
    )
    assert 'domain_type' not in RepoTesterContext.__dict__
    assert BaseContext.for_domain(TesterObject) is TesterContext
    assert BaseContext.for_domain(Request) is RequestContext
    bound = RepoTesterContext.from_domain(tester)
    assert isinstance(bound, RepoTesterContext)
    assert isinstance(bound, TesterContext)

# ** test: repo_tester_context_empty_cases_are_noops
def test_repo_tester_context_empty_cases_are_noops() -> None:
    '''
    Assert empty repository case lists do not touch a repository.

    :return: None
    :rtype: None
    '''

    # None is a legal collaborator when every case list is empty.
    test_ctx = RepoTesterContext.from_domain(TesterObject(
        type='repo',
        id='repo.ErrorConfigRepository',
        module_path='tiferet.repos.error',
        class_name='ErrorConfigRepository',
        config_parameter='error_config',
    ))
    test_ctx.assert_exists(None)
    test_ctx.assert_get(None)
    test_ctx.assert_list(None)
    test_ctx.assert_save(None)
    test_ctx.assert_delete(None)

# *** testers

# ** tester: test_context_tester_context
class TestContextTesterContext:
    '''
    Tests for ContextTesterContext registry and case assertions.
    '''

    # * test: omits_domain_type_and_preserves_registry
    def test_omits_domain_type_and_preserves_registry(self) -> None:
        '''
        Assert the context tester omits domain_type and preserves registrations.

        :return: None
        :rtype: None
        '''

        # Bind a RequestContext identity tester.
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
        '''
        Assert empty context case lists return without importing.

        :return: None
        :rtype: None
        '''

        # The same identity tester has no case lists.
        test_ctx = ContextTesterContext.from_domain(TesterObject(
            type='context',
            id='context.RequestContext',
            module_path=RequestContext.__module__,
            class_name=RequestContext.__name__,
            domain_module_path=Request.__module__,
            domain_class_name=Request.__name__,
        ))
        assert test_ctx.assert_from_domain() is None
        assert test_ctx.assert_domain_type() is None
        assert test_ctx.assert_for_domain() is None

    # * test: declaring_request_context_cases
    def test_declaring_request_context_cases(self) -> None:
        '''
        Assert declaring RequestContext cases complete.

        :return: None
        :rtype: None
        '''

        # Supply sample data and one case for each assertion.
        test_ctx = ContextTesterContext.from_domain(TesterObject(
            type='context',
            id='context.RequestContext',
            module_path=RequestContext.__module__,
            class_name=RequestContext.__name__,
            domain_module_path=Request.__module__,
            domain_class_name=Request.__name__,
            sample_data={
                'session_id': 'test-session',
                'feature_id': 'test.feature',
            },
            from_domain_cases=[{
                'data': {
                    'session_id': 'test-session',
                    'feature_id': 'test.feature',
                },
            }],
            domain_type_cases=[{'declares': True}],
            for_domain_cases=[{
                'domain_module_path': Request.__module__,
                'domain_class_name': Request.__name__,
                'context_module_path': RequestContext.__module__,
                'context_class_name': RequestContext.__name__,
            }],
        ))
        test_ctx.assert_from_domain()
        test_ctx.assert_domain_type()
        test_ctx.assert_for_domain()

    # * test: omitting_cli_session_does_not_clobber_app_session
    def test_omitting_cli_session_does_not_clobber_app_session(self) -> None:
        '''
        Assert an omitting CLI session does not replace the app session mapping.

        :return: None
        :rtype: None
        '''

        # Map AppSession and TesterObject through the registry cases.
        test_ctx = ContextTesterContext.from_domain(TesterObject(
            type='context',
            id='context.CliSessionContext',
            module_path=CliSessionContext.__module__,
            class_name=CliSessionContext.__name__,
            domain_module_path=AppSession.__module__,
            domain_class_name=AppSession.__name__,
            domain_type_cases=[{'declares': False}],
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
        ))
        test_ctx.assert_domain_type()
        test_ctx.assert_for_domain()
