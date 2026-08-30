"""Tiferet Version and Global Exports"""

# *** exports

__all__ = [
    'App',
    'CLI',
    'TiferetError',
    'TiferetAPIError',
    'DomainObject',
    'DomainEvent',
    'Service',
    'Aggregate',
    'TransferObject',
]

# ** app
# Root exports are limited to core runtime entrypoints and DDD vocabulary.
# Infrastructure (utils loaders/middleware) and secondary event/interface
# symbols are imported from their owning packages.
# Use a try-except block to avoid import errors on build systems.
try:
    from .assets import TiferetError, TiferetAPIError
    from .blueprints import build_app as App
    from .blueprints import build_cli as CLI
    from .domain import DomainObject
    from .events import DomainEvent
    from .interfaces import Service
    from .mappers import (
        Aggregate,
        TransferObject,
    )
except Exception as e:
    import os, sys
    # Only print warning if TIFERET_SILENT_IMPORTS is not set to a truthy value
    if not os.getenv('TIFERET_SILENT_IMPORTS'):
        print(f"Warning: Failed to import Tiferet core modules: {e}", file=sys.stderr)
    pass

# *** version

__version__ = '2.0.2'
