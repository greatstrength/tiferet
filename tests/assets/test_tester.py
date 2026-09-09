"""Tests for Tiferet Tester Assets"""

# *** imports

# ** app
from tiferet.assets.tester import (
    CORE_DEFAULT_TESTERS,
    CORE_DEFAULT_TESTER_SESSIONS,
    DEFAULT_TESTER_CONFIG_FILE,
    TESTER_CONFIG_ID,
    TESTER_SERVICE_ID,
    TIFERET_TESTER_ID,
)
from tiferet.contexts.tester import (
    AggregateTesterContext,
    DomainTesterContext,
    TransferObjectTesterContext,
)
from tiferet.domain import (
    AggregateTesterObject,
    DomainTesterObject,
    INVALID_MODEL_ATTRIBUTE_ID,
    TransferObjectTesterObject,
)
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

# ** test: error_message_domain_tester
def test_error_message_domain_tester() -> None:
    '''Test domain tester construction assertions against ErrorMessage.'''

    # Bind a domain tester and assert construction.
    context = DomainTesterContext.from_domain(
        DomainTesterObject(
            id='domain.ErrorMessage',
            module_path=ErrorMessage.__module__,
            class_name=ErrorMessage.__name__,
            sample_data=ERROR_MESSAGE_DATA,
            equality_fields=['lang', 'text'],
        ),
    )
    context.assert_new()
    context.assert_description()

# ** test: error_message_description_tester
def test_error_message_description_tester() -> None:
    '''Test optional description assertions against ErrorMessage.format.'''

    # Bind a domain tester with one description case.
    context = DomainTesterContext.from_domain(
        DomainTesterObject(
            id='domain.ErrorMessage',
            module_path=ErrorMessage.__module__,
            class_name=ErrorMessage.__name__,
            sample_data=ERROR_MESSAGE_DATA,
            equality_fields=['lang', 'text'],
            description_cases=[
                ('format', (), 'An error occurred.'),
            ],
        ),
    )
    context.assert_new()
    context.assert_description()

# ** test: error_aggregate_tester
def test_error_aggregate_tester() -> None:
    '''Test aggregate tester construction assertions against ErrorAggregate.'''

    # Bind an aggregate tester without mutation cases.
    context = AggregateTesterContext.from_domain(
        AggregateTesterObject(
            id='aggregate.ErrorAggregate',
            module_path=ErrorAggregate.__module__,
            class_name=ErrorAggregate.__name__,
            sample_data=ERROR_DATA,
            equality_fields=['id', 'name', 'error_code'],
        ),
    )
    context.assert_new()
    context.assert_set_attribute()

# ** test: error_aggregate_set_attribute_tester
def test_error_aggregate_set_attribute_tester() -> None:
    '''Test optional set_attribute assertions against ErrorAggregate.'''

    # Bind an aggregate tester with valid and invalid mutation cases.
    context = AggregateTesterContext.from_domain(
        AggregateTesterObject(
            id='aggregate.ErrorAggregate',
            module_path=ErrorAggregate.__module__,
            class_name=ErrorAggregate.__name__,
            sample_data=ERROR_DATA,
            equality_fields=['id', 'name', 'error_code'],
            set_attribute_params=[
                ('name', 'Updated Error', None),
                ('invalid_attribute', 'value', INVALID_MODEL_ATTRIBUTE_ID),
            ],
        ),
    )
    context.assert_new()
    context.assert_set_attribute()

# ** test: error_config_object_tester
def test_error_config_object_tester() -> None:
    '''Test transfer-object tester assertions against ErrorConfigObject.'''

    # Bind a transfer-object tester and assert mapping behavior.
    context = TransferObjectTesterContext.from_domain(
        TransferObjectTesterObject(
            id='transfer_object.ErrorConfigObject',
            module_path=ErrorConfigObject.__module__,
            class_name=ErrorConfigObject.__name__,
            sample_data=ERROR_DATA,
            equality_fields=['id', 'name', 'error_code'],
            aggregate_module_path=ErrorAggregate.__module__,
            aggregate_class_name=ErrorAggregate.__name__,
            aggregate_sample_data=ERROR_DATA,
        ),
    )
    context.assert_map()
    context.assert_from_model()
    context.assert_round_trip()

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

    # Assert the tester session declares its own default service and config.
    session = CORE_DEFAULT_TESTER_SESSIONS[TIFERET_TESTER_ID]
    assert session['name'] == 'Tester'
    assert session['description'] == 'Default built-in test-harness application session'
    assert session['constants'] == {
        TESTER_CONFIG_ID: DEFAULT_TESTER_CONFIG_FILE,
    }
    assert session['services'][0]['service_id'] == TESTER_SERVICE_ID
