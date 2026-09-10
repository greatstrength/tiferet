"""Tests for Tiferet Tester Domain Models"""

# *** imports

# ** app
from tiferet.domain import (
    ServiceDependency,
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

# ** test: tester_object_accepts_event_types_and_optional_fields
def test_tester_object_accepts_event_types_and_optional_fields() -> None:
    '''Test domain_event and service_event types plus optional event fields.'''

    domain_event = _TesterObject(
        type='domain_event',
        id='domain_event.ListErrors',
        module_path='tiferet.events.error',
        class_name='ListErrors',
    )
    service_event = _TesterObject(
        type='service_event',
        id='service_event.GetError',
        module_path='tiferet.events.error',
        class_name='GetError',
        dependencies={
            'error_service': {
                'module_path': 'tiferet.interfaces',
                'class_name': 'ErrorService',
            },
        },
        sample_kwargs={'id': 'TEST_ERROR'},
        required_params=[],
        service_attr='error_service',
        not_found_error_code='ERROR_NOT_FOUND',
    )
    assert domain_event.sample_kwargs == {}
    assert domain_event.required_params == []
    assert domain_event.service_attr is None
    assert domain_event.not_found_error_code is None
    assert domain_event.not_found_kwargs == {}
    assert service_event.dependencies['error_service'].class_name == 'ErrorService'
    assert isinstance(
        service_event.dependencies['error_service'],
        ServiceDependency,
    )
    assert service_event.get_target_type().__name__ == 'GetError'

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
