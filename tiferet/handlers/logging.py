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

    # * method: list_all
    def list_all(self) -> Tuple[List[FormatterContract], List[HandlerContract], List[LoggerContract]]:
        '''
        List all formatter, handler, and logger configurations.

        :return: A tuple of formatter, handler, and logger configurations.
        :rtype: Tuple[List[FormatterContract], List[HandlerContract], List[LoggerContract]]
        '''
        # Retrieve all logging configurations from the repository.
        return self.logging_repo.list_all()
    
    # * method: format_config
    def format_config(
        self,
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
        # Get the root logger configuration and ensure it exists.
        root_logger = next((logger for logger in loggers if logger.is_root), None)
        if not root_logger:
            raise_error.execute(
                'LOGGING_CONFIG_FAILED',
                'Failed to configure logging: No root logger configuration found.',
                'No root logger'
            )

        # Format the configurations into a dictionary.
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
        :return: The native logger instance.
        :rtype: logging.Logger
        '''
        # Configure the logging system with the formatted configurations.
        try:
            logging.config.dictConfig(logging_config)
        except Exception as e:
            raise_error.execute(
                'LOGGING_CONFIG_FAILED',
                'Failed to configure logging: {e}.',
                str(e)
            )

        # Return the logger instance by its ID.
        try:
            logger = logging.getLogger(logger_id)
        except Exception as e:
            raise_error.execute(
                'LOGGER_CREATION_FAILED',
                f'Failed to create logger with ID {logger_id}: {e}.',
                logger_id, 
                str(e)
            )

        return logger
