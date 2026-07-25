"""Tiferet Assets App

Provides the default interface definitions plus the core service-dependency and
bootstrap-constant catalogs for the built-in Tiferet application.

The service and constant catalogs mirror the default-error catalog in
``assets/error.py``: id constants, model constants (services built via
``create_app_service_dependency``), and group mappings
(``CORE_DEFAULT_SERVICES`` / ``CORE_DEFAULT_CONSTANTS``) consumed during
application bootstrapping and cache seeding.
"""

# *** imports

# ** app
from .core import (
    create_app_service_dependency,
    create_default_app_session,
    create_service_module_path,
    TIFERET_EVENTS_PATH,
    TIFERET_REPOS_PATH,
    FEATURE_DOMAIN_PATH,
    ERROR_DOMAIN_PATH,
    DI_DOMAIN_PATH,
    APP_DOMAIN_PATH,
    LOGGING_DOMAIN_PATH,
    CLI_DOMAIN_PATH,
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

# ** constant: app_service_id
APP_SERVICE_ID = 'app_service'

# ** constant: add_feature_evt_id
ADD_FEATURE_EVT_ID = 'add_feature_evt'

# ** constant: list_features_evt_id
LIST_FEATURES_EVT_ID = 'list_features_evt'

# ** constant: remove_feature_evt_id
REMOVE_FEATURE_EVT_ID = 'remove_feature_evt'

# ** constant: update_feature_evt_id
UPDATE_FEATURE_EVT_ID = 'update_feature_evt'

# ** constant: add_feature_step_evt_id
ADD_FEATURE_STEP_EVT_ID = 'add_feature_step_evt'

# ** constant: update_feature_step_evt_id
UPDATE_FEATURE_STEP_EVT_ID = 'update_feature_step_evt'

# ** constant: remove_feature_step_evt_id
REMOVE_FEATURE_STEP_EVT_ID = 'remove_feature_step_evt'

# ** constant: reorder_feature_step_evt_id
REORDER_FEATURE_STEP_EVT_ID = 'reorder_feature_step_evt'

# ** constant: add_error_evt_id
ADD_ERROR_EVT_ID = 'add_error_evt'

# ** constant: list_errors_evt_id
LIST_ERRORS_EVT_ID = 'list_errors_evt'

# ** constant: rename_error_evt_id
RENAME_ERROR_EVT_ID = 'rename_error_evt'

# ** constant: set_error_message_evt_id
SET_ERROR_MESSAGE_EVT_ID = 'set_error_message_evt'

# ** constant: remove_error_message_evt_id
REMOVE_ERROR_MESSAGE_EVT_ID = 'remove_error_message_evt'

# ** constant: remove_error_evt_id
REMOVE_ERROR_EVT_ID = 'remove_error_evt'

# ** constant: add_service_registration_evt_id
ADD_SERVICE_REGISTRATION_EVT_ID = 'add_service_registration_evt'

# ** constant: set_default_service_registration_evt_id
SET_DEFAULT_SERVICE_REGISTRATION_EVT_ID = 'set_default_service_registration_evt'

# ** constant: set_di_service_dependency_evt_id
SET_DI_SERVICE_DEPENDENCY_EVT_ID = 'set_di_service_dependency_evt'

# ** constant: remove_di_service_dependency_evt_id
REMOVE_DI_SERVICE_DEPENDENCY_EVT_ID = 'remove_di_service_dependency_evt'

# ** constant: remove_service_registration_evt_id
REMOVE_SERVICE_REGISTRATION_EVT_ID = 'remove_service_registration_evt'

# ** constant: set_service_constants_evt_id
SET_SERVICE_CONSTANTS_EVT_ID = 'set_service_constants_evt'

# ** constant: add_app_session_evt_id
ADD_APP_SESSION_EVT_ID = 'add_app_session_evt'

# ** constant: get_app_session_evt_id
GET_APP_SESSION_EVT_ID = 'get_app_session_evt'

# ** constant: update_app_session_evt_id
UPDATE_APP_SESSION_EVT_ID = 'update_app_session_evt'

# ** constant: set_app_constants_evt_id
SET_APP_CONSTANTS_EVT_ID = 'set_app_constants_evt'

# ** constant: list_app_sessions_evt_id
LIST_APP_SESSIONS_EVT_ID = 'list_app_sessions_evt'

# ** constant: set_app_service_dependency_evt_id
SET_APP_SERVICE_DEPENDENCY_EVT_ID = 'set_app_service_dependency_evt'

# ** constant: remove_app_service_dependency_evt_id
REMOVE_APP_SERVICE_DEPENDENCY_EVT_ID = 'remove_app_service_dependency_evt'

# ** constant: remove_app_session_evt_id
REMOVE_APP_SESSION_EVT_ID = 'remove_app_session_evt'

# ** constant: add_cli_command_evt_id
ADD_CLI_COMMAND_EVT_ID = 'add_cli_command_evt'

# ** constant: add_cli_argument_evt_id
ADD_CLI_ARGUMENT_EVT_ID = 'add_cli_argument_evt'

# ** constant: add_formatter_evt_id
ADD_FORMATTER_EVT_ID = 'add_formatter_evt'

# ** constant: remove_formatter_evt_id
REMOVE_FORMATTER_EVT_ID = 'remove_formatter_evt'

# ** constant: add_handler_evt_id
ADD_HANDLER_EVT_ID = 'add_handler_evt'

# ** constant: remove_handler_evt_id
REMOVE_HANDLER_EVT_ID = 'remove_handler_evt'

# ** constant: add_logger_evt_id
ADD_LOGGER_EVT_ID = 'add_logger_evt'

# ** constant: remove_logger_evt_id
REMOVE_LOGGER_EVT_ID = 'remove_logger_evt'

# *** constants (models)

# ** constant: default_admin_app_session
DEFAULT_ADMIN_APP_SESSION = create_default_app_session(
    TIFERET_ADMIN_ID,
    'Admin App',
    description='Default built-in admin application session',
)

# ** constant: default_admin_cli_session
DEFAULT_ADMIN_CLI_SESSION = create_default_app_session(
    TIFERET_ADMIN_CLI_ID,
    'Admin CLI',
    description='Built-in CLI for managing Tiferet application configurations',
)

# ** constant: default_config_file
DEFAULT_CONFIG_FILE = 'config.yml'

# ** constant: default_app_config_file
DEFAULT_APP_CONFIG_FILE = DEFAULT_CONFIG_FILE

# ** constant: default_app_service_module_path
DEFAULT_APP_SERVICE_MODULE_PATH = create_service_module_path(TIFERET_REPOS_PATH, APP_DOMAIN_PATH)

# ** constant: default_app_service_class_name
DEFAULT_APP_SERVICE_CLASS_NAME = 'AppConfigRepository'

# ** constant: default_app_service_parameters
DEFAULT_APP_SERVICE_PARAMETERS = {'app_config': DEFAULT_APP_CONFIG_FILE}

# ** constant: di_service
DI_SERVICE = create_app_service_dependency(
    DI_SERVICE_ID,
    create_service_module_path(TIFERET_REPOS_PATH, DI_DOMAIN_PATH),
    'DIConfigRepository',
)

# ** constant: error_service
ERROR_SERVICE = create_app_service_dependency(
    ERROR_SERVICE_ID,
    create_service_module_path(TIFERET_REPOS_PATH, ERROR_DOMAIN_PATH),
    'ErrorConfigRepository',
)

# ** constant: logging_service
LOGGING_SERVICE = create_app_service_dependency(
    LOGGING_SERVICE_ID,
    create_service_module_path(TIFERET_REPOS_PATH, LOGGING_DOMAIN_PATH),
    'LoggingConfigRepository',
)

# ** constant: feature_service
FEATURE_SERVICE = create_app_service_dependency(
    FEATURE_SERVICE_ID,
    create_service_module_path(TIFERET_REPOS_PATH, FEATURE_DOMAIN_PATH),
    'FeatureConfigRepository',
)

# ** constant: get_error_evt
GET_ERROR_EVT = create_app_service_dependency(
    GET_ERROR_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, ERROR_DOMAIN_PATH),
    'GetError',
)

