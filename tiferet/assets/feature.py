"""Tiferet CLI Feature Catalog

Three-section catalog for the built-in Tiferet CLI feature workflows.
Each section follows the pattern established by ``assets/error.py``:
- ``constants (ids)`` — 41 individually named feature ID string constants.
- ``constants (features)`` — 41 individually named feature definition dicts,
  each built via ``create_default_feature``.
- ``constants (groups)`` — the ``DEFAULT_ADMIN_FEATURES`` catalog dict
  keyed by ID constants.
"""

# *** imports

# ** core
from typing import Any, Dict, List

# ** app
from .core import create_default_feature

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

# ** constant: cli_list_commands_id
CLI_LIST_COMMANDS_ID = 'cli.list_commands'

# ** constant: cli_add_command_id
CLI_ADD_COMMAND_ID = 'cli.add_command'

# ** constant: cli_add_argument_id
CLI_ADD_ARGUMENT_ID = 'cli.add_argument'

# ** constant: error_list_id
ERROR_LIST_ID = 'error.list'

# ** constant: error_add_id
ERROR_ADD_ID = 'error.add'

# ** constant: error_get_id
ERROR_GET_ID = 'error.get'

# ** constant: error_rename_id
ERROR_RENAME_ID = 'error.rename'

# ** constant: error_set_message_id
ERROR_SET_MESSAGE_ID = 'error.set_message'

# ** constant: error_remove_message_id
ERROR_REMOVE_MESSAGE_ID = 'error.remove_message'

# ** constant: error_remove_id
ERROR_REMOVE_ID = 'error.remove'

# ** constant: feature_list_id
FEATURE_LIST_ID = 'feature.list'

# ** constant: feature_add_id
FEATURE_ADD_ID = 'feature.add'

# ** constant: feature_get_id
FEATURE_GET_ID = 'feature.get'

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

# ** constant: feature_remove_id
FEATURE_REMOVE_ID = 'feature.remove'

# ** constant: service_list_id
SERVICE_LIST_ID = 'service.list'

# ** constant: service_add_id
SERVICE_ADD_ID = 'service.add'

# ** constant: service_set_default_id
SERVICE_SET_DEFAULT_ID = 'service.set_default'

# ** constant: service_set_dependency_id
SERVICE_SET_DEPENDENCY_ID = 'service.set_dependency'

# ** constant: service_remove_dependency_id
SERVICE_REMOVE_DEPENDENCY_ID = 'service.remove_dependency'

# ** constant: service_set_constants_id
SERVICE_SET_CONSTANTS_ID = 'service.set_constants'

# ** constant: service_remove_id
SERVICE_REMOVE_ID = 'service.remove'

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

# ** constant: app_add
APP_ADD = create_default_feature(
    id=APP_ADD_ID,
    name='Add App Session',
    group_id='app',
    feature_key='add',
    steps=[{'service_id': 'add_app_session_evt'}],
    description='Add a new application session configuration.',
)

# ** constant: app_get
APP_GET = create_default_feature(
    id=APP_GET_ID,
    name='Get App Session',
    group_id='app',
    feature_key='get',
    steps=[{'service_id': 'get_app_session_evt'}],
    description='Retrieve an app session by ID.',
)

# ** constant: app_list
APP_LIST = create_default_feature(
    id=APP_LIST_ID,
    name='List App Sessions',
    group_id='app',
    feature_key='list',
    steps=[{'service_id': 'list_app_sessions_evt'}],
    description='List all configured app sessions.',
)

# ** constant: app_update
APP_UPDATE = create_default_feature(
    id=APP_UPDATE_ID,
    name='Update App Session',
    group_id='app',
    feature_key='update',
    steps=[{'service_id': 'update_app_session_evt'}],
    description='Update a scalar attribute on an app session.',
)

# ** constant: app_set_constants
APP_SET_CONSTANTS = create_default_feature(
    id=APP_SET_CONSTANTS_ID,
    name='Set App Constants',
    group_id='app',
    feature_key='set_constants',
    steps=[{'service_id': 'set_app_constants_evt'}],
    description='Set or clear constants on an app session.',
)

# ** constant: app_set_service
APP_SET_SERVICE = create_default_feature(
    id=APP_SET_SERVICE_ID,
    name='Set App Service Dependency',
    group_id='app',
    feature_key='set_service',
    steps=[{'service_id': 'set_app_service_dependency_evt'}],
    description='Set or update a service dependency on an app session.',
)

# ** constant: app_remove_service
APP_REMOVE_SERVICE = create_default_feature(
    id=APP_REMOVE_SERVICE_ID,
    name='Remove App Service Dependency',
    group_id='app',
    feature_key='remove_service',
    steps=[{'service_id': 'remove_app_service_dependency_evt'}],
    description='Remove a service dependency from an app session.',
)

