"""Tests for Tiferet Tester Domain Models"""

# *** imports

# ** app
from tiferet.domain import (
    AggregateTesterObject as _AggregateTesterObject,
    DomainTesterObject as _DomainTesterObject,
    TesterObject as _TesterObject,
    TransferObjectTesterObject as _TransferObjectTesterObject,
    Verification,
)
from tiferet.domain.error import ErrorMessage
from tiferet.mappers.error import (
    ErrorAggregate,
    ErrorConfigObject,
)

# *** tests

# ** test: tester_object_derives_expected_data_and_target_type
def test_tester_object_derives_expected_data_and_target_type() -> None:
    '''
    Test that TesterObject defaults expected_data to sample_data and resolves
    its target class.
    '''

    # Construct a base tester with the required discriminator.
    tester = _TesterObject(
        type='domain',
        id='domain.ErrorMessage',
        module_path='tiferet.domain.error',
        class_name='ErrorMessage',
        sample_data={
            'lang': 'en_US',
            'text': 'An error occurred.',
        },
    )

    # Assert expected data is derived and the target class resolves.
    assert tester.expected_data == tester.sample_data
    assert tester.get_target_type() is ErrorMessage

# ** test: tester_variants_default_their_discriminators_and_resolve_targets
def test_tester_variants_default_their_discriminators_and_resolve_targets() -> None:
    '''
    Test that each tester variant fixes its type discriminator and exposes its
    declared target class.
    '''

    # Construct one tester for each variant.
    domain_tester = _DomainTesterObject(
        id='domain.ErrorMessage',
        module_path='tiferet.domain.error',
        class_name='ErrorMessage',
    )
    aggregate_tester = _AggregateTesterObject(
        id='aggregate.ErrorAggregate',
        module_path='tiferet.mappers.error',
        class_name='ErrorAggregate',
    )
    transfer_tester = _TransferObjectTesterObject(
        id='transfer_object.ErrorConfigObject',
        module_path='tiferet.mappers.error',
        class_name='ErrorConfigObject',
        aggregate_module_path='tiferet.mappers.error',
        aggregate_class_name='ErrorAggregate',
    )

    # Assert every variant selects its fixed discriminator.
    assert domain_tester.type == 'domain'
    assert aggregate_tester.type == 'aggregate'
    assert transfer_tester.type == 'transfer_object'

    # Assert target class resolution for the aggregate and transfer variants.
    assert aggregate_tester.get_target_type() is ErrorAggregate
    assert transfer_tester.get_target_type() is ErrorConfigObject
    assert transfer_tester.get_aggregate_type() is ErrorAggregate

# ** test: verification_constructs_with_optional_message_default
def test_verification_constructs_with_optional_message_default() -> None:
    '''
    Test that Verification retains its predicate and source while defaulting
    its optional message to None.
    '''

    # Construct a verification around a deferred outcome predicate.
    predicate = lambda outcome: outcome == 3
    verification = Verification(
        predicate=predicate,
        source=3,
    )

    # Assert the domain model preserves every declared field.
    assert verification.predicate is predicate
    assert verification.source == 3
    assert verification.message is None
