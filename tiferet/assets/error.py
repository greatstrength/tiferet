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
    APP_CONFIG_LOADING_FAILED_ID,
    APP_ERROR_ID,
    APP_INTERFACE_NOT_FOUND_ID,
    APP_REPOSITORY_IMPORT_FAILED_ID,
    APP_SERVICE_IMPORT_FAILED_ID,
    APP_SERVICE_NOT_LOADED_ID,
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
)

# *** constants

# ** constant: default_errors
DEFAULT_ERRORS = {

    # * error: COMMAND_PARAMETER_REQUIRED
    COMMAND_PARAMETER_REQUIRED_ID: {
        'id': COMMAND_PARAMETER_REQUIRED_ID,
        'name': 'Command Parameter Required',
        'message': [
            {'lang': 'en_US', 'text': 'The required parameter {parameter} for command {command} is missing.'},
        ],
    },

    # * error: ERROR_NOT_FOUND
    ERROR_NOT_FOUND_ID: {
        'id': ERROR_NOT_FOUND_ID,
        'name': 'Error Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Error not found: {id}.'},
        ],
    },

    # * error: ERROR_ALREADY_EXISTS
    ERROR_ALREADY_EXISTS_ID: {
        'id': ERROR_ALREADY_EXISTS_ID,
        'name': 'Error Already Exists',
        'message': [
            {'lang': 'en_US', 'text': 'An error with ID {id} already exists.'},
        ],
    },

    # * error: FEATURE_NAME_REQUIRED
    FEATURE_NAME_REQUIRED_ID: {
        'id': FEATURE_NAME_REQUIRED_ID,
        'name': 'Feature Name Required',
        'message': [
            {'lang': 'en_US', 'text': 'A feature name is required when updating the name attribute.'},
        ],
    },

    # * error: INVALID_FEATURE_ATTRIBUTE
    INVALID_FEATURE_ATTRIBUTE_ID: {
        'id': INVALID_FEATURE_ATTRIBUTE_ID,
        'name': 'Invalid Feature Attribute',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid feature attribute: {attribute}'},
        ],
    },

    # * error: INVALID_FEATURE_COMMAND_ATTRIBUTE
    INVALID_FEATURE_COMMAND_ATTRIBUTE_ID: {
        'id': INVALID_FEATURE_COMMAND_ATTRIBUTE_ID,
        'name': 'Invalid Feature Command Attribute',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid feature command attribute: {attribute}. Supported attributes are name, attribute_id, data_key, pass_on_error, and parameters.'},
        ],
    },

    # * error: NO_ERROR_MESSAGES
    NO_ERROR_MESSAGES_ID: {
        'id': NO_ERROR_MESSAGES_ID,
        'name': 'No Error Messages',
        'message': [
            {'lang': 'en_US', 'text': 'No error messages are defined for error ID {id}.'},
        ],
    },

    # * error: PARAMETER_PARSING_FAILED
    PARAMETER_PARSING_FAILED_ID: {
        'id': PARAMETER_PARSING_FAILED_ID,
        'name': 'Parameter Parsing Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to parse parameter: {parameter}. Error: {exception}.'},
        ],
    },

    # * error: IMPORT_DEPENDENCY_FAILED
    IMPORT_DEPENDENCY_FAILED_ID: {
        'id': IMPORT_DEPENDENCY_FAILED_ID,
        'name': 'Import Dependency Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to import {class_name} from {module_path}. Error: {exception}.'},
        ],
    },

    # * error: APP_SERVICE_IMPORT_FAILED
    APP_SERVICE_IMPORT_FAILED_ID: {
        'id': APP_SERVICE_IMPORT_FAILED_ID,
        'name': 'App Service Import Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to import app service dependencies: {exception}.'},
        ],
    },

    # * error: FEATURE_COMMAND_LOADING_FAILED
    FEATURE_COMMAND_LOADING_FAILED_ID: {
        'id': FEATURE_COMMAND_LOADING_FAILED_ID,
        'name': 'Feature Command Loading Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to load feature command attribute: {service_id}. Error: {exception}.'},
        ],
    },

    # * error: MIDDLEWARE_LOADING_FAILED
    MIDDLEWARE_LOADING_FAILED_ID: {
        'id': MIDDLEWARE_LOADING_FAILED_ID,
        'name': 'Middleware Loading Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to load middleware: {service_id}. Error: {exception}.'},
        ],
    },

    # * error: APP_REPOSITORY_IMPORT_FAILED
    APP_REPOSITORY_IMPORT_FAILED_ID: {
        'id': APP_REPOSITORY_IMPORT_FAILED_ID,
        'name': 'App Repository Import Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to import app repository: {exception}.'},
        ],
    },

    # * error: APP_SERVICE_NOT_LOADED
    APP_SERVICE_NOT_LOADED_ID: {
        'id': APP_SERVICE_NOT_LOADED_ID,
        'name': 'App Service Not Loaded',
        'message': [
            {'lang': 'en_US', 'text': 'App service must be loaded before loading interface {interface_id}.'},
        ],
    },

    # * error: DI_SERVICE_NOT_CONFIGURED
    DI_SERVICE_NOT_CONFIGURED_ID: {
        'id': DI_SERVICE_NOT_CONFIGURED_ID,
        'name': 'DI Service Not Configured',
        'message': [
            {'lang': 'en_US', 'text': 'No di_service dependency is configured for interface {interface_id}.'},
        ],
    },

    # * error: DEPENDENCY_TYPE_NOT_FOUND
    DEPENDENCY_TYPE_NOT_FOUND_ID: {
        'id': DEPENDENCY_TYPE_NOT_FOUND_ID,
        'name': 'Dependency Type Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'No dependency type found for configuration {configuration_id} with flags {flags}.'},
        ],
    },

    # * error: CONTEXT_NOT_FOUND
    CONTEXT_NOT_FOUND_ID: {
        'id': CONTEXT_NOT_FOUND_ID,
        'name': 'Context Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'No context registered for domain type: {domain_type}.'},
        ],
    },

    # * error: REQUEST_NOT_FOUND
    REQUEST_NOT_FOUND_ID: {
        'id': REQUEST_NOT_FOUND_ID,
        'name': 'Request Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Request data is not available for parameter parsing.'},
        ],
    },

    # * error: PARAMETER_NOT_FOUND
    PARAMETER_NOT_FOUND_ID: {
        'id': PARAMETER_NOT_FOUND_ID,
        'name': 'Parameter Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Parameter {parameter} not found in request data.'},
        ],
    },

    # * error: REQUEST_VALIDATION_FAILED
    REQUEST_VALIDATION_FAILED_ID: {
        'id': REQUEST_VALIDATION_FAILED_ID,
        'name': 'Request Validation Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Request validation failed for feature {feature_id}: {violations}.'},
        ],
    },

    # * error: FEATURE_NOT_FOUND
    FEATURE_NOT_FOUND_ID: {
        'id': FEATURE_NOT_FOUND_ID,
        'name': 'Feature Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Feature not found: {feature_id}.'},
        ],
    },

    # * error: FEATURE_ALREADY_EXISTS
    FEATURE_ALREADY_EXISTS_ID: {
        'id': FEATURE_ALREADY_EXISTS_ID,
        'name': 'Feature Already Exists',
        'message': [
            {'lang': 'en_US', 'text': 'Feature with ID {id} already exists.'},
        ],
    },

    # * error: FEATURE_COMMAND_NOT_FOUND
    FEATURE_COMMAND_NOT_FOUND_ID: {
        'id': FEATURE_COMMAND_NOT_FOUND_ID,
        'name': 'Feature Command Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Feature command not found for feature {feature_id} at position {position}.'},
        ],
    },

    # * error: LOGGING_CONFIG_FAILED
    LOGGING_CONFIG_FAILED_ID: {
        'id': LOGGING_CONFIG_FAILED_ID,
        'name': 'Logging Configuration Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to configure logging: {exception}.'},
        ],
    },

    # * error: LOGGER_CREATION_FAILED
    LOGGER_CREATION_FAILED_ID: {
        'id': LOGGER_CREATION_FAILED_ID,
        'name': 'Logger Creation Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to create logger with ID {logger_id}: {exception}.'},
        ],
    },

    # * error: FILE_NOT_FOUND
    FILE_NOT_FOUND_ID: {
        'id': FILE_NOT_FOUND_ID,
        'name': 'File Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'File not found: {path}.'},
        ],
    },

    # * error: INVALID_FILE
    INVALID_FILE_ID: {
        'id': INVALID_FILE_ID,
        'name': 'Invalid File',
        'message': [
            {'lang': 'en_US', 'text': 'Path is not a file: {path}.'},
        ],
    },

    # * error: FILE_ALREADY_OPEN
    FILE_ALREADY_OPEN_ID: {
        'id': FILE_ALREADY_OPEN_ID,
        'name': 'File Already Open',
        'message': [
            {'lang': 'en_US', 'text': 'File is already open: {path}.'},
        ],
    },

    # * error: INVALID_FILE_MODE
    INVALID_FILE_MODE_ID: {
        'id': INVALID_FILE_MODE_ID,
        'name': 'Invalid File Mode',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid file mode: {mode}. Valid modes include {modes}'},
        ],
    },

    # * error: INVALID_ENCODING
    INVALID_ENCODING_ID: {
        'id': INVALID_ENCODING_ID,
        'name': 'Invalid Encoding',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid encoding: {encoding}. Supported encodings are: utf-8, ascii, latin-1.'},
        ],
    },

    # * error: INVALID_JSON_FILE
    INVALID_JSON_FILE_ID: {
        'id': INVALID_JSON_FILE_ID,
        'name': 'Invalid JSON File',
        'message': [
            {'lang': 'en_US', 'text': 'File is not a valid JSON file: {path}.'},
        ],
    },

    # * error: JSON_FILE_LOAD_ERROR
    JSON_FILE_LOAD_ERROR_ID: {
        'id': JSON_FILE_LOAD_ERROR_ID,
        'name': 'JSON Load Failure',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to parse JSON: {error}. Path: {path}.'},
        ],
    },

    # * error: JSON_FILE_SAVE_ERROR
    JSON_FILE_SAVE_ERROR_ID: {
        'id': JSON_FILE_SAVE_ERROR_ID,
        'name': 'JSON Save Failure',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to serialize/write JSON: {error}. Path: {path}.'},
        ],
    },

    # * error: INVALID_YAML_FILE
    INVALID_YAML_FILE_ID: {
        'id': INVALID_YAML_FILE_ID,
        'name': 'Invalid YAML File',
        'message': [
            {'lang': 'en_US', 'text': 'File is not a valid YAML file: {path}.'},
        ],
    },

    # * error: YAML_FILE_NOT_FOUND
    YAML_FILE_NOT_FOUND_ID: {
        'id': YAML_FILE_NOT_FOUND_ID,
        'name': 'YAML File Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'The specified YAML file could not be found at {path}.'},
        ],
    },

    # * error: YAML_FILE_LOAD_ERROR
    YAML_FILE_LOAD_ERROR_ID: {
        'id': YAML_FILE_LOAD_ERROR_ID,
        'name': 'YAML Load Failure',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to parse YAML file: {error}. Path: {path}.'},
        ],
    },

    # * error: YAML_FILE_SAVE_ERROR
    YAML_FILE_SAVE_ERROR_ID: {
        'id': YAML_FILE_SAVE_ERROR_ID,
        'name': 'YAML Save Failure',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to write YAML file: {error}. Path: {path}.'},
        ],
    },

    # * error: UNSUPPORTED_CONFIG_FILE_TYPE
    UNSUPPORTED_CONFIG_FILE_TYPE_ID: {
        'id': UNSUPPORTED_CONFIG_FILE_TYPE_ID,
        'name': 'Unsupported Configuration File Type',
        'message': [
            {'lang': 'en_US', 'text': 'Unsupported configuration file type: {file_extension}.'},
        ],
    },

    # * error: APP_INTERFACE_NOT_FOUND
    APP_INTERFACE_NOT_FOUND_ID: {
        'id': APP_INTERFACE_NOT_FOUND_ID,
        'name': 'App Interface Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'App interface with ID {interface_id} not found.'},
        ],
    },

    # * error: INVALID_SERVICE_REGISTRATION
    INVALID_SERVICE_REGISTRATION_ID: {
        'id': INVALID_SERVICE_REGISTRATION_ID,
        'name': 'Invalid Service Registration',
        'message': [
            {'lang': 'en_US', 'text': 'A service registration must define either a default type (module_path/class_name) or at least one flagged dependency.'},
        ],
    },

    # * error: ATTRIBUTE_ALREADY_EXISTS
    ATTRIBUTE_ALREADY_EXISTS_ID: {
        'id': ATTRIBUTE_ALREADY_EXISTS_ID,
        'name': 'Attribute Already Exists',
        'message': [
            {'lang': 'en_US', 'text': 'A container attribute with ID {id} already exists.'},
        ],
    },

    # * error: SERVICE_REGISTRATION_NOT_FOUND
    SERVICE_REGISTRATION_NOT_FOUND_ID: {
        'id': SERVICE_REGISTRATION_NOT_FOUND_ID,
        'name': 'Service Registration Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Service registration with ID {id} not found.'},
        ],
    },

    # * error: INVALID_FLAGGED_DEPENDENCY
    INVALID_FLAGGED_DEPENDENCY_ID: {
        'id': INVALID_FLAGGED_DEPENDENCY_ID,
        'name': 'Invalid Flagged Dependency',
        'message': [
            {'lang': 'en_US', 'text': 'A flagged dependency must define both module_path and class_name.'},
        ],
    },

    # * error: SERVICE_REGISTRATION_ALREADY_EXISTS
    SERVICE_REGISTRATION_ALREADY_EXISTS_ID: {
        'id': SERVICE_REGISTRATION_ALREADY_EXISTS_ID,
        'name': 'Service Registration Already Exists',
        'message': [
            {'lang': 'en_US', 'text': 'A service registration with ID {id} already exists.'},
        ],
    },

    # * error: INVALID_MODEL_ATTRIBUTE
    INVALID_MODEL_ATTRIBUTE_ID: {
        'id': INVALID_MODEL_ATTRIBUTE_ID,
        'name': 'Invalid Model Attribute',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid attribute: {attribute}. Supported attributes are {supported}.'},
        ],
    },

    # * error: INVALID_APP_INTERFACE_TYPE
    INVALID_APP_INTERFACE_TYPE_ID: {
        'id': INVALID_APP_INTERFACE_TYPE_ID,
        'name': 'Invalid App Interface Type',
        'message': [
            {'lang': 'en_US', 'text': '{attribute} must be a non-empty string.'},
        ],
    },

    # * error: SQLITE_CONN_ALREADY_OPEN
    SQLITE_CONN_ALREADY_OPEN_ID: {
        'id': SQLITE_CONN_ALREADY_OPEN_ID,
        'name': 'SQLite Connection Already Open',
        'message': [
            {'lang': 'en_US', 'text': 'Connection already open for path: {path}.'},
        ],
    },

    # * error: SQLITE_INVALID_MODE
    SQLITE_INVALID_MODE_ID: {
        'id': SQLITE_INVALID_MODE_ID,
        'name': 'Invalid SQLite Mode',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid SQLite mode: {mode}. Supported: ro, rw, rwc (or None for default auto-create).'},
        ],
    },

    # * error: SQLITE_FILE_NOT_FOUND_OR_READONLY
    SQLITE_FILE_NOT_FOUND_OR_READONLY_ID: {
        'id': SQLITE_FILE_NOT_FOUND_OR_READONLY_ID,
        'name': 'SQLite File Not Found or Read-Only',
        'message': [
            {'lang': 'en_US', 'text': 'Unable to open SQLite database at {path}: {original_error}. Check path exists and is writable (use mode=rwc to create).'},
        ],
    },

    # * error: SQLITE_CONN_FAILED
    SQLITE_CONN_FAILED_ID: {
        'id': SQLITE_CONN_FAILED_ID,
        'name': 'SQLite Connection Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to connect to SQLite database at {path}: {original_error}'},
        ],
    },

    # * error: SQLITE_BACKUP_FAILED
    SQLITE_BACKUP_FAILED_ID: {
        'id': SQLITE_BACKUP_FAILED_ID,
        'name': 'SQLite Backup Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Backup to {target_path} failed: {original_error}'},
        ],
    },

    # * error: SQLITE_CONN_NOT_INITIALIZED
    SQLITE_CONN_NOT_INITIALIZED_ID: {
        'id': SQLITE_CONN_NOT_INITIALIZED_ID,
        'name': 'SQLite Connection Not Initialized',
        'message': [
            {'lang': 'en_US', 'text': 'SQLite connection not initialized. Must be used within a "with" block.'},
        ],
    },

    # * error: INVALID_DEPENDENCY_ERROR
    INVALID_DEPENDENCY_ERROR_ID: {
        'id': INVALID_DEPENDENCY_ERROR_ID,
        'name': 'Invalid Dependency Error',
        'message': [
            {'lang': 'en_US', 'text': 'Dependency {dependency} could not be resolved: {reason}.'},
        ],
    },

    # * error: APP_ERROR
    APP_ERROR_ID: {
        'id': APP_ERROR_ID,
        'name': 'App Error',
        'message': [
            {'lang': 'en_US', 'text': 'An error occurred in the app: {error_message}.'},
        ],
    },

    # * error: CONFIG_FILE_NOT_FOUND
    CONFIG_FILE_NOT_FOUND_ID: {
        'id': CONFIG_FILE_NOT_FOUND_ID,
        'name': 'Configuration File Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Configuration file {file_path} not found.'},
        ],
    },

    # * error: APP_CONFIG_LOADING_FAILED
    APP_CONFIG_LOADING_FAILED_ID: {
        'id': APP_CONFIG_LOADING_FAILED_ID,
        'name': 'App Configuration Loading Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Unable to load app configuration file {file_path}: {exception}.'},
        ],
    },

    # * error: CONTAINER_CONFIG_LOADING_FAILED
    CONTAINER_CONFIG_LOADING_FAILED_ID: {
        'id': CONTAINER_CONFIG_LOADING_FAILED_ID,
        'name': 'Container Configuration Loading Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Unable to load container configuration file {file_path}: {exception}.'},
        ],
    },

    # * error: FEATURE_CONFIG_LOADING_FAILED
    FEATURE_CONFIG_LOADING_FAILED_ID: {
        'id': FEATURE_CONFIG_LOADING_FAILED_ID,
        'name': 'Feature Configuration Loading Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Unable to load feature configuration file {file_path}: {exception}.'},
        ],
    },

    # * error: ERROR_CONFIG_LOADING_FAILED
    ERROR_CONFIG_LOADING_FAILED_ID: {
        'id': ERROR_CONFIG_LOADING_FAILED_ID,
        'name': 'Error Configuration Loading Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Unable to load error configuration file {file_path}: {exception}.'},
        ],
    },

    # * error: CLI_CONFIG_LOADING_FAILED
    CLI_CONFIG_LOADING_FAILED_ID: {
        'id': CLI_CONFIG_LOADING_FAILED_ID,
        'name': 'CLI Configuration Loading Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Unable to load CLI configuration file {file_path}: {exception}.'},
        ],
    },

    # * error: CLI_COMMAND_NOT_FOUND
    CLI_COMMAND_NOT_FOUND_ID: {
        'id': CLI_COMMAND_NOT_FOUND_ID,
        'name': 'CLI Command Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'CLI command {command_id} not found.'},
        ],
    },

    # * error: CLI_COMMAND_ALREADY_EXISTS
    CLI_COMMAND_ALREADY_EXISTS_ID: {
        'id': CLI_COMMAND_ALREADY_EXISTS_ID,
        'name': 'CLI Command Already Exists',
        'message': [
            {'lang': 'en_US', 'text': 'CLI command with ID {id} already exists.'},
        ],
    },

    # * error: JSON_FILE_NOT_FOUND
    JSON_FILE_NOT_FOUND_ID: {
        'id': JSON_FILE_NOT_FOUND_ID,
        'name': 'JSON File Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'The specified JSON file could not be found at {path}.'},
        ],
    },

    # * error: INVALID_JSON_PATH
    INVALID_JSON_PATH_ID: {
        'id': INVALID_JSON_PATH_ID,
        'name': 'Invalid JSON Path',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid JSON path: {path}. Failed at segment: {part}.'},
        ],
    },

    # * error: TOML_FILE_NOT_FOUND
    TOML_FILE_NOT_FOUND_ID: {
        'id': TOML_FILE_NOT_FOUND_ID,
        'name': 'TOML File Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'The specified TOML file could not be found at {path}.'},
        ],
    },

    # * error: TOML_FILE_LOAD_ERROR
    TOML_FILE_LOAD_ERROR_ID: {
        'id': TOML_FILE_LOAD_ERROR_ID,
        'name': 'TOML Load Failure',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to parse TOML file: {error}. Path: {path}.'},
        ],
    },

    # * error: INVALID_TOML_FILE
    INVALID_TOML_FILE_ID: {
        'id': INVALID_TOML_FILE_ID,
        'name': 'Invalid TOML File',
        'message': [
            {'lang': 'en_US', 'text': 'File is not a valid TOML file: {path}.'},
        ],
    },

    # * error: CSV_INVALID_MODE
    CSV_INVALID_MODE_ID: {
        'id': CSV_INVALID_MODE_ID,
        'name': 'Invalid CSV Mode',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid file mode for CSV operation: {mode}. Expected r, w, a, etc.'},
        ],
    },

    # * error: CSV_HANDLE_NOT_INITIALIZED
    CSV_HANDLE_NOT_INITIALIZED_ID: {
        'id': CSV_HANDLE_NOT_INITIALIZED_ID,
        'name': 'CSV Handle Not Initialized',
        'message': [
            {'lang': 'en_US', 'text': 'CSV file must be opened before reading/writing.'},
        ],
    },

    # * error: CSV_INVALID_READ_MODE
    CSV_INVALID_READ_MODE_ID: {
        'id': CSV_INVALID_READ_MODE_ID,
        'name': 'Invalid CSV Read Mode',
        'message': [
            {'lang': 'en_US', 'text': 'File not opened in readable mode for CSV reading.'},
        ],
    },

    # * error: CSV_INVALID_WRITE_MODE
    CSV_INVALID_WRITE_MODE_ID: {
        'id': CSV_INVALID_WRITE_MODE_ID,
        'name': 'Invalid CSV Write Mode',
        'message': [
            {'lang': 'en_US', 'text': 'File not opened in writable mode for CSV writing.'},
        ],
    },

    # * error: CSV_FIELDNAMES_REQUIRED
    CSV_FIELDNAMES_REQUIRED_ID: {
        'id': CSV_FIELDNAMES_REQUIRED_ID,
        'name': 'CSV Fieldnames Required',
        'message': [
            {'lang': 'en_US', 'text': 'Fieldnames must be provided when writing dict-based CSV rows.'},
        ],
    },

    # * error: CSV_DICT_NO_HEADER
    CSV_DICT_NO_HEADER_ID: {
        'id': CSV_DICT_NO_HEADER_ID,
        'name': 'CSV Dict Reader Without Header',
        'message': [
            {'lang': 'en_US', 'text': 'Dict reader expects header row; file appears to lack one or was not read correctly.'},
        ],
    },

}
