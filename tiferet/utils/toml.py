"""Tiferet Utils Toml"""

# *** imports

# ** core
from pathlib import Path
from typing import Any, Callable, Optional

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

# ** app
from .file import FileLoader
from ..interfaces.core import ServiceError

# *** constants

# ** constant: toml_file_not_found_id
TOML_FILE_NOT_FOUND_ID = 'TOML_FILE_NOT_FOUND'

# ** constant: toml_file_load_error_id
TOML_FILE_LOAD_ERROR_ID = 'TOML_FILE_LOAD_ERROR'

# ** constant: invalid_toml_file_id
INVALID_TOML_FILE_ID = 'INVALID_TOML_FILE'

# *** utils

# ** util: toml_loader
class TomlLoader(FileLoader):
    '''
    Utility for loading TOML files with structured error handling.
    Extends FileLoader for stream lifecycle management.

    TOML is a read-only format in this utility; writing is not supported
    because the ``tomllib`` / ``tomli`` library only provides parsing.
    '''

    # * init
    def __init__(self,
            path: str | Path,
            mode: str = 'rb',
            **kwargs,
        ):
        '''
        Initialize TomlLoader.

        :param path: Path to the TOML file.
        :type path: str | Path
        :param mode: File open mode (defaults to 'rb' for binary read as required by tomllib).
        :type mode: str
        :param kwargs: Additional parameters passed to parent.
        :type kwargs: dict
        '''

        # Initialize the parent FileLoader with binary mode (no encoding).
        super().__init__(path=path, mode=mode, encoding=None, **kwargs)

    # * method: verify_toml_file (static)
    @staticmethod
    def verify_toml_file(loader: 'TomlLoader', default_path: Optional[Path] = None):
        '''
        Verify the file has a TOML extension and exists (with optional fallback).

        :param loader: TomlLoader instance to verify.
        :type loader: TomlLoader
        :param default_path: Optional fallback path if primary path is invalid.
        :type default_path: Optional[Path]
        :raises ServiceError: If the extension is not a TOML extension or the
            resolved path does not exist.
        '''

        # Start with the loader's path.
        path = loader.path

        # Check if the path has a valid TOML extension; fall back or raise error.
        if path.suffix.lower() != '.toml':
            if default_path and default_path.suffix.lower() == '.toml':
                path = default_path
            else:
                ServiceError.raise_for(
                    loader,
                    INVALID_TOML_FILE_ID,
                    'File must have .toml extension.',
                    path=str(loader.path),
                )

        # Verify the resolved path exists.
        if not path.exists():
            ServiceError.raise_for(
                loader,
                TOML_FILE_NOT_FOUND_ID,
                f'The specified TOML file could not be found at {path}.',
                path=str(path),
            )

    # * method: load
    def load(self,
            start_node: Callable[[Any], Any] = lambda x: x,
            data_factory: Callable[[Any], Any] = lambda x: x,
            **kwargs,
        ) -> Any:
        '''
        Load TOML content, apply optional transformations, and return result.

        :param start_node: First transformation applied to raw data.
        :type start_node: Callable[[Any], Any]
        :param data_factory: Final factory applied to transformed data.
        :type data_factory: Callable[[Any], Any]
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        :return: Parsed and transformed Python object.
        :rtype: Any
        :raises ServiceError: If the file cannot be read or parsed.
        '''

        try:

            # Open the file stream via context manager, parse TOML, and apply transformations.
            with self:
                data = tomllib.load(self.file)

                # Apply the start_node transformation.
                transformed = start_node(data)

                # Apply the data_factory and return.
                return data_factory(transformed)

        except ServiceError:

            # Re-raise service errors from FileLoader (e.g., FILE_NOT_FOUND) so a
            # missing file is not relabelled a parse failure.
            raise

        except Exception as e:

            # Wrap TOML parsing errors as a service error.
            ServiceError.raise_for(
                self,
                TOML_FILE_LOAD_ERROR_ID,
                f'Failed to parse TOML file: {e}. Path: {self.path}.',
                cause=e,
                error=str(e),
                path=str(self.path),
            )
