"""Tiferet CLI Feature Catalog"""

# *** imports

# ** core
from typing import Any, Dict, List

# *** constants

# ** constant: default_tiferet_cli_features
DEFAULT_TIFERET_CLI_FEATURES: Dict[str, Dict[str, Any]] = {

    # -- app group --

    'app.list': {
        'id': 'app.list',
        'name': 'List App Interfaces',
        'group_id': 'app',
        'feature_key': 'list',
        'description': 'List all configured application interfaces.',
        'steps': [
            {'service_id': 'list_app_interfaces_evt'},
        ],
    },
    'app.add': {
        'id': 'app.add',
        'name': 'Add App Interface',
        'group_id': 'app',
        'feature_key': 'add',
        'description': 'Add a new application interface configuration.',
        'steps': [
            {'service_id': 'add_app_interface_evt'},
        ],
    },
    'app.update': {
        'id': 'app.update',
        'name': 'Update App Interface',
        'group_id': 'app',
        'feature_key': 'update',
        'description': 'Update a scalar attribute on an existing application interface.',
        'steps': [
            {'service_id': 'update_app_interface_evt'},
        ],
    },
    'app.set_service': {
        'id': 'app.set_service',
        'name': 'Set App Service Dependency',
        'group_id': 'app',
        'feature_key': 'set_service',
        'description': 'Set or update a service dependency on an application interface.',
        'steps': [
            {'service_id': 'set_app_service_dependency_evt'},
        ],
    },
    'app.remove_service': {
        'id': 'app.remove_service',
        'name': 'Remove App Service Dependency',
        'group_id': 'app',
        'feature_key': 'remove_service',
        'description': 'Remove a service dependency from an application interface.',
        'steps': [
            {'service_id': 'remove_app_service_dependency_evt'},
        ],
    },
    'app.set_constants': {
        'id': 'app.set_constants',
        'name': 'Set App Constants',
        'group_id': 'app',
        'feature_key': 'set_constants',
        'description': 'Set or clear constants on an application interface.',
        'steps': [
            {'service_id': 'set_app_constants_evt'},
        ],
    },
    'app.remove': {
        'id': 'app.remove',
        'name': 'Remove App Interface',
        'group_id': 'app',
        'feature_key': 'remove',
        'description': 'Remove an application interface configuration.',
        'steps': [
            {'service_id': 'remove_app_interface_evt'},
        ],
    },

    # -- cli group --

    'cli.list_commands': {
        'id': 'cli.list_commands',
        'name': 'List CLI Commands',
        'group_id': 'cli',
        'feature_key': 'list_commands',
        'description': 'List all configured CLI commands.',
        'steps': [
            {'service_id': 'list_commands_evt'},
        ],
    },
    'cli.add_command': {
        'id': 'cli.add_command',
        'name': 'Add CLI Command',
        'group_id': 'cli',
        'feature_key': 'add_command',
        'description': 'Add a new CLI command definition.',
        'steps': [
            {'service_id': 'add_cli_command_evt'},
        ],
    },
    'cli.add_argument': {
        'id': 'cli.add_argument',
        'name': 'Add CLI Argument',
        'group_id': 'cli',
        'feature_key': 'add_argument',
        'description': 'Add an argument to an existing CLI command.',
        'steps': [
            {'service_id': 'add_cli_argument_evt'},
        ],
    },

    # -- error group --

    'error.list': {
        'id': 'error.list',
        'name': 'List Errors',
        'group_id': 'error',
        'feature_key': 'list',
        'description': 'List all error definitions.',
        'steps': [
            {'service_id': 'list_errors_evt'},
        ],
    },
    'error.add': {
        'id': 'error.add',
        'name': 'Add Error',
        'group_id': 'error',
        'feature_key': 'add',
        'description': 'Add a new error definition.',
        'steps': [
            {'service_id': 'add_error_evt'},
        ],
    },
    'error.rename': {
        'id': 'error.rename',
        'name': 'Rename Error',
        'group_id': 'error',
        'feature_key': 'rename',
        'description': 'Rename an existing error definition.',
        'steps': [
            {'service_id': 'rename_error_evt'},
        ],
    },
    'error.set_message': {
        'id': 'error.set_message',
        'name': 'Set Error Message',
        'group_id': 'error',
        'feature_key': 'set_message',
        'description': 'Set the message text on an existing error definition.',
        'steps': [
            {'service_id': 'set_error_message_evt'},
        ],
    },
    'error.remove_message': {
        'id': 'error.remove_message',
        'name': 'Remove Error Message',
        'group_id': 'error',
        'feature_key': 'remove_message',
        'description': 'Remove a language message from an existing error definition.',
        'steps': [
            {'service_id': 'remove_error_message_evt'},
        ],
    },
    'error.remove': {
        'id': 'error.remove',
        'name': 'Remove Error',
        'group_id': 'error',
        'feature_key': 'remove',
        'description': 'Remove an error definition.',
        'steps': [
            {'service_id': 'remove_error_evt'},
        ],
    },

    # -- feature group --

    'feature.list': {
        'id': 'feature.list',
        'name': 'List Features',
        'group_id': 'feature',
        'feature_key': 'list',
        'description': 'List all feature workflow definitions.',
        'steps': [
            {'service_id': 'list_features_evt'},
        ],
    },
    'feature.add': {
        'id': 'feature.add',
        'name': 'Add Feature',
        'group_id': 'feature',
        'feature_key': 'add',
        'description': 'Add a new feature workflow definition.',
        'steps': [
            {'service_id': 'add_feature_evt'},
        ],
    },
    'feature.update': {
        'id': 'feature.update',
        'name': 'Update Feature',
        'group_id': 'feature',
        'feature_key': 'update',
        'description': 'Update a metadata attribute on an existing feature.',
        'steps': [
            {'service_id': 'update_feature_evt'},
        ],
    },
    'feature.add_step': {
        'id': 'feature.add_step',
        'name': 'Add Feature Step',
        'group_id': 'feature',
        'feature_key': 'add_step',
        'description': 'Add a step to an existing feature workflow.',
        'steps': [
            {'service_id': 'add_feature_step_evt'},
        ],
    },
    'feature.update_step': {
        'id': 'feature.update_step',
        'name': 'Update Feature Step',
        'group_id': 'feature',
        'feature_key': 'update_step',
        'description': 'Update an attribute on an existing feature step.',
        'steps': [
            {'service_id': 'update_feature_step_evt'},
        ],
    },
    'feature.remove_step': {
        'id': 'feature.remove_step',
        'name': 'Remove Feature Step',
        'group_id': 'feature',
        'feature_key': 'remove_step',
        'description': 'Remove a step from an existing feature workflow.',
        'steps': [
            {'service_id': 'remove_feature_step_evt'},
        ],
    },
    'feature.reorder_step': {
        'id': 'feature.reorder_step',
        'name': 'Reorder Feature Step',
        'group_id': 'feature',
        'feature_key': 'reorder_step',
        'description': 'Reorder a step within an existing feature workflow.',
        'steps': [
            {'service_id': 'reorder_feature_step_evt'},
        ],
    },
    'feature.remove': {
        'id': 'feature.remove',
        'name': 'Remove Feature',
        'group_id': 'feature',
        'feature_key': 'remove',
        'description': 'Remove an existing feature workflow definition.',
        'steps': [
            {'service_id': 'remove_feature_evt'},
        ],
    },

    # -- service group --

    'service.list': {
        'id': 'service.list',
        'name': 'List Services',
        'group_id': 'service',
        'feature_key': 'list',
        'description': 'List all DI service registrations and constants.',
        'steps': [
            {'service_id': 'di_list_all_configs_evt'},
        ],
    },
    'service.add': {
        'id': 'service.add',
        'name': 'Add Service',
        'group_id': 'service',
        'feature_key': 'add',
        'description': 'Add a new DI service registration.',
        'steps': [
            {'service_id': 'add_service_registration_evt'},
        ],
    },
    'service.set_default': {
        'id': 'service.set_default',
        'name': 'Set Default Service Registration',
        'group_id': 'service',
        'feature_key': 'set_default',
        'description': 'Set or update the default type for an existing service registration.',
        'steps': [
            {'service_id': 'set_default_service_registration_evt'},
        ],
    },
    'service.set_dependency': {
        'id': 'service.set_dependency',
        'name': 'Set Service Dependency',
        'group_id': 'service',
        'feature_key': 'set_dependency',
        'description': 'Set or update a flagged dependency on a service registration.',
        'steps': [
            {'service_id': 'set_service_dependency_evt'},
        ],
    },
    'service.remove_dependency': {
        'id': 'service.remove_dependency',
        'name': 'Remove Service Dependency',
        'group_id': 'service',
        'feature_key': 'remove_dependency',
        'description': 'Remove a flagged dependency from a service registration.',
        'steps': [
            {'service_id': 'remove_service_dependency_evt'},
        ],
    },
    'service.set_constants': {
        'id': 'service.set_constants',
        'name': 'Set Service Constants',
        'group_id': 'service',
        'feature_key': 'set_constants',
        'description': 'Set or clear DI service constants.',
        'steps': [
            {'service_id': 'set_service_constants_evt'},
        ],
    },
    'service.remove': {
        'id': 'service.remove',
        'name': 'Remove Service',
        'group_id': 'service',
        'feature_key': 'remove',
        'description': 'Remove a DI service registration.',
        'steps': [
            {'service_id': 'remove_service_registration_evt'},
        ],
    },
}

# ** constant: admin_default_features
ADMIN_DEFAULT_FEATURES: Dict[str, Dict[str, Any]] = {
    k: v for k, v in DEFAULT_TIFERET_CLI_FEATURES.items()
    if v['group_id'] in ('app', 'service', 'cli')
}
