"""Tiferet App Blueprint Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet import assets as a
from tiferet import TiferetError
from tiferet.blueprints.app import (
    build_app_session_context,
    build_app,
)
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.app import AppSessionContext
from tiferet.domain import AppSession

# *** tests

# ** test: build_app_session_context_returns_app_session_context
def test_build_app_session_context_returns_app_session_context(monkeypatch):
    '''
    Test that build_app_session_context returns a fully wired AppSessionContext
    with the domain bound, the resolver handler, and a callable
    build_logger_handler wired.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Arrange a mock app container with no collaborators.
    app_container = mock.Mock()
    app_container.has_dependency.return_value = False
    app_container.get_dependency.return_value = mock.Mock()

    # Arrange a mock resolver.
    resolver = mock.Mock()

    # Patch build_app_service_container and build_service_resolver on the
    # shared core module (app.py calls them via `core.`).
    monkeypatch.setattr(
        'tiferet.blueprints.core.build_app_service_container',
        lambda *a, **kw: app_container,
    )
    monkeypatch.setattr(
        'tiferet.blueprints.core.build_service_resolver',
        lambda *a, **kw: resolver,
    )

    # Build a minimal app session.
    app_session = AppSession(
        id='test_app',
        name='Test App',
    )
    cache = CacheContext()

    # Build the session context.
    result = build_app_session_context(app_session, cache)

    # Assert the result is an AppSessionContext with domain, resolver, cache,
    # and a callable build_logger_handler wired — built lazily rather than
    # eagerly fetching the logging config at compose time.
    assert isinstance(result, AppSessionContext)
    assert result.domain is app_session
    assert result.get_dependency is resolver.get_dependency
    assert result.cache is cache
    assert callable(result._build_logger)


# ** test: build_app_session_context_wires_five_handlers
def test_build_app_session_context_wires_five_handlers(monkeypatch):
    '''
    Test that build_app_session_context wires all five template-method
    handler callables onto the resulting hub.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Arrange an app container with no additional collaborators.
    app_container = mock.Mock()
    app_container.has_dependency.return_value = False
    app_container.get_dependency.return_value = mock.Mock()

    # Patch the two builders on the shared core module.
    monkeypatch.setattr(
        'tiferet.blueprints.core.build_app_service_container',
        lambda *a, **kw: app_container,
    )
    monkeypatch.setattr(
        'tiferet.blueprints.core.build_service_resolver',
        lambda *a, **kw: mock.Mock(),
    )

    # Build the context.
    app_session = AppSession(
        id='test_app',
        name='Test App',
    )
    result = build_app_session_context(app_session, CacheContext())

    # Assert all five handler attributes are callable.
    assert callable(result._build_logger)
    assert callable(result._execute_feature)
    assert callable(result._create_request)
    assert callable(result._raise_error)
    assert callable(result._build_response)


# ** test: build_app_success
def test_build_app_success(monkeypatch):
    '''
    Test that build_app resolves the session via get_app_session and returns
    the AppSessionContext composed by build_app_session_context.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Arrange a resolved session and a spec'd context that passes validation.
    app_session = AppSession(
        id='test_calc',
        name='Test Calculator',
    )
    app_context = mock.Mock(spec=AppSessionContext)

    # Patch session resolution on the shared core module, and the local
    # build_app_session_context (called directly within app.py).
    get_session = mock.Mock(return_value=app_session)
    compose = mock.Mock(return_value=app_context)
    monkeypatch.setattr('tiferet.blueprints.core.get_app_session', get_session)
    monkeypatch.setattr('tiferet.blueprints.app.build_app_session_context', compose)

    # Build the app.
    result = build_app('test_calc', app_config='config.yml')

    # Assert the composed context is returned and the session was resolved by id.
    assert result is app_context
    assert get_session.call_args[0][0] == 'test_calc'
    compose.assert_called_once()


# ** test: build_app_invalid_context
def test_build_app_invalid_context(monkeypatch):
    '''
    Test that build_app raises INVALID_APP_SESSION_TYPE when the composed
    context is not an AppSessionContext.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Arrange a resolved session and an invalid (non-context) compose result.
    app_session = AppSession(
        id='invalid_interface',
        name='Invalid',
    )
    monkeypatch.setattr(
        'tiferet.blueprints.core.get_app_session',
        lambda *args, **kwargs: app_session,
    )
    monkeypatch.setattr(
        'tiferet.blueprints.app.build_app_session_context',
        lambda *args, **kwargs: object(),
    )

    # Assert an invalid composed context raises the expected error.
    with pytest.raises(TiferetError) as exc_info:
        build_app('invalid_interface', app_config='config.yml')

    # Assert the structured error code and interface id.
    assert exc_info.value.error_code == a.error.INVALID_APP_SESSION_TYPE_ID
    assert 'invalid_interface' in str(exc_info.value)


# ** test: build_app_missing_session_propagates_not_found
def test_build_app_missing_session_propagates_not_found(monkeypatch):
    '''
    Test that build_app propagates the GetAppSession APP_SESSION_NOT_FOUND
    error when the session is absent — the core path has no fallback.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    '''

    # Patch get_app_session to raise the not-found error the event would raise.
    def _raise(*args, **kwargs):
        raise TiferetError(a.error.APP_SESSION_NOT_FOUND_ID, interface_id='missing')

    monkeypatch.setattr('tiferet.blueprints.core.get_app_session', _raise)

    # Assert the not-found error propagates unhandled.
    with pytest.raises(TiferetError) as exc_info:
        build_app('missing', app_config='config.yml')

    # Assert the structured error code.
    assert exc_info.value.error_code == a.error.APP_SESSION_NOT_FOUND_ID


# ** test: app_alias_is_build_app
def test_app_alias_is_build_app():
    '''
    Test that the top-level App alias resolves to app.build_app.
    '''

    # Import the public App alias.
    from tiferet import App

    # Assert it is the app.py build_app entry point.
    assert App is build_app
