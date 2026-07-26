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

# ** constant: feature_add_command_id
FEATURE_ADD_COMMAND_ID = 'feature.add'

# ** constant: feature_get_command_id
FEATURE_GET_COMMAND_ID = 'feature.get'

# ** constant: feature_list_command_id
FEATURE_LIST_COMMAND_ID = 'feature.list'

# ** constant: feature_remove_command_id
FEATURE_REMOVE_COMMAND_ID = 'feature.remove'

# ** constant: feature_update_command_id
FEATURE_UPDATE_COMMAND_ID = 'feature.update'

# ** constant: feature_add_step_command_id
FEATURE_ADD_STEP_COMMAND_ID = 'feature.add_step'

# ** constant: feature_update_step_command_id
FEATURE_UPDATE_STEP_COMMAND_ID = 'feature.update_step'

# ** constant: feature_remove_step_command_id
FEATURE_REMOVE_STEP_COMMAND_ID = 'feature.remove_step'

# ** constant: feature_reorder_step_command_id
FEATURE_REORDER_STEP_COMMAND_ID = 'feature.reorder_step'

# ** constant: error_add_command_id
ERROR_ADD_COMMAND_ID = 'error.add'

# ** constant: error_get_command_id
ERROR_GET_COMMAND_ID = 'error.get'

# ** constant: error_list_command_id
ERROR_LIST_COMMAND_ID = 'error.list'

# ** constant: error_rename_command_id
ERROR_RENAME_COMMAND_ID = 'error.rename'

# ** constant: error_set_message_command_id
ERROR_SET_MESSAGE_COMMAND_ID = 'error.set_message'

# ** constant: error_remove_message_command_id
ERROR_REMOVE_MESSAGE_COMMAND_ID = 'error.remove_message'

# ** constant: error_remove_command_id
ERROR_REMOVE_COMMAND_ID = 'error.remove'

# ** constant: service_add_command_id
SERVICE_ADD_COMMAND_ID = 'service.add'

# ** constant: service_list_command_id
SERVICE_LIST_COMMAND_ID = 'service.list'

# ** constant: service_set_default_command_id
SERVICE_SET_DEFAULT_COMMAND_ID = 'service.set_default'

# ** constant: service_set_dependency_command_id
SERVICE_SET_DEPENDENCY_COMMAND_ID = 'service.set_dependency'

# ** constant: service_remove_dependency_command_id
SERVICE_REMOVE_DEPENDENCY_COMMAND_ID = 'service.remove_dependency'

# ** constant: service_remove_command_id
SERVICE_REMOVE_COMMAND_ID = 'service.remove'

# ** constant: service_set_constants_command_id
SERVICE_SET_CONSTANTS_COMMAND_ID = 'service.set_constants'

# ** constant: app_add_command_id
APP_ADD_COMMAND_ID = 'app.add'

# ** constant: app_get_command_id
APP_GET_COMMAND_ID = 'app.get'

# ** constant: app_list_command_id
APP_LIST_COMMAND_ID = 'app.list'

# ** constant: app_update_command_id
APP_UPDATE_COMMAND_ID = 'app.update'

# ** constant: app_set_constants_command_id
APP_SET_CONSTANTS_COMMAND_ID = 'app.set_constants'

# ** constant: app_set_service_command_id
APP_SET_SERVICE_COMMAND_ID = 'app.set_service'

# ** constant: app_remove_service_command_id
APP_REMOVE_SERVICE_COMMAND_ID = 'app.remove_service'

# ** constant: app_remove_command_id
APP_REMOVE_COMMAND_ID = 'app.remove'

# ** constant: cli_add_command_command_id
CLI_ADD_COMMAND_COMMAND_ID = 'cli.add_command'

# ** constant: cli_list_commands_command_id
CLI_LIST_COMMANDS_COMMAND_ID = 'cli.list_commands'

# ** constant: cli_add_argument_command_id
CLI_ADD_ARGUMENT_COMMAND_ID = 'cli.add_argument'

