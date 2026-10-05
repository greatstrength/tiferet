"""Tiferet CLI Command Catalog

Three-section catalog of built-in administrative CLI command definitions:
IDs, individually named command constants, and the ADMIN_DEFAULT_COMMANDS group dict.
"""

# *** imports

# ** core
from typing import Any, Dict, List

# ** app
from .core import create_default_cli_argument, create_default_cli_command_data

# *** constants (ids)

# ** constant: app_list_cli_cmd_id
APP_LIST_CLI_CMD_ID = 'app.list'

# ** constant: app_get_cli_cmd_id
APP_GET_CLI_CMD_ID = 'app.get'

# ** constant: app_add_cli_cmd_id
APP_ADD_CLI_CMD_ID = 'app.add'

# ** constant: app_update_cli_cmd_id
APP_UPDATE_CLI_CMD_ID = 'app.update'

# ** constant: app_set_service_cli_cmd_id
APP_SET_SERVICE_CLI_CMD_ID = 'app.set_service'

# ** constant: app_remove_service_cli_cmd_id
APP_REMOVE_SERVICE_CLI_CMD_ID = 'app.remove_service'

# ** constant: app_set_constants_cli_cmd_id
APP_SET_CONSTANTS_CLI_CMD_ID = 'app.set_constants'

# ** constant: app_remove_cli_cmd_id
APP_REMOVE_CLI_CMD_ID = 'app.remove'

# ** constant: cli_list_commands_cli_cmd_id
CLI_LIST_COMMANDS_CLI_CMD_ID = 'cli.list_commands'

# ** constant: cli_add_command_cli_cmd_id
CLI_ADD_COMMAND_CLI_CMD_ID = 'cli.add_command'

# ** constant: cli_add_argument_cli_cmd_id
CLI_ADD_ARGUMENT_CLI_CMD_ID = 'cli.add_argument'

# ** constant: error_list_cli_cmd_id
ERROR_LIST_CLI_CMD_ID = 'error.list'

# ** constant: error_get_cli_cmd_id
ERROR_GET_CLI_CMD_ID = 'error.get'

# ** constant: error_add_cli_cmd_id
ERROR_ADD_CLI_CMD_ID = 'error.add'

# ** constant: error_rename_cli_cmd_id
ERROR_RENAME_CLI_CMD_ID = 'error.rename'

# ** constant: error_set_message_cli_cmd_id
ERROR_SET_MESSAGE_CLI_CMD_ID = 'error.set_message'

# ** constant: error_remove_message_cli_cmd_id
ERROR_REMOVE_MESSAGE_CLI_CMD_ID = 'error.remove_message'

# ** constant: error_remove_cli_cmd_id
ERROR_REMOVE_CLI_CMD_ID = 'error.remove'

# ** constant: feature_list_cli_cmd_id
FEATURE_LIST_CLI_CMD_ID = 'feature.list'

# ** constant: feature_get_cli_cmd_id
FEATURE_GET_CLI_CMD_ID = 'feature.get'

# ** constant: feature_add_cli_cmd_id
FEATURE_ADD_CLI_CMD_ID = 'feature.add'

# ** constant: feature_update_cli_cmd_id
FEATURE_UPDATE_CLI_CMD_ID = 'feature.update'

# ** constant: feature_add_step_cli_cmd_id
FEATURE_ADD_STEP_CLI_CMD_ID = 'feature.add_step'

# ** constant: feature_update_step_cli_cmd_id
FEATURE_UPDATE_STEP_CLI_CMD_ID = 'feature.update_step'

# ** constant: feature_remove_step_cli_cmd_id
FEATURE_REMOVE_STEP_CLI_CMD_ID = 'feature.remove_step'

# ** constant: feature_reorder_step_cli_cmd_id
FEATURE_REORDER_STEP_CLI_CMD_ID = 'feature.reorder_step'

# ** constant: feature_remove_cli_cmd_id
FEATURE_REMOVE_CLI_CMD_ID = 'feature.remove'

