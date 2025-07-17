# *** imports

# ** core
from typing import List, Tuple
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

    # * attribute: name
    name: str

    # * attribute: description
    description: str

    # * attribute: format
    format: str

    # * attribute: datefmt
    datefmt: str

# ** contract: handler
class HandlerContract(ModelContract):
    '''
    Handler contract for logging configuration.
    '''

    # * attribute: id
    id: str

    # * attribute: name
    name: str

    # * attribute: description
    description: str

    # * attribute: module_path
    module_path: str

    # * attribute: class_name
    class_name: str

    # * attribute: level
    level: str

    # * attribute: formatter
    formatter: str

    # * attribute: stream
    stream: str

    # * attribute: filename
    filename: str

# ** contract: logger
class LoggerContract(ModelContract):
    '''
    Logger contract for logging configuration.
    '''

    # * attribute: id
    id: str

    # * attribute: name
    name: str

    # * attribute: description
    description: str

    # * attribute: level
    level: str

    # * attribute: handlers
    handlers: List[str]

    # * attribute: propagate
    propagate: bool

    # * attribute: is_root
    is_root: bool

# ** contract: logging_repository
class LoggingRepository(Repository):
    '''
    Logging repository interface.
    '''

    # * method: list_all
    @abstractmethod
    def list_all(self) -> Tuple[FormatterContract, HandlerContract, LoggerContract]:
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