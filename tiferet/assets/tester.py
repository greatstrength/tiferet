"""Tiferet Tester Default Assets"""

# *** imports

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

# ** constant: repo_error_config_repository_tester_id
REPO_ERROR_CONFIG_REPOSITORY_TESTER_ID = 'repo.ErrorConfigRepository'

# ** constant: context_request_context_tester_id
CONTEXT_REQUEST_CONTEXT_TESTER_ID = 'context.RequestContext'

# *** constants (data)

# ** constant: domain_error_message_tester_data
DOMAIN_ERROR_MESSAGE_TESTER_DATA = create_default_tester_data(
    type='domain',
    module_path='tiferet.domain.error',
    class_name='ErrorMessage',
    sample_data={
        'lang': 'en_US',
        'text': 'An error occurred.',
    },
    equality_fields=[
        'lang',
        'text',
    ],
    description_cases=[
        ('format', (), 'An error occurred.'),
    ],
)

# ** constant: aggregate_error_tester_data
AGGREGATE_ERROR_TESTER_DATA = create_default_tester_data(
    type='aggregate',
    module_path='tiferet.mappers.error',
    class_name='ErrorAggregate',
    sample_data={
        'id': 'TEST_ERROR',
        'name': 'Test Error',
        'message': [
            {
                'lang': 'en_US',
                'text': 'An error occurred.',
            },
        ],
    },
    equality_fields=[
        'id',
        'name',
        'error_code',
    ],
    set_attribute_params=[
        ('name', 'Updated Error', None),
        ('invalid_attribute', 'value', 'INVALID_MODEL_ATTRIBUTE'),
    ],
)

# ** constant: transfer_object_error_tester_data
TRANSFER_OBJECT_ERROR_TESTER_DATA = create_default_tester_data(
    type='transfer_object',
    module_path='tiferet.mappers.error',
    class_name='ErrorConfigObject',
    sample_data=AGGREGATE_ERROR_TESTER_DATA['sample_data'],
    equality_fields=[
        'id',
        'name',
        'error_code',
    ],
    aggregate_module_path='tiferet.mappers.error',
    aggregate_class_name='ErrorAggregate',
    aggregate_sample_data=AGGREGATE_ERROR_TESTER_DATA['sample_data'],
)

# ** constant: service_event_get_error_tester_data
SERVICE_EVENT_GET_ERROR_TESTER_DATA = create_default_tester_data(
    type='service_event',
    module_path='tiferet.events.error',
    class_name='GetError',
    sample_data={
    },
    equality_fields=[
    ],
    dependencies={
        'error_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'ErrorService',
        },
    },
    sample_kwargs={
        'id': 'TEST_ERROR',
    },
    required_params=[
    ],
    service_attr='error_service',
    not_found_error_code=ERROR_NOT_FOUND_ID,
)

# ** constant: repo_error_config_repository_tester_data
REPO_ERROR_CONFIG_REPOSITORY_TESTER_DATA = create_default_tester_data(
    type='repo',
    module_path='tiferet.repos.error',
    class_name='ErrorConfigRepository',
    sample_data={
    },
    equality_fields=[
        'id',
        'name',
    ],
    config_parameter='error_config',
    aggregate_module_path='tiferet.mappers.error',
    aggregate_class_name='ErrorAggregate',
    aggregate_sample_data={
        'id': 'NEW_ERROR_CODE',
        'name': 'New Error',
        'message': [
            {
                'lang': 'en',
                'text': 'A new error occurred',
            },
            {
                'lang': 'es',
                'text': 'Ocurrió un nuevo error',
            },
        ],
    },
    exists_cases=[
        ('TEST_ERROR_CODE', True),
        ('TEST_FORMATTED_ERROR_CODE', True),
        ('MISSING_ERROR_CODE', False),
    ],
    get_cases=[
        ('TEST_ERROR_CODE', {
            'id': 'TEST_ERROR_CODE',
            'name': 'Test Error',
        }),
        ('TEST_FORMATTED_ERROR_CODE', {
            'id': 'TEST_FORMATTED_ERROR_CODE',
            'name': 'Test Formatted Error',
        }),
        ('MISSING_ERROR_CODE', None),
    ],
    list_ids=[
        'TEST_ERROR_CODE',
        'TEST_FORMATTED_ERROR_CODE',
    ],
    delete_ids=[
        'TEST_FORMATTED_ERROR_CODE',
    ],
)

# ** constant: context_request_context_tester_data
CONTEXT_REQUEST_CONTEXT_TESTER_DATA = create_default_tester_data(
    type='context',
    module_path='tiferet.contexts.request',
    class_name='RequestContext',
    sample_data={
        'session_id': 'test-session',
        'feature_id': 'test.feature',
    },
    equality_fields=[
    ],
    domain_module_path='tiferet.domain.request',
    domain_class_name='Request',
    from_domain_cases=[
        {
            'data': {
                'session_id': 'test-session',
                'feature_id': 'test.feature',
            },
        },
    ],
    domain_type_cases=[
        {
            'declares': True,
        },
    ],
    for_domain_cases=[
        {
            'domain_module_path': 'tiferet.domain.request',
            'domain_class_name': 'Request',
            'context_module_path': 'tiferet.contexts.request',
            'context_class_name': 'RequestContext',
        },
    ],
)

# ** constant: default_tester_app_session_data
DEFAULT_TESTER_APP_SESSION_DATA = create_default_app_session_data(
    'Tester',
    description='Default built-in test-harness application session',
)

# *** constants (groups)

# ** constant: core_default_testers
CORE_DEFAULT_TESTERS = {
    DOMAIN_ERROR_MESSAGE_TESTER_ID: DOMAIN_ERROR_MESSAGE_TESTER_DATA,
    AGGREGATE_ERROR_TESTER_ID: AGGREGATE_ERROR_TESTER_DATA,
    TRANSFER_OBJECT_ERROR_TESTER_ID: TRANSFER_OBJECT_ERROR_TESTER_DATA,
    SERVICE_EVENT_GET_ERROR_TESTER_ID: SERVICE_EVENT_GET_ERROR_TESTER_DATA,
    REPO_ERROR_CONFIG_REPOSITORY_TESTER_ID: REPO_ERROR_CONFIG_REPOSITORY_TESTER_DATA,
    CONTEXT_REQUEST_CONTEXT_TESTER_ID: CONTEXT_REQUEST_CONTEXT_TESTER_DATA,
}

# ** constant: core_default_tester_sessions
CORE_DEFAULT_TESTER_SESSIONS = {
    TIFERET_TESTER_ID: DEFAULT_TESTER_APP_SESSION_DATA,
}
