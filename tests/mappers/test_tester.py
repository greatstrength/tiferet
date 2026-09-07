"""Tiferet Tester Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.assets import TiferetError
from tiferet.assets.error import INVALID_TESTER_TYPE_ID
from tiferet.mappers import TesterAggregate
from tiferet.mappers.error import ErrorAggregate
from tiferet.mappers.tester import (
    AggregateTesterConfigObject,
    DomainTesterConfigObject,
    TransferObjectTesterConfigObject,
    build_tester_config_object,
)

# *** constants

# ** constant: aggregate_tester_data
AGGREGATE_TESTER_DATA = {
    'id': 'aggregate.ErrorAggregate',
    'type': 'aggregate',
    'module_path': 'tiferet.mappers.error',
    'class_name': 'ErrorAggregate',
    'sample_data': {'id': 'TEST', 'name': 'Test', 'message': []},
    'set_attribute_params': [],
}

# *** tests

# ** test: tester_aggregate_mutations
def test_tester_aggregate_mutations_and_target_resolution():
    '''Test tester mutation methods and live target resolution.'''

    # Construct a tester aggregate with aggregate-specific data.
    tester = TesterAggregate(**AGGREGATE_TESTER_DATA)
    tester.retarget('tiferet.mappers.error', 'ErrorAggregate')
    tester.set_sample_data({'name': 'Updated', 'extra': True})

    # Assert mutations merge and the configured class resolves.
    assert tester.sample_data == {
        'id': 'TEST',
        'name': 'Updated',
        'message': [],
        'extra': True,
    }
    assert tester.resolve_target_type() is ErrorAggregate

    # Verify set_attribute dispatches sample data to its merge method.
    tester.set_attribute('sample_data', {'id': 'UPDATED'})
    assert tester.sample_data['id'] == 'UPDATED'
    assert tester.sample_data['extra'] is True


# ** test: build_tester_config_object_dispatch
@pytest.mark.parametrize(
    'type, expected_type, extra_data',
    [
        ('domain', DomainTesterConfigObject, {'description_cases': []}),
        ('aggregate', AggregateTesterConfigObject, {'set_attribute_params': []}),
        (
            'transfer_object',
            TransferObjectTesterConfigObject,
            {
                'aggregate_module_path': 'tiferet.mappers.error',
                'aggregate_class_name': 'ErrorAggregate',
                'aggregate_sample_data': {},
            },
        ),
    ],
)
def test_build_tester_config_object_dispatches_variants(
        type,
        expected_type,
        extra_data,
    ):
    '''Test discriminator-based config-object dispatch.'''

    # Build the variant-specific configuration object.
    config_object = build_tester_config_object(
        {
            **AGGREGATE_TESTER_DATA,
            'type': type,
            **extra_data,
        },
    )

    # Assert the expected config type and aggregate mapping.
    assert isinstance(config_object, expected_type)
    assert isinstance(config_object.map(), TesterAggregate)


# ** test: build_tester_config_object_invalid_type
def test_build_tester_config_object_rejects_invalid_type():
    '''Test that unknown tester types raise the defined structured error.'''

    # Invoke the dispatcher with an unknown discriminator.
    with pytest.raises(TiferetError) as exc_info:
        build_tester_config_object({**AGGREGATE_TESTER_DATA, 'type': 'unknown'})

    # Assert the public invalid-type error is raised.
    assert exc_info.value.error_code == INVALID_TESTER_TYPE_ID
