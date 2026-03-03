"""Tiferet Utils Json"""

# *** imports

# ** core
from pathlib import Path
from typing import Any, Callable, Optional

import json

# ** app
from .file import FileLoader
from ..events import RaiseError, a
from ..events.settings import TiferetError

# *** utils

# ** util: json_loader
class JsonLoader(FileLoader):
    '''
    Utility for loading and saving JSON files with structured error handling.
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
        Initialize JsonLoader.

        :param path: Path to the JSON file.
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

    # * method: verify_json_file (static)
    @staticmethod
    def verify_json_file(loader: 'JsonLoader', default_path: Optional[Path] = None):
        '''
        Verify the file has a JSON extension and exists (with optional fallback).

        :param loader: JsonLoader instance to verify.
        :type loader: JsonLoader
        :param default_path: Optional fallback path if primary path is invalid.
        :type default_path: Optional[Path]
        '''

        # Start with the loader's path.
        path = loader.path

        # Check if the path has a valid JSON extension; fall back or raise error.
        if not path.suffix.lower() == '.json':
            if default_path and default_path.suffix.lower() == '.json':
                path = default_path
            else:
                RaiseError.execute(
                    error_code=a.const.INVALID_FILE_ID,
                    message="File must have .json extension",
                    path=str(loader.path),
                )

        # Verify the resolved path exists.
        if not path.exists():
            RaiseError.execute(
                error_code=a.const.JSON_FILE_NOT_FOUND_ID,
                path=str(path),
            )

    # * method: load
    def load(self,
            start_node: Callable[[Any], Any] = lambda x: x,
            data_factory: Callable[[Any], Any] = lambda x: x,
            **kwargs,
        ) -> Any:
        '''
        Load JSON content, apply optional transformations, and return result.

        :param start_node: First transformation applied to raw data.
        :type start_node: Callable[[Any], Any]
        :param data_factory: Final factory applied to transformed data.
        :type data_factory: Callable[[Any], Any]
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        :return: Parsed and transformed Python object.
        :rtype: Any
        '''

        try:

            # Open the file stream via context manager, parse JSON, and apply transformations.
            with self:
                data = json.load(self.file)

                # Apply the start_node transformation.
                transformed = start_node(data)

                # Apply the data_factory and return.
                return data_factory(transformed)

        except TiferetError:

            # Re-raise structured errors from FileLoader (e.g., FILE_NOT_FOUND).
            raise

        except json.JSONDecodeError as e:

            # Wrap JSON parsing errors as structured TiferetError.
            RaiseError.execute(
                error_code=a.const.JSON_FILE_LOAD_ERROR_ID,
                error=str(e),
                path=str(self.path),
            )

        except Exception as e:

            # Wrap all other exceptions as structured TiferetError.
            RaiseError.execute(
                error_code=a.const.JSON_FILE_LOAD_ERROR_ID,
                error=str(e),
                path=str(self.path),
            )

    # * method: save
    def save(self, data: Any, data_path: Optional[str] = None, **kwargs) -> None:
        '''
        Serialize data to JSON and write to file.

        :param data: Python object to serialize.
        :type data: Any
        :param data_path: Reserved for future partial updates (ignored for now).
        :type data_path: Optional[str]
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        '''

        try:

            # Serialize the data to a JSON string.
            content = json.dumps(
                data,
                indent=2,
                sort_keys=False,
                ensure_ascii=False,
            ) + '\n'

            # Write the serialized JSON to the file stream.
            with self:
                self.file.write(content)

        except TiferetError:

            # Re-raise structured errors from FileLoader (e.g., FILE_NOT_FOUND).
            raise

        except Exception as e:

            # Wrap write errors as structured TiferetError.
            RaiseError.execute(
                error_code=a.const.JSON_FILE_SAVE_ERROR_ID,
                error=str(e),
                path=str(self.path),
            )

    # * method: parse_json_path (static)
    @staticmethod
    def parse_json_path(data: Any, path: str) -> Any:
        '''
        Navigate nested JSON structure using dot notation with array index support.

        :param data: Parsed JSON object (dict or list).
        :type data: Any
        :param path: Dot-separated path (e.g., 'users.0.name').
        :type path: str
        :return: Value at the specified path.
        :rtype: Any
        '''

        # Walk through each segment of the dot-separated path.
        current = data
        parts = path.split('.')
        for part in parts:

            # Navigate dict keys.
            if isinstance(current, dict):
                current = current.get(part)

            # Navigate list indices.
            elif isinstance(current, list) and part.isdigit():
                current = current[int(part)]

            # Raise on invalid navigation.
            else:
                RaiseError.execute(
                    error_code=a.const.INVALID_JSON_PATH_ID,
                    path=path,
                    part=part,
                )

            # Short-circuit if a segment resolves to None.
            if current is None:
                break

        # Return the resolved value.
        return current