# ** constant: service_list_cli_cmd_id
SERVICE_LIST_CLI_CMD_ID = 'service.list'

# ** constant: service_add_cli_cmd_id
SERVICE_ADD_CLI_CMD_ID = 'service.add'

# ** constant: service_set_default_cli_cmd_id
SERVICE_SET_DEFAULT_CLI_CMD_ID = 'service.set_default'

# ** constant: service_set_dependency_cli_cmd_id
SERVICE_SET_DEPENDENCY_CLI_CMD_ID = 'service.set_dependency'

# ** constant: service_remove_dependency_cli_cmd_id
SERVICE_REMOVE_DEPENDENCY_CLI_CMD_ID = 'service.remove_dependency'

# ** constant: service_set_constants_cli_cmd_id
SERVICE_SET_CONSTANTS_CLI_CMD_ID = 'service.set_constants'

# ** constant: service_remove_cli_cmd_id
SERVICE_REMOVE_CLI_CMD_ID = 'service.remove'

# ** constant: logging_add_formatter_cli_cmd_id
LOGGING_ADD_FORMATTER_CLI_CMD_ID = 'logging.add_formatter'

# ** constant: logging_remove_formatter_cli_cmd_id
LOGGING_REMOVE_FORMATTER_CLI_CMD_ID = 'logging.remove_formatter'

# ** constant: logging_add_handler_cli_cmd_id
LOGGING_ADD_HANDLER_CLI_CMD_ID = 'logging.add_handler'

# ** constant: logging_remove_handler_cli_cmd_id
LOGGING_REMOVE_HANDLER_CLI_CMD_ID = 'logging.remove_handler'

# ** constant: logging_add_logger_cli_cmd_id
LOGGING_ADD_LOGGER_CLI_CMD_ID = 'logging.add_logger'

# ** constant: logging_remove_logger_cli_cmd_id
LOGGING_REMOVE_LOGGER_CLI_CMD_ID = 'logging.remove_logger'

# ** constant: logging_list_cli_cmd_id
LOGGING_LIST_CLI_CMD_ID = 'logging.list'

# *** constants (commands)

# ** constant: app_list_cli_cmd_data
APP_LIST_CLI_CMD_DATA = create_default_cli_command_data(
    'list',
    'app',
    'List App Interfaces',
    description='List all configured app interfaces.',
)

# ** constant: app_get_cli_cmd_data
APP_GET_CLI_CMD_DATA = create_default_cli_command_data(
    'get',
    'app',
    'Get App Interface',
    description='Retrieve an app interface by ID.',
    arguments=[
        create_default_cli_argument(
            ['interface_id'],
            description='The interface identifier.',
        ),
    ],
)

# ** constant: app_add_cli_cmd_data
APP_ADD_CLI_CMD_DATA = create_default_cli_command_data(
    'add',
    'app',
    'Add App Interface',
    description='Add a new application interface configuration.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The unique interface identifier.',
        ),
        create_default_cli_argument(
            ['name'],
            description='The human-readable interface name.',
        ),
        create_default_cli_argument(
            ['--description'],
            description='Optional interface description.',
        ),
        create_default_cli_argument(
            ['--logger-id'],
            description='Optional logger identifier. Defaults to "default".',
        ),
        create_default_cli_argument(
            ['--constants'],
            description='Optional constants as key=value pairs.',
            type='dict',
        ),
    ],
)

# ** constant: app_update_cli_cmd_data
APP_UPDATE_CLI_CMD_DATA = create_default_cli_command_data(
    'update',
    'app',
    'Update App Interface',
    description='Update a scalar attribute on an app interface.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The interface identifier.',
        ),
        create_default_cli_argument(
            ['attribute'],
            description='The attribute to update.',
        ),
        create_default_cli_argument(
            ['value'],
            description='The new value for the attribute.',
        ),
    ],
)

