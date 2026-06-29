"""Tiferet Utils Middleware"""

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
    Infrastructure middleware that logs domain event execution.

    Emits a DEBUG record before and after the wrapped execution and an ERROR
    record (with traceback) when the chain raises.  The middleware observes
    execution without altering control flow: the result of ``next_fn`` is
    returned unchanged and any exception is re-raised unaltered.  It contains
    no domain logic and raises no ``TiferetError``.
    '''

    # * attribute: logger
    logger: logging.Logger

    # * init
    def __init__(self, logger_id: str = 'root'):
        '''
        Initialize the LoggingMiddleware.

        :param logger_id: The name of the stdlib logger to resolve.
        :type logger_id: str
        '''

        # Resolve the named stdlib logger by logger_id.
        self.logger = logging.getLogger(logger_id)

    # * method: __call__
    def __call__(self,
            event: Any,
            kwargs: Dict[str, Any],
            next_fn: Callable[[], Any],
        ) -> Any:
        '''
        Log execution around the wrapped chain, then return its result.

        :param event: The instantiated domain event instance.
        :type event: Any
        :param kwargs: The merged execution keyword arguments.
        :type kwargs: Dict[str, Any]
        :param next_fn: Zero-argument callable that invokes the remainder of the chain.
        :type next_fn: Callable[[], Any]
        :return: The unchanged result of the chain execution.
        :rtype: Any
        '''

        # Resolve the event class name for the log records.
        name = event.__class__.__name__

        # Log a DEBUG record before execution.
        self.logger.debug('Executing %s', name)

        # Execute the chain; on failure log an ERROR record with traceback and re-raise.
        try:
            result = next_fn()
        except Exception as exc:
            self.logger.error('Failed %s: %s', name, exc, exc_info=True)
            raise

        # Log a DEBUG record after successful execution.
        self.logger.debug('Completed %s', name)

        # Return the chain result unchanged.
        return result


# ** util: timing_middleware
class TimingMiddleware(MiddlewareService):
    '''
    Infrastructure middleware that times domain event execution.

    Measures elapsed wall-clock time with ``time.perf_counter`` and emits a
    single DEBUG record reporting the duration in milliseconds on both the
    success and exception paths.  The middleware observes execution without
    altering control flow: the result of ``next_fn`` is returned unchanged and
    any exception is re-raised unaltered.  It contains no domain logic and
    raises no ``TiferetError``.
    '''

    # * attribute: logger
    logger: logging.Logger

    # * init
    def __init__(self, logger_id: str = 'root'):
        '''
        Initialize the TimingMiddleware.

        :param logger_id: The name of the stdlib logger to resolve.
        :type logger_id: str
        '''

        # Resolve the named stdlib logger by logger_id.
        self.logger = logging.getLogger(logger_id)

    # * method: __call__
    def __call__(self,
            event: Any,
            kwargs: Dict[str, Any],
            next_fn: Callable[[], Any],
        ) -> Any:
        '''
        Time the wrapped chain, logging elapsed milliseconds, then return its result.

        :param event: The instantiated domain event instance.
        :type event: Any
        :param kwargs: The merged execution keyword arguments.
        :type kwargs: Dict[str, Any]
        :param next_fn: Zero-argument callable that invokes the remainder of the chain.
        :type next_fn: Callable[[], Any]
        :return: The unchanged result of the chain execution.
        :rtype: Any
        '''

        # Resolve the event class name for the log records.
        name = event.__class__.__name__

        # Capture the start time using a high-resolution performance counter.
        start = time.perf_counter()

        # Execute the chain; on failure log elapsed time and re-raise.
        try:
            result = next_fn()
        except Exception:
            elapsed = (time.perf_counter() - start) * 1000
            self.logger.debug('%s raised after %.2fms', name, elapsed)
            raise

        # Compute elapsed time and log a single DEBUG record on success.
        elapsed = (time.perf_counter() - start) * 1000
        self.logger.debug('%s completed in %.2fms', name, elapsed)

        # Return the chain result unchanged.
        return result
