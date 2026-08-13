"""Tiferet Assets Error

Default error catalog mapping each error-code constant to its name and
multilingual message templates, consumed by ErrorContext and the error
domain events when not overridden by consumer configuration.
"""

# *** imports

# ** app
from .core import EN_US, create_default_error

# *** constants (ids)

# ** constant: app_config_loading_failed_id
APP_CONFIG_LOADING_FAILED_ID = 'APP_CONFIG_LOADING_FAILED'

# ** constant: app_error_id
APP_ERROR_ID = 'APP_ERROR'

# ** constant: app_repository_import_failed_id
APP_REPOSITORY_IMPORT_FAILED_ID = 'APP_REPOSITORY_IMPORT_FAILED'

# ** constant: app_service_import_failed_id
APP_SERVICE_IMPORT_FAILED_ID = 'APP_SERVICE_IMPORT_FAILED'

# ** constant: app_service_not_loaded_id
APP_SERVICE_NOT_LOADED_ID = 'APP_SERVICE_NOT_LOADED'

# ** constant: app_session_not_found_id
APP_SESSION_NOT_FOUND_ID = 'APP_SESSION_NOT_FOUND'

# ** constant: attribute_already_exists_id
ATTRIBUTE_ALREADY_EXISTS_ID = 'ATTRIBUTE_ALREADY_EXISTS'

# ** constant: command_parameter_required_id
COMMAND_PARAMETER_REQUIRED_ID = 'COMMAND_PARAMETER_REQUIRED'

# ** constant: config_file_not_found_id
CONFIG_FILE_NOT_FOUND_ID = 'CONFIG_FILE_NOT_FOUND'

# ** constant: container_config_loading_failed_id
CONTAINER_CONFIG_LOADING_FAILED_ID = 'CONTAINER_CONFIG_LOADING_FAILED'

# ** constant: context_not_found_id
CONTEXT_NOT_FOUND_ID = 'CONTEXT_NOT_FOUND'

# ** constant: dependency_type_not_found_id
DEPENDENCY_TYPE_NOT_FOUND_ID = 'DEPENDENCY_TYPE_NOT_FOUND'

# ** constant: di_service_not_configured_id
DI_SERVICE_NOT_CONFIGURED_ID = 'DI_SERVICE_NOT_CONFIGURED'

# ** constant: error_config_loading_failed_id
ERROR_CONFIG_LOADING_FAILED_ID = 'ERROR_CONFIG_LOADING_FAILED'

# ** constant: error_not_found_id
ERROR_NOT_FOUND_ID = 'ERROR_NOT_FOUND'

# ** constant: feature_config_loading_failed_id
FEATURE_CONFIG_LOADING_FAILED_ID = 'FEATURE_CONFIG_LOADING_FAILED'

# ** constant: feature_not_found_id
FEATURE_NOT_FOUND_ID = 'FEATURE_NOT_FOUND'

# ** constant: feature_step_loading_failed_id
FEATURE_STEP_LOADING_FAILED_ID = 'FEATURE_STEP_LOADING_FAILED'

# ** constant: import_dependency_failed_id
IMPORT_DEPENDENCY_FAILED_ID = 'IMPORT_DEPENDENCY_FAILED'

# ** constant: invalid_app_session_type_id
INVALID_APP_SESSION_TYPE_ID = 'INVALID_APP_SESSION_TYPE'

# ** constant: invalid_dependency_error_id
INVALID_DEPENDENCY_ERROR_ID = 'INVALID_DEPENDENCY_ERROR'

# ** constant: invalid_json_file_id
INVALID_JSON_FILE_ID = 'INVALID_JSON_FILE'

# ** constant: invalid_yaml_file_id
INVALID_YAML_FILE_ID = 'INVALID_YAML_FILE'

# ** constant: logger_creation_failed_id
LOGGER_CREATION_FAILED_ID = 'LOGGER_CREATION_FAILED'

