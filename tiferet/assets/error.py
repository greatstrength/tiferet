"""Tiferet Assets Error

Provides the default error catalog for the Tiferet framework. Each entry maps
a framework error-code constant (defined in ``assets/constants.py``) to its
name and multilingual message templates.

The ``ErrorContext`` and the error domain events consume this catalog to
resolve built-in error definitions when they are not overridden by the
consumer's configuration.
"""

# *** imports

# ** app
from .constants import (
    EN_US,
    create_default_error,
)

# *** constants (ids)

# ** constant: command_parameter_required_id
COMMAND_PARAMETER_REQUIRED_ID = 'COMMAND_PARAMETER_REQUIRED'

# ** constant: error_not_found_id
ERROR_NOT_FOUND_ID = 'ERROR_NOT_FOUND'

# ** constant: error_already_exists_id
ERROR_ALREADY_EXISTS_ID = 'ERROR_ALREADY_EXISTS'

# ** constant: feature_name_required_id
FEATURE_NAME_REQUIRED_ID = 'FEATURE_NAME_REQUIRED'

# ** constant: invalid_feature_attribute_id
INVALID_FEATURE_ATTRIBUTE_ID = 'INVALID_FEATURE_ATTRIBUTE'

# ** constant: invalid_feature_command_attribute_id
INVALID_FEATURE_COMMAND_ATTRIBUTE_ID = 'INVALID_FEATURE_COMMAND_ATTRIBUTE'

# ** constant: no_error_messages_id
NO_ERROR_MESSAGES_ID = 'NO_ERROR_MESSAGES'

# ** constant: parameter_parsing_failed_id
PARAMETER_PARSING_FAILED_ID = 'PARAMETER_PARSING_FAILED'

# ** constant: import_dependency_failed_id
IMPORT_DEPENDENCY_FAILED_ID = 'IMPORT_DEPENDENCY_FAILED'

# ** constant: app_service_import_failed_id
APP_SERVICE_IMPORT_FAILED_ID = 'APP_SERVICE_IMPORT_FAILED'

# ** constant: feature_command_loading_failed_id
FEATURE_COMMAND_LOADING_FAILED_ID = 'FEATURE_COMMAND_LOADING_FAILED'

# ** constant: middleware_loading_failed_id
MIDDLEWARE_LOADING_FAILED_ID = 'MIDDLEWARE_LOADING_FAILED'

# ** constant: di_service_not_configured_id
DI_SERVICE_NOT_CONFIGURED_ID = 'DI_SERVICE_NOT_CONFIGURED'

# ** constant: context_not_found_id
CONTEXT_NOT_FOUND_ID = 'CONTEXT_NOT_FOUND'

# ** constant: request_not_found_id
REQUEST_NOT_FOUND_ID = 'REQUEST_NOT_FOUND'

# ** constant: parameter_not_found_id
PARAMETER_NOT_FOUND_ID = 'PARAMETER_NOT_FOUND'

# ** constant: request_validation_failed_id
REQUEST_VALIDATION_FAILED_ID = 'REQUEST_VALIDATION_FAILED'

# ** constant: feature_not_found_id
FEATURE_NOT_FOUND_ID = 'FEATURE_NOT_FOUND'

# ** constant: feature_already_exists_id
FEATURE_ALREADY_EXISTS_ID = 'FEATURE_ALREADY_EXISTS'

# ** constant: feature_command_not_found_id
FEATURE_COMMAND_NOT_FOUND_ID = 'FEATURE_COMMAND_NOT_FOUND'

# ** constant: logging_config_failed_id
LOGGING_CONFIG_FAILED_ID = 'LOGGING_CONFIG_FAILED'

# ** constant: logger_creation_failed_id
LOGGER_CREATION_FAILED_ID = 'LOGGER_CREATION_FAILED'

# ** constant: file_not_found_id
FILE_NOT_FOUND_ID = 'FILE_NOT_FOUND'

# ** constant: invalid_file_id
INVALID_FILE_ID = 'INVALID_FILE'

# ** constant: file_already_open_id
FILE_ALREADY_OPEN_ID = 'FILE_ALREADY_OPEN'