# ** constant: app_set_service_cli_cmd_data
APP_SET_SERVICE_CLI_CMD_DATA = create_default_cli_command_data(
    'set-service',
    'app',
    'Set App Service Dependency',
    description='Set or update a service dependency on an app interface.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The interface identifier.',
        ),
        create_default_cli_argument(
            ['service_id'],
            description='The service dependency identifier.',
        ),
        create_default_cli_argument(
            ['module_path'],
            description='The module path of the service implementation.',
        ),
        create_default_cli_argument(
            ['class_name'],
            description='The class name of the service implementation.',
        ),
        create_default_cli_argument(
            ['--parameters'],
            description='Optional parameters as key=value pairs.',
            type='dict',
        ),
    ],
)

# ** constant: app_remove_service_cli_cmd_data
APP_REMOVE_SERVICE_CLI_CMD_DATA = create_default_cli_command_data(
    'remove-service',
    'app',
    'Remove App Service Dependency',
    description='Remove a service dependency from an app interface.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The interface identifier.',
        ),
        create_default_cli_argument(
            ['service_id'],
            description='The service dependency identifier to remove.',
        ),
    ],
)

# ** constant: app_set_constants_cli_cmd_data
APP_SET_CONSTANTS_CLI_CMD_DATA = create_default_cli_command_data(
    'set-constants',
    'app',
    'Set App Constants',
    description='Set or clear constants on an app interface.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The interface identifier.',
        ),
        create_default_cli_argument(
            ['--constants'],
            description='Optional constants as key=value pairs. Omit to clear all constants.',
            type='dict',
        ),
    ],
)

# ** constant: app_remove_cli_cmd_data
APP_REMOVE_CLI_CMD_DATA = create_default_cli_command_data(
    'remove',
    'app',
    'Remove App Interface',
    description='Remove an app interface by ID.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The interface identifier to remove.',
        ),
    ],
)

# ** constant: cli_list_commands_cli_cmd_data
CLI_LIST_COMMANDS_CLI_CMD_DATA = create_default_cli_command_data(
    'list-commands',
    'cli',
    'List CLI Commands',
    description='List all CLI command definitions.',
)

# ** constant: cli_add_command_cli_cmd_data
CLI_ADD_COMMAND_CLI_CMD_DATA = create_default_cli_command_data(
    'add-command',
    'cli',
    'Add CLI Command',
    description='Add a new CLI command definition.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The unique command identifier.',
        ),
        create_default_cli_argument(
            ['name'],
            description='The human-readable command name.',
        ),
        create_default_cli_argument(
            ['key'],
            description='The command key used in the CLI.',
        ),
        create_default_cli_argument(
            ['group_key'],
            description='The group key this command belongs to.',
        ),
        create_default_cli_argument(
            ['--description'],
            description='Optional command description.',
        ),
    ],
)

# ** constant: cli_add_argument_cli_cmd_data
CLI_ADD_ARGUMENT_CLI_CMD_DATA = create_default_cli_command_data(
    'add-argument',
    'cli',
    'Add CLI Argument',
    description='Add an argument to an existing CLI command.',
    arguments=[
        create_default_cli_argument(
            ['command_id'],
            description='The CLI command identifier.',
        ),
        create_default_cli_argument(
            ['name_or_flags'],
            description='JSON-encoded list of argument names or flags.',
        ),
        create_default_cli_argument(
            ['--description'],
            description='Optional argument description.',
        ),
    ],
)

# ** constant: error_list_cli_cmd_data
ERROR_LIST_CLI_CMD_DATA = create_default_cli_command_data(
    'list',
    'error',
    'List Errors',
    description='List all error definitions.',
)

# ** constant: error_get_cli_cmd_data
ERROR_GET_CLI_CMD_DATA = create_default_cli_command_data(
    'get',
    'error',
    'Get Error',
    description='Retrieve an error by ID.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The error identifier.',
        ),
    ],
)

