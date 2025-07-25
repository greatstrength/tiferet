# *** imports

# ** core
import logging

# ** app
from ..configs.logging import *
from ..models.logging import *
from ..handlers.logging import LoggingService

# *** contexts

# ** context: logging_context
class LoggingContext(object):

    # * attribute: logging_service
    logging_service: LoggingService

    # * attribute: logger_id
    logger_id: str

    def __init__(self, logging_service: LoggingService, logger_id: str):
        '''
        Initialize the logging context.

        :param logging_service: The logging service to use for managing logger configurations.
        :type logging_service: LoggingService
        :param logger_id: The ID of the logger configuration to create.
        :type logger_id: str
        '''
        self.logging_service = logging_service
        self.logger_id = logger_id

    def build_logger(self) -> logging.Logger:
        '''
        Build a logger instance for the specified logger ID.

        :param logger_id: The ID of the logger configuration to create.
        :type logger_id: str
        :return: The native logger instance.
        :rtype: logging.Logger
        '''

        # List all formatter, handler, and logger configurations.
        formatters, handlers, loggers = self.logging_service.list_all()

        # Set the default configurations if not provided.
        if not formatters:
            formatters = [ModelObject.new(
                Formatter,
                **data
            ) for data in DEFAULT_FORMATTERS]
        if not handlers:
            handlers = [ModelObject.new(
                Handler,
                **data
            ) for data in DEFAULT_HANDLERS]
        if not loggers:
            loggers = [ModelObject.new(
                Logger,
                **data
            ) for data in DEFAULT_LOGGERS]

        # Format the configurations into a dictionary.
        config = self.logging_service.format_config(
            formatters=formatters,
            handlers=handlers,
            loggers=loggers
        )

        # Create the logger using the logging service.
        return self.logging_service.create_logger(
            logger_id=self.logger_id,
            logging_config=config
        )