# ** constant: app_remove
APP_REMOVE = create_default_feature(
    id=APP_REMOVE_ID,
    name='Remove App Session',
    group_id='app',
    feature_key='remove',
    steps=[{'service_id': 'remove_app_session_evt'}],
    description='Remove an app session by ID.',
)

# ** constant: cli_list_commands
CLI_LIST_COMMANDS = create_default_feature(
    id=CLI_LIST_COMMANDS_ID,
    name='List CLI Commands',
    group_id='cli',
    feature_key='list_commands',
    steps=[{'service_id': 'list_commands_evt'}],
    description='List all configured CLI commands.',
)

# ** constant: cli_add_command
CLI_ADD_COMMAND = create_default_feature(
    id=CLI_ADD_COMMAND_ID,
    name='Add CLI Command',
    group_id='cli',
    feature_key='add_command',
    steps=[{'service_id': 'add_cli_command_evt'}],
    description='Add a new CLI command definition.',
)

# ** constant: cli_add_argument
CLI_ADD_ARGUMENT = create_default_feature(
    id=CLI_ADD_ARGUMENT_ID,
    name='Add CLI Argument',
    group_id='cli',
    feature_key='add_argument',
    steps=[{'service_id': 'add_cli_argument_evt'}],
    description='Add an argument to an existing CLI command.',
)

# ** constant: error_list
ERROR_LIST = create_default_feature(
    id=ERROR_LIST_ID,
    name='List Errors',
    group_id='error',
    feature_key='list',
    steps=[{'service_id': 'list_errors_evt'}],
    description='List all error definitions.',
)

# ** constant: error_add
ERROR_ADD = create_default_feature(
    id=ERROR_ADD_ID,
    name='Add Error',
    group_id='error',
    feature_key='add',
    steps=[{'service_id': 'add_error_evt'}],
    description='Add a new error definition.',
)

# ** constant: error_get
ERROR_GET = create_default_feature(
    id=ERROR_GET_ID,
    name='Get Error',
    group_id='error',
    feature_key='get',
    steps=[{'service_id': 'get_error_evt'}],
    description='Retrieve an error by ID.',
)

# ** constant: error_rename
ERROR_RENAME = create_default_feature(
    id=ERROR_RENAME_ID,
    name='Rename Error',
    group_id='error',
    feature_key='rename',
    steps=[{'service_id': 'rename_error_evt'}],
    description='Rename an existing error definition.',
)

# ** constant: error_set_message
ERROR_SET_MESSAGE = create_default_feature(
    id=ERROR_SET_MESSAGE_ID,
    name='Set Error Message',
    group_id='error',
    feature_key='set_message',
    steps=[{'service_id': 'set_error_message_evt'}],
    description='Set the message text on an existing error definition.',
)

# ** constant: error_remove_message
ERROR_REMOVE_MESSAGE = create_default_feature(
    id=ERROR_REMOVE_MESSAGE_ID,
    name='Remove Error Message',
    group_id='error',
    feature_key='remove_message',
    steps=[{'service_id': 'remove_error_message_evt'}],
    description='Remove a language message from an existing error definition.',
)

# ** constant: error_remove
ERROR_REMOVE = create_default_feature(
    id=ERROR_REMOVE_ID,
    name='Remove Error',
    group_id='error',
    feature_key='remove',
    steps=[{'service_id': 'remove_error_evt'}],
    description='Remove an error definition.',
)

# ** constant: feature_list
FEATURE_LIST = create_default_feature(
    id=FEATURE_LIST_ID,
    name='List Features',
    group_id='feature',
    feature_key='list',
    steps=[{'service_id': 'list_features_evt'}],
    description='List all feature workflow definitions.',
)

# ** constant: feature_add
FEATURE_ADD = create_default_feature(
    id=FEATURE_ADD_ID,
    name='Add Feature',
    group_id='feature',
    feature_key='add',
    steps=[{'service_id': 'add_feature_evt'}],
    description='Add a new feature workflow definition.',
)

# ** constant: feature_get
FEATURE_GET = create_default_feature(
    id=FEATURE_GET_ID,
    name='Get Feature',
    group_id='feature',
    feature_key='get',
    steps=[{'service_id': 'get_feature_evt'}],
    description='Retrieve a feature by ID.',
)

# ** constant: feature_update
FEATURE_UPDATE = create_default_feature(
    id=FEATURE_UPDATE_ID,
    name='Update Feature',
    group_id='feature',
    feature_key='update',
    steps=[{'service_id': 'update_feature_evt'}],
    description='Update a metadata attribute on an existing feature.',
)

# ** constant: feature_add_step
FEATURE_ADD_STEP = create_default_feature(
    id=FEATURE_ADD_STEP_ID,
    name='Add Feature Step',
    group_id='feature',
    feature_key='add_step',
    steps=[{'service_id': 'add_feature_step_evt'}],
    description='Add a step to an existing feature workflow.',
)