# ** constant: invalid_file_mode_id
INVALID_FILE_MODE_ID = 'INVALID_FILE_MODE'

# ** constant: invalid_encoding_id
INVALID_ENCODING_ID = 'INVALID_ENCODING'

# ** constant: invalid_json_file_id
INVALID_JSON_FILE_ID = 'INVALID_JSON_FILE'

# ** constant: json_file_load_error_id
JSON_FILE_LOAD_ERROR_ID = 'JSON_FILE_LOAD_ERROR'

# ** constant: json_file_save_error_id
JSON_FILE_SAVE_ERROR_ID = 'JSON_FILE_SAVE_ERROR'

# ** constant: invalid_yaml_file_id
INVALID_YAML_FILE_ID = 'INVALID_YAML_FILE'

# ** constant: yaml_file_not_found_id
YAML_FILE_NOT_FOUND_ID = 'YAML_FILE_NOT_FOUND'

# ** constant: yaml_file_load_error_id
YAML_FILE_LOAD_ERROR_ID = 'YAML_FILE_LOAD_ERROR'

# ** constant: yaml_file_save_error_id
YAML_FILE_SAVE_ERROR_ID = 'YAML_FILE_SAVE_ERROR'

# ** constant: unsupported_config_file_type_id
UNSUPPORTED_CONFIG_FILE_TYPE_ID = 'UNSUPPORTED_CONFIG_FILE_TYPE'

# ** constant: app_interface_not_found_id
APP_INTERFACE_NOT_FOUND_ID = 'APP_INTERFACE_NOT_FOUND'

# ** constant: invalid_service_registration_id
INVALID_SERVICE_REGISTRATION_ID = 'INVALID_SERVICE_REGISTRATION'

# ** constant: service_registration_not_found_id
SERVICE_REGISTRATION_NOT_FOUND_ID = 'SERVICE_REGISTRATION_NOT_FOUND'

# ** constant: invalid_flagged_dependency_id
INVALID_FLAGGED_DEPENDENCY_ID = 'INVALID_FLAGGED_DEPENDENCY'

# ** constant: service_registration_already_exists_id
SERVICE_REGISTRATION_ALREADY_EXISTS_ID = 'SERVICE_REGISTRATION_ALREADY_EXISTS'

# ** constant: invalid_model_attribute_id
INVALID_MODEL_ATTRIBUTE_ID = 'INVALID_MODEL_ATTRIBUTE'

# ** constant: invalid_app_interface_type_id
INVALID_APP_INTERFACE_TYPE_ID = 'INVALID_APP_INTERFACE_TYPE'

# ** constant: sqlite_conn_already_open_id
SQLITE_CONN_ALREADY_OPEN_ID = 'SQLITE_CONN_ALREADY_OPEN'

# ** constant: sqlite_invalid_mode_id
SQLITE_INVALID_MODE_ID = 'SQLITE_INVALID_MODE'

# ** constant: sqlite_file_not_found_or_readonly_id
SQLITE_FILE_NOT_FOUND_OR_READONLY_ID = 'SQLITE_FILE_NOT_FOUND_OR_READONLY'

# ** constant: sqlite_conn_failed_id
SQLITE_CONN_FAILED_ID = 'SQLITE_CONN_FAILED'

# ** constant: sqlite_backup_failed_id
SQLITE_BACKUP_FAILED_ID = 'SQLITE_BACKUP_FAILED'

# ** constant: sqlite_conn_not_initialized_id
SQLITE_CONN_NOT_INITIALIZED_ID = 'SQLITE_CONN_NOT_INITIALIZED'

# ** constant: app_error_id
APP_ERROR_ID = 'APP_ERROR'

# ** constant: config_file_not_found_id
CONFIG_FILE_NOT_FOUND_ID = 'CONFIG_FILE_NOT_FOUND'

# ** constant: app_config_loading_failed_id
APP_CONFIG_LOADING_FAILED_ID = 'APP_CONFIG_LOADING_FAILED'

# ** constant: container_config_loading_failed_id
CONTAINER_CONFIG_LOADING_FAILED_ID = 'CONTAINER_CONFIG_LOADING_FAILED'

# ** constant: feature_config_loading_failed_id
FEATURE_CONFIG_LOADING_FAILED_ID = 'FEATURE_CONFIG_LOADING_FAILED'

