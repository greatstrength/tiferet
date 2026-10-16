"""Tiferet Interfaces Check Tests"""

# *** imports

# ** core
import inspect

# ** infra
import pytest

# ** app
from tiferet import use_tester
from tiferet.interfaces.core import Service
from tiferet.interfaces.tester_check import CheckService

# *** testers

# ** tester: test_check_service
@use_tester(
    type='generic',
    target_cls=CheckService,
)
class TestCheckService:
    '''
    Tests for the CheckService contract.
    '''

    # * test: contract
    def test_contract(self, test_ctx):
        '''
        Assert CheckService abstract names and parameter lists.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Lock the abstract names through the generic harness.
        target = test_ctx.make_target()
        test_ctx.assert_contract(target=target)
        abstracts = CheckService.__abstractmethods__
        expected = [
            'equal',
            'codes',
            'role_dump',
            'mapper_contract',
        ]
        assert abstracts
        assert set(abstracts) == set(expected)

        # Read each method's declared parameter names in order.
        expected_params = {
            'equal': ['self', 'actual', 'expected'],
            'codes': ['self', 'actual', 'expected'],
            'role_dump': ['self', 'dumped', 'exclude'],
            'mapper_contract': ['self', 'exclude', 'source'],
        }
        for name, params in expected_params.items():
            signature = inspect.signature(getattr(CheckService, name))
            assert list(signature.parameters.keys()) == params

    # * test: subclasses_service
    def test_subclasses_service(self):
        '''
        Assert CheckService is a Service subclass.
        '''

        # Ask whether CheckService is a subclass of Service.
        assert issubclass(CheckService, Service) is True

    # * test: direct_construction_raises
    def test_direct_construction_raises(self):
        '''
        Assert constructing CheckService directly raises TypeError.
        '''

        # Construct CheckService with no arguments.
        with pytest.raises(TypeError) as exc_info:
            CheckService()
        assert 'CheckService' in str(exc_info.value)
