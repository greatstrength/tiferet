"""Tiferet App Assets

App service ID constants, default app service data, and the CORE_DEFAULT_SERVICES /
CORE_DEFAULT_CONSTANTS bootstrap catalogs consumed by the blueprint layer during
cache seeding for application bootstrapping.
"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from .core import create_app_service_dependency

# *** constants (ids)

# ** constant: di_service_id
DI_SERVICE_ID = 'di_service'

# ** constant: error_service_id
ERROR_SERVICE_ID = 'error_service'

# ** constant: logging_service_id
LOGGING_SERVICE_ID = 'logging_service'

# ** constant: feature_service_id
FEATURE_SERVICE_ID = 'feature_service'

# ** constant: get_error_evt_id
GET_ERROR_EVT_ID = 'get_error_evt'

# ** constant: get_feature_evt_id
GET_FEATURE_EVT_ID = 'get_feature_evt'

# ** constant: logging_list_all_evt_id
LOGGING_LIST_ALL_EVT_ID = 'logging_list_all_evt'

# ** constant: cli_service_id
CLI_SERVICE_ID = 'cli_service'

# ** constant: list_commands_evt_id
LIST_COMMANDS_EVT_ID = 'list_commands_evt'

# ** constant: get_parent_args_evt_id
GET_PARENT_ARGS_EVT_ID = 'get_parent_args_evt'

# ** constant: di_list_all_configs_evt_id
DI_LIST_ALL_CONFIGS_EVT_ID = 'di_list_all_configs_evt'

# ** constant: cli_config_id
CLI_CONFIG_ID = 'cli_config'

# ** constant: di_config_id
DI_CONFIG_ID = 'di_config'

# ** constant: error_config_id
ERROR_CONFIG_ID = 'error_config'

# ** constant: logging_config_id
LOGGING_CONFIG_ID = 'logging_config'

# ** constant: feature_config_id
FEATURE_CONFIG_ID = 'feature_config'

# *** constants (models)

# ** constant: default_config_file
DEFAULT_CONFIG_FILE = 'config.yml'

# ** constant: default_app_service_module_path
DEFAULT_APP_SERVICE_MODULE_PATH = 'tiferet.repos.app'

# ** constant: default_app_service_class_name
DEFAULT_APP_SERVICE_CLASS_NAME = 'AppConfigRepository'

# ** constant: default_app_service_parameters
DEFAULT_APP_SERVICE_PARAMETERS = {'app_config': DEFAULT_CONFIG_FILE}

# ** constant: di_service
DI_SERVICE = create_app_service_dependency(
    DI_SERVICE_ID,
    'tiferet.repos.di',
    'DIConfigRepository',
)

# ** constant: error_service
ERROR_SERVICE = create_app_service_dependency(
    ERROR_SERVICE_ID,
    'tiferet.repos.error',
    'ErrorConfigRepository',
)

# ** constant: logging_service
LOGGING_SERVICE = create_app_service_dependency(
    LOGGING_SERVICE_ID,
    'tiferet.repos.logging',
    'LoggingConfigRepository',
)

# ** constant: feature_service
FEATURE_SERVICE = create_app_service_dependency(
    FEATURE_SERVICE_ID,
    'tiferet.repos.feature',
    'FeatureConfigRepository',
)

# ** constant: get_error_evt
GET_ERROR_EVT = create_app_service_dependency(
    GET_ERROR_EVT_ID,
    'tiferet.events.error',
    'GetError',
)

# ** constant: get_feature_evt
GET_FEATURE_EVT = create_app_service_dependency(
    GET_FEATURE_EVT_ID,
    'tiferet.events.feature',
    'GetFeature',
)

# ** constant: logging_list_all_evt
LOGGING_LIST_ALL_EVT = create_app_service_dependency(
    LOGGING_LIST_ALL_EVT_ID,
    'tiferet.events.logging',
    'ListAllLoggingConfigs',
)

# ** constant: cli_service
CLI_SERVICE = create_app_service_dependency(
    CLI_SERVICE_ID,
    'tiferet.repos.cli',
    'CliConfigRepository',
)

# ** constant: list_commands_evt
LIST_COMMANDS_EVT = create_app_service_dependency(
    LIST_COMMANDS_EVT_ID,
    'tiferet.events.cli',
    'ListCliCommands',
)

# ** constant: get_parent_args_evt
GET_PARENT_ARGS_EVT = create_app_service_dependency(
    GET_PARENT_ARGS_EVT_ID,
    'tiferet.events.cli',
    'GetParentArguments',
)

# ** constant: di_list_all_configs_evt
DI_LIST_ALL_CONFIGS_EVT = create_app_service_dependency(
    DI_LIST_ALL_CONFIGS_EVT_ID,
    'tiferet.events.di',
    'ListAllSettings',
)

# ** constant: core_default_services
CORE_DEFAULT_SERVICES: Dict[str, Dict[str, Any]] = {
    DI_SERVICE_ID: DI_SERVICE,
    ERROR_SERVICE_ID: ERROR_SERVICE,
    LOGGING_SERVICE_ID: LOGGING_SERVICE,
    FEATURE_SERVICE_ID: FEATURE_SERVICE,
    GET_ERROR_EVT_ID: GET_ERROR_EVT,
    GET_FEATURE_EVT_ID: GET_FEATURE_EVT,
    LOGGING_LIST_ALL_EVT_ID: LOGGING_LIST_ALL_EVT,
    CLI_SERVICE_ID: CLI_SERVICE,
    LIST_COMMANDS_EVT_ID: LIST_COMMANDS_EVT,
    GET_PARENT_ARGS_EVT_ID: GET_PARENT_ARGS_EVT,
    DI_LIST_ALL_CONFIGS_EVT_ID: DI_LIST_ALL_CONFIGS_EVT,
}

# ** constant: core_default_constants
CORE_DEFAULT_CONSTANTS: Dict[str, str] = {
    CLI_CONFIG_ID: DEFAULT_CONFIG_FILE,
    DI_CONFIG_ID: DEFAULT_CONFIG_FILE,
    ERROR_CONFIG_ID: DEFAULT_CONFIG_FILE,
    LOGGING_CONFIG_ID: DEFAULT_CONFIG_FILE,
    FEATURE_CONFIG_ID: DEFAULT_CONFIG_FILE,
}
