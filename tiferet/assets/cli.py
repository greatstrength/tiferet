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
APP_LIST_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='list',
    group_key='app',
    name='List App Interfaces',
    description='List all configured application interfaces.',
)

# ** constant: app_get_cli_cmd_data
APP_GET_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='get',
    group_key='app',
    name='Get App Interface',
    description='Retrieve an app interface by ID.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['interface_id'],
            description='The interface identifier.',
        ),
    ],
)

# ** constant: app_add_cli_cmd_data
APP_ADD_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='add',
    group_key='app',
    name='Add App Interface',
    description='Add a new application interface configuration.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The unique interface identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['name'],
            description='The human-readable interface name.',
        ),
        create_default_cli_argument(
            name_or_flags=['module_path'],
            description='The Python module path of the context class.',
        ),
        create_default_cli_argument(
            name_or_flags=['class_name'],
            description='The context class name.',
        ),
        create_default_cli_argument(
            name_or_flags=['--description'],
            description='Optional interface description.',
        ),
        create_default_cli_argument(
            name_or_flags=['--logger-id'],
            description='Optional logger identifier. Defaults to "default".',
        ),
        create_default_cli_argument(
            name_or_flags=['--flags'],
            description='Optional JSON-encoded list of flags.',
            type='json',
        ),
        create_default_cli_argument(
            name_or_flags=['--constants'],
            description='Optional constants as key=value pairs.',
            type='dict',
        ),
    ],
)

# ** constant: app_update_cli_cmd_data
APP_UPDATE_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='update',
    group_key='app',
    name='Update App Interface',
    description='Update a scalar attribute on an existing application interface.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The interface identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['attribute'],
            description='The attribute to update.',
        ),
        create_default_cli_argument(
            name_or_flags=['value'],
            description='The new value for the attribute.',
        ),
    ],
)

# ** constant: app_set_service_cli_cmd_data
APP_SET_SERVICE_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='set-service',
    group_key='app',
    name='Set App Service Dependency',
    description='Set or update a service dependency on an application interface.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The interface identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['service_id'],
            description='The service dependency identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['module_path'],
            description='The module path of the service implementation.',
        ),
        create_default_cli_argument(
            name_or_flags=['class_name'],
            description='The class name of the service implementation.',
        ),
        create_default_cli_argument(
            name_or_flags=['--parameters'],
            description='Optional parameters as key=value pairs.',
            type='dict',
        ),
    ],
)

# ** constant: app_remove_service_cli_cmd_data
APP_REMOVE_SERVICE_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='remove-service',
    group_key='app',
    name='Remove App Service Dependency',
    description='Remove a service dependency from an application interface.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The interface identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['service_id'],
            description='The service dependency identifier to remove.',
        ),
    ],
)

# ** constant: app_set_constants_cli_cmd_data
APP_SET_CONSTANTS_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='set-constants',
    group_key='app',
    name='Set App Constants',
    description='Set or clear constants on an application interface.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The interface identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['--constants'],
            description='Optional constants as key=value pairs. Omit to clear all constants.',
            type='dict',
        ),
    ],
)

# ** constant: app_remove_cli_cmd_data
APP_REMOVE_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='remove',
    group_key='app',
    name='Remove App Interface',
    description='Remove an application interface configuration.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The interface identifier to remove.',
        ),
    ],
)

# ** constant: cli_list_commands_cli_cmd_data
CLI_LIST_COMMANDS_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='list-commands',
    group_key='cli',
    name='List CLI Commands',
    description='List all configured CLI commands.',
)

# ** constant: cli_add_command_cli_cmd_data
CLI_ADD_COMMAND_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='add-command',
    group_key='cli',
    name='Add CLI Command',
    description='Add a new CLI command definition.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The unique command identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['name'],
            description='The human-readable command name.',
        ),
        create_default_cli_argument(
            name_or_flags=['key'],
            description='The command key used in the CLI.',
        ),
        create_default_cli_argument(
            name_or_flags=['group_key'],
            description='The group key this command belongs to.',
        ),
        create_default_cli_argument(
            name_or_flags=['--description'],
            description='Optional command description.',
        ),
    ],
)

# ** constant: cli_add_argument_cli_cmd_data
CLI_ADD_ARGUMENT_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='add-argument',
    group_key='cli',
    name='Add CLI Argument',
    description='Add an argument to an existing CLI command.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['command_id'],
            description='The CLI command identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['--name-or-flags'],
            description='JSON-encoded list of argument names or flags.',
            type='json',
            required=True,
        ),
        create_default_cli_argument(
            name_or_flags=['--description'],
            description='Optional argument description.',
        ),
    ],
)

