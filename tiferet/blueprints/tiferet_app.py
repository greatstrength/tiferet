"""Tiferet App Blueprint — Default Built-in Application Interface"""

# *** imports

# ** core
from typing import Any

# ** app
from ..contexts.app import AppInterfaceContext
from .. import assets as a
from .main import build_app

# *** blueprints

# ** blueprint: build_tiferet_app
def build_tiferet_app(
    interface_id: str = 'tiferet_app',
    **parameters: Any,
) -> AppInterfaceContext:
    '''
    Build the default built-in Tiferet application interface context.

    Behaves identically to :func:`build_app` but seeds
    ``DEFAULT_TIFERET_APP_INTERFACE`` as the interface fallback, so
    callers do not need to define a ``tiferet_app`` interface entry in
    their configuration file.

    :param interface_id: The interface ID to load; defaults to
        ``'tiferet_app'``.
    :type interface_id: str
    :param parameters: Additional parameters forwarded to the app service
        constructor (e.g. ``app_config='config.yml'``).
    :type parameters: dict
    :return: The fully prepared application interface context.
    :rtype: AppInterfaceContext
    '''

    # Delegate to build_app, providing the bootstrapped interface as a default.
    return build_app(
        interface_id,
        default_interfaces=[a.cli_app.DEFAULT_TIFERET_APP_INTERFACE],
        **parameters,
    )
