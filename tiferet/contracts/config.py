"""Configuration Service Contract"""

# *** imports

# ** core
from abc import abstractmethod
from typing import Any, Callable

# ** app
from .settings import Service

# *** contracts

# ** contract: configuration_service
class ConfigurationService(Service):
    '''
    Abstract contract for loading and saving structured configuration data (YAML, JSON, etc.).
    '''

    # * method: load
    @abstractmethod
    def load(self, start_node: Callable = lambda data: data, data_factory: Callable = lambda data: data) -> Any:
        '''
        Load and return configuration data.

        :param start_node: Optional callable to select starting node in loaded structure.
        :type start_node: Callable
        :param data_factory: Optional callable to transform loaded data into desired format.
        :type data_factory: Callable
        :return: Parsed configuration data.
        :rtype: Any
        '''
        
        raise NotImplementedError('load method must be implemented in the ConfigurationService class.')

    # * method: save
    @abstractmethod
    def save(self, data: Any, data_path: str = None, **kwargs):
        '''
        Save data to the configuration file.

        :param data: The data to persist.
        :type data: Any
        :param data_path: Optional path within the configuration structure to save data.
        :type data_path: str
        :param kwargs: Additional keyword arguments for saving.
        :type kwargs: dict
        '''
        
        raise NotImplementedError('save method must be implemented in the ConfigurationService class.')