# ** constant: feature_update_step
FEATURE_UPDATE_STEP = create_default_feature(
    id=FEATURE_UPDATE_STEP_ID,
    name='Update Feature Step',
    group_id='feature',
    feature_key='update_step',
    steps=[{'service_id': 'update_feature_step_evt'}],
    description='Update an attribute on an existing feature step.',
)

# ** constant: feature_remove_step
FEATURE_REMOVE_STEP = create_default_feature(
    id=FEATURE_REMOVE_STEP_ID,
    name='Remove Feature Step',
    group_id='feature',
    feature_key='remove_step',
    steps=[{'service_id': 'remove_feature_step_evt'}],
    description='Remove a step from an existing feature workflow.',
)

# ** constant: feature_reorder_step
FEATURE_REORDER_STEP = create_default_feature(
    id=FEATURE_REORDER_STEP_ID,
    name='Reorder Feature Step',
    group_id='feature',
    feature_key='reorder_step',
    steps=[{'service_id': 'reorder_feature_step_evt'}],
    description='Reorder a step within an existing feature workflow.',
)

# ** constant: feature_remove
FEATURE_REMOVE = create_default_feature(
    id=FEATURE_REMOVE_ID,
    name='Remove Feature',
    group_id='feature',
    feature_key='remove',
    steps=[{'service_id': 'remove_feature_evt'}],
    description='Remove an existing feature workflow definition.',
)

# ** constant: service_list
SERVICE_LIST = create_default_feature(
    id=SERVICE_LIST_ID,
    name='List Services',
    group_id='service',
    feature_key='list',
    steps=[{'service_id': 'di_list_all_configs_evt'}],
    description='List all DI service registrations and constants.',
)

# ** constant: service_add
SERVICE_ADD = create_default_feature(
    id=SERVICE_ADD_ID,
    name='Add Service',
    group_id='service',
    feature_key='add',
    steps=[{'service_id': 'add_service_registration_evt'}],
    description='Add a new DI service registration.',
)

# ** constant: service_set_default
SERVICE_SET_DEFAULT = create_default_feature(
    id=SERVICE_SET_DEFAULT_ID,
    name='Set Default Service Registration',
    group_id='service',
    feature_key='set_default',
    steps=[{'service_id': 'set_default_service_registration_evt'}],
    description='Set or update the default type for an existing service registration.',
)

# ** constant: service_set_dependency
SERVICE_SET_DEPENDENCY = create_default_feature(
    id=SERVICE_SET_DEPENDENCY_ID,
    name='Set Service Dependency',
    group_id='service',
    feature_key='set_dependency',
    steps=[{'service_id': 'set_di_service_dependency_evt'}],
    description='Set or update a flagged dependency on a service registration.',
)

# ** constant: service_remove_dependency
SERVICE_REMOVE_DEPENDENCY = create_default_feature(
    id=SERVICE_REMOVE_DEPENDENCY_ID,
    name='Remove Service Dependency',
    group_id='service',
    feature_key='remove_dependency',
    steps=[{'service_id': 'remove_di_service_dependency_evt'}],
    description='Remove a flagged dependency from a service registration.',
)

# ** constant: service_set_constants
SERVICE_SET_CONSTANTS = create_default_feature(
    id=SERVICE_SET_CONSTANTS_ID,
    name='Set Service Constants',
    group_id='service',
    feature_key='set_constants',
    steps=[{'service_id': 'set_service_constants_evt'}],
    description='Set or clear DI service constants.',
)

# ** constant: service_remove
SERVICE_REMOVE = create_default_feature(
    id=SERVICE_REMOVE_ID,
    name='Remove Service',
    group_id='service',
    feature_key='remove',
    steps=[{'service_id': 'remove_service_registration_evt'}],
    description='Remove a DI service registration.',
)

# ** constant: logging_add_formatter
LOGGING_ADD_FORMATTER = create_default_feature(
    id=LOGGING_ADD_FORMATTER_ID,
    name='Add Formatter',
    group_id='logging',
    feature_key='add_formatter',
    steps=[{'service_id': 'add_formatter_evt'}],
    description='Add a new logging formatter configuration.',
)

# ** constant: logging_remove_formatter
LOGGING_REMOVE_FORMATTER = create_default_feature(
    id=LOGGING_REMOVE_FORMATTER_ID,
    name='Remove Formatter',
    group_id='logging',
    feature_key='remove_formatter',
    steps=[{'service_id': 'remove_formatter_evt'}],
    description='Remove a logging formatter by ID.',
)

# ** constant: logging_add_handler
LOGGING_ADD_HANDLER = create_default_feature(
    id=LOGGING_ADD_HANDLER_ID,
    name='Add Handler',
    group_id='logging',
    feature_key='add_handler',
    steps=[{'service_id': 'add_handler_evt'}],
    description='Add a new logging handler configuration.',
)

