"""Tiferet Assets Builders

Provides default constants and default service wiring definitions used during
application bootstrapping and container initialization.
"""

# *** imports

# ** core
from typing import Any, Dict, List, Tuple

# *** constants

# ** constant: default_constants
DEFAULT_CONSTANTS: Dict[str, str] = {
    'cli_yaml_file': 'config.yml',
    'di_yaml_file': 'config.yml',
    'error_yaml_file': 'config.yml',
    'logging_yaml_file': 'config.yml',
    'feature_yaml_file': 'config.yml',
}

# ** constant: default_app_service_module_path
DEFAULT_APP_SERVICE_MODULE_PATH: str = 'tiferet.repos.app'

# ** constant: default_app_service_class_name
DEFAULT_APP_SERVICE_CLASS_NAME: str = 'AppYamlRepository'

# ** constant: default_services
# Each tuple contains exactly 4 elements in this order:
# (service_id, module_path, class_name, parameters)
# Use None for parameters when no additional DI parameters are required.
DEFAULT_SERVICES: List[Tuple[str, str, str, Dict[str, Any] | None]] = [
    ('di_service', 'tiferet.repos.di', 'DIYamlRepository', None),
    ('error_service', 'tiferet.repos.error', 'ErrorYamlRepository', None),
    ('logging_service', 'tiferet.repos.logging', 'LoggingYamlRepository', None),
    ('feature_service', 'tiferet.repos.feature', 'FeatureYamlRepository', None),
    ('get_error_evt', 'tiferet.events.error', 'GetError', None),
    ('get_feature_evt', 'tiferet.events.feature', 'GetFeature', None),
    ('logging_list_all_evt', 'tiferet.events.logging', 'ListAllLoggingConfigs', None),
    ('cli_service', 'tiferet.repos.cli', 'CliYamlRepository', None),
    ('list_commands_evt', 'tiferet.events.cli', 'ListCliCommands', None),
    ('get_parent_args_evt', 'tiferet.events.cli', 'GetParentArguments', None),
    ('di_list_all_configs_evt', 'tiferet.events.di', 'ListAllSettings', None),
    ('services', 'tiferet.contexts.di', 'DIContext', None),
    ('features', 'tiferet.contexts.feature', 'FeatureContext', None),
    ('errors', 'tiferet.contexts.error', 'ErrorContext', None),
    ('logging', 'tiferet.contexts.logging', 'LoggingContext', None),
]
