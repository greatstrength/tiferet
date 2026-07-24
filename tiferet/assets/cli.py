"""Tiferet CLI Command Catalog"""

# *** imports

# ** core
from typing import Any, Dict, List

# *** constants

# ** constant: default_tiferet_cli_commands
DEFAULT_TIFERET_CLI_COMMANDS: Dict[str, Dict[str, Any]] = {

    # -- app group --

    'app.list': {
        'id': 'app.list',
        'name': 'List App Interfaces',
        'description': 'List all configured application interfaces.',
        'key': 'list',
        'group_key': 'app',
        'arguments': [],
    },
    'app.get': {
        'id': 'app.get',
        'name': 'Get App Interface',
        'description': 'Retrieve an app interface by ID.',
        'key': 'get',
        'group_key': 'app',
        'arguments': [
            {
                'name_or_flags': ['interface_id'],
                'description': 'The interface identifier.',
            },
        ],
    },
    'app.add': {
        'id': 'app.add',
        'name': 'Add App Interface',
        'description': 'Add a new application interface configuration.',
        'key': 'add',
        'group_key': 'app',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The unique interface identifier.',
            },
            {
                'name_or_flags': ['name'],
                'description': 'The human-readable interface name.',
            },
            {
                'name_or_flags': ['module_path'],
                'description': 'The Python module path of the context class.',
            },
            {
                'name_or_flags': ['class_name'],
                'description': 'The context class name.',
            },
            {
                'name_or_flags': ['--description'],
                'description': 'Optional interface description.',
            },
            {
                'name_or_flags': ['--logger-id'],
                'description': 'Optional logger identifier. Defaults to "default".',
            },
            {
                'name_or_flags': ['--flags'],
                'description': 'Optional JSON-encoded list of flags.',
            },
            {
                'name_or_flags': ['--constants'],
                'description': 'Optional JSON-encoded constants dictionary.',
            },
        ],
    },
    'app.update': {
        'id': 'app.update',
        'name': 'Update App Interface',
        'description': 'Update a scalar attribute on an existing application interface.',
        'key': 'update',
        'group_key': 'app',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The interface identifier.',
            },
            {
                'name_or_flags': ['attribute'],
                'description': 'The attribute to update.',
            },
            {
                'name_or_flags': ['value'],
                'description': 'The new value for the attribute.',
            },
        ],
    },
    'app.set_service': {
        'id': 'app.set_service',
        'name': 'Set App Service Dependency',
        'description': 'Set or update a service dependency on an application interface.',
        'key': 'set-service',
        'group_key': 'app',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The interface identifier.',
            },
            {
                'name_or_flags': ['service_id'],
                'description': 'The service dependency identifier.',
            },
            {
                'name_or_flags': ['module_path'],
                'description': 'The module path of the service implementation.',
            },
            {
                'name_or_flags': ['class_name'],
                'description': 'The class name of the service implementation.',
            },
            {
                'name_or_flags': ['--parameters'],
                'description': 'Optional JSON-encoded parameters dictionary.',
            },
        ],
    },
    'app.remove_service': {
        'id': 'app.remove_service',
        'name': 'Remove App Service Dependency',
        'description': 'Remove a service dependency from an application interface.',
        'key': 'remove-service',
        'group_key': 'app',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The interface identifier.',
            },
            {
                'name_or_flags': ['service_id'],
                'description': 'The service dependency identifier to remove.',
            },
        ],
    },
    'app.set_constants': {
        'id': 'app.set_constants',
        'name': 'Set App Constants',
        'description': 'Set or clear constants on an application interface.',
        'key': 'set-constants',
        'group_key': 'app',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The interface identifier.',
            },
            {
                'name_or_flags': ['--constants'],
                'description': 'Optional JSON-encoded constants dictionary. Omit to clear all constants.',
            },
        ],
    },
    'app.remove': {
        'id': 'app.remove',
        'name': 'Remove App Interface',
        'description': 'Remove an application interface configuration.',
        'key': 'remove',
        'group_key': 'app',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The interface identifier to remove.',
            },
        ],
    },

    # -- cli group --

    'cli.list_commands': {
        'id': 'cli.list_commands',
        'name': 'List CLI Commands',
        'description': 'List all configured CLI commands.',
        'key': 'list-commands',
        'group_key': 'cli',
        'arguments': [],
    },
    'cli.add_command': {
        'id': 'cli.add_command',
        'name': 'Add CLI Command',
        'description': 'Add a new CLI command definition.',
        'key': 'add-command',
        'group_key': 'cli',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The unique command identifier.',
            },
            {
                'name_or_flags': ['name'],
                'description': 'The human-readable command name.',
            },
            {
                'name_or_flags': ['key'],
                'description': 'The command key used in the CLI.',
            },
            {
                'name_or_flags': ['group_key'],
                'description': 'The group key this command belongs to.',
            },
            {
                'name_or_flags': ['--description'],
                'description': 'Optional command description.',
            },
        ],
    },
    'cli.add_argument': {
        'id': 'cli.add_argument',
        'name': 'Add CLI Argument',
        'description': 'Add an argument to an existing CLI command.',
        'key': 'add-argument',
        'group_key': 'cli',
        'arguments': [
            {
                'name_or_flags': ['command_id'],
                'description': 'The CLI command identifier.',
            },
            {
                'name_or_flags': ['--name-or-flags'],
                'description': 'JSON-encoded list of argument names or flags.',
                'required': True,
            },
            {
                'name_or_flags': ['--description'],
                'description': 'Optional argument description.',
            },
        ],
    },

    # -- error group --

    'error.list': {
        'id': 'error.list',
        'name': 'List Errors',
        'description': 'List all error definitions.',
        'key': 'list',
        'group_key': 'error',
        'arguments': [
            {
                'name_or_flags': ['--include-defaults'],
                'description': 'Include built-in default error definitions.',
                'action': 'store_true',
            },
        ],
    },
    'error.get': {
        'id': 'error.get',
        'name': 'Get Error',
        'description': 'Retrieve an error by ID.',
        'key': 'get',
        'group_key': 'error',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The error identifier.',
            },
        ],
    },
    'error.add': {
        'id': 'error.add',
        'name': 'Add Error',
        'description': 'Add a new error definition.',
        'key': 'add',
        'group_key': 'error',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The unique error identifier.',
            },
            {
                'name_or_flags': ['name'],
                'description': 'The human-readable error name.',
            },
            {
                'name_or_flags': ['message'],
                'description': 'The primary error message text.',
            },
            {
                'name_or_flags': ['--lang'],
                'description': 'Language code for the message. Defaults to "en_US".',
            },
        ],
    },
    'error.rename': {
        'id': 'error.rename',
        'name': 'Rename Error',
        'description': 'Rename an existing error definition.',
        'key': 'rename',
        'group_key': 'error',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The unique error identifier.',
            },
            {
                'name_or_flags': ['new_name'],
                'description': 'The new error name.',
            },
        ],
    },
    'error.set_message': {
        'id': 'error.set_message',
        'name': 'Set Error Message',
        'description': 'Set the message text on an existing error definition.',
        'key': 'set-message',
        'group_key': 'error',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The unique error identifier.',
            },
            {
                'name_or_flags': ['message'],
                'description': 'The new message text.',
            },
            {
                'name_or_flags': ['--lang'],
                'description': 'Language code for the message. Defaults to "en_US".',
            },
        ],
    },
    'error.remove_message': {
        'id': 'error.remove_message',
        'name': 'Remove Error Message',
        'description': 'Remove a language message from an existing error definition.',
        'key': 'remove-message',
        'group_key': 'error',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The unique error identifier.',
            },
            {
                'name_or_flags': ['--lang'],
                'description': 'Language code of the message to remove. Defaults to "en_US".',
            },
        ],
    },
    'error.remove': {
        'id': 'error.remove',
        'name': 'Remove Error',
        'description': 'Remove an error definition.',
        'key': 'remove',
        'group_key': 'error',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The unique error identifier to remove.',
            },
        ],
    },

    # -- feature group --

    'feature.list': {
        'id': 'feature.list',
        'name': 'List Features',
        'description': 'List all feature workflow definitions.',
        'key': 'list',
        'group_key': 'feature',
        'arguments': [
            {
                'name_or_flags': ['--group-id'],
                'description': 'Optional group identifier to filter results.',
            },
        ],
    },
    'feature.add': {
        'id': 'feature.add',
        'name': 'Add Feature',
        'description': 'Add a new feature workflow definition.',
        'key': 'add',
        'group_key': 'feature',
        'arguments': [
            {
                'name_or_flags': ['name'],
                'description': 'The feature name.',
            },
            {
                'name_or_flags': ['group_id'],
                'description': 'The group identifier.',
            },
            {
                'name_or_flags': ['--feature-key'],
                'description': 'Optional explicit feature key. Defaults to snake_case of name.',
            },
            {
                'name_or_flags': ['--description'],
                'description': 'Optional feature description.',
            },
        ],
    },
    'feature.update': {
        'id': 'feature.update',
        'name': 'Update Feature',
        'description': 'Update a metadata attribute on an existing feature.',
        'key': 'update',
        'group_key': 'feature',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The feature identifier.',
            },
            {
                'name_or_flags': ['attribute'],
                'description': 'The attribute to update (name or description).',
            },
            {
                'name_or_flags': ['value'],
                'description': 'The new value.',
            },
        ],
    },
    'feature.add_step': {
        'id': 'feature.add_step',
        'name': 'Add Feature Step',
        'description': 'Add a step to an existing feature workflow.',
        'key': 'add-step',
        'group_key': 'feature',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The feature identifier.',
            },
            {
                'name_or_flags': ['name'],
                'description': 'The step name.',
            },
            {
                'name_or_flags': ['service_id'],
                'description': 'The DI service registration identifier for this step.',
            },
            {
                'name_or_flags': ['--parameters'],
                'description': 'Optional JSON-encoded step parameters.',
            },
            {
                'name_or_flags': ['--data-key'],
                'description': 'Optional result data key.',
            },
            {
                'name_or_flags': ['--pass-on-error'],
                'description': 'Continue execution if this step raises an error.',
                'action': 'store_true',
            },
            {
                'name_or_flags': ['--position'],
                'description': 'Optional insertion index. Defaults to append.',
                'type': 'int',
            },
        ],
    },
    'feature.update_step': {
        'id': 'feature.update_step',
        'name': 'Update Feature Step',
        'description': 'Update an attribute on an existing feature step.',
        'key': 'update-step',
        'group_key': 'feature',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The feature identifier.',
            },
            {
                'name_or_flags': ['position'],
                'description': 'The zero-based step index.',
                'type': 'int',
            },
            {
                'name_or_flags': ['attribute'],
                'description': 'The step attribute to update.',
            },
            {
                'name_or_flags': ['--value'],
                'description': 'The new value for the attribute.',
            },
        ],
    },
    'feature.remove_step': {
        'id': 'feature.remove_step',
        'name': 'Remove Feature Step',
        'description': 'Remove a step from an existing feature workflow.',
        'key': 'remove-step',
        'group_key': 'feature',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The feature identifier.',
            },
            {
                'name_or_flags': ['position'],
                'description': 'The zero-based index of the step to remove.',
                'type': 'int',
            },
        ],
    },
    'feature.reorder_step': {
        'id': 'feature.reorder_step',
        'name': 'Reorder Feature Step',
        'description': 'Reorder a step within an existing feature workflow.',
        'key': 'reorder-step',
        'group_key': 'feature',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The feature identifier.',
            },
            {
                'name_or_flags': ['start_position'],
                'description': 'The current zero-based step index.',
                'type': 'int',
            },
            {
                'name_or_flags': ['end_position'],
                'description': 'The target zero-based step index.',
                'type': 'int',
            },
        ],
    },
    'feature.remove': {
        'id': 'feature.remove',
        'name': 'Remove Feature',
        'description': 'Remove an existing feature workflow definition.',
        'key': 'remove',
        'group_key': 'feature',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The feature identifier to remove.',
            },
        ],
    },

    # -- service group --

    'service.list': {
        'id': 'service.list',
        'name': 'List Services',
        'description': 'List all DI service registrations and constants.',
        'key': 'list',
        'group_key': 'service',
        'arguments': [],
    },
    'service.add': {
        'id': 'service.add',
        'name': 'Add Service',
        'description': 'Add a new DI service registration.',
        'key': 'add',
        'group_key': 'service',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The unique service registration identifier.',
            },
            {
                'name_or_flags': ['--module-path'],
                'description': 'The module path of the service implementation.',
            },
            {
                'name_or_flags': ['--class-name'],
                'description': 'The class name of the service implementation.',
            },
            {
                'name_or_flags': ['--parameters'],
                'description': 'Optional JSON-encoded parameters dictionary.',
            },
        ],
    },
    'service.set_default': {
        'id': 'service.set_default',
        'name': 'Set Default Service Registration',
        'description': 'Set or update the default type for an existing service registration.',
        'key': 'set-default',
        'group_key': 'service',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The service registration identifier.',
            },
            {
                'name_or_flags': ['--module-path'],
                'description': 'The new default module path.',
            },
            {
                'name_or_flags': ['--class-name'],
                'description': 'The new default class name.',
            },
            {
                'name_or_flags': ['--parameters'],
                'description': 'Optional JSON-encoded parameters dictionary.',
            },
        ],
    },
    'service.set_dependency': {
        'id': 'service.set_dependency',
        'name': 'Set Service Dependency',
        'description': 'Set or update a flagged dependency on a service registration.',
        'key': 'set-dependency',
        'group_key': 'service',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The service registration identifier.',
            },
            {
                'name_or_flags': ['flag'],
                'description': 'The flag identifying this dependency.',
            },
            {
                'name_or_flags': ['module_path'],
                'description': 'The module path for the flagged dependency.',
            },
            {
                'name_or_flags': ['class_name'],
                'description': 'The class name for the flagged dependency.',
            },
            {
                'name_or_flags': ['--parameters'],
                'description': 'Optional JSON-encoded parameters dictionary.',
            },
        ],
    },
    'service.remove_dependency': {
        'id': 'service.remove_dependency',
        'name': 'Remove Service Dependency',
        'description': 'Remove a flagged dependency from a service registration.',
        'key': 'remove-dependency',
        'group_key': 'service',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The service registration identifier.',
            },
            {
                'name_or_flags': ['flag'],
                'description': 'The flag identifying the dependency to remove.',
            },
        ],
    },
    'service.set_constants': {
        'id': 'service.set_constants',
        'name': 'Set Service Constants',
        'description': 'Set or clear DI service constants.',
        'key': 'set-constants',
        'group_key': 'service',
        'arguments': [
            {
                'name_or_flags': ['--constants'],
                'description': 'Optional JSON-encoded constants dictionary. Omit to clear all.',
            },
        ],
    },
    'service.remove': {
        'id': 'service.remove',
        'name': 'Remove Service',
        'description': 'Remove a DI service registration.',
        'key': 'remove',
        'group_key': 'service',
        'arguments': [
            {
                'name_or_flags': ['id'],
                'description': 'The service registration identifier to remove.',
            },
        ],
    },

    # -- logging group --

    'logging.add_formatter': {
        'id': 'logging.add_formatter',
        'name': 'Add Formatter',
        'description': 'Add a new logging formatter configuration.',
        'key': 'add-formatter',
        'group_key': 'logging',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'Unique formatter identifier.'},
            {'name_or_flags': ['name'], 'description': 'Formatter name.'},
            {'name_or_flags': ['format'], 'description': 'Format string for log messages.'},
            {'name_or_flags': ['--description'], 'description': 'Optional description.'},
            {'name_or_flags': ['--datefmt'], 'description': 'Optional date format string.'},
        ],
    },
    'logging.remove_formatter': {
        'id': 'logging.remove_formatter',
        'name': 'Remove Formatter',
        'description': 'Remove a logging formatter by ID.',
        'key': 'remove-formatter',
        'group_key': 'logging',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The formatter identifier to remove.'},
        ],
    },
    'logging.add_handler': {
        'id': 'logging.add_handler',
        'name': 'Add Handler',
        'description': 'Add a new logging handler configuration.',
        'key': 'add-handler',
        'group_key': 'logging',
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
    'logging.remove_handler': {
        'id': 'logging.remove_handler',
        'name': 'Remove Handler',
        'description': 'Remove a logging handler by ID.',
        'key': 'remove-handler',
        'group_key': 'logging',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The handler identifier to remove.'},
        ],
    },
    'logging.add_logger': {
        'id': 'logging.add_logger',
        'name': 'Add Logger',
        'description': 'Add a new logger configuration.',
        'key': 'add-logger',
        'group_key': 'logging',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'Unique logger identifier.'},
            {'name_or_flags': ['name'], 'description': 'Logger name.'},
            {'name_or_flags': ['level'], 'description': 'Logging level.', 'choices': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']},
            {'name_or_flags': ['handlers'], 'description': 'Comma-separated list of handler IDs.'},
            {'name_or_flags': ['--description'], 'description': 'Optional description.'},
            {'name_or_flags': ['--no-propagate'], 'description': 'Disable message propagation.', 'action': 'store_true'},
        ],
    },
    'logging.remove_logger': {
        'id': 'logging.remove_logger',
        'name': 'Remove Logger',
        'description': 'Remove a logger by ID.',
        'key': 'remove-logger',
        'group_key': 'logging',
        'arguments': [
            {'name_or_flags': ['id'], 'description': 'The logger identifier to remove.'},
        ],
    },
    'logging.list': {
        'id': 'logging.list',
        'name': 'List Logging Configs',
        'description': 'List all logging configurations (formatters, handlers, loggers).',
        'key': 'list',
        'group_key': 'logging',
        'arguments': [],
    },
}

# ** constant: admin_default_commands
ADMIN_DEFAULT_COMMANDS: Dict[str, Dict[str, Any]] = DEFAULT_TIFERET_CLI_COMMANDS
