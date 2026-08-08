"""Tiferet Assets CLI Commands

Provides the default CLI command definitions for the built-in Tiferet CLI
management application. Each command maps to a feature workflow defined in
``assets/feature.py`` via the ``group_key.key`` convention.

The blueprint constructs ``CliCommand`` domain objects from these definitions
at startup — they are not loaded from the consumer's config file.
"""

# *** imports

# ** core
from typing import Any, Dict, List

# ** app
from .core import create_default_cli_argument, create_default_cli_command

# *** constants (ids)

# ** constant: app_add_cli_cmd_id
APP_ADD_CLI_CMD_ID = 'app.add'

# ** constant: app_get_cli_cmd_id
APP_GET_CLI_CMD_ID = 'app.get'

# ** constant: app_list_cli_cmd_id
APP_LIST_CLI_CMD_ID = 'app.list'

# ** constant: app_update_cli_cmd_id
APP_UPDATE_CLI_CMD_ID = 'app.update'

# ** constant: app_set_constants_cli_cmd_id
APP_SET_CONSTANTS_CLI_CMD_ID = 'app.set_constants'

# ** constant: app_set_service_cli_cmd_id
APP_SET_SERVICE_CLI_CMD_ID = 'app.set_service'

# ** constant: app_remove_service_cli_cmd_id
APP_REMOVE_SERVICE_CLI_CMD_ID = 'app.remove_service'

# ** constant: app_remove_cli_cmd_id
APP_REMOVE_CLI_CMD_ID = 'app.remove'

# ** constant: cli_add_command_cli_cmd_id
CLI_ADD_COMMAND_CLI_CMD_ID = 'cli.add_command'

# ** constant: cli_list_commands_cli_cmd_id
CLI_LIST_COMMANDS_CLI_CMD_ID = 'cli.list_commands'

# ** constant: cli_add_argument_cli_cmd_id
CLI_ADD_ARGUMENT_CLI_CMD_ID = 'cli.add_argument'

# ** constant: error_add_cli_cmd_id
ERROR_ADD_CLI_CMD_ID = 'error.add'

# ** constant: error_get_cli_cmd_id
ERROR_GET_CLI_CMD_ID = 'error.get'

# ** constant: error_list_cli_cmd_id
ERROR_LIST_CLI_CMD_ID = 'error.list'

# ** constant: error_rename_cli_cmd_id
ERROR_RENAME_CLI_CMD_ID = 'error.rename'

# ** constant: error_set_message_cli_cmd_id
ERROR_SET_MESSAGE_CLI_CMD_ID = 'error.set_message'

# ** constant: error_remove_message_cli_cmd_id
ERROR_REMOVE_MESSAGE_CLI_CMD_ID = 'error.remove_message'

# ** constant: error_remove_cli_cmd_id
ERROR_REMOVE_CLI_CMD_ID = 'error.remove'

# ** constant: feature_add_cli_cmd_id
FEATURE_ADD_CLI_CMD_ID = 'feature.add'

# ** constant: feature_get_cli_cmd_id
FEATURE_GET_CLI_CMD_ID = 'feature.get'

# ** constant: feature_list_cli_cmd_id
FEATURE_LIST_CLI_CMD_ID = 'feature.list'

# ** constant: feature_remove_cli_cmd_id
FEATURE_REMOVE_CLI_CMD_ID = 'feature.remove'

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

# ** constant: service_add_cli_cmd_id
SERVICE_ADD_CLI_CMD_ID = 'service.add'

# ** constant: service_list_cli_cmd_id
SERVICE_LIST_CLI_CMD_ID = 'service.list'

# ** constant: service_set_default_cli_cmd_id
SERVICE_SET_DEFAULT_CLI_CMD_ID = 'service.set_default'

# ** constant: service_set_dependency_cli_cmd_id
SERVICE_SET_DEPENDENCY_CLI_CMD_ID = 'service.set_dependency'

# ** constant: service_remove_dependency_cli_cmd_id
SERVICE_REMOVE_DEPENDENCY_CLI_CMD_ID = 'service.remove_dependency'

# ** constant: service_remove_cli_cmd_id
SERVICE_REMOVE_CLI_CMD_ID = 'service.remove'

# ** constant: service_set_constants_cli_cmd_id
SERVICE_SET_CONSTANTS_CLI_CMD_ID = 'service.set_constants'

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