# ** constant: error_list_cli_cmd_data
ERROR_LIST_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='list',
    group_key='error',
    name='List Errors',
    description='List all error definitions.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['--include-defaults'],
            description='Include built-in default error definitions.',
            type='bool',
        ),
    ],
)

# ** constant: error_get_cli_cmd_data
ERROR_GET_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='get',
    group_key='error',
    name='Get Error',
    description='Retrieve an error by ID.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The error identifier.',
        ),
    ],
)

# ** constant: error_add_cli_cmd_data
ERROR_ADD_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='add',
    group_key='error',
    name='Add Error',
    description='Add a new error definition.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The unique error identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['name'],
            description='The human-readable error name.',
        ),
        create_default_cli_argument(
            name_or_flags=['message'],
            description='The primary error message text.',
        ),
        create_default_cli_argument(
            name_or_flags=['--lang'],
            description='Language code for the message. Defaults to "en_US".',
        ),
        create_default_cli_argument(
            name_or_flags=['--additional-messages'],
            description='Additional messages beyond the primary one, as lang=text pairs.',
            type='dict',
        ),
    ],
)

# ** constant: error_rename_cli_cmd_data
ERROR_RENAME_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='rename',
    group_key='error',
    name='Rename Error',
    description='Rename an existing error definition.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The unique error identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['new_name'],
            description='The new error name.',
        ),
    ],
)

# ** constant: error_set_message_cli_cmd_data
ERROR_SET_MESSAGE_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='set-message',
    group_key='error',
    name='Set Error Message',
    description='Set the message text on an existing error definition.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The unique error identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['message'],
            description='The new message text.',
        ),
        create_default_cli_argument(
            name_or_flags=['--lang'],
            description='Language code for the message. Defaults to "en_US".',
        ),
    ],
)

# ** constant: error_remove_message_cli_cmd_data
ERROR_REMOVE_MESSAGE_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='remove-message',
    group_key='error',
    name='Remove Error Message',
    description='Remove a language message from an existing error definition.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The unique error identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['--lang'],
            description='Language code of the message to remove. Defaults to "en_US".',
        ),
    ],
)

# ** constant: error_remove_cli_cmd_data
ERROR_REMOVE_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='remove',
    group_key='error',
    name='Remove Error',
    description='Remove an error definition.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The unique error identifier to remove.',
        ),
    ],
)

# ** constant: feature_list_cli_cmd_data
FEATURE_LIST_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='list',
    group_key='feature',
    name='List Features',
    description='List all feature workflow definitions.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['--group-id'],
            description='Optional group identifier to filter results.',
        ),
    ],
)

# ** constant: feature_add_cli_cmd_data
FEATURE_ADD_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='add',
    group_key='feature',
    name='Add Feature',
    description='Add a new feature workflow definition.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['name'],
            description='The feature name.',
        ),
        create_default_cli_argument(
            name_or_flags=['group_id'],
            description='The group identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['--feature-key'],
            description='Optional explicit feature key. Defaults to snake_case of name.',
        ),
        create_default_cli_argument(
            name_or_flags=['--description'],
            description='Optional feature description.',
        ),
    ],
)

# ** constant: feature_update_cli_cmd_data
FEATURE_UPDATE_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='update',
    group_key='feature',
    name='Update Feature',
    description='Update a metadata attribute on an existing feature.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The feature identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['attribute'],
            description='The attribute to update (name or description).',
        ),
        create_default_cli_argument(
            name_or_flags=['value'],
            description='The new value.',
        ),
    ],
)

# ** constant: feature_add_step_cli_cmd_data
FEATURE_ADD_STEP_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='add-step',
    group_key='feature',
    name='Add Feature Step',
    description='Add a step to an existing feature workflow.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The feature identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['name'],
            description='The step name.',
        ),
        create_default_cli_argument(
            name_or_flags=['service_id'],
            description='The DI service registration identifier for this step.',
        ),
        create_default_cli_argument(
            name_or_flags=['--parameters'],
            description='Optional step parameters as key=value pairs.',
            type='dict',
        ),
        create_default_cli_argument(
            name_or_flags=['--data-key'],
            description='Optional result data key.',
        ),
        create_default_cli_argument(
            name_or_flags=['--pass-on-error'],
            description='Continue execution if this step raises an error.',
            type='bool',
        ),
        create_default_cli_argument(
            name_or_flags=['--position'],
            description='Optional insertion index. Defaults to append.',
            type='int',
        ),
    ],
)

