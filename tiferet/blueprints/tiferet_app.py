"""Tiferet App Blueprint — Default Built-in Application Interface"""

# *** imports

# ** core
from typing import Any

# ** app
from .. import assets as a
from ..contexts.app import AppSessionContext
from ..events import RaiseError
from . import core
from .tiferet_cli import _resolve_bootstrap_session

# *** blueprints

# ** blueprint: build_tiferet_app
def build_tiferet_app(
    interface_id: str = 'tiferet_app',
    **parameters: Any,
) -> AppSessionContext:
    '''
    Build the default built-in Tiferet application session context.

    Mirrors :func:`core.build_app` but resolves the built-in ``tiferet_app``
    session through the shared bootstrap resolver, seeding
    ``DEFAULT_TIFERET_APP_SESSION`` as the fallback so callers do not need to
    define a ``tiferet_app`` session entry in their configuration file. All
    framework defaults come from the cache seeded by ``core.build_cache``.

    :param interface_id: The session ID to load; defaults to
        ``'tiferet_app'``.
    :type interface_id: str
    :param parameters: Additional parameters forwarded to the app service
        constructor (e.g. ``app_config='config.yml'``).
    :type parameters: dict
    :return: The fully prepared application session context.
    :rtype: AppSessionContext
    '''

    # Build the shared cache (seeds errors, app service dependencies, constants).
    cache = core.build_cache()

    # Resolve the session via the shared bootstrap resolver, using the built-in
    # tiferet_app default session as the fallback.
    app_session = _resolve_bootstrap_session(
        interface_id,
        cache,
        default_interfaces=[a.cli_app.DEFAULT_TIFERET_APP_SESSION],
        **parameters,
    )

    # Compose the wired app session context via the core compose path.
    app_session_context = core.build_app_session_context(app_session, cache)

    # Verify that the composed context is a valid app session context.
    if not isinstance(app_session_context, AppSessionContext):
        RaiseError.execute(
            a.const.INVALID_APP_SESSION_TYPE_ID,
            f'App context for session is not valid: {interface_id}.',
            interface_id=interface_id,
        )

    # Return the validated app session context.
    return app_session_context