# ** constant: error_add_cli_cmd_data
ERROR_ADD_CLI_CMD_DATA = create_default_cli_command_data(
    'add',
    'error',
    'Add Error',
    description='Add a new error definition.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The unique error identifier.',
        ),
        create_default_cli_argument(
            ['name'],
            description='The human-readable error name.',
        ),
        create_default_cli_argument(
            ['message'],
            description='The primary error message text.',
        ),
        create_default_cli_argument(
            ['--lang'],
            description='Language code for the message. Defaults to "en_US".',
            default='en_US',
        ),
        create_default_cli_argument(
            ['--additional-messages'],
            description='Additional messages beyond the primary one, as lang=text pairs.',
            type='dict',
        ),
    ],
)

# ** constant: error_rename_cli_cmd_data
ERROR_RENAME_CLI_CMD_DATA = create_default_cli_command_data(
    'rename',
    'error',
    'Rename Error',
    description='Rename an existing error.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The unique error identifier.',
        ),
        create_default_cli_argument(
            ['new_name'],
            description='The new error name.',
        ),
    ],
)

# ** constant: error_set_message_cli_cmd_data
ERROR_SET_MESSAGE_CLI_CMD_DATA = create_default_cli_command_data(
    'set-message',
    'error',
    'Set Error Message',
    description='Set or update an error message for a language.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The unique error identifier.',
        ),
        create_default_cli_argument(
            ['message'],
            description='The new message text.',
        ),
        create_default_cli_argument(
            ['--lang'],
            description='Language code for the message. Defaults to "en_US".',
            default='en_US',
        ),
    ],
)

# ** constant: error_remove_message_cli_cmd_data
ERROR_REMOVE_MESSAGE_CLI_CMD_DATA = create_default_cli_command_data(
    'remove-message',
    'error',
    'Remove Error Message',
    description='Remove an error message by language.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The unique error identifier.',
        ),
        create_default_cli_argument(
            ['--lang'],
            description='Language code of the message to remove. Defaults to "en_US".',
            default='en_US',
        ),
    ],
)

# ** constant: error_remove_cli_cmd_data
ERROR_REMOVE_CLI_CMD_DATA = create_default_cli_command_data(
    'remove',
    'error',
    'Remove Error',
    description='Remove an error definition by ID.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The unique error identifier to remove.',
        ),
    ],
)

# ** constant: feature_list_cli_cmd_data
FEATURE_LIST_CLI_CMD_DATA = create_default_cli_command_data(
    'list',
    'feature',
    'List Features',
    description='List all features, optionally filtered by group.',
    arguments=[
        create_default_cli_argument(
            ['--group-id'],
            description='Optional group identifier to filter results.',
        ),
    ],
)

# ** constant: feature_get_cli_cmd_data
FEATURE_GET_CLI_CMD_DATA = create_default_cli_command_data(
    'get',
    'feature',
    'Get Feature',
    description='Retrieve a feature by ID.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The feature identifier (e.g. calc.add).',
        ),
    ],
)

# ** constant: feature_add_cli_cmd_data
FEATURE_ADD_CLI_CMD_DATA = create_default_cli_command_data(
    'add',
    'feature',
    'Add Feature',
    description='Add a new feature configuration.',
    arguments=[
        create_default_cli_argument(
            ['name'],
            description='The feature name.',
        ),
        create_default_cli_argument(
            ['group_id'],
            description='The group identifier.',
        ),
        create_default_cli_argument(
            ['--feature-key'],
            description='Optional explicit feature key. Defaults to snake_case of name.',
        ),
        create_default_cli_argument(
            ['--description'],
            description='Optional feature description.',
        ),
    ],
)

# ** constant: feature_update_cli_cmd_data
FEATURE_UPDATE_CLI_CMD_DATA = create_default_cli_command_data(
    'update',
    'feature',
    'Update Feature',
    description='Update a feature attribute (name or description).',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The feature identifier.',
        ),
        create_default_cli_argument(
            ['attribute'],
            description='The attribute to update (name or description).',
            choices=['name', 'description'],
        ),
        create_default_cli_argument(
            ['value'],
            description='The new value.',
        ),
    ],
)