# ** constant: feature_update_step_cli_cmd_data
FEATURE_UPDATE_STEP_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='update-step',
    group_key='feature',
    name='Update Feature Step',
    description='Update an attribute on an existing feature step.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The feature identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['position'],
            description='The zero-based step index.',
            type='int',
        ),
        create_default_cli_argument(
            name_or_flags=['attribute'],
            description='The step attribute to update.',
        ),
        create_default_cli_argument(
            name_or_flags=['--value'],
            description='The new value for the attribute.',
        ),
    ],
)

# ** constant: feature_remove_step_cli_cmd_data
FEATURE_REMOVE_STEP_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='remove-step',
    group_key='feature',
    name='Remove Feature Step',
    description='Remove a step from an existing feature workflow.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The feature identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['position'],
            description='The zero-based index of the step to remove.',
            type='int',
        ),
    ],
)

# ** constant: feature_reorder_step_cli_cmd_data
FEATURE_REORDER_STEP_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='reorder-step',
    group_key='feature',
    name='Reorder Feature Step',
    description='Reorder a step within an existing feature workflow.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The feature identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['start_position'],
            description='The current zero-based step index.',
            type='int',
        ),
        create_default_cli_argument(
            name_or_flags=['end_position'],
            description='The target zero-based step index.',
            type='int',
        ),
    ],
)

# ** constant: feature_remove_cli_cmd_data
FEATURE_REMOVE_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='remove',
    group_key='feature',
    name='Remove Feature',
    description='Remove an existing feature workflow definition.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The feature identifier to remove.',
        ),
    ],
)

# ** constant: service_list_cli_cmd_data
SERVICE_LIST_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='list',
    group_key='service',
    name='List Services',
    description='List all DI service registrations and constants.',
)

# ** constant: service_add_cli_cmd_data
SERVICE_ADD_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='add',
    group_key='service',
    name='Add Service',
    description='Add a new DI service registration.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The unique service registration identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['--module-path'],
            description='The module path of the service implementation.',
        ),
        create_default_cli_argument(
            name_or_flags=['--class-name'],
            description='The class name of the service implementation.',
        ),
        create_default_cli_argument(
            name_or_flags=['--parameters'],
            description='Optional parameters as key=value pairs.',
            type='dict',
        ),
    ],
)

# ** constant: service_set_default_cli_cmd_data
SERVICE_SET_DEFAULT_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='set-default',
    group_key='service',
    name='Set Default Service Registration',
    description='Set or update the default type for an existing service registration.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The service registration identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['--module-path'],
            description='The new default module path.',
        ),
        create_default_cli_argument(
            name_or_flags=['--class-name'],
            description='The new default class name.',
        ),
        create_default_cli_argument(
            name_or_flags=['--parameters'],
            description='Optional parameters as key=value pairs.',
            type='dict',
        ),
    ],
)

# ** constant: service_set_dependency_cli_cmd_data
SERVICE_SET_DEPENDENCY_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='set-dependency',
    group_key='service',
    name='Set Service Dependency',
    description='Set or update a flagged dependency on a service registration.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The service registration identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['flag'],
            description='The flag identifying this dependency.',
        ),
        create_default_cli_argument(
            name_or_flags=['module_path'],
            description='The module path for the flagged dependency.',
        ),
        create_default_cli_argument(
            name_or_flags=['class_name'],
            description='The class name for the flagged dependency.',
        ),
        create_default_cli_argument(
            name_or_flags=['--parameters'],
            description='Optional parameters as key=value pairs.',
            type='dict',
        ),
    ],
)

# ** constant: service_remove_dependency_cli_cmd_data
SERVICE_REMOVE_DEPENDENCY_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='remove-dependency',
    group_key='service',
    name='Remove Service Dependency',
    description='Remove a flagged dependency from a service registration.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The service registration identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['flag'],
            description='The flag identifying the dependency to remove.',
        ),
    ],
)

# ** constant: service_set_constants_cli_cmd_data
SERVICE_SET_CONSTANTS_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='set-constants',
    group_key='service',
    name='Set Service Constants',
    description='Set or clear DI service constants.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['--constants'],
            description='Optional constants as key=value pairs. Omit to clear all.',
            type='dict',
        ),
    ],
)

# ** constant: service_remove_cli_cmd_data
SERVICE_REMOVE_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='remove',
    group_key='service',
    name='Remove Service',
    description='Remove a DI service registration.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The service registration identifier to remove.',
        ),
    ],
)

