"""Tiferet Tester Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.domain import ModelError
from tiferet.mappers import TesterAggregate as ComponentTester
from tiferet.mappers.error import ErrorAggregate
from tiferet.mappers.tester import TesterConfigObject

# *** constants

# ** constant: domain_tester_data
DOMAIN_TESTER_DATA = {
    'id': 'domain.ErrorMessage',
    'type': 'domain',
    'module_path': 'tiferet.domain.error',
    'class_name': 'ErrorMessage',
    'sample_data': {'lang': 'en_US', 'text': 'Test'},
    'equality_fields': ['lang', 'text'],
    'description_cases': [],
}

# ** constant: aggregate_tester_data
AGGREGATE_TESTER_DATA = {
    'id': 'aggregate.ErrorAggregate',
    'type': 'aggregate',
    'module_path': 'tiferet.mappers.error',
    'class_name': 'ErrorAggregate',
    'sample_data': {'id': 'TEST', 'name': 'Test', 'message': []},
    'equality_fields': ['id', 'name'],
    'set_attribute_params': [],
}

# ** constant: transfer_object_tester_data
TRANSFER_OBJECT_TESTER_DATA = {
    'id': 'transfer_object.ErrorConfigObject',
    'type': 'transfer_object',
    'module_path': 'tiferet.mappers.error',
    'class_name': 'ErrorConfigObject',
    'sample_data': {'id': 'TEST', 'name': 'Test', 'message': []},
    'equality_fields': ['id', 'name'],
    'aggregate_module_path': 'tiferet.mappers.error',
    'aggregate_class_name': 'ErrorAggregate',
    'aggregate_sample_data': {'id': 'TEST', 'name': 'Test', 'message': []},
}

# ** constant: tester_equality_fields
TESTER_EQUALITY_FIELDS = [
    'id',
    'type',
    'module_path',
    'class_name',
    'sample_data',
]

# *** tests

# ** tester: TestTesterAggregate
@use_tester(
    type='aggregate',
    target_cls=ComponentTester,
    sample_data=AGGREGATE_TESTER_DATA,
    equality_fields=TESTER_EQUALITY_FIELDS,
    set_attribute_params=[
        ('module_path', 'tiferet.mappers.error', None),
    ],
)
class TestTesterAggregate:
    '''Tests generic and tester-specific aggregate behavior.'''

    # * method: test_new
    def test_new(self, test_ctx):
        '''Verify aggregate construction against declared expected data.'''

        test_ctx.assert_new()

    # * method: test_set_attribute
    def test_set_attribute(self, test_ctx):
        '''Verify declared set_attribute cases.'''

        test_ctx.assert_set_attribute()

    # * test: retarget
    def test_retarget(self, test_ctx) -> None:
        '''Test that retarget updates both target reference fields.'''

        target = test_ctx.make_target()
        target.retarget('tiferet.mappers.error', 'ErrorAggregate')
        assert target.module_path == 'tiferet.mappers.error'
        assert target.class_name == 'ErrorAggregate'

    # * test: set_sample_data
    def test_set_sample_data(self, test_ctx) -> None:
        '''Test last-write-wins sample data merging.'''

        target = test_ctx.make_target()
        target.set_sample_data({'name': 'Updated', 'extra': True})
        assert target.sample_data['name'] == 'Updated'
        assert target.sample_data['extra'] is True

    # * test: resolve_target_type
    def test_resolve_target_type(self, test_ctx) -> None:
        '''Test import-based configured target resolution.'''

        target = test_ctx.make_target()
        target.retarget('tiferet.mappers.error', 'ErrorAggregate')
        assert target.resolve_target_type() is ErrorAggregate

# ** tester: TestTesterConfigObject
@use_tester(
    type='transfer_object',
    target_cls=TesterConfigObject,
    aggregate_cls=ComponentTester,
    sample_data=DOMAIN_TESTER_DATA,
    aggregate_sample_data=DOMAIN_TESTER_DATA,
    equality_fields=TESTER_EQUALITY_FIELDS,
)
class TestTesterConfigObject:
    '''Tests generic tester config mapping behavior.'''

    # * method: test_map
    def test_map(self, test_ctx):
        '''Verify transfer construction and mapping to the declared aggregate.'''

        test_ctx.assert_map()

    # * method: test_from_model
    def test_from_model(self, test_ctx):
        '''Verify aggregate conversion to the declared transfer-object type.'''

        test_ctx.assert_from_model()

    # * method: test_round_trip
    def test_round_trip(self, test_ctx):
        '''Verify aggregate conversion through the transfer object and back.'''

        test_ctx.assert_round_trip()

# ** test: tester_config_object_dispatch
@pytest.mark.parametrize(
    'data',
    [
        DOMAIN_TESTER_DATA,
        AGGREGATE_TESTER_DATA,
        TRANSFER_OBJECT_TESTER_DATA,
    ],
)
def test_tester_config_object_dispatch(data) -> None:
    '''Test class-owned dispatch validates every supported type.'''

    config_object = ComponentTester.build_config_object(data)
    assert isinstance(config_object, TesterConfigObject)

# ** test: tester_config_object_invalid_type
def test_tester_config_object_rejects_invalid_type() -> None:
    '''Test unknown discriminator values raise a model defect.'''

    with pytest.raises(ModelError) as exc_info:
        ComponentTester.build_config_object(
            {**DOMAIN_TESTER_DATA, 'type': 'unknown'},
        )
    assert exc_info.value.error_code == 'INVALID_TESTER_TYPE'
