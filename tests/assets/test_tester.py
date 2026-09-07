"""Tests for Tiferet Tester Assets"""

# *** imports

# ** app
from tiferet.contexts.tester import (
    create_aggregate_tester,
    create_domain_tester,
    create_transfer_object_tester,
)
from tiferet.assets.tester import (
    CORE_DEFAULT_TESTERS,
    CORE_DEFAULT_TESTER_SESSIONS,
    TIFERET_TESTER_ID,
)
from tiferet.domain import INVALID_MODEL_ATTRIBUTE_ID
from tiferet.domain.error import ErrorMessage
from tiferet.mappers.error import (
    ErrorAggregate,
    ErrorConfigObject,
)

# *** constants

# ** constant: error_message_data
ERROR_MESSAGE_DATA = {
    'lang': 'en_US',
    'text': 'An error occurred.',
}

# ** constant: error_data
ERROR_DATA = {
    'id': 'TEST_ERROR',
    'name': 'Test Error',
    'message': [
        {
            'lang': 'en_US',
            'text': 'An error occurred.',
        },
    ],
}

# *** tests

# ** tester: TestErrorMessage
@create_domain_tester(
    domain_cls=ErrorMessage,
    sample_data=ERROR_MESSAGE_DATA,
    equality_fields=[
        'lang',
        'text',
    ],
)
class TestErrorMessage:
    pass

# ** tester: TestErrorMessageDescription
@create_domain_tester(
    domain_cls=ErrorMessage,
    sample_data=ERROR_MESSAGE_DATA,
    equality_fields=[
        'lang',
        'text',
    ],
    description_cases=[
        (
            'format',
            (),
            'An error occurred.',
        ),
    ],
)
class TestErrorMessageDescription:
    pass

# ** tester: TestErrorAggregate
@create_aggregate_tester(
    aggregate_cls=ErrorAggregate,
    sample_data=ERROR_DATA,
    equality_fields=[
        'id',
        'name',
        'error_code',
    ],
)
class TestErrorAggregate:
    pass

# ** tester: TestErrorAggregateSetAttribute
@create_aggregate_tester(
    aggregate_cls=ErrorAggregate,
    sample_data=ERROR_DATA,
    equality_fields=[
        'id',
        'name',
        'error_code',
    ],
    set_attribute_params=[
        (
            'name',
            'Updated Error',
            None,
        ),
        (
            'invalid_attribute',
            'value',
            INVALID_MODEL_ATTRIBUTE_ID,
        ),
    ],
)
class TestErrorAggregateSetAttribute:
    pass

# ** tester: TestErrorConfigObject
@create_transfer_object_tester(
    transfer_cls=ErrorConfigObject,
    aggregate_cls=ErrorAggregate,
    sample_data=ERROR_DATA,
    aggregate_sample_data=ERROR_DATA,
    equality_fields=[
        'id',
        'name',
        'error_code',
    ],
)
class TestErrorConfigObject:
    pass

# ** test: factory_classes_attach_only_declared_optional_assertions
def test_factory_classes_attach_only_declared_optional_assertions() -> None:
    '''
    Test that optional factory assertions are omitted rather than self-skipped
    when no cases are declared.
    '''

    # Assert domain-description methods follow the declared cases.
    assert hasattr(TestErrorMessage, 'test_new')
    assert not hasattr(TestErrorMessage, 'test_description')
    assert hasattr(TestErrorMessageDescription, 'test_description')

    # Assert aggregate mutation methods follow the declared cases.
    assert hasattr(TestErrorAggregate, 'test_new')
    assert not hasattr(TestErrorAggregate, 'test_set_attribute')
    assert hasattr(TestErrorAggregateSetAttribute, 'test_set_attribute')

# ** test: default_tester_catalog_and_session_are_data_only
def test_default_tester_catalog_and_session_are_data_only() -> None:
    '''
    Test that the tester catalog carries all three variant shapes and the
    built-in tester application session is keyed by its framework id.
    '''

    # Assert the catalog provides each supported tester variant.
    assert {data['type'] for data in CORE_DEFAULT_TESTERS.values()} == {
        'domain',
        'aggregate',
        'transfer_object',
    }

    # Assert the tester session uses its built-in identifier and data shape.
    assert CORE_DEFAULT_TESTER_SESSIONS[TIFERET_TESTER_ID] == {
        'name': 'Tester',
        'description': 'Default built-in test-harness application session',
    }
