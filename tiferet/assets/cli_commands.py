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

# *** constants

# ** constant: default_tiferet_cli_command_list
# Each dict matches the CliCommand domain object constructor fields.
# Arguments use CliArgument field names: name_or_flags, description, type, default, required, nargs, choices, action.
_DEFAULT_TIFERET_CLI_COMMAND_LIST: List[Dict[str, Any]] = [

    # * commands: feature domain

    {
        'id': 'feature.add',
        'key': 'add',
        'group_key': 'feature',
        'name': 'Add Feature',
        'description': 'Add a new feature configuration.',
        'arguments': [
            {'name_or_flags': ['name'], 'description': 'The feature name.'},
            {'name_or_flags': ['group_id'], 'description': 'The group identifier.'},
            {'name_or_flags': ['--feature-key'], 'description': 'Optional explicit feature key.'},
            {'name_or_flags': ['--description'], 'description': 'Optional feature description.'},
        ],
    },
    {
        'id': 'feature.get',
        'key': 'get',
        'group_key': 'feature',
        'name': 'Get Feature',
        'description': 'Retrieve a feature by ID.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The feature identifier (e.g. calc.add).'},
        ],
    },
    {
        'id': 'feature.list',
        'key': 'list',
        'group_key': 'feature',
        'name': 'List Features',
        'description': 'List all features, optionally filtered by group.',
        'arguments': [
            {'name_or_flags': ['--group-id'], 'description': 'Optional group ID to filter results.'},
        ],
    },
    {
        'id': 'feature.remove',
        'key': 'remove',
        'group_key': 'feature',
        'name': 'Remove Feature',
        'description': 'Remove a feature configuration by ID.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The feature identifier to remove.'},
        ],
    },
    {
        'id': 'feature.update',
        'key': 'update',
        'group_key': 'feature',
        'name': 'Update Feature',
        'description': 'Update a feature attribute (name or description).',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The feature identifier.'},
            {'name_or_flags': ['attribute'], 'description': 'The attribute to update.', 'choices': ['name', 'description']},
            {'name_or_flags': ['value'], 'description': 'The new value for the attribute.'},
        ],
    },
    {
        'id': 'feature.add_step',
        'key': 'add-step',
        'group_key': 'feature',
        'name': 'Add Feature Step',
        'description': 'Add a step to an existing feature workflow.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The feature identifier.'},
            {'name_or_flags': ['name'], 'description': 'The step name.'},
            {'name_or_flags': ['service_id'], 'description': 'The service configuration ID for the step.'},
            {'name_or_flags': ['--parameters'], 'description': 'Optional step parameters as JSON string.'},
            {'name_or_flags': ['--data-key'], 'description': 'Optional result data key.'},
            {'name_or_flags': ['--position'], 'description': 'Insertion position (default: append).', 'type': 'int'},
        ],
    },
    {
        'id': 'feature.update_step',
        'key': 'update-step',
        'group_key': 'feature',
        'name': 'Update Feature Step',
        'description': 'Update an attribute on a feature step.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The feature identifier.'},
            {'name_or_flags': ['position'], 'description': 'Zero-based index of the step.', 'type': 'int'},
            {'name_or_flags': ['attribute'], 'description': 'The attribute to update.', 'choices': ['name', 'service_id', 'data_key', 'pass_on_error', 'parameters']},
            {'name_or_flags': ['value'], 'description': 'The new value for the attribute.'},
        ],
    },
    {
        'id': 'feature.remove_step',
        'key': 'remove-step',
        'group_key': 'feature',
        'name': 'Remove Feature Step',
        'description': 'Remove a step from a feature by position.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The feature identifier.'},
            {'name_or_flags': ['position'], 'description': 'The index of the step to remove.', 'type': 'int'},
        ],
    },
    {
        'id': 'feature.reorder_step',
        'key': 'reorder-step',
        'group_key': 'feature',
        'name': 'Reorder Feature Step',
        'description': 'Move a feature step from one position to another.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The feature identifier.'},
            {'name_or_flags': ['start_position'], 'description': 'Current index of the step.', 'type': 'int'},
            {'name_or_flags': ['end_position'], 'description': 'Desired new index.', 'type': 'int'},
        ],
    },

    # * commands: error domain

    {
        'id': 'error.add',
        'key': 'add',
        'group_key': 'error',
        'name': 'Add Error',
        'description': 'Add a new error definition.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The unique error identifier.'},
            {'name_or_flags': ['name'], 'description': 'The error name.'},
            {'name_or_flags': ['message'], 'description': 'The primary error message text.'},
            {'name_or_flags': ['--lang'], 'description': 'Language code for the message (default: en_US).', 'default': 'en_US'},
        ],
    },
    {
        'id': 'error.get',
        'key': 'get',
        'group_key': 'error',
        'name': 'Get Error',
        'description': 'Retrieve an error by ID.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The error identifier.'},
        ],
    },
    {
        'id': 'error.list',
        'key': 'list',
        'group_key': 'error',
        'name': 'List Errors',
        'description': 'List all error definitions.',
        'arguments': [
            {'name_or_flags': ['--include-defaults'], 'description': 'Include built-in default errors.', 'action': 'store_true'},
        ],
    },
    {
        'id': 'error.rename',
        'key': 'rename',
        'group_key': 'error',
        'name': 'Rename Error',
        'description': 'Rename an existing error.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The error identifier.'},
            {'name_or_flags': ['new_name'], 'description': 'The new name for the error.'},
        ],
    },
    {
        'id': 'error.set_message',
        'key': 'set-message',
        'group_key': 'error',
        'name': 'Set Error Message',
        'description': 'Set or update an error message for a language.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The error identifier.'},
            {'name_or_flags': ['message'], 'description': 'The message text.'},
            {'name_or_flags': ['--lang'], 'description': 'Language code (default: en_US).', 'default': 'en_US'},
        ],
    },
    {
        'id': 'error.remove_message',
        'key': 'remove-message',
        'group_key': 'error',
        'name': 'Remove Error Message',
        'description': 'Remove an error message by language.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The error identifier.'},
            {'name_or_flags': ['--lang'], 'description': 'Language code to remove (default: en_US).', 'default': 'en_US'},
        ],
    },
    {
        'id': 'error.remove',
        'key': 'remove',
        'group_key': 'error',
        'name': 'Remove Error',
        'description': 'Remove an error definition by ID.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The error identifier to remove.'},
        ],
    },

    # * commands: service (DI) domain

    {
        'id': 'service.add',
        'key': 'add',
        'group_key': 'service',
        'name': 'Add Service Configuration',
        'description': 'Add a new service configuration.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The unique service configuration identifier.'},
            {'name_or_flags': ['--module-path'], 'description': 'Default module path.'},
            {'name_or_flags': ['--class-name'], 'description': 'Default class name.'},
            {'name_or_flags': ['--parameters'], 'description': 'Configuration parameters as JSON string.'},
            {'name_or_flags': ['--flagged-dependencies'], 'description': 'Flagged dependencies as JSON string.'},
        ],
    },
    {
        'id': 'service.list',
        'key': 'list',
        'group_key': 'service',
        'name': 'List All Settings',
        'description': 'List all service configurations and constants.',
        'arguments': [],
    },
    {
        'id': 'service.set_default',
        'key': 'set-default',
        'group_key': 'service',
        'name': 'Set Default Service Configuration',
        'description': 'Set or update the default type for a service configuration.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The service configuration identifier.'},
            {'name_or_flags': ['--module-path'], 'description': 'Default module path.'},
            {'name_or_flags': ['--class-name'], 'description': 'Default class name.'},
            {'name_or_flags': ['--parameters'], 'description': 'Parameters as JSON string.'},
        ],
    },
    {
        'id': 'service.set_dependency',
        'key': 'set-dependency',
        'group_key': 'service',
        'name': 'Set Service Dependency',
        'description': 'Set or update a flagged dependency on a service configuration.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The service configuration identifier.'},
            {'name_or_flags': ['flag'], 'description': 'The flag identifying the dependency.'},
            {'name_or_flags': ['module_path'], 'description': 'Module path for the dependency.'},
            {'name_or_flags': ['class_name'], 'description': 'Class name for the dependency.'},
            {'name_or_flags': ['--parameters'], 'description': 'Parameters as JSON string.'},
        ],
    },
    {
        'id': 'service.remove_dependency',
        'key': 'remove-dependency',
        'group_key': 'service',
        'name': 'Remove Service Dependency',
        'description': 'Remove a flagged dependency from a service configuration.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The service configuration identifier.'},
            {'name_or_flags': ['flag'], 'description': 'The flag identifying the dependency to remove.'},
        ],
    },
    {
        'id': 'service.remove',
        'key': 'remove',
        'group_key': 'service',
        'name': 'Remove Service Configuration',
        'description': 'Remove a service configuration by ID.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The service configuration identifier to remove.'},
        ],
    },
    {
        'id': 'service.set_constants',
        'key': 'set-constants',
        'group_key': 'service',
        'name': 'Set Service Constants',
        'description': 'Set or clear service-level constants.',
        'arguments': [
            {'name_or_flags': ['--constants'], 'description': 'Constants as JSON string. Omit to clear all.'},
        ],
    },

    # * commands: app interface domain

    {
        'id': 'app.add',
        'key': 'add',
        'group_key': 'app',
        'name': 'Add App Interface',
        'description': 'Add a new application interface configuration.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'Unique interface identifier.'},
            {'name_or_flags': ['name'], 'description': 'Interface name.'},
            {'name_or_flags': ['module_path'], 'description': 'Python module path of the context class.'},
            {'name_or_flags': ['class_name'], 'description': 'Name of the context class.'},
            {'name_or_flags': ['--description'], 'description': 'Optional description.'},
            {'name_or_flags': ['--logger-id'], 'description': 'Logger identifier (default: default).', 'default': 'default'},
            {'name_or_flags': ['--services'], 'description': 'Service dependencies as JSON string.'},
            {'name_or_flags': ['--constants'], 'description': 'Constants as JSON string.'},
        ],
    },
    {
        'id': 'app.get',
        'key': 'get',
        'group_key': 'app',
        'name': 'Get App Interface',
        'description': 'Retrieve an app interface by ID.',
        'arguments': [
            {'name_or_flags': ['interface_id'], 'description': 'The interface identifier.'},
        ],
    },
    {
        'id': 'app.list',
        'key': 'list',
        'group_key': 'app',
        'name': 'List App Interfaces',
        'description': 'List all configured app interfaces.',
        'arguments': [],
    },
    {
        'id': 'app.update',
        'key': 'update',
        'group_key': 'app',
        'name': 'Update App Interface',
        'description': 'Update a scalar attribute on an app interface.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The interface identifier.'},
            {'name_or_flags': ['attribute'], 'description': 'The attribute to update.'},
            {'name_or_flags': ['value'], 'description': 'The new value.'},
        ],
    },
    {
        'id': 'app.set_constants',
        'key': 'set-constants',
        'group_key': 'app',
        'name': 'Set App Constants',
        'description': 'Set or clear constants on an app interface.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The interface identifier.'},
            {'name_or_flags': ['--constants'], 'description': 'Constants as JSON string. Omit to clear all.'},
        ],
    },
    {
        'id': 'app.set_service',
        'key': 'set-service',
        'group_key': 'app',
        'name': 'Set App Service Dependency',
        'description': 'Set or update a service dependency on an app interface.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The interface identifier.'},
            {'name_or_flags': ['service_id'], 'description': 'The service dependency identifier.'},
            {'name_or_flags': ['module_path'], 'description': 'Module path for the service.'},
            {'name_or_flags': ['class_name'], 'description': 'Class name for the service.'},
            {'name_or_flags': ['--parameters'], 'description': 'Parameters as JSON string.'},
        ],
    },
    {
        'id': 'app.remove_service',
        'key': 'remove-service',
        'group_key': 'app',
        'name': 'Remove App Service Dependency',
        'description': 'Remove a service dependency from an app interface.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The interface identifier.'},
            {'name_or_flags': ['service_id'], 'description': 'The service dependency identifier to remove.'},
        ],
    },
    {
        'id': 'app.remove',
        'key': 'remove',
        'group_key': 'app',
        'name': 'Remove App Interface',
        'description': 'Remove an app interface by ID.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The interface identifier to remove.'},
        ],
    },

    # * commands: cli domain

    {
        'id': 'cli.add_command',
        'key': 'add-command',
        'group_key': 'cli',
        'name': 'Add CLI Command',
        'description': 'Add a new CLI command definition.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'Unique command identifier.'},
            {'name_or_flags': ['name'], 'description': 'Command name.'},
            {'name_or_flags': ['key'], 'description': 'Command key (used in CLI invocation).'},
            {'name_or_flags': ['group_key'], 'description': 'Group key for the command.'},
            {'name_or_flags': ['--description'], 'description': 'Optional command description.'},
        ],
    },
    {
        'id': 'cli.list_commands',
        'key': 'list-commands',
        'group_key': 'cli',
        'name': 'List CLI Commands',
        'description': 'List all CLI command definitions.',
        'arguments': [],
    },
    {
        'id': 'cli.add_argument',
        'key': 'add-argument',
        'group_key': 'cli',
        'name': 'Add CLI Argument',
        'description': 'Add an argument to an existing CLI command.',
        'arguments': [
            {'name_or_flags': ['command_id'], 'description': 'The CLI command identifier.'},
            {'name_or_flags': ['name_or_flags'], 'description': 'Argument name or flags (comma-separated for multiple flags).'},
            {'name_or_flags': ['--description'], 'description': 'Optional argument description.'},
        ],
    },

    # * commands: logging domain

    {
        'id': 'logging.add_formatter',
        'key': 'add-formatter',
        'group_key': 'logging',
        'name': 'Add Formatter',
        'description': 'Add a new logging formatter configuration.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'Unique formatter identifier.'},
            {'name_or_flags': ['name'], 'description': 'Formatter name.'},
            {'name_or_flags': ['format'], 'description': 'Format string for log messages.'},
            {'name_or_flags': ['--description'], 'description': 'Optional description.'},
            {'name_or_flags': ['--datefmt'], 'description': 'Optional date format string.'},
        ],
    },
    {
        'id': 'logging.remove_formatter',
        'key': 'remove-formatter',
        'group_key': 'logging',
        'name': 'Remove Formatter',
        'description': 'Remove a logging formatter by ID.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The formatter identifier to remove.'},
        ],
    },
    {
        'id': 'logging.add_handler',
        'key': 'add-handler',
        'group_key': 'logging',
        'name': 'Add Handler',
        'description': 'Add a new logging handler configuration.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'Unique handler identifier.'},
            {'name_or_flags': ['name'], 'description': 'Handler name.'},
            {'name_or_flags': ['module_path'], 'description': 'Module path of the handler class.'},
            {'name_or_flags': ['class_name'], 'description': 'Handler class name.'},
            {'name_or_flags': ['level'], 'description': 'Logging level.', 'choices': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']},
            {'name_or_flags': ['formatter'], 'description': 'Formatter ID to use.'},
            {'name_or_flags': ['--description'], 'description': 'Optional description.'},
            {'name_or_flags': ['--stream'], 'description': 'Optional stream specification.'},
            {'name_or_flags': ['--filename'], 'description': 'Optional filename for FileHandler.'},
        ],
    },
    {
        'id': 'logging.remove_handler',
        'key': 'remove-handler',
        'group_key': 'logging',
        'name': 'Remove Handler',
        'description': 'Remove a logging handler by ID.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The handler identifier to remove.'},
        ],
    },
    {
        'id': 'logging.add_logger',
        'key': 'add-logger',
        'group_key': 'logging',
        'name': 'Add Logger',
        'description': 'Add a new logger configuration.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'Unique logger identifier.'},
            {'name_or_flags': ['name'], 'description': 'Logger name.'},
            {'name_or_flags': ['level'], 'description': 'Logging level.', 'choices': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']},
            {'name_or_flags': ['handlers'], 'description': 'Comma-separated list of handler IDs.'},
            {'name_or_flags': ['--description'], 'description': 'Optional description.'},
            {'name_or_flags': ['--no-propagate'], 'description': 'Disable message propagation.', 'action': 'store_true'},
        ],
    },
    {
        'id': 'logging.remove_logger',
        'key': 'remove-logger',
        'group_key': 'logging',
        'name': 'Remove Logger',
        'description': 'Remove a logger by ID.',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The logger identifier to remove.'},
        ],
    },
    {
        'id': 'logging.list',
        'key': 'list',
        'group_key': 'logging',
        'name': 'List Logging Configs',
        'description': 'List all logging configurations (formatters, handlers, loggers).',
        'arguments': [],
    },
]

# ** constant: default_tiferet_cli_commands
# Id-keyed mapping mirroring YAML shape: the key is the command id and the
# value is the record minus id. The bootstrap builder in the orchestration
# layer materializes each record into a typed CliCommand object.
DEFAULT_TIFERET_CLI_COMMANDS: Dict[str, Dict[str, Any]] = {
    entry['id']: {key: value for key, value in entry.items() if key != 'id'}
    for entry in _DEFAULT_TIFERET_CLI_COMMAND_LIST
}
