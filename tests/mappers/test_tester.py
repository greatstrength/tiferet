"""Tiferet Tester Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.assets import TiferetError
from tiferet.assets.error import INVALID_TESTER_TYPE_ID
from tiferet.contexts.tester import (
    create_aggregate_tester,
    create_transfer_object_tester,
)
from tiferet.mappers import TesterAggregate as ComponentTester
from tiferet.mappers.error import ErrorAggregate
from tiferet.mappers.tester import (
    AggregateTesterConfigObject,
    DomainTesterConfigObject,
    TransferObjectTesterConfigObject,
)

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
@create_aggregate_tester(
    aggregate_cls=ComponentTester,
    sample_data=AGGREGATE_TESTER_DATA,
    equality_fields=TESTER_EQUALITY_FIELDS,
    set_attribute_params=[
        ('module_path', 'tiferet.mappers.error', None),
    ],
)
class TestTesterAggregate:
    '''Tests generic and tester-specific aggregate behavior.'''

    # * test: retarget
    def test_retarget(self, target) -> None:
        '''Test that retarget updates both target reference fields.

        :param target: The generated aggregate fixture.
        :type target: ComponentTester
        '''

        # Retarget the aggregate and verify both reference parts change.
        target.retarget('tiferet.mappers.error', 'ErrorAggregate')
        assert target.module_path == 'tiferet.mappers.error'
        assert target.class_name == 'ErrorAggregate'

    # * test: set_sample_data
    def test_set_sample_data(self, target) -> None:
        '''Test last-write-wins sample data merging.

        :param target: The generated aggregate fixture.
        :type target: ComponentTester
        '''

        # Merge a replacement and new value.
        target.set_sample_data({'name': 'Updated', 'extra': True})
        assert target.sample_data['name'] == 'Updated'
        assert target.sample_data['extra'] is True

    # * test: resolve_target_type
    def test_resolve_target_type(self, target) -> None:
        '''Test import-based configured target resolution.

        :param target: The generated aggregate fixture.
        :type target: ComponentTester
        '''

        # Point at the target mapper class and resolve it.
        target.retarget('tiferet.mappers.error', 'ErrorAggregate')
        assert target.resolve_target_type() is ErrorAggregate

# ** tester: TestDomainTesterConfigObject
@create_transfer_object_tester(
    transfer_cls=DomainTesterConfigObject,
    aggregate_cls=ComponentTester,
    sample_data=DOMAIN_TESTER_DATA,
    aggregate_sample_data=DOMAIN_TESTER_DATA,
    equality_fields=TESTER_EQUALITY_FIELDS,
)
class TestDomainTesterConfigObject:
    '''Tests generic domain tester config mapping behavior.'''

# ** tester: TestAggregateTesterConfigObject
@create_transfer_object_tester(
    transfer_cls=AggregateTesterConfigObject,
    aggregate_cls=ComponentTester,
    sample_data=AGGREGATE_TESTER_DATA,
    aggregate_sample_data=AGGREGATE_TESTER_DATA,
    equality_fields=TESTER_EQUALITY_FIELDS,
)
class TestAggregateTesterConfigObject:
    '''Tests generic aggregate tester config mapping behavior.'''

# ** tester: TestTransferObjectTesterConfigObject
@create_transfer_object_tester(
    transfer_cls=TransferObjectTesterConfigObject,
    aggregate_cls=ComponentTester,
    sample_data=TRANSFER_OBJECT_TESTER_DATA,
    aggregate_sample_data=TRANSFER_OBJECT_TESTER_DATA,
    equality_fields=TESTER_EQUALITY_FIELDS,
)
class TestTransferObjectTesterConfigObject:
    '''Tests generic transfer-object tester config mapping behavior.'''

# ** test: tester_config_object_dispatch
@pytest.mark.parametrize(
    'data, expected_type',
    [
        (DOMAIN_TESTER_DATA, DomainTesterConfigObject),
        (AGGREGATE_TESTER_DATA, AggregateTesterConfigObject),
        (TRANSFER_OBJECT_TESTER_DATA, TransferObjectTesterConfigObject),
    ],
)
def test_tester_config_object_dispatch(data, expected_type) -> None:
    '''Test class-owned dispatch selects the matching config object variant.

    :param data: Raw tester configuration data.
    :type data: dict
    :param expected_type: The expected config object type.
    :type expected_type: type
    '''

    # Build the matching config object through the aggregate dispatcher.
    config_object = ComponentTester.build_config_object(data)
    assert isinstance(config_object, expected_type)

# ** test: tester_config_object_invalid_type
def test_tester_config_object_rejects_invalid_type() -> None:
    '''Test unknown discriminator values raise the defined structured error.'''

    # Invoke the dispatcher with an unknown discriminator.
    with pytest.raises(TiferetError) as exc_info:
        ComponentTester.build_config_object(
            {**DOMAIN_TESTER_DATA, 'type': 'unknown'},
        )

    # Assert the public invalid-type error is raised.
    assert exc_info.value.error_code == INVALID_TESTER_TYPE_ID