# ** constant: logging_add_formatter_cli_cmd_data
LOGGING_ADD_FORMATTER_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='add-formatter',
    group_key='logging',
    name='Add Formatter',
    description='Add a new logging formatter configuration.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='Unique formatter identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['name'],
            description='Formatter name.',
        ),
        create_default_cli_argument(
            name_or_flags=['format'],
            description='Format string for log messages.',
        ),
        create_default_cli_argument(
            name_or_flags=['--description'],
            description='Optional description.',
        ),
        create_default_cli_argument(
            name_or_flags=['--datefmt'],
            description='Optional date format string.',
        ),
    ],
)

# ** constant: logging_remove_formatter_cli_cmd_data
LOGGING_REMOVE_FORMATTER_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='remove-formatter',
    group_key='logging',
    name='Remove Formatter',
    description='Remove a logging formatter by ID.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The formatter identifier to remove.',
        ),
    ],
)

# ** constant: logging_add_handler_cli_cmd_data
LOGGING_ADD_HANDLER_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='add-handler',
    group_key='logging',
    name='Add Handler',
    description='Add a new logging handler configuration.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='Unique handler identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['name'],
            description='Handler name.',
        ),
        create_default_cli_argument(
            name_or_flags=['module_path'],
            description='Module path of the handler class.',
        ),
        create_default_cli_argument(
            name_or_flags=['class_name'],
            description='Handler class name.',
        ),
        create_default_cli_argument(
            name_or_flags=['level'],
            description='Logging level.',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        ),
        create_default_cli_argument(
            name_or_flags=['formatter'],
            description='Formatter ID to use.',
        ),
        create_default_cli_argument(
            name_or_flags=['--description'],
            description='Optional description.',
        ),
        create_default_cli_argument(
            name_or_flags=['--stream'],
            description='Optional stream specification.',
        ),
        create_default_cli_argument(
            name_or_flags=['--filename'],
            description='Optional filename for FileHandler.',
        ),
    ],
)

# ** constant: logging_remove_handler_cli_cmd_data
LOGGING_REMOVE_HANDLER_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='remove-handler',
    group_key='logging',
    name='Remove Handler',
    description='Remove a logging handler by ID.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The handler identifier to remove.',
        ),
    ],
)

# ** constant: logging_add_logger_cli_cmd_data
LOGGING_ADD_LOGGER_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='add-logger',
    group_key='logging',
    name='Add Logger',
    description='Add a new logger configuration.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='Unique logger identifier.',
        ),
        create_default_cli_argument(
            name_or_flags=['name'],
            description='Logger name.',
        ),
        create_default_cli_argument(
            name_or_flags=['level'],
            description='Logging level.',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        ),
        create_default_cli_argument(
            name_or_flags=['handlers'],
            description='Comma-separated list of handler IDs.',
        ),
        create_default_cli_argument(
            name_or_flags=['--description'],
            description='Optional description.',
        ),
        create_default_cli_argument(
            name_or_flags=['--no-propagate'],
            description='Disable message propagation.',
            type='bool',
        ),
    ],
)

# ** constant: logging_remove_logger_cli_cmd_data
LOGGING_REMOVE_LOGGER_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='remove-logger',
    group_key='logging',
    name='Remove Logger',
    description='Remove a logger by ID.',
    arguments=[
        create_default_cli_argument(
            name_or_flags=['id'],
            description='The logger identifier to remove.',
        ),
    ],
)

# ** constant: logging_list_cli_cmd_data
LOGGING_LIST_CLI_CMD_DATA: Dict[str, Any] = create_default_cli_command_data(
    key='list',
    group_key='logging',
    name='List Logging Configs',
    description='List all logging configurations (formatters, handlers, loggers).',
)

# *** constants (groups)