# ** constant: feature_add_step_cli_cmd_data
FEATURE_ADD_STEP_CLI_CMD_DATA = create_default_cli_command_data(
    'add-step',
    'feature',
    'Add Feature Step',
    description='Add a step to an existing feature workflow.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The feature identifier.',
        ),
        create_default_cli_argument(
            ['name'],
            description='The step name.',
        ),
        create_default_cli_argument(
            ['service_id'],
            description='The DI service registration identifier for this step.',
        ),
        create_default_cli_argument(
            ['--parameters'],
            description='Optional step parameters as key=value pairs.',
            type='dict',
        ),
        create_default_cli_argument(
            ['--data-key'],
            description='Optional result data key.',
        ),
        create_default_cli_argument(
            ['--position'],
            description='Optional insertion index. Defaults to append.',
            type='int',
        ),
    ],
)

# ** constant: feature_update_step_cli_cmd_data
FEATURE_UPDATE_STEP_CLI_CMD_DATA = create_default_cli_command_data(
    'update-step',
    'feature',
    'Update Feature Step',
    description='Update an attribute on a feature step.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The feature identifier.',
        ),
        create_default_cli_argument(
            ['position'],
            description='The zero-based step index.',
            type='int',
        ),
        create_default_cli_argument(
            ['attribute'],
            description='The step attribute to update.',
            choices=['name', 'service_id', 'data_key', 'pass_on_error', 'parameters'],
        ),
        create_default_cli_argument(
            ['value'],
            description='The new value for the attribute.',
        ),
    ],
)

# ** constant: feature_remove_step_cli_cmd_data
FEATURE_REMOVE_STEP_CLI_CMD_DATA = create_default_cli_command_data(
    'remove-step',
    'feature',
    'Remove Feature Step',
    description='Remove a step from a feature by position.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The feature identifier.',
        ),
        create_default_cli_argument(
            ['position'],
            description='The zero-based index of the step to remove.',
            type='int',
        ),
    ],
)

# ** constant: feature_reorder_step_cli_cmd_data
FEATURE_REORDER_STEP_CLI_CMD_DATA = create_default_cli_command_data(
    'reorder-step',
    'feature',
    'Reorder Feature Step',
    description='Move a feature step from one position to another.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The feature identifier.',
        ),
        create_default_cli_argument(
            ['start_position'],
            description='The current zero-based step index.',
            type='int',
        ),
        create_default_cli_argument(
            ['end_position'],
            description='The target zero-based step index.',
            type='int',
        ),
    ],
)

# ** constant: feature_remove_cli_cmd_data
FEATURE_REMOVE_CLI_CMD_DATA = create_default_cli_command_data(
    'remove',
    'feature',
    'Remove Feature',
    description='Remove a feature configuration by ID.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The feature identifier to remove.',
        ),
    ],
)

# ** constant: service_list_cli_cmd_data
SERVICE_LIST_CLI_CMD_DATA = create_default_cli_command_data(
    'list',
    'service',
    'List All Settings',
    description='List all service configurations and constants.',
)

# ** constant: service_add_cli_cmd_data
SERVICE_ADD_CLI_CMD_DATA = create_default_cli_command_data(
    'add',
    'service',
    'Add Service Configuration',
    description='Add a new service configuration.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The unique service registration identifier.',
        ),
        create_default_cli_argument(
            ['--module-path'],
            description='The module path of the service implementation.',
        ),
        create_default_cli_argument(
            ['--class-name'],
            description='The class name of the service implementation.',
        ),
        create_default_cli_argument(
            ['--parameters'],
            description='Optional parameters as key=value pairs.',
            type='dict',
        ),
    ],
)

