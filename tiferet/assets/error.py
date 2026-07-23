"""Tiferet Error Catalog (Assets)

Default error catalog mapping each error-code constant to its name and
multilingual message templates, consumed by ErrorContext and the error
domain events when not overridden by consumer configuration.
"""

# *** imports

# ** app
from .core import (
    APP_CONFIG_LOADING_FAILED_ID,
    APP_ERROR_ID,
    APP_INTERFACE_NOT_FOUND_ID,
    APP_REPOSITORY_IMPORT_FAILED_ID,
    APP_SERVICE_IMPORT_FAILED_ID,
    APP_SERVICE_NOT_LOADED_ID,
    APP_SESSION_NOT_FOUND_ID,
    ATTRIBUTE_ALREADY_EXISTS_ID,
    CLI_COMMAND_ALREADY_EXISTS_ID,
    CLI_COMMAND_NOT_FOUND_ID,
    CLI_CONFIG_LOADING_FAILED_ID,
    COMMAND_PARAMETER_REQUIRED_ID,
    CONFIG_FILE_NOT_FOUND_ID,
    CONTAINER_CONFIG_LOADING_FAILED_ID,
    CONTEXT_NOT_FOUND_ID,
    CSV_DICT_NO_HEADER_ID,
    CSV_FIELDNAMES_REQUIRED_ID,
    CSV_HANDLE_NOT_INITIALIZED_ID,
    CSV_INVALID_MODE_ID,
    CSV_INVALID_READ_MODE_ID,
    CSV_INVALID_WRITE_MODE_ID,
    DEPENDENCY_TYPE_NOT_FOUND_ID,
    DI_SERVICE_NOT_CONFIGURED_ID,
    EN_US,
    ERROR_ALREADY_EXISTS_ID,
    ERROR_CONFIG_LOADING_FAILED_ID,
    ERROR_NOT_FOUND_ID,
    FEATURE_ALREADY_EXISTS_ID,
    FEATURE_COMMAND_LOADING_FAILED_ID,
    FEATURE_COMMAND_NOT_FOUND_ID,
    FEATURE_CONFIG_LOADING_FAILED_ID,
    FEATURE_NAME_REQUIRED_ID,
    FEATURE_NOT_FOUND_ID,
    FILE_ALREADY_OPEN_ID,
    FILE_NOT_FOUND_ID,
    IMPORT_DEPENDENCY_FAILED_ID,
    INVALID_APP_INTERFACE_TYPE_ID,
    INVALID_DEPENDENCY_ERROR_ID,
    INVALID_ENCODING_ID,
    INVALID_FEATURE_ATTRIBUTE_ID,
    INVALID_FEATURE_COMMAND_ATTRIBUTE_ID,
    INVALID_FILE_ID,
    INVALID_FILE_MODE_ID,
    INVALID_FLAGGED_DEPENDENCY_ID,
    INVALID_JSON_FILE_ID,
    INVALID_JSON_PATH_ID,
    INVALID_MODEL_ATTRIBUTE_ID,
    INVALID_SERVICE_REGISTRATION_ID,
    INVALID_TOML_FILE_ID,
    INVALID_YAML_FILE_ID,
    JSON_FILE_LOAD_ERROR_ID,
    JSON_FILE_NOT_FOUND_ID,
    JSON_FILE_SAVE_ERROR_ID,
    LOGGER_CREATION_FAILED_ID,
    LOGGING_CONFIG_FAILED_ID,
    MIDDLEWARE_LOADING_FAILED_ID,
    NO_ERROR_MESSAGES_ID,
    PARAMETER_NOT_FOUND_ID,
    PARAMETER_PARSING_FAILED_ID,
    REQUEST_NOT_FOUND_ID,
    REQUEST_VALIDATION_FAILED_ID,
    SERVICE_REGISTRATION_ALREADY_EXISTS_ID,
    SERVICE_REGISTRATION_NOT_FOUND_ID,
    SQLITE_BACKUP_FAILED_ID,
    SQLITE_CONN_ALREADY_OPEN_ID,
    SQLITE_CONN_FAILED_ID,
    SQLITE_CONN_NOT_INITIALIZED_ID,
    SQLITE_FILE_NOT_FOUND_OR_READONLY_ID,
    SQLITE_INVALID_MODE_ID,
    TOML_FILE_LOAD_ERROR_ID,
    TOML_FILE_NOT_FOUND_ID,
    UNSUPPORTED_CONFIG_FILE_TYPE_ID,
    YAML_FILE_LOAD_ERROR_ID,
    YAML_FILE_NOT_FOUND_ID,
    YAML_FILE_SAVE_ERROR_ID,
    create_default_error,
)