# ** constant: logging_config_failed_id
LOGGING_CONFIG_FAILED_ID = 'LOGGING_CONFIG_FAILED'

# ** constant: middleware_loading_failed_id
MIDDLEWARE_LOADING_FAILED_ID = 'MIDDLEWARE_LOADING_FAILED'

# ** constant: parameter_not_found_id
PARAMETER_NOT_FOUND_ID = 'PARAMETER_NOT_FOUND'

# ** constant: parameter_parsing_failed_id
PARAMETER_PARSING_FAILED_ID = 'PARAMETER_PARSING_FAILED'

# ** constant: request_not_found_id
REQUEST_NOT_FOUND_ID = 'REQUEST_NOT_FOUND'

# ** constant: request_validation_failed_id
REQUEST_VALIDATION_FAILED_ID = 'REQUEST_VALIDATION_FAILED'

# *** constants (ids_admin)

# ** constant: cli_command_already_exists_id
CLI_COMMAND_ALREADY_EXISTS_ID = 'CLI_COMMAND_ALREADY_EXISTS'

# ** constant: cli_command_not_found_id
CLI_COMMAND_NOT_FOUND_ID = 'CLI_COMMAND_NOT_FOUND'

# ** constant: cli_config_loading_failed_id
CLI_CONFIG_LOADING_FAILED_ID = 'CLI_CONFIG_LOADING_FAILED'

# ** constant: error_already_exists_id
ERROR_ALREADY_EXISTS_ID = 'ERROR_ALREADY_EXISTS'

# ** constant: feature_already_exists_id
FEATURE_ALREADY_EXISTS_ID = 'FEATURE_ALREADY_EXISTS'

# ** constant: feature_command_not_found_id
FEATURE_COMMAND_NOT_FOUND_ID = 'FEATURE_COMMAND_NOT_FOUND'

# ** constant: feature_name_required_id
FEATURE_NAME_REQUIRED_ID = 'FEATURE_NAME_REQUIRED'

# ** constant: invalid_feature_attribute_id
INVALID_FEATURE_ATTRIBUTE_ID = 'INVALID_FEATURE_ATTRIBUTE'

# ** constant: invalid_feature_command_attribute_id
INVALID_FEATURE_COMMAND_ATTRIBUTE_ID = 'INVALID_FEATURE_COMMAND_ATTRIBUTE'

# ** constant: invalid_flagged_dependency_id
INVALID_FLAGGED_DEPENDENCY_ID = 'INVALID_FLAGGED_DEPENDENCY'

# ** constant: invalid_service_registration_id
INVALID_SERVICE_REGISTRATION_ID = 'INVALID_SERVICE_REGISTRATION'

# ** constant: no_error_messages_id
NO_ERROR_MESSAGES_ID = 'NO_ERROR_MESSAGES'

# ** constant: service_registration_already_exists_id
SERVICE_REGISTRATION_ALREADY_EXISTS_ID = 'SERVICE_REGISTRATION_ALREADY_EXISTS'

# ** constant: service_registration_not_found_id
SERVICE_REGISTRATION_NOT_FOUND_ID = 'SERVICE_REGISTRATION_NOT_FOUND'

# *** constants (ids_sqlite)

# Legacy constants — present on main pending rename or retirement in later parity stories.

# ** constant: sqlite_file_not_found_or_readonly_id
SQLITE_FILE_NOT_FOUND_OR_READONLY_ID = 'SQLITE_FILE_NOT_FOUND_OR_READONLY'

# *** constants (ids_csv)

# ** constant: csv_dict_no_header_id
CSV_DICT_NO_HEADER_ID = 'CSV_DICT_NO_HEADER'

# ** constant: csv_handle_not_initialized_id
CSV_HANDLE_NOT_INITIALIZED_ID = 'CSV_HANDLE_NOT_INITIALIZED'

# ** constant: csv_invalid_mode_id
CSV_INVALID_MODE_ID = 'CSV_INVALID_MODE'

# *** constants (models)

