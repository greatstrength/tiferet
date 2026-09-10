"""Tiferet Interfaces Middleware Contract Tests"""

# *** imports

# ** core
import inspect

# ** infra
import pytest

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.interfaces.core import Service
from tiferet.interfaces.middleware import MiddlewareService

# *** testers

# ** tester: test_middleware_service
@use_tester(
    target_cls=MiddlewareService,
)
class TestMiddlewareService:
    '''MiddlewareService ABC lock, signature, and passthrough wrap.'''

    # * fixture: passthrough_middleware
    @pytest.fixture
    def passthrough_middleware(self) -> MiddlewareService:
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

    # * test: contract
    def test_contract(self, test_ctx) -> None:
        '''Lock the ABC abstract method names.'''

        test_ctx.assert_contract()

    # * test: is_service
    def test_is_service(self) -> None:
        '''
        Test that MiddlewareService is a Service subclass.
        '''

        # Verify MiddlewareService derives from the Service base class.
        assert issubclass(MiddlewareService, Service)

    # * test: has_call
    def test_has_call(self) -> None:
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

    # * test: call_is_abstract
    def test_call_is_abstract(self) -> None:
        '''
        Test that __call__ is marked as abstract.
        '''

        # Verify __call__ is in the abstract methods set.
        assert '__call__' in MiddlewareService.__abstractmethods__

    # * test: cannot_instantiate
    def test_cannot_instantiate(self) -> None:
        '''
        Test that MiddlewareService cannot be instantiated directly.
        '''

        # Verify direct instantiation raises a TypeError due to the abstract method.
        with pytest.raises(TypeError):
            MiddlewareService()

    # * test: concrete_wraps_and_continues
    def test_concrete_wraps_and_continues(
            self,
            passthrough_middleware: MiddlewareService,
        ) -> None:
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
