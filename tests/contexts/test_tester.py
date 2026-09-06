"""Tests for Tiferet Tester Context Composition"""

# *** imports

# ** app
from tiferet.contexts.tester import (
    create_aggregate_tester,
    create_domain_tester,
    create_transfer_object_tester,
)
from tiferet.domain.error import ErrorMessage
from tiferet.mappers.error import (
    ErrorAggregate,
    ErrorConfigObject,
)

# *** tests

# ** test: generated_tester_classes_construct_targets
def test_generated_tester_classes_construct_targets() -> None:
    '''
    Test that every tester factory returns a class exposing make_target and the
    target fixture for the target shape its assertions need.
    '''

    # Compose one class for each tester variant.
    domain_tester = create_domain_tester(
        domain_cls=ErrorMessage,
        sample_data={
            'lang': 'en_US',
            'text': 'An error occurred.',
        },
        equality_fields=[
            'lang',
            'text',
        ],
    )
    aggregate_tester = create_aggregate_tester(
        aggregate_cls=ErrorAggregate,
        sample_data={
            'id': 'TEST_ERROR',
            'name': 'Test Error',
        },
        equality_fields=[
            'id',
            'name',
        ],
    )
    transfer_tester = create_transfer_object_tester(
        transfer_cls=ErrorConfigObject,
        aggregate_cls=ErrorAggregate,
        sample_data={
            'id': 'TEST_ERROR',
            'name': 'Test Error',
        },
        aggregate_sample_data={
            'id': 'TEST_ERROR',
            'name': 'Test Error',
        },
    )

    # Assert every generated class exposes its universal target construction API.
    assert isinstance(domain_tester().make_target(), ErrorMessage)
    assert isinstance(aggregate_tester().make_target(), ErrorAggregate)
    assert isinstance(transfer_tester().make_target(), ErrorAggregate)
    assert hasattr(domain_tester, 'target')
    assert hasattr(aggregate_tester, 'target')
    assert hasattr(transfer_tester, 'target')