# ** constant: app_config_loading_failed
APP_CONFIG_LOADING_FAILED = create_default_error(
    APP_CONFIG_LOADING_FAILED_ID,
    'App Configuration Loading Failed',
    [(EN_US, 'Unable to load app configuration file {file_path}: {exception}.')],
)

# ** constant: app_error
APP_ERROR = create_default_error(
    APP_ERROR_ID,
    'App Error',
    [(EN_US, 'An error occurred in the app: {error_message}.')],
)

# ** constant: app_repository_import_failed
APP_REPOSITORY_IMPORT_FAILED = create_default_error(
    APP_REPOSITORY_IMPORT_FAILED_ID,
    'App Repository Import Failed',
    [(EN_US, 'Failed to import app repository: {exception}.')],
)

# ** constant: app_service_import_failed
APP_SERVICE_IMPORT_FAILED = create_default_error(
    APP_SERVICE_IMPORT_FAILED_ID,
    'App Service Import Failed',
    [(EN_US, 'Failed to import app service dependencies: {exception}.')],
)

# ** constant: app_service_not_loaded
APP_SERVICE_NOT_LOADED = create_default_error(
    APP_SERVICE_NOT_LOADED_ID,
    'App Service Not Loaded',
    [(EN_US, 'App service must be loaded before loading interface {interface_id}.')],
)

# ** constant: app_session_not_found
APP_SESSION_NOT_FOUND = create_default_error(
    APP_SESSION_NOT_FOUND_ID,
    'App Session Not Found',
    [(EN_US, 'App session with ID {interface_id} not found.')],
)

# ** constant: attribute_already_exists
ATTRIBUTE_ALREADY_EXISTS = create_default_error(
    ATTRIBUTE_ALREADY_EXISTS_ID,
    'Attribute Already Exists',
    [(EN_US, 'A container attribute with ID {id} already exists.')],
)

# ** constant: command_parameter_required
COMMAND_PARAMETER_REQUIRED = create_default_error(
    COMMAND_PARAMETER_REQUIRED_ID,
    'Command Parameter Required',
    [(EN_US, 'The required parameter {parameter} for command {command} is missing.')],
)

# ** constant: config_file_not_found
CONFIG_FILE_NOT_FOUND = create_default_error(
    CONFIG_FILE_NOT_FOUND_ID,
    'Configuration File Not Found',
    [(EN_US, 'Configuration file {file_path} not found.')],
)

# ** constant: container_config_loading_failed
CONTAINER_CONFIG_LOADING_FAILED = create_default_error(
    CONTAINER_CONFIG_LOADING_FAILED_ID,
    'Container Configuration Loading Failed',
    [(EN_US, 'Unable to load container configuration file {file_path}: {exception}.')],
)

# ** constant: context_not_found
CONTEXT_NOT_FOUND = create_default_error(
    CONTEXT_NOT_FOUND_ID,
    'Context Not Found',
    [(EN_US, 'No context registered for domain type: {domain_type}.')],
)

# ** constant: dependency_type_not_found
DEPENDENCY_TYPE_NOT_FOUND = create_default_error(
    DEPENDENCY_TYPE_NOT_FOUND_ID,
    'Dependency Type Not Found',
    [(EN_US, 'No dependency type found for service configuration {configuration_id} with flags {flags}.')],
)

# ** constant: di_service_not_configured
DI_SERVICE_NOT_CONFIGURED = create_default_error(
    DI_SERVICE_NOT_CONFIGURED_ID,
    'DI Service Not Configured',
    [(EN_US, 'No di_service dependency is configured for interface {interface_id}.')],
)

# ** constant: error_config_loading_failed
ERROR_CONFIG_LOADING_FAILED = create_default_error(
    ERROR_CONFIG_LOADING_FAILED_ID,
    'Error Configuration Loading Failed',
    [(EN_US, 'Unable to load error configuration file {file_path}: {exception}.')],
)

