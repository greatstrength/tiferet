"""Tests for Tiferet Tester Contexts"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest

# ** app
from tiferet.assets import TiferetError
from tiferet.assets.error import ERROR_NOT_FOUND_ID
from tiferet.assets.tester import (
    AGGREGATE_ERROR_TESTER_DATA,
    CORE_DEFAULT_TESTERS,
    DOMAIN_ERROR_MESSAGE_TESTER_DATA,
    SERVICE_EVENT_GET_ERROR_TESTER_DATA,
    SERVICE_EVENT_GET_ERROR_TESTER_ID,
)
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.core import BaseContext
from tiferet.contexts.request import RequestContext
from tiferet.contexts import tester as tester_contexts
from tiferet.domain import AppSession, Request
from tiferet.domain import tester as tester_mod
from tiferet.events import DomainEvent
from tiferet.mappers.error import ErrorAggregate

# *** constants

# ** constant: tester_object
TESTER_OBJECT = tester_mod.TesterObject

# ** constant: tester_context
TESTER_CONTEXT = tester_contexts.TesterContext

# ** constant: test_session_context
TEST_SESSION_CONTEXT = tester_contexts.TestSessionContext

# ** constant: variant_classes
VARIANT_CLASSES = [
    tester_contexts.DomainTesterContext,
    tester_contexts.AggregateTesterContext,
    tester_contexts.TransferObjectTesterContext,
    tester_contexts.DomainEventTesterContext,
    tester_contexts.ServiceEventTesterContext,
]

# ** constant: forbidden_context_names
FORBIDDEN_CONTEXT_NAMES = [
    'GenericTesterContext',
    'RepoTesterContext',
    'ContextTesterContext',
    'TestRequestContext',
]

# ** constant: error_message_tester
def error_message_tester(**overrides):
    '''
    Build a domain ErrorMessage tester.

    :param overrides: Optional TesterObject field overrides.
    :type overrides: dict
    :return: A TesterObject for ErrorMessage.
    :rtype: object
    '''

    # Merge the catalog row with an id and caller overrides.
    payload = dict(DOMAIN_ERROR_MESSAGE_TESTER_DATA)
    payload['id'] = 'domain.ErrorMessage'
    payload.update(overrides)
    return TESTER_OBJECT.model_validate(payload)

# ** constant: error_aggregate_tester
def error_aggregate_tester(**overrides):
    '''
    Build an aggregate ErrorAggregate tester.

    :param overrides: Optional TesterObject field overrides.
    :type overrides: dict
    :return: A TesterObject for ErrorAggregate.
    :rtype: object
    '''

    # Merge the catalog row with an id and caller overrides.
    payload = dict(AGGREGATE_ERROR_TESTER_DATA)
    payload['id'] = 'aggregate.ErrorAggregate'
    payload.update(overrides)
    return TESTER_OBJECT.model_validate(payload)

# ** constant: get_error_tester
def get_error_tester(**overrides):
    '''
    Build a service-event GetError tester.

    :param overrides: Optional TesterObject field overrides.
    :type overrides: dict
    :return: A TesterObject for GetError.
    :rtype: object
    '''

    # Merge the catalog row with an id and caller overrides.
    payload = dict(SERVICE_EVENT_GET_ERROR_TESTER_DATA)
    payload['id'] = SERVICE_EVENT_GET_ERROR_TESTER_ID
    payload.update(overrides)
    return TESTER_OBJECT.model_validate(payload)

# ** constant: required_param_event
class RequiredParamEvent(DomainEvent):
    '''
    A tiny domain event that requires one parameter.
    '''

    def __init__(self, **kwargs):
        pass

    @DomainEvent.parameters_required(['needed'])
    def execute(self, needed: str = None, **kwargs):
        return needed

# *** testers

# ** tester: TestTesterContextRegistry
class TestTesterContextRegistry:
    '''
    Tests for tester context registry and omitting-domain_type variants.
    '''

    # * method: test_master_and_variant_registration
    def test_master_and_variant_registration(self) -> None:
        '''
        Test TesterObject maps to TesterContext and variants omit domain_type.
        '''

        # Assert the master registers TesterObject.
        assert TESTER_CONTEXT.domain_type is TESTER_OBJECT
        assert BaseContext.for_domain(TESTER_OBJECT) is TESTER_CONTEXT

        # Assert Request and AppSession registry entries are unchanged.
        assert BaseContext.for_domain(Request) is RequestContext
        assert BaseContext.for_domain(AppSession) is AppSessionContext

        # Assert each variant omits domain_type and from_domain binds that subclass.
        tester = error_message_tester()
        for variant_cls in VARIANT_CLASSES:
            assert 'domain_type' not in variant_cls.__dict__
            bound = variant_cls.from_domain(tester)
            assert isinstance(bound, variant_cls)
            assert bound.domain is tester

        # Assert registry from_domain still selects the master.
        master = BaseContext.from_domain(tester)
        assert type(master) is TESTER_CONTEXT

    # * method: test_extension_contexts_absent
    def test_extension_contexts_absent(self) -> None:
        '''
        Test that generic, repo, and context tester contexts are not defined.
        '''

        # Assert each forbidden context name is absent.
        for name in FORBIDDEN_CONTEXT_NAMES:
            assert not hasattr(tester_contexts, name)

# ** tester: TestSessionIsARequest
class TestSessionIsARequest:
    '''
    Tests that the test session is a request, not an application session.
    '''

    # * method: test_session_is_request_context
    def test_session_is_request_context(self) -> None:
        '''
        Test TestSessionContext subclasses RequestContext and omits domain_type.
        '''

        # Assert the session omits domain_type and is not an AppSessionContext.
        assert 'domain_type' not in TEST_SESSION_CONTEXT.__dict__
        assert issubclass(TEST_SESSION_CONTEXT, RequestContext)
        assert not issubclass(TEST_SESSION_CONTEXT, AppSessionContext)

        # Construct a session and assert it binds a Request as domain.
        test_ctx = tester_contexts.DomainTesterContext.from_domain(error_message_tester())
        session = TEST_SESSION_CONTEXT(tester_ctx=test_ctx)
        assert isinstance(session.domain, Request)
        assert session.tester_ctx is test_ctx

        # Assert fluent methods return self and overlay last-write-wins.
        assert session.given(a=1) is session
        assert session.invoke(b=2) is session
        assert session.verify(True) is session
        overlay = TEST_SESSION_CONTEXT(tester_ctx=test_ctx)
        assert overlay.given(a=1).given(a=2).data == {'a': 2}

    # * method: test_module_does_not_steal_the_hub
    def test_module_does_not_steal_the_hub(self) -> None:
        '''
        Test the tester context module does not import AppSessionContext or presets.
        '''

        # Read the production module source.
        source = Path(tester_contexts.__file__).read_text()

        # Assert hub and preset artifacts are absent.
        assert 'AppSessionContext' not in source
        assert not hasattr(tester_contexts, 'TEST_PRESET_CACHE_PREFIX')
        assert not hasattr(tester_contexts, 'add_default_test_presets')
        assert 'import pytest' not in source
        assert 'import inspect' not in source

# ** tester: TestSessionRunAgainstBoundTester
class TestSessionRunAgainstBoundTester:
    '''
    Tests for TestSessionContext.run against a bound tester.
    '''

    # * method: test_domain_run_overlays_request_not_sample
    def test_domain_run_overlays_request_not_sample(self) -> None:
        '''
        Test given/verify/run overlays request data without mutating sample_data.
        '''

        # Bind a domain tester and capture sample identity.
        tester = error_message_tester()
        test_ctx = tester_contexts.DomainTesterContext.from_domain(tester)
        sample_id = id(test_ctx.domain.sample_data)
        sample_lang = test_ctx.domain.sample_data['lang']

        # Overlay lang on the request and verify the constructed outcome.
        session = TEST_SESSION_CONTEXT(tester_ctx=test_ctx)
        outcome = (
            session
            .given(lang='fr_FR')
            .verify(lambda result: result.lang == 'fr_FR')
            .run()
        )

        # Assert overlay lived on the request and sample identity is unchanged.
        assert outcome.lang == 'fr_FR'
        assert session.data['lang'] == 'fr_FR'
        assert id(test_ctx.domain.sample_data) == sample_id
        assert test_ctx.domain.sample_data['lang'] == sample_lang
        assert session.verifications == []

    # * method: test_two_failing_verifies_raise_one_error
    def test_two_failing_verifies_raise_one_error(self) -> None:
        '''
        Test two failing verify predicates raise one AssertionError.
        '''

        # Queue two failing literal predicates.
        test_ctx = tester_contexts.DomainTesterContext.from_domain(error_message_tester())
        session = TEST_SESSION_CONTEXT(tester_ctx=test_ctx)

        # Assert one AssertionError is raised and the queue is cleared.
        with pytest.raises(AssertionError) as caught:
            session.verify(False, message='first').verify(False, message='second').run()
        assert 'first' in str(caught.value)
        assert 'second' in str(caught.value)
        assert session.verifications == []

    # * method: test_run_ignores_target
    def test_run_ignores_target(self) -> None:
        '''
        Test run(target=...) still succeeds and ignores the target argument.
        '''

        # Run with an explicit target that must be ignored.
        test_ctx = tester_contexts.DomainTesterContext.from_domain(error_message_tester())
        session = TEST_SESSION_CONTEXT(tester_ctx=test_ctx)
        outcome = session.run(target=object())

        # Assert the bound tester still constructed ErrorMessage.
        assert outcome.lang == 'en_US'

    # * method: test_run_source_is_not_a_hub
    def test_run_source_is_not_a_hub(self) -> None:
        '''
        Test run and its module do not mention hub dispatch or TiferetAPIError.
        '''

        # Read the production module source.
        source = Path(tester_contexts.__file__).read_text()

        # Assert hub dispatch names are absent.
        assert 'execute_feature' not in source
        assert 'build_logger' not in source
        assert 'handle_error' not in source
        assert 'TiferetAPIError' not in source

    # * method: test_service_event_run_goes_through_handle
    def test_service_event_run_goes_through_handle(self) -> None:
        '''
        Test a service-event session run dispatches through handle.
        '''

        # Bind a GetError tester and wrap handle.
        tester = get_error_tester()
        test_ctx = tester_contexts.ServiceEventTesterContext.from_domain(tester)
        calls = []
        original = test_ctx.handle

        def wrapped_handle(dependencies=None, **kwargs):
            calls.append('handle')
            return original(dependencies=dependencies, **kwargs)

        test_ctx.handle = wrapped_handle
        TEST_SESSION_CONTEXT(tester_ctx=test_ctx).run()

        # Assert handle ran and execute_feature was not involved.
        assert calls == ['handle']

    # * method: test_get_error_not_found_propagates
    def test_get_error_not_found_propagates(self) -> None:
        '''
        Test a raw TiferetError from GetError propagates from run.
        '''

        # Configure the service mock to miss.
        tester = get_error_tester()
        test_ctx = tester_contexts.ServiceEventTesterContext.from_domain(tester)
        deps = test_ctx.mock_dependencies()
        deps['error_service'].get.return_value = None
        test_ctx.mock_dependencies = lambda: deps

        # Assert run propagates the not-found error without wrapping.
        with pytest.raises(TiferetError) as caught:
            TEST_SESSION_CONTEXT(tester_ctx=test_ctx).run()
        assert caught.value.error_code == ERROR_NOT_FOUND_ID

# ** tester: TestVariantAssertions
class TestVariantAssertions:
    '''
    Tests for variant assertion methods and empty-list no-ops.
    '''

    # * method: test_empty_case_lists_are_no_ops
    def test_empty_case_lists_are_no_ops(self) -> None:
        '''
        Test empty optional case lists do not raise.
        '''

        # Domain description cases default empty.
        domain_ctx = tester_contexts.DomainTesterContext.from_domain(
            error_message_tester(description_cases=[])
        )
        domain_ctx.assert_description()

        # Aggregate set-attribute cases default empty.
        aggregate_ctx = tester_contexts.AggregateTesterContext.from_domain(
            error_aggregate_tester(set_attribute_params=[])
        )
        aggregate_ctx.assert_set_attribute()

        # Event required-params default empty.
        event_ctx = tester_contexts.DomainEventTesterContext.from_domain(
            get_error_tester(required_params=[])
        )
        event_ctx.assert_missing_required_params()

        # Not-found is a no-op when the contract is unset.
        unset_ctx = tester_contexts.ServiceEventTesterContext.from_domain(
            get_error_tester(service_attr=None, not_found_error_code=None)
        )
        unset_ctx.assert_not_found()

    # * method: test_assert_description
    def test_assert_description(self) -> None:
        '''
        Test assert_description uses (name, args, expected) cases.
        '''

        # Assert ErrorMessage.format() with empty args.
        ctx = tester_contexts.DomainTesterContext.from_domain(error_message_tester())
        ctx.assert_description()

    # * method: test_assert_set_attribute_mutates_fresh_target
    def test_assert_set_attribute_mutates_fresh_target(self) -> None:
        '''
        Test assert_set_attribute mutates a fresh aggregate, not self.domain.
        '''

        # Bind an aggregate tester and capture sample identity.
        tester = error_aggregate_tester()
        ctx = tester_contexts.AggregateTesterContext.from_domain(tester)
        sample_id = id(ctx.domain.sample_data)
        original_name = ctx.domain.sample_data['name']

        # Assert mutations succeed and do not write back to the tester.
        ctx.assert_set_attribute()
        assert ctx.domain is tester
        assert id(ctx.domain.sample_data) == sample_id
        assert ctx.domain.sample_data['name'] == original_name
        assert isinstance(ctx.domain, TESTER_OBJECT)
        assert not isinstance(ctx.domain, ErrorAggregate)

    # * method: test_assert_missing_required_params
    def test_assert_missing_required_params(self) -> None:
        '''
        Test assert_missing_required_params against a local domain event.
        '''

        # Bind a tester pointing at the local event.
        tester = TESTER_OBJECT(
            type='domain_event',
            id='domain_event.RequiredParamEvent',
            module_path=RequiredParamEvent.__module__,
            class_name='RequiredParamEvent',
            required_params=['needed'],
        )
        ctx = tester_contexts.DomainEventTesterContext.from_domain(tester)
        ctx.assert_missing_required_params()

    # * method: test_assert_not_found
    def test_assert_not_found(self) -> None:
        '''
        Test assert_not_found against GetError without pytest.raises in the context.
        '''

        # Assert the service-event not-found contract.
        ctx = tester_contexts.ServiceEventTesterContext.from_domain(get_error_tester())
        ctx.assert_not_found()

# ** tester: TestAddDefaultTesters
class TestAddDefaultTesters:
    '''
    Tests for add_default_testers cache seeding.
    '''

    # * method: test_seeds_tester_object_instances
    def test_seeds_tester_object_instances(self) -> None:
        '''
        Test add_default_testers seeds TesterObject instances under the prefix.
        '''

        # Wrap a cache builder with the default tester catalog.
        @tester_contexts.add_default_testers(CORE_DEFAULT_TESTERS)
        def build_cache(cache=None):
            return CacheContext(cache)

        # Assert seeded values are TesterObject instances under the prefix.
        cache = build_cache()
        seeded = cache.get(
            'domain.ErrorMessage',
            *tester_contexts.TESTER_CACHE_PREFIX,
        )
        assert isinstance(seeded, TESTER_OBJECT)
        assert seeded.type == 'domain'
        assert seeded.id == 'domain.ErrorMessage'
        assert tester_contexts.TESTER_CACHE_PREFIX == ('app', 'testers')