# ** constant: admin_default_commands
ADMIN_DEFAULT_COMMANDS: Dict[str, Dict[str, Any]] = {
    APP_LIST_CLI_CMD_ID: APP_LIST_CLI_CMD_DATA,
    APP_GET_CLI_CMD_ID: APP_GET_CLI_CMD_DATA,
    APP_ADD_CLI_CMD_ID: APP_ADD_CLI_CMD_DATA,
    APP_UPDATE_CLI_CMD_ID: APP_UPDATE_CLI_CMD_DATA,
    APP_SET_SERVICE_CLI_CMD_ID: APP_SET_SERVICE_CLI_CMD_DATA,
    APP_REMOVE_SERVICE_CLI_CMD_ID: APP_REMOVE_SERVICE_CLI_CMD_DATA,
    APP_SET_CONSTANTS_CLI_CMD_ID: APP_SET_CONSTANTS_CLI_CMD_DATA,
    APP_REMOVE_CLI_CMD_ID: APP_REMOVE_CLI_CMD_DATA,
    CLI_LIST_COMMANDS_CLI_CMD_ID: CLI_LIST_COMMANDS_CLI_CMD_DATA,
    CLI_ADD_COMMAND_CLI_CMD_ID: CLI_ADD_COMMAND_CLI_CMD_DATA,
    CLI_ADD_ARGUMENT_CLI_CMD_ID: CLI_ADD_ARGUMENT_CLI_CMD_DATA,
    ERROR_LIST_CLI_CMD_ID: ERROR_LIST_CLI_CMD_DATA,
    ERROR_GET_CLI_CMD_ID: ERROR_GET_CLI_CMD_DATA,
    ERROR_ADD_CLI_CMD_ID: ERROR_ADD_CLI_CMD_DATA,
    ERROR_RENAME_CLI_CMD_ID: ERROR_RENAME_CLI_CMD_DATA,
    ERROR_SET_MESSAGE_CLI_CMD_ID: ERROR_SET_MESSAGE_CLI_CMD_DATA,
    ERROR_REMOVE_MESSAGE_CLI_CMD_ID: ERROR_REMOVE_MESSAGE_CLI_CMD_DATA,
    ERROR_REMOVE_CLI_CMD_ID: ERROR_REMOVE_CLI_CMD_DATA,
    FEATURE_LIST_CLI_CMD_ID: FEATURE_LIST_CLI_CMD_DATA,
    FEATURE_ADD_CLI_CMD_ID: FEATURE_ADD_CLI_CMD_DATA,
    FEATURE_UPDATE_CLI_CMD_ID: FEATURE_UPDATE_CLI_CMD_DATA,
    FEATURE_ADD_STEP_CLI_CMD_ID: FEATURE_ADD_STEP_CLI_CMD_DATA,
    FEATURE_UPDATE_STEP_CLI_CMD_ID: FEATURE_UPDATE_STEP_CLI_CMD_DATA,
    FEATURE_REMOVE_STEP_CLI_CMD_ID: FEATURE_REMOVE_STEP_CLI_CMD_DATA,
    FEATURE_REORDER_STEP_CLI_CMD_ID: FEATURE_REORDER_STEP_CLI_CMD_DATA,
    FEATURE_REMOVE_CLI_CMD_ID: FEATURE_REMOVE_CLI_CMD_DATA,
    SERVICE_LIST_CLI_CMD_ID: SERVICE_LIST_CLI_CMD_DATA,
    SERVICE_ADD_CLI_CMD_ID: SERVICE_ADD_CLI_CMD_DATA,
    SERVICE_SET_DEFAULT_CLI_CMD_ID: SERVICE_SET_DEFAULT_CLI_CMD_DATA,
    SERVICE_SET_DEPENDENCY_CLI_CMD_ID: SERVICE_SET_DEPENDENCY_CLI_CMD_DATA,
    SERVICE_REMOVE_DEPENDENCY_CLI_CMD_ID: SERVICE_REMOVE_DEPENDENCY_CLI_CMD_DATA,
    SERVICE_SET_CONSTANTS_CLI_CMD_ID: SERVICE_SET_CONSTANTS_CLI_CMD_DATA,
    SERVICE_REMOVE_CLI_CMD_ID: SERVICE_REMOVE_CLI_CMD_DATA,
    LOGGING_ADD_FORMATTER_CLI_CMD_ID: LOGGING_ADD_FORMATTER_CLI_CMD_DATA,
    LOGGING_REMOVE_FORMATTER_CLI_CMD_ID: LOGGING_REMOVE_FORMATTER_CLI_CMD_DATA,
    LOGGING_ADD_HANDLER_CLI_CMD_ID: LOGGING_ADD_HANDLER_CLI_CMD_DATA,
    LOGGING_REMOVE_HANDLER_CLI_CMD_ID: LOGGING_REMOVE_HANDLER_CLI_CMD_DATA,
    LOGGING_ADD_LOGGER_CLI_CMD_ID: LOGGING_ADD_LOGGER_CLI_CMD_DATA,
    LOGGING_REMOVE_LOGGER_CLI_CMD_ID: LOGGING_REMOVE_LOGGER_CLI_CMD_DATA,
    LOGGING_LIST_CLI_CMD_ID: LOGGING_LIST_CLI_CMD_DATA,
}