# ** constant: app_add_cli_cmd
APP_ADD_CLI_CMD = create_default_cli_command(
    APP_ADD_CLI_CMD_ID,
    'add',
    'app',
    'Add App Interface',
    description='Add a new application interface configuration.',
    arguments=[
        create_default_cli_argument(['id'], 'Unique interface identifier.'),
        create_default_cli_argument(['name'], 'Interface name.'),
        create_default_cli_argument(['module_path'], 'Python module path of the context class.'),
        create_default_cli_argument(['class_name'], 'Name of the context class.'),
        create_default_cli_argument(['--description'], 'Optional description.'),
        create_default_cli_argument(['--logger-id'], 'Logger identifier (default: default).', default='default'),
        create_default_cli_argument(['--services'], 'Service dependencies as JSON string.', type='json'),
        create_default_cli_argument(['--constants'], 'Constants as JSON string.', type='json'),
    ],
)

# ** constant: app_get_cli_cmd
APP_GET_CLI_CMD = create_default_cli_command(
    APP_GET_CLI_CMD_ID,
    'get',
    'app',
    'Get App Interface',
    description='Retrieve an app interface by ID.',
    arguments=[
        create_default_cli_argument(['interface_id'], 'The interface identifier.'),
    ],
)

# ** constant: app_list_cli_cmd
APP_LIST_CLI_CMD = create_default_cli_command(
    APP_LIST_CLI_CMD_ID,
    'list',
    'app',
    'List App Interfaces',
    description='List all configured app interfaces.',
)

# ** constant: app_update_cli_cmd
APP_UPDATE_CLI_CMD = create_default_cli_command(
    APP_UPDATE_CLI_CMD_ID,
    'update',
    'app',
    'Update App Interface',
    description='Update a scalar attribute on an app interface.',
    arguments=[
        create_default_cli_argument(['id'], 'The interface identifier.'),
        create_default_cli_argument(['attribute'], 'The attribute to update.'),
        create_default_cli_argument(['value'], 'The new value.'),
    ],
)

# ** constant: app_set_constants_cli_cmd
APP_SET_CONSTANTS_CLI_CMD = create_default_cli_command(
    APP_SET_CONSTANTS_CLI_CMD_ID,
    'set-constants',
    'app',
    'Set App Constants',
    description='Set or clear constants on an app interface.',
    arguments=[
        create_default_cli_argument(['id'], 'The interface identifier.'),
        create_default_cli_argument(['--constants'], 'Constants as JSON string. Omit to clear all.', type='json'),
    ],
)

# ** constant: app_set_service_cli_cmd
APP_SET_SERVICE_CLI_CMD = create_default_cli_command(
    APP_SET_SERVICE_CLI_CMD_ID,
    'set-service',
    'app',
    'Set App Service Dependency',
    description='Set or update a service dependency on an app interface.',
    arguments=[
        create_default_cli_argument(['id'], 'The interface identifier.'),
        create_default_cli_argument(['service_id'], 'The service dependency identifier.'),
        create_default_cli_argument(['module_path'], 'Module path for the service.'),
        create_default_cli_argument(['class_name'], 'Class name for the service.'),
        create_default_cli_argument(['--parameters'], 'Parameters as JSON string.', type='json'),
    ],
)

# ** constant: app_remove_service_cli_cmd
APP_REMOVE_SERVICE_CLI_CMD = create_default_cli_command(
    APP_REMOVE_SERVICE_CLI_CMD_ID,
    'remove-service',
    'app',
    'Remove App Service Dependency',
    description='Remove a service dependency from an app interface.',
    arguments=[
        create_default_cli_argument(['id'], 'The interface identifier.'),
        create_default_cli_argument(['service_id'], 'The service dependency identifier to remove.'),
    ],
)

# ** constant: app_remove_cli_cmd
APP_REMOVE_CLI_CMD = create_default_cli_command(
    APP_REMOVE_CLI_CMD_ID,
    'remove',
    'app',
    'Remove App Interface',
    description='Remove an app interface by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The interface identifier to remove.'),
    ],
)

