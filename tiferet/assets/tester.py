"""Tiferet Tester Default Assets"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from .core import (
    create_default_app_session_data,
    create_default_tester_data,
)
from .error import ERROR_NOT_FOUND_ID

# *** constants (ids)

# ** constant: domain_error_message_tester_id
DOMAIN_ERROR_MESSAGE_TESTER_ID = 'domain.ErrorMessage'

# ** constant: aggregate_error_tester_id
AGGREGATE_ERROR_TESTER_ID = 'aggregate.ErrorAggregate'

# ** constant: transfer_object_error_tester_id
TRANSFER_OBJECT_ERROR_TESTER_ID = 'transfer_object.ErrorConfigObject'

# ** constant: service_event_get_error_tester_id
SERVICE_EVENT_GET_ERROR_TESTER_ID = 'service_event.GetError'

# ** constant: tiferet_tester_id
TIFERET_TESTER_ID = 'tester'

# *** constants (data)

# ** constant: domain_error_message_tester_data
DOMAIN_ERROR_MESSAGE_TESTER_DATA = create_default_tester_data(
    'domain',
    'tiferet.domain.error',
    'ErrorMessage',
    {
        'lang': 'en_US',
        'text': 'An error occurred.',
    },
    [
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

# ** constant: aggregate_error_tester_data
AGGREGATE_ERROR_TESTER_DATA = create_default_tester_data(
    'aggregate',
    'tiferet.mappers.error',
    'ErrorAggregate',
    {
        'id': 'TEST_ERROR',
        'name': 'Test Error',
        'message': [
            {
                'lang': 'en_US',
                'text': 'An error occurred.',
            },
        ],
    },
    [
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
            'INVALID_MODEL_ATTRIBUTE',
        ),
    ],
)

# ** constant: transfer_object_error_tester_data
TRANSFER_OBJECT_ERROR_TESTER_DATA = create_default_tester_data(
    'transfer_object',
    'tiferet.mappers.error',
    'ErrorConfigObject',
    {
        'id': 'TEST_ERROR',
        'name': 'Test Error',
        'message': [
            {
                'lang': 'en_US',
                'text': 'An error occurred.',
            },
        ],
    },
    [
        'id',
        'name',
        'error_code',
    ],
    aggregate_module_path='tiferet.mappers.error',
    aggregate_class_name='ErrorAggregate',
    aggregate_sample_data={
        'id': 'TEST_ERROR',
        'name': 'Test Error',
        'message': [
            {
                'lang': 'en_US',
                'text': 'An error occurred.',
            },
        ],
    },
)

# ** constant: service_event_get_error_tester_data
SERVICE_EVENT_GET_ERROR_TESTER_DATA = create_default_tester_data(
    'service_event',
    'tiferet.events.error',
    'GetError',
    {},
    [],
    dependencies={
        'error_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'ErrorService',
        },
    },
    sample_kwargs={
        'id': 'TEST_ERROR',
    },
    required_params=[],
    service_attr='error_service',
    not_found_error_code=ERROR_NOT_FOUND_ID,
)

# ** constant: default_tester_app_session_data
DEFAULT_TESTER_APP_SESSION_DATA = create_default_app_session_data(
    'Tester',
    description='Default built-in test-harness application session',
)

# *** constants (groups)

# ** constant: core_default_testers
CORE_DEFAULT_TESTERS: Dict[str, Dict[str, Any]] = {
    DOMAIN_ERROR_MESSAGE_TESTER_ID: DOMAIN_ERROR_MESSAGE_TESTER_DATA,
    AGGREGATE_ERROR_TESTER_ID: AGGREGATE_ERROR_TESTER_DATA,
    TRANSFER_OBJECT_ERROR_TESTER_ID: TRANSFER_OBJECT_ERROR_TESTER_DATA,
    SERVICE_EVENT_GET_ERROR_TESTER_ID: SERVICE_EVENT_GET_ERROR_TESTER_DATA,
}

# ** constant: core_default_tester_sessions
CORE_DEFAULT_TESTER_SESSIONS: Dict[str, Dict[str, Any]] = {
    TIFERET_TESTER_ID: DEFAULT_TESTER_APP_SESSION_DATA,
}
