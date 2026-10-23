"""Tiferet Admin Blueprints Tests"""

# *** imports

# ** infra
import pytest
import yaml
from unittest import mock

# ** app
from tiferet import assets as a
from tiferet.assets import TiferetError
from tiferet.blueprints.admin import (
    AdminApp,
    build_admin_app,
    build_admin_app_session_context,
    build_admin_service_resolver,
    build_admin_session_constants,
    build_cache,
)
from tiferet.blueprints import core
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.cache import CacheContext
from tiferet.di import DIAppServiceContainer, DIDynamicServiceResolver
from tiferet.domain import AppServiceDependency, AppSession
from tiferet.mappers import FeatureAggregate

# *** tests

# ** test: build_cache_seeds_admin_services
def test_build_cache_seeds_admin_services():
    '''
    Test that build_cache seeds admin services under ADMIN_SERVICE_CACHE_PREFIX.
    '''

    # Build the admin cache and resolve a known admin service entry.
    cache = build_cache()
    cached = cache.get('di_service', *a.app.ADMIN_SERVICE_CACHE_PREFIX)

    # Assert the admin service catalog is seeded under the admin prefix.
    assert isinstance(cached, AppServiceDependency)
    assert cached.service_id == 'di_service'

# ** test: build_admin_service_resolver_routes_by_flag
def test_build_admin_service_resolver_routes_by_flag():
    '''
    Test that the app flag resolves from the app container while admin and
    empty-flag resolution both use the admin container.
    '''

    # Build a distinct app container with a flag_probe entry.
    app_container = DIAppServiceContainer.from_dependencies(
        services=[
            AppServiceDependency(
                service_id='di_service',
                module_path='tiferet.contexts.cache',
                class_name='CacheContext',
            ),
            AppServiceDependency(
                service_id='flag_probe',
                module_path='tiferet.contexts.request',
                class_name='RequestContext',
            ),
        ],
        constants={},
    )

    # Seed a bare cache whose admin-service prefix holds only a probe entry.
    admin_probe = AppServiceDependency(
        service_id='flag_probe',
        module_path='tiferet.contexts.cache',
        class_name='CacheContext',
    )
    cache = CacheContext()
    cache.set('flag_probe', admin_probe, *a.app.ADMIN_SERVICE_CACHE_PREFIX)

    # Build the resolver against the app container and probe-seeded cache.
    resolver = build_admin_service_resolver(app_container, cache)

    # Assert flag routing: app vs admin vs empty-flag default.
    assert isinstance(resolver, DIDynamicServiceResolver)
    from tiferet.contexts.request import RequestContext
    assert isinstance(resolver.get_dependency('flag_probe', 'app'), RequestContext)
    assert isinstance(resolver.get_dependency('flag_probe', 'admin'), CacheContext)
    assert isinstance(resolver.get_dependency('flag_probe'), CacheContext)
    assert resolver.get_container('admin') is resolver.get_container()

# ** test: build_admin_session_constants_overlays_config_paths
def test_build_admin_session_constants_overlays_config_paths():
    '''
    Test that build_admin_session_constants keeps existing entries, sets all six
    config-file keys to app_config, and does not mutate its input.
    '''

    # Overlay a constants dict holding a stale config path and an unrelated key.
    constants = {'cli_config': 'old.yml', 'keep': 'x'}
    result = build_admin_session_constants(constants, 'other.yml')

    # Assert the unrelated key is kept and every config-file key is overlaid.
    assert result['keep'] == 'x'
    for key in ('app_config', 'cli_config', 'di_config', 'error_config', 'feature_config', 'logging_config'):
        assert result[key] == 'other.yml'

    # Assert the input dict is unchanged.
    assert constants == {'cli_config': 'old.yml', 'keep': 'x'}

    # Assert a None input yields exactly the six config-file keys.
    assert build_admin_session_constants(None, 'other.yml') == {
        'app_config': 'other.yml',
        'cli_config': 'other.yml',
        'di_config': 'other.yml',
        'error_config': 'other.yml',
        'feature_config': 'other.yml',
        'logging_config': 'other.yml',
    }