# ** constant: get_feature_evt
GET_FEATURE_EVT = create_app_service_dependency(
    GET_FEATURE_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'GetFeature',
)

# ** constant: logging_list_all_evt
LOGGING_LIST_ALL_EVT = create_app_service_dependency(
    LOGGING_LIST_ALL_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, LOGGING_DOMAIN_PATH),
    'ListAllLoggingConfigs',
)

# ** constant: cli_service
CLI_SERVICE = create_app_service_dependency(
    CLI_SERVICE_ID,
    create_service_module_path(TIFERET_REPOS_PATH, CLI_DOMAIN_PATH),
    'CliConfigRepository',
)

# ** constant: list_commands_evt
LIST_COMMANDS_EVT = create_app_service_dependency(
    LIST_COMMANDS_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, CLI_DOMAIN_PATH),
    'ListCliCommands',
)

# ** constant: get_parent_args_evt
GET_PARENT_ARGS_EVT = create_app_service_dependency(
    GET_PARENT_ARGS_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, CLI_DOMAIN_PATH),
    'GetParentArguments',
)

# ** constant: di_list_all_configs_evt
DI_LIST_ALL_CONFIGS_EVT = create_app_service_dependency(
    DI_LIST_ALL_CONFIGS_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, DI_DOMAIN_PATH),
    'ListAllSettings',
)