# ** constant: logging_remove_handler
LOGGING_REMOVE_HANDLER = create_default_feature(
    id=LOGGING_REMOVE_HANDLER_ID,
    name='Remove Handler',
    group_id='logging',
    feature_key='remove_handler',
    steps=[{'service_id': 'remove_handler_evt'}],
    description='Remove a logging handler by ID.',
)

# ** constant: logging_add_logger
LOGGING_ADD_LOGGER = create_default_feature(
    id=LOGGING_ADD_LOGGER_ID,
    name='Add Logger',
    group_id='logging',
    feature_key='add_logger',
    steps=[{'service_id': 'add_logger_evt'}],
    description='Add a new logger configuration.',
)

# ** constant: logging_remove_logger
LOGGING_REMOVE_LOGGER = create_default_feature(
    id=LOGGING_REMOVE_LOGGER_ID,
    name='Remove Logger',
    group_id='logging',
    feature_key='remove_logger',
    steps=[{'service_id': 'remove_logger_evt'}],
    description='Remove a logger by ID.',
)

# ** constant: logging_list
LOGGING_LIST = create_default_feature(
    id=LOGGING_LIST_ID,
    name='List Logging Configs',
    group_id='logging',
    feature_key='list',
    steps=[{'service_id': 'logging_list_all_evt'}],
    description='List all logging configurations (formatters, handlers, loggers).',
)

# *** constants (groups)

# ** constant: default_admin_features
DEFAULT_ADMIN_FEATURES: Dict[str, Any] = {
    APP_ADD_ID: APP_ADD,
    APP_GET_ID: APP_GET,
    APP_LIST_ID: APP_LIST,
    APP_UPDATE_ID: APP_UPDATE,
    APP_SET_CONSTANTS_ID: APP_SET_CONSTANTS,
    APP_SET_SERVICE_ID: APP_SET_SERVICE,
    APP_REMOVE_SERVICE_ID: APP_REMOVE_SERVICE,
    APP_REMOVE_ID: APP_REMOVE,
    CLI_LIST_COMMANDS_ID: CLI_LIST_COMMANDS,
    CLI_ADD_COMMAND_ID: CLI_ADD_COMMAND,
    CLI_ADD_ARGUMENT_ID: CLI_ADD_ARGUMENT,
    ERROR_LIST_ID: ERROR_LIST,
    ERROR_ADD_ID: ERROR_ADD,
    ERROR_GET_ID: ERROR_GET,
    ERROR_RENAME_ID: ERROR_RENAME,
    ERROR_SET_MESSAGE_ID: ERROR_SET_MESSAGE,
    ERROR_REMOVE_MESSAGE_ID: ERROR_REMOVE_MESSAGE,
    ERROR_REMOVE_ID: ERROR_REMOVE,
    FEATURE_LIST_ID: FEATURE_LIST,
    FEATURE_ADD_ID: FEATURE_ADD,
    FEATURE_GET_ID: FEATURE_GET,
    FEATURE_UPDATE_ID: FEATURE_UPDATE,
    FEATURE_ADD_STEP_ID: FEATURE_ADD_STEP,
    FEATURE_UPDATE_STEP_ID: FEATURE_UPDATE_STEP,
    FEATURE_REMOVE_STEP_ID: FEATURE_REMOVE_STEP,
    FEATURE_REORDER_STEP_ID: FEATURE_REORDER_STEP,
    FEATURE_REMOVE_ID: FEATURE_REMOVE,
    SERVICE_LIST_ID: SERVICE_LIST,
    SERVICE_ADD_ID: SERVICE_ADD,
    SERVICE_SET_DEFAULT_ID: SERVICE_SET_DEFAULT,
    SERVICE_SET_DEPENDENCY_ID: SERVICE_SET_DEPENDENCY,
    SERVICE_REMOVE_DEPENDENCY_ID: SERVICE_REMOVE_DEPENDENCY,
    SERVICE_SET_CONSTANTS_ID: SERVICE_SET_CONSTANTS,
    SERVICE_REMOVE_ID: SERVICE_REMOVE,
    LOGGING_ADD_FORMATTER_ID: LOGGING_ADD_FORMATTER,
    LOGGING_REMOVE_FORMATTER_ID: LOGGING_REMOVE_FORMATTER,
    LOGGING_ADD_HANDLER_ID: LOGGING_ADD_HANDLER,
    LOGGING_REMOVE_HANDLER_ID: LOGGING_REMOVE_HANDLER,
    LOGGING_ADD_LOGGER_ID: LOGGING_ADD_LOGGER,
    LOGGING_REMOVE_LOGGER_ID: LOGGING_REMOVE_LOGGER,
    LOGGING_LIST_ID: LOGGING_LIST,
}