# ** constant: error_config_loading_failed_id
ERROR_CONFIG_LOADING_FAILED_ID = 'ERROR_CONFIG_LOADING_FAILED'

# ** constant: cli_config_loading_failed_id
CLI_CONFIG_LOADING_FAILED_ID = 'CLI_CONFIG_LOADING_FAILED'

# ** constant: cli_command_not_found_id
CLI_COMMAND_NOT_FOUND_ID = 'CLI_COMMAND_NOT_FOUND'

# ** constant: cli_command_already_exists_id
CLI_COMMAND_ALREADY_EXISTS_ID = 'CLI_COMMAND_ALREADY_EXISTS'

# ** constant: json_file_not_found_id
JSON_FILE_NOT_FOUND_ID = 'JSON_FILE_NOT_FOUND'

# ** constant: invalid_json_path_id
INVALID_JSON_PATH_ID = 'INVALID_JSON_PATH'

# ** constant: toml_file_not_found_id
TOML_FILE_NOT_FOUND_ID = 'TOML_FILE_NOT_FOUND'

# ** constant: toml_file_load_error_id
TOML_FILE_LOAD_ERROR_ID = 'TOML_FILE_LOAD_ERROR'

# ** constant: invalid_toml_file_id
INVALID_TOML_FILE_ID = 'INVALID_TOML_FILE'

# ** constant: csv_invalid_mode_id
CSV_INVALID_MODE_ID = 'CSV_INVALID_MODE'

# ** constant: csv_handle_not_initialized_id
CSV_HANDLE_NOT_INITIALIZED_ID = 'CSV_HANDLE_NOT_INITIALIZED'

# ** constant: csv_invalid_read_mode_id
CSV_INVALID_READ_MODE_ID = 'CSV_INVALID_READ_MODE'

# ** constant: csv_invalid_write_mode_id
CSV_INVALID_WRITE_MODE_ID = 'CSV_INVALID_WRITE_MODE'

# ** constant: csv_fieldnames_required_id
CSV_FIELDNAMES_REQUIRED_ID = 'CSV_FIELDNAMES_REQUIRED'

# ** constant: csv_dict_no_header_id
CSV_DICT_NO_HEADER_ID = 'CSV_DICT_NO_HEADER'

# *** constants (models)

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
    [(EN_US, 'Invalid feature attribute: {attribute}')],
)

# ** constant: invalid_feature_command_attribute
INVALID_FEATURE_COMMAND_ATTRIBUTE = create_default_error(
    INVALID_FEATURE_COMMAND_ATTRIBUTE_ID,
    'Invalid Feature Command Attribute',
    [(EN_US, 'Invalid feature command attribute: {attribute}. Supported attributes are name, attribute_id, data_key, pass_on_error, and parameters.')],
)

# ** constant: no_error_messages
NO_ERROR_MESSAGES = create_default_error(
    NO_ERROR_MESSAGES_ID,
    'No Error Messages',
    [(EN_US, 'No error messages are defined for error ID {id}.')],
)

# ** constant: parameter_parsing_failed
PARAMETER_PARSING_FAILED = create_default_error(
    PARAMETER_PARSING_FAILED_ID,
    'Parameter Parsing Failed',
    [(EN_US, 'Failed to parse parameter: {parameter}. Error: {exception}.')],
)

# ** constant: import_dependency_failed
IMPORT_DEPENDENCY_FAILED = create_default_error(
    IMPORT_DEPENDENCY_FAILED_ID,
    'Import Dependency Failed',
    [(EN_US, 'Failed to import {class_name} from {module_path}. Error: {exception}.')],
)

# ** constant: app_service_import_failed
APP_SERVICE_IMPORT_FAILED = create_default_error(
    APP_SERVICE_IMPORT_FAILED_ID,
    'App Service Import Failed',
    [(EN_US, 'Failed to import app service dependencies: {exception}.')],
)

# ** constant: feature_command_loading_failed
FEATURE_COMMAND_LOADING_FAILED = create_default_error(
    FEATURE_COMMAND_LOADING_FAILED_ID,
    'Feature Command Loading Failed',
    [(EN_US, 'Failed to load feature command attribute: {service_id}. Error: {exception}.')],
)

