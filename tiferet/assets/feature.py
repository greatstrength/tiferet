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

# ** config: default_tiferet_cli_features
# Each dict matches the Feature domain object constructor fields.
# Steps use FeatureEvent field names: service_id, name, parameters, data_key.
DEFAULT_TIFERET_CLI_FEATURES: List[Dict[str, Any]] = [

    # * features: feature domain
    dict(
        id='feature.add',
        group_id='feature',
        feature_key='add',
        name='Add Feature',
        description='Add a new feature configuration.',
        steps=[dict(service_id='add_feature_evt', name='Add feature')],
    ),
    dict(
        id='feature.get',
        group_id='feature',
        feature_key='get',
        name='Get Feature',
        description='Retrieve a feature by ID.',
        steps=[dict(service_id='get_feature_evt', name='Get feature')],
    ),
    dict(
        id='feature.list',
        group_id='feature',
        feature_key='list',
        name='List Features',
        description='List all features, optionally filtered by group.',
        steps=[dict(service_id='list_features_evt', name='List features')],
    ),
    dict(
        id='feature.remove',
        group_id='feature',
        feature_key='remove',
        name='Remove Feature',
        description='Remove a feature configuration by ID.',
        steps=[dict(service_id='remove_feature_evt', name='Remove feature')],
    ),
    dict(
        id='feature.update',
        group_id='feature',
        feature_key='update',
        name='Update Feature',
        description='Update a feature attribute (name or description).',
        steps=[dict(service_id='update_feature_evt', name='Update feature')],
    ),
    dict(
        id='feature.add_step',
        group_id='feature',
        feature_key='add_step',
        name='Add Feature Step',
        description='Add a step to an existing feature workflow.',
        steps=[dict(service_id='add_feature_step_evt', name='Add feature step')],
    ),
    dict(
        id='feature.update_step',
        group_id='feature',
        feature_key='update_step',
        name='Update Feature Step',
        description='Update an attribute on a feature step.',
        steps=[dict(service_id='update_feature_step_evt', name='Update feature step')],
    ),
    dict(
        id='feature.remove_step',
        group_id='feature',
        feature_key='remove_step',
        name='Remove Feature Step',
        description='Remove a step from a feature by position.',
        steps=[dict(service_id='remove_feature_step_evt', name='Remove feature step')],
    ),
    dict(
        id='feature.reorder_step',
        group_id='feature',
        feature_key='reorder_step',
        name='Reorder Feature Step',
        description='Move a feature step from one position to another.',
        steps=[dict(service_id='reorder_feature_step_evt', name='Reorder feature step')],
    ),

    # * features: error domain
    dict(
        id='error.add',
        group_id='error',
        feature_key='add',
        name='Add Error',
        description='Add a new error definition.',
        steps=[dict(service_id='add_error_evt', name='Add error')],
    ),
    dict(
        id='error.get',
        group_id='error',
        feature_key='get',
        name='Get Error',
        description='Retrieve an error by ID.',
        steps=[dict(service_id='get_error_evt', name='Get error')],
    ),
    dict(
        id='error.list',
        group_id='error',
        feature_key='list',
        name='List Errors',
        description='List all error definitions.',
        steps=[dict(service_id='list_errors_evt', name='List errors')],
    ),
    dict(
        id='error.rename',
        group_id='error',
        feature_key='rename',
        name='Rename Error',
        description='Rename an existing error.',
        steps=[dict(service_id='rename_error_evt', name='Rename error')],
    ),
    dict(
        id='error.set_message',
        group_id='error',
        feature_key='set_message',
        name='Set Error Message',
        description='Set or update an error message for a language.',
        steps=[dict(service_id='set_error_message_evt', name='Set error message')],
    ),
    dict(
        id='error.remove_message',
        group_id='error',
        feature_key='remove_message',
        name='Remove Error Message',
        description='Remove an error message by language.',
        steps=[dict(service_id='remove_error_message_evt', name='Remove error message')],
    ),
    dict(
        id='error.remove',
        group_id='error',
        feature_key='remove',
        name='Remove Error',
        description='Remove an error definition by ID.',
        steps=[dict(service_id='remove_error_evt', name='Remove error')],
    ),

    # * features: service (DI) domain
    dict(
        id='service.add',
        group_id='service',
        feature_key='add',
        name='Add Service Configuration',
        description='Add a new service configuration.',
        steps=[dict(service_id='add_service_configuration_evt', name='Add service configuration')],
    ),
    dict(
        id='service.list',
        group_id='service',
        feature_key='list',
        name='List All Settings',
        description='List all service configurations and constants.',
        steps=[dict(service_id='di_list_all_configs_evt', name='List all settings')],
    ),
    dict(
        id='service.set_default',
        group_id='service',
        feature_key='set_default',
        name='Set Default Service Configuration',
        description='Set or update the default type for a service configuration.',
        steps=[dict(service_id='set_default_service_configuration_evt', name='Set default service configuration')],
    ),
    dict(
        id='service.set_dependency',
        group_id='service',
        feature_key='set_dependency',
        name='Set Service Dependency',
        description='Set or update a flagged dependency on a service configuration.',
        steps=[dict(service_id='set_di_service_dependency_evt', name='Set service dependency')],
    ),
    dict(
        id='service.remove_dependency',
        group_id='service',
        feature_key='remove_dependency',
        name='Remove Service Dependency',
        description='Remove a flagged dependency from a service configuration.',
        steps=[dict(service_id='remove_di_service_dependency_evt', name='Remove service dependency')],
    ),
    dict(
        id='service.remove',
        group_id='service',
        feature_key='remove',
        name='Remove Service Configuration',
        description='Remove a service configuration by ID.',
        steps=[dict(service_id='remove_service_configuration_evt', name='Remove service configuration')],
    ),
    dict(
        id='service.set_constants',
        group_id='service',
        feature_key='set_constants',
        name='Set Service Constants',
        description='Set or clear service-level constants.',
        steps=[dict(service_id='set_service_constants_evt', name='Set service constants')],
    ),

    # * features: app interface domain
    dict(
        id='app.add',
        group_id='app',
        feature_key='add',
        name='Add App Interface',
        description='Add a new application interface configuration.',
        steps=[dict(service_id='add_app_interface_evt', name='Add app interface')],
    ),
    dict(
        id='app.get',
        group_id='app',
        feature_key='get',
        name='Get App Interface',
        description='Retrieve an app interface by ID.',
        steps=[dict(service_id='get_app_interface_evt', name='Get app interface')],
    ),
    dict(
        id='app.list',
        group_id='app',
        feature_key='list',
        name='List App Interfaces',
        description='List all configured app interfaces.',
        steps=[dict(service_id='list_app_interfaces_evt', name='List app interfaces')],
    ),
    dict(
        id='app.update',
        group_id='app',
        feature_key='update',
        name='Update App Interface',
        description='Update a scalar attribute on an app interface.',
        steps=[dict(service_id='update_app_interface_evt', name='Update app interface')],
    ),
    dict(
        id='app.set_constants',
        group_id='app',
        feature_key='set_constants',
        name='Set App Constants',
        description='Set or clear constants on an app interface.',
        steps=[dict(service_id='set_app_constants_evt', name='Set app constants')],
    ),
    dict(
        id='app.set_service',
        group_id='app',
        feature_key='set_service',
        name='Set App Service Dependency',
        description='Set or update a service dependency on an app interface.',
        steps=[dict(service_id='set_app_service_dependency_evt', name='Set app service dependency')],
    ),
    dict(
        id='app.remove_service',
        group_id='app',
        feature_key='remove_service',
        name='Remove App Service Dependency',
        description='Remove a service dependency from an app interface.',
        steps=[dict(service_id='remove_app_service_dependency_evt', name='Remove app service dependency')],
    ),
    dict(
        id='app.remove',
        group_id='app',
        feature_key='remove',
        name='Remove App Interface',
        description='Remove an app interface by ID.',
        steps=[dict(service_id='remove_app_interface_evt', name='Remove app interface')],
    ),

    # * features: cli domain
    dict(
        id='cli.add_command',
        group_id='cli',
        feature_key='add_command',
        name='Add CLI Command',
        description='Add a new CLI command definition.',
        steps=[dict(service_id='add_cli_command_evt', name='Add CLI command')],
    ),
    dict(
        id='cli.list_commands',
        group_id='cli',
        feature_key='list_commands',
        name='List CLI Commands',
        description='List all CLI command definitions.',
        steps=[dict(service_id='list_commands_evt', name='List CLI commands')],
    ),
    dict(
        id='cli.add_argument',
        group_id='cli',
        feature_key='add_argument',
        name='Add CLI Argument',
        description='Add an argument to an existing CLI command.',
        steps=[dict(service_id='add_cli_argument_evt', name='Add CLI argument')],
    ),

    # * features: logging domain
    dict(
        id='logging.add_formatter',
        group_id='logging',
        feature_key='add_formatter',
        name='Add Formatter',
        description='Add a new logging formatter configuration.',
        steps=[dict(service_id='add_formatter_evt', name='Add formatter')],
    ),
    dict(
        id='logging.remove_formatter',
        group_id='logging',
        feature_key='remove_formatter',
        name='Remove Formatter',
        description='Remove a logging formatter by ID.',
        steps=[dict(service_id='remove_formatter_evt', name='Remove formatter')],
    ),
    dict(
        id='logging.add_handler',
        group_id='logging',
        feature_key='add_handler',
        name='Add Handler',
        description='Add a new logging handler configuration.',
        steps=[dict(service_id='add_handler_evt', name='Add handler')],
    ),
    dict(
        id='logging.remove_handler',
        group_id='logging',
        feature_key='remove_handler',
        name='Remove Handler',
        description='Remove a logging handler by ID.',
        steps=[dict(service_id='remove_handler_evt', name='Remove handler')],
    ),
    dict(
        id='logging.add_logger',
        group_id='logging',
        feature_key='add_logger',
        name='Add Logger',
        description='Add a new logger configuration.',
        steps=[dict(service_id='add_logger_evt', name='Add logger')],
    ),
    dict(
        id='logging.remove_logger',
        group_id='logging',
        feature_key='remove_logger',
        name='Remove Logger',
        description='Remove a logger by ID.',
        steps=[dict(service_id='remove_logger_evt', name='Remove logger')],
    ),
    dict(
        id='logging.list',
        group_id='logging',
        feature_key='list',
        name='List Logging Configs',
        description='List all logging configurations (formatters, handlers, loggers).',
        steps=[dict(service_id='logging_list_all_evt', name='List all logging configs')],
    ),
]