# ** constant: logging_add_formatter_command_id
LOGGING_ADD_FORMATTER_COMMAND_ID = 'logging.add_formatter'

# ** constant: logging_remove_formatter_command_id
LOGGING_REMOVE_FORMATTER_COMMAND_ID = 'logging.remove_formatter'

# ** constant: logging_add_handler_command_id
LOGGING_ADD_HANDLER_COMMAND_ID = 'logging.add_handler'

# ** constant: logging_remove_handler_command_id
LOGGING_REMOVE_HANDLER_COMMAND_ID = 'logging.remove_handler'

# ** constant: logging_add_logger_command_id
LOGGING_ADD_LOGGER_COMMAND_ID = 'logging.add_logger'

# ** constant: logging_remove_logger_command_id
LOGGING_REMOVE_LOGGER_COMMAND_ID = 'logging.remove_logger'

# ** constant: logging_list_command_id
LOGGING_LIST_COMMAND_ID = 'logging.list'

# *** constants (commands)

# ** constant: feature_add_command
FEATURE_ADD_COMMAND = create_default_cli_command(
    FEATURE_ADD_COMMAND_ID,
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

# ** constant: feature_get_command
FEATURE_GET_COMMAND = create_default_cli_command(
    FEATURE_GET_COMMAND_ID,
    'get',
    'feature',
    'Get Feature',
    description='Retrieve a feature by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The feature identifier (e.g. calc.add).'),
    ],
)

# ** constant: feature_list_command
FEATURE_LIST_COMMAND = create_default_cli_command(
    FEATURE_LIST_COMMAND_ID,
    'list',
    'feature',
    'List Features',
    description='List all features, optionally filtered by group.',
    arguments=[
        create_default_cli_argument(['--group-id'], 'Optional group ID to filter results.'),
    ],
)

# ** constant: feature_remove_command
FEATURE_REMOVE_COMMAND = create_default_cli_command(
    FEATURE_REMOVE_COMMAND_ID,
    'remove',
    'feature',
    'Remove Feature',
    description='Remove a feature configuration by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The feature identifier to remove.'),
    ],
)