# ** constant: cli_add_command_cli_cmd
CLI_ADD_COMMAND_CLI_CMD = create_default_cli_command(
    CLI_ADD_COMMAND_CLI_CMD_ID,
    'add-command',
    'cli',
    'Add CLI Command',
    description='Add a new CLI command definition.',
    arguments=[
        create_default_cli_argument(['id'], 'Unique command identifier.'),
        create_default_cli_argument(['name'], 'Command name.'),
        create_default_cli_argument(['key'], 'Command key (used in CLI invocation).'),
        create_default_cli_argument(['group_key'], 'Group key for the command.'),
        create_default_cli_argument(['--description'], 'Optional command description.'),
    ],
)

# ** constant: cli_list_commands_cli_cmd
CLI_LIST_COMMANDS_CLI_CMD = create_default_cli_command(
    CLI_LIST_COMMANDS_CLI_CMD_ID,
    'list-commands',
    'cli',
    'List CLI Commands',
    description='List all CLI command definitions.',
)

# ** constant: cli_add_argument_cli_cmd
CLI_ADD_ARGUMENT_CLI_CMD = create_default_cli_command(
    CLI_ADD_ARGUMENT_CLI_CMD_ID,
    'add-argument',
    'cli',
    'Add CLI Argument',
    description='Add an argument to an existing CLI command.',
    arguments=[
        create_default_cli_argument(['command_id'], 'The CLI command identifier.'),
        create_default_cli_argument(
            ['name_or_flags'],
            'Argument name or flags (comma-separated for multiple flags).',
        ),
        create_default_cli_argument(['--description'], 'Optional argument description.'),
    ],
)

# ** constant: error_add_cli_cmd
ERROR_ADD_CLI_CMD = create_default_cli_command(
    ERROR_ADD_CLI_CMD_ID,
    'add',
    'error',
    'Add Error',
    description='Add a new error definition.',
    arguments=[
        create_default_cli_argument(['id'], 'The unique error identifier.'),
        create_default_cli_argument(['name'], 'The error name.'),
        create_default_cli_argument(['message'], 'The primary error message text.'),
        create_default_cli_argument(['--lang'], 'Language code for the message (default: en_US).', default='en_US'),
    ],
)

# ** constant: error_get_cli_cmd
ERROR_GET_CLI_CMD = create_default_cli_command(
    ERROR_GET_CLI_CMD_ID,
    'get',
    'error',
    'Get Error',
    description='Retrieve an error by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The error identifier.'),
    ],
)

# ** constant: error_list_cli_cmd
ERROR_LIST_CLI_CMD = create_default_cli_command(
    ERROR_LIST_CLI_CMD_ID,
    'list',
    'error',
    'List Errors',
    description='List all error definitions.',
)

# ** constant: error_rename_cli_cmd
ERROR_RENAME_CLI_CMD = create_default_cli_command(
    ERROR_RENAME_CLI_CMD_ID,
    'rename',
    'error',
    'Rename Error',
    description='Rename an existing error.',
    arguments=[
        create_default_cli_argument(['id'], 'The error identifier.'),
        create_default_cli_argument(['new_name'], 'The new name for the error.'),
    ],
)

# ** constant: error_set_message_cli_cmd
ERROR_SET_MESSAGE_CLI_CMD = create_default_cli_command(
    ERROR_SET_MESSAGE_CLI_CMD_ID,
    'set-message',
    'error',
    'Set Error Message',
    description='Set or update an error message for a language.',
    arguments=[
        create_default_cli_argument(['id'], 'The error identifier.'),
        create_default_cli_argument(['message'], 'The message text.'),
        create_default_cli_argument(['--lang'], 'Language code (default: en_US).', default='en_US'),
    ],
)

# ** constant: error_remove_message_cli_cmd
ERROR_REMOVE_MESSAGE_CLI_CMD = create_default_cli_command(
    ERROR_REMOVE_MESSAGE_CLI_CMD_ID,
    'remove-message',
    'error',
    'Remove Error Message',
    description='Remove an error message by language.',
    arguments=[
        create_default_cli_argument(['id'], 'The error identifier.'),
        create_default_cli_argument(['--lang'], 'Language code to remove (default: en_US).', default='en_US'),
    ],
)

# ** constant: error_remove_cli_cmd
ERROR_REMOVE_CLI_CMD = create_default_cli_command(
    ERROR_REMOVE_CLI_CMD_ID,
    'remove',
    'error',
    'Remove Error',
    description='Remove an error definition by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The error identifier to remove.'),
    ],
)