# ** constant: logging_middleware
LOGGING_MIDDLEWARE = create_app_service_dependency(
    LOGGING_MIDDLEWARE_ID, 'tiferet.utils.middleware', 'LoggingMiddleware',
)

# ** constant: timing_middleware
TIMING_MIDDLEWARE = create_app_service_dependency(
    TIMING_MIDDLEWARE_ID, 'tiferet.utils.middleware', 'TimingMiddleware',
)

# ** constant: cache_middleware
CACHE_MIDDLEWARE = create_app_service_dependency(
    CACHE_MIDDLEWARE_ID, 'tiferet.utils.middleware', 'CacheMiddleware',
)

# ** constant: app_service
APP_SERVICE = create_app_service_dependency(
    APP_SERVICE_ID,
    create_service_module_path(TIFERET_REPOS_PATH, APP_DOMAIN_PATH),
    'AppConfigRepository',
)

# ** constant: add_feature_evt
ADD_FEATURE_EVT = create_app_service_dependency(
    ADD_FEATURE_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'AddFeature',
)

# ** constant: list_features_evt
LIST_FEATURES_EVT = create_app_service_dependency(
    LIST_FEATURES_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'ListFeatures',
)

# ** constant: remove_feature_evt
REMOVE_FEATURE_EVT = create_app_service_dependency(
    REMOVE_FEATURE_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'RemoveFeature',
)

# ** constant: update_feature_evt
UPDATE_FEATURE_EVT = create_app_service_dependency(
    UPDATE_FEATURE_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'UpdateFeature',
)

# ** constant: add_feature_step_evt
ADD_FEATURE_STEP_EVT = create_app_service_dependency(
    ADD_FEATURE_STEP_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'AddFeatureStep',
)

# ** constant: update_feature_step_evt
UPDATE_FEATURE_STEP_EVT = create_app_service_dependency(
    UPDATE_FEATURE_STEP_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'UpdateFeatureStep',
)

# ** constant: remove_feature_step_evt
REMOVE_FEATURE_STEP_EVT = create_app_service_dependency(
    REMOVE_FEATURE_STEP_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'RemoveFeatureStep',
)

# ** constant: reorder_feature_step_evt
REORDER_FEATURE_STEP_EVT = create_app_service_dependency(
    REORDER_FEATURE_STEP_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'ReorderFeatureStep',
)

# ** constant: add_error_evt
ADD_ERROR_EVT = create_app_service_dependency(
    ADD_ERROR_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, ERROR_DOMAIN_PATH),
    'AddError',
)