# ** constant: middleware_loading_failed
MIDDLEWARE_LOADING_FAILED = create_default_error(
    MIDDLEWARE_LOADING_FAILED_ID,
    'Middleware Loading Failed',
    [(EN_US, 'Failed to load middleware: {service_id}. Error: {exception}.')],
)

# ** constant: di_service_not_configured
DI_SERVICE_NOT_CONFIGURED = create_default_error(
    DI_SERVICE_NOT_CONFIGURED_ID,
    'DI Service Not Configured',
    [(EN_US, 'No di_service dependency is configured for interface {interface_id}.')],
)

# ** constant: context_not_found
CONTEXT_NOT_FOUND = create_default_error(
    CONTEXT_NOT_FOUND_ID,
    'Context Not Found',
    [(EN_US, 'No context registered for domain type: {domain_type}.')],
)

# ** constant: request_not_found
REQUEST_NOT_FOUND = create_default_error(
    REQUEST_NOT_FOUND_ID,
    'Request Not Found',
    [(EN_US, 'Request data is not available for parameter parsing.')],
)

# ** constant: parameter_not_found
PARAMETER_NOT_FOUND = create_default_error(
    PARAMETER_NOT_FOUND_ID,
    'Parameter Not Found',
    [(EN_US, 'Parameter {parameter} not found in request data.')],
)

