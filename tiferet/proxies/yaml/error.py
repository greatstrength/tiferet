# *** imports

# ** core
from typing import Any, List, Dict

# ** app
from .core import *
from ...data.error import ErrorData
from ...contracts.error import (
    Error,
    ErrorRepository
)
from ...clients import yaml as yaml_client


# *** proxies

# ** proxy: yaml_proxy
class ErrorYamlProxy(ErrorRepository, YamlConfigurationProxy):
    '''
    The YAML proxy for the error repository
    '''

    # * method: init
    def __init__(self, error_config_file: str):
        '''
        Initialize the yaml proxy.

        :param error_config_file: The error configuration file.
        :type error_config_file: str
        '''

        # Set the base path.
        super().__init__(error_config_file)

    # * method: load_yaml
    def load_yaml(self, start_node: callable = lambda data: data, create_data: callable = lambda data: data) -> Any:
        '''
        Load data from the YAML configuration file.
        :param start_node: The starting node in the YAML file.
        :type start_node: str
        :param create_data: A callable to create data objects from the loaded data.
        :type create_data: callable
        :return: The loaded data.
        :rtype: Any
        '''

        # Load the YAML file contents using the yaml config proxy.
        try:
            return super().load_yaml(
                start_node=start_node,
                create_data=create_data
            )
        
        # Raise an error if the loading fails.
        except (Exception, TiferetError) as e:
            raise_error.execute(
                'ERROR_CONFIG_LOADING_FAILED',
                f'Unable to load error configuration file {self.config_file}: {e}.',
                self.config_file,
                str(e)
            )

    # * method: exists
    def exists(self, id: str, **kwargs) -> bool:
        '''
        Check if the error exists.
        
        :param id: The error id.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Whether the error exists.
        :rtype: bool
        '''

        # Load the error data from the yaml configuration file.
        data = self.get(id)

        # Return whether the error exists.
        return data is not None

    # * method: get
    def get(self, id: str) -> Error:
        '''
        Get the error.
        
        :param id: The error id.
        :type id: str
        :return: The error.
        :rtype: Error
        '''

        # Load the error data from the yaml configuration file.
        _data: ErrorData = self.load_yaml(
            create_data=lambda data: ErrorData.from_data(
                id=id, **data),
            start_node=lambda data: data.get('errors').get(id))

        # Return the error object.
        return _data.map() if _data else None
    
    # * method: list
    def list(self) -> List[Error]:
        '''
        List all errors.

        :return: The list of errors.
        :rtype: List[Error]
        '''

        # Load the error data from the yaml configuration file.
        _data: Dict[str, ErrorData] = self.load_yaml(
            create_data=lambda data: {id: ErrorData.from_data(
                id=id, **error_data) for id, error_data in data.items()},
            start_node=lambda data: data.get('errors'))

        # Return the error object.
        return [data.map() for data in _data.values()]

    # * method: save
    def save(self, error: Error):
        '''
        Save the error.

        :param error: The error.
        :type error: Error
        '''

        # Create updated error data.
        error_data = ErrorData.from_model(ErrorData, error)

        # Update the error data.
        yaml_client.save(
            yaml_file=self.config_file,
            data=error_data.to_primitive(),
            data_save_path=f'errors/{error.id}',
        )