# *** constants (errors)

# ** constant: command_parameter_required
COMMAND_PARAMETER_REQUIRED = create_default_error(
    COMMAND_PARAMETER_REQUIRED_ID,
    'Command Parameter Required',
    [(EN_US, 'The required parameter {parameter} for command {command} is missing.')],
)

# ** constant: error_not_found
ERROR_NOT_FOUND = create_default_error(
    ERROR_NOT_FOUND_ID,
    'Error Not Found',
    [(EN_US, 'Error not found: {id}.')],
)

# ** constant: error_already_exists
ERROR_ALREADY_EXISTS = create_default_error(
    ERROR_ALREADY_EXISTS_ID,
    'Error Already Exists',
    [(EN_US, 'An error with ID {id} already exists.')],
)

# ** constant: feature_not_found
FEATURE_NOT_FOUND = create_default_error(
    FEATURE_NOT_FOUND_ID,
    'Feature Not Found',
    [(EN_US, 'Feature not found: {feature_id}.')],
)

# ** constant: feature_already_exists
FEATURE_ALREADY_EXISTS = create_default_error(
    FEATURE_ALREADY_EXISTS_ID,
    'Feature Already Exists',
    [(EN_US, 'Feature with ID {id} already exists.')],
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

# ** constant: feature_command_not_found
FEATURE_COMMAND_NOT_FOUND = create_default_error(
    FEATURE_COMMAND_NOT_FOUND_ID,
    'Feature Command Not Found',
    [(EN_US, 'Feature command not found for feature {feature_id} at position {position}.')],
)

# ** constant: feature_command_loading_failed
FEATURE_COMMAND_LOADING_FAILED = create_default_error(
    FEATURE_COMMAND_LOADING_FAILED_ID,
    'Feature Command Loading Failed',
    [(EN_US, 'Failed to load feature command attribute: {service_id}. Error: {exception}.')],
)

# ** constant: invalid_model_attribute
INVALID_MODEL_ATTRIBUTE = create_default_error(
    INVALID_MODEL_ATTRIBUTE_ID,
    'Invalid Model Attribute',
    [(EN_US, 'Invalid attribute: {attribute}. Supported attributes are {supported}.')],
)

# ** constant: invalid_app_interface_type
INVALID_APP_INTERFACE_TYPE = create_default_error(
    INVALID_APP_INTERFACE_TYPE_ID,
    'Invalid App Interface Type',
    [(EN_US, '{attribute} must be a non-empty string.')],
)

# ** constant: attribute_already_exists
ATTRIBUTE_ALREADY_EXISTS = create_default_error(
    ATTRIBUTE_ALREADY_EXISTS_ID,
    'Attribute Already Exists',
    [(EN_US, 'A container attribute with ID {id} already exists.')],
)

# ** constant: di_service_not_configured
DI_SERVICE_NOT_CONFIGURED = create_default_error(
    DI_SERVICE_NOT_CONFIGURED_ID,
    'DI Service Not Configured',
    [(EN_US, 'No di_service dependency is configured for interface {interface_id}.')],
)

# ** constant: dependency_type_not_found
DEPENDENCY_TYPE_NOT_FOUND = create_default_error(
    DEPENDENCY_TYPE_NOT_FOUND_ID,
    'Dependency Type Not Found',
    [(EN_US, 'No dependency type found for service configuration {configuration_id} with flags {flags}.')],
)

# ** constant: invalid_service_registration
INVALID_SERVICE_REGISTRATION = create_default_error(
    INVALID_SERVICE_REGISTRATION_ID,
    'Invalid Service Registration',
    [(EN_US,
      'A service registration must define either a default type '
      '(module_path/class_name) or at least one flagged dependency.')],
)

# ** constant: service_registration_not_found
SERVICE_REGISTRATION_NOT_FOUND = create_default_error(
    SERVICE_REGISTRATION_NOT_FOUND_ID,
    'Service Registration Not Found',
    [(EN_US, 'Service registration with ID {id} not found.')],
)

# ** constant: service_registration_already_exists
SERVICE_REGISTRATION_ALREADY_EXISTS = create_default_error(
    SERVICE_REGISTRATION_ALREADY_EXISTS_ID,
    'Service Registration Already Exists',
    [(EN_US, 'A service registration with ID {id} already exists.')],
)

# ** constant: invalid_flagged_dependency
INVALID_FLAGGED_DEPENDENCY = create_default_error(
    INVALID_FLAGGED_DEPENDENCY_ID,
    'Invalid Flagged Dependency',
    [(EN_US, 'A flagged dependency must define both module_path and class_name.')],
)

# ** constant: invalid_dependency_error
INVALID_DEPENDENCY_ERROR = create_default_error(
    INVALID_DEPENDENCY_ERROR_ID,
    'Invalid Dependency Error',
    [(EN_US, 'Dependency {dependency} could not be resolved: {reason}.')],
)

# ** constant: parameter_parsing_failed
PARAMETER_PARSING_FAILED = create_default_error(
    PARAMETER_PARSING_FAILED_ID,
    'Parameter Parsing Failed',
    [(EN_US, 'Failed to parse parameter: {parameter}. Error: {exception}.')],
)

# ** constant: parameter_not_found
PARAMETER_NOT_FOUND = create_default_error(
    PARAMETER_NOT_FOUND_ID,
    'Parameter Not Found',
    [(EN_US, 'Parameter {parameter} not found in request data.')],
)

# ** constant: import_dependency_failed
IMPORT_DEPENDENCY_FAILED = create_default_error(
    IMPORT_DEPENDENCY_FAILED_ID,
    'Import Dependency Failed',
    [(EN_US, 'Failed to import {class_name} from {module_path}. Error: {exception}.')],
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

# ** constant: no_error_messages
NO_ERROR_MESSAGES = create_default_error(
    NO_ERROR_MESSAGES_ID,
    'No Error Messages',
    [(EN_US, 'No error messages are defined for error ID {id}.')],
)

# ** constant: middleware_loading_failed
MIDDLEWARE_LOADING_FAILED = create_default_error(
    MIDDLEWARE_LOADING_FAILED_ID,
    'Middleware Loading Failed',
    [(EN_US, 'Failed to load middleware: {service_id}. Error: {exception}.')],
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

# ** constant: app_interface_not_found
APP_INTERFACE_NOT_FOUND = create_default_error(
    APP_INTERFACE_NOT_FOUND_ID,
    'App Interface Not Found',
    [(EN_US, 'App interface with ID {interface_id} not found.')],
)

# ** constant: app_error
APP_ERROR = create_default_error(
    APP_ERROR_ID,
    'App Error',
    [(EN_US, 'An error occurred in the app: {error_message}.')],
)

# ** constant: config_file_not_found
CONFIG_FILE_NOT_FOUND = create_default_error(
    CONFIG_FILE_NOT_FOUND_ID,
    'Configuration File Not Found',
    [(EN_US, 'Configuration file {file_path} not found.')],
)

# ** constant: app_config_loading_failed
APP_CONFIG_LOADING_FAILED = create_default_error(
    APP_CONFIG_LOADING_FAILED_ID,
    'App Configuration Loading Failed',
    [(EN_US, 'Unable to load app configuration file {file_path}: {exception}.')],
)

# ** constant: container_config_loading_failed
CONTAINER_CONFIG_LOADING_FAILED = create_default_error(
    CONTAINER_CONFIG_LOADING_FAILED_ID,
    'Container Configuration Loading Failed',
    [(EN_US, 'Unable to load container configuration file {file_path}: {exception}.')],
)

# ** constant: feature_config_loading_failed
FEATURE_CONFIG_LOADING_FAILED = create_default_error(
    FEATURE_CONFIG_LOADING_FAILED_ID,
    'Feature Configuration Loading Failed',
    [(EN_US, 'Unable to load feature configuration file {file_path}: {exception}.')],
)

# ** constant: error_config_loading_failed
ERROR_CONFIG_LOADING_FAILED = create_default_error(
    ERROR_CONFIG_LOADING_FAILED_ID,
    'Error Configuration Loading Failed',
    [(EN_US, 'Unable to load error configuration file {file_path}: {exception}.')],
)

# ** constant: cli_config_loading_failed
CLI_CONFIG_LOADING_FAILED = create_default_error(
    CLI_CONFIG_LOADING_FAILED_ID,
    'CLI Configuration Loading Failed',
    [(EN_US, 'Unable to load CLI configuration file {file_path}: {exception}.')],
)

# ** constant: cli_command_not_found
CLI_COMMAND_NOT_FOUND = create_default_error(
    CLI_COMMAND_NOT_FOUND_ID,
    'CLI Command Not Found',
    [(EN_US, 'CLI command {command_id} not found.')],
)

# ** constant: cli_command_already_exists
CLI_COMMAND_ALREADY_EXISTS = create_default_error(
    CLI_COMMAND_ALREADY_EXISTS_ID,
    'CLI Command Already Exists',
    [(EN_US, 'CLI command with ID {id} already exists.')],
)

# ** constant: logging_config_failed
LOGGING_CONFIG_FAILED = create_default_error(
    LOGGING_CONFIG_FAILED_ID,
    'Logging Configuration Failed',
    [(EN_US, 'Failed to configure logging: {exception}.')],
)

# ** constant: logger_creation_failed
LOGGER_CREATION_FAILED = create_default_error(
    LOGGER_CREATION_FAILED_ID,
    'Logger Creation Failed',
    [(EN_US, 'Failed to create logger with ID {logger_id}: {exception}.')],
)

# ** constant: file_not_found
FILE_NOT_FOUND = create_default_error(
    FILE_NOT_FOUND_ID,
    'File Not Found',
    [(EN_US, 'File not found: {path}.')],
)

# ** constant: invalid_file
INVALID_FILE = create_default_error(
    INVALID_FILE_ID,
    'Invalid File',
    [(EN_US, 'Path is not a file: {path}.')],
)

# ** constant: file_already_open
FILE_ALREADY_OPEN = create_default_error(
    FILE_ALREADY_OPEN_ID,
    'File Already Open',
    [(EN_US, 'File is already open: {path}.')],
)

# ** constant: invalid_file_mode
INVALID_FILE_MODE = create_default_error(
    INVALID_FILE_MODE_ID,
    'Invalid File Mode',
    [(EN_US, 'Invalid file mode: {mode}. Valid modes include {modes}')],
)

# ** constant: invalid_encoding
INVALID_ENCODING = create_default_error(
    INVALID_ENCODING_ID,
    'Invalid Encoding',
    [(EN_US, 'Invalid encoding: {encoding}. Supported encodings are: utf-8, ascii, latin-1.')],
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

# ** constant: unsupported_config_file_type
UNSUPPORTED_CONFIG_FILE_TYPE = create_default_error(
    UNSUPPORTED_CONFIG_FILE_TYPE_ID,
    'Unsupported Configuration File Type',
    [(EN_US, 'Unsupported configuration file type: {file_extension}.')],
)

# ** constant: yaml_file_not_found
YAML_FILE_NOT_FOUND = create_default_error(
    YAML_FILE_NOT_FOUND_ID,
    'YAML File Not Found',
    [(EN_US, 'The specified YAML file could not be found at {path}.')],
)

# ** constant: yaml_file_load_error
YAML_FILE_LOAD_ERROR = create_default_error(
    YAML_FILE_LOAD_ERROR_ID,
    'YAML Load Failure',
    [(EN_US, 'Failed to parse YAML file: {error}. Path: {path}.')],
)

# ** constant: yaml_file_save_error
YAML_FILE_SAVE_ERROR = create_default_error(
    YAML_FILE_SAVE_ERROR_ID,
    'YAML Save Failure',
    [(EN_US, 'Failed to write YAML file: {error}. Path: {path}.')],
)

# ** constant: json_file_not_found
JSON_FILE_NOT_FOUND = create_default_error(
    JSON_FILE_NOT_FOUND_ID,
    'JSON File Not Found',
    [(EN_US, 'The specified JSON file could not be found at {path}.')],
)

# ** constant: json_file_load_error
JSON_FILE_LOAD_ERROR = create_default_error(
    JSON_FILE_LOAD_ERROR_ID,
    'JSON Load Failure',
    [(EN_US, 'Failed to parse JSON: {error}. Path: {path}.')],
)

# ** constant: json_file_save_error
JSON_FILE_SAVE_ERROR = create_default_error(
    JSON_FILE_SAVE_ERROR_ID,
    'JSON Save Failure',
    [(EN_US, 'Failed to serialize/write JSON: {error}. Path: {path}.')],
)

# ** constant: invalid_json_path
INVALID_JSON_PATH = create_default_error(
    INVALID_JSON_PATH_ID,
    'Invalid JSON Path',
    [(EN_US, 'Invalid JSON path: {path}. Failed at segment: {part}.')],
)

# ** constant: csv_invalid_mode
CSV_INVALID_MODE = create_default_error(
    CSV_INVALID_MODE_ID,
    'Invalid CSV Mode',
    [(EN_US, 'Invalid file mode for CSV operation: {mode}. Expected r, w, a, etc.')],
)

# ** constant: csv_handle_not_initialized
CSV_HANDLE_NOT_INITIALIZED = create_default_error(
    CSV_HANDLE_NOT_INITIALIZED_ID,
    'CSV Handle Not Initialized',
    [(EN_US, 'CSV file must be opened before reading/writing.')],
)

# ** constant: csv_invalid_read_mode
CSV_INVALID_READ_MODE = create_default_error(
    CSV_INVALID_READ_MODE_ID,
    'Invalid CSV Read Mode',
    [(EN_US, 'File not opened in readable mode for CSV reading.')],
)

# ** constant: csv_invalid_write_mode
CSV_INVALID_WRITE_MODE = create_default_error(
    CSV_INVALID_WRITE_MODE_ID,
    'Invalid CSV Write Mode',
    [(EN_US, 'File not opened in writable mode for CSV writing.')],
)

# ** constant: csv_fieldnames_required
CSV_FIELDNAMES_REQUIRED = create_default_error(
    CSV_FIELDNAMES_REQUIRED_ID,
    'CSV Fieldnames Required',
    [(EN_US, 'Fieldnames must be provided when writing dict-based CSV rows.')],
)

# ** constant: csv_dict_no_header
CSV_DICT_NO_HEADER = create_default_error(
    CSV_DICT_NO_HEADER_ID,
    'CSV Dict Reader Without Header',
    [(EN_US, 'Dict reader expects header row; file appears to lack one or was not read correctly.')],
)

# ** constant: toml_file_not_found
TOML_FILE_NOT_FOUND = create_default_error(
    TOML_FILE_NOT_FOUND_ID,
    'TOML File Not Found',
    [(EN_US, 'The specified TOML file could not be found at {path}.')],
)

# ** constant: toml_file_load_error
TOML_FILE_LOAD_ERROR = create_default_error(
    TOML_FILE_LOAD_ERROR_ID,
    'TOML Load Failure',
    [(EN_US, 'Failed to parse TOML file: {error}. Path: {path}.')],
)

# ** constant: invalid_toml_file
INVALID_TOML_FILE = create_default_error(
    INVALID_TOML_FILE_ID,
    'Invalid TOML File',
    [(EN_US, 'File is not a valid TOML file: {path}.')],
)

# ** constant: sqlite_conn_already_open
SQLITE_CONN_ALREADY_OPEN = create_default_error(
    SQLITE_CONN_ALREADY_OPEN_ID,
    'SQLite Connection Already Open',
    [(EN_US, 'Connection already open for path: {path}.')],
)

# ** constant: sqlite_invalid_mode
SQLITE_INVALID_MODE = create_default_error(
    SQLITE_INVALID_MODE_ID,
    'Invalid SQLite Mode',
    [(EN_US, 'Invalid SQLite mode: {mode}. Supported: ro, rw, rwc (or None for default auto-create).')],
)

# ** constant: sqlite_file_not_found_or_readonly
SQLITE_FILE_NOT_FOUND_OR_READONLY = create_default_error(
    SQLITE_FILE_NOT_FOUND_OR_READONLY_ID,
    'SQLite File Not Found or Read-Only',
    [(EN_US,
      'Unable to open SQLite database at {path}: {original_error}. '
      'Check path exists and is writable (use mode=rwc to create).')],
)

# ** constant: sqlite_conn_failed
SQLITE_CONN_FAILED = create_default_error(
    SQLITE_CONN_FAILED_ID,
    'SQLite Connection Failed',
    [(EN_US, 'Failed to connect to SQLite database at {path}: {original_error}')],
)

# ** constant: sqlite_backup_failed
SQLITE_BACKUP_FAILED = create_default_error(
    SQLITE_BACKUP_FAILED_ID,
    'SQLite Backup Failed',
    [(EN_US, 'Backup to {target_path} failed: {original_error}')],
)

# ** constant: sqlite_conn_not_initialized
SQLITE_CONN_NOT_INITIALIZED = create_default_error(
    SQLITE_CONN_NOT_INITIALIZED_ID,
    'SQLite Connection Not Initialized',
    [(EN_US, 'SQLite connection not initialized. Must be used within a "with" block.')],
)

# ** constant: context_not_found
CONTEXT_NOT_FOUND = create_default_error(
    CONTEXT_NOT_FOUND_ID,
    'Context Not Found',
    [(EN_US, 'No context registered for domain type: {domain_type}.')],
)

# *** constants (groups)

# ** constant: default_errors
DEFAULT_ERRORS = {
    COMMAND_PARAMETER_REQUIRED_ID: COMMAND_PARAMETER_REQUIRED,
    ERROR_NOT_FOUND_ID: ERROR_NOT_FOUND,
    ERROR_ALREADY_EXISTS_ID: ERROR_ALREADY_EXISTS,
    FEATURE_NOT_FOUND_ID: FEATURE_NOT_FOUND,
    FEATURE_ALREADY_EXISTS_ID: FEATURE_ALREADY_EXISTS,
    FEATURE_NAME_REQUIRED_ID: FEATURE_NAME_REQUIRED,
    INVALID_FEATURE_ATTRIBUTE_ID: INVALID_FEATURE_ATTRIBUTE,
    INVALID_FEATURE_COMMAND_ATTRIBUTE_ID: INVALID_FEATURE_COMMAND_ATTRIBUTE,
    FEATURE_COMMAND_NOT_FOUND_ID: FEATURE_COMMAND_NOT_FOUND,
    FEATURE_COMMAND_LOADING_FAILED_ID: FEATURE_COMMAND_LOADING_FAILED,
    INVALID_MODEL_ATTRIBUTE_ID: INVALID_MODEL_ATTRIBUTE,
    INVALID_APP_INTERFACE_TYPE_ID: INVALID_APP_INTERFACE_TYPE,
    ATTRIBUTE_ALREADY_EXISTS_ID: ATTRIBUTE_ALREADY_EXISTS,
    DI_SERVICE_NOT_CONFIGURED_ID: DI_SERVICE_NOT_CONFIGURED,
    DEPENDENCY_TYPE_NOT_FOUND_ID: DEPENDENCY_TYPE_NOT_FOUND,
    INVALID_SERVICE_REGISTRATION_ID: INVALID_SERVICE_REGISTRATION,
    SERVICE_REGISTRATION_NOT_FOUND_ID: SERVICE_REGISTRATION_NOT_FOUND,
    SERVICE_REGISTRATION_ALREADY_EXISTS_ID: SERVICE_REGISTRATION_ALREADY_EXISTS,
    INVALID_FLAGGED_DEPENDENCY_ID: INVALID_FLAGGED_DEPENDENCY,
    INVALID_DEPENDENCY_ERROR_ID: INVALID_DEPENDENCY_ERROR,
    PARAMETER_PARSING_FAILED_ID: PARAMETER_PARSING_FAILED,
    PARAMETER_NOT_FOUND_ID: PARAMETER_NOT_FOUND,
    IMPORT_DEPENDENCY_FAILED_ID: IMPORT_DEPENDENCY_FAILED,
    REQUEST_NOT_FOUND_ID: REQUEST_NOT_FOUND,
    REQUEST_VALIDATION_FAILED_ID: REQUEST_VALIDATION_FAILED,
    NO_ERROR_MESSAGES_ID: NO_ERROR_MESSAGES,
    MIDDLEWARE_LOADING_FAILED_ID: MIDDLEWARE_LOADING_FAILED,
    APP_REPOSITORY_IMPORT_FAILED_ID: APP_REPOSITORY_IMPORT_FAILED,
    APP_SERVICE_IMPORT_FAILED_ID: APP_SERVICE_IMPORT_FAILED,
    APP_SERVICE_NOT_LOADED_ID: APP_SERVICE_NOT_LOADED,
    APP_SESSION_NOT_FOUND_ID: APP_SESSION_NOT_FOUND,
    APP_INTERFACE_NOT_FOUND_ID: APP_INTERFACE_NOT_FOUND,
    APP_ERROR_ID: APP_ERROR,
    CONFIG_FILE_NOT_FOUND_ID: CONFIG_FILE_NOT_FOUND,
    APP_CONFIG_LOADING_FAILED_ID: APP_CONFIG_LOADING_FAILED,
    CONTAINER_CONFIG_LOADING_FAILED_ID: CONTAINER_CONFIG_LOADING_FAILED,
    FEATURE_CONFIG_LOADING_FAILED_ID: FEATURE_CONFIG_LOADING_FAILED,
    ERROR_CONFIG_LOADING_FAILED_ID: ERROR_CONFIG_LOADING_FAILED,
    CLI_CONFIG_LOADING_FAILED_ID: CLI_CONFIG_LOADING_FAILED,
    CLI_COMMAND_NOT_FOUND_ID: CLI_COMMAND_NOT_FOUND,
    CLI_COMMAND_ALREADY_EXISTS_ID: CLI_COMMAND_ALREADY_EXISTS,
    LOGGING_CONFIG_FAILED_ID: LOGGING_CONFIG_FAILED,
    LOGGER_CREATION_FAILED_ID: LOGGER_CREATION_FAILED,
    FILE_NOT_FOUND_ID: FILE_NOT_FOUND,
    INVALID_FILE_ID: INVALID_FILE,
    FILE_ALREADY_OPEN_ID: FILE_ALREADY_OPEN,
    INVALID_FILE_MODE_ID: INVALID_FILE_MODE,
    INVALID_ENCODING_ID: INVALID_ENCODING,
    INVALID_JSON_FILE_ID: INVALID_JSON_FILE,
    INVALID_YAML_FILE_ID: INVALID_YAML_FILE,
    UNSUPPORTED_CONFIG_FILE_TYPE_ID: UNSUPPORTED_CONFIG_FILE_TYPE,
    YAML_FILE_NOT_FOUND_ID: YAML_FILE_NOT_FOUND,
    YAML_FILE_LOAD_ERROR_ID: YAML_FILE_LOAD_ERROR,
    YAML_FILE_SAVE_ERROR_ID: YAML_FILE_SAVE_ERROR,
    JSON_FILE_NOT_FOUND_ID: JSON_FILE_NOT_FOUND,
    JSON_FILE_LOAD_ERROR_ID: JSON_FILE_LOAD_ERROR,
    JSON_FILE_SAVE_ERROR_ID: JSON_FILE_SAVE_ERROR,
    INVALID_JSON_PATH_ID: INVALID_JSON_PATH,
    CSV_INVALID_MODE_ID: CSV_INVALID_MODE,
    CSV_HANDLE_NOT_INITIALIZED_ID: CSV_HANDLE_NOT_INITIALIZED,
    CSV_INVALID_READ_MODE_ID: CSV_INVALID_READ_MODE,
    CSV_INVALID_WRITE_MODE_ID: CSV_INVALID_WRITE_MODE,
    CSV_FIELDNAMES_REQUIRED_ID: CSV_FIELDNAMES_REQUIRED,
    CSV_DICT_NO_HEADER_ID: CSV_DICT_NO_HEADER,
    TOML_FILE_NOT_FOUND_ID: TOML_FILE_NOT_FOUND,
    TOML_FILE_LOAD_ERROR_ID: TOML_FILE_LOAD_ERROR,
    INVALID_TOML_FILE_ID: INVALID_TOML_FILE,
    SQLITE_CONN_ALREADY_OPEN_ID: SQLITE_CONN_ALREADY_OPEN,
    SQLITE_INVALID_MODE_ID: SQLITE_INVALID_MODE,
    SQLITE_FILE_NOT_FOUND_OR_READONLY_ID: SQLITE_FILE_NOT_FOUND_OR_READONLY,
    SQLITE_CONN_FAILED_ID: SQLITE_CONN_FAILED,
    SQLITE_BACKUP_FAILED_ID: SQLITE_BACKUP_FAILED,
    SQLITE_CONN_NOT_INITIALIZED_ID: SQLITE_CONN_NOT_INITIALIZED,
    CONTEXT_NOT_FOUND_ID: CONTEXT_NOT_FOUND,
}
