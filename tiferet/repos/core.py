"""Tiferet Configuration Repository Settings"""

# *** imports

# ** core
from pathlib import Path
from typing import Any, Callable

# ** app
from ..utils import YamlLoader, JsonLoader
from ..events import RaiseError, a

# *** classes

# ** class: configuration_repository
class ConfigurationRepository:
    '''
    A format-agnostic base for configuration repositories.

    Dispatches load and save operations to a format-specific loader (YAML or
    JSON) based on the configuration file extension, and exposes a single
    ``default_role`` for transfer-object serialization regardless of the
    underlying file format.
    '''

    # * attribute: config_file
    config_file: str

    # * attribute: encoding
    encoding: str

    # * attribute: default_role
    default_role: str

    # * init
    def __init__(self, config_file: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the configuration repository.

        :param config_file: The configuration file path (.yaml/.yml or .json).
        :type config_file: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Set the configuration repository attributes.
        self.config_file = config_file
        self.encoding = encoding
        self.default_role = 'to_data'

    # * method: _get_loader
    def _get_loader(self, mode: str = 'r') -> Any:
        '''
        Resolve a format-specific configuration loader by file extension.

        :param mode: The file open mode (typically 'r' or 'w').
        :type mode: str
        :return: A loader appropriate for the configuration file's format.
        :rtype: Any
        '''

        # Determine the configuration file extension.
        ext = Path(self.config_file).suffix.lower()

        # Dispatch to the YAML loader for YAML extensions.
        if ext in ('.yaml', '.yml'):
            return YamlLoader(self.config_file, mode=mode, encoding=self.encoding)

        # Dispatch to the JSON loader for the JSON extension.
        if ext == '.json':
            return JsonLoader(self.config_file, mode=mode, encoding=self.encoding)

        # Raise a structured error for any unsupported file type.
        RaiseError.execute(
            error_code=a.error.UNSUPPORTED_CONFIG_FILE_TYPE_ID,
            file_extension=ext,
        )

    # * method: _load
    def _load(self,
            start_node: Callable[[Any], Any] = lambda x: x,
            data_factory: Callable[[Any], Any] = lambda x: x,
        ) -> Any:
        '''
        Load configuration data via the format-specific loader.

        :param start_node: Callable to select the starting node of the loaded data.
        :type start_node: Callable[[Any], Any]
        :param data_factory: Callable to transform the loaded data.
        :type data_factory: Callable[[Any], Any]
        :return: The loaded and transformed configuration data.
        :rtype: Any
        '''

        # Delegate to the resolved loader's load method.
        return self._get_loader().load(
            start_node=start_node,
            data_factory=data_factory,
        )

    # * method: _save
    def _save(self, data: Any) -> None:
        '''
        Persist configuration data via the format-specific loader.

        :param data: The configuration data to persist.
        :type data: Any
        :return: None
        :rtype: None
        '''

        # Delegate to the resolved write-mode loader's save method.
        self._get_loader(mode='w').save(data=data)