# ** constant: feature_add_cli_cmd
FEATURE_ADD_CLI_CMD = create_default_cli_command(
    FEATURE_ADD_CLI_CMD_ID,
    'add',
    'feature',
    'Add Feature',
    description='Add a new feature configuration.',
    arguments=[
        create_default_cli_argument(['name'], 'The feature name.'),
        create_default_cli_argument(['group_id'], 'The group identifier.'),
        create_default_cli_argument(['--feature-key'], 'Optional explicit feature key.'),
        create_default_cli_argument(['--description'], 'Optional feature description.'),
    ],
)

# ** constant: feature_get_cli_cmd
FEATURE_GET_CLI_CMD = create_default_cli_command(
    FEATURE_GET_CLI_CMD_ID,
    'get',
    'feature',
    'Get Feature',
    description='Retrieve a feature by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The feature identifier (e.g. calc.add).'),
    ],
)

# ** constant: feature_list_cli_cmd
FEATURE_LIST_CLI_CMD = create_default_cli_command(
    FEATURE_LIST_CLI_CMD_ID,
    'list',
    'feature',
    'List Features',
    description='List all features, optionally filtered by group.',
    arguments=[
        create_default_cli_argument(['--group-id'], 'Optional group ID to filter results.'),
    ],
)

# ** constant: feature_remove_cli_cmd
FEATURE_REMOVE_CLI_CMD = create_default_cli_command(
    FEATURE_REMOVE_CLI_CMD_ID,
    'remove',
    'feature',
    'Remove Feature',
    description='Remove a feature configuration by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The feature identifier to remove.'),
    ],
)

# ** constant: feature_update_cli_cmd
FEATURE_UPDATE_CLI_CMD = create_default_cli_command(
    FEATURE_UPDATE_CLI_CMD_ID,
    'update',
    'feature',
    'Update Feature',
    description='Update a feature attribute (name or description).',
    arguments=[
        create_default_cli_argument(['id'], 'The feature identifier.'),
        create_default_cli_argument(['attribute'], 'The attribute to update.', choices=['name', 'description']),
        create_default_cli_argument(['value'], 'The new value for the attribute.'),
    ],
)

# ** constant: feature_add_step_cli_cmd
FEATURE_ADD_STEP_CLI_CMD = create_default_cli_command(
    FEATURE_ADD_STEP_CLI_CMD_ID,
    'add-step',
    'feature',
    'Add Feature Step',
    description='Add a step to an existing feature workflow.',
    arguments=[
        create_default_cli_argument(['id'], 'The feature identifier.'),
        create_default_cli_argument(['name'], 'The step name.'),
        create_default_cli_argument(['service_id'], 'The service configuration ID for the step.'),
        create_default_cli_argument(['--parameters'], 'Optional step parameters as JSON string.', type='json'),
        create_default_cli_argument(['--data-key'], 'Optional result data key.'),
        create_default_cli_argument(['--position'], 'Insertion position (default: append).', type='int'),
    ],
)

# ** constant: feature_update_step_cli_cmd
FEATURE_UPDATE_STEP_CLI_CMD = create_default_cli_command(
    FEATURE_UPDATE_STEP_CLI_CMD_ID,
    'update-step',
    'feature',
    'Update Feature Step',
    description='Update an attribute on a feature step.',
    arguments=[
        create_default_cli_argument(['id'], 'The feature identifier.'),
        create_default_cli_argument(['position'], 'Zero-based index of the step.', type='int'),
        create_default_cli_argument(
            ['attribute'],
            'The attribute to update.',
            choices=['name', 'service_id', 'data_key', 'pass_on_error', 'parameters'],
        ),
        create_default_cli_argument(['value'], 'The new value for the attribute.'),
    ],
)

# ** constant: feature_remove_step_cli_cmd
FEATURE_REMOVE_STEP_CLI_CMD = create_default_cli_command(
    FEATURE_REMOVE_STEP_CLI_CMD_ID,
    'remove-step',
    'feature',
    'Remove Feature Step',
    description='Remove a step from a feature by position.',
    arguments=[
        create_default_cli_argument(['id'], 'The feature identifier.'),
        create_default_cli_argument(['position'], 'The index of the step to remove.', type='int'),
    ],
)

# ** constant: feature_reorder_step_cli_cmd
FEATURE_REORDER_STEP_CLI_CMD = create_default_cli_command(
    FEATURE_REORDER_STEP_CLI_CMD_ID,
    'reorder-step',
    'feature',
    'Reorder Feature Step',
    description='Move a feature step from one position to another.',
    arguments=[
        create_default_cli_argument(['id'], 'The feature identifier.'),
        create_default_cli_argument(['start_position'], 'Current index of the step.', type='int'),
        create_default_cli_argument(['end_position'], 'Desired new index.', type='int'),
    ],
)

