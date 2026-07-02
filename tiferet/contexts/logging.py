"""Tiferet Logging Contexts"""

# *** imports

# ** core
import logging
import logging.config
from typing import Dict, Any, List, Callable

# ** app
from .base import BaseContext
from .cache import CacheContext
from ..assets.logging import *
from ..domain import (
    Formatter,
    Handler,
    Logger,
    LoggingSettings,
)
from ..events import DomainEvent, RaiseError, a

# *** contexts

# ** context: logging_context
class LoggingContext(BaseContext):
    '''
    The logging context builds a configured logger from formatter, handler, and
    logger definitions, applying built-in defaults when none are configured.
    '''

    # * attribute: list_all_handler
    list_all_handler: Callable

    # * attribute: logger_id
    logger_id: str

    # * init
    def __init__(self, logging_list_all_evt: DomainEvent, logger_id: str, cache: CacheContext = None):
        '''
        Initialize the logging context.

        :param logging_list_all_evt: The event to list all logging configurations.
        :type logging_list_all_evt: DomainEvent
        :param logger_id: The ID of the logger configuration to create.
        :type logger_id: str
        :param cache: The shared cache context.
        :type cache: CacheContext
        '''

        # Initialize the shared cache via the base context.
        super().__init__(cache=cache)

        # Bind the list all handler and store the logger ID.
        self.list_all_handler = logging_list_all_evt.execute
        self.logger_id = logger_id

    # * method: create_logger
    def create_logger(self, logger_id: str, logging_config: Dict[str, Any]) -> logging.Logger:
        '''
        Create a logger instance for the specified logger ID.

        :param logger_id: The ID of the logger configuration to create.
        :type logger_id: str
        :param logging_config: The logging configuration dictionary.
        :type logging_config: Dict[str, Any]
        :return: The native logger instance.
        :rtype: logging.Logger
        '''

        # Configure the logging system with the formatted configurations.
        try:
            logging.config.dictConfig(logging_config)
        except Exception as e:
            RaiseError.execute(
                a.const.LOGGING_CONFIG_FAILED_ID,
                f'Failed to configure logging: {e}.',
                exception=str(e)
            )

        # Return the logger instance by its ID.
        try:
            logger = logging.getLogger(logger_id)
        except Exception as e:
            RaiseError.execute(
                a.const.LOGGER_CREATION_FAILED_ID,
                f'Failed to create logger with ID {logger_id}: {e}.',
                logger_id=logger_id,
                exception=str(e)
            )

        # Return the logger.
        return logger

    # * method: build_logger
    def build_logger(self) -> logging.Logger:
        '''
        Build a logger instance for the specified logger ID.

        :return: The native logger instance.
        :rtype: logging.Logger
        '''

        # List all formatter, handler, and logger configurations.
        formatters, handlers, loggers = self.list_all_handler()

        # Build the runtime logging settings value object, applying the built-in
        # defaults as the fallback for any section the repository does not provide.
        settings = LoggingSettings(
            formatters=formatters or [Formatter(**data) for data in DEFAULT_FORMATTERS],
            handlers=handlers or [Handler(**data) for data in DEFAULT_HANDLERS],
            loggers=loggers or [Logger(**data) for data in DEFAULT_LOGGERS],
        )

        # Assemble the dictConfig via the value object and create the logger.
        return self.create_logger(
            logger_id=self.logger_id,
            logging_config=settings.format_config(),
        )

