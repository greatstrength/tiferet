"""Tiferet Tester Blueprint Tests"""

# *** imports

# ** core
import inspect

# ** app
from tiferet import a, use_tester
from tiferet.blueprints import tester as tester_blueprints
from tiferet.blueprints.tester import (
    build_cache,
    build_test_session,
    build_tester_context,
)
from tiferet.contexts.app import (
    APP_CONSTANT_CACHE_PREFIX,
    APP_SERVICE_CACHE_PREFIX,
)
from tiferet.contexts.error import ERROR_CACHE_PREFIX
from tiferet.contexts.request import RequestContext
from tiferet.contexts.tester import (
    ContextTesterContext,
    DomainEventTesterContext,
    GenericTesterContext,
    RepoTesterContext,
    ServiceEventTesterContext,
    TESTER_CACHE_PREFIX,
    TestSessionContext as _TestSessionContext,
)
from tiferet.domain import Request, TesterObject
from tiferet.domain.error import ErrorMessage

# *** tests

# ** test: tester_build_cache
def test_tester_build_cache_isolated_from_standard_app_catalogs():
    '''Test that the tester dialect seeds only tester-scoped catalog entries.'''

    # Build the tester-specific cache.
    cache = build_cache()

    # Verify tester defaults and only feature-dispatch machinery.
    assert set(cache.get_by_prefix(*TESTER_CACHE_PREFIX)) == set(
        a.tester.CORE_DEFAULT_TESTERS,
    )
    assert cache.get_by_prefix(*ERROR_CACHE_PREFIX) == {}
    assert set(cache.get_by_prefix(*APP_SERVICE_CACHE_PREFIX)) == {
        a.app.DI_SERVICE_ID,
        a.app.FEATURE_SERVICE_ID,
        a.app.GET_FEATURE_EVT_ID,
    }
    assert cache.get_by_prefix(*APP_CONSTANT_CACHE_PREFIX) == (
        {
            a.app.DI_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
            a.app.FEATURE_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
        }
    )

# ** test: build_test_session
def test_build_test_session_constructs_request_session() -> None:
    '''Test the thin session helper constructs a TestSessionContext.'''

    # Bind a domain tester and construct a session without the decorator.
    test_ctx = build_tester_context(
        TesterObject(
            type='domain',
            id='domain.ErrorMessage',
            module_path=ErrorMessage.__module__,
            class_name=ErrorMessage.__name__,
            sample_data={'lang': 'en_US', 'text': 'An error occurred.'},
        ),
    )
    session = build_test_session(test_ctx, data={'text': 'overlay'})

    # Verify the session is a request bound to the supplied master.
    assert isinstance(session, _TestSessionContext)
    assert session.tester_ctx is test_ctx
    assert session.data == {'text': 'overlay'}

# ** test: tester_build_app_is_not_a_hub
def test_tester_build_app_is_not_a_hub() -> None:
    '''Test tester build_app no longer composes a mini-App session hub.'''

    # Assert the retired mini-App surface is gone from the tester blueprint.
    assert not hasattr(tester_blueprints, 'build_app')
    assert not hasattr(tester_blueprints, 'build_test_session_context')
    assert not hasattr(tester_blueprints, 'build_test_request')
    assert not hasattr(tester_blueprints, 'test_case')
    assert not hasattr(tester_blueprints, 'TestRequestContext')
    assert not hasattr(tester_blueprints, 'resolve_tester')

    # Assert the remaining resolve path is not reintroduced on the session helper.
    source = inspect.getsource(tester_blueprints.build_test_session)
    assert 'get_app_session' not in source
    assert 'compose_session_context' not in source
    assert 'build_app_service_container' not in source
    assert 'build_service_resolver' not in source

# ** test: use_tester_is_exported
def test_use_tester_is_exported() -> None:
    '''Test use_tester remains the public tester decorator export.'''

    assert use_tester is tester_blueprints.use_tester

# ** test: use_tester_keeps_pytest_out_of_tiferet
def test_use_tester_keeps_pytest_out_of_tiferet() -> None:
    '''Test wrap-all does not import pytest or add a use_fixture decorator.'''

    source = inspect.getsource(tester_blueprints)
    assert 'import pytest' not in source
    assert 'pytest11' not in source
    assert not hasattr(tester_blueprints, 'use_fixture')

