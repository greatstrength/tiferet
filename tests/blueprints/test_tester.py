"""Tiferet Tester Blueprint Tests"""

# *** imports

# ** infra
import yaml

# ** app
from tiferet import Tester as RootTester, a, test_case as create_test_case
from tiferet.blueprints.tester import (
    build_app,
    build_cache,
    build_test_request,
    build_tester_context,
    resolve_tester,
)
from tiferet.contexts.app import (
    APP_CONSTANT_CACHE_PREFIX,
    APP_SERVICE_CACHE_PREFIX,
)
from tiferet.contexts.error import ERROR_CACHE_PREFIX
from tiferet.contexts.feature import FEATURE_CACHE_PREFIX, Feature
from tiferet.contexts.tester import (
    DomainEventTesterContext,
    ServiceEventTesterContext,
    TestRequestContext as _TestRequestContext,
    TestSessionContext as _TestSessionContext,
    TESTER_CACHE_PREFIX,
)
from tiferet.domain import TesterObject

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

# ** test: resolve_tester
def test_resolve_tester_returns_seeded_default_domain_object():
    '''Test direct resolution from the tester cache catalog.'''

    # Resolve a default tester through the non-root blueprint function.
    tester = resolve_tester('aggregate.ErrorAggregate')

    # Assert the cache-hit object is the seeded domain variant.
    assert isinstance(tester, TesterObject)
    assert tester.id == 'aggregate.ErrorAggregate'

# ** test: resolve_tester_with_config
def test_resolve_tester_uses_tester_session_service(tmp_path) -> None:
    '''Test custom configuration resolves through the tester app service.

    :param tmp_path: Pytest temporary path fixture.
    :type tmp_path: object
    '''

    # Write a non-default tester definition to a temporary configuration file.
    config_file = tmp_path / 'testers.yml'
    with open(config_file, 'w', encoding='utf-8') as config_stream:
        yaml.safe_dump(
            {
                'testers': {
                    'domain.Custom': {
                        'type': 'domain',
                        'module_path': 'tiferet.domain.error',
                        'class_name': 'ErrorMessage',
                        'sample_data': {},
                    },
                },
            },
            config_stream,
        )

    # Resolve the tester through the default service declared on the session.
    tester = resolve_tester('domain.Custom', tester_config=str(config_file))
    assert tester.id == 'domain.Custom'

# ** test: build_test_request
def test_build_test_request_creates_specialized_context() -> None:
    '''Test that the fluent tester handler creates a TestRequestContext.'''

    # Build the request through the tester-specific handler.
    request = build_test_request('tester', 'test.feature', data={'value': 1})

    # Verify its specialized type and stamped request fields.
    assert isinstance(request, _TestRequestContext)
    assert request.headers['interface_id'] == 'tester'
    assert request.feature_id == 'test.feature'
    assert request.data == {'value': 1}

# ** test: build_app
def test_build_app_returns_default_test_session_context() -> None:
    '''Test that the zero-argument Tester composition is ready to use.'''

    # Build the default cache-seeded tester session.
    context = build_app()

    # Verify the fluent test-session context is composed.
    assert isinstance(context, _TestSessionContext)
    assert context.domain.id == a.tester.TIFERET_TESTER_ID
    assert RootTester is build_app

# ** test: build_app_feature_dispatch
def test_build_app_dispatches_cached_feature_without_external_config() -> None:
    '''Test the default Tester dispatches a cached feature without config I/O.'''

    # Compose the default tester and seed an empty executable feature.
    context = build_app()
    feature = Feature(
        id='test.empty',
        name='Empty Test Feature',
    )
    context.cache.set(feature.id, feature, *FEATURE_CACHE_PREFIX)

    # Dispatch through the inherited feature handler without loading config.yml.
    assert context.given(value=1).invoke(feature_id=feature.id).verify(None).run() is None

# ** test: test_case
def test_test_case_seeds_given_state_without_dispatching(monkeypatch) -> None:
    '''Test that test_case constructs Tester() and supplies given-state.'''

    # Define a minimal context spy that records baseline state.
    class TesterContext:
        def __init__(self):
            self.given_state = None

        def given(self, **data):
            self.given_state = data
            return self

    # Replace Tester construction so the decorator behavior is isolated.
    context = TesterContext()
    monkeypatch.setattr(
        'tiferet.blueprints.tester.build_app',
        lambda interface_id=None: context,
    )

    # Decorate a test-shaped callable that returns its context unchanged.
    @create_test_case(value=1)
    def target(tester_ctx):
        return tester_ctx

    # Assert the wrapper constructs the session and does not require a fixture.
    assert target() is context
    assert context.given_state == {'value': 1}

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