# ** constant: feature_update_command
FEATURE_UPDATE_COMMAND = create_default_cli_command(
    FEATURE_UPDATE_COMMAND_ID,
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

# ** constant: feature_add_step_command
FEATURE_ADD_STEP_COMMAND = create_default_cli_command(
    FEATURE_ADD_STEP_COMMAND_ID,
    'add-step',
    'feature',
    'Add Feature Step',
    description='Add a step to an existing feature workflow.',
    arguments=[
        create_default_cli_argument(['id'], 'The feature identifier.'),
        create_default_cli_argument(['name'], 'The step name.'),
        create_default_cli_argument(['service_id'], 'The service configuration ID for the step.'),
        create_default_cli_argument(['--parameters'], 'Optional step parameters as JSON string.'),
        create_default_cli_argument(['--data-key'], 'Optional result data key.'),
        create_default_cli_argument(['--position'], 'Insertion position (default: append).', type='int'),
    ],
)

# ** constant: feature_update_step_command
FEATURE_UPDATE_STEP_COMMAND = create_default_cli_command(
    FEATURE_UPDATE_STEP_COMMAND_ID,
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

# ** constant: feature_remove_step_command
FEATURE_REMOVE_STEP_COMMAND = create_default_cli_command(
    FEATURE_REMOVE_STEP_COMMAND_ID,
    'remove-step',
    'feature',
    'Remove Feature Step',
    description='Remove a step from a feature by position.',
    arguments=[
        create_default_cli_argument(['id'], 'The feature identifier.'),
        create_default_cli_argument(['position'], 'The index of the step to remove.', type='int'),
    ],
)

# ** constant: feature_reorder_step_command
FEATURE_REORDER_STEP_COMMAND = create_default_cli_command(
    FEATURE_REORDER_STEP_COMMAND_ID,
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

# ** constant: error_add_command
ERROR_ADD_COMMAND = create_default_cli_command(
    ERROR_ADD_COMMAND_ID,
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

# ** constant: error_get_command
ERROR_GET_COMMAND = create_default_cli_command(
    ERROR_GET_COMMAND_ID,
    'get',
    'error',
    'Get Error',
    description='Retrieve an error by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The error identifier.'),
    ],
)

# ** constant: error_list_command
ERROR_LIST_COMMAND = create_default_cli_command(
    ERROR_LIST_COMMAND_ID,
    'list',
    'error',
    'List Errors',
    description='List all error definitions.',
    arguments=[
        create_default_cli_argument(['--include-defaults'], 'Include built-in default errors.', action='store_true'),
    ],
)

# ** constant: error_rename_command
ERROR_RENAME_COMMAND = create_default_cli_command(
    ERROR_RENAME_COMMAND_ID,
    'rename',
    'error',
    'Rename Error',
    description='Rename an existing error.',
    arguments=[
        create_default_cli_argument(['id'], 'The error identifier.'),
        create_default_cli_argument(['new_name'], 'The new name for the error.'),
    ],
)

# ** constant: error_set_message_command
ERROR_SET_MESSAGE_COMMAND = create_default_cli_command(
    ERROR_SET_MESSAGE_COMMAND_ID,
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

# ** constant: error_remove_message_command
ERROR_REMOVE_MESSAGE_COMMAND = create_default_cli_command(
    ERROR_REMOVE_MESSAGE_COMMAND_ID,
    'remove-message',
    'error',
    'Remove Error Message',
    description='Remove an error message by language.',
    arguments=[
        create_default_cli_argument(['id'], 'The error identifier.'),
        create_default_cli_argument(['--lang'], 'Language code to remove (default: en_US).', default='en_US'),
    ],
)

# ** constant: error_remove_command
ERROR_REMOVE_COMMAND = create_default_cli_command(
    ERROR_REMOVE_COMMAND_ID,
    'remove',
    'error',
    'Remove Error',
    description='Remove an error definition by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The error identifier to remove.'),
    ],
)

# ** constant: service_add_command
SERVICE_ADD_COMMAND = create_default_cli_command(
    SERVICE_ADD_COMMAND_ID,
    'add',
    'service',
    'Add Service Configuration',
    description='Add a new service configuration.',
    arguments=[
        create_default_cli_argument(['id'], 'The unique service configuration identifier.'),
        create_default_cli_argument(['--module-path'], 'Default module path.'),
        create_default_cli_argument(['--class-name'], 'Default class name.'),
        create_default_cli_argument(['--parameters'], 'Configuration parameters as JSON string.'),
        create_default_cli_argument(['--flagged-dependencies'], 'Flagged dependencies as JSON string.'),
    ],
)

# ** constant: service_list_command
SERVICE_LIST_COMMAND = create_default_cli_command(
    SERVICE_LIST_COMMAND_ID,
    'list',
    'service',
    'List All Settings',
    description='List all service configurations and constants.',
)

# ** constant: service_set_default_command
SERVICE_SET_DEFAULT_COMMAND = create_default_cli_command(
    SERVICE_SET_DEFAULT_COMMAND_ID,
    'set-default',
    'service',
    'Set Default Service Configuration',
    description='Set or update the default type for a service configuration.',
    arguments=[
        create_default_cli_argument(['id'], 'The service configuration identifier.'),
        create_default_cli_argument(['--module-path'], 'Default module path.'),
        create_default_cli_argument(['--class-name'], 'Default class name.'),
        create_default_cli_argument(['--parameters'], 'Parameters as JSON string.'),
    ],
)

# ** constant: service_set_dependency_command
SERVICE_SET_DEPENDENCY_COMMAND = create_default_cli_command(
    SERVICE_SET_DEPENDENCY_COMMAND_ID,
    'set-dependency',
    'service',
    'Set Service Dependency',
    description='Set or update a flagged dependency on a service configuration.',
    arguments=[
        create_default_cli_argument(['id'], 'The service configuration identifier.'),
        create_default_cli_argument(['flag'], 'The flag identifying the dependency.'),
        create_default_cli_argument(['module_path'], 'Module path for the dependency.'),
        create_default_cli_argument(['class_name'], 'Class name for the dependency.'),
        create_default_cli_argument(['--parameters'], 'Parameters as JSON string.'),
    ],
)

# ** constant: service_remove_dependency_command
SERVICE_REMOVE_DEPENDENCY_COMMAND = create_default_cli_command(
    SERVICE_REMOVE_DEPENDENCY_COMMAND_ID,
    'remove-dependency',
    'service',
    'Remove Service Dependency',
    description='Remove a flagged dependency from a service configuration.',
    arguments=[
        create_default_cli_argument(['id'], 'The service configuration identifier.'),
        create_default_cli_argument(['flag'], 'The flag identifying the dependency to remove.'),
    ],
)

# ** constant: service_remove_command
SERVICE_REMOVE_COMMAND = create_default_cli_command(
    SERVICE_REMOVE_COMMAND_ID,
    'remove',
    'service',
    'Remove Service Configuration',
    description='Remove a service configuration by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The service configuration identifier to remove.'),
    ],
)

