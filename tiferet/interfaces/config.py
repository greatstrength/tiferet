"""Tiferet Interfaces Configuration"""

# *** imports

# ** core
from abc import abstractmethod
from typing import Any, Callable

# ** app
from .settings import Service

# *** interfaces

# ** interface: configuration_service
class ConfigurationService(Service):
    '''
    Service contract for loading and persisting structured configuration data.
    '''

    # * method: load
    @abstractmethod
    def load(self,
            start_node: Callable[[Any], Any] = lambda x: x,
            data_factory: Callable[[Any], Any] = lambda x: x,
            **kwargs) -> Any:
        '''
        Load structured configuration data, optionally transforming it.

        :param start_node: Callable to select the starting node of the data.
        :type start_node: Callable[[Any], Any]
        :param data_factory: Callable to transform the loaded data.
        :type data_factory: Callable[[Any], Any]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The loaded configuration data.
        :rtype: Any
        '''
        raise NotImplementedError()

    # * method: save
    @abstractmethod
    def save(self, data: Any, data_path: str | None = None, **kwargs) -> None:
        '''
        Persist structured configuration data.

        :param data: The configuration data to persist.
        :type data: Any
        :param data_path: Optional path within the data structure.
        :type data_path: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''
        raise NotImplementedError()
