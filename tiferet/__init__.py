"""Tiferet Version and Global Exports"""

# *** exports

# ** app
# Export the main application context and related modules.
# Use a try-except block to avoid import errors on build systems.
try:
    from .assets import TiferetError, TiferetAPIError
    from .contexts import AppManagerContext as App
    from .models import (
        ModelObject,
        StringType,
        IntegerType,
        BooleanType,
        FloatType,
        ListType,
        DictType,
        ModelType,
    )
    from .commands import *
    from .commands import (
        Command,
        ParseParameter
    )
    from .contracts import (
        ModelContract,
        Repository
    )
    from .data import DataObject
    from .proxies import (
        YamlFileProxy,
        JsonFileProxy,
        CsvFileProxy
    )
    from .middleware import (
        File,
        FileLoaderMiddleware,
        Yaml,
        YamlLoaderMiddleware,
        Json,
        JsonLoaderMiddleware,
        Csv,
        CsvLoaderMiddleware,
        CsvDict,
        CsvDictLoaderMiddleware
    )
except Exception as e:
    print(f"Warning: Failed to import Tiferet core modules: {e}")
    pass

# *** version

__version__ = '1.7.0'