# ** constant: service_set_constants_command
SERVICE_SET_CONSTANTS_COMMAND = create_default_cli_command(
    SERVICE_SET_CONSTANTS_COMMAND_ID,
    'set-constants',
    'service',
    'Set Service Constants',
    description='Set or clear service-level constants.',
    arguments=[
        create_default_cli_argument(['--constants'], 'Constants as JSON string. Omit to clear all.'),
    ],
)

# ** constant: app_add_command
APP_ADD_COMMAND = create_default_cli_command(
    APP_ADD_COMMAND_ID,
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
        create_default_cli_argument(['--services'], 'Service dependencies as JSON string.'),
        create_default_cli_argument(['--constants'], 'Constants as JSON string.'),
    ],
)

# ** constant: app_get_command
APP_GET_COMMAND = create_default_cli_command(
    APP_GET_COMMAND_ID,
    'get',
    'app',
    'Get App Interface',
    description='Retrieve an app interface by ID.',
    arguments=[
        create_default_cli_argument(['interface_id'], 'The interface identifier.'),
    ],
)

# ** constant: app_list_command
APP_LIST_COMMAND = create_default_cli_command(
    APP_LIST_COMMAND_ID,
    'list',
    'app',
    'List App Interfaces',
    description='List all configured app interfaces.',
)

# ** constant: app_update_command
APP_UPDATE_COMMAND = create_default_cli_command(
    APP_UPDATE_COMMAND_ID,
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

# ** constant: app_set_constants_command
APP_SET_CONSTANTS_COMMAND = create_default_cli_command(
    APP_SET_CONSTANTS_COMMAND_ID,
    'set-constants',
    'app',
    'Set App Constants',
    description='Set or clear constants on an app interface.',
    arguments=[
        create_default_cli_argument(['id'], 'The interface identifier.'),
        create_default_cli_argument(['--constants'], 'Constants as JSON string. Omit to clear all.'),
    ],
)

# ** constant: app_set_service_command
APP_SET_SERVICE_COMMAND = create_default_cli_command(
    APP_SET_SERVICE_COMMAND_ID,
    'set-service',
    'app',
    'Set App Service Dependency',
    description='Set or update a service dependency on an app interface.',
    arguments=[
        create_default_cli_argument(['id'], 'The interface identifier.'),
        create_default_cli_argument(['service_id'], 'The service dependency identifier.'),
        create_default_cli_argument(['module_path'], 'Module path for the service.'),
        create_default_cli_argument(['class_name'], 'Class name for the service.'),
        create_default_cli_argument(['--parameters'], 'Parameters as JSON string.'),
    ],
)

# ** constant: app_remove_service_command
APP_REMOVE_SERVICE_COMMAND = create_default_cli_command(
    APP_REMOVE_SERVICE_COMMAND_ID,
    'remove-service',
    'app',
    'Remove App Service Dependency',
    description='Remove a service dependency from an app interface.',
    arguments=[
        create_default_cli_argument(['id'], 'The interface identifier.'),
        create_default_cli_argument(['service_id'], 'The service dependency identifier to remove.'),
    ],
)

# ** constant: app_remove_command
APP_REMOVE_COMMAND = create_default_cli_command(
    APP_REMOVE_COMMAND_ID,
    'remove',
    'app',
    'Remove App Interface',
    description='Remove an app interface by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The interface identifier to remove.'),
    ],
)

