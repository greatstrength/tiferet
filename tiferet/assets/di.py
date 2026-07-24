"""Tiferet CLI DI Service Catalog"""

# *** imports

# ** core
from typing import Any, Dict, List, Tuple

# *** constants

# ** constant: default_tiferet_cli_services
DEFAULT_TIFERET_CLI_SERVICES: List[Tuple[str, str, str, Dict[str, Any] | None]] = [
    ('app_service', 'tiferet.repos.app', 'AppYamlRepository', None),
    ('list_app_interfaces_evt', 'tiferet.events.app', 'ListAppInterfaces', None),
    ('add_app_interface_evt', 'tiferet.events.app', 'AddAppInterface', None),
    ('update_app_interface_evt', 'tiferet.events.app', 'UpdateAppInterface', None),
    ('set_app_service_dependency_evt', 'tiferet.events.app', 'SetServiceDependency', None),
    ('remove_app_service_dependency_evt', 'tiferet.events.app', 'RemoveServiceDependency', None),
    ('set_app_constants_evt', 'tiferet.events.app', 'SetAppConstants', None),
    ('remove_app_interface_evt', 'tiferet.events.app', 'RemoveAppInterface', None),
    ('add_service_registration_evt', 'tiferet.events.di', 'AddServiceRegistration', None),
    ('set_default_service_registration_evt', 'tiferet.events.di', 'SetDefaultServiceRegistration', None),
    ('set_service_dependency_evt', 'tiferet.events.di', 'SetServiceDependency', None),
    ('remove_service_dependency_evt', 'tiferet.events.di', 'RemoveServiceDependency', None),
    ('remove_service_registration_evt', 'tiferet.events.di', 'RemoveServiceRegistration', None),
    ('set_service_constants_evt', 'tiferet.events.di', 'SetServiceConstants', None),
    ('list_features_evt', 'tiferet.events.feature', 'ListFeatures', None),
    ('add_feature_evt', 'tiferet.events.feature', 'AddFeature', None),
    ('update_feature_evt', 'tiferet.events.feature', 'UpdateFeature', None),
    ('add_feature_step_evt', 'tiferet.events.feature', 'AddFeatureStep', None),
    ('update_feature_step_evt', 'tiferet.events.feature', 'UpdateFeatureStep', None),
    ('remove_feature_step_evt', 'tiferet.events.feature', 'RemoveFeatureStep', None),
    ('reorder_feature_step_evt', 'tiferet.events.feature', 'ReorderFeatureStep', None),
    ('remove_feature_evt', 'tiferet.events.feature', 'RemoveFeature', None),
    ('list_errors_evt', 'tiferet.events.error', 'ListErrors', None),
    ('add_error_evt', 'tiferet.events.error', 'AddError', None),
    ('rename_error_evt', 'tiferet.events.error', 'RenameError', None),
    ('set_error_message_evt', 'tiferet.events.error', 'SetErrorMessage', None),
    ('remove_error_message_evt', 'tiferet.events.error', 'RemoveErrorMessage', None),
    ('remove_error_evt', 'tiferet.events.error', 'RemoveError', None),
    ('add_cli_command_evt', 'tiferet.events.cli', 'AddCliCommand', None),
    ('add_cli_argument_evt', 'tiferet.events.cli', 'AddCliArgument', None),
]
