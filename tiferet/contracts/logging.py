# *** imports

# ** core
from typing import Any, Dict, List, Tuple
import logging

# ** app
from .settings import *

# *** contracts

# ** contract: formatter
class FormatterContract(ModelContract):
    '''
    Formatter contract for logging configuration.
    '''

    # * attribute: id
    id: str

    # * method: format_config
    def format_config(self) -> Dict[str, Any]:
        '''
        Format the formatter configuration into a dictionary.

        :return: The formatted formatter configuration.
        :rtype: Dict[str, Any]
        '''
        raise NotImplementedError('The format_config method must be implemented by the formatter contract.')

# ** contract: handler
class HandlerContract(ModelContract):
    '''
    Handler contract for logging configuration.
    '''

    # * attribute: id
    id: str

    # * method: format_config
    def format_config(self) -> Dict[str, Any]:
        '''
        Format the handler configuration into a dictionary.

        :return: The formatted handler configuration.
        :rtype: Dict[str, Any]
        '''
        raise NotImplementedError('The format_config method must be implemented by the handler contract.')

# ** contract: logger
class LoggerContract(ModelContract):
    '''
    Logger contract for logging configuration.
    '''

    # * attribute: id
    id: str

    # * attribute: is_root
    is_root: bool

    # * method: format_config
    def format_config(self) -> Dict[str, Any]:
        '''
        Format the logger configuration into a dictionary.

        :return: The formatted logger configuration.
        :rtype: Dict[str, Any]
        '''
        raise NotImplementedError('The format_config method must be implemented by the logger contract.')

# ** contract: logging_repository
class LoggingRepository(Repository):
    '''
    Logging repository interface.
    '''

    # * method: list_all
    @abstractmethod
    def list_all(self) -> Tuple[List[FormatterContract], List[HandlerContract], List[LoggerContract]]:
        '''
        List all logging configurations.

        :return: A tuple of formatter, handler, and logger configurations.
        :rtype: Tuple[FormatterContract, HandlerContract, LoggerContract]
        '''
        raise NotImplementedError('The list_all method must be implemented by the logging repository.')

# ** contract: logging_service
class LoggingService(Service):
    '''
    Logging service contract.
    '''

    # * method: create_logger
    @abstractmethod
    def create_logger(self, logger_id: str) -> logging.Logger:
        '''
        Create a logger instance for the specified logger ID.

        :param logger_id: The ID of the logger configuration to create.
        :type logger_id: str
        :return: The native logger instance.
        :rtype: logging.Logger
        '''
        raise NotImplementedError('The create_logger method must be implemented by the logging service.')