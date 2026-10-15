"""Tiferet Interfaces Yaml Tests"""

# *** imports

# ** core
import inspect

# ** infra
import pytest

# ** app
from tiferet import use_tester
from tiferet.interfaces.file import FileService
from tiferet.interfaces.yaml import ANCHOR_VALUE_ABSENT, YamlService

# *** tests

# ** test: anchor_value_absent_identity
def test_anchor_value_absent_identity():
    '''
    Assert ANCHOR_VALUE_ABSENT is a unique sentinel object.
    '''

    # Compare the sentinel to itself and to a newly constructed object.
    other = object()
    assert ANCHOR_VALUE_ABSENT is ANCHOR_VALUE_ABSENT
    assert ANCHOR_VALUE_ABSENT is not other

# *** testers

# ** tester: test_yaml_service
@use_tester(
    type='generic',
    target_cls=YamlService,
)
class TestYamlService:
    '''
    Tests for the YamlService contract.
    '''

    # * test: contract
    def test_contract(self, test_ctx):
        '''
        Assert YamlService abstract names and parameter lists.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Lock the abstract names through the generic harness.
        target = test_ctx.make_target()
        test_ctx.assert_contract(target=target)
        abstracts = YamlService.__abstractmethods__
        expected = [
            'load_mapping',
            'save_mapping',
            'read_anchored',
            'write_anchored',
            'list_anchors',
            'get_anchor',
            'set_anchor',
            'remove_anchor',
            'rename_anchor',
        ]
        assert abstracts
        for name in expected:
            assert name in abstracts

        # Read each method's declared parameter names in order.
        expected_params = {
            'load_mapping': ['self', 'path'],
            'save_mapping': ['self', 'path', 'data'],
            'read_anchored': ['self', 'path'],
            'write_anchored': ['self', 'path', 'text'],
            'list_anchors': ['self', 'path'],
            'get_anchor': ['self', 'path', 'name'],
            'set_anchor': ['self', 'path', 'name', 'value', 'key_path'],
            'remove_anchor': ['self', 'path', 'name'],
            'rename_anchor': ['self', 'path', 'name', 'new_name'],
        }
        for name, params in expected_params.items():
            signature = inspect.signature(getattr(YamlService, name))
            assert list(signature.parameters.keys()) == params

        # The key_path default is null.
        set_anchor_signature = inspect.signature(YamlService.set_anchor)
        assert set_anchor_signature.parameters['key_path'].default is None

    # * test: subclasses_file_service
    def test_subclasses_file_service(self):
        '''
        Assert YamlService is a FileService subclass.
        '''

        # Ask whether YamlService is a subclass of FileService.
        assert issubclass(YamlService, FileService) is True

    # * test: own_namespace_methods
    def test_own_namespace_methods(self):
        '''
        Assert YamlService declares the nine methods in its own namespace.
        '''

        # Read YamlService's own namespace.
        expected = [
            'load_mapping',
            'save_mapping',
            'read_anchored',
            'write_anchored',
            'list_anchors',
            'get_anchor',
            'set_anchor',
            'remove_anchor',
            'rename_anchor',
        ]
        declared = [
            name
            for name in YamlService.__dict__
            if name in expected
        ]
        assert declared == expected
        for name in ('__init__', 'open_file', 'close_file', '__enter__', '__exit__'):
            assert name not in YamlService.__dict__

    # * test: set_anchor_value_default
    def test_set_anchor_value_default(self):
        '''
        Assert set_anchor defaults value to ANCHOR_VALUE_ABSENT.
        '''

        # Read the default bound to value.
        signature = inspect.signature(YamlService.set_anchor)
        assert signature.parameters['value'].default is ANCHOR_VALUE_ABSENT

    # * test: direct_construction_raises
    def test_direct_construction_raises(self):
        '''
        Assert constructing YamlService directly raises TypeError.
        '''

        # Construct YamlService with no arguments.
        with pytest.raises(TypeError) as exc_info:
            YamlService()
        assert 'YamlService' in str(exc_info.value)
