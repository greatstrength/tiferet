"""Tiferet Repository Settings"""

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
    Format-agnostic base class for configuration-backed repositories.

    Inspects the file extension of ``config_file`` to dispatch I/O to the
    appropriate loader (YAML or JSON). Concrete repos extend this class
    alongside their domain Service interface and use ``_load`` / ``_save``
    for all persistence operations.
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

        :param config_file: Path to the configuration file (.yml, .yaml, or .json).
        :type config_file: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Set the repository attributes.
        self.config_file = config_file
        self.encoding = encoding
        self.default_role = 'to_data'

    # * method: _get_loader
    def _get_loader(self, mode: str = 'r') -> Any:
        '''
        Return the appropriate file loader based on the config file extension.

        :param mode: File open mode ('r' for read, 'w' for write).
        :type mode: str
        :return: A loader instance (YamlLoader or JsonLoader).
        :rtype: Any
        '''

        # Determine the file extension.
        ext = Path(self.config_file).suffix.lower()

        # Dispatch to the appropriate loader.
        if ext in ('.yaml', '.yml'):
            return YamlLoader(self.config_file, mode=mode, encoding=self.encoding)

        if ext == '.json':
            return JsonLoader(self.config_file, mode=mode, encoding=self.encoding)

        # Raise a structured error for unsupported extensions.
        RaiseError.execute(
            error_code=a.const.UNSUPPORTED_CONFIG_FILE_TYPE_ID,
            file_extension=ext,
        )

    # * method: _load
    def _load(self,
            start_node: Callable[[Any], Any] = lambda x: x,
            data_factory: Callable[[Any], Any] = lambda x: x,
        ) -> Any:
        '''
        Load configuration data using the format-appropriate loader.

        :param start_node: Callable to select the starting node of the data.
        :type start_node: Callable[[Any], Any]
        :param data_factory: Callable to transform the loaded data.
        :type data_factory: Callable[[Any], Any]
        :return: The loaded and transformed configuration data.
        :rtype: Any
        '''

        # Delegate to the loader's load method.
        return self._get_loader().load(
            start_node=start_node,
            data_factory=data_factory,
        )

    # * method: _save
    def _save(self, data: Any) -> None:
        '''
        Save configuration data using the format-appropriate loader.

        :param data: The data to persist.
        :type data: Any
        '''

        # Delegate to the loader's save method.
        self._get_loader(mode='w').save(data=data)
