"""Tiferet Interfaces Middleware Contract Tests"""

# *** imports

# ** core
import inspect

# ** infra
import pytest

# ** app
from tiferet.interfaces.core import Service
from tiferet.interfaces.middleware import MiddlewareService

# *** fixtures

# ** fixture: passthrough_middleware
@pytest.fixture
def passthrough_middleware() -> MiddlewareService:
    '''
    A concrete synchronous middleware that records invocation and continues the chain.

    :return: A concrete MiddlewareService subclass instance.
    :rtype: MiddlewareService
    '''

    # Define a concrete middleware that wraps and continues the chain.
    class PassthroughMiddleware(MiddlewareService):

        def __init__(self):
            self.calls = []

        def __call__(self, event, kwargs, next_fn):
            self.calls.append((event, kwargs))
            return next_fn()

    # Return an instance of the concrete middleware.
    return PassthroughMiddleware()

# *** tests

# ** test: middleware_service_is_service
def test_middleware_service_is_service():
    '''
    Test that MiddlewareService is a Service subclass.
    '''

    # Verify MiddlewareService derives from the Service base class.
    assert issubclass(MiddlewareService, Service)

# ** test: middleware_service_has_call
def test_middleware_service_has_call():
    '''
    Test that MiddlewareService defines __call__ with the expected signature.
    '''

    # Verify the method exists.
    assert hasattr(MiddlewareService, '__call__')

    # Inspect the signature.
    sig = inspect.signature(MiddlewareService.__call__)
    params = list(sig.parameters.keys())

    # Verify parameter names.
    assert params == ['self', 'event', 'kwargs', 'next_fn']

# ** test: middleware_service_call_is_abstract
def test_middleware_service_call_is_abstract():
    '''
    Test that __call__ is marked as abstract.
    '''

    # Verify __call__ is in the abstract methods set.
    assert '__call__' in MiddlewareService.__abstractmethods__

# ** test: middleware_service_cannot_instantiate
def test_middleware_service_cannot_instantiate():
    '''
    Test that MiddlewareService cannot be instantiated directly.
    '''

    # Verify direct instantiation raises a TypeError due to the abstract method.
    with pytest.raises(TypeError):
        MiddlewareService()

# ** test: middleware_service_concrete_wraps_and_continues
def test_middleware_service_concrete_wraps_and_continues(passthrough_middleware: MiddlewareService):
    '''
    Test that a concrete middleware invokes next_fn and returns its result.

    :param passthrough_middleware: A concrete synchronous middleware instance.
    :type passthrough_middleware: MiddlewareService
    '''

    # Arrange a sentinel event and kwargs plus a next_fn returning a known result.
    event = object()
    kwargs = {'a': 1}
    next_fn = lambda: 'result'

    # Execute the middleware.
    result = passthrough_middleware(event, kwargs, next_fn)

    # Verify the chain continued and the result propagated.
    assert result == 'result'
    assert passthrough_middleware.calls == [(event, kwargs)]