# ** constant: service_set_default_cli_cmd_data
SERVICE_SET_DEFAULT_CLI_CMD_DATA = create_default_cli_command_data(
    'set-default',
    'service',
    'Set Default Service Configuration',
    description='Set or update the default type for a service configuration.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The service registration identifier.',
        ),
        create_default_cli_argument(
            ['--module-path'],
            description='The new default module path.',
        ),
        create_default_cli_argument(
            ['--class-name'],
            description='The new default class name.',
        ),
        create_default_cli_argument(
            ['--parameters'],
            description='Optional parameters as key=value pairs.',
            type='dict',
        ),
    ],
)

# ** constant: service_set_dependency_cli_cmd_data
SERVICE_SET_DEPENDENCY_CLI_CMD_DATA = create_default_cli_command_data(
    'set-dependency',
    'service',
    'Set Service Dependency',
    description='Set or update a flagged dependency on a service configuration.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The service registration identifier.',
        ),
        create_default_cli_argument(
            ['flag'],
            description='The flag identifying this dependency.',
        ),
        create_default_cli_argument(
            ['module_path'],
            description='The module path for the flagged dependency.',
        ),
        create_default_cli_argument(
            ['class_name'],
            description='The class name for the flagged dependency.',
        ),
        create_default_cli_argument(
            ['--parameters'],
            description='Optional parameters as key=value pairs.',
            type='dict',
        ),
    ],
)

# ** constant: service_remove_dependency_cli_cmd_data
SERVICE_REMOVE_DEPENDENCY_CLI_CMD_DATA = create_default_cli_command_data(
    'remove-dependency',
    'service',
    'Remove Service Dependency',
    description='Remove a flagged dependency from a service configuration.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The service registration identifier.',
        ),
        create_default_cli_argument(
            ['flag'],
            description='The flag identifying the dependency to remove.',
        ),
    ],
)

# ** constant: service_set_constants_cli_cmd_data
SERVICE_SET_CONSTANTS_CLI_CMD_DATA = create_default_cli_command_data(
    'set-constants',
    'service',
    'Set Service Constants',
    description='Set or clear service-level constants.',
    arguments=[
        create_default_cli_argument(
            ['--constants'],
            description='Optional constants as key=value pairs. Omit to clear all.',
            type='dict',
        ),
    ],
)

# ** constant: service_remove_cli_cmd_data
SERVICE_REMOVE_CLI_CMD_DATA = create_default_cli_command_data(
    'remove',
    'service',
    'Remove Service Configuration',
    description='Remove a service configuration by ID.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The service registration identifier to remove.',
        ),
    ],
)

# ** constant: logging_add_formatter_cli_cmd_data
LOGGING_ADD_FORMATTER_CLI_CMD_DATA = create_default_cli_command_data(
    'add-formatter',
    'logging',
    'Add Formatter',
    description='Add a new logging formatter configuration.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='Unique formatter identifier.',
        ),
        create_default_cli_argument(
            ['name'],
            description='Formatter name.',
        ),
        create_default_cli_argument(
            ['format'],
            description='Format string for log messages.',
        ),
        create_default_cli_argument(
            ['--description'],
            description='Optional description.',
        ),
        create_default_cli_argument(
            ['--datefmt'],
            description='Optional date format string.',
        ),
    ],
)

# ** constant: logging_remove_formatter_cli_cmd_data
LOGGING_REMOVE_FORMATTER_CLI_CMD_DATA = create_default_cli_command_data(
    'remove-formatter',
    'logging',
    'Remove Formatter',
    description='Remove a logging formatter by ID.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The formatter identifier to remove.',
        ),
    ],
)

