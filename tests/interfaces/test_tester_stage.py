"""Tiferet Interfaces Stage Tests"""

# *** imports

# ** core
import inspect

# ** infra
import pytest

# ** app
from tiferet import use_tester
from tiferet.interfaces.core import Service
from tiferet.interfaces.tester_stage import StageService

# *** testers

# ** tester: test_stage_service
@use_tester(
    type='generic',
    target_cls=StageService,
)
class TestStageService:
    '''
    Tests for the StageService contract.
    '''

    # * test: contract
    def test_contract(self, test_ctx):
        '''
        Assert StageService subclasses Service, its abstract names and parameter lists, and that it cannot be constructed.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Run the generic contract check on the target.
        target = test_ctx.make_target()
        test_ctx.assert_contract(target=target)
        assert issubclass(StageService, Service) is True

        # Lock the abstract names.
        assert set(StageService.__abstractmethods__) == {
            'arrange',
            'close',
            'path',
            'write',
            'read',
            'exists',
            'records',
            'message',
        }

        # Read each abstract method's parameter names in order.
        expected_params = {
            'arrange': ['self'],
            'close': ['self'],
            'path': ['self', 'parts'],
            'write': ['self', 'name', 'text'],
            'read': ['self', 'name'],
            'exists': ['self', 'name'],
            'records': ['self'],
            'message': ['self', 'level', 'index'],
        }
        for name, params in expected_params.items():
            signature = inspect.signature(getattr(StageService, name))
            assert list(signature.parameters.keys()) == params

        # Construct StageService with no arguments.
        with pytest.raises(TypeError):
            StageService()
