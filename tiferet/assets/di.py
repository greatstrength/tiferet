"""Tiferet Assets Service

Provides the default service configurations for the built-in Tiferet CLI
management application. These register domain events as injectable services
for CLI feature workflows.

Services already defined in ``blueprints.DEFAULT_SERVICES`` (e.g.
``get_error_evt``, ``get_feature_evt``, ``list_all_settings_evt``) are
**not** duplicated here. The blueprint merges both lists at startup.
"""

# *** imports

# ** core
from typing import Any, Dict, List, Tuple

# *** constants

# ** constant: default_tiferet_cli_services
# Each tuple: (service_id, module_path, class_name, parameters | None)
DEFAULT_TIFERET_CLI_SERVICES: List[Tuple[str, str, str, Dict[str, Any] | None]] = [

    # * services: app_service (repository — needed by app domain events)
    ('app_service', 'tiferet.repos.app', 'AppConfigRepository', None),

    # * services: feature domain events
    ('add_feature_evt', 'tiferet.events.feature', 'AddFeature', None),
    ('list_features_evt', 'tiferet.events.feature', 'ListFeatures', None),
    ('remove_feature_evt', 'tiferet.events.feature', 'RemoveFeature', None),
    ('update_feature_evt', 'tiferet.events.feature', 'UpdateFeature', None),
    ('add_feature_step_evt', 'tiferet.events.feature', 'AddFeatureStep', None),
    ('update_feature_step_evt', 'tiferet.events.feature', 'UpdateFeatureStep', None),
    ('remove_feature_step_evt', 'tiferet.events.feature', 'RemoveFeatureStep', None),
    ('reorder_feature_step_evt', 'tiferet.events.feature', 'ReorderFeatureStep', None),

    # * services: error domain events
    ('add_error_evt', 'tiferet.events.error', 'AddError', None),
    ('list_errors_evt', 'tiferet.events.error', 'ListErrors', None),
    ('rename_error_evt', 'tiferet.events.error', 'RenameError', None),
    ('set_error_message_evt', 'tiferet.events.error', 'SetErrorMessage', None),
    ('remove_error_message_evt', 'tiferet.events.error', 'RemoveErrorMessage', None),
    ('remove_error_evt', 'tiferet.events.error', 'RemoveError', None),

    # * services: di (service configuration) domain events
    ('add_service_registration_evt', 'tiferet.events.di', 'AddServiceRegistration', None),
    ('set_default_service_registration_evt', 'tiferet.events.di', 'SetDefaultServiceRegistration', None),
    ('set_di_service_dependency_evt', 'tiferet.events.di', 'SetServiceDependency', None),
    ('remove_di_service_dependency_evt', 'tiferet.events.di', 'RemoveServiceDependency', None),
    ('remove_service_registration_evt', 'tiferet.events.di', 'RemoveServiceRegistration', None),
    ('set_service_constants_evt', 'tiferet.events.di', 'SetServiceConstants', None),

    # * services: app interface domain events
    ('add_app_interface_evt', 'tiferet.events.app', 'AddAppInterface', None),
    ('get_app_interface_evt', 'tiferet.events.app', 'GetAppInterface', None),
    ('update_app_interface_evt', 'tiferet.events.app', 'UpdateAppInterface', None),
    ('set_app_constants_evt', 'tiferet.events.app', 'SetAppConstants', None),
    ('list_app_interfaces_evt', 'tiferet.events.app', 'ListAppInterfaces', None),
    ('set_app_service_dependency_evt', 'tiferet.events.app', 'SetServiceDependency', None),
    ('remove_app_service_dependency_evt', 'tiferet.events.app', 'RemoveServiceDependency', None),
    ('remove_app_interface_evt', 'tiferet.events.app', 'RemoveAppInterface', None),

    # * services: cli domain events
    ('add_cli_command_evt', 'tiferet.events.cli', 'AddCliCommand', None),
    ('add_cli_argument_evt', 'tiferet.events.cli', 'AddCliArgument', None),

    # * services: logging domain events
    ('add_formatter_evt', 'tiferet.events.logging', 'AddFormatter', None),
    ('remove_formatter_evt', 'tiferet.events.logging', 'RemoveFormatter', None),
    ('add_handler_evt', 'tiferet.events.logging', 'AddHandler', None),
    ('remove_handler_evt', 'tiferet.events.logging', 'RemoveHandler', None),
    ('add_logger_evt', 'tiferet.events.logging', 'AddLogger', None),
    ('remove_logger_evt', 'tiferet.events.logging', 'RemoveLogger', None),
]