# ** constant: error_not_found
ERROR_NOT_FOUND = create_default_error(
    ERROR_NOT_FOUND_ID,
    'Error Not Found',
    [(EN_US, 'Error not found: {id}.')],
)

# ** constant: feature_config_loading_failed
FEATURE_CONFIG_LOADING_FAILED = create_default_error(
    FEATURE_CONFIG_LOADING_FAILED_ID,
    'Feature Configuration Loading Failed',
    [(EN_US, 'Unable to load feature configuration file {file_path}: {exception}.')],
)

# ** constant: feature_not_found
FEATURE_NOT_FOUND = create_default_error(
    FEATURE_NOT_FOUND_ID,
    'Feature Not Found',
    [(EN_US, 'Feature not found: {feature_id}.')],
)

# ** constant: feature_step_loading_failed
FEATURE_STEP_LOADING_FAILED = create_default_error(
    FEATURE_STEP_LOADING_FAILED_ID,
    'Feature Step Loading Failed',
    [(EN_US, 'Failed to load feature step: {service_id}. Error: {exception}.')],
)

# ** constant: import_dependency_failed
IMPORT_DEPENDENCY_FAILED = create_default_error(
    IMPORT_DEPENDENCY_FAILED_ID,
    'Import Dependency Failed',
    [(EN_US, 'Failed to import {class_name} from {module_path}. Error: {exception}.')],
)

# ** constant: invalid_app_session_type
INVALID_APP_SESSION_TYPE = create_default_error(
    INVALID_APP_SESSION_TYPE_ID,
    'Invalid App Session Type',
    [(EN_US, 'App context for interface is not valid: {interface_id}.')],
)

# ** constant: invalid_dependency_error
INVALID_DEPENDENCY_ERROR = create_default_error(
    INVALID_DEPENDENCY_ERROR_ID,
    'Invalid Dependency Error',
    [(EN_US, 'Dependency {dependency} could not be resolved: {reason}.')],
)

# ** constant: invalid_json_file
INVALID_JSON_FILE = create_default_error(
    INVALID_JSON_FILE_ID,
    'Invalid JSON File',
    [(EN_US, 'File is not a valid JSON file: {path}.')],
)

# ** constant: invalid_yaml_file
INVALID_YAML_FILE = create_default_error(
    INVALID_YAML_FILE_ID,
    'Invalid YAML File',
    [(EN_US, 'File is not a valid YAML file: {path}.')],
)

# ** constant: logger_creation_failed
LOGGER_CREATION_FAILED = create_default_error(
    LOGGER_CREATION_FAILED_ID,
    'Logger Creation Failed',
    [(EN_US, 'Failed to create logger with ID {logger_id}: {exception}.')],
)

# ** constant: logging_config_failed
LOGGING_CONFIG_FAILED = create_default_error(
    LOGGING_CONFIG_FAILED_ID,
    'Logging Configuration Failed',
    [(EN_US, 'Failed to configure logging: {exception}.')],
)

# ** constant: middleware_loading_failed
MIDDLEWARE_LOADING_FAILED = create_default_error(
    MIDDLEWARE_LOADING_FAILED_ID,
    'Middleware Loading Failed',
    [(EN_US, 'Failed to load middleware: {service_id}. Error: {exception}.')],
)

# ** constant: parameter_not_found
PARAMETER_NOT_FOUND = create_default_error(
    PARAMETER_NOT_FOUND_ID,
    'Parameter Not Found',
    [(EN_US, 'Parameter {parameter} not found in request data.')],
)

# ** constant: parameter_parsing_failed
PARAMETER_PARSING_FAILED = create_default_error(
    PARAMETER_PARSING_FAILED_ID,
    'Parameter Parsing Failed',
    [(EN_US, 'Failed to parse parameter: {parameter}. Error: {exception}.')],
)

# ** constant: request_not_found
REQUEST_NOT_FOUND = create_default_error(
    REQUEST_NOT_FOUND_ID,
    'Request Not Found',
    [(EN_US, 'Request data is not available for parameter parsing.')],
)

