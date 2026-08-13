"""Tiferet Admin Blueprints Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet import assets as a
from tiferet.assets import TiferetError
from tiferet.blueprints.admin import (
    AdminApp,
    build_admin_app,
    build_admin_app_session_context,
    build_admin_service_resolver,
    build_cache,
)
from tiferet.blueprints import core
from tiferet.contexts.app import (
    ADMIN_SERVICE_CACHE_PREFIX,
    AppSessionContext,
)
from tiferet.contexts.cache import CacheContext
from tiferet.di import DIAppServiceContainer, DIDynamicServiceResolver
from tiferet.domain import AppServiceDependency, AppSession

# *** tests

# ** test: build_cache_seeds_admin_services
def test_build_cache_seeds_admin_services():
    '''
    Test that build_cache seeds admin services under ADMIN_SERVICE_CACHE_PREFIX.
    '''

    # Build the admin cache and resolve a known admin service entry.
    cache = build_cache()
    cached = cache.get('di_service', *ADMIN_SERVICE_CACHE_PREFIX)

    # Assert the admin service catalog is seeded under the admin prefix.
    assert isinstance(cached, AppServiceDependency)
    assert cached.service_id == 'di_service'

# ** test: build_admin_service_resolver_routes_by_flag
def test_build_admin_service_resolver_routes_by_flag():
    '''
    Test that the app flag resolves from the app container while admin and
    empty-flag resolution both use the admin container.
    '''

    # Seed an admin cache and build distinct app and admin containers.
    cache = build_cache()
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
    admin_probe = AppServiceDependency(
        service_id='flag_probe',
        module_path='tiferet.contexts.cache',
        class_name='CacheContext',
    )
    with mock.patch(
        'tiferet.blueprints.admin.get_default_admin_services',
        return_value=[admin_probe],
    ), mock.patch(
        'tiferet.blueprints.admin.get_default_admin_constants',
        return_value={},
    ):
        resolver = build_admin_service_resolver(app_container, cache)

    # Assert flag routing: app vs admin vs empty-flag default.
    assert isinstance(resolver, DIDynamicServiceResolver)
    from tiferet.contexts.request import RequestContext
    assert isinstance(resolver.get_dependency('flag_probe', 'app'), RequestContext)
    assert isinstance(resolver.get_dependency('flag_probe', 'admin'), CacheContext)
    assert isinstance(resolver.get_dependency('flag_probe'), CacheContext)
    assert resolver.get_container('admin') is resolver.get_container()

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
    assert context._create_request is core.create_session_request

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
    assert context._create_request is core.create_session_request
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
