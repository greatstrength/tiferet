"""Tiferet Configuration Repository Settings"""

# *** imports

# ** core
import os

# ** app
from ...contracts import ConfigurationService
from ...middleware import (
    Yaml,
    Json,
    TiferetError,
    const
)

# *** classes

# ** class: configuration_file_repository
class ConfigurationFileRepository(object):
    '''
    The base class for configuration file repositories.
    '''

    # * attribute: default_role
    default_role: str

    # * method: open_config
    def open_config(self, file_path: str, mode: str, encoding = 'utf-8', **kwargs) -> ConfigurationService:
        '''
        Open the configuration file.

        :param file_path: The configuration file path.
        :type file_path: str
        :param mode: The file open mode.
        :type mode: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The configuration service.
        :rtype: ConfigurationService
        '''
        
        # Retrieve the file extension.
        _, ext = os.path.splitext(file_path)

        # If the file is a YAML file, set the default role and return the YAML configuration service.
        if ext.lower() in ['.yaml', '.yml']:
            self.default_role = 'to_data.yaml'
            return Yaml(
                file_path,
                mode=mode,
                encoding=encoding,
                **kwargs
            )
        
        # If the file is a JSON file, set the default role and return the JSON configuration service.
        elif ext.lower() == '.json':
            self.default_role = 'to_data.json'
            return Json(
                file_path,
                mode=mode,
                encoding=encoding,
                **kwargs
            )
        
        # Raise an error for unsupported file types.
        else:
            raise TiferetError(
                const.UNSUPPORTED_CONFIG_FILE_TYPE_ID,
                f'Unsupported configuration file type: {ext}.',
                file_path=file_path,
                file_extension=ext
            )
        