# ** test: build_tester_context_selects_event_variants
def test_build_tester_context_selects_event_variants() -> None:
    '''Test build_tester_context maps domain_event and service_event types.'''

    domain_event_ctx = build_tester_context(
        TesterObject(
            type='domain_event',
            id='domain_event.ListErrors',
            module_path='tiferet.events.error',
            class_name='ListErrors',
        ),
    )
    service_event_ctx = build_tester_context(
        TesterObject(
            type='service_event',
            id='service_event.GetError',
            module_path='tiferet.events.error',
            class_name='GetError',
            dependencies={
                'error_service': {
                    'module_path': 'tiferet.interfaces',
                    'class_name': 'ErrorService',
                },
            },
            sample_kwargs={'id': 'TEST_ERROR'},
            service_attr='error_service',
            not_found_error_code='ERROR_NOT_FOUND',
        ),
    )
    assert isinstance(domain_event_ctx, DomainEventTesterContext)
    assert isinstance(service_event_ctx, ServiceEventTesterContext)
    assert not isinstance(domain_event_ctx, ServiceEventTesterContext)

# ** test: build_tester_context_selects_generic_variant
def test_build_tester_context_selects_generic_variant() -> None:
    '''Test build_tester_context maps generic to GenericTesterContext.'''

    test_ctx = build_tester_context(
        TesterObject(
            type='generic',
            id='generic.ErrorMessage',
            module_path=ErrorMessage.__module__,
            class_name=ErrorMessage.__name__,
            sample_data={'lang': 'en_US', 'text': 'An error occurred.'},
        ),
    )
    assert isinstance(test_ctx, GenericTesterContext)

# ** test: build_tester_context_selects_repo_variant
def test_build_tester_context_selects_repo_variant() -> None:
    '''Test build_tester_context maps repo to RepoTesterContext.'''

    test_ctx = build_tester_context(
        TesterObject(
            type='repo',
            id='repo.ErrorConfigRepository',
            module_path='tiferet.repos.error',
            class_name='ErrorConfigRepository',
            config_parameter='error_config',
        ),
    )
    assert isinstance(test_ctx, RepoTesterContext)

# ** test: use_tester_injects_repo_test_ctx
@use_tester(
    type='repo',
    module_path='tiferet.repos.error',
    class_name='ErrorConfigRepository',
    config_parameter='error_config',
)
def test_use_tester_injects_repo_test_ctx(test_ctx) -> None:
    '''Test @use_tester injects RepoTesterContext as test_ctx.'''

    assert isinstance(test_ctx, RepoTesterContext)

# ** test: use_tester_injects_generic_test_ctx
@use_tester(
    type='generic',
    target_cls=ErrorMessage,
    sample_data={'lang': 'en_US', 'text': 'An error occurred.'},
)
def test_use_tester_injects_generic_test_ctx(test_ctx) -> None:
    '''Test @use_tester injects GenericTesterContext as test_ctx.'''

    assert isinstance(test_ctx, GenericTesterContext)

# *** testers

# ** tester: context_tester_blueprint_tester
class ContextTesterBlueprintTester:
    '''Prove build_tester_context and @use_tester map type=context.'''

    # * test: build_tester_context_selects_context_variant
    def test_build_tester_context_selects_context_variant(self) -> None:
        '''build_tester_context maps context to ContextTesterContext.'''

        test_ctx = build_tester_context(
            TesterObject(
                type='context',
                id='context.RequestContext',
                module_path=RequestContext.__module__,
                class_name=RequestContext.__name__,
                domain_module_path=Request.__module__,
                domain_class_name=Request.__name__,
            ),
        )
        assert isinstance(test_ctx, ContextTesterContext)

    # * test: use_tester_injects_context_test_ctx
    @use_tester(
        type='context',
        target_cls=RequestContext,
        domain_cls=Request,
        sample_data={
            'session_id': 'test-session',
            'feature_id': 'test.feature',
        },
    )
    def test_use_tester_injects_context_test_ctx(self, test_ctx) -> None:
        '''@use_tester injects ContextTesterContext and fills domain identity.'''

        assert isinstance(test_ctx, ContextTesterContext)
        assert test_ctx.domain.domain_module_path == Request.__module__
        assert test_ctx.domain.domain_class_name == Request.__name__
