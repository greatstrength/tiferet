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

    # * attribute: logger
    logger: logging.Logger

    # * method: list_all
    @abstractmethod
    def list_all(self) -> Tuple[List[FormatterContract], List[HandlerContract], List[LoggerContract]]:
        '''
        List all logging configurations.

        :return: A tuple of formatter, handler, and logger configurations.
        :rtype: Tuple[List[FormatterContract], List[HandlerContract], List[LoggerContract]]
        '''
        raise NotImplementedError('The list_all method must be implemented by the logging service.')
    
    # * method: format_config
    @abstractmethod
    def format_config(self, 
        formatters: List[FormatterContract], 
        handlers: List[HandlerContract], 
        loggers: List[LoggerContract],
        version: int = 1,
        disable_existing_loggers: bool = False
        ) -> Dict[str, Any]:
        '''
        Format the logging configurations into a dictionary.

        :param formatters: List of formatter configurations.
        :type formatters: List[FormatterContract]
        :param handlers: List of handler configurations.
        :type handlers: List[HandlerContract]
        :param loggers: List of logger configurations.
        :type loggers: List[LoggerContract]
        :param version: The version of the logging configuration format.
        :type version: int
        :param disable_existing_loggers: Whether to disable existing loggers.
        :type disable_existing_loggers: bool
        :return: The formatted logging configurations.
        :rtype: Dict[str, Any]
        '''
        raise NotImplementedError('The format_config method must be implemented by the logging service.')

    # * method: create_logger
    @abstractmethod
    def create_logger(self, logger_id: str, logging_config: Dict[str, Any]) -> logging.Logger:
        '''
        Create a logger instance for the specified logger ID.

        :param logger_id: The ID of the logger configuration to create.
        :type logger_id: str
        :return: The native logger instance.
        :param logging_config: The logging configuration dictionary.
        :type logging_config: Dict[str, Any]
        :rtype: logging.Logger
        '''
        raise NotImplementedError('The create_logger method must be implemented by the logging service.')
