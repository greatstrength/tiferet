"""Tiferet Assets Feature

Provides the default feature workflow definitions for the built-in Tiferet CLI
management application. Each feature maps to a single-step workflow that
invokes the corresponding domain event service.

The blueprint constructs ``Feature`` domain objects from these definitions
at startup — they are not loaded from the consumer's config file.
"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from .core import create_default_feature_data, create_params_schema

# *** constants (ids)

# ** constant: app_add_id
APP_ADD_ID = 'app.add'

# ** constant: app_get_id
APP_GET_ID = 'app.get'

# ** constant: app_list_id
APP_LIST_ID = 'app.list'

# ** constant: app_update_id
APP_UPDATE_ID = 'app.update'

# ** constant: app_set_constants_id
APP_SET_CONSTANTS_ID = 'app.set_constants'

# ** constant: app_set_service_id
APP_SET_SERVICE_ID = 'app.set_service'

# ** constant: app_remove_service_id
APP_REMOVE_SERVICE_ID = 'app.remove_service'

# ** constant: app_remove_id
APP_REMOVE_ID = 'app.remove'

# ** constant: cli_add_command_id
CLI_ADD_COMMAND_ID = 'cli.add_command'

# ** constant: cli_list_commands_id
CLI_LIST_COMMANDS_ID = 'cli.list_commands'

# ** constant: cli_add_argument_id
CLI_ADD_ARGUMENT_ID = 'cli.add_argument'

# ** constant: error_add_id
ERROR_ADD_ID = 'error.add'

# ** constant: error_get_id
ERROR_GET_ID = 'error.get'

# ** constant: error_list_id
ERROR_LIST_ID = 'error.list'

# ** constant: error_rename_id
ERROR_RENAME_ID = 'error.rename'

# ** constant: error_set_message_id
ERROR_SET_MESSAGE_ID = 'error.set_message'

# ** constant: error_remove_message_id
ERROR_REMOVE_MESSAGE_ID = 'error.remove_message'

# ** constant: error_remove_id
ERROR_REMOVE_ID = 'error.remove'

# ** constant: feature_add_id
FEATURE_ADD_ID = 'feature.add'

# ** constant: feature_get_id
FEATURE_GET_ID = 'feature.get'

# ** constant: feature_list_id
FEATURE_LIST_ID = 'feature.list'

# ** constant: feature_remove_id
FEATURE_REMOVE_ID = 'feature.remove'

# ** constant: feature_update_id
FEATURE_UPDATE_ID = 'feature.update'

# ** constant: feature_add_step_id
FEATURE_ADD_STEP_ID = 'feature.add_step'

# ** constant: feature_update_step_id
FEATURE_UPDATE_STEP_ID = 'feature.update_step'

# ** constant: feature_remove_step_id
FEATURE_REMOVE_STEP_ID = 'feature.remove_step'

# ** constant: feature_reorder_step_id
FEATURE_REORDER_STEP_ID = 'feature.reorder_step'

# ** constant: service_add_id
SERVICE_ADD_ID = 'service.add'

# ** constant: service_list_id
SERVICE_LIST_ID = 'service.list'

# ** constant: service_set_default_id
SERVICE_SET_DEFAULT_ID = 'service.set_default'

# ** constant: service_set_dependency_id
SERVICE_SET_DEPENDENCY_ID = 'service.set_dependency'

# ** constant: service_remove_dependency_id
SERVICE_REMOVE_DEPENDENCY_ID = 'service.remove_dependency'

# ** constant: service_remove_id
SERVICE_REMOVE_ID = 'service.remove'

# ** constant: service_set_constants_id
SERVICE_SET_CONSTANTS_ID = 'service.set_constants'

# ** constant: logging_add_formatter_id
LOGGING_ADD_FORMATTER_ID = 'logging.add_formatter'

# ** constant: logging_remove_formatter_id
LOGGING_REMOVE_FORMATTER_ID = 'logging.remove_formatter'

# ** constant: logging_add_handler_id
LOGGING_ADD_HANDLER_ID = 'logging.add_handler'

# ** constant: logging_remove_handler_id
LOGGING_REMOVE_HANDLER_ID = 'logging.remove_handler'

# ** constant: logging_add_logger_id
LOGGING_ADD_LOGGER_ID = 'logging.add_logger'

# ** constant: logging_remove_logger_id
LOGGING_REMOVE_LOGGER_ID = 'logging.remove_logger'

# ** constant: logging_list_id
LOGGING_LIST_ID = 'logging.list'

# *** constants (features)

# ** constant: app_add_data
APP_ADD_DATA = create_default_feature_data(
    'Add App Session',
    'app',
    'add',
    [{'service_id': 'add_app_session_evt', 'name': 'Add app session'}],
    description='Add a new application session configuration.',
    params_schema=create_params_schema(
        id='str',
        name='str',
        module_path='str',
        class_name='str',
        description={'type': 'str', 'required': False},
        logger_id={'type': 'str', 'required': False, 'default': 'default'},
        flags={'type': 'list', 'required': False, 'default': ['default']},
        services={'type': 'list', 'required': False, 'default': []},
        constants={'type': 'dict', 'required': False, 'default': {}},
    ),
)

# ** constant: app_get_data
APP_GET_DATA = create_default_feature_data(
    'Get App Session',
    'app',
    'get',
    [{'service_id': 'get_app_session_evt', 'name': 'Get app session'}],
    description='Retrieve an app session by ID.',
    params_schema=create_params_schema(interface_id='str'),
)

# ** constant: app_list_data
APP_LIST_DATA = create_default_feature_data(
    'List App Sessions',
    'app',
    'list',
    [{'service_id': 'list_app_sessions_evt', 'name': 'List app sessions'}],
    description='List all configured app sessions.',
)

# ** constant: app_update_data
APP_UPDATE_DATA = create_default_feature_data(
    'Update App Session',
    'app',
    'update',
    [{'service_id': 'update_app_session_evt', 'name': 'Update app session'}],
    description='Update a scalar attribute on an app session.',
    params_schema=create_params_schema(id='str', attribute='str'),
)

# ** constant: app_set_constants_data
APP_SET_CONSTANTS_DATA = create_default_feature_data(
    'Set App Constants',
    'app',
    'set_constants',
    [{'service_id': 'set_app_constants_evt', 'name': 'Set app constants'}],
    description='Set or clear constants on an app session.',
    params_schema=create_params_schema(
        id='str',
        constants={'type': 'dict', 'required': False},
    ),
)

# ** constant: app_set_service_data
APP_SET_SERVICE_DATA = create_default_feature_data(
    'Set App Service Dependency',
    'app',
    'set_service',
    [{'service_id': 'set_app_service_dependency_evt', 'name': 'Set app service dependency'}],
    description='Set or update a service dependency on an app session.',
    params_schema=create_params_schema(
        id='str',
        service_id='str',
        module_path='str',
        class_name='str',
        parameters={'type': 'dict', 'required': False},
    ),
)

# ** constant: app_remove_service_data
APP_REMOVE_SERVICE_DATA = create_default_feature_data(
    'Remove App Service Dependency',
    'app',
    'remove_service',
    [{'service_id': 'remove_app_service_dependency_evt', 'name': 'Remove app service dependency'}],
    description='Remove a service dependency from an app session.',
    params_schema=create_params_schema(id='str', service_id='str'),
)

# ** constant: app_remove_data
APP_REMOVE_DATA = create_default_feature_data(
    'Remove App Session',
    'app',
    'remove',
    [{'service_id': 'remove_app_session_evt', 'name': 'Remove app session'}],
    description='Remove an app session by ID.',
    params_schema=create_params_schema(id='str'),
)

# ** constant: cli_add_command_data
CLI_ADD_COMMAND_DATA = create_default_feature_data(
    'Add CLI Command',
    'cli',
    'add_command',
    [{'service_id': 'add_cli_command_evt', 'name': 'Add CLI command'}],
    description='Add a new CLI command definition.',
    params_schema=create_params_schema(
        id='str',
        name='str',
        key='str',
        group_key='str',
        description={'type': 'str', 'required': False},
        arguments={'type': 'list', 'required': False, 'default': []},
    ),
)

# ** constant: cli_list_commands_data
CLI_LIST_COMMANDS_DATA = create_default_feature_data(
    'List CLI Commands',
    'cli',
    'list_commands',
    [{'service_id': 'list_commands_evt', 'name': 'List CLI commands'}],
    description='List all CLI command definitions.',
)

# ** constant: cli_add_argument_data
CLI_ADD_ARGUMENT_DATA = create_default_feature_data(
    'Add CLI Argument',
    'cli',
    'add_argument',
    [{'service_id': 'add_cli_argument_evt', 'name': 'Add CLI argument'}],
    description='Add an argument to an existing CLI command.',
    params_schema=create_params_schema(
        command_id='str',
        description={'type': 'str', 'required': False},
    ),
)

# ** constant: error_add_data
ERROR_ADD_DATA = create_default_feature_data(
    'Add Error',
    'error',
    'add',
    [{'service_id': 'add_error_evt', 'name': 'Add error'}],
    description='Add a new error definition.',
    params_schema=create_params_schema(
        id='str',
        name='str',
        message='str',
        lang={'type': 'str', 'required': False, 'default': 'en_US'},
        additional_messages={'type': 'dict', 'required': False, 'default': {}},
    ),
)

# ** constant: error_get_data
ERROR_GET_DATA = create_default_feature_data(
    'Get Error',
    'error',
    'get',
    [{'service_id': 'get_error_evt', 'name': 'Get error'}],
    description='Retrieve an error by ID.',
    params_schema=create_params_schema(id='str'),
)

# ** constant: error_list_data
ERROR_LIST_DATA = create_default_feature_data(
    'List Errors',
    'error',
    'list',
    [{'service_id': 'list_errors_evt', 'name': 'List errors'}],
    description='List all error definitions.',
)

# ** constant: error_rename_data
ERROR_RENAME_DATA = create_default_feature_data(
    'Rename Error',
    'error',
    'rename',
    [{'service_id': 'rename_error_evt', 'name': 'Rename error'}],
    description='Rename an existing error.',
    params_schema=create_params_schema(id='str', new_name='str'),
)

# ** constant: error_set_message_data
ERROR_SET_MESSAGE_DATA = create_default_feature_data(
    'Set Error Message',
    'error',
    'set_message',
    [{'service_id': 'set_error_message_evt', 'name': 'Set error message'}],
    description='Set or update an error message for a language.',
    params_schema=create_params_schema(
        id='str',
        message='str',
        lang={'type': 'str', 'required': False, 'default': 'en_US'},
    ),
)

# ** constant: error_remove_message_data
ERROR_REMOVE_MESSAGE_DATA = create_default_feature_data(
    'Remove Error Message',
    'error',
    'remove_message',
    [{'service_id': 'remove_error_message_evt', 'name': 'Remove error message'}],
    description='Remove an error message by language.',
    params_schema=create_params_schema(
        id='str',
        lang={'type': 'str', 'required': False, 'default': 'en_US'},
    ),
)

# ** constant: error_remove_data
ERROR_REMOVE_DATA = create_default_feature_data(
    'Remove Error',
    'error',
    'remove',
    [{'service_id': 'remove_error_evt', 'name': 'Remove error'}],
    description='Remove an error definition by ID.',
    params_schema=create_params_schema(id='str'),
)

# ** constant: feature_add_data
FEATURE_ADD_DATA = create_default_feature_data(
    'Add Feature',
    'feature',
    'add',
    [{'service_id': 'add_feature_evt', 'name': 'Add feature'}],
    description='Add a new feature configuration.',
    params_schema=create_params_schema(
        name='str',
        group_id='str',
        feature_key={'type': 'str', 'required': False},
        id={'type': 'str', 'required': False},
        description={'type': 'str', 'required': False},
        steps={'type': 'list', 'required': False},
        log_params={'type': 'dict', 'required': False},
    ),
)

# ** constant: feature_get_data
FEATURE_GET_DATA = create_default_feature_data(
    'Get Feature',
    'feature',
    'get',
    [{'service_id': 'get_feature_evt', 'name': 'Get feature'}],
    description='Retrieve a feature by ID.',
    params_schema=create_params_schema(id='str'),
)

# ** constant: feature_list_data
FEATURE_LIST_DATA = create_default_feature_data(
    'List Features',
    'feature',
    'list',
    [{'service_id': 'list_features_evt', 'name': 'List features'}],
    description='List all features, optionally filtered by group.',
    params_schema=create_params_schema(group_id={'type': 'str', 'required': False}),
)

# ** constant: feature_remove_data
FEATURE_REMOVE_DATA = create_default_feature_data(
    'Remove Feature',
    'feature',
    'remove',
    [{'service_id': 'remove_feature_evt', 'name': 'Remove feature'}],
    description='Remove a feature configuration by ID.',
    params_schema=create_params_schema(id='str'),
)

# ** constant: feature_update_data
FEATURE_UPDATE_DATA = create_default_feature_data(
    'Update Feature',
    'feature',
    'update',
    [{'service_id': 'update_feature_evt', 'name': 'Update feature'}],
    description='Update a feature attribute (name or description).',
    params_schema=create_params_schema(id='str', attribute='str'),
)

# ** constant: feature_add_step_data
FEATURE_ADD_STEP_DATA = create_default_feature_data(
    'Add Feature Step',
    'feature',
    'add_step',
    [{'service_id': 'add_feature_step_evt', 'name': 'Add feature step'}],
    description='Add a step to an existing feature workflow.',
    params_schema=create_params_schema(
        id='str',
        name='str',
        service_id='str',
        parameters={'type': 'dict', 'required': False},
        data_key={'type': 'str', 'required': False},
        pass_on_error={'type': 'bool', 'required': False, 'default': False},
        position={'type': 'int', 'required': False},
    ),
)

# ** constant: feature_update_step_data
FEATURE_UPDATE_STEP_DATA = create_default_feature_data(
    'Update Feature Step',
    'feature',
    'update_step',
    [{'service_id': 'update_feature_step_evt', 'name': 'Update feature step'}],
    description='Update an attribute on a feature step.',
    params_schema=create_params_schema(id='str', position='int', attribute='str'),
)

# ** constant: feature_remove_step_data
FEATURE_REMOVE_STEP_DATA = create_default_feature_data(
    'Remove Feature Step',
    'feature',
    'remove_step',
    [{'service_id': 'remove_feature_step_evt', 'name': 'Remove feature step'}],
    description='Remove a step from a feature by position.',
    params_schema=create_params_schema(id='str', position='int'),
)

# ** constant: feature_reorder_step_data
FEATURE_REORDER_STEP_DATA = create_default_feature_data(
    'Reorder Feature Step',
    'feature',
    'reorder_step',
    [{'service_id': 'reorder_feature_step_evt', 'name': 'Reorder feature step'}],
    description='Move a feature step from one position to another.',
    params_schema=create_params_schema(id='str', start_position='int', end_position='int'),
)

# ** constant: service_add_data
SERVICE_ADD_DATA = create_default_feature_data(
    'Add Service Configuration',
    'service',
    'add',
    [{'service_id': 'add_service_registration_evt', 'name': 'Add service configuration'}],
    description='Add a new service configuration.',
    params_schema=create_params_schema(
        id='str',
        module_path={'type': 'str', 'required': False},
        class_name={'type': 'str', 'required': False},
        parameters={'type': 'dict', 'required': False, 'default': {}},
        flagged_dependencies={'type': 'list', 'required': False, 'default': []},
    ),
)

# ** constant: service_list_data
SERVICE_LIST_DATA = create_default_feature_data(
    'List All Settings',
    'service',
    'list',
    [{'service_id': 'di_list_all_configs_evt', 'name': 'List all settings'}],
    description='List all service configurations and constants.',
)

# ** constant: service_set_default_data
SERVICE_SET_DEFAULT_DATA = create_default_feature_data(
    'Set Default Service Configuration',
    'service',
    'set_default',
    [{'service_id': 'set_default_service_registration_evt', 'name': 'Set default service configuration'}],
    description='Set or update the default type for a service configuration.',
    params_schema=create_params_schema(
        id='str',
        module_path={'type': 'str', 'required': False},
        class_name={'type': 'str', 'required': False},
        parameters={'type': 'dict', 'required': False},
    ),
)

# ** constant: service_set_dependency_data
SERVICE_SET_DEPENDENCY_DATA = create_default_feature_data(
    'Set Service Dependency',
    'service',
    'set_dependency',
    [{'service_id': 'set_di_service_dependency_evt', 'name': 'Set service dependency'}],
    description='Set or update a flagged dependency on a service configuration.',
    params_schema=create_params_schema(
        id='str',
        flag='str',
        module_path='str',
        class_name='str',
        parameters={'type': 'dict', 'required': False, 'default': {}},
    ),
)

# ** constant: service_remove_dependency_data
SERVICE_REMOVE_DEPENDENCY_DATA = create_default_feature_data(
    'Remove Service Dependency',
    'service',
    'remove_dependency',
    [{'service_id': 'remove_di_service_dependency_evt', 'name': 'Remove service dependency'}],
    description='Remove a flagged dependency from a service configuration.',
    params_schema=create_params_schema(id='str', flag='str'),
)

# ** constant: service_remove_data
SERVICE_REMOVE_DATA = create_default_feature_data(
    'Remove Service Configuration',
    'service',
    'remove',
    [{'service_id': 'remove_service_registration_evt', 'name': 'Remove service configuration'}],
    description='Remove a service configuration by ID.',
    params_schema=create_params_schema(id='str'),
)

# ** constant: service_set_constants_data
SERVICE_SET_CONSTANTS_DATA = create_default_feature_data(
    'Set Service Constants',
    'service',
    'set_constants',
    [{'service_id': 'set_service_constants_evt', 'name': 'Set service constants'}],
    description='Set or clear service-level constants.',
    params_schema=create_params_schema(constants={'type': 'dict', 'required': False, 'default': {}}),
)

# ** constant: logging_add_formatter_data
LOGGING_ADD_FORMATTER_DATA = create_default_feature_data(
    'Add Formatter',
    'logging',
    'add_formatter',
    [{'service_id': 'add_formatter_evt', 'name': 'Add formatter'}],
    description='Add a new logging formatter configuration.',
    params_schema=create_params_schema(
        id='str',
        name='str',
        format='str',
        description={'type': 'str', 'required': False},
        datefmt={'type': 'str', 'required': False},
    ),
)

# ** constant: logging_remove_formatter_data
LOGGING_REMOVE_FORMATTER_DATA = create_default_feature_data(
    'Remove Formatter',
    'logging',
    'remove_formatter',
    [{'service_id': 'remove_formatter_evt', 'name': 'Remove formatter'}],
    description='Remove a logging formatter by ID.',
    params_schema=create_params_schema(id='str'),
)

# ** constant: logging_add_handler_data
LOGGING_ADD_HANDLER_DATA = create_default_feature_data(
    'Add Handler',
    'logging',
    'add_handler',
    [{'service_id': 'add_handler_evt', 'name': 'Add handler'}],
    description='Add a new logging handler configuration.',
    params_schema=create_params_schema(
        id='str',
        name='str',
        module_path='str',
        class_name='str',
        level='str',
        formatter='str',
        description={'type': 'str', 'required': False},
        stream={'type': 'str', 'required': False},
        filename={'type': 'str', 'required': False},
    ),
)

# ** constant: logging_remove_handler_data
LOGGING_REMOVE_HANDLER_DATA = create_default_feature_data(
    'Remove Handler',
    'logging',
    'remove_handler',
    [{'service_id': 'remove_handler_evt', 'name': 'Remove handler'}],
    description='Remove a logging handler by ID.',
    params_schema=create_params_schema(id='str'),
)

# ** constant: logging_add_logger_data
LOGGING_ADD_LOGGER_DATA = create_default_feature_data(
    'Add Logger',
    'logging',
    'add_logger',
    [{'service_id': 'add_logger_evt', 'name': 'Add logger'}],
    description='Add a new logger configuration.',
    params_schema=create_params_schema(
        id='str',
        name='str',
        level='str',
        description={'type': 'str', 'required': False},
        propagate={'type': 'bool', 'required': False, 'default': True},
    ),
)

# ** constant: logging_remove_logger_data
LOGGING_REMOVE_LOGGER_DATA = create_default_feature_data(
    'Remove Logger',
    'logging',
    'remove_logger',
    [{'service_id': 'remove_logger_evt', 'name': 'Remove logger'}],
    description='Remove a logger by ID.',
    params_schema=create_params_schema(id='str'),
)

# ** constant: logging_list_data
LOGGING_LIST_DATA = create_default_feature_data(
    'List Logging Configs',
    'logging',
    'list',
    [{'service_id': 'logging_list_all_evt', 'name': 'List all logging configs'}],
    description='List all logging configurations (formatters, handlers, loggers).',
)

# *** constants (groups)

# ** constant: admin_default_features
ADMIN_DEFAULT_FEATURES: Dict[str, Any] = {
    APP_ADD_ID: APP_ADD_DATA,
    APP_GET_ID: APP_GET_DATA,
    APP_LIST_ID: APP_LIST_DATA,
    APP_UPDATE_ID: APP_UPDATE_DATA,
    APP_SET_CONSTANTS_ID: APP_SET_CONSTANTS_DATA,
    APP_SET_SERVICE_ID: APP_SET_SERVICE_DATA,
    APP_REMOVE_SERVICE_ID: APP_REMOVE_SERVICE_DATA,
    APP_REMOVE_ID: APP_REMOVE_DATA,
    CLI_ADD_COMMAND_ID: CLI_ADD_COMMAND_DATA,
    CLI_LIST_COMMANDS_ID: CLI_LIST_COMMANDS_DATA,
    CLI_ADD_ARGUMENT_ID: CLI_ADD_ARGUMENT_DATA,
    ERROR_ADD_ID: ERROR_ADD_DATA,
    ERROR_GET_ID: ERROR_GET_DATA,
    ERROR_LIST_ID: ERROR_LIST_DATA,
    ERROR_RENAME_ID: ERROR_RENAME_DATA,
    ERROR_SET_MESSAGE_ID: ERROR_SET_MESSAGE_DATA,
    ERROR_REMOVE_MESSAGE_ID: ERROR_REMOVE_MESSAGE_DATA,
    ERROR_REMOVE_ID: ERROR_REMOVE_DATA,
    FEATURE_ADD_ID: FEATURE_ADD_DATA,
    FEATURE_GET_ID: FEATURE_GET_DATA,
    FEATURE_LIST_ID: FEATURE_LIST_DATA,
    FEATURE_REMOVE_ID: FEATURE_REMOVE_DATA,
    FEATURE_UPDATE_ID: FEATURE_UPDATE_DATA,
    FEATURE_ADD_STEP_ID: FEATURE_ADD_STEP_DATA,
    FEATURE_UPDATE_STEP_ID: FEATURE_UPDATE_STEP_DATA,
    FEATURE_REMOVE_STEP_ID: FEATURE_REMOVE_STEP_DATA,
    FEATURE_REORDER_STEP_ID: FEATURE_REORDER_STEP_DATA,
    SERVICE_ADD_ID: SERVICE_ADD_DATA,
    SERVICE_LIST_ID: SERVICE_LIST_DATA,
    SERVICE_SET_DEFAULT_ID: SERVICE_SET_DEFAULT_DATA,
    SERVICE_SET_DEPENDENCY_ID: SERVICE_SET_DEPENDENCY_DATA,
    SERVICE_REMOVE_DEPENDENCY_ID: SERVICE_REMOVE_DEPENDENCY_DATA,
    SERVICE_REMOVE_ID: SERVICE_REMOVE_DATA,
    SERVICE_SET_CONSTANTS_ID: SERVICE_SET_CONSTANTS_DATA,
    LOGGING_ADD_FORMATTER_ID: LOGGING_ADD_FORMATTER_DATA,
    LOGGING_REMOVE_FORMATTER_ID: LOGGING_REMOVE_FORMATTER_DATA,
    LOGGING_ADD_HANDLER_ID: LOGGING_ADD_HANDLER_DATA,
    LOGGING_REMOVE_HANDLER_ID: LOGGING_REMOVE_HANDLER_DATA,
    LOGGING_ADD_LOGGER_ID: LOGGING_ADD_LOGGER_DATA,
    LOGGING_REMOVE_LOGGER_ID: LOGGING_REMOVE_LOGGER_DATA,
    LOGGING_LIST_ID: LOGGING_LIST_DATA,
}