# ** constant: list_errors_evt
LIST_ERRORS_EVT = create_app_service_dependency(
    LIST_ERRORS_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, ERROR_DOMAIN_PATH),
    'ListErrors',
)

# ** constant: rename_error_evt
RENAME_ERROR_EVT = create_app_service_dependency(
    RENAME_ERROR_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, ERROR_DOMAIN_PATH),
    'RenameError',
)

# ** constant: set_error_message_evt
SET_ERROR_MESSAGE_EVT = create_app_service_dependency(
    SET_ERROR_MESSAGE_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, ERROR_DOMAIN_PATH),
    'SetErrorMessage',
)

# ** constant: remove_error_message_evt
REMOVE_ERROR_MESSAGE_EVT = create_app_service_dependency(
    REMOVE_ERROR_MESSAGE_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, ERROR_DOMAIN_PATH),
    'RemoveErrorMessage',
)

# ** constant: remove_error_evt
REMOVE_ERROR_EVT = create_app_service_dependency(
    REMOVE_ERROR_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, ERROR_DOMAIN_PATH),
    'RemoveError',
)

# ** constant: add_service_registration_evt
ADD_SERVICE_REGISTRATION_EVT = create_app_service_dependency(
    ADD_SERVICE_REGISTRATION_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, DI_DOMAIN_PATH),
    'AddServiceRegistration',
)

# ** constant: set_default_service_registration_evt
SET_DEFAULT_SERVICE_REGISTRATION_EVT = create_app_service_dependency(
    SET_DEFAULT_SERVICE_REGISTRATION_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, DI_DOMAIN_PATH),
    'SetDefaultServiceRegistration',
)

# ** constant: set_di_service_dependency_evt
SET_DI_SERVICE_DEPENDENCY_EVT = create_app_service_dependency(
    SET_DI_SERVICE_DEPENDENCY_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, DI_DOMAIN_PATH),
    'SetServiceDependency',
)

# ** constant: remove_di_service_dependency_evt
REMOVE_DI_SERVICE_DEPENDENCY_EVT = create_app_service_dependency(
    REMOVE_DI_SERVICE_DEPENDENCY_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, DI_DOMAIN_PATH),
    'RemoveServiceDependency',
)

# ** constant: remove_service_registration_evt
REMOVE_SERVICE_REGISTRATION_EVT = create_app_service_dependency(
    REMOVE_SERVICE_REGISTRATION_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, DI_DOMAIN_PATH),
    'RemoveServiceRegistration',
)

# ** constant: set_service_constants_evt
SET_SERVICE_CONSTANTS_EVT = create_app_service_dependency(
    SET_SERVICE_CONSTANTS_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, DI_DOMAIN_PATH),
    'SetServiceConstants',
)

# ** constant: add_app_session_evt
ADD_APP_SESSION_EVT = create_app_service_dependency(
    ADD_APP_SESSION_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, APP_DOMAIN_PATH),
    'AddAppSession',
)

# ** constant: get_app_session_evt
GET_APP_SESSION_EVT = create_app_service_dependency(
    GET_APP_SESSION_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, APP_DOMAIN_PATH),
    'GetAppSession',
)

# ** constant: update_app_session_evt
UPDATE_APP_SESSION_EVT = create_app_service_dependency(
    UPDATE_APP_SESSION_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, APP_DOMAIN_PATH),
    'UpdateAppSession',
)

# ** constant: set_app_constants_evt
SET_APP_CONSTANTS_EVT = create_app_service_dependency(
    SET_APP_CONSTANTS_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, APP_DOMAIN_PATH),
    'SetAppConstants',
)

# ** constant: list_app_sessions_evt
LIST_APP_SESSIONS_EVT = create_app_service_dependency(
    LIST_APP_SESSIONS_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, APP_DOMAIN_PATH),
    'ListAppSessions',
)

