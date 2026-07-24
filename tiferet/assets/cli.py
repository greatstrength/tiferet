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
                'type': 'str',
            },
            {
                'name_or_flags': ['name'],
                'description': 'The human-readable interface name.',
                'type': 'str',
            },
            {
                'name_or_flags': ['module_path'],
                'description': 'The Python module path of the context class.',
                'type': 'str',
            },
            {
                'name_or_flags': ['class_name'],
                'description': 'The context class name.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--description'],
                'description': 'Optional interface description.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--logger-id'],
                'description': 'Optional logger identifier. Defaults to "default".',
                'type': 'str',
            },
            {
                'name_or_flags': ['--flags'],
                'description': 'Optional JSON-encoded list of flags.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--constants'],
                'description': 'Optional JSON-encoded constants dictionary.',
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['attribute'],
                'description': 'The attribute to update.',
                'type': 'str',
            },
            {
                'name_or_flags': ['value'],
                'description': 'The new value for the attribute.',
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['service_id'],
                'description': 'The service dependency identifier.',
                'type': 'str',
            },
            {
                'name_or_flags': ['module_path'],
                'description': 'The module path of the service implementation.',
                'type': 'str',
            },
            {
                'name_or_flags': ['class_name'],
                'description': 'The class name of the service implementation.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--parameters'],
                'description': 'Optional JSON-encoded parameters dictionary.',
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['service_id'],
                'description': 'The service dependency identifier to remove.',
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['--constants'],
                'description': 'Optional JSON-encoded constants dictionary. Omit to clear all constants.',
                'type': 'str',
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
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['name'],
                'description': 'The human-readable command name.',
                'type': 'str',
            },
            {
                'name_or_flags': ['key'],
                'description': 'The command key used in the CLI.',
                'type': 'str',
            },
            {
                'name_or_flags': ['group_key'],
                'description': 'The group key this command belongs to.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--description'],
                'description': 'Optional command description.',
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['--name-or-flags'],
                'description': 'JSON-encoded list of argument names or flags.',
                'type': 'str',
                'required': True,
            },
            {
                'name_or_flags': ['--description'],
                'description': 'Optional argument description.',
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['name'],
                'description': 'The human-readable error name.',
                'type': 'str',
            },
            {
                'name_or_flags': ['message'],
                'description': 'The primary error message text.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--lang'],
                'description': 'Language code for the message. Defaults to "en_US".',
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['new_name'],
                'description': 'The new error name.',
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['message'],
                'description': 'The new message text.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--lang'],
                'description': 'Language code for the message. Defaults to "en_US".',
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['--lang'],
                'description': 'Language code of the message to remove. Defaults to "en_US".',
                'type': 'str',
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
                'type': 'str',
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
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['group_id'],
                'description': 'The group identifier.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--feature-key'],
                'description': 'Optional explicit feature key. Defaults to snake_case of name.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--description'],
                'description': 'Optional feature description.',
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['attribute'],
                'description': 'The attribute to update (name or description).',
                'type': 'str',
            },
            {
                'name_or_flags': ['value'],
                'description': 'The new value.',
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['name'],
                'description': 'The step name.',
                'type': 'str',
            },
            {
                'name_or_flags': ['service_id'],
                'description': 'The DI service registration identifier for this step.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--parameters'],
                'description': 'Optional JSON-encoded step parameters.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--data-key'],
                'description': 'Optional result data key.',
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['position'],
                'description': 'The zero-based step index.',
                'type': 'int',
            },
            {
                'name_or_flags': ['attribute'],
                'description': 'The step attribute to update.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--value'],
                'description': 'The new value for the attribute.',
                'type': 'str',
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
                'type': 'str',
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
                'type': 'str',
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
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['--module-path'],
                'description': 'The module path of the service implementation.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--class-name'],
                'description': 'The class name of the service implementation.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--parameters'],
                'description': 'Optional JSON-encoded parameters dictionary.',
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['--module-path'],
                'description': 'The new default module path.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--class-name'],
                'description': 'The new default class name.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--parameters'],
                'description': 'Optional JSON-encoded parameters dictionary.',
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['flag'],
                'description': 'The flag identifying this dependency.',
                'type': 'str',
            },
            {
                'name_or_flags': ['module_path'],
                'description': 'The module path for the flagged dependency.',
                'type': 'str',
            },
            {
                'name_or_flags': ['class_name'],
                'description': 'The class name for the flagged dependency.',
                'type': 'str',
            },
            {
                'name_or_flags': ['--parameters'],
                'description': 'Optional JSON-encoded parameters dictionary.',
                'type': 'str',
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
                'type': 'str',
            },
            {
                'name_or_flags': ['flag'],
                'description': 'The flag identifying the dependency to remove.',
                'type': 'str',
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
                'type': 'str',
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
                'type': 'str',
            },
        ],
    },
}

# ** constant: admin_default_commands
ADMIN_DEFAULT_COMMANDS: Dict[str, Dict[str, Any]] = {
    k: v for k, v in DEFAULT_TIFERET_CLI_COMMANDS.items()
    if v['group_key'] in ('app', 'service', 'cli')
}
