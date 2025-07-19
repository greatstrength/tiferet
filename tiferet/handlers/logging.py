# *** imports

# ** core
import logging
import logging.config

# ** app
from ..commands import *
from ..contracts.logging import *

# *** handlers

# ** handler: logging_handler
class LoggingHandler(LoggingService):
    '''
    Logging handler for managing logger configurations.
    '''

    # * attribute: logging_repo
    logging_repo: LoggingRepository

    # * method: __init__
    def __init__(self, logging_repo: LoggingRepository):
        '''
        Initialize the logging handler.

        :param logging_repo: The logging repository to use for retrieving configurations.
        :type logging_repo: LoggingRepository
        '''
        self.logging_repo = logging_repo

    # * method: create_logger
    def create_logger(self, logger_id: str) -> logging.Logger:
        '''
        Create a logger instance for the specified logger ID.

        :param logger_id: The ID of the logger configuration to create.
        :type logger_id: str
        :return: The native logger instance.
        :rtype: logging.Logger
        '''
        # Get the logging configurations from the logging repository.
        formatters, handlers, loggers = self.logging_repo.list_all()

        # Check for root logger presence.
        root_logger = next((logger for logger in loggers if logger.is_root), None)
        if not root_logger:
            raise_error.execute(
                'LOGGING_CONFIG_FAILED',
                'Failed to configure logging: No root logger configuration found.',
                'No root logger'
            )

        # Format the configurations dictionary.
        config = dict(
            version=1,
            disable_existing_loggers=False,
            formatters={formatter.id: formatter.format_config() for formatter in formatters},
            handlers={handler.id: handler.format_config() for handler in handlers},
            loggers={logger.id: logger.format_config() for logger in loggers if not logger.is_root},
            root=root_logger.format_config() if root_logger else None
        )

        # Configure the logging system with the formatted configurations.
        try:
            logging.config.dictConfig(config)
        except Exception as e:
            raise_error.execute(
                'LOGGING_CONFIG_FAILED',
                'Failed to configure logging: {}.',
                str(e)
            )

        # Return the logger instance by its ID.
        try:
            logger = logging.getLogger(logger_id)
        except:
            raise_error.execute(
                'LOGGER_CREATION_FAILED',
                'Failed to create logger with ID {}: {}.',
                logger_id, 'Logger not configured with handlers'
            )

        return logger