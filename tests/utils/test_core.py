"""Tiferet Utils Core Tests"""

# *** imports

# ** core
import logging
import re

# ** infra
import pytest

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.interfaces.middleware import MiddlewareService
from tiferet.utils.core import CacheMiddleware, LoggingMiddleware, TimingMiddleware

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

# *** testers

# ** tester: test_logging_middleware
@use_tester(
    target_cls=LoggingMiddleware,
)
class TestLoggingMiddleware:
    '''LoggingMiddleware binder coverage via GenericTesterContext.'''

    # * test: conformance
    def test_conformance(self, test_ctx) -> None:
        '''
        Test that LoggingMiddleware conforms to MiddlewareService and resolves the default logger.
        '''

        # Assert class-level conformance to the MiddlewareService contract.
        assert issubclass(LoggingMiddleware, MiddlewareService)

        # Instantiate with the default logger_id.
        logging_mw = test_ctx.make_target()

        # Assert instance-level conformance to the MiddlewareService contract.
        assert isinstance(logging_mw, MiddlewareService)

        # Assert the default logger_id resolves a logger named 'root'.
        # NOTE: logging.getLogger('root') returns a named logger called 'root' — a child of
        # the true process root logger (logging.getLogger() with no name), not the root
        # logger itself; records still propagate to the root handlers.
        assert logging_mw.logger.name == 'root'

    # * test: resolves_named_logger
    def test_resolves_named_logger(self, test_ctx) -> None:
        '''
        Test that a custom logger_id resolves a logger whose name matches.
        '''

        # Instantiate with a custom logger_id.
        logging_mw = test_ctx.make_target(data={'logger_id': 'tiferet.test'})

        # Assert the resolved logger carries the requested name.
        assert logging_mw.logger.name == 'tiferet.test'

    # * test: forwards_nonempty_kwargs
    def test_forwards_nonempty_kwargs(self, test_ctx, sample_event: object) -> None:
        '''
        Test that LoggingMiddleware returns the chain result unchanged and leaves a non-empty kwargs dict intact.

        :param sample_event: The stub event instance.
        :type sample_event: object
        '''

        # Build the utility and a next_fn returning a sentinel result.
        logging_mw = test_ctx.make_target()
        next_fn = lambda: 'result'

        # Provide a non-empty kwargs dict that the middleware must forward without inspecting or mutating.
        kwargs = {'a': 1}

        # Assert the utility returns the chain result unchanged.
        assert logging_mw(sample_event, kwargs, next_fn) == 'result'

        # Assert the kwargs dict was neither consumed nor mutated.
        assert kwargs == {'a': 1}

    # * test: success
    def test_success(self, test_ctx, sample_event: object, caplog) -> None:
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
        middleware = test_ctx.make_target()
        next_fn = lambda: 'result'

        # Execute the middleware around the chain.
        result = middleware(sample_event, {}, next_fn)

        # Assert the chain result is returned unchanged.
        assert result == 'result'

        # Assert DEBUG records were emitted before and after execution.
        debug_messages = [r.getMessage() for r in caplog.records if r.levelno == logging.DEBUG]
        assert 'Executing SampleEvent' in debug_messages
        assert 'Completed SampleEvent' in debug_messages

    # * test: failure
    def test_failure(self, test_ctx, sample_event: object, caplog) -> None:
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
        middleware = test_ctx.make_target()

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

