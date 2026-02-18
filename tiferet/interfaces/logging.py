"""Tiferet Logging Contracts"""

# *** imports

# ** core
from abc import abstractmethod
from typing import (
    Any,
    Dict,
    List,
    Tuple
)
import logging

# ** app
from ..mappers import (
    FormatterAggregate,
    HandlerAggregate,
    LoggerAggregate,
)
from .settings import Service

# *** interfaces

# ** interface: logging_service
class LoggingService(Service):
    '''
    Service interface for managing logging configurations.
    '''

    # * method: list_all
    @abstractmethod
    def list_all(self) -> Tuple[List[FormatterAggregate], List[HandlerAggregate], List[LoggerAggregate]]:
        '''
        List all logging configurations.

        :return: A tuple of formatter, handler, and logger aggregates.
        :rtype: Tuple[List[FormatterAggregate], List[HandlerAggregate], List[LoggerAggregate]]
        '''
        # Not implemented.
        raise NotImplementedError('list_all method is required for LoggingService.')
    
    # * method: save_formatter
    @abstractmethod
    def save_formatter(self, formatter: FormatterAggregate) -> None:
        '''
        Save a formatter configuration.

        :param formatter: The formatter aggregate to save.
        :type formatter: FormatterAggregate
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('save_formatter method is required for LoggingService.')
    
    # * method: save_handler
    @abstractmethod
    def save_handler(self, handler: HandlerAggregate) -> None:
        '''
        Save a handler configuration.

        :param handler: The handler aggregate to save.
        :type handler: HandlerAggregate
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('save_handler method is required for LoggingService.')
    
    # * method: save_logger
    @abstractmethod
    def save_logger(self, logger: LoggerAggregate) -> None:
        '''
        Save a logger configuration.

        :param logger: The logger aggregate to save.
        :type logger: LoggerAggregate
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('save_logger method is required for LoggingService.')
    
    # * method: delete_formatter
    @abstractmethod
    def delete_formatter(self, formatter_id: str) -> None:
        '''
        Delete a formatter configuration by its ID.

        :param formatter_id: The ID of the formatter to delete.
        :type formatter_id: str
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('delete_formatter method is required for LoggingService.')
    
    # * method: delete_handler
    @abstractmethod
    def delete_handler(self, handler_id: str) -> None:
        '''
        Delete a handler configuration by its ID.

        :param handler_id: The ID of the handler to delete.
        :type handler_id: str
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('delete_handler method is required for LoggingService.')
    
    # * method: delete_logger
    @abstractmethod
    def delete_logger(self, logger_id: str) -> None:
        '''
        Delete a logger configuration by its ID.

        :param logger_id: The ID of the logger to delete.
        :type logger_id: str
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('delete_logger method is required for LoggingService.')