# ** constant: service_add_cli_cmd
SERVICE_ADD_CLI_CMD = create_default_cli_command(
    SERVICE_ADD_CLI_CMD_ID,
    'add',
    'service',
    'Add Service Configuration',
    description='Add a new service configuration.',
    arguments=[
        create_default_cli_argument(['id'], 'The unique service configuration identifier.'),
        create_default_cli_argument(['--module-path'], 'Default module path.'),
        create_default_cli_argument(['--class-name'], 'Default class name.'),
        create_default_cli_argument(['--parameters'], 'Configuration parameters as JSON string.', type='json'),
        create_default_cli_argument(['--flagged-dependencies'], 'Flagged dependencies as JSON string.', type='json'),
    ],
)

# ** constant: service_list_cli_cmd
SERVICE_LIST_CLI_CMD = create_default_cli_command(
    SERVICE_LIST_CLI_CMD_ID,
    'list',
    'service',
    'List All Settings',
    description='List all service configurations and constants.',
)

# ** constant: service_set_default_cli_cmd
SERVICE_SET_DEFAULT_CLI_CMD = create_default_cli_command(
    SERVICE_SET_DEFAULT_CLI_CMD_ID,
    'set-default',
    'service',
    'Set Default Service Configuration',
    description='Set or update the default type for a service configuration.',
    arguments=[
        create_default_cli_argument(['id'], 'The service configuration identifier.'),
        create_default_cli_argument(['--module-path'], 'Default module path.'),
        create_default_cli_argument(['--class-name'], 'Default class name.'),
        create_default_cli_argument(['--parameters'], 'Parameters as JSON string.', type='json'),
    ],
)

# ** constant: service_set_dependency_cli_cmd
SERVICE_SET_DEPENDENCY_CLI_CMD = create_default_cli_command(
    SERVICE_SET_DEPENDENCY_CLI_CMD_ID,
    'set-dependency',
    'service',
    'Set Service Dependency',
    description='Set or update a flagged dependency on a service configuration.',
    arguments=[
        create_default_cli_argument(['id'], 'The service configuration identifier.'),
        create_default_cli_argument(['flag'], 'The flag identifying the dependency.'),
        create_default_cli_argument(['module_path'], 'Module path for the dependency.'),
        create_default_cli_argument(['class_name'], 'Class name for the dependency.'),
        create_default_cli_argument(['--parameters'], 'Parameters as JSON string.', type='json'),
    ],
)

# ** constant: service_remove_dependency_cli_cmd
SERVICE_REMOVE_DEPENDENCY_CLI_CMD = create_default_cli_command(
    SERVICE_REMOVE_DEPENDENCY_CLI_CMD_ID,
    'remove-dependency',
    'service',
    'Remove Service Dependency',
    description='Remove a flagged dependency from a service configuration.',
    arguments=[
        create_default_cli_argument(['id'], 'The service configuration identifier.'),
        create_default_cli_argument(['flag'], 'The flag identifying the dependency to remove.'),
    ],
)

# ** constant: service_remove_cli_cmd
SERVICE_REMOVE_CLI_CMD = create_default_cli_command(
    SERVICE_REMOVE_CLI_CMD_ID,
    'remove',
    'service',
    'Remove Service Configuration',
    description='Remove a service configuration by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The service configuration identifier to remove.'),
    ],
)

# ** constant: service_set_constants_cli_cmd
SERVICE_SET_CONSTANTS_CLI_CMD = create_default_cli_command(
    SERVICE_SET_CONSTANTS_CLI_CMD_ID,
    'set-constants',
    'service',
    'Set Service Constants',
    description='Set or clear service-level constants.',
    arguments=[
        create_default_cli_argument(['--constants'], 'Constants as JSON string. Omit to clear all.', type='json'),
    ],
)