# ** constant: logging_add_handler_cli_cmd_data
LOGGING_ADD_HANDLER_CLI_CMD_DATA = create_default_cli_command_data(
    'add-handler',
    'logging',
    'Add Handler',
    description='Add a new logging handler configuration.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='Unique handler identifier.',
        ),
        create_default_cli_argument(
            ['name'],
            description='Handler name.',
        ),
        create_default_cli_argument(
            ['module_path'],
            description='Module path of the handler class.',
        ),
        create_default_cli_argument(
            ['class_name'],
            description='Handler class name.',
        ),
        create_default_cli_argument(
            ['level'],
            description='Logging level.',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        ),
        create_default_cli_argument(
            ['formatter'],
            description='Formatter ID to use.',
        ),
        create_default_cli_argument(
            ['--description'],
            description='Optional description.',
        ),
        create_default_cli_argument(
            ['--stream'],
            description='Optional stream specification.',
        ),
        create_default_cli_argument(
            ['--filename'],
            description='Optional filename for FileHandler.',
        ),
    ],
)

# ** constant: logging_remove_handler_cli_cmd_data
LOGGING_REMOVE_HANDLER_CLI_CMD_DATA = create_default_cli_command_data(
    'remove-handler',
    'logging',
    'Remove Handler',
    description='Remove a logging handler by ID.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The handler identifier to remove.',
        ),
    ],
)

# ** constant: logging_add_logger_cli_cmd_data
LOGGING_ADD_LOGGER_CLI_CMD_DATA = create_default_cli_command_data(
    'add-logger',
    'logging',
    'Add Logger',
    description='Add a new logger configuration.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='Unique logger identifier.',
        ),
        create_default_cli_argument(
            ['name'],
            description='Logger name.',
        ),
        create_default_cli_argument(
            ['level'],
            description='Logging level.',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        ),
        create_default_cli_argument(
            ['handlers'],
            description='Comma-separated list of handler IDs.',
        ),
        create_default_cli_argument(
            ['--description'],
            description='Optional description.',
        ),
        create_default_cli_argument(
            ['--no-propagate'],
            description='Disable message propagation.',
            type='bool',
        ),
    ],
)

# ** constant: logging_remove_logger_cli_cmd_data
LOGGING_REMOVE_LOGGER_CLI_CMD_DATA = create_default_cli_command_data(
    'remove-logger',
    'logging',
    'Remove Logger',
    description='Remove a logger by ID.',
    arguments=[
        create_default_cli_argument(
            ['id'],
            description='The logger identifier to remove.',
        ),
    ],
)

# ** constant: logging_list_cli_cmd_data
LOGGING_LIST_CLI_CMD_DATA = create_default_cli_command_data(
    'list',
    'logging',
    'List Logging Configs',
    description='List all logging configurations (formatters, handlers, loggers).',
)

# *** constants (groups)