# ** constant: cli_add_command_command
CLI_ADD_COMMAND_COMMAND = create_default_cli_command(
    CLI_ADD_COMMAND_COMMAND_ID,
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

# ** constant: cli_list_commands_command
CLI_LIST_COMMANDS_COMMAND = create_default_cli_command(
    CLI_LIST_COMMANDS_COMMAND_ID,
    'list-commands',
    'cli',
    'List CLI Commands',
    description='List all CLI command definitions.',
)

# ** constant: cli_add_argument_command
CLI_ADD_ARGUMENT_COMMAND = create_default_cli_command(
    CLI_ADD_ARGUMENT_COMMAND_ID,
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

# ** constant: logging_add_formatter_command
LOGGING_ADD_FORMATTER_COMMAND = create_default_cli_command(
    LOGGING_ADD_FORMATTER_COMMAND_ID,
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

# ** constant: logging_remove_formatter_command
LOGGING_REMOVE_FORMATTER_COMMAND = create_default_cli_command(
    LOGGING_REMOVE_FORMATTER_COMMAND_ID,
    'remove-formatter',
    'logging',
    'Remove Formatter',
    description='Remove a logging formatter by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The formatter identifier to remove.'),
    ],
)

# ** constant: logging_add_handler_command
LOGGING_ADD_HANDLER_COMMAND = create_default_cli_command(
    LOGGING_ADD_HANDLER_COMMAND_ID,
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

# ** constant: logging_remove_handler_command
LOGGING_REMOVE_HANDLER_COMMAND = create_default_cli_command(
    LOGGING_REMOVE_HANDLER_COMMAND_ID,
    'remove-handler',
    'logging',
    'Remove Handler',
    description='Remove a logging handler by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The handler identifier to remove.'),
    ],
)

# ** constant: logging_add_logger_command
LOGGING_ADD_LOGGER_COMMAND = create_default_cli_command(
    LOGGING_ADD_LOGGER_COMMAND_ID,
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
        create_default_cli_argument(['--no-propagate'], 'Disable message propagation.', action='store_true'),
    ],
)

# ** constant: logging_remove_logger_command
LOGGING_REMOVE_LOGGER_COMMAND = create_default_cli_command(
    LOGGING_REMOVE_LOGGER_COMMAND_ID,
    'remove-logger',
    'logging',
    'Remove Logger',
    description='Remove a logger by ID.',
    arguments=[
        create_default_cli_argument(['id'], 'The logger identifier to remove.'),
    ],
)

# ** constant: logging_list_command
LOGGING_LIST_COMMAND = create_default_cli_command(
    LOGGING_LIST_COMMAND_ID,
    'list',
    'logging',
    'List Logging Configs',
    description='List all logging configurations (formatters, handlers, loggers).',
)

# *** constants (groups)

