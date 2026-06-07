"""Tiferet Middleware Utilities"""

# *** imports

# ** core
import logging
import time
from typing import Any, Callable, Dict

# ** app
from ..interfaces.middleware import MiddlewareService

# *** utils

# ** util: logging_middleware
class LoggingMiddleware(MiddlewareService):
    '''
    Middleware utility that logs domain event execution using Python's standard
    ``logging`` module.

    Emits a ``DEBUG`` record before execution and after successful execution.
    Emits an ``ERROR`` record (with ``exc_info``) when execution raises an
    exception, then re-raises so normal error handling is unaffected.

    The logger is resolved by name via ``logging.getLogger(logger_id)`` —
    ``LoggingContext.build_logger()`` must have been called during application
    startup (as it is by default) before any feature step executes.

    **Config example**::

        services:
          logging_middleware:
            module_path: tiferet.utils.middleware
            class_name: LoggingMiddleware
            parameters:
              logger_id: my_app_logger

    **Direct use**::

        DomainEvent.handle(
            AddNumber,
            middleware=[LoggingMiddleware(logger_id='my_app_logger')],
            a=1, b=2,
        )
    '''

    # * attribute: logger
    logger: logging.Logger

    # * init
    def __init__(self, logger_id: str = 'root'):
        '''
        Initialize the logging middleware.

        :param logger_id: Name of the logger to use (must match a logger
            defined in ``logging.yml`` or a stdlib root/named logger).
        :type logger_id: str
        '''

        # Resolve the named logger; relies on LoggingContext having configured
        # the logging subsystem during application startup.
        self.logger = logging.getLogger(logger_id)

    # * method: __call__
    def __call__(self,
            event: Any,
            kwargs: Dict[str, Any],
            next_fn: Callable[[], Any]) -> Any:
        '''
        Execute the logging middleware.

        Logs a DEBUG message before and after execution; logs an ERROR on
        exception and re-raises.

        :param event: The instantiated domain event instance.
        :type event: Any
        :param kwargs: The merged execution keyword arguments.
        :type kwargs: Dict[str, Any]
        :param next_fn: Zero-argument callable that continues the chain.
        :type next_fn: Callable[[], Any]
        :return: The result of the event execution.
        :rtype: Any
        '''

        # Capture the event class name for log messages.
        name = event.__class__.__name__

        # Log the pre-execution entry.
        self.logger.debug('Executing %s', name)

        # Execute the chain, logging errors and re-raising for normal handling.
        try:
            result = next_fn()

        except Exception as exc:
            self.logger.error('Failed %s: %s', name, exc, exc_info=True)
            raise

        # Log the post-execution exit.
        self.logger.debug('Completed %s', name)

        # Return the result.
        return result


# ** util: timing_middleware
class TimingMiddleware(MiddlewareService):
    '''
    Middleware utility that measures and logs wall-clock execution time for
    each domain event using ``time.perf_counter``.

    Emits a single ``DEBUG`` record after execution (or after an exception)
    reporting elapsed time in milliseconds.  Exceptions are always re-raised
    so normal error handling is unaffected.

    **Config example**::

        services:
          timing_middleware:
            module_path: tiferet.utils.middleware
            class_name: TimingMiddleware
            parameters:
              logger_id: my_app_logger

    **Direct use**::

        DomainEvent.handle(
            AddNumber,
            middleware=[TimingMiddleware(logger_id='my_app_logger')],
            a=1, b=2,
        )
    '''

    # * attribute: logger
    logger: logging.Logger

    # * init
    def __init__(self, logger_id: str = 'root'):
        '''
        Initialize the timing middleware.

        :param logger_id: Name of the logger to use (must match a logger
            defined in ``logging.yml`` or a stdlib root/named logger).
        :type logger_id: str
        '''

        # Resolve the named logger; relies on LoggingContext having configured
        # the logging subsystem during application startup.
        self.logger = logging.getLogger(logger_id)

    # * method: __call__
    def __call__(self,
            event: Any,
            kwargs: Dict[str, Any],
            next_fn: Callable[[], Any]) -> Any:
        '''
        Execute the timing middleware.

        Records wall-clock elapsed time and logs it at DEBUG level after
        execution.  Re-raises any exception after logging the elapsed time.

        :param event: The instantiated domain event instance.
        :type event: Any
        :param kwargs: The merged execution keyword arguments.
        :type kwargs: Dict[str, Any]
        :param next_fn: Zero-argument callable that continues the chain.
        :type next_fn: Callable[[], Any]
        :return: The result of the event execution.
        :rtype: Any
        '''

        # Capture the event class name and start the timer.
        name = event.__class__.__name__
        start = time.perf_counter()

        # Execute the chain, ensuring elapsed time is always logged.
        try:
            result = next_fn()

        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            self.logger.debug('%s raised after %.2fms', name, elapsed)
            raise

        # Log the elapsed execution time.
        elapsed = (time.perf_counter() - start) * 1000
        self.logger.debug('%s completed in %.2fms', name, elapsed)

        # Return the result.
        return result