# ** constant: admin_default_commands
ADMIN_DEFAULT_COMMANDS: Dict[str, Dict[str, Any]] = {
    APP_ADD_CLI_CMD_ID: APP_ADD_CLI_CMD_DATA,
    APP_GET_CLI_CMD_ID: APP_GET_CLI_CMD_DATA,
    APP_LIST_CLI_CMD_ID: APP_LIST_CLI_CMD_DATA,
    APP_UPDATE_CLI_CMD_ID: APP_UPDATE_CLI_CMD_DATA,
    APP_SET_CONSTANTS_CLI_CMD_ID: APP_SET_CONSTANTS_CLI_CMD_DATA,
    APP_SET_SERVICE_CLI_CMD_ID: APP_SET_SERVICE_CLI_CMD_DATA,
    APP_REMOVE_SERVICE_CLI_CMD_ID: APP_REMOVE_SERVICE_CLI_CMD_DATA,
    APP_REMOVE_CLI_CMD_ID: APP_REMOVE_CLI_CMD_DATA,
    CLI_ADD_COMMAND_CLI_CMD_ID: CLI_ADD_COMMAND_CLI_CMD_DATA,
    CLI_LIST_COMMANDS_CLI_CMD_ID: CLI_LIST_COMMANDS_CLI_CMD_DATA,
    CLI_ADD_ARGUMENT_CLI_CMD_ID: CLI_ADD_ARGUMENT_CLI_CMD_DATA,
    ERROR_ADD_CLI_CMD_ID: ERROR_ADD_CLI_CMD_DATA,
    ERROR_GET_CLI_CMD_ID: ERROR_GET_CLI_CMD_DATA,
    ERROR_LIST_CLI_CMD_ID: ERROR_LIST_CLI_CMD_DATA,
    ERROR_RENAME_CLI_CMD_ID: ERROR_RENAME_CLI_CMD_DATA,
    ERROR_SET_MESSAGE_CLI_CMD_ID: ERROR_SET_MESSAGE_CLI_CMD_DATA,
    ERROR_REMOVE_MESSAGE_CLI_CMD_ID: ERROR_REMOVE_MESSAGE_CLI_CMD_DATA,
    ERROR_REMOVE_CLI_CMD_ID: ERROR_REMOVE_CLI_CMD_DATA,
    FEATURE_ADD_CLI_CMD_ID: FEATURE_ADD_CLI_CMD_DATA,
    FEATURE_GET_CLI_CMD_ID: FEATURE_GET_CLI_CMD_DATA,
    FEATURE_LIST_CLI_CMD_ID: FEATURE_LIST_CLI_CMD_DATA,
    FEATURE_REMOVE_CLI_CMD_ID: FEATURE_REMOVE_CLI_CMD_DATA,
    FEATURE_UPDATE_CLI_CMD_ID: FEATURE_UPDATE_CLI_CMD_DATA,
    FEATURE_ADD_STEP_CLI_CMD_ID: FEATURE_ADD_STEP_CLI_CMD_DATA,
    FEATURE_UPDATE_STEP_CLI_CMD_ID: FEATURE_UPDATE_STEP_CLI_CMD_DATA,
    FEATURE_REMOVE_STEP_CLI_CMD_ID: FEATURE_REMOVE_STEP_CLI_CMD_DATA,
    FEATURE_REORDER_STEP_CLI_CMD_ID: FEATURE_REORDER_STEP_CLI_CMD_DATA,
    SERVICE_ADD_CLI_CMD_ID: SERVICE_ADD_CLI_CMD_DATA,
    SERVICE_LIST_CLI_CMD_ID: SERVICE_LIST_CLI_CMD_DATA,
    SERVICE_SET_DEFAULT_CLI_CMD_ID: SERVICE_SET_DEFAULT_CLI_CMD_DATA,
    SERVICE_SET_DEPENDENCY_CLI_CMD_ID: SERVICE_SET_DEPENDENCY_CLI_CMD_DATA,
    SERVICE_REMOVE_DEPENDENCY_CLI_CMD_ID: SERVICE_REMOVE_DEPENDENCY_CLI_CMD_DATA,
    SERVICE_REMOVE_CLI_CMD_ID: SERVICE_REMOVE_CLI_CMD_DATA,
    SERVICE_SET_CONSTANTS_CLI_CMD_ID: SERVICE_SET_CONSTANTS_CLI_CMD_DATA,
    LOGGING_ADD_FORMATTER_CLI_CMD_ID: LOGGING_ADD_FORMATTER_CLI_CMD_DATA,
    LOGGING_REMOVE_FORMATTER_CLI_CMD_ID: LOGGING_REMOVE_FORMATTER_CLI_CMD_DATA,
    LOGGING_ADD_HANDLER_CLI_CMD_ID: LOGGING_ADD_HANDLER_CLI_CMD_DATA,
    LOGGING_REMOVE_HANDLER_CLI_CMD_ID: LOGGING_REMOVE_HANDLER_CLI_CMD_DATA,
    LOGGING_ADD_LOGGER_CLI_CMD_ID: LOGGING_ADD_LOGGER_CLI_CMD_DATA,
    LOGGING_REMOVE_LOGGER_CLI_CMD_ID: LOGGING_REMOVE_LOGGER_CLI_CMD_DATA,
    LOGGING_LIST_CLI_CMD_ID: LOGGING_LIST_CLI_CMD_DATA,
}