# ** constant: admin_default_commands
ADMIN_DEFAULT_COMMANDS: Dict[str, Dict[str, Any]] = {
    FEATURE_ADD_COMMAND_ID:           FEATURE_ADD_COMMAND,
    FEATURE_GET_COMMAND_ID:           FEATURE_GET_COMMAND,
    FEATURE_LIST_COMMAND_ID:          FEATURE_LIST_COMMAND,
    FEATURE_REMOVE_COMMAND_ID:        FEATURE_REMOVE_COMMAND,
    FEATURE_UPDATE_COMMAND_ID:        FEATURE_UPDATE_COMMAND,
    FEATURE_ADD_STEP_COMMAND_ID:      FEATURE_ADD_STEP_COMMAND,
    FEATURE_UPDATE_STEP_COMMAND_ID:   FEATURE_UPDATE_STEP_COMMAND,
    FEATURE_REMOVE_STEP_COMMAND_ID:   FEATURE_REMOVE_STEP_COMMAND,
    FEATURE_REORDER_STEP_COMMAND_ID:  FEATURE_REORDER_STEP_COMMAND,
    ERROR_ADD_COMMAND_ID:             ERROR_ADD_COMMAND,
    ERROR_GET_COMMAND_ID:             ERROR_GET_COMMAND,
    ERROR_LIST_COMMAND_ID:            ERROR_LIST_COMMAND,
    ERROR_RENAME_COMMAND_ID:          ERROR_RENAME_COMMAND,
    ERROR_SET_MESSAGE_COMMAND_ID:     ERROR_SET_MESSAGE_COMMAND,
    ERROR_REMOVE_MESSAGE_COMMAND_ID:  ERROR_REMOVE_MESSAGE_COMMAND,
    ERROR_REMOVE_COMMAND_ID:          ERROR_REMOVE_COMMAND,
    SERVICE_ADD_COMMAND_ID:           SERVICE_ADD_COMMAND,
    SERVICE_LIST_COMMAND_ID:          SERVICE_LIST_COMMAND,
    SERVICE_SET_DEFAULT_COMMAND_ID:   SERVICE_SET_DEFAULT_COMMAND,
    SERVICE_SET_DEPENDENCY_COMMAND_ID: SERVICE_SET_DEPENDENCY_COMMAND,
    SERVICE_REMOVE_DEPENDENCY_COMMAND_ID: SERVICE_REMOVE_DEPENDENCY_COMMAND,
    SERVICE_REMOVE_COMMAND_ID:        SERVICE_REMOVE_COMMAND,
    SERVICE_SET_CONSTANTS_COMMAND_ID: SERVICE_SET_CONSTANTS_COMMAND,
    APP_ADD_COMMAND_ID:               APP_ADD_COMMAND,
    APP_GET_COMMAND_ID:               APP_GET_COMMAND,
    APP_LIST_COMMAND_ID:              APP_LIST_COMMAND,
    APP_UPDATE_COMMAND_ID:            APP_UPDATE_COMMAND,
    APP_SET_CONSTANTS_COMMAND_ID:     APP_SET_CONSTANTS_COMMAND,
    APP_SET_SERVICE_COMMAND_ID:       APP_SET_SERVICE_COMMAND,
    APP_REMOVE_SERVICE_COMMAND_ID:    APP_REMOVE_SERVICE_COMMAND,
    APP_REMOVE_COMMAND_ID:            APP_REMOVE_COMMAND,
    CLI_ADD_COMMAND_COMMAND_ID:       CLI_ADD_COMMAND_COMMAND,
    CLI_LIST_COMMANDS_COMMAND_ID:     CLI_LIST_COMMANDS_COMMAND,
    CLI_ADD_ARGUMENT_COMMAND_ID:      CLI_ADD_ARGUMENT_COMMAND,
    LOGGING_ADD_FORMATTER_COMMAND_ID:    LOGGING_ADD_FORMATTER_COMMAND,
    LOGGING_REMOVE_FORMATTER_COMMAND_ID: LOGGING_REMOVE_FORMATTER_COMMAND,
    LOGGING_ADD_HANDLER_COMMAND_ID:      LOGGING_ADD_HANDLER_COMMAND,
    LOGGING_REMOVE_HANDLER_COMMAND_ID:   LOGGING_REMOVE_HANDLER_COMMAND,
    LOGGING_ADD_LOGGER_COMMAND_ID:       LOGGING_ADD_LOGGER_COMMAND,
    LOGGING_REMOVE_LOGGER_COMMAND_ID:    LOGGING_REMOVE_LOGGER_COMMAND,
    LOGGING_LIST_COMMAND_ID:             LOGGING_LIST_COMMAND,
}