# ** tester: test_timing_middleware
@use_tester(
    target_cls=TimingMiddleware,
)
class TestTimingMiddleware:
    '''TimingMiddleware binder coverage via GenericTesterContext.'''

    # * test: conformance
    def test_conformance(self, test_ctx) -> None:
        '''
        Test that TimingMiddleware conforms to MiddlewareService and resolves the default logger.
        '''

        # Assert class-level conformance to the MiddlewareService contract.
        assert issubclass(TimingMiddleware, MiddlewareService)

        # Instantiate with the default logger_id.
        timing_mw = test_ctx.make_target()

        # Assert instance-level conformance to the MiddlewareService contract.
        assert isinstance(timing_mw, MiddlewareService)

        # Assert the default logger_id resolves a logger named 'root'.
        assert timing_mw.logger.name == 'root'

    # * test: resolves_named_logger
    def test_resolves_named_logger(self, test_ctx) -> None:
        '''
        Test that a custom logger_id resolves a logger whose name matches.
        '''

        # Instantiate with a custom logger_id.
        timing_mw = test_ctx.make_target(data={'logger_id': 'tiferet.test'})

        # Assert the resolved logger carries the requested name.
        assert timing_mw.logger.name == 'tiferet.test'

    # * test: forwards_nonempty_kwargs
    def test_forwards_nonempty_kwargs(self, test_ctx, sample_event: object) -> None:
        '''
        Test that TimingMiddleware returns the chain result unchanged and leaves a non-empty kwargs dict intact.

        :param sample_event: The stub event instance.
        :type sample_event: object
        '''

        # Build the utility and a next_fn returning a sentinel result.
        timing_mw = test_ctx.make_target()
        next_fn = lambda: 'result'

        # Provide a non-empty kwargs dict that the middleware must forward without inspecting or mutating.
        kwargs = {'a': 1}

        # Assert the utility returns the chain result unchanged.
        assert timing_mw(sample_event, kwargs, next_fn) == 'result'

        # Assert the kwargs dict was neither consumed nor mutated.
        assert kwargs == {'a': 1}

    # * test: success
    def test_success(self, test_ctx, sample_event: object, caplog) -> None:
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
        middleware = test_ctx.make_target()
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

    # * test: failure
    def test_failure(self, test_ctx, sample_event: object, caplog) -> None:
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
        middleware = test_ctx.make_target()

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

# ** tester: test_cache_middleware
@use_tester(
    target_cls=CacheMiddleware,
)
class TestCacheMiddleware:
    '''CacheMiddleware binder coverage via GenericTesterContext.'''

    # * test: conformance
    def test_conformance(self, test_ctx) -> None:
        '''
        Test that CacheMiddleware conforms to MiddlewareService and defaults its loader to None.
        '''

        # Assert class-level conformance to the MiddlewareService contract.
        assert issubclass(CacheMiddleware, MiddlewareService)

        # Instantiate without a loader and assert instance-level conformance.
        middleware = test_ctx.make_target()
        assert isinstance(middleware, MiddlewareService)

        # Assert the loader defaults to None.
        assert middleware.load_cache is None

    # * test: injects_snapshot
    def test_injects_snapshot(self, test_ctx, sample_event: object) -> None:
        '''
        Test that CacheMiddleware injects the load_cache snapshot as the 'cache' kwarg.

        :param sample_event: The stub event instance.
        :type sample_event: object
        '''

        # Build a middleware whose loader yields a known snapshot dict.
        snapshot = {'answer': 42}
        middleware = test_ctx.make_target(data={'load_cache': lambda: snapshot})

        # Provide a kwargs dict without a cache entry and a sentinel next_fn.
        kwargs = {'a': 1}
        result = middleware(sample_event, kwargs, lambda: 'result')

        # Assert the chain result is returned unchanged.
        assert result == 'result'

        # Assert the snapshot was injected under the 'cache' key, leaving others intact.
        assert kwargs['cache'] == snapshot
        assert kwargs['a'] == 1

    # * test: skips_when_cache_present
    def test_skips_when_cache_present(self, test_ctx, sample_event: object) -> None:
        '''
        Test that CacheMiddleware does not overwrite an existing 'cache' kwarg.

        :param sample_event: The stub event instance.
        :type sample_event: object
        '''

        # Build a middleware whose loader would raise if it were ever invoked.
        def _loader():
            raise AssertionError('load_cache must not be called when cache is present')

        middleware = test_ctx.make_target(data={'load_cache': _loader})

        # Provide a kwargs dict that already carries a cache value.
        existing = {'existing': True}
        kwargs = {'cache': existing}
        result = middleware(sample_event, kwargs, lambda: 'result')

        # Assert the chain result is returned and the existing cache is preserved.
        assert result == 'result'
        assert kwargs['cache'] is existing

    # * test: noop_without_loader
    def test_noop_without_loader(self, test_ctx, sample_event: object) -> None:
        '''
        Test that CacheMiddleware is a transparent no-op when no loader is supplied.

        :param sample_event: The stub event instance.
        :type sample_event: object
        '''

        # Build a middleware without a loader.
        middleware = test_ctx.make_target()

        # Provide a kwargs dict with no cache entry.
        kwargs = {'a': 1}
        result = middleware(sample_event, kwargs, lambda: 'result')

        # Assert the chain result is returned and no cache key was injected.
        assert result == 'result'
        assert 'cache' not in kwargs
