"""Tiferet Utils Core Tests"""

# *** imports

# ** core
import logging
import re

# ** infra
import pytest

# ** app
from tiferet.utils.core import CacheMiddleware, LoggingMiddleware, TimingMiddleware
from tiferet.interfaces.middleware import MiddlewareService


# *** fixtures

# ** fixture: sample_event
@pytest.fixture
def sample_event() -> object:
    '''
    Provide a stub domain event whose class name is observable in log records.

    :return: A stub event instance with class name ``SampleEvent``.
    :rtype: object
    '''

    # Define a minimal stand-in event class.
    class SampleEvent:
        pass

    # Return an instance of the stub event.
    return SampleEvent()


# *** tests

# ** test: middleware_conformance
def test_middleware_conformance():
    '''
    Test that both utilities conform to MiddlewareService and resolve the default logger.
    '''

    # Assert class-level conformance to the MiddlewareService contract.
    assert issubclass(LoggingMiddleware, MiddlewareService)
    assert issubclass(CacheMiddleware, MiddlewareService)
    assert issubclass(TimingMiddleware, MiddlewareService)

    # Instantiate the utilities with their default constructor arguments.
    logging_mw = LoggingMiddleware()
    cache_mw = CacheMiddleware()
    timing_mw = TimingMiddleware()

    # Assert instance-level conformance to the MiddlewareService contract.
    assert isinstance(logging_mw, MiddlewareService)
    assert isinstance(cache_mw, MiddlewareService)
    assert isinstance(timing_mw, MiddlewareService)

    # Assert the default logger_id resolves a logger named 'root'.
    # NOTE: logging.getLogger('root') returns a named logger called 'root' — a child of
    # the true process root logger (logging.getLogger() with no name), not the root
    # logger itself; records still propagate to the root handlers.
    assert logging_mw.logger.name == 'root'
    assert timing_mw.logger.name == 'root'


# ** test: middleware_resolves_named_logger
def test_middleware_resolves_named_logger():
    '''
    Test that a custom logger_id resolves a logger whose name matches.
    '''

    # Instantiate both utilities with a custom logger_id.
    logging_mw = LoggingMiddleware(logger_id='tiferet.test')
    timing_mw = TimingMiddleware(logger_id='tiferet.test')

    # Assert the resolved loggers carry the requested name.
    assert logging_mw.logger.name == 'tiferet.test'
    assert timing_mw.logger.name == 'tiferet.test'


# ** test: middleware_forwards_nonempty_kwargs
def test_middleware_forwards_nonempty_kwargs(sample_event: object):
    '''
    Test that both utilities return the chain result unchanged and leave a non-empty kwargs dict intact.

    :param sample_event: The stub event instance.
    :type sample_event: object
    '''

    # Build both utilities and a next_fn returning a sentinel result.
    logging_mw = LoggingMiddleware()
    timing_mw = TimingMiddleware()
    next_fn = lambda: 'result'

    # Provide a non-empty kwargs dict that the middleware must forward without inspecting or mutating.
    kwargs = {'a': 1}

    # Assert both utilities return the chain result unchanged.
    assert logging_mw(sample_event, kwargs, next_fn) == 'result'
    assert timing_mw(sample_event, kwargs, next_fn) == 'result'

    # Assert the kwargs dict was neither consumed nor mutated.
    assert kwargs == {'a': 1}


# ** test: logging_middleware_success
def test_logging_middleware_success(sample_event: object, caplog):
    '''
    Test that LoggingMiddleware returns the chain result unchanged and logs DEBUG records.

    :param sample_event: The stub event instance.
    :type sample_event: object
    :param caplog: Pytest log-capture fixture.
    :type caplog: pytest.LogCaptureFixture
    '''

    # Capture DEBUG-level records.
    caplog.set_level(logging.DEBUG)

    # Build the middleware and a next_fn returning a sentinel result.
    middleware = LoggingMiddleware()
    next_fn = lambda: 'result'

    # Execute the middleware around the chain.
    result = middleware(sample_event, {}, next_fn)

    # Assert the chain result is returned unchanged.
    assert result == 'result'

    # Assert DEBUG records were emitted before and after execution.
    debug_messages = [r.getMessage() for r in caplog.records if r.levelno == logging.DEBUG]
    assert 'Executing SampleEvent' in debug_messages
    assert 'Completed SampleEvent' in debug_messages


# ** test: logging_middleware_failure
def test_logging_middleware_failure(sample_event: object, caplog):
    '''
    Test that LoggingMiddleware logs an ERROR record with traceback and re-raises.

    :param sample_event: The stub event instance.
    :type sample_event: object
    :param caplog: Pytest log-capture fixture.
    :type caplog: pytest.LogCaptureFixture
    '''

    # Capture DEBUG-level records.
    caplog.set_level(logging.DEBUG)

    # Build the middleware and a next_fn that raises.
    middleware = LoggingMiddleware()

    def next_fn():
        raise ValueError('boom')

    # Execute and assert the original exception propagates unaltered.
    with pytest.raises(ValueError, match='boom'):
        middleware(sample_event, {}, next_fn)

    # Assert a single ERROR record with traceback was emitted.
    error_records = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert len(error_records) == 1
    assert error_records[0].exc_info is not None
    assert 'Failed SampleEvent' in error_records[0].getMessage()

    # Assert the pre-execution DEBUG record fired but not the completion record.
    debug_messages = [r.getMessage() for r in caplog.records if r.levelno == logging.DEBUG]
    assert 'Executing SampleEvent' in debug_messages
    assert 'Completed SampleEvent' not in debug_messages


