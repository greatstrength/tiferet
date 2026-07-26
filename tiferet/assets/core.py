"""Tiferet Core (Assets)"""

# *** imports

# ** core
from typing import Any, Dict, List, Tuple

# *** constants

# ** constant: en_us
EN_US = 'en_US'

# *** constants (bootstrap)

# ** constant: default_app_service_module_path
DEFAULT_APP_SERVICE_MODULE_PATH: str = 'tiferet.repos.app'

# ** constant: default_app_service_class_name
DEFAULT_APP_SERVICE_CLASS_NAME: str = 'AppYamlRepository'

# ** constant: default_constants
DEFAULT_CONSTANTS: Dict[str, str] = {
    'cli_yaml_file': 'config.yml',
    'di_yaml_file': 'config.yml',
    'error_yaml_file': 'config.yml',
    'logging_yaml_file': 'config.yml',
    'feature_yaml_file': 'config.yml',
}

# ** constant: default_services
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

# *** functions

# ** function: create_default_error
def create_default_error(id: str,
        name: str,
        messages: List[Tuple[str, str]]) -> Dict[str, Any]:
    '''
    Build a default error definition dictionary.

    :param id: The unique identifier of the error.
    :type id: str
    :param name: The human-readable error name.
    :type name: str
    :param messages: Ordered (lang, text) message pairs.
    :type messages: List[Tuple[str, str]]
    :return: The default error definition.
    :rtype: Dict[str, Any]
    '''

    # Assemble and return the default error definition dictionary.
    return {
        'id': id,
        'name': name,
        'message': [{'lang': lang, 'text': text} for lang, text in messages],
    }

# ** function: create_app_service_dependency
def create_app_service_dependency(
        service_id: str,
        module_path: str,
        class_name: str,
        parameters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
    '''
    Build a default app service dependency definition dictionary.

    :param service_id: The unique service identifier for the dependency.
    :type service_id: str
    :param module_path: The module path of the service implementation.
    :type module_path: str
    :param class_name: The class name of the service implementation.
    :type class_name: str
    :param parameters: Optional DI parameters for the dependency.
    :type parameters: Dict[str, Any]
    :return: The default app service dependency definition.
    :rtype: Dict[str, Any]
    '''

    # Assemble and return the default app service dependency definition dictionary.
    return {
        'service_id': service_id,
        'module_path': module_path,
        'class_name': class_name,
        'parameters': parameters or {},
    }