# ** constant: request_validation_failed
REQUEST_VALIDATION_FAILED = create_default_error(
    REQUEST_VALIDATION_FAILED_ID,
    'Request Validation Failed',
    [(EN_US, 'Request validation failed for feature {feature_id}: {violations}.')],
)

# *** constants (models_admin)

# ** constant: cli_command_already_exists
CLI_COMMAND_ALREADY_EXISTS = create_default_error(
    CLI_COMMAND_ALREADY_EXISTS_ID,
    'CLI Command Already Exists',
    [(EN_US, 'CLI command with ID {id} already exists.')],
)

# ** constant: cli_command_not_found
CLI_COMMAND_NOT_FOUND = create_default_error(
    CLI_COMMAND_NOT_FOUND_ID,
    'CLI Command Not Found',
    [(EN_US, 'CLI command {command_id} not found.')],
)

# ** constant: cli_config_loading_failed
CLI_CONFIG_LOADING_FAILED = create_default_error(
    CLI_CONFIG_LOADING_FAILED_ID,
    'CLI Configuration Loading Failed',
    [(EN_US, 'Unable to load CLI configuration file {file_path}: {exception}.')],
)

# ** constant: error_already_exists
ERROR_ALREADY_EXISTS = create_default_error(
    ERROR_ALREADY_EXISTS_ID,
    'Error Already Exists',
    [(EN_US, 'An error with ID {id} already exists.')],
)

# ** constant: feature_already_exists
FEATURE_ALREADY_EXISTS = create_default_error(
    FEATURE_ALREADY_EXISTS_ID,
    'Feature Already Exists',
    [(EN_US, 'Feature with ID {id} already exists.')],
)

# ** constant: feature_command_not_found
FEATURE_COMMAND_NOT_FOUND = create_default_error(
    FEATURE_COMMAND_NOT_FOUND_ID,
    'Feature Command Not Found',
    [(EN_US, 'Feature command not found for feature {feature_id} at position {position}.')],
)

# ** constant: feature_name_required
FEATURE_NAME_REQUIRED = create_default_error(
    FEATURE_NAME_REQUIRED_ID,
    'Feature Name Required',
    [(EN_US, 'A feature name is required when updating the name attribute.')],
)

# ** constant: invalid_feature_attribute
INVALID_FEATURE_ATTRIBUTE = create_default_error(
    INVALID_FEATURE_ATTRIBUTE_ID,
    'Invalid Feature Attribute',
    [(EN_US, 'Invalid feature attribute: {attribute}. Supported attributes are name and description.')],
)

# ** constant: invalid_feature_command_attribute
INVALID_FEATURE_COMMAND_ATTRIBUTE = create_default_error(
    INVALID_FEATURE_COMMAND_ATTRIBUTE_ID,
    'Invalid Feature Command Attribute',
    [(EN_US,
      'Invalid feature command attribute: {attribute}. Supported attributes are '
      'name, attribute_id, data_key, pass_on_error, and parameters.')],
)

# ** constant: invalid_flagged_dependency
INVALID_FLAGGED_DEPENDENCY = create_default_error(
    INVALID_FLAGGED_DEPENDENCY_ID,
    'Invalid Flagged Dependency',
    [(EN_US, 'A flagged dependency must define both module_path and class_name.')],
)

# ** constant: invalid_service_registration
INVALID_SERVICE_REGISTRATION = create_default_error(
    INVALID_SERVICE_REGISTRATION_ID,
    'Invalid Service Registration',
    [(EN_US,
      'A service registration must define either a default type '
      '(module_path/class_name) or at least one flagged dependency.')],
)

# ** constant: no_error_messages
NO_ERROR_MESSAGES = create_default_error(
    NO_ERROR_MESSAGES_ID,
    'No Error Messages',
    [(EN_US, 'No error messages are defined for error ID {id}.')],
)

