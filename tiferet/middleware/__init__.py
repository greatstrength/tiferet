"""
Tiferet Middleware Exports

.. deprecated::
    The ``tiferet.middleware`` package is deprecated and will be removed in a
    future release.  Use the ``tiferet.utils`` package instead, which provides
    the same file-I/O utilities under their canonical names (``FileLoader``,
    ``YamlLoader``, ``JsonLoader``, ``CsvLoader``, ``CsvDictLoader``,
    ``SqliteClient``).
"""

# *** exports

# ** app
from ..commands import TiferetError, const
from .file import FileLoaderMiddleware, FileLoaderMiddleware as File
from .yaml import YamlLoaderMiddleware, YamlLoaderMiddleware as Yaml
from .json import JsonLoaderMiddleware, JsonLoaderMiddleware as Json
from .csv import (
    CsvLoaderMiddleware, 
    CsvLoaderMiddleware as Csv,
    CsvDictLoaderMiddleware,
    CsvDictLoaderMiddleware as CsvDict
)
from .sqlite import SqliteMiddleware, SqliteMiddleware as Sqlite