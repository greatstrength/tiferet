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
    Test that every tester decorator adds make_target and the target fixture
    for the target shape its assertions need.
    '''

    # Decorate one class for each tester variant.
    @create_domain_tester(
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
    class DomainTester:
        pass

    @create_aggregate_tester(
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
    class AggregateTester:
        pass

    @create_transfer_object_tester(
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
    class TransferObjectTester:
        pass

    # Assert every decorated class exposes its universal target construction API.
    assert isinstance(DomainTester().make_target(), ErrorMessage)
    assert isinstance(AggregateTester().make_target(), ErrorAggregate)
    assert isinstance(TransferObjectTester().make_target(), ErrorAggregate)
    assert hasattr(DomainTester, 'target')
    assert hasattr(AggregateTester, 'target')
    assert hasattr(TransferObjectTester, 'target')

# ** test: tester_decorator_preserves_explicit_members
def test_tester_decorator_preserves_explicit_members() -> None:
    '''
    Test that a decorator preserves an explicitly declared generated-method
    override on the consumer's own class.
    '''

    # Decorate a class that supplies its own construction assertion.
    @create_domain_tester(
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
    class OverrideTester:

        # * test: test_new
        def test_new(self) -> str:
            '''Return a sentinel proving this explicit method was retained.'''

            return 'consumer override'

    # Assert the decorator retained the consumer's own member.
    assert OverrideTester().test_new() == 'consumer override'
    assert hasattr(OverrideTester, 'target')
