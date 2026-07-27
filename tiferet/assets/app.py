"""Tiferet App Assets

App service ID constants, module path constants, default app service and session
definitions, service model constants (built via create_service_module_path), and
the bootstrap catalog dicts consumed by the blueprint layer during cache seeding.
"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from .core import (
    create_app_service_dependency,
    create_default_app_session,
    create_service_module_path,
    TIFERET,
    TIFERET_EVENTS_PATH,
    TIFERET_REPOS_PATH,
    TIFERET_UTILS_PATH,
    FEATURE_DOMAIN_PATH,
    ERROR_DOMAIN_PATH,
    DI_DOMAIN_PATH,
    APP_DOMAIN_PATH,
    LOGGING_DOMAIN_PATH,
    CLI_DOMAIN_PATH,
    MIDDLEWARE_DOMAIN_PATH,
)

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

# ** constant: logging_middleware_id
LOGGING_MIDDLEWARE_ID = 'logging_middleware'

# ** constant: timing_middleware_id
TIMING_MIDDLEWARE_ID = 'timing_middleware'

# ** constant: cache_middleware_id
CACHE_MIDDLEWARE_ID = 'cache_middleware'

# ** constant: tiferet_admin_id
TIFERET_ADMIN_ID = 'admin'

# ** constant: tiferet_admin_cli_id
TIFERET_ADMIN_CLI_ID = 'admin_cli'

# *** constants (paths)

# ** constant: default_config_file
DEFAULT_CONFIG_FILE = 'config.yml'

# ** constant: default_app_config_file
DEFAULT_APP_CONFIG_FILE = DEFAULT_CONFIG_FILE

# *** constants (app_service)

# ** constant: default_app_service_module_path
DEFAULT_APP_SERVICE_MODULE_PATH = create_service_module_path(
    TIFERET,
    TIFERET_REPOS_PATH,
    APP_DOMAIN_PATH,
)

# ** constant: default_app_service_class_name
DEFAULT_APP_SERVICE_CLASS_NAME = 'AppConfigRepository'

# ** constant: default_app_service_parameters
DEFAULT_APP_SERVICE_PARAMETERS = {'app_config': DEFAULT_APP_CONFIG_FILE}

# *** constants (sessions)

# ** constant: default_admin_app_session
DEFAULT_ADMIN_APP_SESSION = create_default_app_session(
    TIFERET_ADMIN_ID,
    'Admin App',
    'Default built-in admin application session',
)

# ** constant: default_admin_cli_session
DEFAULT_ADMIN_CLI_SESSION = create_default_app_session(
    TIFERET_ADMIN_CLI_ID,
    'Admin CLI',
    'Built-in CLI for managing Tiferet application configurations',
)

# *** constants (services)

# ** constant: di_service
DI_SERVICE = create_app_service_dependency(
    DI_SERVICE_ID,
    create_service_module_path(TIFERET, TIFERET_REPOS_PATH, DI_DOMAIN_PATH),
    'DIConfigRepository',
)

# ** constant: error_service
ERROR_SERVICE = create_app_service_dependency(
    ERROR_SERVICE_ID,
    create_service_module_path(TIFERET, TIFERET_REPOS_PATH, ERROR_DOMAIN_PATH),
    'ErrorConfigRepository',
)

# ** constant: logging_service
LOGGING_SERVICE = create_app_service_dependency(
    LOGGING_SERVICE_ID,
    create_service_module_path(TIFERET, TIFERET_REPOS_PATH, LOGGING_DOMAIN_PATH),
    'LoggingConfigRepository',
)

# ** constant: feature_service
FEATURE_SERVICE = create_app_service_dependency(
    FEATURE_SERVICE_ID,
    create_service_module_path(TIFERET, TIFERET_REPOS_PATH, FEATURE_DOMAIN_PATH),
    'FeatureConfigRepository',
)

# ** constant: get_error_evt
GET_ERROR_EVT = create_app_service_dependency(
    GET_ERROR_EVT_ID,
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, ERROR_DOMAIN_PATH),
    'GetError',
)

# ** constant: get_feature_evt
GET_FEATURE_EVT = create_app_service_dependency(
    GET_FEATURE_EVT_ID,
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'GetFeature',
)

# ** constant: logging_list_all_evt
LOGGING_LIST_ALL_EVT = create_app_service_dependency(
    LOGGING_LIST_ALL_EVT_ID,
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, LOGGING_DOMAIN_PATH),
    'ListAllLoggingConfigs',
)

# ** constant: cli_service
CLI_SERVICE = create_app_service_dependency(
    CLI_SERVICE_ID,
    create_service_module_path(TIFERET, TIFERET_REPOS_PATH, CLI_DOMAIN_PATH),
    'CliConfigRepository',
)

# ** constant: list_commands_evt
LIST_COMMANDS_EVT = create_app_service_dependency(
    LIST_COMMANDS_EVT_ID,
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, CLI_DOMAIN_PATH),
    'ListCliCommands',
)

# ** constant: get_parent_args_evt
GET_PARENT_ARGS_EVT = create_app_service_dependency(
    GET_PARENT_ARGS_EVT_ID,
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, CLI_DOMAIN_PATH),
    'GetParentArguments',
)

# ** constant: di_list_all_configs_evt
DI_LIST_ALL_CONFIGS_EVT = create_app_service_dependency(
    DI_LIST_ALL_CONFIGS_EVT_ID,
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, DI_DOMAIN_PATH),
    'ListAllSettings',
)

# ** constant: logging_middleware
LOGGING_MIDDLEWARE = create_app_service_dependency(
    LOGGING_MIDDLEWARE_ID,
    create_service_module_path(TIFERET, TIFERET_UTILS_PATH, MIDDLEWARE_DOMAIN_PATH),
    'LoggingMiddleware',
)

# ** constant: timing_middleware
TIMING_MIDDLEWARE = create_app_service_dependency(
    TIMING_MIDDLEWARE_ID,
    create_service_module_path(TIFERET, TIFERET_UTILS_PATH, MIDDLEWARE_DOMAIN_PATH),
    'TimingMiddleware',
)

# ** constant: cache_middleware
CACHE_MIDDLEWARE = create_app_service_dependency(
    CACHE_MIDDLEWARE_ID,
    create_service_module_path(TIFERET, TIFERET_UTILS_PATH, MIDDLEWARE_DOMAIN_PATH),
    'CacheMiddleware',
)

# *** constants (groups)

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
    LOGGING_MIDDLEWARE_ID: LOGGING_MIDDLEWARE,
    TIMING_MIDDLEWARE_ID: TIMING_MIDDLEWARE,
    CACHE_MIDDLEWARE_ID: CACHE_MIDDLEWARE,
}

# ** constant: core_default_constants
CORE_DEFAULT_CONSTANTS: Dict[str, str] = {
    CLI_CONFIG_ID: DEFAULT_CONFIG_FILE,
    DI_CONFIG_ID: DEFAULT_CONFIG_FILE,
    ERROR_CONFIG_ID: DEFAULT_CONFIG_FILE,
    LOGGING_CONFIG_ID: DEFAULT_CONFIG_FILE,
    FEATURE_CONFIG_ID: DEFAULT_CONFIG_FILE,
}

# ** constant: admin_default_services
ADMIN_DEFAULT_SERVICES = {**CORE_DEFAULT_SERVICES}

# ** constant: admin_default_constants
# Core constants plus the app_config key that the admin layer exposes directly.
ADMIN_DEFAULT_CONSTANTS = {**CORE_DEFAULT_CONSTANTS, 'app_config': DEFAULT_CONFIG_FILE}

# ** constant: core_default_app_sessions
# Built-in session definitions seeded into the cache by build_cache.
CORE_DEFAULT_APP_SESSIONS = {
    TIFERET_ADMIN_ID: DEFAULT_ADMIN_APP_SESSION,
    TIFERET_ADMIN_CLI_ID: DEFAULT_ADMIN_CLI_SESSION,
}