# ** constant: service_registration_already_exists
SERVICE_REGISTRATION_ALREADY_EXISTS = create_default_error(
    SERVICE_REGISTRATION_ALREADY_EXISTS_ID,
    'Service Registration Already Exists',
    [(EN_US, 'A service registration with ID {id} already exists.')],
)

# ** constant: service_registration_not_found
SERVICE_REGISTRATION_NOT_FOUND = create_default_error(
    SERVICE_REGISTRATION_NOT_FOUND_ID,
    'Service Registration Not Found',
    [(EN_US, 'Service registration with ID {id} not found.')],
)

# *** constants (models_sqlite)

# ** constant: sqlite_file_not_found_or_readonly
SQLITE_FILE_NOT_FOUND_OR_READONLY = create_default_error(
    SQLITE_FILE_NOT_FOUND_OR_READONLY_ID,
    'SQLite File Not Found or Read-Only',
    [(EN_US,
      'Unable to open SQLite database at {path}: {original_error}. '
      'Check path exists and is writable (use mode=rwc to create).')],
)

# *** constants (models_csv)

# ** constant: csv_dict_no_header
CSV_DICT_NO_HEADER = create_default_error(
    CSV_DICT_NO_HEADER_ID,
    'CSV Dict Reader Without Header',
    [(EN_US, 'Dict reader expects header row; file appears to lack one or was not read correctly.')],
)

# ** constant: csv_handle_not_initialized
CSV_HANDLE_NOT_INITIALIZED = create_default_error(
    CSV_HANDLE_NOT_INITIALIZED_ID,
    'CSV Handle Not Initialized',
    [(EN_US, 'CSV file must be opened before reading/writing.')],
)

# ** constant: csv_invalid_mode
CSV_INVALID_MODE = create_default_error(
    CSV_INVALID_MODE_ID,
    'Invalid CSV Mode',
    [(EN_US, 'Invalid file mode for CSV operation: {mode}. Expected r, w, a, etc.')],
)

# *** constants (groups)

# ** constant: core_default_errors
CORE_DEFAULT_ERRORS = {
    APP_CONFIG_LOADING_FAILED_ID: APP_CONFIG_LOADING_FAILED,
    APP_ERROR_ID: APP_ERROR,
    APP_REPOSITORY_IMPORT_FAILED_ID: APP_REPOSITORY_IMPORT_FAILED,
    APP_SERVICE_IMPORT_FAILED_ID: APP_SERVICE_IMPORT_FAILED,
    APP_SERVICE_NOT_LOADED_ID: APP_SERVICE_NOT_LOADED,
    APP_SESSION_NOT_FOUND_ID: APP_SESSION_NOT_FOUND,
    ATTRIBUTE_ALREADY_EXISTS_ID: ATTRIBUTE_ALREADY_EXISTS,
    COMMAND_PARAMETER_REQUIRED_ID: COMMAND_PARAMETER_REQUIRED,
    CONFIG_FILE_NOT_FOUND_ID: CONFIG_FILE_NOT_FOUND,
    CONTAINER_CONFIG_LOADING_FAILED_ID: CONTAINER_CONFIG_LOADING_FAILED,
    CONTEXT_NOT_FOUND_ID: CONTEXT_NOT_FOUND,
    DEPENDENCY_TYPE_NOT_FOUND_ID: DEPENDENCY_TYPE_NOT_FOUND,
    DI_SERVICE_NOT_CONFIGURED_ID: DI_SERVICE_NOT_CONFIGURED,
    ERROR_CONFIG_LOADING_FAILED_ID: ERROR_CONFIG_LOADING_FAILED,
    ERROR_NOT_FOUND_ID: ERROR_NOT_FOUND,
    FEATURE_CONFIG_LOADING_FAILED_ID: FEATURE_CONFIG_LOADING_FAILED,
    FEATURE_NOT_FOUND_ID: FEATURE_NOT_FOUND,
    FEATURE_STEP_LOADING_FAILED_ID: FEATURE_STEP_LOADING_FAILED,
    IMPORT_DEPENDENCY_FAILED_ID: IMPORT_DEPENDENCY_FAILED,
    INVALID_APP_SESSION_TYPE_ID: INVALID_APP_SESSION_TYPE,
    INVALID_DEPENDENCY_ERROR_ID: INVALID_DEPENDENCY_ERROR,
    INVALID_JSON_FILE_ID: INVALID_JSON_FILE,
    INVALID_YAML_FILE_ID: INVALID_YAML_FILE,
    LOGGER_CREATION_FAILED_ID: LOGGER_CREATION_FAILED,
    LOGGING_CONFIG_FAILED_ID: LOGGING_CONFIG_FAILED,
    MIDDLEWARE_LOADING_FAILED_ID: MIDDLEWARE_LOADING_FAILED,
    PARAMETER_NOT_FOUND_ID: PARAMETER_NOT_FOUND,
    PARAMETER_PARSING_FAILED_ID: PARAMETER_PARSING_FAILED,
    REQUEST_NOT_FOUND_ID: REQUEST_NOT_FOUND,
    REQUEST_VALIDATION_FAILED_ID: REQUEST_VALIDATION_FAILED,
}