# ** test: cache_middleware_injects_snapshot
def test_cache_middleware_injects_snapshot(sample_event: object):
    '''
    Test that CacheMiddleware injects the loaded snapshot as the 'cache' kwarg.

    :param sample_event: The stub event instance.
    :type sample_event: object
    '''

    # Build the middleware with a loader returning a sentinel snapshot.
    snapshot = {'seeded': 'value'}
    middleware = CacheMiddleware(load_cache=lambda: snapshot)

    # Provide a kwargs dict that carries no cache entry.
    kwargs = {'a': 1}

    # Execute the middleware around a chain returning a sentinel result.
    result = middleware(sample_event, kwargs, lambda: 'result')

    # Assert the chain result is returned unchanged.
    assert result == 'result'

    # Assert the snapshot was injected alongside the untouched original kwargs.
    assert kwargs['cache'] is snapshot
    assert kwargs['a'] == 1


# ** test: cache_middleware_preserves_existing_cache
def test_cache_middleware_preserves_existing_cache(sample_event: object):
    '''
    Test that CacheMiddleware never overwrites a cache value already in kwargs.

    :param sample_event: The stub event instance.
    :type sample_event: object
    '''

    # Build a loader that records whether it was invoked.
    calls = []

    def load_cache():
        calls.append(1)
        return {'seeded': 'value'}

    # Build the middleware and provide a kwargs dict already carrying a cache.
    middleware = CacheMiddleware(load_cache=load_cache)
    existing = {'existing': 'cache'}
    kwargs = {'cache': existing}

    # Execute the middleware around a chain returning a sentinel result.
    result = middleware(sample_event, kwargs, lambda: 'result')

    # Assert the chain result is returned unchanged.
    assert result == 'result'

    # Assert the pre-existing cache survived and the loader was never invoked.
    assert kwargs['cache'] is existing
    assert calls == []


# ** test: cache_middleware_no_loader_is_noop
def test_cache_middleware_no_loader_is_noop(sample_event: object):
    '''
    Test that CacheMiddleware is a transparent no-op when no loader is supplied.

    :param sample_event: The stub event instance.
    :type sample_event: object
    '''

    # Build the middleware without a cache loader.
    middleware = CacheMiddleware()

    # Provide a kwargs dict that carries no cache entry.
    kwargs = {'a': 1}

    # Execute the middleware around a chain returning a sentinel result.
    result = middleware(sample_event, kwargs, lambda: 'result')

    # Assert the chain result is returned unchanged.
    assert result == 'result'

    # Assert the kwargs dict was left entirely untouched.
    assert kwargs == {'a': 1}


# ** test: timing_middleware_success
def test_timing_middleware_success(sample_event: object, caplog):
    '''
    Test that TimingMiddleware returns the chain result and logs one elapsed-time DEBUG record.

    :param sample_event: The stub event instance.
    :type sample_event: object
    :param caplog: Pytest log-capture fixture.
    :type caplog: pytest.LogCaptureFixture
    '''

    # Capture DEBUG-level records.
    caplog.set_level(logging.DEBUG)

    # Build the middleware and a next_fn returning a sentinel result.
    middleware = TimingMiddleware()
    next_fn = lambda: 'result'

    # Execute the middleware around the chain.
    result = middleware(sample_event, {}, next_fn)

    # Assert the chain result is returned unchanged.
    assert result == 'result'

    # Assert a single DEBUG elapsed-time record reported the completion.
    timing_records = [
        r for r in caplog.records
        if r.levelno == logging.DEBUG and 'SampleEvent' in r.getMessage()
    ]
    assert len(timing_records) == 1
    assert re.search(r'completed in \d+\.\d{2}ms', timing_records[0].getMessage())


# ** test: timing_middleware_failure
def test_timing_middleware_failure(sample_event: object, caplog):
    '''
    Test that TimingMiddleware logs an elapsed-time DEBUG record and re-raises on failure.

    :param sample_event: The stub event instance.
    :type sample_event: object
    :param caplog: Pytest log-capture fixture.
    :type caplog: pytest.LogCaptureFixture
    '''

    # Capture DEBUG-level records.
    caplog.set_level(logging.DEBUG)

    # Build the middleware and a next_fn that raises.
    middleware = TimingMiddleware()

    def next_fn():
        raise ValueError('boom')

    # Execute and assert the original exception propagates unaltered.
    with pytest.raises(ValueError, match='boom'):
        middleware(sample_event, {}, next_fn)

    # Assert a single DEBUG elapsed-time record reported the failure.
    timing_records = [
        r for r in caplog.records
        if r.levelno == logging.DEBUG and 'SampleEvent' in r.getMessage()
    ]
    assert len(timing_records) == 1
    assert re.search(r'raised after \d+\.\d{2}ms', timing_records[0].getMessage())
