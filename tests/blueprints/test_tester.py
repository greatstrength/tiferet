"""Tiferet Tester Blueprint Tests"""

# *** imports

# ** core
import logging

# ** infra
import pytest
import yaml

# ** app
from tiferet import Tester as RootTester, a, test_case as create_test_case
from tiferet.assets import TiferetAPIError, TiferetError
from tiferet.blueprints.tester import (
    build_app,
    build_cache,
    build_test_request,
    resolve_tester,
)
from tiferet.contexts.app import (
    APP_CONSTANT_CACHE_PREFIX,
    APP_SERVICE_CACHE_PREFIX,
    APP_SESSION_CACHE_PREFIX,
)
from tiferet.contexts.error import ERROR_CACHE_PREFIX
from tiferet.contexts.feature import FEATURE_CACHE_PREFIX, Feature
from tiferet.contexts.logging import LOGGING_CACHE_PREFIX, LOGGER_CACHE_PREFIX
from tiferet.contexts.tester import (
    TestRequestContext as _TestRequestContext,
    TestSessionContext as _TestSessionContext,
    TESTER_CACHE_PREFIX,
)
from tiferet.domain import (
    LoggingSettings,
    ParameterSpecification,
    RequestSpecification,
    TesterObject,
)

# *** tests

# ** test: tester_build_cache
def test_tester_build_cache_isolated_from_standard_app_catalogs():
    '''Test that the tester dialect seeds logging/errors without app catalogs.'''

    # Build the tester-specific cache.
    cache = build_cache()

    # Verify tester defaults plus logging and error catalogs for feature dispatch.
    assert set(cache.get_by_prefix(*TESTER_CACHE_PREFIX)) == set(
        a.tester.CORE_DEFAULT_TESTERS,
    )
    assert set(cache.get_by_prefix(*ERROR_CACHE_PREFIX)) == set(
        a.error.CORE_DEFAULT_ERRORS,
    )
    assert isinstance(cache.get('default', *LOGGING_CACHE_PREFIX), LoggingSettings)
    assert set(cache.get_by_prefix(*APP_SERVICE_CACHE_PREFIX)) == {
        a.app.DI_SERVICE_ID,
        a.app.FEATURE_SERVICE_ID,
        a.app.GET_FEATURE_EVT_ID,
        a.app.LOGGING_SERVICE_ID,
        a.app.LOGGING_LIST_ALL_EVT_ID,
        a.app.ERROR_SERVICE_ID,
        a.app.GET_ERROR_EVT_ID,
    }
    assert cache.get_by_prefix(*APP_CONSTANT_CACHE_PREFIX) == (
        {
            a.app.DI_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
            a.app.FEATURE_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
            a.app.LOGGING_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
            a.app.ERROR_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
        }
    )
    assert set(cache.get_by_prefix(*APP_SESSION_CACHE_PREFIX)) == set(
        a.tester.CORE_DEFAULT_TESTER_SESSIONS,
    )
    assert a.app.TIFERET_ADMIN_ID not in cache.get_by_prefix(*APP_SESSION_CACHE_PREFIX)
    assert a.app.CLI_SERVICE_ID not in cache.get_by_prefix(*APP_SERVICE_CACHE_PREFIX)
    assert a.app.LOGGING_MIDDLEWARE_ID not in cache.get_by_prefix(*APP_SERVICE_CACHE_PREFIX)

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

    # Assert the feature path constructed and cached a logger.
    logger = context.cache.get(context.domain.logger_id, *LOGGER_CACHE_PREFIX)
    assert isinstance(logger, logging.Logger)

# ** test: build_app_feature_dispatch_api_error
def test_build_app_feature_dispatch_raises_tiferet_api_error() -> None:
    '''Test a catalogued feature-path TiferetError surfaces as TiferetAPIError.'''

    # Compose the default tester and seed a feature with a required request field.
    context = build_app()
    feature = Feature(
        id='test.invalid',
        name='Invalid Test Feature',
        params_schema=RequestSpecification(
            parameters=[
                ParameterSpecification(name='required_value', type='str'),
            ],
        ),
    )
    context.cache.set(feature.id, feature, *FEATURE_CACHE_PREFIX)

    # Dispatch without the required field and capture the formatted API error.
    with pytest.raises(TiferetAPIError) as exc_info:
        context.invoke(feature_id=feature.id).run()

    # Assert the catalogued code and that pending state was cleared.
    assert exc_info.value.error_code == a.error.REQUEST_VALIDATION_FAILED_ID
    assert context._pending_request is None

# ** test: build_app_event_dispatch_raw_error
def test_build_app_event_dispatch_raises_raw_tiferet_error() -> None:
    '''Test an invoke(event=...) TiferetError is not formatted as TiferetAPIError.'''

    # Compose the default tester and a direct event that raises a domain error.
    context = build_app()

    def raise_domain_error():
        TiferetError.raise_error(
            a.error.FEATURE_NOT_FOUND_ID,
            feature_id='missing',
        )

    # Dispatch the event and capture the unformatted domain error.
    with pytest.raises(TiferetError) as exc_info:
        context.invoke(event=raise_domain_error).run()

    # Assert the error remains a raw TiferetError.
    assert type(exc_info.value) is TiferetError
    assert exc_info.value.error_code == a.error.FEATURE_NOT_FOUND_ID

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
