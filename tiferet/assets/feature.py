"""Tiferet Assets Feature

Provides the default feature workflow definitions for the built-in Tiferet CLI
management application. Each feature maps to a single-step workflow that
invokes the corresponding domain event service.

The blueprint constructs ``Feature`` domain objects from these definitions
at startup — they are not loaded from the consumer's config file.
"""

# *** imports

# ** core
from typing import Any, Dict, List

# *** configs

# ** config: default_tiferet_cli_feature_list
# Each dict matches the Feature domain object constructor fields.
# Steps use EventFeatureStep field names: service_id, name, parameters, data_key.
# ``params_schema`` declares the feature-level request validation schema
# (RFP #838) for each feature, mapping the underlying event's expected request
# parameters to declared types and defaults. It uses the ergonomic keyed form:
# the shorthand ``name: type`` for required parameters and the expanded form
# ``name: {type, required, default}`` for optional parameters. Framework
# context parameters (e.g. default_* fallbacks), free-form ``value`` arguments,
# and comma-separated list arguments (handlers, name_or_flags) are intentionally
# omitted so existing request behavior is preserved.
_DEFAULT_TIFERET_CLI_FEATURE_LIST: List[Dict[str, Any]] = [

    # * features: feature domain
    {
        'id': 'feature.add',
        'group_id': 'feature',
        'feature_key': 'add',
        'name': 'Add Feature',
        'description': 'Add a new feature configuration.',
        'params_schema': {
            'name': 'str',
            'group_id': 'str',
            'feature_key': {'type': 'str', 'required': False},
            'id': {'type': 'str', 'required': False},
            'description': {'type': 'str', 'required': False},
            'steps': {'type': 'list', 'required': False},
            'log_params': {'type': 'dict', 'required': False},
        },
        'steps': [{'service_id': 'add_feature_evt', 'name': 'Add feature'}],
    },
    {
        'id': 'feature.get',
        'group_id': 'feature',
        'feature_key': 'get',
        'name': 'Get Feature',
        'description': 'Retrieve a feature by ID.',
        'params_schema': {
            'id': 'str',
        },
        'steps': [{'service_id': 'get_feature_evt', 'name': 'Get feature'}],
    },
    {
        'id': 'feature.list',
        'group_id': 'feature',
        'feature_key': 'list',
        'name': 'List Features',
        'description': 'List all features, optionally filtered by group.',
        'params_schema': {
            'group_id': {'type': 'str', 'required': False},
        },
        'steps': [{'service_id': 'list_features_evt', 'name': 'List features'}],
    },
    {
        'id': 'feature.remove',
        'group_id': 'feature',
        'feature_key': 'remove',
        'name': 'Remove Feature',
        'description': 'Remove a feature configuration by ID.',
        'params_schema': {
            'id': 'str',
        },
        'steps': [{'service_id': 'remove_feature_evt', 'name': 'Remove feature'}],
    },
    {
        'id': 'feature.update',
        'group_id': 'feature',
        'feature_key': 'update',
        'name': 'Update Feature',
        'description': 'Update a feature attribute (name or description).',
        'params_schema': {
            'id': 'str',
            'attribute': 'str',
        },
        'steps': [{'service_id': 'update_feature_evt', 'name': 'Update feature'}],
    },
    {
        'id': 'feature.add_step',
        'group_id': 'feature',
        'feature_key': 'add_step',
        'name': 'Add Feature Step',
        'description': 'Add a step to an existing feature workflow.',
        'params_schema': {
            'id': 'str',
            'name': 'str',
            'service_id': 'str',
            'parameters': {'type': 'dict', 'required': False},
            'data_key': {'type': 'str', 'required': False},
            'pass_on_error': {'type': 'bool', 'required': False, 'default': False},
            'position': {'type': 'int', 'required': False},
        },
        'steps': [{'service_id': 'add_feature_step_evt', 'name': 'Add feature step'}],
    },
    {
        'id': 'feature.update_step',
        'group_id': 'feature',
        'feature_key': 'update_step',
        'name': 'Update Feature Step',
        'description': 'Update an attribute on a feature step.',
        'params_schema': {
            'id': 'str',
            'position': 'int',
            'attribute': 'str',
        },
        'steps': [{'service_id': 'update_feature_step_evt', 'name': 'Update feature step'}],
    },
    {
        'id': 'feature.remove_step',
        'group_id': 'feature',
        'feature_key': 'remove_step',
        'name': 'Remove Feature Step',
        'description': 'Remove a step from a feature by position.',
        'params_schema': {
            'id': 'str',
            'position': 'int',
        },
        'steps': [{'service_id': 'remove_feature_step_evt', 'name': 'Remove feature step'}],
    },
    {
        'id': 'feature.reorder_step',
        'group_id': 'feature',
        'feature_key': 'reorder_step',
        'name': 'Reorder Feature Step',
        'description': 'Move a feature step from one position to another.',
        'params_schema': {
            'id': 'str',
            'start_position': 'int',
            'end_position': 'int',
        },
        'steps': [{'service_id': 'reorder_feature_step_evt', 'name': 'Reorder feature step'}],
    },

    # * features: error domain
    {
        'id': 'error.add',
        'group_id': 'error',
        'feature_key': 'add',
        'name': 'Add Error',
        'description': 'Add a new error definition.',
        'params_schema': {
            'id': 'str',
            'name': 'str',
            'message': 'str',
            'lang': {'type': 'str', 'required': False, 'default': 'en_US'},
            'additional_messages': {'type': 'list', 'required': False, 'default': []},
        },
        'steps': [{'service_id': 'add_error_evt', 'name': 'Add error'}],
    },
    {
        'id': 'error.get',
        'group_id': 'error',
        'feature_key': 'get',
        'name': 'Get Error',
        'description': 'Retrieve an error by ID.',
        'params_schema': {
            'id': 'str',
            'include_defaults': {'type': 'bool', 'required': False, 'default': False},
        },
        'steps': [{'service_id': 'get_error_evt', 'name': 'Get error'}],
    },
    {
        'id': 'error.list',
        'group_id': 'error',
        'feature_key': 'list',
        'name': 'List Errors',
        'description': 'List all error definitions.',
        'params_schema': {
            'include_defaults': {'type': 'bool', 'required': False, 'default': False},
        },
        'steps': [{'service_id': 'list_errors_evt', 'name': 'List errors'}],
    },
    {
        'id': 'error.rename',
        'group_id': 'error',
        'feature_key': 'rename',
        'name': 'Rename Error',
        'description': 'Rename an existing error.',
        'params_schema': {
            'id': 'str',
            'new_name': 'str',
        },
        'steps': [{'service_id': 'rename_error_evt', 'name': 'Rename error'}],
    },
    {
        'id': 'error.set_message',
        'group_id': 'error',
        'feature_key': 'set_message',
        'name': 'Set Error Message',
        'description': 'Set or update an error message for a language.',
        'params_schema': {
            'id': 'str',
            'message': 'str',
            'lang': {'type': 'str', 'required': False, 'default': 'en_US'},
        },
        'steps': [{'service_id': 'set_error_message_evt', 'name': 'Set error message'}],
    },
    {
        'id': 'error.remove_message',
        'group_id': 'error',
        'feature_key': 'remove_message',
        'name': 'Remove Error Message',
        'description': 'Remove an error message by language.',
        'params_schema': {
            'id': 'str',
            'lang': {'type': 'str', 'required': False, 'default': 'en_US'},
        },
        'steps': [{'service_id': 'remove_error_message_evt', 'name': 'Remove error message'}],
    },
    {
        'id': 'error.remove',
        'group_id': 'error',
        'feature_key': 'remove',
        'name': 'Remove Error',
        'description': 'Remove an error definition by ID.',
        'params_schema': {
            'id': 'str',
        },
        'steps': [{'service_id': 'remove_error_evt', 'name': 'Remove error'}],
    },

    # * features: service (DI) domain
    {
        'id': 'service.add',
        'group_id': 'service',
        'feature_key': 'add',
        'name': 'Add Service Configuration',
        'description': 'Add a new service configuration.',
        'params_schema': {
            'id': 'str',
            'module_path': {'type': 'str', 'required': False},
            'class_name': {'type': 'str', 'required': False},
            'parameters': {'type': 'dict', 'required': False, 'default': {}},
            'flagged_dependencies': {'type': 'list', 'required': False, 'default': []},
        },
        'steps': [{'service_id': 'add_service_registration_evt', 'name': 'Add service configuration'}],
    },
    {
        'id': 'service.list',
        'group_id': 'service',
        'feature_key': 'list',
        'name': 'List All Settings',
        'description': 'List all service configurations and constants.',
        'steps': [{'service_id': 'di_list_all_configs_evt', 'name': 'List all settings'}],
    },
    {
        'id': 'service.set_default',
        'group_id': 'service',
        'feature_key': 'set_default',
        'name': 'Set Default Service Configuration',
        'description': 'Set or update the default type for a service configuration.',
        'params_schema': {
            'id': 'str',
            'module_path': {'type': 'str', 'required': False},
            'class_name': {'type': 'str', 'required': False},
            'parameters': {'type': 'dict', 'required': False},
        },
        'steps': [{'service_id': 'set_default_service_registration_evt', 'name': 'Set default service configuration'}],
    },
    {
        'id': 'service.set_dependency',
        'group_id': 'service',
        'feature_key': 'set_dependency',
        'name': 'Set Service Dependency',
        'description': 'Set or update a flagged dependency on a service configuration.',
        'params_schema': {
            'id': 'str',
            'flag': 'str',
            'module_path': 'str',
            'class_name': 'str',
            'parameters': {'type': 'dict', 'required': False, 'default': {}},
        },
        'steps': [{'service_id': 'set_di_service_dependency_evt', 'name': 'Set service dependency'}],
    },
    {
        'id': 'service.remove_dependency',
        'group_id': 'service',
        'feature_key': 'remove_dependency',
        'name': 'Remove Service Dependency',
        'description': 'Remove a flagged dependency from a service configuration.',
        'params_schema': {
            'id': 'str',
            'flag': 'str',
        },
        'steps': [{'service_id': 'remove_di_service_dependency_evt', 'name': 'Remove service dependency'}],
    },
    {
        'id': 'service.remove',
        'group_id': 'service',
        'feature_key': 'remove',
        'name': 'Remove Service Configuration',
        'description': 'Remove a service configuration by ID.',
        'params_schema': {
            'id': 'str',
        },
        'steps': [{'service_id': 'remove_service_registration_evt', 'name': 'Remove service configuration'}],
    },
    {
        'id': 'service.set_constants',
        'group_id': 'service',
        'feature_key': 'set_constants',
        'name': 'Set Service Constants',
        'description': 'Set or clear service-level constants.',
        'params_schema': {
            'constants': {'type': 'dict', 'required': False, 'default': {}},
        },
        'steps': [{'service_id': 'set_service_constants_evt', 'name': 'Set service constants'}],
    },

    # * features: app interface domain
    {
        'id': 'app.add',
        'group_id': 'app',
        'feature_key': 'add',
        'name': 'Add App Interface',
        'description': 'Add a new application interface configuration.',
        'params_schema': {
            'id': 'str',
            'name': 'str',
            'module_path': 'str',
            'class_name': 'str',
            'description': {'type': 'str', 'required': False},
            'logger_id': {'type': 'str', 'required': False, 'default': 'default'},
            'flags': {'type': 'list', 'required': False, 'default': ['default']},
            'services': {'type': 'list', 'required': False, 'default': []},
            'constants': {'type': 'dict', 'required': False, 'default': {}},
        },
        'steps': [{'service_id': 'add_app_interface_evt', 'name': 'Add app interface'}],
    },
    {
        'id': 'app.get',
        'group_id': 'app',
        'feature_key': 'get',
        'name': 'Get App Interface',
        'description': 'Retrieve an app interface by ID.',
        'params_schema': {
            'interface_id': 'str',
        },
        'steps': [{'service_id': 'get_app_interface_evt', 'name': 'Get app interface'}],
    },
    {
        'id': 'app.list',
        'group_id': 'app',
        'feature_key': 'list',
        'name': 'List App Interfaces',
        'description': 'List all configured app interfaces.',
        'steps': [{'service_id': 'list_app_interfaces_evt', 'name': 'List app interfaces'}],
    },
    {
        'id': 'app.update',
        'group_id': 'app',
        'feature_key': 'update',
        'name': 'Update App Interface',
        'description': 'Update a scalar attribute on an app interface.',
        'params_schema': {
            'id': 'str',
            'attribute': 'str',
        },
        'steps': [{'service_id': 'update_app_interface_evt', 'name': 'Update app interface'}],
    },
    {
        'id': 'app.set_constants',
        'group_id': 'app',
        'feature_key': 'set_constants',
        'name': 'Set App Constants',
        'description': 'Set or clear constants on an app interface.',
        'params_schema': {
            'id': 'str',
            'constants': {'type': 'dict', 'required': False},
        },
        'steps': [{'service_id': 'set_app_constants_evt', 'name': 'Set app constants'}],
    },
    {
        'id': 'app.set_service',
        'group_id': 'app',
        'feature_key': 'set_service',
        'name': 'Set App Service Dependency',
        'description': 'Set or update a service dependency on an app interface.',
        'params_schema': {
            'id': 'str',
            'service_id': 'str',
            'module_path': 'str',
            'class_name': 'str',
            'parameters': {'type': 'dict', 'required': False},
        },
        'steps': [{'service_id': 'set_app_service_dependency_evt', 'name': 'Set app service dependency'}],
    },
    {
        'id': 'app.remove_service',
        'group_id': 'app',
        'feature_key': 'remove_service',
        'name': 'Remove App Service Dependency',
        'description': 'Remove a service dependency from an app interface.',
        'params_schema': {
            'id': 'str',
            'service_id': 'str',
        },
        'steps': [{'service_id': 'remove_app_service_dependency_evt', 'name': 'Remove app service dependency'}],
    },
    {
        'id': 'app.remove',
        'group_id': 'app',
        'feature_key': 'remove',
        'name': 'Remove App Interface',
        'description': 'Remove an app interface by ID.',
        'params_schema': {
            'id': 'str',
        },
        'steps': [{'service_id': 'remove_app_interface_evt', 'name': 'Remove app interface'}],
    },

    # * features: cli domain
    {
        'id': 'cli.add_command',
        'group_id': 'cli',
        'feature_key': 'add_command',
        'name': 'Add CLI Command',
        'description': 'Add a new CLI command definition.',
        'params_schema': {
            'id': 'str',
            'name': 'str',
            'key': 'str',
            'group_key': 'str',
            'description': {'type': 'str', 'required': False},
            'arguments': {'type': 'list', 'required': False, 'default': []},
        },
        'steps': [{'service_id': 'add_cli_command_evt', 'name': 'Add CLI command'}],
    },
    {
        'id': 'cli.list_commands',
        'group_id': 'cli',
        'feature_key': 'list_commands',
        'name': 'List CLI Commands',
        'description': 'List all CLI command definitions.',
        'steps': [{'service_id': 'list_commands_evt', 'name': 'List CLI commands'}],
    },
    {
        'id': 'cli.add_argument',
        'group_id': 'cli',
        'feature_key': 'add_argument',
        'name': 'Add CLI Argument',
        'description': 'Add an argument to an existing CLI command.',
        'params_schema': {
            'command_id': 'str',
            'description': {'type': 'str', 'required': False},
        },
        'steps': [{'service_id': 'add_cli_argument_evt', 'name': 'Add CLI argument'}],
    },

    # * features: logging domain
    {
        'id': 'logging.add_formatter',
        'group_id': 'logging',
        'feature_key': 'add_formatter',
        'name': 'Add Formatter',
        'description': 'Add a new logging formatter configuration.',
        'params_schema': {
            'id': 'str',
            'name': 'str',
            'format': 'str',
            'description': {'type': 'str', 'required': False},
            'datefmt': {'type': 'str', 'required': False},
        },
        'steps': [{'service_id': 'add_formatter_evt', 'name': 'Add formatter'}],
    },
    {
        'id': 'logging.remove_formatter',
        'group_id': 'logging',
        'feature_key': 'remove_formatter',
        'name': 'Remove Formatter',
        'description': 'Remove a logging formatter by ID.',
        'params_schema': {
            'id': 'str',
        },
        'steps': [{'service_id': 'remove_formatter_evt', 'name': 'Remove formatter'}],
    },
    {
        'id': 'logging.add_handler',
        'group_id': 'logging',
        'feature_key': 'add_handler',
        'name': 'Add Handler',
        'description': 'Add a new logging handler configuration.',
        'params_schema': {
            'id': 'str',
            'name': 'str',
            'module_path': 'str',
            'class_name': 'str',
            'level': 'str',
            'formatter': 'str',
            'description': {'type': 'str', 'required': False},
            'stream': {'type': 'str', 'required': False},
            'filename': {'type': 'str', 'required': False},
        },
        'steps': [{'service_id': 'add_handler_evt', 'name': 'Add handler'}],
    },
    {
        'id': 'logging.remove_handler',
        'group_id': 'logging',
        'feature_key': 'remove_handler',
        'name': 'Remove Handler',
        'description': 'Remove a logging handler by ID.',
        'params_schema': {
            'id': 'str',
        },
        'steps': [{'service_id': 'remove_handler_evt', 'name': 'Remove handler'}],
    },
    {
        'id': 'logging.add_logger',
        'group_id': 'logging',
        'feature_key': 'add_logger',
        'name': 'Add Logger',
        'description': 'Add a new logger configuration.',
        'params_schema': {
            'id': 'str',
            'name': 'str',
            'level': 'str',
            'description': {'type': 'str', 'required': False},
            'propagate': {'type': 'bool', 'required': False, 'default': True},
        },
        'steps': [{'service_id': 'add_logger_evt', 'name': 'Add logger'}],
    },
    {
        'id': 'logging.remove_logger',
        'group_id': 'logging',
        'feature_key': 'remove_logger',
        'name': 'Remove Logger',
        'description': 'Remove a logger by ID.',
        'params_schema': {
            'id': 'str',
        },
        'steps': [{'service_id': 'remove_logger_evt', 'name': 'Remove logger'}],
    },
    {
        'id': 'logging.list',
        'group_id': 'logging',
        'feature_key': 'list',
        'name': 'List Logging Configs',
        'description': 'List all logging configurations (formatters, handlers, loggers).',
        'steps': [{'service_id': 'logging_list_all_evt', 'name': 'List all logging configs'}],
    },
]

# ** config: default_tiferet_cli_features
# Id-keyed mapping mirroring YAML shape: the key is the feature id and the
# value is the record minus id. The bootstrap builder in the orchestration
# layer materializes each record into a typed Feature object.
DEFAULT_TIFERET_CLI_FEATURES: Dict[str, Dict[str, Any]] = {
    entry['id']: {key: value for key, value in entry.items() if key != 'id'}
    for entry in _DEFAULT_TIFERET_CLI_FEATURE_LIST
}