# ** test: build_admin_service_resolver_overlays_session_constants
def test_build_admin_service_resolver_overlays_session_constants(tmp_path, monkeypatch):
    '''
    Test that session constants override the admin container defaults on both
    the empty-flag default and the 'admin' flag.

    :param tmp_path: A temporary working directory.
    :type tmp_path: pathlib.Path
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Work in a directory holding both config files.
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'config.yml').write_text('features: {}\n')
    (tmp_path / 'other.yml').write_text('features: {}\n')

    # Build the resolver with a feature_config session constant.
    cache = build_cache()
    app_container = core.build_app_service_container(cache, None)
    resolver = build_admin_service_resolver(
        app_container,
        cache,
        session_constants={'feature_config': 'other.yml'},
    )

    # Assert both admin registrations resolve the overlaid config path.
    assert resolver.get_dependency('feature_service').config_file == 'other.yml'
    assert resolver.get_dependency('feature_service', 'admin').config_file == 'other.yml'

    # Assert a resolver built without session constants keeps the admin default.
    default_resolver = build_admin_service_resolver(app_container, cache)
    assert default_resolver.get_dependency('feature_service').config_file == 'config.yml'

# ** test: build_admin_app_reseeds_app_config
def test_build_admin_app_reseeds_app_config(tmp_path, monkeypatch):
    '''
    Test that build_admin_app re-seeds app_config onto both the default admin
    container and the 'app' container.

    :param tmp_path: A temporary working directory.
    :type tmp_path: pathlib.Path
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Work in a directory holding both config files.
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'config.yml').write_text('features: {}\n')
    (tmp_path / 'other.yml').write_text('features: {}\n')

    # Build the admin app against the supplied config file.
    context = build_admin_app(app_config='other.yml')

    # Assert both containers resolve the feature service against other.yml.
    assert context.get_dependency('feature_service').config_file == 'other.yml'
    assert context.get_dependency('feature_service', 'app').config_file == 'other.yml'

# ** test: build_admin_app_writes_to_supplied_config
def test_build_admin_app_writes_to_supplied_config(tmp_path, monkeypatch):
    '''
    Test that a feature write through build_admin_app lands in the supplied
    config file and leaves ./config.yml unchanged.

    :param tmp_path: A temporary working directory.
    :type tmp_path: pathlib.Path
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Work in a directory holding both config files.
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'config.yml').write_text('features: {}\n')
    (tmp_path / 'other.yml').write_text('features: {}\n')

    # Save a feature through the admin app built against other.yml.
    context = build_admin_app(app_config='other.yml')
    context.get_dependency('feature_service').save(FeatureAggregate(
        id='demo.demo',
        name='Demo',
        group_id='demo',
        feature_key='demo',
        description='Demo',
    ))

    # Assert the feature landed in other.yml and config.yml is byte-for-byte unchanged.
    written = yaml.safe_load((tmp_path / 'other.yml').read_text())
    assert 'demo' in written['features']['demo']
    assert (tmp_path / 'config.yml').read_bytes() == b'features: {}\n'

# ** test: build_admin_app_session_context_wires_handlers
def test_build_admin_app_session_context_wires_handlers():
    '''
    Test that build_admin_app_session_context returns an AppSessionContext with
    all five handlers wired, including build_logger_handler.
    '''

    # Seed the admin cache and a minimal session for composition.
    cache = build_cache()
    app_session = AppSession(id=a.app.TIFERET_ADMIN_ID, name='Admin App')

    # Bypass the real logging pipeline; this test targets handler wiring only.
    fake_build_logger = mock.Mock(name='build_logger_handler')
    with mock.patch(
        'tiferet.blueprints.core.build_logger_handler',
        return_value=fake_build_logger,
    ):
        context = build_admin_app_session_context(app_session, cache)

    # Assert the context is fully wired with all five template-method handlers.
    assert isinstance(context, AppSessionContext)
    assert context._build_logger is fake_build_logger
    assert context._execute_feature is not None
    assert context._raise_error is not None
    assert context._build_response is core.response_handler
    assert context._create_request is core.create_request_context

# ** test: build_admin_app_returns_app_session_context
def test_build_admin_app_returns_app_session_context():
    '''
    Test that build_admin_app returns a fully wired AppSessionContext for the
    built-in admin session.
    '''

    # Build the admin app with no consumer config entry required.
    context = build_admin_app()

    # Assert the composed context is bound to the built-in admin session.
    assert isinstance(context, AppSessionContext)
    assert context.domain.id == a.app.TIFERET_ADMIN_ID

    # Assert all five template-method handlers were wired.
    assert context._build_logger is not None
    assert context._execute_feature is not None
    assert context._raise_error is not None
    assert context._create_request is core.create_request_context
    assert context._build_response is core.response_handler

# ** test: build_admin_app_alias
def test_build_admin_app_alias():
    '''
    Test that AdminApp is an alias for build_admin_app.
    '''

    # Assert the exported alias points at the single-call entry point.
    assert AdminApp is build_admin_app

# ** test: build_admin_app_invalid_type
def test_build_admin_app_invalid_type():
    '''
    Test that build_admin_app raises INVALID_APP_SESSION_TYPE_ID when the
    resolved context type is invalid.
    '''

    # Isolate build_admin_app and force an invalid context type.
    with mock.patch('tiferet.blueprints.admin.build_cache') as mock_cache, \
         mock.patch('tiferet.blueprints.core.get_app_session') as mock_get_session, \
         mock.patch('tiferet.blueprints.admin.build_admin_app_session_context') as mock_build_ctx:
        mock_cache.return_value = CacheContext()
        mock_get_session.return_value = AppSession(id='admin', name='Admin App')
        mock_build_ctx.return_value = object()

        # Invoke build_admin_app and expect the structured type error.
        with pytest.raises(TiferetError) as exc_info:
            build_admin_app()

    # Assert the structured invalid-type error is raised.
    assert exc_info.value.error_code == a.error.INVALID_APP_SESSION_TYPE_ID