# ** constant: set_app_service_dependency_evt
SET_APP_SERVICE_DEPENDENCY_EVT = create_app_service_dependency(
    SET_APP_SERVICE_DEPENDENCY_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, APP_DOMAIN_PATH),
    'SetServiceDependency',
)

# ** constant: remove_app_service_dependency_evt
REMOVE_APP_SERVICE_DEPENDENCY_EVT = create_app_service_dependency(
    REMOVE_APP_SERVICE_DEPENDENCY_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, APP_DOMAIN_PATH),
    'RemoveServiceDependency',
)

# ** constant: remove_app_session_evt
REMOVE_APP_SESSION_EVT = create_app_service_dependency(
    REMOVE_APP_SESSION_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, APP_DOMAIN_PATH),
    'RemoveAppSession',
)

# ** constant: add_cli_command_evt
ADD_CLI_COMMAND_EVT = create_app_service_dependency(
    ADD_CLI_COMMAND_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, CLI_DOMAIN_PATH),
    'AddCliCommand',
)

# ** constant: add_cli_argument_evt
ADD_CLI_ARGUMENT_EVT = create_app_service_dependency(
    ADD_CLI_ARGUMENT_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, CLI_DOMAIN_PATH),
    'AddCliArgument',
)

# ** constant: add_formatter_evt
ADD_FORMATTER_EVT = create_app_service_dependency(
    ADD_FORMATTER_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, LOGGING_DOMAIN_PATH),
    'AddFormatter',
)

# ** constant: remove_formatter_evt
REMOVE_FORMATTER_EVT = create_app_service_dependency(
    REMOVE_FORMATTER_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, LOGGING_DOMAIN_PATH),
    'RemoveFormatter',
)

# ** constant: add_handler_evt
ADD_HANDLER_EVT = create_app_service_dependency(
    ADD_HANDLER_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, LOGGING_DOMAIN_PATH),
    'AddHandler',
)

# ** constant: remove_handler_evt
REMOVE_HANDLER_EVT = create_app_service_dependency(
    REMOVE_HANDLER_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, LOGGING_DOMAIN_PATH),
    'RemoveHandler',
)

# ** constant: add_logger_evt
ADD_LOGGER_EVT = create_app_service_dependency(
    ADD_LOGGER_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, LOGGING_DOMAIN_PATH),
    'AddLogger',
)

# ** constant: remove_logger_evt
REMOVE_LOGGER_EVT = create_app_service_dependency(
    REMOVE_LOGGER_EVT_ID,
    create_service_module_path(TIFERET_EVENTS_PATH, LOGGING_DOMAIN_PATH),
    'RemoveLogger',
)

# *** constants (groups)