# ** constant: logging_add_formatter_cli_cmd
LOGGING_ADD_FORMATTER_CLI_CMD = create_default_cli_command(
    LOGGING_ADD_FORMATTER_CLI_CMD_ID,
    'add-formatter',
    'logging',
    'Add Formatter',
    description='Add a new logging formatter configuration.',
    arguments=[
        create_default_cli_argument(['id'], 'Unique formatter identifier.'),
        create_default_cli_argument(['name'], 'Formatter name.'),
        create_default_cli_argument(['format'], 'Format string for log messages.'),
        create_default_cli_argument(['--description'], 'Optional description.'),
        create_default_cli_argument(['--datefmt'], 'Optional date format string.'),
    ],
)

# ** constant: logging_remove_formatter_cli_cmd
LOGGING_REMOVE_FORMATTER_CLI_CMD = create_default_cli_command(
    LOGGING_REMOVE_FORMATTER_CLI_CMD_ID,
    'remove-formatter',
    'logging',
    'Remove Formatter',
    description='Remove a logging formatter by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The formatter identifier to remove.'),
    ],
)

# ** constant: logging_add_handler_cli_cmd
LOGGING_ADD_HANDLER_CLI_CMD = create_default_cli_command(
    LOGGING_ADD_HANDLER_CLI_CMD_ID,
    'add-handler',
    'logging',
    'Add Handler',
    description='Add a new logging handler configuration.',
    arguments=[
        create_default_cli_argument(['id'], 'Unique handler identifier.'),
        create_default_cli_argument(['name'], 'Handler name.'),
        create_default_cli_argument(['module_path'], 'Module path of the handler class.'),
        create_default_cli_argument(['class_name'], 'Handler class name.'),
        create_default_cli_argument(
            ['level'],
            'Logging level.',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        ),
        create_default_cli_argument(['formatter'], 'Formatter ID to use.'),
        create_default_cli_argument(['--description'], 'Optional description.'),
        create_default_cli_argument(['--stream'], 'Optional stream specification.'),
        create_default_cli_argument(['--filename'], 'Optional filename for FileHandler.'),
    ],
)

# ** constant: logging_remove_handler_cli_cmd
LOGGING_REMOVE_HANDLER_CLI_CMD = create_default_cli_command(
    LOGGING_REMOVE_HANDLER_CLI_CMD_ID,
    'remove-handler',
    'logging',
    'Remove Handler',
    description='Remove a logging handler by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The handler identifier to remove.'),
    ],
)

# ** constant: logging_add_logger_cli_cmd
LOGGING_ADD_LOGGER_CLI_CMD = create_default_cli_command(
    LOGGING_ADD_LOGGER_CLI_CMD_ID,
    'add-logger',
    'logging',
    'Add Logger',
    description='Add a new logger configuration.',
    arguments=[
        create_default_cli_argument(['id'], 'Unique logger identifier.'),
        create_default_cli_argument(['name'], 'Logger name.'),
        create_default_cli_argument(
            ['level'],
            'Logging level.',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        ),
        create_default_cli_argument(['handlers'], 'Comma-separated list of handler IDs.'),
        create_default_cli_argument(['--description'], 'Optional description.'),
        create_default_cli_argument(['--no-propagate'], 'Disable message propagation.', type='bool'),
    ],
)

# ** constant: logging_remove_logger_cli_cmd
LOGGING_REMOVE_LOGGER_CLI_CMD = create_default_cli_command(
    LOGGING_REMOVE_LOGGER_CLI_CMD_ID,
    'remove-logger',
    'logging',
    'Remove Logger',
    description='Remove a logger by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The logger identifier to remove.'),
    ],
)

# ** constant: logging_list_cli_cmd
LOGGING_LIST_CLI_CMD = create_default_cli_command(
    LOGGING_LIST_CLI_CMD_ID,
    'list',
    'logging',
    'List Logging Configs',
    description='List all logging configurations (formatters, handlers, loggers).',
)

# *** constants (groups)

