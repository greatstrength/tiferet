"""Tiferet Blueprint Exports"""

# *** exports

__all__ = [
    'build_app',
    'App',
    'build_cli',
    'CLI',
    'build_admin_app',
    'AdminApp',
    'build_admin_cli',
    'AdminCLI',
    'build_tiferet_app',
    'TiferetApp',
    'build_tiferet_cli',
    'TiferetCLI',
]

# ** app
from .core import build_app, build_app as App
from .cli import build_app as build_cli, build_app as CLI
from .admin import build_admin_app, build_admin_app as AdminApp
from .admin_cli import build_admin_cli, build_admin_cli as AdminCLI
from .admin import build_tiferet_app, build_tiferet_app as TiferetApp
from .admin_cli import build_tiferet_cli, build_tiferet_cli as TiferetCLI