# ** constant: admin_default_errors
ADMIN_DEFAULT_ERRORS = {
    **CORE_DEFAULT_ERRORS,
    CLI_COMMAND_ALREADY_EXISTS_ID: CLI_COMMAND_ALREADY_EXISTS,
    CLI_COMMAND_NOT_FOUND_ID: CLI_COMMAND_NOT_FOUND,
    CLI_CONFIG_LOADING_FAILED_ID: CLI_CONFIG_LOADING_FAILED,
    ERROR_ALREADY_EXISTS_ID: ERROR_ALREADY_EXISTS,
    FEATURE_ALREADY_EXISTS_ID: FEATURE_ALREADY_EXISTS,
    FEATURE_COMMAND_NOT_FOUND_ID: FEATURE_COMMAND_NOT_FOUND,
    FEATURE_NAME_REQUIRED_ID: FEATURE_NAME_REQUIRED,
    INVALID_FEATURE_ATTRIBUTE_ID: INVALID_FEATURE_ATTRIBUTE,
    INVALID_FEATURE_COMMAND_ATTRIBUTE_ID: INVALID_FEATURE_COMMAND_ATTRIBUTE,
    INVALID_FLAGGED_DEPENDENCY_ID: INVALID_FLAGGED_DEPENDENCY,
    INVALID_SERVICE_REGISTRATION_ID: INVALID_SERVICE_REGISTRATION,
    NO_ERROR_MESSAGES_ID: NO_ERROR_MESSAGES,
    SERVICE_REGISTRATION_ALREADY_EXISTS_ID: SERVICE_REGISTRATION_ALREADY_EXISTS,
    SERVICE_REGISTRATION_NOT_FOUND_ID: SERVICE_REGISTRATION_NOT_FOUND,
}

# ** constant: sqlite_default_errors
SQLITE_DEFAULT_ERRORS = {
    SQLITE_FILE_NOT_FOUND_OR_READONLY_ID: SQLITE_FILE_NOT_FOUND_OR_READONLY,
}

# ** constant: toml_default_errors
TOML_DEFAULT_ERRORS = {}

# ** constant: csv_default_errors
CSV_DEFAULT_ERRORS = {
    CSV_DICT_NO_HEADER_ID: CSV_DICT_NO_HEADER,
    CSV_HANDLE_NOT_INITIALIZED_ID: CSV_HANDLE_NOT_INITIALIZED,
    CSV_INVALID_MODE_ID: CSV_INVALID_MODE,
}

# ** constant: default_errors
DEFAULT_ERRORS = {
    **CORE_DEFAULT_ERRORS,
    **ADMIN_DEFAULT_ERRORS,
    **SQLITE_DEFAULT_ERRORS,
    **TOML_DEFAULT_ERRORS,
    **CSV_DEFAULT_ERRORS,
}
