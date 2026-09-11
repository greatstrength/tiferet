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
    CONTEXT_REQUEST_CONTEXT_TESTER_DATA,
    CONTEXT_REQUEST_CONTEXT_TESTER_ID,
    CORE_DEFAULT_TESTERS,
    DOMAIN_ERROR_MESSAGE_TESTER_DATA,
    SERVICE_EVENT_GET_ERROR_TESTER_DATA,
    SERVICE_EVENT_GET_ERROR_TESTER_ID,
)
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.cli import CliSessionContext
from tiferet.contexts.core import BaseContext, ContextMeta
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
    tester_contexts.GenericTesterContext,
    tester_contexts.RepoTesterContext,
    tester_contexts.ContextTesterContext,
]

# ** constant: forbidden_context_names
FORBIDDEN_CONTEXT_NAMES = [
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

# ** constant: probe_function
def _probe_function():
    '''Return a sentinel for generic session run tests.'''

    # Return a stable sentinel.
    return 7

# ** constant: generic_tester
def generic_tester(**overrides):
    '''
    Build a generic tester pointing at _probe_function.

    :param overrides: Optional TesterObject field overrides.
    :type overrides: dict
    :return: A generic TesterObject.
    :rtype: object
    '''

    # Merge generic identity with caller overrides.
    payload = {
        'type': 'generic',
        'id': 'generic._probe_function',
        'module_path': __name__,
        'class_name': '_probe_function',
    }
    payload.update(overrides)
    return TESTER_OBJECT(**payload)

# ** constant: repo_tester
def repo_tester(**overrides):
    '''
    Build a repo tester pointing at ErrorConfigRepository.

    :param overrides: Optional TesterObject field overrides.
    :type overrides: dict
    :return: A repo TesterObject.
    :rtype: object
    '''

    # Merge repo identity with caller overrides.
    payload = {
        'type': 'repo',
        'id': 'repo.ErrorConfigRepository',
        'module_path': 'tiferet.repos.error',
        'class_name': 'ErrorConfigRepository',
    }
    payload.update(overrides)
    return TESTER_OBJECT(**payload)

# ** constant: context_tester
def context_tester(**overrides):
    '''
    Build a context tester from the RequestContext catalog row.

    :param overrides: Optional TesterObject field overrides.
    :type overrides: dict
    :return: A context TesterObject.
    :rtype: object
    '''

    # Merge the catalog row with an id and caller overrides.
    payload = dict(CONTEXT_REQUEST_CONTEXT_TESTER_DATA)
    payload['id'] = CONTEXT_REQUEST_CONTEXT_TESTER_ID
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
        Test that retired tester context names are not defined.
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

    # * method: test_run_rejects_target_on_specialized_type
    def test_run_rejects_target_on_specialized_type(self) -> None:
        '''
        Test run(target=...) raises when the bound tester is not generic.
        '''

        # Run with an explicit target on a specialized tester.
        test_ctx = tester_contexts.DomainTesterContext.from_domain(error_message_tester())
        session = TEST_SESSION_CONTEXT(tester_ctx=test_ctx)

        # Assert a live target is rejected off the generic type.
        with pytest.raises(ValueError) as caught:
            session.run(target=object())
        assert str(caught.value) == (
            'run(target=...) is only valid when tester type is generic.'
        )

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

# ** tester: TestRepoTesterContext
class TestRepoTesterContext:
    '''
    Tests for RepoTesterContext registry, no-ops, and import law.
    '''

    # * method: test_omits_domain_type
    def test_omits_domain_type(self) -> None:
        '''
        Test that RepoTesterContext omits domain_type from its own namespace.
        '''

        # Assert the variant does not re-register TesterObject.
        assert 'domain_type' not in tester_contexts.RepoTesterContext.__dict__

    # * method: test_for_domain_remains_tester_context
    def test_for_domain_remains_tester_context(self) -> None:
        '''
        Test that BaseContext.for_domain(TesterObject) remains TesterContext.
        '''

        # Assert the master registry mapping is unchanged.
        assert BaseContext.for_domain(TESTER_OBJECT) is TESTER_CONTEXT

    # * method: test_from_domain_binds_subclass
    def test_from_domain_binds_subclass(self) -> None:
        '''
        Test that RepoTesterContext.from_domain binds that subclass.
        '''

        # Bind a repo tester through the variant and the registry.
        tester = repo_tester()
        bound = tester_contexts.RepoTesterContext.from_domain(tester)
        master = BaseContext.from_domain(tester)

        # Assert the variant binds while the registry stays on the master.
        assert isinstance(bound, tester_contexts.RepoTesterContext)
        assert bound.domain is tester
        assert type(master) is TESTER_CONTEXT

    # * method: test_empty_case_lists_are_no_ops
    def test_empty_case_lists_are_no_ops(self) -> None:
        '''
        Test that empty repo case lists and unset aggregate_class_name are no-ops.
        '''

        # Bind a repo tester with empty optional fields.
        ctx = tester_contexts.RepoTesterContext.from_domain(repo_tester())
        ctx.assert_exists(None)
        ctx.assert_get(None)
        ctx.assert_list(None)
        ctx.assert_delete(None)
        ctx.assert_save(None)

    # * method: test_module_import_law
    def test_module_import_law(self) -> None:
        '''
        Test that tiferet/contexts/tester.py has no pytest or forbidden app imports.
        '''

        # Read the production module source.
        source = Path(tester_contexts.__file__).read_text()

        # Assert pytest and forbidden app packages are not imported.
        assert 'import pytest' not in source
        assert 'from ..repos' not in source
        assert 'from ..mappers' not in source
        assert 'from ..utils' not in source
        assert 'from ..interfaces' not in source
        assert 'from ..di' not in source
        assert 'from ..blueprints' not in source

# ** tester: TestContextTesterContext
class TestContextTesterContext:
    '''
    Tests for ContextTesterContext registry, no-ops, and assertions.
    '''

    # * method: test_omits_domain_type
    def test_omits_domain_type(self) -> None:
        '''
        Test that ContextTesterContext omits domain_type from its own namespace.
        '''

        # Assert the variant does not re-register TesterObject.
        assert 'domain_type' not in tester_contexts.ContextTesterContext.__dict__

    # * method: test_registry_mappings_unchanged
    def test_registry_mappings_unchanged(self) -> None:
        '''
        Test that TesterObject, Request, and AppSession registry mappings stay.
        '''

        # Assert master mappings and that BaseContext is not a registry value.
        assert BaseContext.for_domain(TESTER_OBJECT) is TESTER_CONTEXT
        assert BaseContext.for_domain(Request) is RequestContext
        assert BaseContext.for_domain(AppSession) is AppSessionContext
        assert BaseContext not in ContextMeta.registry.values()

    # * method: test_from_domain_binds_subclass
    def test_from_domain_binds_subclass(self) -> None:
        '''
        Test that ContextTesterContext.from_domain binds that subclass.
        '''

        # Bind a context tester through the variant and the registry.
        tester = context_tester()
        bound = tester_contexts.ContextTesterContext.from_domain(tester)
        master = BaseContext.from_domain(tester)

        # Assert the variant binds while the registry stays on the master.
        assert isinstance(bound, tester_contexts.ContextTesterContext)
        assert bound.domain is tester
        assert type(master) is TESTER_CONTEXT

    # * method: test_empty_case_lists_are_no_ops
    def test_empty_case_lists_are_no_ops(self) -> None:
        '''
        Test that empty from_domain / domain_type / for_domain case lists no-op.
        '''

        # Bind a context tester with empty optional case lists.
        ctx = tester_contexts.ContextTesterContext.from_domain(
            context_tester(
                from_domain_cases=[],
                domain_type_cases=[],
                for_domain_cases=[],
            )
        )
        ctx.assert_from_domain()
        ctx.assert_domain_type()
        ctx.assert_for_domain()

    # * method: test_declaring_request_context_cases
    def test_declaring_request_context_cases(self) -> None:
        '''
        Test catalog-row cases against RequestContext pass the three assertions.
        '''

        # Bind the RequestContext catalog tester and run the three asserts.
        ctx = tester_contexts.ContextTesterContext.from_domain(context_tester())
        ctx.assert_from_domain()
        ctx.assert_domain_type()
        ctx.assert_for_domain()

    # * method: test_omitting_cli_session_context_cases
    def test_omitting_cli_session_context_cases(self) -> None:
        '''
        Test an omitting case against CliSessionContext without hub kwargs.
        '''

        # Bind a tester targeting CliSessionContext, which omits domain_type.
        tester = TESTER_OBJECT(
            type='context',
            id='context.CliSessionContext',
            module_path=CliSessionContext.__module__,
            class_name='CliSessionContext',
            domain_module_path='tiferet.domain.app',
            domain_class_name='AppSession',
            domain_type_cases=[
                {
                    'declares': False,
                },
            ],
            for_domain_cases=[
                {
                    'domain_module_path': 'tiferet.domain.app',
                    'domain_class_name': 'AppSession',
                    'context_module_path': 'tiferet.contexts.app',
                    'context_class_name': 'AppSessionContext',
                },
                {
                    'domain_module_path': 'tiferet.domain.tester',
                    'domain_class_name': 'TesterObject',
                    'context_module_path': 'tiferet.contexts.tester',
                    'context_class_name': 'TesterContext',
                },
            ],
        )
        ctx = tester_contexts.ContextTesterContext.from_domain(tester)

        # Assert omission and registry mappings without hub from_domain kwargs.
        ctx.assert_domain_type()
        ctx.assert_for_domain()
        assert 'domain_type' not in CliSessionContext.__dict__

# *** tests

# ** test: generic_tester_context_omits_domain_type
def test_generic_tester_context_omits_domain_type() -> None:
    '''
    Test that GenericTesterContext omits domain_type from its own namespace.
    '''

    # Assert the variant does not re-register TesterObject.
    assert 'domain_type' not in tester_contexts.GenericTesterContext.__dict__

# ** test: for_domain_tester_object_remains_tester_context
def test_for_domain_tester_object_remains_tester_context() -> None:
    '''
    Test that BaseContext.for_domain(TesterObject) remains TesterContext.
    '''

    # Assert the master registry mapping is unchanged.
    assert BaseContext.for_domain(TESTER_OBJECT) is TESTER_CONTEXT

# ** test: for_domain_request_remains_request_context
def test_for_domain_request_remains_request_context() -> None:
    '''
    Test that BaseContext.for_domain(Request) remains RequestContext.
    '''

    # Assert the request registry mapping is unchanged.
    assert BaseContext.for_domain(Request) is RequestContext

# ** test: assert_contract_noop_on_concrete_class
def test_assert_contract_noop_on_concrete_class() -> None:
    '''
    Test that assert_contract returns without assertion on a concrete class or instance.
    '''

    # Bind a generic tester context and a concrete probe.
    class Probe:
        def __init__(self, value=0):
            self.value = value

    ctx = tester_contexts.GenericTesterContext.from_domain(generic_tester())

    # Assert no-op on the class and on an instance.
    ctx.assert_contract(Probe)
    ctx.assert_contract(Probe(value=1))

# ** test: assert_contract_noop_on_empty_abc
def test_assert_contract_noop_on_empty_abc() -> None:
    '''
    Test that missing or empty __abstractmethods__ returns without assertion.
    '''

    # Bind a generic tester context.
    ctx = tester_contexts.GenericTesterContext.from_domain(generic_tester())

    class EmptyABC:
        __abstractmethods__ = frozenset()

    class MissingAttr:
        pass

    # Assert no-op on empty and missing abstract-method sets.
    ctx.assert_contract(EmptyABC)
    ctx.assert_contract(MissingAttr)
    ctx.assert_contract(None)

# ** test: assert_contract_locks_error_service_abc
def test_assert_contract_locks_error_service_abc() -> None:
    '''
    Test that assert_contract returns for ErrorService abstract method names.
    '''

    # Import the ABC from this test file, never from the context module.
    from tiferet.interfaces import ErrorService

    # Bind a generic tester context and lock the ABC.
    ctx = tester_contexts.GenericTesterContext.from_domain(generic_tester())
    ctx.assert_contract(ErrorService)

# ** test: assert_contract_fails_when_abstract_name_missing
def test_assert_contract_fails_when_abstract_name_missing() -> None:
    '''
    Test that assert_contract raises when an abstract name is missing.
    '''

    # Bind a generic tester context.
    ctx = tester_contexts.GenericTesterContext.from_domain(generic_tester())

    class MissingAbstract:
        __abstractmethods__ = frozenset({'not_there'})

    # Assert the missing abstract name fails.
    with pytest.raises(AssertionError):
        ctx.assert_contract(MissingAbstract)

# ** test: generic_tester_context_has_no_fluent_verbs
def test_generic_tester_context_has_no_fluent_verbs() -> None:
    '''
    Test that given, invoke, verify, and run are not defined on GenericTesterContext.
    '''

    # Assert fluent session verbs are not on the generic variant.
    for name in ('given', 'invoke', 'verify', 'run'):
        assert name not in tester_contexts.GenericTesterContext.__dict__
        assert not hasattr(tester_contexts.GenericTesterContext, name)

# ** test: run_target_invokes_local_callable_with_given_state
def test_run_target_invokes_local_callable_with_given_state() -> None:
    '''
    Test that run(target=_add) invokes the callable with given-state kwargs.
    '''

    def _add(a, b):
        return a + b

    # Bind a generic session and overlay given-state.
    ctx = tester_contexts.GenericTesterContext.from_domain(generic_tester())
    session = TEST_SESSION_CONTEXT(tester_ctx=ctx)
    outcome = session.given(a=1, b=2).verify(3).run(target=_add)

    # Assert the callable received request data as kwargs.
    assert outcome == 3

# ** test: run_generic_does_not_call_feature_pipeline
def test_run_generic_does_not_call_feature_pipeline() -> None:
    '''
    Test that generic run does not call the feature pipeline.
    '''

    # Bind a generic session and install pipeline sentinels.
    ctx = tester_contexts.GenericTesterContext.from_domain(generic_tester())
    session = TEST_SESSION_CONTEXT(tester_ctx=ctx)
    calls = []

    def _record(name):
        def _hook(*args, **kwargs):
            calls.append(name)
        return _hook

    session.execute_feature = _record('execute_feature')
    session._dispatch_event = _record('_dispatch_event')
    session.build_logger = _record('build_logger')
    session.handle_error = _record('handle_error')

    def _probe():
        return 7

    # Run with an explicit target and via get_target.
    assert session.run(target=_probe) == 7
    assert session.run() == 7
    assert calls == []

# ** test: run_target_does_not_write_sample_data_or_domain
def test_run_target_does_not_write_sample_data_or_domain() -> None:
    '''
    Test that run(target=obj) leaves sample_data and the bound domain unchanged.
    '''

    # Bind a generic tester with sample_data.
    tester = generic_tester(sample_data={'value': 1})
    ctx = tester_contexts.GenericTesterContext.from_domain(tester)
    domain_ref = ctx.domain
    sample_id = id(tester.sample_data)
    before = dict(tester.sample_data)

    # Run with an explicit live object.
    TEST_SESSION_CONTEXT(tester_ctx=ctx).run(target=object())

    # Assert declaration-time state is unchanged.
    assert tester.sample_data == before
    assert id(tester.sample_data) == sample_id
    assert ctx.domain is domain_ref
    assert ctx.domain is tester

# ** test: run_raises_when_target_set_on_non_generic
def test_run_raises_when_target_set_on_non_generic() -> None:
    '''
    Test that run(target=...) raises ValueError when the tester type is not generic.
    '''

    # Bind a specialized domain tester.
    ctx = tester_contexts.DomainTesterContext.from_domain(error_message_tester())
    session = TEST_SESSION_CONTEXT(tester_ctx=ctx)

    # Assert the reserved target argument is rejected.
    with pytest.raises(ValueError) as caught:
        session.run(target=object())
    assert str(caught.value) == (
        'run(target=...) is only valid when tester type is generic.'
    )
