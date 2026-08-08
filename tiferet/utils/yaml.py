"""Tiferet Utils Yaml"""

# *** imports

# ** core
from pathlib import Path
from typing import Any, Callable, Optional

import yaml

# ** app
from .file import FileLoader, INVALID_FILE_ID
from ..interfaces.core import ServiceError

# *** constants

# ** constant: yaml_file_not_found_id
YAML_FILE_NOT_FOUND_ID = 'YAML_FILE_NOT_FOUND'

# ** constant: yaml_file_load_error_id
YAML_FILE_LOAD_ERROR_ID = 'YAML_FILE_LOAD_ERROR'

# ** constant: yaml_file_save_error_id
YAML_FILE_SAVE_ERROR_ID = 'YAML_FILE_SAVE_ERROR'

# *** utils

# ** util: yaml_loader
class YamlLoader(FileLoader):
    '''
    Utility for loading and saving YAML files with structured error handling.
    Extends FileLoader for stream lifecycle management.
    '''

    # * init
    def __init__(self,
            path: str | Path,
            mode: str = 'r',
            encoding: str = 'utf-8',
            **kwargs,
        ):
        '''
        Initialize YamlLoader.

        :param path: Path to the YAML file.
        :type path: str | Path
        :param mode: File open mode (typically 'r' or 'w').
        :type mode: str
        :param encoding: Text encoding (defaults to utf-8).
        :type encoding: str
        :param kwargs: Additional parameters passed to parent.
        :type kwargs: dict
        '''

        # Initialize the parent FileLoader.
        super().__init__(path=path, mode=mode, encoding=encoding, **kwargs)

    # * method: verify_yaml_file (static)
    @staticmethod
    def verify_yaml_file(loader: 'YamlLoader', default_path: Optional[Path] = None):
        '''
        Verify the file has a YAML extension and exists (with optional fallback).

        :param loader: YamlLoader instance to verify.
        :type loader: YamlLoader
        :param default_path: Optional fallback path if primary path is invalid.
        :type default_path: Optional[Path]
        :raises ServiceError: If the extension is not a YAML extension or the
            resolved path does not exist.
        '''

        # Start with the loader's path.
        path = loader.path

        # Check if the path has a valid YAML extension; fall back or raise error.
        if not path.suffix.lower() in {'.yaml', '.yml'}:
            if default_path and default_path.suffix.lower() in {'.yaml', '.yml'}:
                path = default_path
            else:
                ServiceError.raise_for(
                    loader,
                    INVALID_FILE_ID,
                    'File must have .yaml or .yml extension.',
                    path=str(loader.path),
                )

        # Verify the resolved path exists.
        if not path.exists():
            ServiceError.raise_for(
                loader,
                YAML_FILE_NOT_FOUND_ID,
                f'The specified YAML file could not be found at {path}.',
                path=str(path),
            )

    # * method: load
    def load(self,
            start_node: Callable[[Any], Any] = lambda x: x,
            data_factory: Callable[[Any], Any] = lambda x: x,
            **kwargs,
        ) -> Any:
        '''
        Load YAML content, apply optional transformations, and return result.

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

            # Open the file stream via context manager, parse YAML, and apply transformations.
            with self:
                data = yaml.safe_load(self.file)

                # Treat empty YAML as an empty dict.
                if data is None:
                    data = {}

                # Apply the start_node transformation.
                transformed = start_node(data)

                # Apply the data_factory and return.
                return data_factory(transformed)

        except ServiceError:

            # Re-raise service errors from FileLoader (e.g., FILE_NOT_FOUND) so a
            # missing file is not relabelled a parse failure.
            raise

        except yaml.YAMLError as e:

            # Wrap YAML parsing errors as a service error.
            ServiceError.raise_for(
                self,
                YAML_FILE_LOAD_ERROR_ID,
                f'Failed to parse YAML file: {e}. Path: {self.path}.',
                cause=e,
                error=str(e),
                path=str(self.path),
            )

        except Exception as e:

            # Wrap all other exceptions as a service error.
            ServiceError.raise_for(
                self,
                YAML_FILE_LOAD_ERROR_ID,
                f'Failed to parse YAML file: {e}. Path: {self.path}.',
                cause=e,
                error=str(e),
                path=str(self.path),
            )

    # * method: save
    def save(self, data: Any, data_path: Optional[str] = None, **kwargs) -> None:
        '''
        Serialize data to YAML and write to file.

        :param data: Python object to serialize.
        :type data: Any
        :param data_path: Reserved for future partial updates (ignored for now).
        :type data_path: Optional[str]
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        :raises ServiceError: If the file cannot be serialized or written.
        '''

        try:

            # Serialize the data to a YAML string.
            content = yaml.safe_dump(
                data,
                sort_keys=False,
                allow_unicode=True,
                width=4096,
            )

            # Write the serialized YAML to the file stream.
            with self:
                self.file.write(content)

        except ServiceError:

            # Re-raise service errors from FileLoader (e.g., FILE_NOT_FOUND) so a
            # missing file is not relabelled a write failure.
            raise

        except Exception as e:

            # Wrap write errors as a service error.
            ServiceError.raise_for(
                self,
                YAML_FILE_SAVE_ERROR_ID,
                f'Failed to write YAML file: {e}. Path: {self.path}.',
                cause=e,
                error=str(e),
                path=str(self.path),
            )