# ** constant: request_validation_failed
REQUEST_VALIDATION_FAILED = create_default_error(
    REQUEST_VALIDATION_FAILED_ID,
    'Request Validation Failed',
    [(EN_US, 'Request validation failed for feature {feature_id}: {violations}.')],
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

# ** constant: feature_command_not_found
FEATURE_COMMAND_NOT_FOUND = create_default_error(
    FEATURE_COMMAND_NOT_FOUND_ID,
    'Feature Command Not Found',
    [(EN_US, 'Feature command not found for feature {feature_id} at position {position}.')],
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

# ** constant: invalid_yaml_file
INVALID_YAML_FILE = create_default_error(
    INVALID_YAML_FILE_ID,
    'Invalid YAML File',
    [(EN_US, 'File is not a valid YAML file: {path}.')],
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

# ** constant: unsupported_config_file_type
UNSUPPORTED_CONFIG_FILE_TYPE = create_default_error(
    UNSUPPORTED_CONFIG_FILE_TYPE_ID,
    'Unsupported Configuration File Type',
    [(EN_US, 'Unsupported configuration file type: {file_extension}.')],
)

# ** constant: app_interface_not_found
APP_INTERFACE_NOT_FOUND = create_default_error(
    APP_INTERFACE_NOT_FOUND_ID,
    'App Interface Not Found',
    [(EN_US, 'App interface with ID {interface_id} not found.')],
)

# ** constant: invalid_service_registration
INVALID_SERVICE_REGISTRATION = create_default_error(
    INVALID_SERVICE_REGISTRATION_ID,
    'Invalid Service Registration',
    [(EN_US, 'A service registration must define either a default type (module_path/class_name) or at least one flagged dependency.')],
)

# ** constant: service_registration_not_found
SERVICE_REGISTRATION_NOT_FOUND = create_default_error(
    SERVICE_REGISTRATION_NOT_FOUND_ID,
    'Service Registration Not Found',
    [(EN_US, 'Service registration with ID {id} not found.')],
)

# ** constant: invalid_flagged_dependency
INVALID_FLAGGED_DEPENDENCY = create_default_error(
    INVALID_FLAGGED_DEPENDENCY_ID,
    'Invalid Flagged Dependency',
    [(EN_US, 'A flagged dependency must define both module_path and class_name.')],
)

# ** constant: service_registration_already_exists
SERVICE_REGISTRATION_ALREADY_EXISTS = create_default_error(
    SERVICE_REGISTRATION_ALREADY_EXISTS_ID,
    'Service Registration Already Exists',
    [(EN_US, 'A service registration with ID {id} already exists.')],
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
    [(EN_US, 'Unable to open SQLite database at {path}: {original_error}. Check path exists and is writable (use mode=rwc to create).')],
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

# ** constant: json_file_not_found
JSON_FILE_NOT_FOUND = create_default_error(
    JSON_FILE_NOT_FOUND_ID,
    'JSON File Not Found',
    [(EN_US, 'The specified JSON file could not be found at {path}.')],
)

# ** constant: invalid_json_path
INVALID_JSON_PATH = create_default_error(
    INVALID_JSON_PATH_ID,
    'Invalid JSON Path',
    [(EN_US, 'Invalid JSON path: {path}. Failed at segment: {part}.')],
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

# *** constants (groups)

# ** constant: core_default_errors
CORE_DEFAULT_ERRORS = {
    COMMAND_PARAMETER_REQUIRED_ID: COMMAND_PARAMETER_REQUIRED,
    PARAMETER_PARSING_FAILED_ID: PARAMETER_PARSING_FAILED,
    IMPORT_DEPENDENCY_FAILED_ID: IMPORT_DEPENDENCY_FAILED,
    APP_SERVICE_IMPORT_FAILED_ID: APP_SERVICE_IMPORT_FAILED,
    APP_INTERFACE_NOT_FOUND_ID: APP_INTERFACE_NOT_FOUND,
    DI_SERVICE_NOT_CONFIGURED_ID: DI_SERVICE_NOT_CONFIGURED,
    INVALID_APP_INTERFACE_TYPE_ID: INVALID_APP_INTERFACE_TYPE,
    APP_ERROR_ID: APP_ERROR,
    CONTEXT_NOT_FOUND_ID: CONTEXT_NOT_FOUND,
    FEATURE_NOT_FOUND_ID: FEATURE_NOT_FOUND,
    FEATURE_COMMAND_LOADING_FAILED_ID: FEATURE_COMMAND_LOADING_FAILED,
    MIDDLEWARE_LOADING_FAILED_ID: MIDDLEWARE_LOADING_FAILED,
    REQUEST_NOT_FOUND_ID: REQUEST_NOT_FOUND,
    PARAMETER_NOT_FOUND_ID: PARAMETER_NOT_FOUND,
    REQUEST_VALIDATION_FAILED_ID: REQUEST_VALIDATION_FAILED,
    LOGGING_CONFIG_FAILED_ID: LOGGING_CONFIG_FAILED,
    LOGGER_CREATION_FAILED_ID: LOGGER_CREATION_FAILED,
    ERROR_NOT_FOUND_ID: ERROR_NOT_FOUND,
    CONFIG_FILE_NOT_FOUND_ID: CONFIG_FILE_NOT_FOUND,
    APP_CONFIG_LOADING_FAILED_ID: APP_CONFIG_LOADING_FAILED,
    CONTAINER_CONFIG_LOADING_FAILED_ID: CONTAINER_CONFIG_LOADING_FAILED,
    FEATURE_CONFIG_LOADING_FAILED_ID: FEATURE_CONFIG_LOADING_FAILED,
    ERROR_CONFIG_LOADING_FAILED_ID: ERROR_CONFIG_LOADING_FAILED,
    UNSUPPORTED_CONFIG_FILE_TYPE_ID: UNSUPPORTED_CONFIG_FILE_TYPE,
    FILE_NOT_FOUND_ID: FILE_NOT_FOUND,
    INVALID_FILE_ID: INVALID_FILE,
    FILE_ALREADY_OPEN_ID: FILE_ALREADY_OPEN,
    INVALID_FILE_MODE_ID: INVALID_FILE_MODE,
    INVALID_ENCODING_ID: INVALID_ENCODING,
    INVALID_YAML_FILE_ID: INVALID_YAML_FILE,
    YAML_FILE_NOT_FOUND_ID: YAML_FILE_NOT_FOUND,
    YAML_FILE_LOAD_ERROR_ID: YAML_FILE_LOAD_ERROR,
    INVALID_JSON_FILE_ID: INVALID_JSON_FILE,
    JSON_FILE_NOT_FOUND_ID: JSON_FILE_NOT_FOUND,
    JSON_FILE_LOAD_ERROR_ID: JSON_FILE_LOAD_ERROR,
    INVALID_JSON_PATH_ID: INVALID_JSON_PATH,
    INVALID_MODEL_ATTRIBUTE_ID: INVALID_MODEL_ATTRIBUTE,
}

# ** constant: admin_default_errors
ADMIN_DEFAULT_ERRORS = {
    ERROR_ALREADY_EXISTS_ID: ERROR_ALREADY_EXISTS,
    NO_ERROR_MESSAGES_ID: NO_ERROR_MESSAGES,
    FEATURE_ALREADY_EXISTS_ID: FEATURE_ALREADY_EXISTS,
    FEATURE_NAME_REQUIRED_ID: FEATURE_NAME_REQUIRED,
    INVALID_FEATURE_ATTRIBUTE_ID: INVALID_FEATURE_ATTRIBUTE,
    INVALID_FEATURE_COMMAND_ATTRIBUTE_ID: INVALID_FEATURE_COMMAND_ATTRIBUTE,
    FEATURE_COMMAND_NOT_FOUND_ID: FEATURE_COMMAND_NOT_FOUND,
    INVALID_SERVICE_REGISTRATION_ID: INVALID_SERVICE_REGISTRATION,
    SERVICE_REGISTRATION_NOT_FOUND_ID: SERVICE_REGISTRATION_NOT_FOUND,
    INVALID_FLAGGED_DEPENDENCY_ID: INVALID_FLAGGED_DEPENDENCY,
    SERVICE_REGISTRATION_ALREADY_EXISTS_ID: SERVICE_REGISTRATION_ALREADY_EXISTS,
    CLI_COMMAND_NOT_FOUND_ID: CLI_COMMAND_NOT_FOUND,
    CLI_COMMAND_ALREADY_EXISTS_ID: CLI_COMMAND_ALREADY_EXISTS,
    CLI_CONFIG_LOADING_FAILED_ID: CLI_CONFIG_LOADING_FAILED,
    YAML_FILE_SAVE_ERROR_ID: YAML_FILE_SAVE_ERROR,
    JSON_FILE_SAVE_ERROR_ID: JSON_FILE_SAVE_ERROR,
}

# ** constant: sqlite_default_errors
SQLITE_DEFAULT_ERRORS = {
    SQLITE_CONN_ALREADY_OPEN_ID: SQLITE_CONN_ALREADY_OPEN,
    SQLITE_INVALID_MODE_ID: SQLITE_INVALID_MODE,
    SQLITE_FILE_NOT_FOUND_OR_READONLY_ID: SQLITE_FILE_NOT_FOUND_OR_READONLY,
    SQLITE_CONN_FAILED_ID: SQLITE_CONN_FAILED,
    SQLITE_BACKUP_FAILED_ID: SQLITE_BACKUP_FAILED,
    SQLITE_CONN_NOT_INITIALIZED_ID: SQLITE_CONN_NOT_INITIALIZED,
}

# ** constant: toml_default_errors
TOML_DEFAULT_ERRORS = {
    TOML_FILE_NOT_FOUND_ID: TOML_FILE_NOT_FOUND,
    TOML_FILE_LOAD_ERROR_ID: TOML_FILE_LOAD_ERROR,
    INVALID_TOML_FILE_ID: INVALID_TOML_FILE,
}

# ** constant: csv_default_errors
CSV_DEFAULT_ERRORS = {
    CSV_INVALID_MODE_ID: CSV_INVALID_MODE,
    CSV_HANDLE_NOT_INITIALIZED_ID: CSV_HANDLE_NOT_INITIALIZED,
    CSV_INVALID_READ_MODE_ID: CSV_INVALID_READ_MODE,
    CSV_INVALID_WRITE_MODE_ID: CSV_INVALID_WRITE_MODE,
    CSV_FIELDNAMES_REQUIRED_ID: CSV_FIELDNAMES_REQUIRED,
    CSV_DICT_NO_HEADER_ID: CSV_DICT_NO_HEADER,
}

# ** constant: default_errors
DEFAULT_ERRORS = {
    **CORE_DEFAULT_ERRORS,
    **ADMIN_DEFAULT_ERRORS,
    **SQLITE_DEFAULT_ERRORS,
    **TOML_DEFAULT_ERRORS,
    **CSV_DEFAULT_ERRORS,
}