# ** constant: core_default_services
CORE_DEFAULT_SERVICES = {
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
CORE_DEFAULT_CONSTANTS = {
    CLI_CONFIG_ID: DEFAULT_CONFIG_FILE,
    DI_CONFIG_ID: DEFAULT_CONFIG_FILE,
    ERROR_CONFIG_ID: DEFAULT_CONFIG_FILE,
    LOGGING_CONFIG_ID: DEFAULT_CONFIG_FILE,
    FEATURE_CONFIG_ID: DEFAULT_CONFIG_FILE,
}

# ** constant: default_admin_cli_services
DEFAULT_ADMIN_CLI_SERVICES = {
    APP_SERVICE_ID: APP_SERVICE,
    ADD_FEATURE_EVT_ID: ADD_FEATURE_EVT,
    LIST_FEATURES_EVT_ID: LIST_FEATURES_EVT,
    REMOVE_FEATURE_EVT_ID: REMOVE_FEATURE_EVT,
    UPDATE_FEATURE_EVT_ID: UPDATE_FEATURE_EVT,
    ADD_FEATURE_STEP_EVT_ID: ADD_FEATURE_STEP_EVT,
    UPDATE_FEATURE_STEP_EVT_ID: UPDATE_FEATURE_STEP_EVT,
    REMOVE_FEATURE_STEP_EVT_ID: REMOVE_FEATURE_STEP_EVT,
    REORDER_FEATURE_STEP_EVT_ID: REORDER_FEATURE_STEP_EVT,
    ADD_ERROR_EVT_ID: ADD_ERROR_EVT,
    LIST_ERRORS_EVT_ID: LIST_ERRORS_EVT,
    RENAME_ERROR_EVT_ID: RENAME_ERROR_EVT,
    SET_ERROR_MESSAGE_EVT_ID: SET_ERROR_MESSAGE_EVT,
    REMOVE_ERROR_MESSAGE_EVT_ID: REMOVE_ERROR_MESSAGE_EVT,
    REMOVE_ERROR_EVT_ID: REMOVE_ERROR_EVT,
    ADD_SERVICE_REGISTRATION_EVT_ID: ADD_SERVICE_REGISTRATION_EVT,
    SET_DEFAULT_SERVICE_REGISTRATION_EVT_ID: SET_DEFAULT_SERVICE_REGISTRATION_EVT,
    SET_DI_SERVICE_DEPENDENCY_EVT_ID: SET_DI_SERVICE_DEPENDENCY_EVT,
    REMOVE_DI_SERVICE_DEPENDENCY_EVT_ID: REMOVE_DI_SERVICE_DEPENDENCY_EVT,
    REMOVE_SERVICE_REGISTRATION_EVT_ID: REMOVE_SERVICE_REGISTRATION_EVT,
    SET_SERVICE_CONSTANTS_EVT_ID: SET_SERVICE_CONSTANTS_EVT,
    ADD_APP_SESSION_EVT_ID: ADD_APP_SESSION_EVT,
    GET_APP_SESSION_EVT_ID: GET_APP_SESSION_EVT,
    UPDATE_APP_SESSION_EVT_ID: UPDATE_APP_SESSION_EVT,
    SET_APP_CONSTANTS_EVT_ID: SET_APP_CONSTANTS_EVT,
    LIST_APP_SESSIONS_EVT_ID: LIST_APP_SESSIONS_EVT,
    SET_APP_SERVICE_DEPENDENCY_EVT_ID: SET_APP_SERVICE_DEPENDENCY_EVT,
    REMOVE_APP_SERVICE_DEPENDENCY_EVT_ID: REMOVE_APP_SERVICE_DEPENDENCY_EVT,
    REMOVE_APP_SESSION_EVT_ID: REMOVE_APP_SESSION_EVT,
    ADD_CLI_COMMAND_EVT_ID: ADD_CLI_COMMAND_EVT,
    ADD_CLI_ARGUMENT_EVT_ID: ADD_CLI_ARGUMENT_EVT,
    ADD_FORMATTER_EVT_ID: ADD_FORMATTER_EVT,
    REMOVE_FORMATTER_EVT_ID: REMOVE_FORMATTER_EVT,
    ADD_HANDLER_EVT_ID: ADD_HANDLER_EVT,
    REMOVE_HANDLER_EVT_ID: REMOVE_HANDLER_EVT,
    ADD_LOGGER_EVT_ID: ADD_LOGGER_EVT,
    REMOVE_LOGGER_EVT_ID: REMOVE_LOGGER_EVT,
}

# ** constant: admin_default_services
ADMIN_DEFAULT_SERVICES = {
    **CORE_DEFAULT_SERVICES,
    **DEFAULT_ADMIN_CLI_SERVICES,
}

# ** constant: admin_default_constants
# Core constants plus the app_config key that the admin layer exposes directly.
ADMIN_DEFAULT_CONSTANTS = {
    **CORE_DEFAULT_CONSTANTS,
    'app_config': DEFAULT_CONFIG_FILE,
}

# ** constant: core_default_app_sessions
# Built-in session definitions seeded into the cache by build_cache so the admin
# paths can resolve them without a config-file entry or a separate fallback.
CORE_DEFAULT_APP_SESSIONS = {
    TIFERET_ADMIN_ID: DEFAULT_ADMIN_APP_SESSION,
    TIFERET_ADMIN_CLI_ID: DEFAULT_ADMIN_CLI_SESSION,
}
