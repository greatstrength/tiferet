"""Tiferet Version and Global Exports"""

# *** exports

# ** app
# Export the main application context and related modules.
# Use a try-except block to avoid import errors on build systems.
try:
    from .assets import TiferetError, TiferetAPIError
    from .contexts import AppManagerContext as App
    from .domain import (
        DomainObject,
        StringType,
        IntegerType,
        BooleanType,
        FloatType,
        ListType,
        DictType,
        ModelType,
    )
    from .events import (
        DomainEvent,
        ParseParameter,
    )
    from .interfaces import Service
    from .mappers import (
        Aggregate,
        TransferObject,
    )
    from .utils import (
        FileLoader,
        FileLoader as File,
        YamlLoader,
        YamlLoader as Yaml,
        JsonLoader,
        JsonLoader as Json,
        CsvLoader,
        CsvLoader as Csv,
        CsvDictLoader,
        CsvDictLoader as CsvDict,
        SqliteClient,
        SqliteClient as Sqlite,
    )
except Exception as e:
    import os, sys
    # Only print warning if TIFERET_SILENT_IMPORTS is not set to a truthy value
    if not os.getenv('TIFERET_SILENT_IMPORTS'):
        print(f"Warning: Failed to import Tiferet core modules: {e}", file=sys.stderr)
    pass

# *** version

__version__ = '2.0.0a5'
