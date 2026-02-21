# *** imports

# ** core
import logging
import logging.config
from typing import (
    Dict,
    Any,
    List,
    Callable
)

# ** app
from ..assets.logging import *
from ..domain import (
    DomainObject,
    Formatter,
    Handler,
    Logger
)
from ..events import RaiseError, a
from ..events.logging import ListAllLoggingConfigs

# *** contexts

# ** context: logging_context
class LoggingContext(object):

    # * attribute: list_all_handler
    list_all_handler: Callable

    # * attribute: logger_id
    logger_id: str

    # * init
    def __init__(self,
                 list_all_cmd: ListAllLoggingConfigs,
                 logger_id: str):
        '''
        Initialize the logging context.

        :param list_all_cmd: Command to list all logging configurations.
        :type list_all_cmd: ListAllLoggingConfigs
        :param logger_id: The ID of the logger configuration to create.
        :type logger_id: str
        '''
        self.list_all_handler = list_all_cmd.execute
        self.logger_id = logger_id

    # * method: format_config
    def format_config(self,
                      formatters: List[Formatter],
                      handlers: List[Handler],
                      loggers: List[Logger],
                      version: int = 1,
                      disable_existing_loggers: bool = False) -> Dict[str, Any]:
        '''
        Format logging configurations into a dictionary suitable for logging.config.dictConfig.

        :param formatters: List of formatter entities.
        :type formatters: List[Formatter]
        :param handlers: List of handler entities.
        :type handlers: List[Handler]
        :param loggers: List of logger entities.
        :type loggers: List[Logger]
        :param version: Logging configuration version (default 1).
        :type version: int
        :param disable_existing_loggers: Whether to disable existing loggers (default False).
        :type disable_existing_loggers: bool
        :return: Dictionary configuration for logging.config.dictConfig.
        :rtype: Dict[str, Any]
        '''

        # Return the formatted configuration dictionary.
        return dict(
            version=version,
            disable_existing_loggers=disable_existing_loggers,
            formatters={formatter.id: formatter.format_config() for formatter in formatters},
            handlers={handler.id: handler.format_config() for handler in handlers},
            loggers={logger.id: logger.format_config() for logger in loggers if not logger.is_root},
            root=next((logger.format_config() for logger in loggers if logger.is_root), None)
        )

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
                'Failed to configure logging: {e}.',
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

        # Set the default configurations if not provided.
        if not formatters:
            formatters = [DomainObject.new(
                Formatter,
                **data
            ) for data in DEFAULT_FORMATTERS]
        if not handlers:
            handlers = [DomainObject.new(
                Handler,
                **data
            ) for data in DEFAULT_HANDLERS]
        if not loggers:
            loggers = [DomainObject.new(
                Logger,
                **data
            ) for data in DEFAULT_LOGGERS]

        # Format the configurations into a dictionary.
        config = self.format_config(
            formatters=formatters,
            handlers=handlers,
            loggers=loggers
        )

        # Create the logger using the create_logger method.
        return self.create_logger(
            logger_id=self.logger_id,
            logging_config=config
        )

