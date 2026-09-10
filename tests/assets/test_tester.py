"""Tests for Tiferet Tester Assets"""

# *** imports

# ** app
from tiferet.assets.tester import (
    CORE_DEFAULT_TESTERS,
    CORE_DEFAULT_TESTER_SESSIONS,
    SERVICE_EVENT_GET_ERROR_TESTER_ID,
    REPO_ERROR_CONFIG_REPOSITORY_TESTER_ID,
    TIFERET_TESTER_ID,
)
from tiferet.blueprints.tester import use_tester
from tiferet.assets.error import ERROR_NOT_FOUND_ID
from tiferet.domain import INVALID_MODEL_ATTRIBUTE_ID, TesterObject
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
@use_tester(
    type='domain',
    target_cls=ErrorMessage,
    sample_data=ERROR_MESSAGE_DATA,
    equality_fields=['lang', 'text'],
)
def test_error_message_domain_tester(test_ctx) -> None:
    '''Test domain tester construction assertions against ErrorMessage.'''

    test_ctx.assert_new()
    test_ctx.assert_description()

# ** test: error_message_description_tester
@use_tester(
    type='domain',
    target_cls=ErrorMessage,
    sample_data=ERROR_MESSAGE_DATA,
    equality_fields=['lang', 'text'],
    description_cases=[
        ('format', (), 'An error occurred.'),
    ],
)
def test_error_message_description_tester(test_ctx) -> None:
    '''Test optional description assertions against ErrorMessage.format.'''

    test_ctx.assert_new()
    test_ctx.assert_description()

# ** test: error_aggregate_tester
@use_tester(
    type='aggregate',
    target_cls=ErrorAggregate,
    sample_data=ERROR_DATA,
    equality_fields=['id', 'name', 'error_code'],
)
def test_error_aggregate_tester(test_ctx) -> None:
    '''Test aggregate tester construction assertions against ErrorAggregate.'''

    test_ctx.assert_new()
    test_ctx.assert_set_attribute()

# ** test: error_aggregate_set_attribute_tester
@use_tester(
    type='aggregate',
    target_cls=ErrorAggregate,
    sample_data=ERROR_DATA,
    equality_fields=['id', 'name', 'error_code'],
    set_attribute_params=[
        ('name', 'Updated Error', None),
        ('invalid_attribute', 'value', INVALID_MODEL_ATTRIBUTE_ID),
    ],
)
def test_error_aggregate_set_attribute_tester(test_ctx) -> None:
    '''Test optional set_attribute assertions against ErrorAggregate.'''

    test_ctx.assert_new()
    test_ctx.assert_set_attribute()

# ** test: error_config_object_tester
@use_tester(
    type='transfer_object',
    target_cls=ErrorConfigObject,
    aggregate_cls=ErrorAggregate,
    sample_data=ERROR_DATA,
    equality_fields=['id', 'name', 'error_code'],
    aggregate_sample_data=ERROR_DATA,
)
def test_error_config_object_tester(test_ctx) -> None:
    '''Test transfer-object tester assertions against ErrorConfigObject.'''

    test_ctx.assert_map()
    test_ctx.assert_from_model()
    test_ctx.assert_round_trip()

# ** test: default_tester_catalog_and_session_are_data_only
def test_default_tester_catalog_and_session_are_data_only() -> None:
    '''
    Test that the tester catalog carries all three variant shapes and the
    built-in tester application session is keyed by its framework id.
    '''

    assert {data['type'] for data in CORE_DEFAULT_TESTERS.values()} == {
        'domain',
        'aggregate',
        'transfer_object',
        'service_event',
        'repo',
    }
    session = CORE_DEFAULT_TESTER_SESSIONS[TIFERET_TESTER_ID]
    assert session['name'] == 'Tester'
    assert session['description'] == 'Default built-in test-harness application session'
    assert 'constants' not in session
    assert 'services' not in session

# ** test: get_error_service_event_catalog_round_trips
def test_get_error_service_event_catalog_round_trips() -> None:
    '''Test the GetError catalog row validates and maps without type errors.'''

    data = {
        **CORE_DEFAULT_TESTERS[SERVICE_EVENT_GET_ERROR_TESTER_ID],
        'id': SERVICE_EVENT_GET_ERROR_TESTER_ID,
    }
    tester = TesterObject.model_validate(data)
    assert tester.type == 'service_event'
    assert tester.class_name == 'GetError'
    assert tester.not_found_error_code == ERROR_NOT_FOUND_ID
    assert tester.service_attr == 'error_service'

# ** test: error_config_repository_catalog_round_trips
def test_error_config_repository_catalog_round_trips() -> None:
    '''Test the ErrorConfigRepository catalog row validates as type repo.'''

    data = {
        **CORE_DEFAULT_TESTERS[REPO_ERROR_CONFIG_REPOSITORY_TESTER_ID],
        'id': REPO_ERROR_CONFIG_REPOSITORY_TESTER_ID,
    }
    tester = TesterObject.model_validate(data)
    assert tester.type == 'repo'
    assert tester.class_name == 'ErrorConfigRepository'
    assert tester.config_parameter == 'error_config'
    assert tester.aggregate_class_name == 'ErrorAggregate'