# ** constant: admin_default_commands
ADMIN_DEFAULT_COMMANDS: Dict[str, Dict[str, Any]] = {
    APP_ADD_CLI_CMD_ID:               APP_ADD_CLI_CMD,
    APP_GET_CLI_CMD_ID:               APP_GET_CLI_CMD,
    APP_LIST_CLI_CMD_ID:              APP_LIST_CLI_CMD,
    APP_UPDATE_CLI_CMD_ID:            APP_UPDATE_CLI_CMD,
    APP_SET_CONSTANTS_CLI_CMD_ID:     APP_SET_CONSTANTS_CLI_CMD,
    APP_SET_SERVICE_CLI_CMD_ID:       APP_SET_SERVICE_CLI_CMD,
    APP_REMOVE_SERVICE_CLI_CMD_ID:    APP_REMOVE_SERVICE_CLI_CMD,
    APP_REMOVE_CLI_CMD_ID:            APP_REMOVE_CLI_CMD,
    CLI_ADD_COMMAND_CLI_CMD_ID:       CLI_ADD_COMMAND_CLI_CMD,
    CLI_LIST_COMMANDS_CLI_CMD_ID:     CLI_LIST_COMMANDS_CLI_CMD,
    CLI_ADD_ARGUMENT_CLI_CMD_ID:      CLI_ADD_ARGUMENT_CLI_CMD,
    ERROR_ADD_CLI_CMD_ID:             ERROR_ADD_CLI_CMD,
    ERROR_GET_CLI_CMD_ID:             ERROR_GET_CLI_CMD,
    ERROR_LIST_CLI_CMD_ID:            ERROR_LIST_CLI_CMD,
    ERROR_RENAME_CLI_CMD_ID:          ERROR_RENAME_CLI_CMD,
    ERROR_SET_MESSAGE_CLI_CMD_ID:     ERROR_SET_MESSAGE_CLI_CMD,
    ERROR_REMOVE_MESSAGE_CLI_CMD_ID:  ERROR_REMOVE_MESSAGE_CLI_CMD,
    ERROR_REMOVE_CLI_CMD_ID:          ERROR_REMOVE_CLI_CMD,
    FEATURE_ADD_CLI_CMD_ID:           FEATURE_ADD_CLI_CMD,
    FEATURE_GET_CLI_CMD_ID:           FEATURE_GET_CLI_CMD,
    FEATURE_LIST_CLI_CMD_ID:          FEATURE_LIST_CLI_CMD,
    FEATURE_REMOVE_CLI_CMD_ID:        FEATURE_REMOVE_CLI_CMD,
    FEATURE_UPDATE_CLI_CMD_ID:        FEATURE_UPDATE_CLI_CMD,
    FEATURE_ADD_STEP_CLI_CMD_ID:      FEATURE_ADD_STEP_CLI_CMD,
    FEATURE_UPDATE_STEP_CLI_CMD_ID:   FEATURE_UPDATE_STEP_CLI_CMD,
    FEATURE_REMOVE_STEP_CLI_CMD_ID:   FEATURE_REMOVE_STEP_CLI_CMD,
    FEATURE_REORDER_STEP_CLI_CMD_ID:  FEATURE_REORDER_STEP_CLI_CMD,
    SERVICE_ADD_CLI_CMD_ID:           SERVICE_ADD_CLI_CMD,
    SERVICE_LIST_CLI_CMD_ID:          SERVICE_LIST_CLI_CMD,
    SERVICE_SET_DEFAULT_CLI_CMD_ID:   SERVICE_SET_DEFAULT_CLI_CMD,
    SERVICE_SET_DEPENDENCY_CLI_CMD_ID: SERVICE_SET_DEPENDENCY_CLI_CMD,
    SERVICE_REMOVE_DEPENDENCY_CLI_CMD_ID: SERVICE_REMOVE_DEPENDENCY_CLI_CMD,
    SERVICE_REMOVE_CLI_CMD_ID:        SERVICE_REMOVE_CLI_CMD,
    SERVICE_SET_CONSTANTS_CLI_CMD_ID: SERVICE_SET_CONSTANTS_CLI_CMD,
    LOGGING_ADD_FORMATTER_CLI_CMD_ID:    LOGGING_ADD_FORMATTER_CLI_CMD,
    LOGGING_REMOVE_FORMATTER_CLI_CMD_ID: LOGGING_REMOVE_FORMATTER_CLI_CMD,
    LOGGING_ADD_HANDLER_CLI_CMD_ID:      LOGGING_ADD_HANDLER_CLI_CMD,
    LOGGING_REMOVE_HANDLER_CLI_CMD_ID:   LOGGING_REMOVE_HANDLER_CLI_CMD,
    LOGGING_ADD_LOGGER_CLI_CMD_ID:       LOGGING_ADD_LOGGER_CLI_CMD,
    LOGGING_REMOVE_LOGGER_CLI_CMD_ID:    LOGGING_REMOVE_LOGGER_CLI_CMD,
    LOGGING_LIST_CLI_CMD_ID:             LOGGING_LIST_CLI_CMD,
}

