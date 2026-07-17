"""Tiferet Logging Contexts"""

# *** imports

# ** core
import logging
import logging.config
from typing import Any, Callable, Dict, Tuple

# ** app
from .core import BaseContext
from .cache import CacheContext
from ..domain import LoggingSettings
from ..events import RaiseError, a

# *** constants

# ** constant: logging_cache_prefix
LOGGING_CACHE_PREFIX: Tuple[str, ...] = ('logging',)

# *** functions

# ** function: add_default_logging_settings
def add_default_logging_settings(settings: Dict[str, Any]) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with the default
    LoggingSettings domain object.

    Wraps a cache-builder callable so that, after the cache is constructed,
    the supplied settings dict is validated into a ``LoggingSettings`` domain
    object and stored in the cache under ``LOGGING_CACHE_PREFIX`` keyed by
    ``'default'``.

    :param settings: A raw dict of logging settings (formatters, handlers, loggers).
    :type settings: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Return the decorator that wraps the cache-builder.
    def decorator(build_fn: Callable) -> Callable:

        # Build the cache, then populate it with the default LoggingSettings domain object.
        def wrapper(*args, **kwargs) -> CacheContext:

            # Delegate to the wrapped cache-builder.
            cache = build_fn(*args, **kwargs)

            # Validate the raw settings dict into a LoggingSettings domain object
            # and store it under the logging namespace keyed by 'default'.
            cache.set('default', LoggingSettings.model_validate(settings), *LOGGING_CACHE_PREFIX)

            # Return the populated cache context.
            return cache

        return wrapper

    return decorator

# ** function: get_default_logging_settings
def get_default_logging_settings(cache: CacheContext) -> LoggingSettings:
    '''
    Return the default LoggingSettings seeded on the cache.

    :param cache: The cache context to read.
    :type cache: CacheContext
    :return: The default LoggingSettings domain object.
    :rtype: LoggingSettings
    '''

    # Retrieve the default LoggingSettings from the logging namespace.
    return cache.get('default', *LOGGING_CACHE_PREFIX)

# *** contexts

# ** context: logging_context
class LoggingContext(BaseContext):
    '''
    The logging context builds a configured logger from a pre-assembled
    ``LoggingSettings`` domain object, applying the settings once at session
    startup rather than re-fetching from the repository on every request.
    '''

    # * attribute: domain_type
    domain_type = LoggingSettings

    # * attribute: logger_id
    logger_id: str

    # * init
    def __init__(self, logger_id: str):
        '''
        Initialize the logging context.

        :param logger_id: The ID of the logger configuration to create.
        :type logger_id: str
        '''

        # Initialize the base context.
        super().__init__()

        # Store the logger ID.
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
        Build a logger instance from the pre-assembled domain settings.

        :return: The native logger instance.
        :rtype: logging.Logger
        '''

        # Assemble the dictConfig via the domain value object and create the logger.
        return self.create_logger(
            logger_id=self.logger_id,
            logging_config=self.domain.format_config(),
        )

