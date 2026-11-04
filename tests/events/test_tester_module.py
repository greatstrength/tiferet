"""Tiferet Test Module Event Tests"""

# *** imports

# ** core
import importlib
import inspect
import sys

# ** infra
import pytest

# ** app
from tiferet.assets import TiferetError
from tiferet.events.core import DomainEvent
from tiferet.events.tester_module import TestEvent, TestModuleEvent
from tiferet.events.tester_phase import CheckEvent

# *** classes

# ** class: reserved_event
class ReservedEvent(DomainEvent):
    '''
    An event whose execute takes the reserved handle names as keywords.
    '''

    # * init
    def __init__(self, service=None):
        '''
        Store the optional dependency.

        :param service: The optional dependency.
        :type service: Any
        '''

        # Store the dependency.
        self.service = service

    # * method: execute
    def execute(self, **kwargs):
        '''
        Return the dependency and the kwargs it was given.

        :param kwargs: The event arguments.
        :type kwargs: dict
        :return: The dependency and received arguments.
        :rtype: dict
        '''

        # Return a copy so the test can see what execute received.
        return {'service': self.service, 'kwargs': dict(kwargs)}

# ** class: failing_event
class FailingEvent(DomainEvent):
    '''
    An event that raises a TiferetError.
    '''

    # * method: execute
    def execute(self, **kwargs):
        '''
        Raise a catalogued error.

        :param kwargs: The event arguments.
        :type kwargs: dict
        '''

        # Raise the error.
        self.raise_error('TEST_ERROR', 'An error has occurred.')

# *** tests

# ** test: test_event_is_base_of_tester_events
def test_event_is_base_of_tester_events():
    '''
    TestEvent extends DomainEvent and is the base of the tester events.
    '''

    # The tester bases extend TestEvent.
    assert issubclass(TestEvent, DomainEvent)
    assert issubclass(TestModuleEvent, TestEvent)
    assert issubclass(CheckEvent, TestEvent)
    assert TestEvent.__test__ is False

# ** test: test_event_modules_import_in_either_order
@pytest.mark.parametrize('order', [
    ('tiferet.events.tester_phase', 'tiferet.events.tester_module'),
    ('tiferet.events.tester_module', 'tiferet.events.tester_phase'),
])
def test_event_modules_import_in_either_order(order):
    '''
    tester_phase and tester_module import cleanly in either order.

    :param order: The import order.
    :type order: tuple
    '''

    # Drop both modules and import them fresh in the given order.
    saved = {name: sys.modules.pop(name) for name in order if name in sys.modules}
    try:
        for name in order:
            importlib.import_module(name)
    finally:
        sys.modules.update(saved)

# ** test: test_handle_test_signature
def test_handle_test_signature():
    '''
    event_cls is positional-only and the controls are keyword-only.
    '''

    # Read the parameter kinds.
    parameters = inspect.signature(TestEvent.handle_test).parameters
    assert parameters['event_cls'].kind == inspect.Parameter.POSITIONAL_ONLY
    for name in ('dependencies', 'middleware', 'execute_kwargs'):
        assert parameters[name].kind == inspect.Parameter.KEYWORD_ONLY
        assert parameters[name].default is None

# ** test: test_handle_test_reserved_keys_reach_execute
def test_handle_test_reserved_keys_reach_execute():
    '''
    Keys named dependencies, middleware, and event_cls reach execute unchanged.
    '''

    # The caller's mapping holds all three reserved names.
    execute_kwargs = {
        'dependencies': ['a'],
        'middleware': ['b'],
        'event_cls': 'c',
    }
    snapshot = dict(execute_kwargs)
    result = TestEvent.handle_test(ReservedEvent, execute_kwargs=execute_kwargs)

    # All three keys pass through, and the caller's mapping is unchanged.
    assert result['kwargs'] == snapshot
    assert execute_kwargs == snapshot

# ** test: test_handle_test_mapping_not_mutated_by_middleware
def test_handle_test_mapping_not_mutated_by_middleware():
    '''
    A middleware that mutates kwargs does not mutate the caller's mapping.
    '''

    # The middleware adds a key before continuing.
    def add_key(event, kwargs, next_fn):
        kwargs['added'] = True
        return next_fn()

    execute_kwargs = {'id': 'x'}
    result = TestEvent.handle_test(
        ReservedEvent,
        middleware=[add_key],
        execute_kwargs=execute_kwargs,
    )
    assert result['kwargs'] == {'id': 'x', 'added': True}
    assert execute_kwargs == {'id': 'x'}

# ** test: test_handle_test_defaults
def test_handle_test_defaults():
    '''
    With no controls, handle_test matches DomainEvent.handle.
    '''

    # Omitted dependencies and kwargs normalise to empty.
    assert TestEvent.handle_test(ReservedEvent) == DomainEvent.handle(ReservedEvent)
    assert TestEvent.handle_test(ReservedEvent) == {'service': None, 'kwargs': {}}

# ** test: test_handle_test_matches_handle_with_middleware
def test_handle_test_matches_handle_with_middleware():
    '''
    handle_test builds and wraps the event exactly as DomainEvent.handle does.
    '''

    # Record the order and the event each middleware sees.
    def make_recorder(label, log):
        def middleware(event, kwargs, next_fn):
            log.append((label, type(event).__name__, event.service, dict(kwargs)))
            return next_fn()
        return middleware

    handle_log = []
    handle_result = DomainEvent.handle(
        ReservedEvent,
        dependencies={'service': 'svc'},
        middleware=[make_recorder('outer', handle_log), make_recorder('inner', handle_log)],
        id='x',
    )
    test_log = []
    test_result = TestEvent.handle_test(
        ReservedEvent,
        dependencies={'service': 'svc'},
        middleware=[make_recorder('outer', test_log), make_recorder('inner', test_log)],
        execute_kwargs={'id': 'x'},
    )
    assert test_result == handle_result
    assert test_log == handle_log
    assert test_log[0][0] == 'outer'

# ** test: test_handle_test_error_handling
def test_handle_test_error_handling():
    '''
    An event error propagates and a middleware can intercept it, as with handle.
    '''

    # Without middleware the error propagates.
    with pytest.raises(TiferetError) as exc_info:
        TestEvent.handle_test(FailingEvent)
    assert exc_info.value.error_code == 'TEST_ERROR'

    # A middleware intercepts the error.
    def intercept(event, kwargs, next_fn):
        try:
            return next_fn()
        except TiferetError as error:
            return error.error_code

    assert TestEvent.handle_test(FailingEvent, middleware=[intercept]) == 'TEST_ERROR'
    assert DomainEvent.handle(FailingEvent, middleware=[intercept]) == 'TEST_ERROR'
