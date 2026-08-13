"""Tiferet DI Assets

Three-section catalog for the built-in Tiferet CLI service registrations.
Each section follows the pattern established by ``assets/error.py``:
- ``constants (ids)`` — 37 individually named service ID string constants.
- ``constants (services)`` — 37 individually named service registration
  dicts, each built via ``create_service_registration_data``.
- ``constants (groups)`` — the ``DEFAULT_ADMIN_SERVICES`` catalog dict
  keyed by ID constants.
"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from .core import (
    create_service_registration_data,
    create_service_module_path,
    TIFERET,
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

# *** constants (services)

# ** constant: app_service_data
APP_SERVICE_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_REPOS_PATH, APP_DOMAIN_PATH),
    'AppConfigRepository',
)

# ** constant: add_feature_evt_data
ADD_FEATURE_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'AddFeature',
)

# ** constant: list_features_evt_data
LIST_FEATURES_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'ListFeatures',
)

# ** constant: remove_feature_evt_data
REMOVE_FEATURE_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'RemoveFeature',
)

# ** constant: update_feature_evt_data
UPDATE_FEATURE_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'UpdateFeature',
)

# ** constant: add_feature_step_evt_data
ADD_FEATURE_STEP_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'AddFeatureStep',
)

# ** constant: update_feature_step_evt_data
UPDATE_FEATURE_STEP_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'UpdateFeatureStep',
)

# ** constant: remove_feature_step_evt_data
REMOVE_FEATURE_STEP_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'RemoveFeatureStep',
)

# ** constant: reorder_feature_step_evt_data
REORDER_FEATURE_STEP_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH),
    'ReorderFeatureStep',
)

# ** constant: add_error_evt_data
ADD_ERROR_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, ERROR_DOMAIN_PATH),
    'AddError',
)

# ** constant: list_errors_evt_data
LIST_ERRORS_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, ERROR_DOMAIN_PATH),
    'ListErrors',
)

# ** constant: rename_error_evt_data
RENAME_ERROR_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, ERROR_DOMAIN_PATH),
    'RenameError',
)

# ** constant: set_error_message_evt_data
SET_ERROR_MESSAGE_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, ERROR_DOMAIN_PATH),
    'SetErrorMessage',
)

# ** constant: remove_error_message_evt_data
REMOVE_ERROR_MESSAGE_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, ERROR_DOMAIN_PATH),
    'RemoveErrorMessage',
)

# ** constant: remove_error_evt_data
REMOVE_ERROR_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, ERROR_DOMAIN_PATH),
    'RemoveError',
)

# ** constant: add_service_registration_evt_data
ADD_SERVICE_REGISTRATION_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, DI_DOMAIN_PATH),
    'AddServiceRegistration',
)

# ** constant: set_default_service_registration_evt_data
SET_DEFAULT_SERVICE_REGISTRATION_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, DI_DOMAIN_PATH),
    'SetDefaultServiceRegistration',
)

# ** constant: set_di_service_dependency_evt_data
SET_DI_SERVICE_DEPENDENCY_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, DI_DOMAIN_PATH),
    'SetServiceDependency',
)

# ** constant: remove_di_service_dependency_evt_data
REMOVE_DI_SERVICE_DEPENDENCY_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, DI_DOMAIN_PATH),
    'RemoveServiceDependency',
)

# ** constant: remove_service_registration_evt_data
REMOVE_SERVICE_REGISTRATION_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, DI_DOMAIN_PATH),
    'RemoveServiceRegistration',
)

# ** constant: set_service_constants_evt_data
SET_SERVICE_CONSTANTS_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, DI_DOMAIN_PATH),
    'SetServiceConstants',
)

# ** constant: add_app_session_evt_data
ADD_APP_SESSION_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, APP_DOMAIN_PATH),
    'AddAppSession',
)

# ** constant: get_app_session_evt_data
GET_APP_SESSION_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, APP_DOMAIN_PATH),
    'GetAppSession',
)

# ** constant: update_app_session_evt_data
UPDATE_APP_SESSION_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, APP_DOMAIN_PATH),
    'UpdateAppSession',
)

# ** constant: set_app_constants_evt_data
SET_APP_CONSTANTS_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, APP_DOMAIN_PATH),
    'SetAppConstants',
)

# ** constant: list_app_sessions_evt_data
LIST_APP_SESSIONS_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, APP_DOMAIN_PATH),
    'ListAppSessions',
)

# ** constant: set_app_service_dependency_evt_data
SET_APP_SERVICE_DEPENDENCY_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, APP_DOMAIN_PATH),
    'SetServiceDependency',
)

# ** constant: remove_app_service_dependency_evt_data
REMOVE_APP_SERVICE_DEPENDENCY_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, APP_DOMAIN_PATH),
    'RemoveServiceDependency',
)

# ** constant: remove_app_session_evt_data
REMOVE_APP_SESSION_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, APP_DOMAIN_PATH),
    'RemoveAppSession',
)

# ** constant: add_cli_command_evt_data
ADD_CLI_COMMAND_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, CLI_DOMAIN_PATH),
    'AddCliCommand',
)

# ** constant: add_cli_argument_evt_data
ADD_CLI_ARGUMENT_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, CLI_DOMAIN_PATH),
    'AddCliArgument',
)

# ** constant: add_formatter_evt_data
ADD_FORMATTER_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, LOGGING_DOMAIN_PATH),
    'AddFormatter',
)

# ** constant: remove_formatter_evt_data
REMOVE_FORMATTER_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, LOGGING_DOMAIN_PATH),
    'RemoveFormatter',
)

# ** constant: add_handler_evt_data
ADD_HANDLER_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, LOGGING_DOMAIN_PATH),
    'AddHandler',
)

# ** constant: remove_handler_evt_data
REMOVE_HANDLER_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, LOGGING_DOMAIN_PATH),
    'RemoveHandler',
)

# ** constant: add_logger_evt_data
ADD_LOGGER_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, LOGGING_DOMAIN_PATH),
    'AddLogger',
)

# ** constant: remove_logger_evt_data
REMOVE_LOGGER_EVT_DATA = create_service_registration_data(
    create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, LOGGING_DOMAIN_PATH),
    'RemoveLogger',
)

# *** constants (groups)

# ** constant: default_admin_services
DEFAULT_ADMIN_SERVICES: Dict[str, Dict] = {
    APP_SERVICE_ID: APP_SERVICE_DATA,
    ADD_FEATURE_EVT_ID: ADD_FEATURE_EVT_DATA,
    LIST_FEATURES_EVT_ID: LIST_FEATURES_EVT_DATA,
    REMOVE_FEATURE_EVT_ID: REMOVE_FEATURE_EVT_DATA,
    UPDATE_FEATURE_EVT_ID: UPDATE_FEATURE_EVT_DATA,
    ADD_FEATURE_STEP_EVT_ID: ADD_FEATURE_STEP_EVT_DATA,
    UPDATE_FEATURE_STEP_EVT_ID: UPDATE_FEATURE_STEP_EVT_DATA,
    REMOVE_FEATURE_STEP_EVT_ID: REMOVE_FEATURE_STEP_EVT_DATA,
    REORDER_FEATURE_STEP_EVT_ID: REORDER_FEATURE_STEP_EVT_DATA,
    ADD_ERROR_EVT_ID: ADD_ERROR_EVT_DATA,
    LIST_ERRORS_EVT_ID: LIST_ERRORS_EVT_DATA,
    RENAME_ERROR_EVT_ID: RENAME_ERROR_EVT_DATA,
    SET_ERROR_MESSAGE_EVT_ID: SET_ERROR_MESSAGE_EVT_DATA,
    REMOVE_ERROR_MESSAGE_EVT_ID: REMOVE_ERROR_MESSAGE_EVT_DATA,
    REMOVE_ERROR_EVT_ID: REMOVE_ERROR_EVT_DATA,
    ADD_SERVICE_REGISTRATION_EVT_ID: ADD_SERVICE_REGISTRATION_EVT_DATA,
    SET_DEFAULT_SERVICE_REGISTRATION_EVT_ID: SET_DEFAULT_SERVICE_REGISTRATION_EVT_DATA,
    SET_DI_SERVICE_DEPENDENCY_EVT_ID: SET_DI_SERVICE_DEPENDENCY_EVT_DATA,
    REMOVE_DI_SERVICE_DEPENDENCY_EVT_ID: REMOVE_DI_SERVICE_DEPENDENCY_EVT_DATA,
    REMOVE_SERVICE_REGISTRATION_EVT_ID: REMOVE_SERVICE_REGISTRATION_EVT_DATA,
    SET_SERVICE_CONSTANTS_EVT_ID: SET_SERVICE_CONSTANTS_EVT_DATA,
    ADD_APP_SESSION_EVT_ID: ADD_APP_SESSION_EVT_DATA,
    GET_APP_SESSION_EVT_ID: GET_APP_SESSION_EVT_DATA,
    UPDATE_APP_SESSION_EVT_ID: UPDATE_APP_SESSION_EVT_DATA,
    SET_APP_CONSTANTS_EVT_ID: SET_APP_CONSTANTS_EVT_DATA,
    LIST_APP_SESSIONS_EVT_ID: LIST_APP_SESSIONS_EVT_DATA,
    SET_APP_SERVICE_DEPENDENCY_EVT_ID: SET_APP_SERVICE_DEPENDENCY_EVT_DATA,
    REMOVE_APP_SERVICE_DEPENDENCY_EVT_ID: REMOVE_APP_SERVICE_DEPENDENCY_EVT_DATA,
    REMOVE_APP_SESSION_EVT_ID: REMOVE_APP_SESSION_EVT_DATA,
    ADD_CLI_COMMAND_EVT_ID: ADD_CLI_COMMAND_EVT_DATA,
    ADD_CLI_ARGUMENT_EVT_ID: ADD_CLI_ARGUMENT_EVT_DATA,
    ADD_FORMATTER_EVT_ID: ADD_FORMATTER_EVT_DATA,
    REMOVE_FORMATTER_EVT_ID: REMOVE_FORMATTER_EVT_DATA,
    ADD_HANDLER_EVT_ID: ADD_HANDLER_EVT_DATA,
    REMOVE_HANDLER_EVT_ID: REMOVE_HANDLER_EVT_DATA,
    ADD_LOGGER_EVT_ID: ADD_LOGGER_EVT_DATA,
    REMOVE_LOGGER_EVT_ID: REMOVE_LOGGER_EVT_DATA,
}
