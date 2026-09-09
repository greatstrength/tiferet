"""Tests for Tiferet Tester Domain Models"""

# *** imports

# ** app
from tiferet.domain import (
    TesterObject as _TesterObject,
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
    assert tester.expected_data == tester.sample_data
    assert tester.get_target_type() is ErrorMessage

# ** test: tester_object_optional_fields_and_aggregate_target
def test_tester_object_optional_fields_and_aggregate_target() -> None:
    '''Test optional variant fields default and transfer aggregate resolution.'''

    domain_tester = _TesterObject(
        type='domain',
        id='domain.ErrorMessage',
        module_path='tiferet.domain.error',
        class_name='ErrorMessage',
    )
    aggregate_tester = _TesterObject(
        type='aggregate',
        id='aggregate.ErrorAggregate',
        module_path='tiferet.mappers.error',
        class_name='ErrorAggregate',
    )
    transfer_tester = _TesterObject(
        type='transfer_object',
        id='transfer_object.ErrorConfigObject',
        module_path='tiferet.mappers.error',
        class_name='ErrorConfigObject',
        aggregate_module_path='tiferet.mappers.error',
        aggregate_class_name='ErrorAggregate',
    )
    assert domain_tester.description_cases == []
    assert aggregate_tester.set_attribute_params == []
    assert aggregate_tester.get_target_type() is ErrorAggregate
    assert transfer_tester.get_target_type() is ErrorConfigObject
    assert transfer_tester.get_aggregate_type() is ErrorAggregate

# ** test: verification_constructs_with_optional_message_default
def test_verification_constructs_with_optional_message_default() -> None:
    '''
    Test that Verification retains its predicate and source while defaulting
    its optional message to None.
    '''

    predicate = lambda outcome: outcome == 3
    verification = Verification(
        predicate=predicate,
        source=3,
    )
    assert verification.predicate is predicate
    assert verification.source == 3
    assert verification.message is None
